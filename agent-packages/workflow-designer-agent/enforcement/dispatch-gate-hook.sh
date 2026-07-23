#!/usr/bin/env bash
set -euo pipefail

input=$(cat)

tool_name=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', d.get('toolName', '')))
except: print('')
" 2>/dev/null || echo "")

hook_event=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('hook_event_name', d.get('hookEventName', '')))
except: print('')
" 2>/dev/null || echo "")

pkg_root=""
dir=$(pwd)
while [ "$dir" != "/" ] && [ -n "$dir" ]; do
  if [ -f "$dir/.opencode/workflow-state.json" ] || [ -f "$dir/.opencode/workflow-config.json" ]; then
    pkg_root="$dir"
    break
  fi
  dir=$(dirname "$dir")
done

if [ -z "$pkg_root" ]; then
  exit 0
fi

enforce_script="$pkg_root/scripts/enforcement/workflow-enforce.sh"
if [ ! -f "$enforce_script" ]; then
  exit 0
fi

if echo "$hook_event" | grep -qi "PreToolUse"; then
  tool_arg=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', d.get('toolArgs', d.get('toolInput', {})))
    if isinstance(ti, dict):
        print(ti.get('command', ti.get('filePath', ti.get('path', ti.get('file', '')))))
    else:
        print(str(ti))
except: print('')
" 2>/dev/null || echo "")
  result=$(bash "$enforce_script" check "$tool_name" "$tool_arg" 2>/dev/null || true)
  if echo "$result" | grep -q "^block:"; then
    reason=$(echo "$result" | sed 's/^block://')
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"$reason\"}}"
    echo "$reason" >&2
    exit 2
  fi
  exit 0
fi

if echo "$hook_event" | grep -qi "PostToolUse"; then
  if echo "$tool_name" | grep -qi "^task$\|^agent$"; then
    tool_response=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    r = d.get('tool_response', d.get('toolResult', d.get('tool_output', '')))
    if isinstance(r, dict):
        r = json.dumps(r)
    print(r)
except: print('')
" 2>/dev/null || echo "")
    if echo "$tool_response" | grep -qiE "(Skills not found|TASK_DISPATCH_UNAVAILABLE|dispatch.*failed|Error:|error:)"; then
      bash "$enforce_script" dispatch-failed 2>/dev/null || true
    fi
  fi
  exit 0
fi

exit 0
