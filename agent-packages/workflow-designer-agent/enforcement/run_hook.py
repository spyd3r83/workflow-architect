import json
import os
from pathlib import Path
import subprocess
import sys
from run_store import require, token
from run_operator import Operator
from run_effects import operator_key, TERMINAL
from run_policy import READ_TOOLS


def invoke(root, request):
    result = subprocess.run(
        ["bash", str(root / "scripts/enforcement/workflow-enforce.sh")],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        cwd=root,
        timeout=2,
    )
    require(result.returncode == 0, "enforcement subprocess denied or failed")
    reply = json.loads(result.stdout)
    require(reply.get("ok") is True, "explicit success required")
    return reply["result"]


def envelope(state, session, action, **extra):
    return dict(
        workspace=state["workspace"],
        run_id=state["run_id"],
        session_id=session,
        expected=token(state),
        action=action,
        **extra,
    )


def before(root, payload, state, session):
    tool = payload["tool_name"].lower()
    require(
        tool not in {"task", "agent", "workflow_action"},
        "Claude task/action adapter unsupported",
    )
    request = envelope(
        state, session, "check", tool=tool, arguments=payload["tool_input"]
    )
    require(invoke(root, request).get("decision") == "allow", "tool denied")
    if tool in READ_TOOLS:
        return
    Operator(root, operator_key(root))
    request.update(
        action="tool-begin",
        dispatch_id=payload["tool_use_id"],
        deliverable_digest=state["data"]["actors"][session]["scope"][
            "deliverable_digest"
        ],
    )
    invoke(root, request)


def reconciler(state, record, session):
    if list(token(state)) == record["start_token"]:
        return None
    parent = record.get("parent_effect")
    candidate = (
        state["data"]["effect_records"][parent]["origin_session"] if parent else session
    )
    actor = state["data"]["actors"][candidate]
    require(
        actor.get("can_reconcile") and actor.get("host_reconcile"),
        "explicit reconciliation grant required",
    )
    return candidate


def after(root, payload, state, session):
    tool = payload["tool_name"].lower()
    if tool in READ_TOOLS:
        return
    record = invoke(
        root, envelope(state, session, "effect-status", call_id=payload["tool_use_id"])
    )
    chosen = (
        reconciler(state, record, session) if record["status"] == "running" else None
    )
    status = (
        "failed" if payload["hook_event_name"] == "PostToolUseFailure" else "completed"
    )
    evidence = json.dumps(
        payload.get("error") if status == "failed" else payload.get("tool_response"),
        sort_keys=True,
    )
    op = Operator(root, operator_key(root))
    proof = op.observe(
        state["run_id"],
        token(state),
        session,
        payload["tool_use_id"],
        tool,
        payload["tool_input"],
        status,
        evidence,
        producer="claude-host",
    )
    action = "reconcile-effect" if chosen else "tool-end"
    request = completion_packet(state, record, proof, chosen or session, action)
    invoke(root, request)


def completion_packet(state, record, proof, session, default_action):
    audit = proof.get("replay_audit", {})
    action = audit.get("action", default_action)
    request = envelope(state, audit.get("session_id", session), action)
    request.update(
        expected=proof["expected"],
        dispatch_id=record["dispatch_id"],
        effect_token=record["token"],
        identity_digest=record["identity_digest"],
        completion_digest=proof["completion_digest"],
        reason="Authorized Claude host event with explicitly inspected CAS",
        reason_provenance={
            "source": "Claude 2.1.286 tool hook",
            "reference": proof["completion_digest"],
        },
    )
    return request


def execute(root, payload):
    require(payload.get("cwd") == str(root), "explicit host cwd binding required")
    if os.environ.get("WORKFLOW_WORKSPACE"):
        require(
            os.environ["WORKFLOW_WORKSPACE"] == str(root), "workspace override denied"
        )
    session = payload.get("agent_id") or payload.get("session_id")
    state = invoke(root, dict(workspace=str(root), session_id=session, action="bound"))
    event = payload.get("hook_event_name")
    if event == "PreCompact":
        print(json.dumps(envelope(state, session, "status")))
    elif event == "PreToolUse":
        before(root, payload, state, session)
    elif event in {"PostToolUse", "PostToolUseFailure"}:
        after(root, payload, state, session)
    else:
        raise ValueError("unregistered hook event")


def main():
    payload = {}
    try:
        payload = json.load(sys.stdin)
        root = Path(__file__).resolve().parents[2]
        execute(root, payload)
        return 0
    except Exception as error:
        if payload.get("hook_event_name") == "PreToolUse":
            output = {
                "hookSpecificOutput": dict(
                    hookEventName="PreToolUse",
                    permissionDecision="deny",
                    permissionDecisionReason=str(error),
                )
            }
        else:
            output = {
                "systemMessage": "Workflow event rejected; effects remain protected: "
                + str(error)
            }
        print(json.dumps(output))
        return 2


if __name__ == "__main__":
    sys.exit(main())
