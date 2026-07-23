# Harness Compatibility and Runtime QA Matrix

Authoritative per-harness QA status. Container smoke is the acceptance path.

## Oracle-Reviewed Classification (2026-07-16)

Oracle verdict: REJECT blanket release. Only runtime-proven harnesses ship in the supported release matrix. Others are experimental or excluded.

## Release Tiers

| Tier | Definition | Ship in release? |
|------|-----------|-----------------|
| **Tier 1: Release-Ready** | Container runtime evidence exists | Yes |
| **Tier 2: Experimental** | Artifacts valid, runtime pending credentials | Draft PRs only |
| **Tier 3: Unsupported** | No headless auth mechanism | Excluded; roadmap note |

## Per-Harness Status

### OpenCode — Tier 1: Release-Ready

| Field | Value |
|-------|-------|
| **Official headless path** | `opencode run --dir <pkg> --agent <name> --format json "prompt"` |
| **Container evidence** | Orchestrator responded in `node:22-slim` container with config mounted read-only |
| **Auth** | Provider credentials via config dir (env-injected in container) |
| **Status** | **RUNTIME-PROVEN** |

### Claude Code — Tier 2: Experimental

| Field | Value |
|-------|-------|
| **Official headless path** | `claude --bare -p "prompt" --allowedTools Read` |
| **Container evidence** | Static artifacts valid; runtime returned 401 auth error |
| **Blocker** | Valid `ANTHROPIC_API_KEY` required |
| **Auth pattern** | `ANTHROPIC_API_KEY` via GitHub Secret; bare mode skips keychain |
| **Status** | **BLOCKED — needs valid credentials** |

### Codex CLI — Tier 2: Experimental

| Field | Value |
|-------|-------|
| **Official headless path** | `codex exec "prompt" --skip-git-repo-check` |
| **Container evidence** | Static TOML valid; runtime needs `--skip-git-repo-check` flag |
| **Blocker** | Retry with correct flags; verify OpenAI credentials valid |
| **Auth pattern** | Config dir or `OPENAI_API_KEY` via GitHub Secret |
| **Status** | **BLOCKED — needs flag retry** |

### Copilot CLI — Tier 2: Experimental

| Field | Value |
|-------|-------|
| **Official headless path** | `copilot -p "prompt"` with env token |
| **Container evidence** | Static artifacts valid; host binary is wrapper script |
| **Blocker** | Fresh npm install in container + fine-grained PAT (v2) required |
| **Auth pattern** | `COPILOT_GITHUB_TOKEN` via GitHub Secret (fine-grained PAT only) |
| **Status** | **BLOCKED — needs PAT + fresh install** |

### Devin — Tier 3: Unsupported (Excluded from Release)

| Field | Value |
|-------|-------|
| **Official headless path** | `devin -- "prompt"` (requires browser OAuth on first run) |
| **Container evidence** | Static artifacts valid; no headless auth mechanism exists |
| **Blocker** | Browser OAuth required; no env-var headless auth documented |
| **Status** | **EXCLUDED — no CI injection possible** |

## Summary Table

| Harness | Tier | Container static | Container runtime | Release status |
|---------|------|-----------------|-------------------|----------------|
| **OpenCode** | 1 | PASS | **PASS** | **Release-ready** |
| **Claude Code** | 2 | PASS | BLOCKED | Experimental draft |
| **Codex CLI** | 2 | PASS | BLOCKED | Experimental draft |
| **Copilot CLI** | 2 | PASS | BLOCKED | Experimental draft |
| **Devin** | 3 | PASS | BLOCKED | **Excluded** |

## CI Gates (per Oracle)

| Gate | Blocking? | Scope |
|------|-----------|-------|
| Source lint / format / type check | **Blocking** | All source |
| Manifest schema validation | **Blocking** | Generated manifests |
| Secret/credential scan | **Blocking** | All artifacts |
| Runtime smoke (Tier 1) | **Blocking** | OpenCode only |
| Frontmatter + TOML parse | **Blocking** | All harness files |
| Runtime smoke (Tier 2) | Advisory | Claude, Codex, Copilot |

## Container Smoke Script

`scripts/harness-smoke.sh <package-path>` runs Phase 1 (static) and Phase 2 (runtime) in disposable containers. Auth mounted read-only; never printed or committed.

CI cannot validate any harness runtime behavior without credentials injected via GitHub Secrets.
