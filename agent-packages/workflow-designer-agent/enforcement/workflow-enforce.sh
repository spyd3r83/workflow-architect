#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="${WORKFLOW_CONFIG_FILE:-.opencode/workflow-config.json}"
STATE_FILE="${WORKFLOW_STATE_FILE:-.opencode/workflow-state.json}"

load_config() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo '{"workflow_package":"unknown","total_phases":15,"implementation_phases":[9,10],"write_tools":["write","edit","apply_patch","str_replace_editor"],"bash_is_conditional":true,"max_revisions":3,"min_evidence_chars":20}'
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
  CONFIG_JSON="$config" STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os
from datetime import datetime, timezone

config = json.loads(os.environ["CONFIG_JSON"])
total = config.get("total_phases", 15)
pkg = config.get("workflow_package", "unknown")
state_path = os.environ["STATE_PATH"]

state = {
    "workflow_package": pkg,
    "current_phase": 1,
    "phases": {},
    "revision_count": 0,
    "escalated": False,
    "dispatch_failed": False,
    "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

for i in range(1, total + 1):
    key = str(i)
    state["phases"][key] = {
        "status": "in_progress" if i == 1 else "pending",
        "gate": "pending",
    }

with open(state_path, "w") as f:
    json.dump(state, f, indent=2)

print(f"Initialized workflow state at {state_path} ({total} phases, package: {pkg})")
PY
}

check_tool() {
  local tool_name="${1:-}"
  local tool_arg="${2:-}"

  if [ "$tool_name" = "call_omo_agent" ] || [ "$tool_name" = "call-omo-agent" ] || [ "$tool_name" = "call_omo_Agent" ]; then
    echo "block:call_omo_agent is forbidden as an OpenCode dispatch path. Use task(subagent_type=...); if a real task call fails, stop with TASK_DISPATCH_UNAVAILABLE. See dispatch-protocol.md."
    return 0
  fi

  tool_name=$(echo "$tool_name" | tr '[:upper:]' '[:lower:]')

  if [ ! -f "$STATE_FILE" ] || [ ! -f "$CONFIG_FILE" ]; then
    echo "allow"
    return 0
  fi

  TOOL_NAME="$tool_name" TOOL_ARG="$tool_arg" CONFIG_PATH="$CONFIG_FILE" STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os, re, sys

tool = os.environ.get("TOOL_NAME", "")
tool_arg = os.environ.get("TOOL_ARG", "")

with open(os.environ["CONFIG_PATH"]) as f:
    config = json.load(f)
with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)

write_tools = set(config.get("write_tools", ["write", "edit", "apply_patch", "str_replace_editor", "create"]))
impl_phases = set(int(x) for x in config.get("implementation_phases", [9, 10]))
revision_phases = set(int(x) for x in config.get("revision_phases", list(impl_phases) + [11, 12, 13]))
bash_conditional = config.get("bash_is_conditional", True)
revision_mode = bool(state.get("revision_mode", False))

MUTATING_BASH = re.compile(
    r"(?:"
    r"\b(?:rm|mv|cp|mkdir|touch|truncate|tee|chmod|chown|chgrp|ln|install)\b|"
    r"\b(?:sed|perl)\s+-i\b|"
    r"\bgit\s+(?:add|commit|push|reset|checkout|rebase|merge|stash|clean|tag|am|cherry-pick|restore|switch)\b|"
    r"\b(?:npm|pnpm|yarn|bun)\s+(?:add|remove|install|uninstall|publish|update|link)\b|"
    r"\bpip(?:3)?\s+install\b|"
    r"\b(?:cat|tee)\s*>|\s>>\s*|[^\s]\s*>\s*[^\s]|"
    r"\bapply_patch\b|\bpatch\b|"
    r"\bdd\b|\bshred\b"
    r")",
    re.IGNORECASE,
)

# External / destructive actions always need explicit approval, even in revision mode.
APPROVAL_REQUIRED = re.compile(
    r"(?:"
    r"\bgit\s+push\b|"
    r"\bgit\s+push\s+--force\b|"
    r"\bgh\s+release\b|"
    r"\bgh\s+pr\s+create\b|"
    r"\bnpm\s+publish\b|"
    r"\bbun\s+publish\b|"
    r"\bpnpm\s+publish\b|"
    r"\bdocker\s+push\b|"
    r"\brm\s+-rf\s+/"
    r")",
    re.IGNORECASE,
)

def is_write_tool(name: str, arg: str) -> bool:
    if name in write_tools:
        return True
    if name in ("bash", "exec"):
        if not bash_conditional:
            return True
        if not arg.strip():
            return False
        return bool(MUTATING_BASH.search(arg))
    return False

def is_approval_required(name: str, arg: str) -> bool:
    if name == "bash" and arg.strip() and APPROVAL_REQUIRED.search(arg):
        return True
    return False

def has_failed_gates(st: dict) -> bool:
    for v in st.get("phases", {}).values():
        if v.get("gate") == "failed":
            return True
    return False

def local_mutation_allowed(st: dict, cfg_impl, cfg_rev) -> bool:
    current = int(st.get("current_phase", 1))
    phase = st.get("phases", {}).get(str(current), {})
    status = phase.get("status", "pending")
    gate = phase.get("gate", "pending")
    rev_mode = bool(st.get("revision_mode", False)) or has_failed_gates(st)

    if rev_mode and current in cfg_rev and status in ("in_progress", "completed", "pending"):
        return True
    if current in cfg_impl and status == "in_progress":
        return True
    if status == "completed" and gate == "passed" and current in cfg_impl:
        return True
    return False

if is_approval_required(tool, tool_arg):
    approvals = state.get("approvals", {})
    if not approvals.get("external_actions"):
        print(
            "block:External/destructive action requires approval. "
            "Run: workflow-enforce.sh approve external_actions <evidence>"
        )
        sys.exit(0)

if not is_write_tool(tool, tool_arg):
    print("allow")
    sys.exit(0)

dispatch_failed = state.get("dispatch_failed", False)
if dispatch_failed:
    print(
        "block:Dispatch failure detected. Mutating tools are blocked until "
        "workflow_status fail_gate is called to acknowledge the failure. "
        "Do not fall back to direct implementation."
    )
    sys.exit(0)

current = int(state.get("current_phase", 1))
phase_key = str(current)
phase = state.get("phases", {}).get(phase_key, {})

if local_mutation_allowed(state, impl_phases, revision_phases):
    print("allow")
else:
    print(
        f"block:Phase {current} is read-only/review (status={phase.get('status', 'unknown')}, "
        f"gate={phase.get('gate', 'pending')}, revision_mode={revision_mode}). "
        "Local mutation tools blocked outside implementation/revision phases. "
        "Use enter_revision or recover, or pass_gate/advance with evidence."
    )
PY
}

advance_phase() {
  local target_phase="${1:-}"
  local evidence="${2:-}"
  TARGET_PHASE="$target_phase" EVIDENCE="$evidence" CONFIG_PATH="$CONFIG_FILE" STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os, sys
from datetime import datetime, timezone

with open(os.environ["CONFIG_PATH"]) as f:
    config = json.load(f)
with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)

if state.get("dispatch_failed", False):
    print("error:Cannot advance while dispatch_failed is true. Call fail_gate to acknowledge the failure first.")
    sys.exit(1)

min_chars = int(config.get("min_evidence_chars", 20))
target_raw = os.environ.get("TARGET_PHASE", "").strip()
evidence = os.environ.get("EVIDENCE", "").strip()
old = state.get("current_phase", 1)
target = int(target_raw) if target_raw else old + 1
old_key = str(old)
old_phase = state.get("phases", {}).get(old_key, {})

if old_phase.get("gate") != "passed":
    print(
        f"error:Cannot advance from phase {old} because its gate is not passed "
        f"(gate={old_phase.get('gate', 'pending')}). Call pass_gate with evidence first."
    )
    sys.exit(1)

if target > old + 1:
    print(f"error:Cannot skip phases. Current={old}, requested={target}. Advance one phase at a time.")
    sys.exit(1)

if not evidence or len(evidence) < min_chars:
    print(
        f"error:Advance requires evidence (>= {min_chars} chars) describing why the next phase may begin."
    )
    sys.exit(1)

state["phases"][old_key]["status"] = "completed"
state["phases"][old_key]["gate"] = "passed"
state["phases"][old_key]["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

state["current_phase"] = target
new_key = str(target)
if new_key not in state.get("phases", {}):
    state.setdefault("phases", {})[new_key] = {"status": "pending", "gate": "pending"}
state["phases"][new_key]["status"] = "in_progress"
state["phases"][new_key]["advance_evidence"] = evidence
state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

with open(os.environ["STATE_PATH"], "w") as f:
    json.dump(state, f, indent=2)

print(f"Advanced from phase {old} to phase {target}")
PY
}

pass_gate() {
  local phase="${1:-}"
  local evidence="${2:-}"
  PHASE="$phase" EVIDENCE="$evidence" CONFIG_PATH="$CONFIG_FILE" STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os, sys
from datetime import datetime, timezone

with open(os.environ["CONFIG_PATH"]) as f:
    config = json.load(f)
with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)

if state.get("dispatch_failed", False):
    print("error:Cannot pass gate while dispatch_failed is true. Call fail_gate to acknowledge the failure first.")
    sys.exit(1)

min_chars = int(config.get("min_evidence_chars", 20))
phase_raw = os.environ.get("PHASE", "").strip()
evidence = os.environ.get("EVIDENCE", "").strip()
phase = int(phase_raw) if phase_raw else state.get("current_phase", 1)
key = str(phase)

if not evidence or len(evidence) < min_chars:
    print(
        f"error:pass_gate requires evidence (>= {min_chars} chars) describing completed phase work "
        "(files inspected/created, validation commands, outcomes)."
    )
    sys.exit(1)

if key not in state.get("phases", {}):
    state.setdefault("phases", {})[key] = {"status": "pending", "gate": "pending"}

state["phases"][key]["gate"] = "passed"
state["phases"][key]["status"] = "completed"
state["phases"][key]["pass_evidence"] = evidence
state["phases"][key]["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

with open(os.environ["STATE_PATH"], "w") as f:
    json.dump(state, f, indent=2)

print(f"Gate passed for phase {phase}")
PY
}

fail_gate() {
  local phase="${1:-}"
  local reason="${2:-}"
  if [ -z "$reason" ]; then
    echo "error:fail_gate requires a reason describing the failure."
    exit 1
  fi
  PHASE="$phase" REASON="$reason" CONFIG_PATH="$CONFIG_FILE" STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os
from datetime import datetime, timezone

with open(os.environ["CONFIG_PATH"]) as f:
    config = json.load(f)
with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)

phase_raw = os.environ.get("PHASE", "").strip()
phase = int(phase_raw) if phase_raw else state.get("current_phase", 1)
key = str(phase)
reason = os.environ.get("REASON", "unspecified")
max_rev = config.get("max_revisions", 3)

if key not in state.get("phases", {}):
    state.setdefault("phases", {})[key] = {"status": "pending", "gate": "pending"}

state["phases"][key]["gate"] = "failed"
state["phases"][key]["fail_reason"] = reason
state["phases"][key]["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
state["phases"][key]["status"] = "in_progress"
state["revision_mode"] = True
state["revision_target_phase"] = phase
state["dispatch_failed"] = False

rev = state.get("revision_count", 0) + 1
state["revision_count"] = rev
if rev >= max_rev:
    state["escalated"] = True

state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

with open(os.environ["STATE_PATH"], "w") as f:
    json.dump(state, f, indent=2)

print(f"Gate FAILED for phase {phase}: {reason}. Revision count: {rev}/{max_rev}. revision_mode=true")
PY
}

enter_revision() {
  local phase="${1:-}"
  local evidence="${2:-}"
  PHASE="$phase" EVIDENCE="$evidence" CONFIG_PATH="$CONFIG_FILE" STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os, sys
from datetime import datetime, timezone

with open(os.environ["CONFIG_PATH"]) as f:
    config = json.load(f)
with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)

min_chars = int(config.get("min_evidence_chars", 20))
phase_raw = os.environ.get("PHASE", "").strip()
evidence = os.environ.get("EVIDENCE", "").strip()
phase = int(phase_raw) if phase_raw else state.get("current_phase", 1)
if not evidence or len(evidence) < min_chars:
    print(f"error:enter_revision requires evidence (>= {min_chars} chars)")
    sys.exit(1)

key = str(phase)
if key not in state.get("phases", {}):
    state.setdefault("phases", {})[key] = {"status": "pending", "gate": "pending"}
state["revision_mode"] = True
state["revision_target_phase"] = phase
state["current_phase"] = phase
state["phases"][key]["status"] = "in_progress"
state["phases"][key]["gate"] = "pending"
state["phases"][key]["revision_evidence"] = evidence
state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with open(os.environ["STATE_PATH"], "w") as f:
    json.dump(state, f, indent=2)
print(f"Entered revision mode at phase {phase}")
PY
}

recover() {
  local evidence="${1:-}"
  EVIDENCE="$evidence" CONFIG_PATH="$CONFIG_FILE" STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os, sys
from datetime import datetime, timezone

with open(os.environ["CONFIG_PATH"]) as f:
    config = json.load(f)
with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)

min_chars = int(config.get("min_evidence_chars", 20))
evidence = os.environ.get("EVIDENCE", "").strip()
if not evidence or len(evidence) < min_chars:
    print(f"error:recover requires evidence (>= {min_chars} chars) describing deadlock recovery")
    sys.exit(1)

impl = [int(x) for x in config.get("implementation_phases", [9, 10])]
target = impl[0] if impl else int(state.get("current_phase", 1))
key = str(target)
if key not in state.get("phases", {}):
    state.setdefault("phases", {})[key] = {"status": "pending", "gate": "pending"}
state["revision_mode"] = True
state["revision_target_phase"] = target
state["current_phase"] = target
state["phases"][key]["status"] = "in_progress"
state["phases"][key]["gate"] = "pending"
state["recovery_evidence"] = evidence
state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with open(os.environ["STATE_PATH"], "w") as f:
    json.dump(state, f, indent=2)
print(f"Recovered deadlock: revision_mode=true at phase {target}")
PY
}

approve() {
  local key="${1:-}"
  local evidence="${2:-}"
  KEY="$key" EVIDENCE="$evidence" CONFIG_PATH="$CONFIG_FILE" STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os, sys
from datetime import datetime, timezone

with open(os.environ["CONFIG_PATH"]) as f:
    config = json.load(f)
with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)

min_chars = int(config.get("min_evidence_chars", 20))
key = os.environ.get("KEY", "").strip() or "external_actions"
evidence = os.environ.get("EVIDENCE", "").strip()
if not evidence or len(evidence) < min_chars:
    print(f"error:approve requires evidence (>= {min_chars} chars)")
    sys.exit(1)
approvals = state.setdefault("approvals", {})
approvals[key] = {
    "approved": True,
    "evidence": evidence,
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
state["approvals"] = approvals
state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with open(os.environ["STATE_PATH"], "w") as f:
    json.dump(state, f, indent=2)
print(f"Approved: {key}")
PY
}

compaction_context() {
  if [ ! -f "$STATE_FILE" ]; then
    echo "No workflow state file found."
    exit 0
  fi
  STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os
with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)

current = state.get("current_phase", 1)
phases = state.get("phases", {})
completed = [k for k, v in phases.items() if v.get("status") == "completed"]
in_progress = [k for k, v in phases.items() if v.get("status") == "in_progress"]
failed = [(k, v.get("fail_reason", "unknown")) for k, v in phases.items() if v.get("gate") == "failed"]

print("## WORKFLOW ENFORCEMENT STATE (PERSIST ACROSS COMPACTION)")
print(f"Workflow: {state.get('workflow_package', 'unknown')}")
print(f"Current Phase: {current}")
print(f"Completed Phases: {completed if completed else 'none'}")
print(f"In Progress: {in_progress if in_progress else 'none'}")
print(f"Failed Gates: {failed if failed else 'none'}")
print(f"Revision Count: {state.get('revision_count', 0)}/3")
print(f"Revision Mode: {state.get('revision_mode', False)}")
print(f"Escalated: {state.get('escalated', False)}")
print(f"Dispatch Failed: {state.get('dispatch_failed', False)}")
print(f"Last Updated: {state.get('updated_at', 'unknown')}")
print("IMPORTANT: Do not skip phases. pass_gate and advance require evidence.")
print("Local mutations allowed in implementation/revision phases; external push/release needs approve.")
print("Read-only bash is allowed. Use enter_revision/recover if deadlocked.")
PY
}

dispatch_failed() {
  STATE_PATH="$STATE_FILE" python3 - <<'PY'
import json, os
from datetime import datetime, timezone

with open(os.environ["STATE_PATH"]) as f:
    state = json.load(f)
state["dispatch_failed"] = True
state["dispatch_failed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with open(os.environ["STATE_PATH"], "w") as f:
    json.dump(state, f, indent=2)
print("Dispatch failure recorded. Mutating tools blocked until fail_gate is called.")
PY
}

case "${1:-help}" in
  init) init_state ;;
  status) show_status ;;
  check) shift; check_tool "$@" ;;
  advance) shift; advance_phase "$@" ;;
  pass) shift; pass_gate "$@" ;;
  fail) shift; fail_gate "$@" ;;
  enter_revision) shift; enter_revision "$@" ;;
  recover) shift; recover "$@" ;;
  approve) shift; approve "$@" ;;
  dispatch-failed) dispatch_failed ;;
  compaction) compaction_context ;;
  help|*)
    echo "Usage: workflow-enforce.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  init                         Initialize workflow state from workflow-config.json"
    echo "  status                       Show current workflow state as JSON"
    echo "  check <tool> [arg]           Check if a tool is allowed"
    echo "  advance [phase] <evidence>   Advance one phase (requires current gate passed + evidence)"
    echo "  pass [phase] <evidence>      Mark a phase gate as passed (requires evidence)"
    echo "  fail [phase] [reason]        Mark a phase gate as failed (enters revision_mode)"
    echo "  enter_revision [phase] <evidence>  Authorize local mutations for repair loop"
    echo "  recover <evidence>           Recover from stale/deadlock into revision at impl phase"
    echo "  approve <key> <evidence>     Approve external/destructive actions (e.g. external_actions)"
    echo "  compaction                   Print workflow state for compaction context injection"
    ;;
esac
