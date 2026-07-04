# Generated Package Command Template — Update (Self-Improve)

This template defines the `/update` command for a generated workflow package. The Workflow Designer Agent fills in `{{PLACEHOLDERS}}` when generating a package.

---

Self-improve the {{WORKFLOW_NAME}} package.

Usage: /{{COMMAND_NAME}}-update

## Instructions

You are executing the self-improvement protocol defined in `improvement-protocol.md`.

### Steps

1. **Collect signals**: Read `defect-patterns.md`, recent validation reports, red-team findings, and `source-log.md` for stale sources.
2. **Analyze**: Classify defects. Identify recurring patterns (≥ 2 occurrences). Identify escaped defects. Identify stale sources.
3. **Propose improvements**: For each finding, create a proposal (IMP-XXX) with type, target file, change, trigger, risk. Maximum 10 proposals per invocation.
4. **Oracle review**: Oracle reviews each proposal. Rejects if safety weakened or authority broadened.
5. **Eval gate**: Snapshot current version. Apply changes. Run validation, regression tests, idempotency tests. Rollback if any fail.
6. **Version and document**: Increment semver. Write `CHANGELOG.md` entry. Archive previous version.
7. **Report**: Proposals, Oracle decisions, test results, files changed, version.

### Safety Guardrails

- Cannot weaken Oracle gates, rollback protocol, error budget, or assumption risk rules.
- Cannot broaden authority without oversight.
- Must pass all tests before and after changes.
- Max 10 file changes per invocation.
- Snapshot before apply. Rollback on any failure.

---

## Fill Instructions

1. **{{WORKFLOW_NAME}}**: The name of the generated workflow.
2. **{{COMMAND_NAME}}**: The slash command name (same as flowstart).

## Validation Criteria

- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] References improvement-protocol.md.
- [ ] Safety guardrails section intact.