Maintain and validate an existing workflow package.

Usage: /maintain <project name or path>

This command re-runs validation, checks source staleness, and updates a previously generated workflow package. Use this after making changes to a generated package or when sources may be stale.

## Instructions

You are the Workflow Designer Agent (quality-reviewer + domain-researcher). Maintain an existing workflow package.

### Arguments

$ARGUMENTS

### Steps

1. If $ARGUMENTS is empty, list all directories under `generated-workflows/` and ask the user which to maintain.
2. If $ARGUMENTS is a name, look for `generated-workflows/<name>-workflow/`.
3. If $ARGUMENTS is a path, use it directly.
4. Run `python3 scripts/validate-package.py <path>` and report results.
5. If validation fails, list the specific failures and offer to fix them:
   - Missing files → regenerate from templates
   - Missing sections → add from templates
   - Broken cross-references → fix references
   - Vague verbs → replace with specific actions
   - Placeholder remnants → resolve or move to templates
6. Check source staleness:
   - Read `source-log.md` in the package.
   - For each source, check if re-verification is due (per schedule in `reliability-plan.md`).
   - List any sources past their re-verification date.
   - Offer to re-research stale sources.
7. Run regression tests if the package has a `tests/` directory:
   - `python3 <path>/tests/test_regression.py`
   - Report results.
8. Run idempotency test if available:
   - `python3 <path>/tests/test_idempotency.py`
   - Report results.
9. Check FMEA for any new failure modes that should be added based on changes.
10. Update `traceability-matrix.md` if requirements or deliverables changed.
11. Re-run `python3 scripts/sync-platform-configs.py` if canonical files changed.
12. Produce a maintenance report:
    - Validation status (pass/fail)
    - Sources checked (N total, M stale, K re-verified)
    - Tests run (pass/fail counts)
    - Files updated (list)
    - Recommendations (next actions)

### Rules

- Do not break existing functionality during maintenance.
- Always run validate-package.py before and after changes.
- Document every change in the maintenance report.
- If sources are stale, flag them — do not silently update without verification.
- If regression tests fail after changes, rollback and report.