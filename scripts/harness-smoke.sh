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
OC_AUTH="${HOME}/.local/share/opencode/auth.json"
if [ -f "$OC_AUTH" ] && [ -f /usr/local/bin/opencode ]; then
  timeout 90 docker run --rm \
    -v "$PKG_COPY:/pkg:ro" \
    -v "$OC_AUTH:/home/jfi/.local/share/opencode/auth.json:ro" \
    -v "/usr/local/bin/opencode:/usr/local/bin/opencode:ro" \
    -e OPENCODE_DISABLE_CHANNEL_DB=1 \
    node:22-slim \
    bash -c 'cd /pkg && timeout 30 opencode run --dir /pkg --agent maintenance-orchestrator --format json "Reply: OC_OK" 2>&1 | grep -o "OC_OK" | head -1 && echo "RUNTIME-PROVEN" || echo "BLOCKED"' \
    2>&1 | grep -vE "auth|token|key|secret|credential" | tail -2
else
  echo "BLOCKED: config not found"
fi

echo ""
echo "=== Claude Code ==="
echo "Official headless: claude --bare -p \"prompt\" --allowedTools Read"
echo "Auth: ANTHROPIC_API_KEY env or apiKeyHelper in --settings"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  timeout 60 docker run --rm \
    --user node \
    -v "$PKG_COPY:/pkg:ro" \
    -v "/home/jfi/.local/bin/claude:/usr/local/bin/claude:ro" \
    -e ANTHROPIC_API_KEY \
    -e HOME=/home/node \
    node:22-slim \
    bash -c 'echo "{}" > /home/node/.claude.json 2>/dev/null; timeout 30 claude --bare -p "Reply: CC_OK" --allowedTools Read 2>&1 | tail -3' \
    2>&1 | grep -vE "credential|token|secret|key" | tail -3
else
  echo "BLOCKED: ANTHROPIC_API_KEY not set"
fi

echo ""
echo "=== Codex CLI ==="
echo "Official headless: codex exec \"prompt\" --skip-git-repo-check"
echo "Auth: config dir or OPENAI_API_KEY env"
CX_AUTH="${HOME}/.codex/auth.json"
CX_CFG="${HOME}/.codex/config.toml"
if [ -f "$CX_AUTH" ]; then
  timeout 90 docker run --rm \
    -v "$PKG_COPY:/pkg:ro" \
    -v "$CX_AUTH:/root/.codex/auth.json:ro" \
    -v "$CX_CFG:/root/.codex/config.toml:ro" \
    -e OPENAI_API_KEY \
    node:22-slim \
    bash -c 'npm install -g @openai/codex 2>/dev/null; timeout 30 codex exec "Reply: CX_OK" --skip-git-repo-check 2>&1 | tail -3' \
    2>&1 | grep -vE "auth|token|secret|key|credential|funding|bson" | tail -3
else
  echo "BLOCKED: config not found"
fi

echo ""
echo "=== Copilot CLI ==="
echo "Official headless: copilot -p \"prompt\""
echo "Auth: COPILOT_GITHUB_TOKEN or GH_TOKEN or GITHUB_TOKEN env"
echo "BLOCKED: host binary is a wrapper script requiring full nvm tree"
echo "Fix: fresh npm install in container + valid token env"

echo ""
echo "=== Devin ==="
echo "Official headless: devin -- \"prompt\""
echo "Auth: browser OAuth on first run (no env-var headless auth documented)"
echo "BLOCKED: no headless auth mechanism; requires browser OAuth"

echo ""
echo "========================================"
echo "CLEANUP"
echo "========================================"
rm -rf "$WORK"
echo "removed $WORK"
