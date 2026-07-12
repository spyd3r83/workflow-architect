#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="${WORKFLOW_CONFIG_FILE:-.opencode/workflow-config.json}"
STATE_FILE="${WORKFLOW_STATE_FILE:-.opencode/workflow-state.json}"

load_config() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo '{"workflow_package":"unknown","total_phases":15,"implementation_phases":[9,10],"write_tools":["write","edit","bash"],"max_revisions":3}'
    return
  fi
  cat "$CONFIG_FILE"
}

show_status() {
  if [ ! -f "$STATE_FILE" ]; then
    echo '{"error": "No workflow state file found. Run with init first."}'
    exit 1
  fi
  cat "$STATE_FILE"
}

init_state() {
  local config
  config=$(load_config)
  mkdir -p "$(dirname "$STATE_FILE")"
  python3 -c "
import json
from datetime import datetime, timezone

config = json.loads('''$config''')
total = config.get('total_phases', 15)
pkg = config.get('workflow_package', 'unknown')

state = {
    'workflow_package': pkg,
    'current_phase': 1,
    'phases': {},
    'revision_count': 0,
    'escalated': False,
    'created_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
}

for i in range(1, total + 1):
    key = str(i)
    state['phases'][key] = {
        'status': 'in_progress' if i == 1 else 'pending',
        'gate': 'pending'
    }

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f'Initialized workflow state at $STATE_FILE ({total} phases, package: {pkg})')
"
}

check_tool() {
  local tool_name="$1"
  if [ ! -f "$STATE_FILE" ] || [ ! -f "$CONFIG_FILE" ]; then
    echo "allow"
    return 0
  fi

  python3 -c "
import json, sys

with open('$CONFIG_FILE') as f:
    config = json.load(f)
with open('$STATE_FILE') as f:
    state = json.load(f)

tool = '$tool_name'
write_tools = config.get('write_tools', ['write', 'edit', 'bash'])
impl_phases = config.get('implementation_phases', [9, 10])
max_rev = config.get('max_revisions', 3)

if tool not in write_tools:
    print('allow')
    sys.exit(0)

current = state.get('current_phase', 1)
phase_key = str(current)
phase = state.get('phases', {}).get(phase_key, {})

if phase.get('status') == 'completed' and phase.get('gate') == 'passed':
    print('allow')
elif current in impl_phases and phase.get('status') == 'in_progress':
    print('allow')
else:
    print(f'block:Phase {current} gate not passed (status={phase.get(\"status\", \"unknown\")}). Write tools blocked. Use workflow_status tool to check state.')
"
}

advance_phase() {
  local target_phase="${1:-}"
  python3 -c "
import json
from datetime import datetime, timezone

with open('$CONFIG_FILE') as f:
    config = json.load(f)
with open('$STATE_FILE') as f:
    state = json.load(f)

target = int('$target_phase') if '$target_phase' else state.get('current_phase', 1) + 1
old = state.get('current_phase', 1)
old_key = str(old)

if old_key in state.get('phases', {}):
    state['phases'][old_key]['status'] = 'completed'
    state['phases'][old_key]['gate'] = 'passed'
    state['phases'][old_key]['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

state['current_phase'] = target
new_key = str(target)
if new_key in state.get('phases', {}):
    state['phases'][new_key]['status'] = 'in_progress'

state['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f'Advanced from phase {old} to phase {target}')
"
}

pass_gate() {
  local phase="${1:-}"
  python3 -c "
import json
from datetime import datetime, timezone

with open('$STATE_FILE') as f:
    state = json.load(f)

phase = int('$phase') if '$phase' else state.get('current_phase', 1)
key = str(phase)
if key in state.get('phases', {}):
    state['phases'][key]['gate'] = 'passed'
    state['phases'][key]['status'] = 'completed'
    state['phases'][key]['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

state['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f'Gate passed for phase {phase}')
"
}

fail_gate() {
  local phase="${1:-}"
  local reason="${2:-unspecified}"
  python3 -c "
import json
from datetime import datetime, timezone

with open('$CONFIG_FILE') as f:
    config = json.load(f)
with open('$STATE_FILE') as f:
    state = json.load(f)

phase = int('$phase') if '$phase' else state.get('current_phase', 1)
key = str(phase)
reason = '$reason'
max_rev = config.get('max_revisions', 3)

if key in state.get('phases', {}):
    state['phases'][key]['gate'] = 'failed'
    state['phases'][key]['fail_reason'] = reason
    state['phases'][key]['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

rev = state.get('revision_count', 0) + 1
state['revision_count'] = rev
if rev >= max_rev:
    state['escalated'] = True

state['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f'Gate FAILED for phase {phase}: {reason}. Revision count: {rev}/{max_rev}')
"
}

compaction_context() {
  if [ ! -f "$STATE_FILE" ]; then
    echo "No workflow state file found."
    exit 0
  fi
  python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)

current = state.get('current_phase', 1)
phases = state.get('phases', {})
completed = [k for k, v in phases.items() if v.get('status') == 'completed']
in_progress = [k for k, v in phases.items() if v.get('status') == 'in_progress']
failed = [(k, v.get('fail_reason', 'unknown')) for k, v in phases.items() if v.get('gate') == 'failed']

print('## WORKFLOW ENFORCEMENT STATE (PERSIST ACROSS COMPACTION)')
print(f'Workflow: {state.get(\"workflow_package\", \"unknown\")}')
print(f'Current Phase: {current}')
print(f'Completed Phases: {completed if completed else \"none\"}')
print(f'In Progress: {in_progress if in_progress else \"none\"}')
print(f'Failed Gates: {failed if failed else \"none\"}')
print(f'Revision Count: {state.get(\"revision_count\", 0)}/3')
print(f'Escalated: {state.get(\"escalated\", False)}')
print(f'Last Updated: {state.get(\"updated_at\", \"unknown\")}')
print('IMPORTANT: Do not skip phases. Do not proceed past a failed gate. Use workflow_status tool to check state.')
"
}

case "${1:-help}" in
  init) init_state ;;
  status) show_status ;;
  check) shift; check_tool "$@" ;;
  advance) shift; advance_phase "$@" ;;
  pass) shift; pass_gate "$@" ;;
  fail) shift; fail_gate "$@" ;;
  compaction) compaction_context ;;
  help|*)
    echo "Usage: workflow-enforce.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  init               Initialize workflow state from workflow-config.json"
    echo "  status             Show current workflow state as JSON"
    echo "  check <tool>       Check if a tool is allowed (prints 'allow' or 'block:reason')"
    echo "  advance [phase]    Advance to next or specified phase"
    echo "  pass [phase]       Mark a phase gate as passed"
    echo "  fail [phase] [reason]  Mark a phase gate as failed"
    echo "  compaction         Print workflow state for compaction context injection"
    ;;
esac
