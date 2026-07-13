#!/usr/bin/env bash
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="$ROOT/.opencode/workflow-state.json"
CONFIG_FILE="$ROOT/.opencode/workflow-config.json"

if [ ! -f "$STATE_FILE" ] || [ ! -f "$CONFIG_FILE" ]; then
  exit 0
fi

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
TOOL_ARG=$(echo "$INPUT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
ti=d.get('tool_input') or {}
print(ti.get('command') or ti.get('cmd') or ti.get('file_path') or ti.get('filePath') or ti.get('path') or '')
" 2>/dev/null || echo "")

RESULT=$(bash "$ROOT/scripts/enforcement/workflow-enforce.sh" check "$TOOL_NAME" "$TOOL_ARG" 2>/dev/null || echo "allow")

if [[ "$RESULT" == allow ]]; then
  exit 0
else
  REASON="${RESULT#block:}"
  jq -n --arg reason "$REASON" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
fi
