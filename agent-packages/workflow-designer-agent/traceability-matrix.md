# Traceability Matrix

This matrix traces every requirement derived from the user objective, domain research, and compliance needs to a specific deliverable, verification method, and status. No requirement is untraced. No deliverable is unrequired.

## Requirements

### REQ-001: Understand high-level project objective

| Field | Value |
|-------|-------|
| Source | User input (intake) |
| Type | Functional |
| Priority | Critical |
| Deliverable | Intake document (intake.md) |
| Verification Method | Intake document contains refined objective statement; all 11 fields addressed |
| Status | Verified |

### REQ-002: Identify domain and project type

| Field | Value |
|-------|-------|
| Source | Intake (Phase 3) |
| Type | Functional |
| Priority | Critical |
| Deliverable | Domain classification in intake document |
| Verification Method | Domain label present with confidence score; Oracle gate confirmed |
| Status | Verified |

### REQ-003: Ask only essential intake questions

| Field | Value |
|-------|-------|
| Source | Design rule (intake.md) |
| Type | Non-functional |
| Priority | High |
| Deliverable | Intake document with labelled assumptions |
| Verification Method | Question count ≤ 5; all missing fields have labelled assumptions |
| Status | Verified |

### REQ-004: Make reasonable assumptions when information is missing

| Field | Value |
|-------|-------|
| Source | Design rule (intake.md) |
| Type | Functional |
| Priority | High |
| Deliverable | Assumptions section in intake document |
| Verification Method | Every assumption labelled with reasoning and confidence; risk classification assigned |
| Status | Verified |

### REQ-005: Research domain using authoritative sources

| Field | Value |
|-------|-------|
| Source | Design rule (research-protocol.md) |
| Type | Functional |
| Priority | Critical |
| Deliverable | Research summary with citations |
| Verification Method | Every claim tagged [VERIFIED] or [ASSUMPTION]; citations in correct format; source-log has retrieval IDs |
| Status | Verified |

### REQ-006: Preserve source citations

| Field | Value |
|-------|-------|
| Source | Design rule (research-protocol.md) |
| Type | Non-functional |
| Priority | Critical |
| Deliverable | Source-log.md with retrieval IDs and fetch metadata |
| Verification Method | validate-package.py checks source-log structure; citations include retrieval IDs |
| Status | Verified |

### REQ-007: Design specialized agents for the project

| Field | Value |
|-------|-------|
| Source | User objective (Phase 7) |
| Type | Functional |
| Priority | Critical |
| Deliverable | Agent definition files in agents/ |
| Verification Method | Every agent has all 10 required sections; roles are distinct; validate-package.py confirms |
| Status | Verified |

### REQ-008: Design reusable skills for the project

| Field | Value |
|-------|-------|
| Source | User objective (Phase 8) |
| Type | Functional |
| Priority | Critical |
| Deliverable | Skill definition files in skills/ |
| Verification Method | Every skill has all 8 required sections; skills are reusable; validate-package.py confirms |
| Status | Verified |

### REQ-009: Create sequenced workflow from intake to final delivery

| Field | Value |
|-------|-------|
| Source | User objective (Phase 6) |
| Type | Functional |
| Priority | Critical |
| Deliverable | workflow.md with phased sequence |
| Verification Method | Every phase has purpose, inputs, outputs, responsible agent, validation criteria; revision loop defined |
| Status | Verified |

### REQ-010: Create repo-ready file and folder structures

| Field | Value |
|-------|-------|
| Source | User objective (Phase 9-10) |
| Type | Functional |
| Priority | Critical |
| Deliverable | Complete package on disk |
| Verification Method | File tree matches package-output-spec.md; validate-package.py confirms all files exist |
| Status | Verified |

### REQ-011: Include quality-control review loop

| Field | Value |
|-------|-------|
| Source | Design rule (quality-control.md) |
| Type | Functional |
| Priority | Critical |
| Deliverable | QC report |
| Verification Method | All 18 QC dimensions evaluated; quantitative thresholds met; validate-package.py passed |
| Status | Verified |

### REQ-012: Include red-team review loop

| Field | Value |
|-------|-------|
| Source | Design rule (red-team-review.md) |
| Type | Functional |
| Priority | Critical |
| Deliverable | Red-team report |
| Verification Method | All 6 perspectives covered; all mandatory issues resolved; FMEA reviewed |
| Status | Verified |

### REQ-013: Include independent verification

| Field | Value |
|-------|-------|
| Source | Reliability plan (FMEA FM-002) |
| Type | Functional |
| Priority | Critical |
| Deliverable | Independent verification report |
| Verification Method | Phase 11.5 executed by different model or deterministic script; report shows PASS |
| Status | Verified |

### REQ-014: Include failure mode analysis

| Field | Value |
|-------|-------|
| Source | Reliability plan |
| Type | Functional |
| Priority | Critical |
| Deliverable | fmea.md |
| Verification Method | FMEA has RPN scoring; all RPN ≥ 100 have mitigations; validate-package.py confirms structure |
| Status | Verified |

### REQ-015: Include traceability matrix

| Field | Value |
|-------|-------|
| Source | Reliability plan |
| Type | Functional |
| Priority | Critical |
| Deliverable | traceability-matrix.md (this file) |
| Verification Method | Every requirement traces to deliverable and verification method; validate-package.py confirms |
| Status | Verified |

### REQ-016: Distinguish assumptions from verified facts

| Field | Value |
|-------|-------|
| Source | Design rule |
| Type | Non-functional |
| Priority | Critical |
| Deliverable | Tagged claims throughout package |
| Verification Method | Every claim tagged [VERIFIED] or [ASSUMPTION]; assumptions have risk classification |
| Status | Verified |

### REQ-017: Include known limitations

| Field | Value |
|-------|-------|
| Source | Design rule |
| Type | Non-functional |
| Priority | High |
| Deliverable | Limitations section in README.md |
| Verification Method | Limitations section present and honest |
| Status | Verified |

### REQ-018: Package is immediately usable by another agent

| Field | Value |
|-------|-------|
| Source | Design rule |
| Type | Non-functional |
| Priority | Critical |
| Deliverable | Complete self-contained package |
| Verification Method | README explains usage; workflow defines all phases; templates are fillable; validate-package.py passes |
| Status | Verified |

### REQ-019: First draft is never final; revision loop included

| Field | Value |
|-------|-------|
| Source | Design rule |
| Type | Functional |
| Priority | High |
| Deliverable | Revision loop in workflow.md |
| Verification Method | Phase 13 defined; max 3 iterations; escalation protocol defined |
| Status | Verified |

### REQ-020: Idempotency guarantees

| Field | Value |
|-------|-------|
| Source | Reliability plan (FMEA FM-006) |
| Type | Non-functional |
| Priority | High |
| Deliverable | Idempotency protocol in workflow.md |
| Verification Method | test_idempotency.py runs workflow twice and confirms identical output |
| Status | Verified |

## Coverage Check

| Objective Component | Requirement IDs | Deliverables |
|---------------------|-----------------|--------------|
| Understand objective | REQ-001, REQ-003, REQ-004 | Intake document |
| Identify domain | REQ-002 | Domain classification |
| Research domain | REQ-005, REQ-006 | Research summary, source-log |
| Design agents | REQ-007 | Agent files |
| Design skills | REQ-008 | Skill files |
| Sequence workflow | REQ-009 | workflow.md |
| Create file structure | REQ-010 | Package on disk |
| Quality control | REQ-011, REQ-013 | QC report, independent verification |
| Red-team review | REQ-012 | Red-team report |
| Failure mode analysis | REQ-014 | fmea.md |
| Traceability | REQ-015 | This matrix |
| Assumption management | REQ-016, REQ-004 | Tagged claims, risk classification |
| Limitations | REQ-017 | README limitations section |
| Usability | REQ-018 | Complete package |
| Revision loop | REQ-019 | Phase 13 |
| Idempotency | REQ-020 | Idempotency protocol |

## Untraced Deliverables Check

Every deliverable in the package must trace to at least one requirement. If a deliverable has no tracing requirement, it is either:
1. Unnecessary — remove it.
2. Missing a requirement — add one.

| Deliverable | Traced To |
|-----------|-----------|
| README.md | REQ-017, REQ-018 |
| AGENTS.md | REQ-018 |
| workflow.md | REQ-009, REQ-019, REQ-020 |
| intake.md | REQ-001, REQ-003, REQ-004 |
| research-protocol.md | REQ-005, REQ-006 |
| quality-control.md | REQ-011 |
| red-team-review.md | REQ-012 |
| package-output-spec.md | REQ-010, REQ-018 |
| fmea.md | REQ-014 |
| traceability-matrix.md | REQ-015 |
| reliability-plan.md | REQ-013, REQ-014, REQ-020 |
| source-log.md | REQ-006 |
| requirements.md | REQ-001, REQ-015 |
| agents/*.md | REQ-007 |
| skills/*.md | REQ-008 |
| prompts/*.md | REQ-018 |
| templates/*.md | REQ-018 |
| examples/*.md | REQ-018 |