# Generated Package Command Template — Maintain

This template defines the `/maintain` command for a generated workflow package.

---

Maintain and validate an existing {{WORKFLOW_NAME}} project.

Usage: /{{COMMAND_NAME}}-maintain <project name or path>

## Instructions

You are the quality-reviewer for the {{WORKFLOW_NAME}} workflow. Maintain an existing project.

### Arguments

$ARGUMENTS

### Steps

1. If $ARGUMENTS is empty, list existing project directories and ask the user which to maintain.
2. Locate the project by name or path.
3. Run validation checks per `quality-control.md`.
4. If validation fails, list failures and offer to fix them.
5. Check source staleness: read `source-log.md`, compare re-verification dates to today, list stale sources.
6. Run regression tests if `tests/` exists.
7. Run idempotency test if available.
8. Check `fmea.md` for new failure modes based on changes.
9. Update `traceability-matrix.md` if requirements or deliverables changed.
10. Produce a maintenance report: validation status, sources checked, tests run, files updated, recommendations.

### Rules

- Do not break existing functionality during maintenance.
- Always run validation before and after changes.
- Document every change in the maintenance report.
- If regression tests fail after changes, rollback and report.

---

## Fill Instructions

1. **{{WORKFLOW_NAME}}**: The name of the generated workflow.
2. **{{COMMAND_NAME}}**: The slash command name (same as flowstart).

## Validation Criteria

- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] Command name matches the flowstart command name with `-maintain` suffix.