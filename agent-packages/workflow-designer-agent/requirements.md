# Requirements — Workflow Designer Agent

This document formalizes the requirements derived from the user objective, domain research, and compliance needs. Every requirement has a unique ID, priority, type, and acceptance criteria. Requirements are traced to deliverables in `traceability-matrix.md`.

## Requirement Types

| Type | Description |
|------|-------------|
| Functional | What the system must do |
| Non-functional | How the system must behave (quality attributes) |
| Safety | What the system must not do |
| Regulatory | What the system must comply with |

## Priority Levels

| Priority | Description |
|----------|-------------|
| Critical | Must be satisfied; failure blocks finalization |
| High | Must be satisfied; failure triggers revision loop |
| Medium | Should be satisfied; failure documented in final summary |
| Low | Nice to have; failure noted but does not block |

## Requirements

### REQ-001: Understand high-level project objective

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | User input |
| Description | The Workflow Designer Agent must accept a high-level project objective and refine it into a precise, actionable statement. |
| Acceptance Criteria | (1) Objective refined to 1-2 sentences. (2) Scope boundaries explicit. (3) Objective confirmed by orchestrator or user. |
| Traced Deliverable | Intake document (intake.md) |

### REQ-002: Identify domain and project type

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | Intake (Phase 3) |
| Description | The agent must classify the project domain with a confidence score. |
| Acceptance Criteria | (1) Domain label assigned. (2) Confidence score (high/medium/low). (3) Oracle gate confirms domain before research. (4) Domain-specific risks identified. |
| Traced Deliverable | Domain classification in intake document |

### REQ-003: Minimal intake questioning

| Field | Value |
|-------|-------|
| Type | Non-functional |
| Priority | High |
| Source | Design rule |
| Description | The intake must ask at most 5 clarifying questions. |
| Acceptance Criteria | (1) Question count ≤ 5. (2) All missing fields have labelled assumptions. (3) No question asked when a reasonable assumption can be made. |
| Traced Deliverable | Intake document |

### REQ-004: Labelled assumptions with risk classification

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | Design rule + FMEA FM-004 |
| Description | Every assumption must be labelled with reasoning, confidence, and risk classification. High/critical assumptions must be retired or formally accepted. |
| Acceptance Criteria | (1) Every assumption has [ASSUMPTION] tag. (2) Every assumption has reasoning and confidence. (3) Every assumption has risk level (low/medium/high/critical). (4) High/critical assumptions retired or formally accepted by user. |
| Traced Deliverable | Assumptions section in intake document |

### REQ-005: Source-backed research

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | Design rule |
| Description | Domain-specific claims must be sourced from authoritative sources following the source hierarchy. |
| Acceptance Criteria | (1) Every factual claim tagged [VERIFIED] or [ASSUMPTION]. (2) [VERIFIED] claims have citations in correct format. (3) No fabricated sources. (4) Source hierarchy applied. (5) Conflicts documented. |
| Traced Deliverable | Research summary |

### REQ-006: Source chain-of-custody

| Field | Value |
|-------|-------|
| Type | Non-functional |
| Priority | Critical |
| Source | FMEA FM-001, FM-010 |
| Description | Every cited source must have a retrieval ID and fetch metadata in source-log.md. |
| Acceptance Criteria | (1) source-log.md exists. (2) Every citation has a retrieval ID (RET-XXX). (3) Source-log includes fetch timestamp, URL, retrieval status. (4) Compliance/regulatory claims verified by second independent source. |
| Traced Deliverable | source-log.md |

### REQ-007: Specialized agent design

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | User objective |
| Description | The agent must design specialized agents for the workflow, each with all 10 required sections. |
| Acceptance Criteria | (1) Every workstream has a responsible agent. (2) Every agent file has all 10 sections. (3) Agent roles are distinct. (4) No vague descriptions. (5) Handoffs explicit. (6) validate-package.py confirms. |
| Traced Deliverable | Agent definition files |

### REQ-008: Reusable skill design

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | User objective |
| Description | The agent must design reusable skills, each with all 8 required sections. |
| Acceptance Criteria | (1) Every reusable capability has a skill. (2) Every skill file has all 8 sections. (3) Skills are reusable (not hardcoded). (4) No duplicate skills. (5) Every skill has example usage. (6) validate-package.py confirms. |
| Traced Deliverable | Skill definition files |

### REQ-009: Sequenced workflow with gates

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | User objective |
| Description | The agent must create a phased workflow with gates, handoffs, and a revision loop. |
| Acceptance Criteria | (1) Every phase has purpose, inputs, outputs, responsible agent, validation criteria. (2) Gates between phases. (3) Revision loop defined. (4) Oracle-in-the-loop gates at critical points. (5) Idempotency protocol specified. |
| Traced Deliverable | workflow.md |

### REQ-010: Repo-ready file structure

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | User objective |
| Description | The agent must produce a complete file/folder package on disk. |
| Acceptance Criteria | (1) File tree matches package-output-spec.md. (2) All files populated (no empty/placeholder). (3) Cross-references valid. (4) validate-package.py passes. |
| Traced Deliverable | Package on disk |

### REQ-011: Quality control with quantitative criteria

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | Design rule + FMEA FM-009 |
| Description | QC must use quantitative acceptance criteria, not just qualitative checklists. |
| Acceptance Criteria | (1) All 13+ dimensions evaluated. (2) Quantitative thresholds defined and met. (3) validate-package.py passed before LLM-based QC. (4) Every fail has actionable fix. |
| Traced Deliverable | QC report |

### REQ-012: Red-team review with FMEA scoring

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | Design rule |
| Description | Red-team must review from 6 perspectives with quantitative severity scoring. |
| Acceptance Criteria | (1) All 6 perspectives covered. (2) Every issue has severity, fix, mandatory/optional. (3) FMEA reviewed for new failure modes. (4) All mandatory issues resolved. |
| Traced Deliverable | Red-team report |

### REQ-013: Independent verification

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | FMEA FM-002 |
| Description | An independent verification phase must check the package using a different model or deterministic script. |
| Acceptance Criteria | (1) Phase 11.5 executed. (2) Verifier is independent (different model or script). (3) Verifier does not see QC results (no anchoring). (4) Report shows PASS. |
| Traced Deliverable | Independent verification report |

### REQ-014: Failure mode analysis

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | Reliability plan |
| Description | FMEA must identify failure modes with RPN scoring and mitigations. |
| Acceptance Criteria | (1) fmea.md exists. (2) Failure modes have severity, occurrence, detection, RPN. (3) All RPN ≥ 100 have mitigations. (4) Mitigations have verification methods. |
| Traced Deliverable | fmea.md |

### REQ-015: Traceability matrix

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | Critical |
| Source | Reliability plan |
| Description | Every requirement must trace to a deliverable and verification method. |
| Acceptance Criteria | (1) traceability-matrix.md exists. (2) Every requirement has ID, deliverable, verification. (3) No untraced deliverables. (4) Coverage check passes. |
| Traced Deliverable | traceability-matrix.md |

### REQ-016: Assumption vs fact distinction

| Field | Value |
|-------|-------|
| Type | Non-functional |
| Priority | Critical |
| Source | Design rule |
| Description | Every claim must be tagged as [VERIFIED] or [ASSUMPTION]. No untagged claims. |
| Acceptance Criteria | (1) No untagged claims in package. (2) Assumptions have risk classification. (3) Verified claims have citations. |
| Traced Deliverable | Tagged claims throughout package |

### REQ-017: Known limitations documented

| Field | Value |
|-------|-------|
| Type | Non-functional |
| Priority | High |
| Source | Design rule |
| Description | The package must include honest limitations. |
| Acceptance Criteria | (1) Limitations section in README. (2) Limitations are specific, not generic. (3) Risk controls documented. |
| Traced Deliverable | README.md limitations section |

### REQ-018: Self-contained package

| Field | Value |
|-------|-------|
| Type | Non-functional |
| Priority | Critical |
| Source | Design rule |
| Description | The package must be usable by another agent without additional explanation. |
| Acceptance Criteria | (1) README explains usage. (2) Workflow defines all phases. (3) Templates are fillable. (4) validate-package.py passes. |
| Traced Deliverable | Complete package |

### REQ-019: Revision loop

| Field | Value |
|-------|-------|
| Type | Functional |
| Priority | High |
| Source | Design rule |
| Description | The first draft is never final; a revision loop must exist. |
| Acceptance Criteria | (1) Phase 13 defined. (2) Max 3 iterations. (3) Escalation protocol defined. (4) Escalation report includes severity and impact. |
| Traced Deliverable | workflow.md Phase 13 |

### REQ-020: Idempotency

| Field | Value |
|-------|-------|
| Type | Non-functional |
| Priority | High |
| Source | FMEA FM-006 |
| Description | Same input must produce same output. |
| Acceptance Criteria | (1) Temperature=0, pinned model, fixed seed. (2) Deterministic file ordering. (3) test_idempotency.py passes. |
| Traced Deliverable | Idempotency protocol in workflow.md |

## Requirements Coverage

| Source | Requirements |
|-------|-------------|
| User objective | REQ-001, REQ-007, REQ-008, REQ-009, REQ-010 |
| Design rules | REQ-003, REQ-004, REQ-005, REQ-011, REQ-012, REQ-016, REQ-017, REQ-018, REQ-019 |
| Reliability plan / FMEA | REQ-006, REQ-013, REQ-014, REQ-015, REQ-020 |
| Intake | REQ-002 |