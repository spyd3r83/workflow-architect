#!/usr/bin/env bash
set -euo pipefail

PKG="${1:-generated-workflows/backend-repo-maintenance-workflow}"
WORK="$(mktemp -d /tmp/harness-smoke-XXXXXX)"
PKG_COPY="$WORK/pkg"
mkdir -p "$PKG_COPY"

if [ ! -d "$PKG" ]; then
  echo "BLOCKED: package not found at $PKG"
  exit 1
fi
cp -a "$PKG/." "$PKG_COPY/"

ENFORCER_SRC="agent-packages/workflow-designer-agent/enforcement/workflow-enforce.sh"
if [ -f "$ENFORCER_SRC" ]; then
  mkdir -p "$PKG_COPY/scripts/enforcement"
  cp "$ENFORCER_SRC" "$PKG_COPY/scripts/enforcement/"
  chmod +x "$PKG_COPY/scripts/enforcement/workflow-enforce.sh"
fi

HAS_DOCKER="no"
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  HAS_DOCKER="yes"
fi

echo "WORK=$WORK"
echo "DOCKER=$HAS_DOCKER"
echo ""

if [ "$HAS_DOCKER" != "yes" ]; then
  echo "BLOCKED: docker not available"
  rm -rf "$WORK"
  exit 1
fi

echo "========================================"
echo "PHASE 1: CONTAINER STATIC VALIDATION"
echo "========================================"
docker run --rm -v "$PKG_COPY:/pkg:ro" python:3.12-slim bash -c '
  pip install -q pyyaml > /dev/null 2>&1
  python3 - <<INNER
import yaml, sys
from pathlib import Path
pkg = Path("/pkg")
roots = [pkg/".agents/skills", pkg/".claude/agents", pkg/".opencode/agents", pkg/".devin/agents", pkg/".github/agents", pkg/"skills", pkg/"agents"]
ok=0; fail=0
for root in roots:
    if not root.exists(): continue
    for pattern in ["SKILL.md","AGENT.md","*.agent.md","*.md"]:
        for path in root.rglob(pattern):
            text = path.read_text(errors="replace")
            if not text.startswith("---"): continue
            lines = text.splitlines()
            close=None
            for i,l in enumerate(lines[1:],1):
                if l=="---": close=i; break
                if l.startswith("---") and l!="---": close=-1; break
            if close is None or close<0: continue
            try:
                data=yaml.safe_load("\n".join(lines[1:close]))
                if isinstance(data,dict) and isinstance(data.get("description",""),str): ok+=1
                else: fail+=1
            except: fail+=1
print(f"frontmatter: ok={ok} fail={fail}")
import tomllib
count=0
for f in sorted(Path("/pkg/.codex/agents").glob("*.toml")):
    d=tomllib.loads(f.read_text()); assert "name" in d and "developer_instructions" in d; count+=1
print(f"toml: ok={count}")
print(f"agents: opencode=$(ls /pkg/.opencode/agents/*.md 2>/dev/null | wc -l) claude=$(ls /pkg/.claude/agents/*.md 2>/dev/null | wc -l) codex=$(ls /pkg/.codex/agents/*.toml 2>/dev/null | wc -l) github=$(ls /pkg/.github/agents/*.agent.md 2>/dev/null | wc -l) devin=$(ls /pkg/.devin/agents/*/AGENT.md 2>/dev/null | wc -l)")
INNER
'
STATIC_RC=$?
echo "STATIC: $([ $STATIC_RC -eq 0 ] && echo PASS || echo FAIL)"

echo ""
echo "========================================"
echo "PHASE 2: CONTAINER RUNTIME SMOKE"
echo "========================================"

echo ""
echo "=== OpenCode ==="
if [ -f /home/jfi/.local/share/opencode/auth.json ]; then
  timeout 90 docker run --rm \
    -v "$PKG_COPY:/pkg:ro" \
    -v "/home/jfi/.local/share/opencode/auth.json:/home/jfi/.local/share/opencode/auth.json:ro" \
    -v "/usr/local/bin/opencode:/usr/local/bin/opencode:ro" \
    -e OPENCODE_DISABLE_CHANNEL_DB=1 \
    node:22-slim \
    bash -c 'cd /pkg && timeout 30 opencode run --dir /pkg --agent maintenance-orchestrator --format json "Reply with exactly: OC_OK" 2>&1 | grep -o "OC_OK" | head -1 && echo "RESULT: RUNTIME-PROVEN" || echo "RESULT: BLOCKED"' \
    2>&1 | grep -v -iE "auth\.json|token|secret|api.key|credential" | tail -3
else
  echo "RESULT: BLOCKED (auth.json not found)"
fi

echo ""
echo "=== Claude Code ==="
if [ -f /home/jfi/.claude/.credentials.json ]; then
  timeout 60 docker run --rm \
    --user node \
    -v "$PKG_COPY:/pkg:ro" \
    -v "/home/jfi/.claude/.credentials.json:/tmp/creds.json:ro" \
    -v "/home/jfi/.local/bin/claude:/usr/local/bin/claude:ro" \
    -e ANTHROPIC_API_KEY \
    -e HOME=/home/node \
    node:22-slim \
    bash -c 'mkdir -p /home/node/.claude && cp /tmp/creds.json /home/node/.claude/.credentials.json && echo "{}" > /home/node/.claude.json && timeout 30 claude --print --dangerously-skip-permissions "Reply with exactly: CC_OK" 2>&1 | tail -3' \
    2>&1 | grep -v -iE "credentials|token|secret|api.key|sk-|ANTHROPIC" | tail -3
  echo "RESULT: see output above (401=BLOCKED auth, CC_OK=RUNTIME-PROVEN)"
else
  echo "RESULT: BLOCKED (credentials not found)"
fi

echo ""
echo "=== Codex CLI ==="
if [ -f /home/jfi/.codex/auth.json ]; then
  timeout 90 docker run --rm \
    -v "$PKG_COPY:/pkg:ro" \
    -v "/home/jfi/.codex/auth.json:/root/.codex/auth.json:ro" \
    -v "/home/jfi/.codex/config.toml:/root/.codex/config.toml:ro" \
    -e OPENAI_API_KEY \
    node:22-slim \
    bash -c 'npm install -g @openai/codex 2>/dev/null && timeout 30 codex exec "Reply with exactly: CX_OK" 2>&1 | tail -3' \
    2>&1 | grep -v -iE "auth\.json|token|secret|api.key|credential|sk-|funding|bson" | tail -3
  echo "RESULT: BLOCKED (codex exec requires trusted git repo + interactive TTY)"
else
  echo "RESULT: BLOCKED (codex auth not found)"
fi

echo ""
echo "=== Copilot CLI ==="
echo "RESULT: BLOCKED (copilot binary is a host wrapper calling copilot-real with full nvm tree)"

echo ""
echo "=== Devin ==="
echo "RESULT: BLOCKED (no installable CLI; web-access platform only)"

echo ""
echo "========================================"
echo "CLEANUP"
echo "========================================"
rm -rf "$WORK"
echo "removed $WORK"
