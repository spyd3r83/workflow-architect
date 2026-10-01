# QA Checklist Template

This template defines the structure for a QC checklist. Fill in `{{PACKAGE_SPECIFIC_ITEMS}}` with items specific to the generated package.

---

# QC Checklist: {{PACKAGE_NAME}}

## Summary

- Total items: {{N}}
- Passed: {{N}}
- Failed: {{N}}

## Results

### Accuracy

- [ ] **All factual claims tagged** — Every claim is `[VERIFIED]` (with citation) or `[ASSUMPTION]` (with reasoning).
  - Status: {{PASS/FAIL}}
  - Evidence: {{what was checked}}
  - Required fix (if fail): {{specific fix}}

- [ ] **No fabricated sources** — All citations point to real sources. No invented URLs, quotes, dates, or versions.
  - Status: {{PASS/FAIL}}
  - Evidence: {{what was checked}}

### Completeness

- [ ] **All required files present** — Every file from `package-output-spec.md` exists on disk.
  - Status: {{PASS/FAIL}}
  - Evidence: {{file list checked}}

- [ ] **Agent section completeness** — Every agent file has all 10 sections.
  - Status: {{PASS/FAIL}}
  - Evidence: {{agents checked, any missing sections}}

- [ ] **Skill section completeness** — Every skill file has all 8 sections.
  - Status: {{PASS/FAIL}}
  - Evidence: {{skills checked, any missing sections}}

### Source Support

- [ ] **Citations formatted correctly** — All citations follow `[Source: <title>, <author/org>, <date>, <URL>]`.
  - Status: {{PASS/FAIL}}
  - Evidence: {{citations checked}}

- [ ] **Conflicts documented** — All source conflicts have documented resolutions.
  - Status: {{PASS/FAIL}}

### Internal Consistency

- [ ] **Cross-references valid** — All file references point to files that exist.
  - Status: {{PASS/FAIL}}

- [ ] **Agent handoffs valid** — All handoff references point to agents that exist.
  - Status: {{PASS/FAIL}}

### Implementation Readiness

- [ ] **Package README explains usage** — How to run the workflow is documented.
  - Status: {{PASS/FAIL}}

- [ ] **Workflow defines all phases** — Each phase has purpose, inputs, outputs, responsible agent, validation criteria.
  - Status: {{PASS/FAIL}}

### File/Folder Completeness

- [ ] **No empty files** — Every file has real content.
  - Status: {{PASS/FAIL}}

- [ ] **No orphaned files** — Every file is referenced by an agent, workflow, or README.
  - Status: {{PASS/FAIL}}

### Agent-Role Clarity

- [ ] **Distinct roles** — No two agents have overlapping responsibilities.
  - Status: {{PASS/FAIL}}

- [ ] **Concrete responsibilities** — No "helps with" or "supports" without specifics.
  - Status: {{PASS/FAIL}}

### Skill Reusability

- [ ] **Skills reusable** — No skill is hardcoded to one project.
  - Status: {{PASS/FAIL}}

- [ ] **No duplicate skills** — No two skills serve the same purpose.
  - Status: {{PASS/FAIL}}

### Vague Instructions

- [ ] **No vague instructions** — No "handle", "manage", "support" without specifics.
  - Status: {{PASS/FAIL}}

### Hidden Assumptions

- [ ] **All assumptions labelled** — Every assumption has `[ASSUMPTION]` tag with reasoning.
  - Status: {{PASS/FAIL}}

### Missing Validation

- [ ] **Every phase has validation criteria**.
  - Status: {{PASS/FAIL}}

- [ ] **Every agent has a quality checklist**.
  - Status: {{PASS/FAIL}}

- [ ] **Every skill has validation criteria**.
  - Status: {{PASS/FAIL}}

### Overconfident Claims

- [ ] **No overconfident claims** — No "will", "guarantees", "best practice" without source.
  - Status: {{PASS/FAIL}}

### User-Objective Alignment

- [ ] **Every deliverable serves the objective**.
  - Status: {{PASS/FAIL}}

## Package-Specific Items

{{PACKAGE_SPECIFIC_ITEMS — add items specific to this domain/package. Example for website revamp:}}

- [ ] **Accessibility requirements target WCAG 2.1 AA** (sourced from W3C).
  - Status: {{PASS/FAIL}}
- [ ] **URL preservation constraint addressed**.
  - Status: {{PASS/FAIL}}

## Overall Recommendation

{{PASS / FAIL}}

---

## Fill Instructions

1. Run every checklist item. No skipping.
2. For each item, record status (PASS/FAIL), evidence (what was checked), and required fix (if fail).
3. Add package-specific items based on the domain and objective.
4. The overall recommendation is FAIL if any item fails. PASS only if all items pass.
5. Produce a structured report, not a narrative.