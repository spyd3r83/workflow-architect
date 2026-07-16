# Harness Compatibility and Runtime QA Matrix

This document defines the supported artifact files, runtime contract, smoke-test method, and current evidence status for each target harness. It is the authoritative source for what is runtime-proven versus static-only.

## Evidence Policy

Authoritative acceptance evidence comes from **disposable container smoke** (`scripts/harness-smoke.sh`), not from host-installed tools. Host exploratory notes may appear in per-harness sections but are **non-authoritative**.

No credentials (`auth.json`, API keys, tokens, cookies) are ever copied into the repo or committed. Auth files are mounted **read-only** into containers at their expected paths. No secret values are read, printed, or logged.

## Container Smoke Result (2026-07-16)

`scripts/harness-smoke.sh` ran against a disposable copy of the backend maintenance package.

### Phase 1: Static validation (python:3.12-slim container)

| Check | Result |
|-------|--------|
| YAML frontmatter scan | **PASS** — 162 files, 0 failures |
| TOML parse (Codex agents) | **PASS** — 19 agents |
| Agent counts | 19 per harness (OpenCode, Claude, Codex, GitHub, Devin) |
| Skills | 12 |

### Phase 2: Container runtime smoke (node:22-slim + read-only auth mounts)

| Harness | Container image | Auth mount | Smoke output | Status |
|---------|----------------|------------|-------------|--------|
| OpenCode | node:22-slim + opencode binary | `auth.json:ro` | `OC_OK` confirmed via `opencode run --agent maintenance-orchestrator` | **RUNTIME-PROVEN** |
| Claude Code | node:22-slim + claude binary, `--user node` | `.credentials.json:ro` + `ANTHROPIC_API_KEY` env | `401 Invalid authentication credentials` | **BLOCKED** |
| Codex CLI | node:22-slim, npm-installed codex | `auth.json:ro` + `config.toml:ro` + `OPENAI_API_KEY` env | `Not inside a trusted directory and --skip-git-repo-check was not specified` | **BLOCKED** |
| Copilot CLI | N/A | N/A | Binary is host wrapper (`copilot-real` + nvm tree); cannot isolate in container | **BLOCKED** |
| Devin | N/A | N/A | No installable CLI; web-access platform | **BLOCKED** |

## Status Definitions

| Status | Meaning |
|--------|---------|
| **RUNTIME-PROVEN** | Live runtime evidence from a disposable container with auth safely mounted read-only |
| **BLOCKED** | Cannot runtime-test in container: auth failure, binary wrapper, missing CLI, or platform limitation |

## Per-Harness Detail

### OpenCode

| Field | Value |
|-------|-------|
| **Status** | **RUNTIME-PROVEN** |
| **Container evidence** | `node:22-slim` container with opencode binary mounted + `auth.json` mounted read-only. `opencode run --agent maintenance-orchestrator` successfully loaded package config, registered agents, and responded to prompt. |
| **Binary** | `/usr/local/bin/opencode` (mounted from host) |
| **Auth mechanism** | `~/.local/share/opencode/auth.json` mounted read-only at same path in container |

### Claude Code

| Field | Value |
|-------|-------|
| **Status** | **BLOCKED** |
| **Container evidence** | `node:22-slim` as `--user node`, claude binary mounted, `.credentials.json` copied to writable home. `claude --print --dangerously-skip-permissions` returned `401 Invalid authentication credentials`. |
| **Blocker** | Anthropic API key is expired or invalid. The env var is set but credentials rejected. No secret values were exposed. |

### Codex CLI

| Field | Value |
|-------|-------|
| **Status** | **BLOCKED** |
| **Container evidence** | `node:22-slim` with `@openai/codex` npm-installed (v0.144.5), `auth.json` + `config.toml` mounted read-only. `codex exec` returned: "Not inside a trusted directory and --skip-git-repo-check was not specified." |
| **Blocker** | Codex requires a trusted git repository directory and interactive TTY approval. Container smoke with read-only mounted package cannot satisfy git trust requirement without modifying the package. |

### GitHub Copilot CLI

| Field | Value |
|-------|-------|
| **Status** | **BLOCKED** |
| **Container evidence** | Copilot binary on host is a bash wrapper (`#!/usr/bin/env bash`) that calls `copilot-real` with full nvm dependency tree. Mounting just the wrapper produces "No such file or directory" for `copilot-real`. |
| **Blocker** | Binary is a host-specific wrapper requiring full nvm/node_modules tree. Cannot be isolated in a container without replicating the entire host Node.js installation. |

### Devin

| Field | Value |
|-------|-------|
| **Status** | **BLOCKED** |
| **Container evidence** | No installable CLI exists. Devin is a web-access platform requiring browser session authentication at devin.ai. |
| **Blocker** | No programmatic CLI for container isolation. Playbook files (`.devin.md`) are generated and validated statically. |

## Summary Table

| Harness | Container static | Container runtime | Status |
|---------|-----------------|-------------------|--------|
| **OpenCode** | PASS (19 agents, 12 skills) | **PASS** — orchestrator responded in container | **RUNTIME-PROVEN** |
| **Claude Code** | PASS (19 agents, hooks valid) | BLOCKED — 401 auth | **BLOCKED** |
| **Codex CLI** | PASS (19 TOML) | BLOCKED — git trust required | **BLOCKED** |
| **Copilot CLI** | PASS (19 agents) | BLOCKED — wrapper binary | **BLOCKED** |
| **Devin** | PASS (19 AGENT.md, 4 playbooks) | BLOCKED — no CLI | **BLOCKED** |

## CI Validation Coverage

CI (`.github/workflows/enterprise-validation.yml`) validates without secrets:
- pytest suite (enforcer, frontmatter, regression, harness matrix)
- `validate-package.py` (54+ structural checks)
- `validate_frontmatter.py` (recursive YAML scan)

CI **cannot** validate:
- Harness runtime behavior
- Agent discovery by harness runtime
- Hook execution
- Enforcer plugin load

## Container Smoke Script

`scripts/harness-smoke.sh <package-path>` runs:
- Phase 1: static validation in `python:3.12-slim` (no auth needed)
- Phase 2: runtime smoke in `node:22-slim` with read-only auth mounts (requires Docker + existing auth configs)

Auth files are mounted `:ro` and never read, printed, or committed.

## Honest Claims Policy

Generated packages **must not** claim runtime support for a harness unless there is container runtime evidence in this matrix. `validate-package.py` `harness_matrix_exists` enforces this file is present.
