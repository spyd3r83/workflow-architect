# Traceability Matrix Template

This template defines the structure for tracing requirements to deliverables and verification. Fill in all `{{PLACEHOLDERS}}`.

---

# Traceability Matrix: {{PACKAGE_NAME}}

## Requirements

### REQ-001: {{requirement name}}

| Field | Value |
|-------|-------|
| Source | {{where this requirement comes from}} |
| Type | {{Functional / Non-functional / Safety / Regulatory}} |
| Priority | {{Critical / High / Medium / Low}} |
| Deliverable | {{what artifact satisfies this requirement}} |
| Verification Method | {{how it is verified}} |
| Status | {{Verified / Pending / Failed}} |

### REQ-002: {{requirement name}}

{{...copy table per requirement...}}

## Coverage Check

| Objective Component | Requirement IDs | Deliverables |
|---------------------|-----------------|--------------|
| {{objective part 1}} | REQ-001, REQ-002 | {{deliverables}} |
| {{objective part 2}} | REQ-003 | {{deliverables}} |

## Untraced Deliverables Check

| Deliverable | Traced To |
|-----------|-----------|
| {{file name}} | REQ-XXX |
| {{file name}} | REQ-XXX |

If a deliverable has no tracing requirement, either remove it or add a requirement.

---

## Fill Instructions

1. Derive requirements from the user objective, domain research, and compliance needs.
2. Give every requirement a unique ID (REQ-XXX).
3. Trace every requirement to a specific deliverable and verification method.
4. Check that every deliverable traces to at least one requirement.
5. Check that every objective component is covered by at least one requirement.
6. No untraced deliverables. No untraced requirements.

## Validation Criteria

- [ ] Every requirement has a unique ID.
- [ ] Every requirement traces to a deliverable.
- [ ] Every requirement traces to a verification method.
- [ ] No untraced deliverables.
- [ ] Coverage check passes (every objective component covered).
- [ ] validate-package.py confirms requirement IDs and verification columns.