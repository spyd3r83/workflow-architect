# Harness Compatibility and Runtime QA Matrix

Authoritative per-harness QA status. Container smoke is the acceptance path; host runs are exploratory only.

## Status Definitions

| Status | Meaning |
|--------|---------|
| **RUNTIME-PROVEN** | Live runtime evidence from a disposable container with auth safely mounted via env or read-only config |
| **BLOCKED** | Cannot runtime-test in container: auth unavailable, binary wrapper, CLI missing, or platform limitation |

## Per-Harness Matrix

### OpenCode

| Field | Value |
|-------|-------|
| **Status** | **RUNTIME-PROVEN** |
| **Official headless path** | `opencode run --dir <pkg> --agent <name> --format json "prompt"` |
| **Auth mechanism** | Provider credentials in config dir (env-injected in container) |
| **Container test** | `node:22-slim` + binary mount + config mounted read-only; `opencode run --agent maintenance-orchestrator` responded successfully |
| **CI can prove runtime?** | No — requires local install + provider access |

### Claude Code

| Field | Value |
|-------|-------|
| **Status** | **BLOCKED** |
| **Official headless path** | `claude --bare -p "prompt" --allowedTools "Read"` ([docs](https://code.claude.com/docs/en/headless)) |
| **Auth mechanism** | `ANTHROPIC_API_KEY` env var or `apiKeyHelper` in `--settings` JSON (bare mode skips OAuth/keychain) |
| **Container test** | `node:22-slim --user node` + binary mount; `claude --print` returned 401 auth error |
| **Exact blocker** | Available API key is expired or invalid |
| **CI can prove runtime?** | No — requires valid `ANTHROPIC_API_KEY` |

### OpenAI Codex CLI

| Field | Value |
|-------|-------|
| **Status** | **BLOCKED** |
| **Official headless path** | `codex exec "prompt" --skip-git-repo-check` ([docs](https://learn.chatgpt.com/docs/codex/non-interactive-mode)) |
| **Auth mechanism** | OAuth or API key in config dir; env `OPENAI_API_KEY` |
| **Container test** | `node:22-slim` + npm `@openai/codex` + config mounted read-only; `codex exec` returned "Not inside a trusted directory" (needs `--skip-git-repo-check`) |
| **Exact blocker** | Container read-only mount cannot satisfy git trust; retry with `--skip-git-repo-check` flag needed |
| **CI can prove runtime?** | No — requires valid OpenAI credentials |

### GitHub Copilot CLI

| Field | Value |
|-------|-------|
| **Status** | **BLOCKED** |
| **Official headless path** | `copilot -p "prompt"` with env auth (`COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, or `GITHUB_TOKEN`) ([docs](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)) |
| **Auth mechanism** | Fine-grained PAT (v2) or OAuth token via env var; classic PATs not supported |
| **Container test** | Host binary is a bash wrapper calling `copilot-real` with full nvm dependency tree; cannot isolate in container without replicating host Node.js installation |
| **Exact blocker** | Binary is a host-specific wrapper; needs `npm install -g` fresh install in container + valid `COPILOT_GITHUB_TOKEN` |
| **CI can prove runtime?** | No — requires Copilot subscription + token |

### Devin

| Field | Value |
|-------|-------|
| **Status** | **BLOCKED** |
| **Official headless path** | `devin -- "prompt"` after `curl -fsSL https://cli.devin.ai/install.sh \| bash` ([docs](https://docs.devin.ai/cli)) |
| **Auth mechanism** | Browser-based OAuth on first run; no env-var token documented for headless |
| **Container test** | Devin CLI not installed; install script available but requires interactive browser auth |
| **Exact blocker** | No headless auth mechanism documented; first-run requires browser OAuth |
| **CI can prove runtime?** | No — requires Devin account + browser auth |

## Summary Table

| Harness | Official headless path | Container static | Container runtime | Status |
|---------|----------------------|-----------------|-------------------|--------|
| **OpenCode** | `opencode run --agent <name>` | PASS | PASS | **RUNTIME-PROVEN** |
| **Claude Code** | `claude --bare -p` + `ANTHROPIC_API_KEY` | PASS | BLOCKED | **BLOCKED** |
| **Codex CLI** | `codex exec --skip-git-repo-check` | PASS | BLOCKED | **BLOCKED** |
| **Copilot CLI** | `copilot -p` + `COPILOT_GITHUB_TOKEN` | PASS | BLOCKED | **BLOCKED** |
| **Devin** | `devin --` (needs browser OAuth) | PASS | BLOCKED | **BLOCKED** |

## Container Static Validation (all harnesses)

Validated in `python:3.12-slim` container without credentials:

- Frontmatter: all files valid
- TOML: all Codex agents valid
- Hook syntax: all Claude hooks valid
- Agent counts: consistent across all platforms

## CI Validation Coverage

CI validates without secrets:
- pytest suite (enforcer, frontmatter, regression, harness matrix)
- `validate-package.py` (structural checks + `harness_matrix_exists`)
- `validate_frontmatter.py` (recursive YAML scan)

CI **cannot** validate any harness runtime behavior.

## Container Smoke Script

`scripts/harness-smoke.sh <package-path>` runs:
- Phase 1: static validation in `python:3.12-slim` (no auth)
- Phase 2: runtime smoke in `node:22-slim` with read-only auth mounts (requires Docker + existing auth)

Auth is mounted read-only and never printed or committed.
