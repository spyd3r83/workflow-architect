# Improvement Protocol Template

This template defines the structure for a self-improvement protocol in generated packages. Fill in `{{PLACEHOLDERS}}`.

---

# Improvement Protocol: {{PACKAGE_NAME}}

## Principle

**Defect-driven, eval-gated, Oracle-reviewed, versioned self-improvement.**

## What Can Be Improved

| Artifact | Can Self-Improve? |
|----------|-------------------|
| Agent definitions | Yes |
| Skill definitions | Yes |
| Workflow phases | Yes |
| QC criteria | Yes |
| FMEA | Yes |
| Templates | Yes |
| Regression tests | Yes |
| Validation script | Yes |

## What Cannot Be Self-Improved

| Artifact | Who Can Change |
|----------|----------------|
| Oracle gate definitions | User only |
| Rollback protocol | User only |
| Improvement protocol | User only |
| Error budget target | User only |

## Improvement Loop

1. **Collect signals**: Read defect log, validation reports, red-team reports, source log.
2. **Analyze**: Classify defects, identify recurring patterns, identify escaped defects.
3. **Propose**: Create IMP-XXX proposals with type, target, change, trigger, risk.
4. **Oracle review**: Oracle approves, rejects, or modifies.
5. **Eval gate**: Snapshot, apply, run tests, rollback if any fail.
6. **Version**: Increment semver, write changelog, archive, sync.
7. **Report**: Proposals, Oracle decisions, test results, files changed.

## Safety Guardrails

1. Cannot weaken safety boundaries.
2. Cannot broaden authority without oversight.
3. Must pass all tests.
4. Must be reversible.
5. Oracle must approve.
6. Max 10 changes per invocation.
7. Snapshot before apply.
8. Rollback on any failure.

---

## Fill Instructions

1. **{{PACKAGE_NAME}}**: The name of the generated package.
2. Keep the safety guardrails unchanged — they apply to all generated packages.

## Validation Criteria

- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] Safety guardrails section is intact.
- [ ] Improvement loop has all 7 steps.