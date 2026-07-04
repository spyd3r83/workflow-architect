# Agent File Template

This template defines the structure for creating an agent file. Fill in all `{{PLACEHOLDERS}}`.

---

# Agent: {{AGENT_NAME}}

## Role

{{ROLE — one phrase describing what this agent does. e.g., "Audits existing website content for quality and SEO performance."}}

## Mission

{{MISSION — one sentence describing what this agent must accomplish. e.g., "Produce a content audit report with keep/revise/remove recommendations per page."}}

## Responsibilities

{{RESPONSIBILITIES — 5-10 concrete actions. Use a list.}}

- {{responsibility 1}}
- {{responsibility 2}}
- {{responsibility 3}}
- ...

## Required Inputs

{{REQUIRED_INPUTS — what the agent needs to do its job.}}

- {{input 1}}
- {{input 2}}
- ...

## Expected Outputs

{{EXPECTED_OUTPUTS — concrete deliverables the agent produces.}}

- {{output 1}}
- {{output 2}}

## Operating Rules

{{OPERATING_RULES — constraints and rules the agent must follow. Numbered list.}}

1. {{rule 1}}
2. {{rule 2}}
3. ...

## Decision Criteria

{{DECISION_CRITERIA — when the agent does X vs Y. Table format.}}

| Situation | Decision |
|-----------|---------|
| {{situation 1}} | {{decision 1}} |
| {{situation 2}} | {{decision 2}} |

## Escalation Rules

{{ESCALATION_RULES — when to escalate to the orchestrator or user.}}

- Escalate to {{orchestrator/user}} if: {{condition 1}}
- Escalate to {{orchestrator/user}} if: {{condition 2}}

## Quality Checklist

{{QUALITY_CHECKLIST — what must be true before the agent's output is accepted.}}

- [ ] {{checklist item 1}}
- [ ] {{checklist item 2}}
- [ ] ...

## Failure Modes To Avoid

{{FAILURE_MODES — common mistakes this agent must not make.}}

- {{failure mode 1}}
- {{failure mode 2}}
- ...

---

## Fill Instructions

1. **Agent name**: kebab-case, domain-appropriate (e.g., `content-auditor`, `threat-modeler`).
2. **Role**: one phrase, specific to the domain. Not "helper" or "doer".
3. **Mission**: one sentence, outcome-oriented.
4. **Responsibilities**: concrete actions, not vague descriptions. "Creates", "Audits", "Defines" — not "Helps with", "Supports".
5. **Required Inputs**: list everything the agent needs. If an input is optional, mark it.
6. **Expected Outputs**: concrete deliverables. "Content audit report" — not "analysis".
7. **Operating Rules**: numbered, enforceable constraints.
8. **Decision Criteria**: table format, covering the main branching points the agent faces.
9. **Escalation Rules**: specific conditions, not "when in doubt".
10. **Quality Checklist**: verifiable items, not subjective.
11. **Failure Modes**: common mistakes specific to this agent's domain.

## Validation Criteria (when this template is properly filled)

- [ ] All 10 sections present and populated.
- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] Role is specific (not generic).
- [ ] Responsibilities are concrete actions.
- [ ] Decision criteria cover main branching points.
- [ ] Quality checklist items are verifiable.
- [ ] Failure modes are specific to the agent's domain.