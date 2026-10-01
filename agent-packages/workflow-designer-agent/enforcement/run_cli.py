import json
from pathlib import Path
import sys
import os
import signal
import subprocess
import tempfile
import resource
from typing import Any
from run_store import Store, require, read_json, token
import run_policy
import run_effects


def config_for(root):
    config = read_json(root / ".opencode/workflow-config.json")
    require("bash_is_conditional" not in config, "legacy shell policy flag rejected")
    require(
        type(config.get("schema_version")) is int and config["schema_version"] == 1,
        "unsupported policy schema",
    )
    for key in ["total_phases", "min_evidence_chars", "max_revisions"]:
        require(
            type(config.get(key)) is int and config[key] > 0, "invalid policy config"
        )
    for key in ["implementation_phases", "revision_phases"]:
        require(type(config.get(key)) is list, "missing policy phase map")
    return config


def context(root, request):
    require(
        request.get("workspace") == str(root),
        "exact workspace binding required",
    )
    store = Store(root)
    state = store.bound(request.get("session_id"))
    require(state["lifecycle"] == "active", "inactive run")
    config = config_for(root)
    require(
        state["data"].get("policy_config") == config,
        "policy config changed; explicit reconciliation required",
    )
    if request["action"] != "bound":
        require(request.get("run_id") == state["run_id"], "run binding mismatch")
        if request["action"] not in {"dispatch-end", "tool-end", "reconcile-effect"}:
            store._expected(state, tuple(request.get("expected", [])))
    return store, state, config


def execute(request):
    root = Path(__file__).resolve().parents[2]
    require(Path.cwd() == root, "exact workspace cwd required")
    return execute_for(root, request)


def execute_for(root, request):
    store, state, config = context(root, request)
    action = request["action"]
    if action in {"bound", "status", "compaction"}:
        return state
    if action == "effect-status":
        return run_effects.lookup(state, request["session_id"], request.get("call_id"))
    if action == "run-action":
        return run_action(store, state, request)
    if action == "check":
        store.discover()
        run_policy.check(state, config, request)
        return {"decision": "allow", "state": state}
    expected = tuple(request["expected"])

    def change(current):
        require(token(current) == token(state), "stale context")
        run_policy.transition(current, config, request)

    replay = (
        (lambda current: run_effects.replay(current, request))
        if action in {"dispatch-end", "tool-end", "reconcile-effect"}
        else None
    )
    return store._change(state["run_id"], expected, change, replay=replay)


def run_action(store, state, request):
    spec = run_policy.exact_action(state, request)
    targets = run_policy.lease_paths(state, list(spec["inputs"]) + spec["outputs"])

    def begin(current):
        run_policy.exact_action(current, request)
        run_policy.unlocked_targets(current, targets)
        run_effects.begin(current, dict(request, target_paths=targets), "tool")

    started = store._change(state["run_id"], tuple(request["expected"]), begin)
    outcome = run_program(store.root, store.home, spec)
    return dict(outcome, state=started)


def file_limit():
    resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))


ACTION_ENV = dict(
    PATH="/usr/bin:/bin",
    LANG="C.UTF-8",
    PYTHONDONTWRITEBYTECODE="1",
    GIT_CONFIG_NOSYSTEM="1",
    GIT_CONFIG_GLOBAL="/dev/null",
)
PROCESS_OPTIONS: dict[str, Any] = dict(
    stderr=subprocess.STDOUT,
    start_new_session=True,
    preexec_fn=file_limit,
    close_fds=True,
)


def wait_program(process, milliseconds):
    try:
        return process.wait(timeout=milliseconds / 1000) == 0
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=3)
        return False


def run_program(root, home, spec):
    cwd = run_policy.canonical_target(root, spec["cwd"])
    env = dict(ACTION_ENV, HOME=str(root))
    with tempfile.TemporaryFile(dir=home) as output:
        process = subprocess.Popen(
            spec["argv"],
            cwd=cwd,
            env=env,
            stdout=output,
            **PROCESS_OPTIONS,
        )
        success = wait_program(process, spec["timeout_ms"])
        output.seek(0)
        text = output.read(1048576).decode(errors="replace")
    return dict(
        status="completed" if success else "failed",
        output=text,
        returncode=process.returncode,
    )


def main():
    try:
        require(len(sys.argv) == 1, "legacy command interface disabled")
        request = json.load(sys.stdin)
        result = execute(request)
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
