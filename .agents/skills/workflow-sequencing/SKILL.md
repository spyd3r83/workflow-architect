---
name: workflow-sequencing
description: Defines the proper order of operations from intake to final output. Produces a phased, gated workflow that ensures work moves correctly from agent to agent. Use when: - Phase 6 (Workflow Decomposition) and Phase 7 (Agent Design) of the Workflow Designer Agent workflow.
- When the workflow-architect needs to sequence workstreams into a phased workflow with gates.
---

# Skill: Workflow Sequencing

## Purpose

Defines the proper order of operations from intake to final output. Produces a phased, gated workflow that ensures work moves correctly from agent to agent.

## When To Use

- Phase 6 (Workflow Decomposition) and Phase 7 (Agent Design) of the Workflow Designer Agent workflow.
- When the workflow-architect needs to sequence workstreams into a phased workflow with gates.

## Required Inputs

- **Workstream list** — from objective-decomposition skill.
- **Agent definitions** — from agent-design skill.
- **Dependencies** — which workstreams depend on which.
- **Domain classification** — to inform phase structure (e.g., compliance domains need compliance gates).

## Process

1. **Order workstreams by dependencies.** Topological sort: a workstream with no dependencies comes first; a workstream that depends on others comes after them.
2. **Group workstreams into phases.** A phase is a set of workstreams that can execute together (parallel) or in sequence (serial) before a gate. Typically 1-3 workstreams per phase.
3. **Define gates.** A gate is a validation checkpoint between phases. The next phase cannot begin until the gate passes. For each gate, define:
   - What is checked (validation criteria from the prior phase).
   - Who checks (responsible agent).
   - Pass condition (what "pass" looks like).
   - Fail action (revision loop or escalation).
4. **Define handoffs.** For each phase transition, specify:
   - What deliverable passes from the prior phase to the next.
   - In what format.
   - To which agent.
5. **Add mandatory phases.** Every workflow must include:
   - Intake phase (beginning).
   - Research phase (if domain-specific facts matter).
   - QC phase (before final packaging).
   - Red-team phase (after QC).
   - Revision loop (if QC or red-team fails).
   - Final packaging phase (end).
6. **Add domain-specific phases.** Based on the domain, add phases like:
   - Compliance review (legal, compliance domains).
   - Security review (security, app domains).
   - User testing (product, app domains).
   - Accessibility audit (web, design domains).
7. **Produce the workflow document.** Phased sequence with all fields.

## Output Format

```
# Workflow: <objective>

## Phases

### Phase 1: <name>
- Purpose: <one sentence>
- Inputs: <what this phase needs>
- Outputs: <concrete deliverables>
- Responsible Agent: <agent name>
- Validation Criteria: <checklist>
- Gate: <what must pass before Phase 2>

### Phase 2: <name>
...

## Handoffs
Phase 1 → <deliverable> → Phase 2
Phase 2 → <deliverable> → Phase 3
...

## Revision Loop
<description of what happens when a gate fails>
```

## Validation Criteria

- [ ] Workstreams ordered by dependencies (no circular dependencies).
- [ ] Workstreams grouped into phases logically.
- [ ] Every gate has validation criteria and a pass condition.
- [ ] Every phase transition has a defined handoff (deliverable, format, receiving agent).
- [ ] Mandatory phases included (intake, research if needed, QC, red-team, revision loop, final packaging).
- [ ] Domain-specific phases included where relevant.
- [ ] No phase lacks a responsible agent.
- [ ] No phase lacks validation criteria.

## Common Mistakes

- **Missing gates**: phases flow into each other without validation. Every phase transition needs a gate.
- **Circular dependencies**: workstream A depends on B, B depends on A. Resolve by splitting or reordering.
- **Missing mandatory phases**: skipping QC or red-team. These are always required.
- **Vague handoffs**: "pass the work" — pass what, in what format, to whom?
- **Over-phasing**: 20 phases for a simple workflow. Group related workstreams.
- **Under-phasing**: 3 phases for a complex workflow. Split into logical stages.
- **No revision loop**: assuming the first draft is final. The revision loop is mandatory.

## Example Usage

**Input:**
```
Workstreams: content-audit (no deps), ia-mapping (deps: content-audit), visual-design (deps: ia-mapping), seo-analysis (deps: content-audit), accessibility-audit (no deps), frontend-implementation (deps: visual-design, seo-analysis, accessibility-audit), qa-and-launch (deps: frontend-implementation)
Domain: web
```

**Output (excerpt):**
```
# Workflow: Revamp marketing website

## Phases

### Phase 1: Intake
- Purpose: Capture project objective and context.
- Inputs: User objective.
- Outputs: Intake document with labelled assumptions.
- Responsible Agent: intake-analyst
- Validation Criteria: All 11 fields addressed; objective refined; domain classified.
- Gate: Intake document accepted by orchestrator.

### Phase 2: Research
- Purpose: Gather domain-specific research (accessibility standards, SEO best practices).
- Inputs: Intake document, domain classification.
- Outputs: Research summary with citations.
- Responsible Agent: domain-researcher
- Validation Criteria: All claims tagged; citations present; gaps documented.
- Gate: Research summary accepted.

### Phase 3: Content Audit + Accessibility Requirements (parallel)
- Purpose: Audit existing content and define accessibility requirements simultaneously.
- Inputs: Research summary.
- Outputs: Content audit report; accessibility requirements checklist.
- Responsible Agent: content-auditor, accessibility-auditor (parallel)
- Validation Criteria: Content audit complete; accessibility requirements target WCAG 2.1 AA.
- Gate: Both deliverables accepted.

### Phase 4: IA Mapping + SEO Requirements (parallel)
...

### Phase 5: Visual Design
...

### Phase 6: Frontend Implementation
...

### Phase 7: QA and Launch
...

### Phase 8: QC
...

### Phase 9: Red-Team Review
...

### Phase 10: Final Packaging
...

## Revision Loop
If QC or red-team fails, route mandatory fixes to responsible agents, re-run failed gate. Max 3 iterations before escalation.
```