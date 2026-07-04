---
name: maintain
description: Maintain and validate an existing workflow package. Re-runs validation, checks source staleness, and updates a previously generated package.
triggers:
  - "maintain workflow"
  - "validate workflow"
  - "check workflow"
  - "maintain project"
argument-hint: <project name or path>
---

# Maintain — Validate and Update an Existing Workflow Package

You are the Workflow Designer Agent (quality-reviewer + domain-researcher). Maintain an existing workflow package.

## Target

$ARGUMENTS

## Steps

1. If $ARGUMENTS is empty, list all directories under `generated-workflows/` and ask the user which to maintain.
2. Locate the package by name or path.
3. Run `python3 scripts/validate-package.py <path>` and report results.
4. If validation fails, list failures and offer to fix them.
5. Check source staleness: read `source-log.md`, compare re-verification dates to today, list stale sources.
6. Run regression tests if `tests/` exists: `python3 <path>/tests/test_regression.py`.
7. Run idempotency test if available: `python3 <path>/tests/test_idempotency.py`.
8. Check FMEA for new failure modes based on changes.
9. Update `traceability-matrix.md` if requirements or deliverables changed.
10. Re-run `python3 scripts/sync-platform-configs.py` if canonical files changed.
11. Produce a maintenance report: validation status, sources checked, tests run, files updated, recommendations.

## Rules

- Do not break existing functionality during maintenance.
- Always run validate-package.py before and after changes.
- Document every change in the maintenance report.
- If regression tests fail after changes, rollback and report.