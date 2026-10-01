from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("/home/jfi/GitHub/workflow-architect")
assert ROOT.name == "workflow-architect-run-scoped-handoff"
OUT = ROOT / "agent-packages/workflow-designer-agent/tests/fixtures/legacy-hooks"
baseline = json.loads(
    (ROOT / "checkpoint1-evidence/main-inventory-before.json").read_text()
)
sources = {
    "root": ".claude/settings.json",
    "network": "generated-workflows/network-infrastructure-execution-workflow/.claude/settings.json",
}
OUT.mkdir(parents=True, exist_ok=True)
provenance = {}
for name, path in sources.items():
    data = (MAIN / path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == baseline[path]["sha256"], (
        "Original settings drifted from checkpoint1"
    )
    (OUT / f"{name}.json").write_bytes(data)
    provenance[name] = dict(source=path, sha256=digest, fixture=f"{name}.json")
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
print(json.dumps(provenance, indent=2))
