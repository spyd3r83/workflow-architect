# Intake Model — Workflow Designer Agent

The intake model captures the minimum information needed to design a workflow package. The intake-analyst agent asks only essential questions and fills the rest with labelled assumptions.

## Intake Fields

| # | Field | Required? | Description |
|---|-------|-----------|-------------|
| 1 | Project goal | Required | One or two sentences describing what the workflow should accomplish. |
| 2 | Project type | Optional | e.g., website revamp, new app, security audit, compliance review, research project, documentation system, marketing campaign, business process. Inferred if omitted. |
| 3 | Target audience / users | Optional | Who will use the workflow output or the deliverables it produces. |
| 4 | Current assets | Optional | Existing code, documents, designs, data, or infrastructure the workflow should account for. |
| 5 | Desired deliverables | Optional | What the workflow should produce. e.g., "a deployed website", "a security report", "a compliance checklist". |
| 6 | Tools / platforms | Optional | Specific tools, frameworks, or platforms the workflow must use or target. |
| 7 | Constraints | Optional | Timeline, budget, team size, compliance requirements, technical limitations. |
| 8 | Timeline / priority | Optional | Deadline or priority level (high/medium/low). |
| 9 | Success criteria | Optional | What "done" looks like. Measurable if possible. |
| 10 | Risk / compliance issues | Optional | Known risks, regulatory requirements, or compliance frameworks that apply. |
| 11 | Source materials | Optional | Documents, specs, links, or code the user provides for the domain-researcher to review. |

## Intake Process

1. **Receive the project objective.** This is the only required input.
2. **Ask clarifying questions — maximum 5.** Only ask when the missing information would change the workflow design. If a reasonable assumption can be made, make it instead of asking.
3. **Fill all 11 fields.** For each field the user did not provide, record a labelled assumption.
4. **Produce the intake document.** Use `templates/intake-template.md`.

## Assumption Labelling

Every assumption follows this format:

```
[ASSUMPTION] <field>: <assumed value>
  Reasoning: <why this assumption is reasonable>
  Confidence: high / medium / low
  Risk: low / medium / high / critical
  User can override: yes
```

### Risk Classification

Every assumption must have a risk classification. Risk determines whether the assumption can be accepted or must be retired (verified) before proceeding.

| Risk Level | Definition | Action |
|-----------|-----------|--------|
| Low | Assumption is easily corrected later with minimal impact | Label and proceed |
| Medium | Assumption could cause rework if wrong | Label and proceed; flag for verification in research phase |
| High | Assumption could cause significant rework or wrong deliverables | Must be retired (verified) or formally accepted by user at requirements gate |
| Critical | Assumption could cause safety, legal, or compliance failure | Must be retired (verified) before proceeding; cannot be user-approved away |

### Requirements Extraction

After intake, the intake-analyst derives formal requirements (Phase 1.5) from the intake document. Every requirement gets a unique ID (REQ-XXX), type, priority, source, measurable acceptance criteria, and traced deliverable. See `requirements.md` and `templates/requirements-template.md`.

### Examples

```
[ASSUMPTION] Project type: website revamp
  Reasoning: The objective mentions "redesign our marketing site", which maps to a website revamp.
  Confidence: high
  Risk: low
  User can override: yes

[ASSUMPTION] Target audience: prospective customers visiting the marketing site
  Reasoning: Marketing sites typically target prospects. User did not specify.
  Confidence: medium
  Risk: medium
  User can override: yes

[ASSUMPTION] Tools/platforms: not specified — workflow will be tool-agnostic
  Reasoning: User did not specify tools. The workflow will design agents that adapt to the project's existing stack.
  Confidence: medium
  Risk: low
  User can override: yes
```

## When To Ask vs Assume

| Situation | Action |
|-----------|--------|
| Missing info would change the agents or skills designed | Ask (counts toward the 5-question limit) |
| Missing info can be reasonably inferred from the objective | Assume and label |
| Missing info is about preferences (tools, style) that can be adaptive | Assume "tool-agnostic" or "adaptive" and label |
| Missing info is about compliance or legal risk | Ask — never assume on compliance |
| User explicitly says "you decide" | Assume and label with high confidence |

## Intake Document Structure

The final intake document contains:

1. **Objective statement** — the refined 1-2 sentence objective.
2. **Field table** — all 11 fields, each marked as `[PROVIDED]` or `[ASSUMPTION]`.
3. **Assumptions list** — all assumptions with reasoning and confidence.
4. **Scope boundaries** — what is in scope, what is out of scope.
5. **Open questions** — any questions that remain open (escalated to user if blocking).

## Anti-Patterns

- Asking more than 5 questions. The intake is minimal, not an interrogation.
- Making assumptions about compliance or legal requirements. Always ask.
- Making assumptions without labelling them. Hidden assumptions fail QC.
- Filling fields with "TBD" or "unknown". Either fill with an assumption or escalate.
- Recording the objective as a vague phrase. The objective must be specific enough to drive agent design.