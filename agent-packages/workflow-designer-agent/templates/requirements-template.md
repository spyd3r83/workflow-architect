# Requirements Template

This template defines the structure for formal requirements. Fill in all `{{PLACEHOLDERS}}`.

---

# Requirements: {{PACKAGE_NAME}}

## Requirement Types

| Type | Description |
|------|-------------|
| Functional | What the system must do |
| Non-functional | How the system must behave |
| Safety | What the system must not do |
| Regulatory | What the system must comply with |

## Priority Levels

| Priority | Description |
|----------|-------------|
| Critical | Must be satisfied; failure blocks finalization |
| High | Must be satisfied; failure triggers revision loop |
| Medium | Should be satisfied; failure documented |
| Low | Nice to have; failure noted |

## Requirements

### REQ-001: {{requirement name}}

| Field | Value |
|-------|-------|
| Type | {{Functional / Non-functional / Safety / Regulatory}} |
| Priority | {{Critical / High / Medium / Low}} |
| Source | {{where this requirement comes from}} |
| Description | {{what the system must do or how it must behave}} |
| Acceptance Criteria | {{measurable conditions for satisfaction}} |
| Traced Deliverable | {{what artifact satisfies this}} |

### REQ-002: {{requirement name}}

{{...copy table per requirement...}}

## Requirements Coverage

| Source | Requirements |
|-------|-------------|
| {{source 1}} | REQ-001, REQ-002 |
| {{source 2}} | REQ-003 |

---

## Fill Instructions

1. Derive requirements from the user objective, domain research, and compliance needs.
2. Give every requirement a unique ID (REQ-XXX).
3. Write acceptance criteria that are measurable (not "works correctly" but "output contains X with Y format").
4. Trace every requirement to a deliverable.
5. Ensure coverage: every objective component has at least one requirement.

## Validation Criteria

- [ ] Every requirement has a unique ID (REQ-XXX).
- [ ] Every requirement has type, priority, source, description, acceptance criteria.
- [ ] Acceptance criteria are measurable.
- [ ] Every requirement traces to a deliverable.
- [ ] Coverage check passes.
- [ ] validate-package.py confirms requirement IDs and acceptance criteria.