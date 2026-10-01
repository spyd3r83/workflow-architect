# Quality Control — Workflow Designer Agent

The quality-control system checks every generated workflow package for correctness, completeness, consistency, and implementation readiness. The quality-reviewer agent executes this before red-team review.

## QC Dimensions

| # | Dimension | What It Checks |
|---|-----------|----------------|
| 1 | Accuracy | Factual claims are sourced or labelled as assumptions. No hallucinated facts. |
| 2 | Completeness | All required files exist. All required sections present in each file. |
| 3 | Source support | Every `[VERIFIED]` claim has a citation. Every claim is tagged. |
| 4 | Internal consistency | Agent handoffs match. Cross-references are valid. No file references a non-existent file. |
| 5 | Implementation readiness | The package can be used by another agent without additional explanation. |
| 6 | File/folder completeness | File tree matches `package-output-spec.md`. No empty files. No placeholder files. |
| 7 | Agent-role clarity | Every agent has a distinct role. No overlapping responsibilities. Every agent has all 10 required sections. |
| 8 | Skill reusability | Every skill is reusable across similar projects. No skill is hardcoded to one project. Every skill has all 8 required sections. |
| 9 | Vague instructions | No agent description, skill, or workflow step lacks concrete actions. |
| 10 | Hidden assumptions | Every assumption is explicitly labelled `[ASSUMPTION]`. No untagged assumptions. |
| 11 | Missing validation | Every phase has validation criteria. Every agent has a quality checklist. Every skill has validation criteria. |
| 12 | Overconfident claims | No claim is presented as certain when it rests on an assumption. |
| 13 | User-objective alignment | Every deliverable serves the stated objective. No deliverable is unrelated to the objective. |
| 14 | Traceability | Every requirement traces to a deliverable and verification method. No untraced deliverables. |
| 15 | FMEA coverage | All failure modes with RPN ≥ 100 have mitigations. Mitigations have verification methods. |
| 16 | Source chain-of-custody | Every citation has a retrieval ID in source-log.md. Compliance claims have dual-source verification. |
| 17 | Assumption risk classification | Every assumption has a risk level (low/medium/high/critical). High/critical assumptions retired or accepted. |
| 18 | Idempotency | test_idempotency.py passes. Same input produces same output. |

## Quantitative Acceptance Criteria

All criteria are measurable. A criterion is PASS only if the measured value meets the threshold.

| # | Metric | Target | Measurement Method |
|---|--------|--------|-------------------|
| Q1 | Structural defect rate | 0% | validate-package.py: (total - passed) / total |
| Q2 | Citation format compliance | 100% | validate-package.py: citations matching format / total citations |
| Q3 | Cross-reference resolution | 100% | validate-package.py: resolved refs / total refs |
| Q4 | Vague verb count in agents | 0 | validate-package.py: regex match count |
| Q5 | Placeholder count (non-templates) | 0 | validate-package.py: {{...}} count |
| Q6 | Empty file count | 0 | validate-package.py: files < 50 bytes |
| Q7 | Assumption risk classification coverage | 100% | QC: assumptions with risk level / total assumptions |
| Q8 | Source-log retrieval ID coverage | 100% | validate-package.py: citations with RET-XXX / total citations |
| Q9 | Traceability matrix coverage | 100% | validate-package.py: requirements with deliverables / total requirements |
| Q10 | FMEA mitigation coverage (RPN ≥ 100) | 100% | QC: mitigated failure modes / total high-RPN modes |
| Q11 | Agent section completeness | 100% | validate-package.py: agents with 10 sections / total agents |
| Q12 | Skill section completeness | 100% | validate-package.py: skills with 8 sections / total skills |
| Q13 | Assumption ratio | ≤ 15% | QC: assumptions / total claims |
| Q14 | Independent verification pass rate | 100% | Phase 11.5 report |
| Q15 | Idempotency test pass | 100% | test_idempotency.py |

### Scoring

- **PASS**: All 15 quantitative criteria meet their targets.
- **FAIL**: Any single criterion does not meet its target. The specific failing criterion and its measured value are recorded in the QC report.
- **No averaging**: A package cannot "average out" a failure in one criterion by exceeding in another.

## QC Checklist

This checklist must be completed before the package is considered final. Every item must pass.

### Accuracy
- [ ] All factual claims are tagged `[VERIFIED]` or `[ASSUMPTION]`.
- [ ] All `[VERIFIED]` claims have citations with source, author, date, and URL/reference.
- [ ] No fabricated sources or URLs.
- [ ] No untagged claims.

### Completeness
- [ ] All files from `package-output-spec.md` exist on disk.
- [ ] Every agent file has all 10 sections: role, mission, responsibilities, required inputs, expected outputs, operating rules, decision criteria, escalation rules, quality checklist, failure modes to avoid.
- [ ] Every skill file has all 8 sections: purpose, when to use, required inputs, process, output format, validation criteria, common mistakes, example usage.
- [ ] Every prompt file is ready to paste into an agent session.
- [ ] Every template file has placeholder markers and fill instructions.
- [ ] At least one example package is included.

### Source Support
- [ ] Research summary exists and is structured.
- [ ] All citations follow the format: `[Source: <title>, <author/org>, <date>, <URL>]`.
- [ ] Conflicting sources are documented with resolutions.
- [ ] Time-sensitive claims have research dates.

### Internal Consistency
- [ ] Agent handoffs reference agents that exist in the package.
- [ ] Skill references in agent files reference skills that exist in the package.
- [ ] Cross-references between files point to files that exist.
- [ ] No file references a non-existent file or section.

### Implementation Readiness
- [ ] The package README explains how to use the package.
- [ ] The workflow file defines all phases with inputs, outputs, responsible agent, and validation criteria.
- [ ] The intake model is usable (not an interrogation).
- [ ] Templates are fillable without additional documentation.
- [ ] Another agent could execute the workflow without asking the user additional questions beyond intake.

### File/Folder Completeness
- [ ] File tree matches `package-output-spec.md`.
- [ ] No file is empty.
- [ ] No file contains only a placeholder without content.
- [ ] Folder structure is clean (no orphaned files).

### Agent-Role Clarity
- [ ] Every agent has a distinct role (no two agents do the same thing).
- [ ] Every agent's mission is one sentence.
- [ ] Every agent's responsibilities are concrete actions, not vague descriptions.
- [ ] Every agent has decision criteria (when it does X vs Y).
- [ ] Every agent has escalation rules (when to escalate to the orchestrator or user).

### Skill Reusability
- [ ] Every skill is domain-appropriate but not hardcoded to one project.
- [ ] Every skill has a concrete example usage with inputs and expected outputs.
- [ ] No skill duplicates another skill's purpose.
- [ ] Every skill's process is step-by-step, not narrative.

### Vague Instructions
- [ ] No agent description says "helps with" or "supports" without specifying what.
- [ ] No workflow step says "handle" or "manage" without specifying how.
- [ ] No skill says "use when appropriate" without defining what "appropriate" means.

### Hidden Assumptions
- [ ] Every assumption in the intake document is labelled `[ASSUMPTION]`.
- [ ] Every assumption in the research summary is labelled `[ASSUMPTION]`.
- [ ] No file contains an unstated assumption (if a decision rests on an assumption, it is visible).

### Missing Validation
- [ ] Every workflow phase has validation criteria.
- [ ] Every agent file has a quality checklist.
- [ ] Every skill file has validation criteria.
- [ ] The QC checklist itself is complete (this checklist).

### Overconfident Claims
- [ ] No claim says "will" or "guarantees" when it rests on an assumption.
- [ ] No claim says "best practice" without a source.
- [ ] No claim says "standard" without citing the standard.

### User-Objective Alignment
- [ ] Every agent serves the stated objective.
- [ ] Every skill serves the stated objective.
- [ ] Every workflow phase produces a deliverable that serves the stated objective.
- [ ] No deliverable is unrelated to the objective.

## QC Report Format

The quality-reviewer produces a structured report:

```
# QC Report: <package name>

## Summary
- Total items: <N>
- Passed: <N>
- Failed: <N>

## Results

### Item 1: Accuracy — All claims tagged
Status: PASS / FAIL
Evidence: <what was checked and what was found>
Required fix (if fail): <specific fix>

### Item 2: ...
...

## Overall Recommendation
PASS / FAIL (proceed to red-team / return to revision loop)
```

## Failure Handling

- Any single item failing → the package goes to the revision loop (Phase 13).
- The QC report specifies the exact fix required for each failed item.
- The orchestrator routes fixes to the responsible agent.
- After fixes, QC is re-run on the revised package.
- Maximum 3 QC iterations before escalation to the user.

## Anti-Patterns

- Marking an item as "pass" without evidence. Every pass must state what was checked.
- Marking an item as "fail" without a required fix. Every fail must have an actionable fix.
- Skipping items because "they seem fine". Every item is checked.
- Producing a narrative report instead of a structured one.
- Allowing the package to proceed to red-team with known QC failures.