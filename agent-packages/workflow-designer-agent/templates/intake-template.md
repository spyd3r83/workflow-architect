# Intake Template

This template defines the structure for an intake document. Fill in all fields. For fields the user did not provide, record a labelled assumption.

---

# Intake Document: {{PROJECT_NAME}}

## Objective Statement

{{OBJECTIVE — refined 1-2 sentence statement}}

## Scope

- **In scope**: {{what is in scope}}
- **Out of scope**: {{what is out of scope}}

## Intake Fields

| # | Field | Status | Value |
|---|-------|--------|-------|
| 1 | Project goal | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 2 | Project type | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 3 | Target audience / users | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 4 | Current assets | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 5 | Desired deliverables | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 6 | Tools / platforms | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 7 | Constraints | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 8 | Timeline / priority | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 9 | Success criteria | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 10 | Risk / compliance issues | [PROVIDED] / [ASSUMPTION] | {{value}} |
| 11 | Source materials | [PROVIDED] / [ASSUMPTION] | {{value}} |

## Assumptions

For each field marked [ASSUMPTION], record the assumption here:

```
[ASSUMPTION] {{field}}: {{assumed value}}
  Reasoning: {{why this assumption is reasonable}}
  Confidence: high / medium / low
  User can override: yes
```

### Assumption 1
```
[ASSUMPTION] {{field}}: {{value}}
  Reasoning: {{reasoning}}
  Confidence: {{high/medium/low}}
  User can override: yes
```

### Assumption 2
```
[ASSUMPTION] {{field}}: {{value}}
  Reasoning: {{reasoning}}
  Confidence: {{high/medium/low}}
  User can override: yes
```

## Domain Classification

- **Domain**: {{domain label}}
- **Sub-domain**: {{sub-domain if applicable}}
- **Domain-specific risks**: {{list of risks}}

## Open Questions

Any questions that remain open (escalated to user if blocking):

- {{question 1 (or "none")}}
- {{question 2 (or "none")}}

---

## Fill Instructions

1. **Objective**: Refine the user's objective into a precise 1-2 sentence statement. If vague, ask one clarifying question.
2. **Scope**: Explicitly state what is in and out of scope. "Everything" is not a scope.
3. **Fields**: For each of the 11 fields, mark as [PROVIDED] (user gave it) or [ASSUMPTION] (inferred). Fill the value.
4. **Assumptions**: For every [ASSUMPTION] field, record the assumption with reasoning and confidence. Never assume on compliance — always ask.
5. **Domain**: Classify the domain and identify domain-specific risks.
6. **Open questions**: List any questions that remain. If a question blocks the workflow, escalate to the user.

## Validation Criteria

- [ ] All 11 fields addressed (provided or labelled as assumption).
- [ ] Objective is a precise 1-2 sentence statement.
- [ ] Scope boundaries are explicit.
- [ ] Every assumption labelled with reasoning and confidence.
- [ ] No more than 5 clarifying questions asked to the user.
- [ ] Domain classified with risks identified.
- [ ] No field filled with "TBD" or "unknown" — either fill with assumption or escalate.