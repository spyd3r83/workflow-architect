# Changelog — Workflow Designer Agent

Every improvement to the Workflow Designer Agent package is recorded here. Entries are append-only — never deleted or modified.

## Version 1.0.0 — 2025-07-03

- **Initial release**: Complete Workflow Designer Agent package with 18-phase workflow, 9 agents, 10 skills, 5 prompts, 18 templates, 2 examples, FMEA, traceability matrix, reliability plan, source-log, requirements, regression tests, idempotency tests, self-improvement protocol.
- **Reliability mechanisms**: Independent verification (Phase 11.5), Oracle-in-the-loop gates (3), quantitative QC (15 criteria), deterministic validation (validate-package.py), idempotency protocol, rollback protocol, error budget (< 0.1%).
- **Platform compatibility**: OpenCode, Claude Code, Codex CLI, Copilot CLI, Devin — via sync-platform-configs.py.
- **Slash commands**: /flowstart, /resume, /maintain across all 5 platforms.
- **Self-improvement**: /update command with improvement-protocol.md, defect-patterns.md, and this changelog.

## Unreleased — 2026-10-01 — Run-scoped handoff repair candidate

- Replaced singleton writers with explicit run/session binding, CAS, typed effects, authenticated operator actions and scoped host adapters.
- Production generation installs complete runtime dependencies while retaining package-local phase/specialist policy. Agent generation distinguishes coordinator dispatch from task:false leaf work; validator rejects broad stop rules.
- Added lifetime admission refusal to bound permanent retirement markers without reusing run IDs.
- Verification is recorded in the isolated candidate's authoritative progress/evidence. Independent focused QC/red-team is pending; this entry is not approval, release numbering, live compatibility certification or activation authority.

## Changelog Entry Format

```
## Version X.Y.Z — YYYY-MM-DD

### Changes
- **[file]**: <what changed>

### Trigger
<what triggered this improvement — defect ID, pattern, user request>

### Oracle Review
- Proposals: N
- Approved: N
- Rejected: N (reasoning)

### Test Results
- validate-package.py: PASS (N/N)
- Regression: PASS (N/N)
- Idempotency: PASS (N/N)

### Risk Assessment
<low/medium/high — with justification>

### Rollback Status
N/A | Rolled back (reason)
```
