"""Bounded provenance capture; reads source and writes only isolated candidate."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

MAIN = Path("/home/jfi/GitHub/workflow-architect")
DEST = Path(__file__).resolve().parent
BASE = "57fe1421573d0e3fa2aea404db15e1ba3db7c32d"
NETWORK = Path("generated-workflows/network-infrastructure-execution-workflow")
EVIDENCE = DEST / "checkpoint1-evidence"


def git(*args):
    return subprocess.check_output(["git", "-C", str(MAIN), *args])


def digest(path):
    data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def inventory():
    names = set(
        git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
        .decode()
        .split("\0")
    ) - {""}
    for root in [
        NETWORK,
        Path("generated-workflows/product-engineering-change-workflow"),
    ]:
        names.update(
            str(p.relative_to(MAIN))
            for p in (MAIN / root).rglob("*")
            if p.is_file() or p.is_symlink()
        )
    names.update(
        str(p.relative_to(MAIN))
        for p in (MAIN / ".opencode").glob("*state*")
        if p.is_file()
    )
    return {
        name: {"sha256": digest(MAIN / name), "symlink": (MAIN / name).is_symlink()}
        for name in sorted(names)
        if (MAIN / name).is_file() or (MAIN / name).is_symlink()
    }


assert DEST != MAIN and git("rev-parse", "HEAD").decode().strip() == BASE
EVIDENCE.mkdir(exist_ok=True)
before = inventory()
status = git("status", "--porcelain=v1", "--untracked-files=all")
(EVIDENCE / "main-status-before.txt").write_bytes(status)
(EVIDENCE / "main-inventory-before.json").write_text(json.dumps(before, indent=2))
selected = [
    "agent-packages/workflow-designer-agent/scripts/enforcement/workflow-enforce.sh",
    "agent-packages/workflow-designer-agent/scripts/enforcement/dispatch-gate-hook.sh",
    "agent-packages/workflow-designer-agent/.opencode/plugins/workflow-enforcer.ts",
    "agent-packages/workflow-designer-agent/.opencode/workflow-config.json",
    "agent-packages/workflow-designer-agent/enforcement.md",
    "scripts/enforcement/dispatch-gate-hook.sh",
]
manifest = []
for name in selected:
    src, dst = MAIN / name, DEST / name
    assert src.is_file() and not src.is_symlink()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    manifest.append(
        {
            "path": name,
            "sha256": digest(src),
            "reason": "Existing untracked enforcement surface required for canonical/root path parity; no unrelated dirty WIP imported.",
        }
    )
assert not (DEST / NETWORK).exists()
for src in sorted((MAIN / NETWORK).rglob("*")):
    rel = src.relative_to(MAIN)
    if any(
        part in {"__pycache__", ".pytest_cache", "node_modules", ".git"}
        for part in rel.parts
    ):
        continue
    dst = DEST / rel
    if src.is_symlink():
        target = os.readlink(src)
        assert not Path(target).is_absolute() and (
            src.parent / target
        ).resolve().is_relative_to((MAIN / NETWORK).resolve())
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(target)
    elif src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
    elif src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        continue
    if src.is_file() or src.is_symlink():
        assert digest(src) == digest(dst)
        manifest.append(
            {
                "path": str(rel),
                "sha256": digest(src),
                "reason": "Ignored network package isolated snapshot; local policies, tests, receipts and singleton retained unchanged.",
            }
        )
after = inventory()
assert before == after and status == git(
    "status", "--porcelain=v1", "--untracked-files=all"
)
(EVIDENCE / "snapshot-manifest.json").write_text(
    json.dumps(
        {
            "base": BASE,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "files": manifest,
        },
        indent=2,
    )
)
(EVIDENCE / "main-unchanged.json").write_text(
    json.dumps(
        {
            "inventory_equal": before == after,
            "status_equal": True,
            "files_hashed": len(before),
            "head": BASE,
        },
        indent=2,
    )
)
print(
    json.dumps(
        {
            "source_files_hashed": len(before),
            "snapshot_files": len(manifest),
            "main_unchanged": True,
        }
    )
)
