import json
import os
from pathlib import Path
import sys
from run_store import require
from run_operator import Operator

OPERATIONS = {
    "clear-hold": (
        "clear_hold",
        ["run_id", "expected", "hold", "reason", "additional_revisions"],
    ),
    "create-run": (
        "create",
        ["run_id", "owner", "session_id", "profile", "policy", "expected"],
    ),
    "enroll": ("enroll", ["run_id", "expected", "session_id", "profile"]),
    "close-child": ("close_child", ["run_id", "expected", "session_id", "reason"]),
    "import-human-approval": (
        "import_approval",
        ["run_id", "expected", "signed_receipt"],
    ),
    "recover-attempt": (
        "recover",
        ["run_id", "expected", "phase", "deliverable_digest", "reason"],
    ),
    "pin-action": ("pin_action", ["run_id", "expected", "action_id", "definition"]),
    "observe": (
        "observe",
        [
            "run_id",
            "expected",
            "session_id",
            "dispatch_id",
            "tool",
            "arguments",
            "status",
            "evidence",
        ],
    ),
}


def dispatch(operator, request):
    action = request["action"]
    if action == "inspect-run":
        return operator.store.read(request["run_id"])
    if action == "attest-completion":
        return operator.attest(
            request["run_id"],
            tuple(request["expected"]),
            request["dispatch_id"],
            request["producer"],
            request["evidence"].encode(),
            request["deliverable_digest"],
        )
    require(action in OPERATIONS, "unknown operator action")
    method, fields = OPERATIONS[action]
    values = [tuple(request[k]) if k == "expected" else request[k] for k in fields]
    return getattr(operator, method)(*values)


def authenticate(root, request):
    fd = int(os.environ["WORKFLOW_OPERATOR_FD"])
    require(fd >= 3, "dedicated inherited capability FD required")
    capability = os.read(fd, 33)
    if request["action"] == "bootstrap":
        require(
            request.get("expected") == [None, 0, 0],
            "explicit absent expectation required",
        )
        return Operator.bootstrap(root, capability, request["capacity"])
    return Operator(root, capability)


def main():
    try:
        root = Path(__file__).resolve().parents[2]
        request = json.load(sys.stdin)
        require(request.get("workspace") == str(root), "operator workspace mismatch")
        require(Path.cwd() == root, "operator cwd mismatch")
        operator = authenticate(root, request)
        result = (
            {"initialized": True}
            if request["action"] == "bootstrap"
            else dispatch(operator, request)
        )
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
