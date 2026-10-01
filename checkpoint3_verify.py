from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parent
MAIN = Path("/home/jfi/GitHub/workflow-architect")
EVIDENCE = ROOT / "checkpoint3-evidence"
assert ROOT.name == "workflow-architect-run-scoped-handoff"


def digest(path):
    return hashlib.sha256(
        os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    ).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


commands = [
    (
        ROOT,
        [
            "python3",
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "agent-packages/workflow-designer-agent/tests",
            "-p",
            "test_run_store.py",
        ],
    ),
    (
        ROOT,
        [
            "python3",
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "agent-packages/workflow-designer-agent/tests",
            "-p",
            "test_runtime_paths.py",
        ],
    ),
    (
        ROOT,
        [
            "bun",
            "test",
            "agent-packages/workflow-designer-agent/tests/runtime_plugin.test.ts",
        ],
    ),
    (
        ROOT / "generated-workflows/network-infrastructure-execution-workflow",
        [
            "python3",
            "-B",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "tests/test_enforcement_alignment.py",
            "-k",
            "enforcement_alignment_passes or workflow_configs_match",
        ],
    ),
]
results = []
for index, (cwd, command) in enumerate(commands):
    result = subprocess.run(
        command, cwd=cwd, text=True, capture_output=True, timeout=20
    )
    (EVIDENCE / f"test-{index}.txt").write_text(result.stdout + result.stderr)
    results.append(
        {"cwd": str(cwd), "command": command, "returncode": result.returncode}
    )
baseline = json.loads(
    (ROOT / "checkpoint1-evidence/main-inventory-before.json").read_text()
)
changed_main = [
    name for name, value in baseline.items() if digest(MAIN / name) != value["sha256"]
]
snapshot = json.loads(
    (ROOT / "checkpoint1-evidence/snapshot-manifest.json").read_text()
)["files"]
changed_main.extend(
    row["path"] for row in snapshot if digest(MAIN / row["path"]) != row["sha256"]
)
status_equal = (
    git(MAIN, "status", "--porcelain=v1", "--untracked-files=all")
    == (ROOT / "checkpoint1-evidence/main-status-before.txt").read_bytes()
)
changed = set(git(ROOT, "diff", "--name-only").decode().splitlines())
changed.update(
    row["path"] for row in snapshot if digest(ROOT / row["path"]) != row["sha256"]
)
changed.update(
    git(ROOT, "ls-files", "--others", "--exclude-standard").decode().splitlines()
)
for directory in [
    "scripts/enforcement",
    "agent-packages/workflow-designer-agent/enforcement",
    "generated-workflows/network-infrastructure-execution-workflow/scripts/enforcement",
    "generated-workflows/network-infrastructure-execution-workflow/enforcement",
]:
    changed.update(
        str(path.relative_to(ROOT)) for path in (ROOT / directory).glob("run_*.py")
    )
changed.add(
    "generated-workflows/network-infrastructure-execution-workflow/scripts/enforcement/network_policy.py"
)
changed.update(
    "generated-workflows/network-infrastructure-execution-workflow/" + name
    for name in ["enforcement/network_policy.py", "run-binding.md"]
)
manifest = {
    name: digest(ROOT / name)
    for name in sorted(changed)
    if (ROOT / name).is_file() and not name.startswith("checkpoint3-evidence/")
}
(EVIDENCE / "candidate-paths.json").write_text(json.dumps(manifest, indent=2))
report = {
    "tests": results,
    "main_changed": sorted(set(changed_main)),
    "main_status_equal": status_equal,
    "main_head": git(MAIN, "rev-parse", "HEAD").decode().strip(),
    "candidate_head": git(ROOT, "rev-parse", "HEAD").decode().strip(),
    "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
(EVIDENCE / "final-checks.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
assert (
    not changed_main and status_equal and all(row["returncode"] == 0 for row in results)
)
