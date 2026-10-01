# Failure Mode and Effects Analysis (FMEA)

This document systematically identifies every way the Workflow Designer Agent can fail, scores the risk, and assigns mitigation ownership. It is a living document — updated whenever new failure modes are discovered.

## Scoring System

| Dimension | Scale | Meaning |
|-----------|-------|---------|
| Severity (S) | 1-10 | 1 = cosmetic, 10 = catastrophic (workflow unusable or causes harm) |
| Occurrence (O) | 1-10 | 1 = rare, 10 = frequent |
| Detection (D) | 1-10 | 1 = easily detected, 10 = undetectable until too late |
| RPN | S x O x D | Risk Priority Number. Threshold: **≥ 100 requires mandatory mitigation. ≥ 200 requires redesign.** |

## Failure Modes

### FM-001: Hallucinated Sources

| Field | Value |
|-------|-------|
| Failure mode | Domain-researcher fabricates a citation (fake URL, wrong author, invented standard) |
| Effect | Generated workflow is built on false premises; downstream agents propagate the error |
| Severity | 9 |
| Occurrence | 4 |
| Detection | 7 |
| RPN | 252 |
| Mitigation | (1) Source-log with retrieval IDs and fetch verification. (2) Dual-source requirement for compliance/regulatory claims. (3) validate-package.py checks citation format mechanically. (4) Independent verification phase re-checks sources. |
| Owner | domain-researcher |
| Status | Mitigated by source-log + retrieval IDs + dual-source rule |

### FM-002: Same-Model Self-Review Blind Spot

| Field | Value |
|-------|-------|
| Failure mode | QC and red-team agents share the same model biases and jointly miss an error |
| Effect | Subtle omissions, contradictions, or domain-specific errors pass all gates |
| Severity | 8 |
| Occurrence | 6 |
| Detection | 8 |
| RPN | 384 |
| Mitigation | (1) Independent Verification Phase (11.5) using a different model or deterministic script. (2) validate-package.py provides mechanical checks that do not rely on LLM judgement. (3) Oracle-in-the-loop gate for high-criticality workflows. |
| Owner | workflow-orchestrator |
| Status | Mitigated by Phase 11.5 + validate-package.py + Oracle gate |

### FM-003: Syntactic Completeness Without Semantic Coverage

| Field | Value |
|-------|-------|
| Failure mode | Agent/skill files have all required section headers but content does not actually cover the workstream |
| Effect | Workflow appears complete but has functional gaps |
| Severity | 7 |
| Occurrence | 5 |
| Detection | 6 |
| RPN | 210 |
| Mitigation | (1) Traceability matrix maps every requirement to a deliverable and verification method. (2) Quantitative QC criteria measure coverage, not just presence. (3) Red-team reviews from developer perspective: "can I implement this?" |
| Owner | quality-reviewer |
| Status | Mitigated by traceability matrix + quantitative QC |

### FM-004: Accepted Assumptions Become Hidden Requirements

| Field | Value |
|-------|-------|
| Failure mode | Intake-analyst labels missing info as assumptions and proceeds; high-risk assumptions silently become design foundations |
| Effect | Generated workflow does not match real constraints; fails in execution |
| Severity | 8 |
| Occurrence | 7 |
| Detection | 5 |
| RPN | 280 |
| Mitigation | (1) Assumption risk classification (low/medium/high/critical). (2) High/critical assumptions must be retired (verified) or formally accepted by Oracle. (3) Assumptions tracked in traceability matrix and FMEA. (4) Oracle-in-the-loop gate at requirements baseline. |
| Owner | intake-analyst |
| Status | Mitigated by assumption risk classification + Oracle gate |

### FM-005: Cross-Reference Decay

| Field | Value |
|-------|-------|
| Failure mode | Agent files reference skills or other files that do not exist or were renamed |
| Effect | Broken references; downstream agents cannot find required resources |
| Severity | 5 |
| Occurrence | 6 |
| Detection | 2 |
| RPN | 60 |
| Mitigation | validate-package.py mechanically checks all cross-references resolve. Runs before QC and after revision. |
| Owner | implementation-planner |
| Status | Mitigated by validate-package.py |

### FM-006: Non-Idempotent Generation

| Field | Value |
|-------|-------|
| Failure mode | Same objective produces different workflow packages across runs due to model stochasticity |
| Effect | Regression testing impossible; quality not reproducible |
| Severity | 6 |
| Occurrence | 8 |
| Detection | 3 |
| RPN | 144 |
| Mitigation | (1) Idempotency protocol: temperature=0, pinned model, fixed seed, deterministic file ordering. (2) Idempotency test runs workflow twice and diffs outputs. (3) Regression test suite with golden outputs. |
| Owner | workflow-orchestrator |
| Status | Mitigated by idempotency protocol + regression tests |

### FM-007: Domain Misclassification

| Field | Value |
|-------|-------|
| Failure mode | Domain label is wrong (e.g., security workflow designed with web conventions) |
| Effect | Wrong agents, wrong skills, wrong research; entire package is domain-inappropriate |
| Severity | 9 |
| Occurrence | 3 |
| Detection | 6 |
| RPN | 162 |
| Mitigation | (1) Domain classification requires confidence score. (2) Oracle-in-the-loop gate confirms domain before research begins. (3) Red-team reviews from domain-expert perspective. |
| Owner | intake-analyst |
| Status | Mitigated by confidence scoring + Oracle gate |

### FM-008: Revision Loop Exhaustion Without Resolution

| Field | Value |
|-------|-------|
| Failure mode | After 3 revision iterations, package escalates to user with unresolved defects |
| Effect | Known defects may be shipped if user approves without understanding |
| Severity | 7 |
| Occurrence | 4 |
| Detection | 4 |
| RPN | 112 |
| Mitigation | (1) Escalation report must include defect severity and impact analysis. (2) High/critical defects cannot be user-approved away — they must be fixed. (3) Error budget tracking: if escalation rate exceeds threshold, workflow design itself must be reviewed. |
| Owner | workflow-orchestrator |
| Status | Mitigated by escalation report requirements + error budget |

### FM-009: Vague Instructions Pass QC

| Field | Value |
|-------|-------|
| Failure mode | Agent descriptions with "helps with" or "handles" pass qualitative QC |
| Effect | Generated agents are not actionable; downstream execution fails |
| Severity | 6 |
| Occurrence | 5 |
| Detection | 4 |
| RPN | 120 |
| Mitigation | (1) validate-package.py mechanically detects vague verbs. (2) Quantitative QC: vague verb count must be 0. (3) Every responsibility must start with a verb and specify an object. |
| Owner | quality-reviewer |
| Status | Mitigated by validate-package.py + quantitative QC |

### FM-010: Source Staleness

| Field | Value |
|-------|-------|
| Failure mode | Cited source was accurate at research time but has since changed (e.g., API version, regulation update) |
| Effect | Generated workflow relies on outdated information |
| Severity | 7 |
| Occurrence | 6 |
| Detection | 7 |
| RPN | 294 |
| Mitigation | (1) All time-sensitive claims tagged with research date. (2) Source-log records fetch timestamp. (3) Reliability plan mandates re-verification period per domain (security: 30 days, legal: 90 days, technical: 60 days). (4) Generated package includes re-verification schedule. |
| Owner | domain-researcher |
| Status | Mitigated by time-sensitive tagging + re-verification schedule |

## Summary

| ID | Failure Mode | RPN | Status |
|----|-------------|-----|--------|
| FM-001 | Hallucinated sources | 252 | Mitigated |
| FM-002 | Same-model self-review blind spot | 384 | Mitigated |
| FM-003 | Syntactic completeness without semantic coverage | 210 | Mitigated |
| FM-004 | Accepted assumptions become hidden requirements | 280 | Mitigated |
| FM-005 | Cross-reference decay | 60 | Mitigated |
| FM-006 | Non-idempotent generation | 144 | Mitigated |
| FM-007 | Domain misclassification | 162 | Mitigated |
| FM-008 | Revision loop exhaustion | 112 | Mitigated |
| FM-009 | Vague instructions pass QC | 120 | Mitigated |
| FM-010 | Source staleness | 294 | Mitigated |

## Mitigation Verification

Every mitigation must be verified. The verification method is recorded here:

| Mitigation | Verification Method | Verified By |
|-----------|-------------------|-------------|
| Source-log + retrieval IDs | validate-package.py checks source-log structure | validate-package.py |
| Independent verification phase | Phase 11.5 in workflow.md; different model or script | workflow-orchestrator |
| Traceability matrix | validate-package.py checks requirement IDs and verification columns | validate-package.py |
| Assumption risk classification | QC checks all assumptions have risk level; high/critical retired or accepted | quality-reviewer |
| Idempotency protocol | test_idempotency.py runs workflow twice and diffs | test suite |
| Domain confidence scoring | Oracle gate confirms domain before research | Oracle-in-the-loop |
| Quantitative QC | validate-package.py + QC scoring matrix | quality-reviewer |
| Re-verification schedule | Source-log includes re-verification dates per domain | domain-researcher |