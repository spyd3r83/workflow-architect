# Changelog Template

This template defines the structure for a changelog in generated packages. Entries are append-only.

---

# Changelog: {{PACKAGE_NAME}}

## Version 1.0.0 — {{DATE}}

- **Initial release**: {{WORKFLOW_DESCRIPTION}}

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

---

## Fill Instructions

1. **{{PACKAGE_NAME}}**: The name of the generated package.
2. **{{DATE}}**: The date the package was generated.
3. **{{WORKFLOW_DESCRIPTION}}**: One-line description of the workflow.

## Validation Criteria

- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] Entry format is documented.
- [ ] Initial version entry exists.