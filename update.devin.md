---
name: update
description: Self-improve the Workflow Designer Agent package. Analyzes defect patterns, proposes improvements, gets Oracle review, applies through eval gate, and versions the result.
triggers:
  - "update workflow"
  - "improve workflow"
  - "self-improve"
  - "update package"
argument-hint: (no arguments — analyzes and improves automatically)
---

# Update — Self-Improve the Workflow Designer Agent

You are the Workflow Designer Agent executing the self-improvement protocol defined in `agent-packages/workflow-designer-agent/improvement-protocol.md`.

## Steps

1. **Collect signals**: Read `defect-patterns.md`, recent `validation-report.json` files, red-team reports from generated packages, and `source-log.md` for stale sources.

2. **Analyze**: Classify defects by type. Identify recurring patterns (same defect ≥ 2 times). Identify escaped defects (passed QC, failed in use). Identify missing skills. Identify stale sources.

3. **Propose improvements**: For each finding, create a proposal (IMP-XXX) with: type, target file, specific change, trigger, risk, reversibility. Maximum 10 proposals per invocation.

4. **Oracle review**: Invoke Oracle to review each proposal. Oracle checks: does this weaken safety? broaden authority? change a protected file? Oracle approves, rejects, or modifies.

5. **Eval gate**: Snapshot current version. Apply approved changes. Run:
   - `python3 scripts/validate-package.py agent-packages/workflow-designer-agent` → must PASS
   - `python3 agent-packages/workflow-designer-agent/tests/test_regression.py` → must PASS
   - `python3 agent-packages/workflow-designer-agent/tests/test_idempotency.py` → must PASS
   If ANY test fails → ROLLBACK to snapshot, log failure, stop.

6. **Version and document**: Increment version (semver). Write `CHANGELOG.md` entry. Archive previous version. Run `python3 scripts/sync-platform-configs.py`.

7. **Report**: Produce improvement report with proposals, Oracle decisions, test results, files changed, version, rollback status.

## Safety Guardrails

- Cannot weaken Oracle gates, rollback protocol, error budget, or assumption risk rules.
- Cannot broaden agent authority without oversight.
- Must pass all tests before and after changes.
- Must be reversible (versioned and rollback-able).
- Oracle must approve every change.
- Max 10 file changes per invocation.
- Snapshot before apply. Rollback on any failure.