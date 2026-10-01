import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MAIN = Path("/home/jfi/GitHub/workflow-architect")
assert sys.argv[1:] in ([], ["3d"])
OUT = ROOT / ("checkpoint3d-evidence" if sys.argv[1:] else "checkpoint3c-evidence")
assert ROOT.name == "workflow-architect-run-scoped-handoff"


def digest(path):
    return hashlib.sha256(
        os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    ).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


main_baseline = json.loads(
    (ROOT / "checkpoint1-evidence/main-inventory-before.json").read_text()
)
changed_main = [p for p, v in main_baseline.items() if digest(MAIN / p) != v["sha256"]]
snapshot = json.loads(
    (ROOT / "checkpoint1-evidence/snapshot-manifest.json").read_text()
)["files"]
changed_main.extend(
    v["path"] for v in snapshot if digest(MAIN / v["path"]) != v["sha256"]
)
status_equal = (
    git(MAIN, "status", "--porcelain=v1", "--untracked-files=all")
    == (ROOT / "checkpoint1-evidence/main-status-before.txt").read_bytes()
)
prior = json.loads((ROOT / "checkpoint3-evidence/candidate-paths.json").read_text())
prior.update(
    json.loads((ROOT / "checkpoint3b-evidence/changed-paths.json").read_text())
)
if sys.argv[1:]:
    prior.update(
        json.loads((ROOT / "checkpoint3c-evidence/changed-paths.json").read_text())
    )
for row in snapshot:
    prior.setdefault(row["path"], row["sha256"])
paths = set(prior) | set(
    git(ROOT, "ls-files", "--others", "--exclude-standard").decode().splitlines()
)
changes = {
    p: digest(ROOT / p)
    for p in sorted(paths)
    if (ROOT / p).is_file()
    and "-evidence" not in Path(p).parts[0]
    and digest(ROOT / p) != prior.get(p)
}
(OUT / "changed-paths.json").write_text(json.dumps(changes, indent=2))
handlers = {
    "check",
    "gate",
    "dispatch_begin",
    "dispatch_end",
    "transition",
    "execute_for",
    "main",
    "before",
    "after",
    "execute",
    "dispatch",
    "bootstrap",
    "create",
    "enroll",
    "close_child",
    "attest",
    "observe",
    "pin_action",
    "import_approval",
    "recover",
    "change",
}
findings = []
for path in (ROOT / "agent-packages/workflow-designer-agent/enforcement").glob("*.py"):
    lines = path.read_text().splitlines()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.FunctionDef):
            count = sum(
                bool(s.strip()) for s in lines[node.lineno - 1 : node.end_lineno]
            )
            budget = 40 if node.name in handlers else 20
            if count > budget:
                findings.append(
                    {
                        "path": str(path.relative_to(ROOT)),
                        "function": node.name,
                        "nonblank_lines": count,
                        "budget": budget,
                    }
                )
(OUT / "size-findings.json").write_text(json.dumps(findings, indent=2))
live = []
for entry in Path("/proc").iterdir():
    if not entry.name.isdigit():
        continue
    try:
        cwd = os.readlink(entry / "cwd")
        if cwd.startswith(
            str(ROOT / "agent-packages/workflow-designer-agent/tests") + "/"
        ):
            live.append(int(entry.name))
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
report = {
    "main_changed": sorted(set(changed_main)),
    "main_status_equal": status_equal,
    "main_head": git(MAIN, "rev-parse", "HEAD").decode().strip(),
    "candidate_head": git(ROOT, "rev-parse", "HEAD").decode().strip(),
    "live_fixture_subprocess_pids": live,
    "python_size_findings": len(findings),
    "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
(OUT / "preservation.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
assert not changed_main and status_equal and not live
