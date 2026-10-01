# Defect Patterns Template

This template defines the structure for a defect patterns database in generated packages.

---

# Defect Patterns: {{PACKAGE_NAME}}

## Defect Entry Format

```
### DEF-XXX: <defect name>
- Date Found: YYYY-MM-DD
- Source: <which package / phase / test>
- Type: structural / semantic / domain-specific / source-related / vague-instruction / broken-reference / non-idempotent / escaped
- Severity: critical / high / medium / low
- Description: <what was wrong>
- Root Cause: <why it happened>
- Detection Method: <how it was found>
- Escape Point: <which gate should have caught it>
- Resolution: <how it was fixed>
- Improvement Action: <what /update should do to prevent recurrence>
- Status: resolved / open
```

## Defects

### DEF-001: Initial baseline — no defects yet
- Status: resolved

## Statistics

| Metric | Value |
|--------|-------|
| Total defects logged | 1 (baseline) |
| Defects resolved | 1 |
| Defects open | 0 |
| Escaped defects | 0 |

## Recurring Patterns

| Pattern | Count | First Seen | Last Seen | Improvement Proposed |
|---------|-------|------------|-----------|---------------------|
| (none yet) | — | — | — | — |

## Improvement Proposals Log

| ID | Type | Target | Trigger | Oracle Status | Applied |
|----|------|--------|---------|---------------|---------|
| (none yet) | — | — | — | — | — |

---

## Fill Instructions

1. **{{PACKAGE_NAME}}**: The name of the generated package.
2. Start with DEF-001 as baseline. Add new defects as they are found.

## Validation Criteria

- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] Entry format is documented.
- [ ] Statistics table exists.
- [ ] Recurring patterns table exists.