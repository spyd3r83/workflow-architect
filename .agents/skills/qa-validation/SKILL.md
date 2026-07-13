---
name: qa-validation
description: |
  Checks a generated workflow package for correctness and implementation readiness using the QC checklist. Produces a structured pass/fail report. Use when: - Phase 11 (Internal QA) of the Workflow Designer Agent workflow.
  - When the quality-reviewer needs to validate the draft package before red-team review.
---

# Skill: QA Validation

## Purpose

Checks a generated workflow package for correctness and implementation readiness using the QC checklist. Produces a structured pass/fail report.

## When To Use

- Phase 11 (Internal QA) of the Workflow Designer Agent workflow.
- When the quality-reviewer needs to validate the draft package before red-team review.

## Required Inputs

- **Draft package** on disk.
- **`quality-control.md`** — the QC checklist with 18 dimensions.
- **`package-output-spec.md`** — to verify file completeness.
- **Intake document** — to verify user-objective alignment.

## Process

1. **File existence check.** Verify every file from `package-output-spec.md` exists on disk. List any missing files.
2. **Section completeness check.** For each agent file, verify all 10 sections exist. For each skill file, verify all 8 sections exist. List any missing sections.
3. **Accuracy check.** Scan all files for factual claims. Verify every claim is tagged `[VERIFIED]` (with citation) or `[ASSUMPTION]` (with reasoning). List any untagged claims.
4. **Source support check.** For every `[VERIFIED]` claim, verify the citation exists and follows the format. List any missing or malformed citations.
5. **Internal consistency check.** Verify all cross-references point to files that exist. Verify agent handoffs reference agents that exist. List any broken references.
6. **Implementation readiness check.** Verify the package README explains how to use the package. Verify the workflow defines all phases with required fields. Verify templates are fillable.
7. **File/folder completeness check.** Verify no file is empty or placeholder-only. Verify the folder structure is clean.
8. **Agent-role clarity check.** Verify every agent has a distinct role. Verify no overlapping responsibilities.
9. **Skill reusability check.** Verify every skill is reusable (not hardcoded). Verify no duplicate skills.
10. **Vague instructions check.** Scan for "helps with", "supports", "handles", "manages" without specifics. List any vague instructions.
11. **Hidden assumptions check.** Scan for unlabelled assumptions. List any.
12. **Missing validation check.** Verify every phase has validation criteria. Every agent has a quality checklist. Every skill has validation criteria.
13. **Overconfident claims check.** Scan for "will", "guarantees", "best practice" without source. List any.
14. **User-objective alignment check.** Verify every deliverable serves the stated objective. List any unrelated deliverables.
15. **Produce the QC report.** Structured document with per-item results.

## Output Format

```
# QC Report: <package name>

## Summary
- Total items: <N>
- Passed: <N>
- Failed: <N>

## Results

### Item 1: File existence
Status: PASS / FAIL
Evidence: <list of files checked, any missing files>
Required fix (if fail): <specific fix>

### Item 2: Section completeness
Status: PASS / FAIL
Evidence: <agents checked, skills checked, any missing sections>
Required fix (if fail): <specific fix>

... (items 3-13)

## Overall Recommendation
PASS / FAIL
```

## Validation Criteria

- [ ] All 18 QC dimensions evaluated.
- [ ] Every item has evidence (what was checked, what was found).
- [ ] Every fail has an actionable required fix.
- [ ] Report is structured (not narrative).
- [ ] Overall recommendation is PASS or FAIL.

## Common Mistakes

- **Marking pass without evidence**: "looks fine" is not evidence. State what was checked.
- **Marking fail without a fix**: "this is wrong" without a fix is not actionable.
- **Skipping items**: not checking vague instructions or hidden assumptions because they seem fine.
- **Narrative report**: writing paragraphs instead of structured per-item results.
- **Being lenient**: passing vague instructions or hidden assumptions. These are automatic fails.
- **Not checking cross-references**: broken references cause downstream failures.

## Example Usage

**Input:**
```
Package: website-revamp-workflow
Files on disk: (list of 25 files)
```

**Output (excerpt):**
```
# QC Report: website-revamp-workflow

## Summary
- Total items: 13
- Passed: 12
- Failed: 1

## Results

### Item 1: File existence
Status: PASS
Evidence: All 25 files from package-output-spec.md exist on disk.

### Item 2: Section completeness
Status: PASS
Evidence: All 7 agent files have 10 sections. All 6 skill files have 8 sections.

### Item 9: Vague instructions
Status: FAIL
Evidence: visual-designer.md line 45: "handles the design process" — "handles" is vague.
Required fix: Replace with specific action, e.g., "Creates the design system spec including colors, typography, and component library."

...

## Overall Recommendation
FAIL (1 item failed; route to revision loop)
```