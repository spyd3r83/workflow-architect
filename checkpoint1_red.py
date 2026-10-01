import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "checkpoint1-evidence"
results = []


def invoke(script, cwd, *args, env=None, payload=None):
    return subprocess.run(
        ["bash", str(script), *args],
        cwd=cwd,
        env=env or os.environ.copy(),
        input=payload,
        text=True,
        capture_output=True,
        timeout=10,
    )


def record(name, result, expected):
    results.append(
        {
            "name": name,
            "expected": expected,
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "red": result.returncode == 0 and not result.stdout.startswith("block:"),
        }
    )


with tempfile.TemporaryDirectory(dir=EVIDENCE) as temporary:
    sandbox = Path(temporary)
    for package in [
        ROOT,
        ROOT / "generated-workflows/network-infrastructure-execution-workflow",
    ]:
        script = package / "scripts/enforcement/workflow-enforce.sh"
        record(
            f"{package.name}: missing binding/state/config denies write",
            invoke(script, sandbox, "check", "write", "harmless.txt"),
            "explicit denial",
        )
    (sandbox / ".opencode").mkdir()
    (sandbox / ".opencode/workflow-state.json").write_text("{}")
    (sandbox / ".opencode/workflow-config.json").write_text("{}")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(sandbox))
    result = invoke(
        ROOT / ".claude/hooks/pre-tool-use.sh",
        sandbox,
        env=env,
        payload=json.dumps(
            {"tool_name": "Write", "tool_input": {"file_path": "harmless.txt"}}
        ),
    )
    record(
        "actual Claude hook: missing enforcement script denies write",
        result,
        "deny decision, not empty success",
    )
    state = sandbox / ".opencode/workflow-state.json"
    state.write_text(
        json.dumps(
            {
                "current_phase": 9,
                "phases": {"9": {"gate": "pending", "status": "in_progress"}},
                "owner": "new-owner",
                "owner_epoch": 2,
                "state_version": 10,
            }
        )
    )
    env = dict(
        os.environ,
        WORKFLOW_STATE_FILE=str(state),
        WORKFLOW_CONFIG_FILE=str(sandbox / ".opencode/workflow-config.json"),
        WORKFLOW_RUN_ID="old-run",
        WORKFLOW_OWNER="old-owner",
        WORKFLOW_OWNER_EPOCH="1",
        WORKFLOW_STATE_VERSION="9",
    )
    before = state.read_bytes()
    result = invoke(
        ROOT / "scripts/enforcement/workflow-enforce.sh",
        sandbox,
        "dispatch-failed",
        env=env,
    )
    record(
        "stale owner callback must leave state unchanged",
        result,
        "denial and byte-identical state",
    )
    results[-1]["state_changed"] = before != state.read_bytes()
    results[-1]["red"] = before != state.read_bytes()

(EVIDENCE / "red-results.json").write_text(json.dumps(results, indent=2))
for row in results:
    print(("RED" if row["red"] else "NOT_REPRODUCED") + ": " + row["name"])
raise SystemExit(1 if any(row["red"] for row in results) else 0)
