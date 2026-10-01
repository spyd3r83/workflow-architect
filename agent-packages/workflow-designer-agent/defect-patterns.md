# Defect Patterns Database

This file logs defects found in generated workflow packages. Each defect is a signal for self-improvement via the `/update` command.

## Defect Entry Format

```
### DEF-XXX: <defect name>
- Date Found: YYYY-MM-DD
- Source: <which generated package / which phase / which test>
- Type: structural / semantic / domain-specific / source-related / vague-instruction / broken-reference / non-idempotent / escaped
- Severity: critical / high / medium / low
- Description: <what was wrong>
- Root Cause: <why it happened>
- Detection Method: <how it was found — validate-package.py / QC / red-team / independent-verification / post-delivery>
- Escape Point: <which gate should have caught it but didn't (if escaped)>
- Resolution: <how it was fixed>
- Improvement Action: <what /update should do to prevent recurrence>
- Status: resolved / open
```

## Defects

### DEF-001: Initial baseline — no defects yet

- Date Found: 2025-07-03
- Source: N/A (initial release)
- Type: N/A
- Severity: N/A
- Description: No defects logged yet. This is the initial baseline.
- Root Cause: N/A
- Detection Method: N/A
- Escape Point: N/A
- Resolution: N/A
- Improvement Action: N/A
- Status: resolved

## Statistics

| Metric | Value |
|--------|-------|
| Total defects logged | 1 (baseline) |
| Defects resolved | 1 |
| Defects open | 0 |
| Escaped defects (passed QC, failed in use) | 0 |
| Most common defect type | N/A |
| Last /update run | N/A |

## Recurring Patterns

When the same defect type appears ≥ 2 times, it is flagged here as a recurring pattern:

| Pattern | Count | First Seen | Last Seen | Improvement Proposed |
|---------|-------|------------|-----------|---------------------|
| (none yet) | — | — | — | — |

## Improvement Proposals Log

When /update proposes improvements, they are logged here:

| ID | Type | Target | Trigger | Oracle Status | Applied |
|----|------|--------|---------|---------------|---------|
| (none yet) | — | — | — | — | — |