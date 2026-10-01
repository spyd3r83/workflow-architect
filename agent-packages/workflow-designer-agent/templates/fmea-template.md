# FMEA Template

This template defines the structure for a Failure Mode and Effects Analysis. Fill in all `{{PLACEHOLDERS}}`.

---

# FMEA: {{PACKAGE_NAME}}

## Scoring System

| Dimension | Scale | Meaning |
|-----------|-------|---------|
| Severity (S) | 1-10 | 1 = cosmetic, 10 = catastrophic |
| Occurrence (O) | 1-10 | 1 = rare, 10 = frequent |
| Detection (D) | 1-10 | 1 = easily detected, 10 = undetectable |
| RPN | S x O x D | ≥ 100 requires mandatory mitigation. ≥ 200 requires redesign. |

## Failure Modes

### FM-001: {{failure mode name}}

| Field | Value |
|-------|-------|
| Failure mode | {{description of how it fails}} |
| Effect | {{what happens if it fails}} |
| Severity | {{1-10}} |
| Occurrence | {{1-10}} |
| Detection | {{1-10}} |
| RPN | {{S x O x D}} |
| Mitigation | {{specific actions to prevent or detect}} |
| Owner | {{responsible agent}} |
| Status | {{Open / Mitigated / Verified}} |

### FM-002: {{failure mode name}}

{{...copy table per failure mode...}}

## Summary

| ID | Failure Mode | RPN | Status |
|----|-------------|-----|--------|
| FM-001 | {{name}} | {{RPN}} | {{status}} |
| FM-002 | {{name}} | {{RPN}} | {{status}} |

## Mitigation Verification

| Mitigation | Verification Method | Verified By |
|-----------|-------------------|-------------|
| {{mitigation}} | {{method}} | {{verifier}} |

---

## Fill Instructions

1. Identify every way the workflow or generated package can fail.
2. Score each failure mode on severity, occurrence, and detection.
3. Calculate RPN. Any RPN ≥ 100 requires mandatory mitigation.
4. Assign an owner responsible for the mitigation.
5. Define how each mitigation is verified.
6. Update this document whenever new failure modes are discovered.

## Validation Criteria

- [ ] At least 5 failure modes identified.
- [ ] Every failure mode has S, O, D, and RPN.
- [ ] Every RPN ≥ 100 has a mitigation.
- [ ] Every mitigation has a verification method.
- [ ] Every failure mode has an owner.