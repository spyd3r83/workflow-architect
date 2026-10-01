from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "checkpoint3d-evidence"
assert ROOT.name == "workflow-architect-run-scoped-handoff"
commands = [
    (
        ROOT,
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "agent-packages/workflow-designer-agent/tests",
            "-p",
            name,
        ],
    )
    for name in [
        "test_run_store.py",
        "test_effect_lifecycle.py",
        "test_runtime_paths.py",
    ]
]
commands.append(
    (
        ROOT,
        [
            "bun",
            "test",
            "agent-packages/workflow-designer-agent/tests/runtime_plugin.test.ts",
        ],
    )
)
commands.append(
    (
        ROOT / "generated-workflows/network-infrastructure-execution-workflow",
        [
            sys.executable,
            "-B",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "tests/test_enforcement_alignment.py",
            "-k",
            "enforcement_alignment_passes or workflow_configs_match",
        ],
    )
)
results = []
for index, (cwd, command) in enumerate(commands):
    result = subprocess.run(
        command, cwd=cwd, text=True, capture_output=True, timeout=30
    )
    (OUT / f"test-{index}.txt").write_text(result.stdout + result.stderr)
    results.append(dict(command=command, cwd=str(cwd), returncode=result.returncode))
(OUT / "tests.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
assert all(result["returncode"] == 0 for result in results)
subprocess.run(
    [sys.executable, "-B", "checkpoint3c_snapshot.py", "3d"], cwd=ROOT, check=True
)
