from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parent
MAIN = Path("/home/jfi/GitHub/workflow-architect")
OUT = ROOT / "checkpoint3b-evidence"
assert ROOT.name == "workflow-architect-run-scoped-handoff"


def digest(path):
    data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


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
            "test_effect_lifecycle.py",
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
            "test_run_store.py",
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
        command, cwd=cwd, capture_output=True, text=True, timeout=20
    )
    (OUT / f"test-{index}.txt").write_text(result.stdout + result.stderr)
    results.append(
        {"command": command, "cwd": str(cwd), "returncode": result.returncode}
    )
baseline = json.loads(
    (ROOT / "checkpoint1-evidence/main-inventory-before.json").read_text()
)
drift = [
    path for path, value in baseline.items() if digest(MAIN / path) != value["sha256"]
]
snapshot = json.loads(
    (ROOT / "checkpoint1-evidence/snapshot-manifest.json").read_text()
)["files"]
drift.extend(
    row["path"] for row in snapshot if digest(MAIN / row["path"]) != row["sha256"]
)
same_status = (
    git(MAIN, "status", "--porcelain=v1", "--untracked-files=all")
    == (ROOT / "checkpoint1-evidence/main-status-before.txt").read_bytes()
)
prior = json.loads((ROOT / "checkpoint3-evidence/candidate-paths.json").read_text())
paths = set(prior)
paths.update(
    git(ROOT, "ls-files", "--others", "--exclude-standard").decode().splitlines()
)
for base in [
    "scripts/enforcement",
    "agent-packages/workflow-designer-agent/enforcement",
    "generated-workflows/network-infrastructure-execution-workflow/enforcement",
    "generated-workflows/network-infrastructure-execution-workflow/scripts/enforcement",
]:
    paths.update(str(p.relative_to(ROOT)) for p in (ROOT / base).glob("*.py"))
changes = {
    p: digest(ROOT / p)
    for p in sorted(paths)
    if (ROOT / p).is_file()
    and "-evidence" not in Path(p).parts[0]
    and digest(ROOT / p) != prior.get(p)
}
(OUT / "changed-paths.json").write_text(json.dumps(changes, indent=2))
report = {
    "tests": results,
    "main_changed": sorted(set(drift)),
    "main_status_equal": same_status,
    "main_head": git(MAIN, "rev-parse", "HEAD").decode().strip(),
    "candidate_head": git(ROOT, "rev-parse", "HEAD").decode().strip(),
    "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
(OUT / "final-checks.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
assert (
    all(result["returncode"] == 0 for result in results) and not drift and same_status
)
