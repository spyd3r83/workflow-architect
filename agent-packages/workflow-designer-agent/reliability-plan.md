# Reliability Plan

This document defines the error budget, reliability targets, measurement methods, and continuous improvement protocol for the Workflow Designer Agent.

## Reliability Target

**Target error rate: < 0.1%** (less than 1 defect per 1000 generated deliverables).

This means: for every 1000 items the Workflow Designer Agent produces (agent files, skill files, workflow phases, research claims, cross-references), no more than 1 may contain a defect that escapes to the final package.

## Error Budget Allocation

The total error budget (0.1%) is allocated across phases. Each phase must stay within its allocation.

| Phase | Budget Allocation | Rationale |
|-------|------------------|-----------|
| Intake (1-3) | 0.02% | Assumptions are the main risk; mitigated by risk classification |
| Research (4-5) | 0.03% | Hallucinated sources are the main risk; mitigated by source-log + dual-source |
| Design (6-8) | 0.02% | Semantic coverage gaps; mitigated by traceability matrix |
| Implementation (9-10) | 0.01% | Structural errors; mitigated by validate-package.py |
| QC (11) | 0.01% | QC itself can miss errors; mitigated by quantitative criteria |
| Independent Verification (11.5) | 0.005% | Last mechanical gate before red-team |
| Red-Team (12) | 0.005% | Final adversarial gate |
| **Total** | **0.1%** | |

## Measurement Methods

| Method | What It Measures | Frequency |
|--------|-----------------|-----------|
| validate-package.py | Structural defects (missing files, sections, broken refs, placeholders, vague verbs) | Every package |
| Quantitative QC scoring | Semantic defects (coverage, assumption ratio, citation compliance) | Every package |
| Independent verification | Defects missed by QC (same-model blind spot) | Every package |
| Regression test suite | Defects introduced by changes to the Workflow Designer Agent | Every change |
| Idempotency test | Non-deterministic output (stochastic defects) | Every change |
| Human review sampling | Defects that escape all automated gates | 10% of packages |
| Post-delivery audit | Defects found after package is used | As reported |

## Reliability Metrics

| Metric | Target | Current | Measurement Method |
|--------|--------|---------|-------------------|
| Structural defect rate | 0% | 0% | validate-package.py |
| Citation format compliance | 100% | 100% | validate-package.py |
| Cross-reference resolution | 100% | 100% | validate-package.py |
| Vague verb count | 0 | 0 | validate-package.py |
| Assumption risk classification coverage | 100% | 100% | QC scoring |
| Source-log retrieval ID coverage | 100% | 100% | validate-package.py |
| Traceability matrix coverage | 100% | 100% | validate-package.py |
| FMEA mitigation coverage | 100% for RPN ≥ 100 | 100% | FMEA review |
| Independent verification pass rate | 100% | 100% | Phase 11.5 report |
| Idempotency test pass rate | 100% | 100% | test_idempotency.py |
| Regression test pass rate | 100% | 100% | test_regression.py |
| Human review defect escape rate | < 0.1% | TBD | Human sampling |

## Re-Verification Schedule

Domain-specific claims become stale. The re-verification schedule mandates when sourced claims must be re-checked.

| Domain | Re-Verification Period | Rationale |
|--------|----------------------|-----------|
| Security | 30 days | Vulnerability landscape changes rapidly |
| Technical (APIs, frameworks) | 60 days | Version updates and deprecations |
| Legal / compliance | 90 days | Regulatory updates |
| Marketing / market data | 60 days | Market conditions shift |
| Design / accessibility | 180 days | Standards evolve slowly |
| Business operations | 180 days | Processes evolve slowly |

## Continuous Improvement Protocol

1. **Defect logging**: Every defect found (by any method) is logged with: phase, severity, root cause, mitigation.
2. **Root cause analysis**: For every defect with severity ≥ high, conduct RCA to determine why existing gates did not catch it.
3. **Gate improvement**: If a gate missed a defect, strengthen that gate (add a check, lower a threshold, add a test case).
4. **FMEA update**: New failure modes discovered through defects are added to fmea.md.
5. **Regression test update**: New defect types get regression test cases to prevent recurrence.
6. **Error budget review**: If a phase exceeds its error budget, halt and review the phase design.

## Escalation Protocol

| Condition | Action |
|-----------|--------|
| Error budget exceeded for any phase | Halt generation; review phase design; strengthen gates |
| Same defect type occurs 3 times | Add regression test case; update FMEA; review root cause |
| Independent verification fails | Do not proceed to red-team; route to revision loop |
| Idempotency test fails | Halt; investigate model configuration; enforce deterministic settings |
| Human review finds defect escaped all gates | Add mechanical check to validate-package.py; update FMEA |

## Idempotency Protocol

To achieve deterministic output:

| Parameter | Required Value |
|-----------|---------------|
| Model temperature | 0 |
| Model | Pinned (specific version, not "latest") |
| Seed | Fixed (if supported by model) |
| File generation order | Alphabetical by path |
| Phase execution | Sequential (no parallel phases in generation mode) |

The idempotency test (`tests/test_idempotency.py`) runs the workflow twice with the same input and compares outputs. Any difference is a failure.

## Version Control

| Artifact | Versioning |
|----------|-----------|
| Canonical package files | Git-tracked; every change is a commit |
| Generated platform files | Regenerated by sync-platform-configs.py; not hand-edited |
| Validation reports | Generated per-run; archived for audit |
| Golden test outputs | Git-tracked; changes require explicit approval |
| FMEA | Living document; updated when new failure modes found |
| Reliability plan | Reviewed quarterly; updated when metrics change |