import hashlib, json, os, shutil, subprocess, sys, tempfile, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = Path("/home/jfi/GitHub/workflow-architect")
OUTPUTS = {
    "--review-repair": "review-repair-evidence",
    "--hook-migration": "hook-migration-evidence",
}
assert not sys.argv[1:] or (len(sys.argv) == 2 and sys.argv[1] in OUTPUTS)
OUT = ROOT / OUTPUTS.get(sys.argv[1] if sys.argv[1:] else "", "checkpoint4-evidence")
META = ROOT / "agent-packages/workflow-designer-agent"
NET = ROOT / "generated-workflows/network-infrastructure-execution-workflow"
assert ROOT.name == "workflow-architect-run-scoped-handoff"


def sha(path):
    return hashlib.sha256(
        os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    ).hexdigest()


def git(*args, root=ROOT):
    return subprocess.check_output(["git", "-C", str(root), *args])


def purpose(name):
    path = Path(name)
    if (
        "-evidence" in path.parts[0]
        or name.startswith("checkpoint")
        or name == "RUN-SCOPED-HANDOFF-PROGRESS.md"
    ):
        return "evidence"
    platforms = {".agents", ".claude", ".opencode", ".codex", ".github", ".devin"}
    if (
        platforms.intersection(path.parts)
        or name.endswith(".devin.md")
        or "scripts/enforcement" in name
    ):
        return "generated"
    if (
        path.name in {"run-binding.md", "enforcement.md", "dispatch-gate.md"}
        and path.parent.name != "enforcement"
    ):
        return "generated"
    return "docs" if path.suffix == ".md" else "code-and-tests"


def run(command, cwd=ROOT):
    result = subprocess.run(
        command, cwd=cwd, env=env, text=True, capture_output=True, timeout=45
    )
    (OUT / f"command-{len(results):02}.txt").write_text(result.stdout + result.stderr)
    results.append(dict(command=command, cwd=str(cwd), returncode=result.returncode))
    return result.returncode


def generated():
    paths = set()
    for root in [ROOT, META, NET]:
        for directory in [
            ".agents",
            ".claude",
            ".opencode",
            ".codex",
            ".github",
            ".devin",
            "scripts/enforcement",
        ]:
            paths.update(
                p
                for p in (root / directory).rglob("*")
                if p.is_file() or p.is_symlink()
            )
        paths.update(root.glob("*.devin.md"))
        paths.update(p for p in (root / "enforcement").rglob("*") if p.is_file())
        paths.update(
            root / name
            for name in ["enforcement.md", "dispatch-gate.md", "run-binding.md"]
            if (root / name).is_file()
        )
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}


snapshot = json.loads(
    (ROOT / "checkpoint1-evidence/snapshot-manifest.json").read_text()
)["files"]
name = "generated-workflows/network-infrastructure-execution-workflow/scripts/preflight-task-check.sh"
expected = next(row["sha256"] for row in snapshot if row["path"] == name)
assert sha(MAIN / name) == expected
shutil.copy2(MAIN / name, ROOT / name)
local_config = (NET / "enforcement/workflow-config.json").read_bytes()
local_policy = sha(NET / "enforcement/network_policy.py")
results = []
with tempfile.TemporaryDirectory(dir=OUT, prefix="fixtures-") as scratch:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=scratch)
    generation = [
        [sys.executable, "-B", "scripts/sync-platform-configs.py"],
        [
            sys.executable,
            "-B",
            "scripts/sync-platform-configs.py",
            "--package",
            str(META),
        ],
        [
            sys.executable,
            "-B",
            "scripts/sync-platform-configs.py",
            "--package",
            str(NET),
            "--runtime-source",
            str(META / "enforcement"),
        ],
    ]
    for command in generation:
        run(command)
    first = generated()
    for command in generation:
        run(command)
    second = generated()
    run([sys.executable, "-B", "scripts/validate-package.py", str(META)])
    run(
        [
            sys.executable,
            "-B",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            str(META / "tests/test_regression.py"),
            str(META / "tests/test_idempotency.py"),
            str(META / "tests/test_frontmatter.py"),
            str(META / "tests/test_sync_identity.py"),
            "-q",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            str(META / "tests/test_dispatch_contract.py"),
            "-k",
            "broad_rule",
            "-q",
        ]
    )
    for test in [
        "test_run_store.py",
        "test_effect_lifecycle.py",
        "test_runtime_paths.py",
    ]:
        run(
            [
                sys.executable,
                "-B",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(META / "tests"),
                "-p",
                test,
            ]
        )
    run(["bun", "test", str(META / "tests/runtime_plugin.test.ts")])
    run(
        [sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "tests", "-q"],
        NET,
    )
    run([sys.executable, "-B", "scripts/validate-package.py", str(NET)], NET)
    run(["git", "diff", "--check"])
(OUT / "commands.json").write_text(json.dumps(results, indent=2))
(OUT / "generation.json").write_text(
    json.dumps(
        dict(
            identical=first == second,
            files=len(first),
            first_sha=hashlib.sha256(
                json.dumps(first, sort_keys=True).encode()
            ).hexdigest(),
            second_sha=hashlib.sha256(
                json.dumps(second, sort_keys=True).encode()
            ).hexdigest(),
            network_config_unchanged=local_config
            == (NET / "enforcement/workflow-config.json").read_bytes(),
            network_policy_unchanged=local_policy
            == sha(NET / "enforcement/network_policy.py"),
        ),
        indent=2,
    )
)
baseline = json.loads(
    (ROOT / "checkpoint1-evidence/main-inventory-before.json").read_text()
)
changed = [p for p, v in baseline.items() if sha(MAIN / p) != v["sha256"]]
changed += [r["path"] for r in snapshot if sha(MAIN / r["path"]) != r["sha256"]]
status_equal = (
    git("status", "--porcelain=v1", "--untracked-files=all", root=MAIN)
    == (ROOT / "checkpoint1-evidence/main-status-before.txt").read_bytes()
)
verified_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
report = dict(
    base=git("rev-parse", "HEAD").decode().strip(),
    main_changed=sorted(set(changed)),
    main_status_equal=status_equal,
    verified_at=verified_time,
    failed_commands=[i for i, r in enumerate(results) if r["returncode"]],
    generation_identical=first == second,
)
(OUT / "preservation.json").write_text(json.dumps(report, indent=2))
imports = {row["path"]: row["sha256"] for row in snapshot}
fixture_root = META / "tests/fixtures/legacy-hooks"
fixture_sources = (
    json.loads((fixture_root / "provenance.json").read_text())
    if (fixture_root / "provenance.json").exists()
    else {}
)
for item in fixture_sources.values():
    imports[str((fixture_root / item["fixture"]).relative_to(ROOT))] = item["sha256"]
tracked = set(git("ls-files", "-z").decode().split("\0")) - {""}
paths = {
    str(p.relative_to(ROOT))
    for p in ROOT.rglob("*")
    if (p.is_file() or p.is_symlink())
    and ".git" not in p.relative_to(ROOT).parts
    and "__pycache__" not in p.parts
}
ignored = subprocess.run(
    ["git", "check-ignore", "--stdin", "-z"],
    cwd=ROOT,
    input="\0".join(sorted(paths)) + "\0",
    text=True,
    capture_output=True,
).stdout.split("\0")
manifest = []
for name in sorted(paths | tracked):
    if name in {
        str((OUT / "candidate-manifest.json").relative_to(ROOT)),
        str((OUT / "file-inventory.json").relative_to(ROOT)),
    }:
        continue
    path = ROOT / name
    current = sha(path) if path.exists() or path.is_symlink() else None
    base = (
        hashlib.sha256(git("show", "HEAD:" + name)).hexdigest()
        if name in tracked
        else None
    )
    imported = imports.get(name)
    if current != (imported if imported is not None else base):
        manifest.append(
            dict(
                path=name,
                category="tracked"
                if name in tracked
                else "ignored"
                if name in ignored
                else "untracked",
                base_sha256=base,
                import_sha256=imported,
                candidate_sha256=current,
                purpose=purpose(name),
                baseline_origin="import"
                if imported is not None
                else "HEAD"
                if base is not None
                else "new",
            )
        )
groups = {key: [] for key in ["code-and-tests", "docs", "generated", "evidence"]}
for row in manifest:
    groups[row["purpose"]].append(row["path"])
inventory_name = str((OUT / "file-inventory.json").relative_to(ROOT))
groups["evidence"].append(inventory_name)
import_rows = [
    dict(
        path=p,
        original_sha256=h,
        current_sha256=sha(ROOT / p),
        changed=sha(ROOT / p) != h,
        purpose=purpose(p),
    )
    for p, h in sorted(imports.items())
]
inventory = dict(
    changes_by_purpose=groups,
    counts={k: len(v) for k, v in groups.items()},
    baseline_imports=import_rows,
    settings_fixture_provenance=fixture_sources,
    note="Baseline imports are separately enumerated, not all newly authored files. The manifest self-hash is excluded.",
)
(OUT / "file-inventory.json").write_text(json.dumps(inventory, indent=2))
manifest.append(
    dict(
        path=inventory_name,
        category="untracked",
        base_sha256=None,
        import_sha256=None,
        candidate_sha256=sha(OUT / "file-inventory.json"),
        purpose="evidence",
        baseline_origin="new",
    )
)
report = dict(
    base=git("rev-parse", "HEAD").decode().strip(),
    main_changed=sorted(set(changed)),
    main_status_equal=status_equal,
    verified_at=verified_time,
    failed_commands=[i for i, r in enumerate(results) if r["returncode"]],
    generation_identical=first == second,
)
(OUT / "preservation.json").write_text(json.dumps(report, indent=2))
(OUT / "candidate-manifest.json").write_text(
    json.dumps(
        dict(
            self_excluded=str((OUT / "candidate-manifest.json").relative_to(ROOT)),
            baseline="HEAD plus provenance-bound checkpoint1 imports",
            files=manifest,
        ),
        indent=2,
    )
)
print(json.dumps(report, indent=2))
assert not changed and status_equal and first == second
