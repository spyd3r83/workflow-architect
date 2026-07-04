# Workflow Designer Agent

A reusable meta-agent package that designs domain-specific agent workflows on demand. Give it a project objective; it returns a complete, implementation-ready agent workflow package.

## What This Is

The Workflow Designer Agent is a meta-agent. Its job is not to execute a project directly. Its job is to **design other agent workflows**. You provide a high-level objective (e.g., "revamp a marketing website", "build a new mobile app", "stand up a compliance review process"), and the agent produces a full folder/file package containing specialized agents, reusable skills, a sequenced workflow, intake model, research protocol, QA process, red-team review process, templates, examples, and implementation instructions.

The output package is structured to be dropped into an OpenCode-style project and used immediately by other agents without additional explanation.

## When To Use It

- You are starting a new project domain and want a structured agent workflow rather than ad-hoc prompting.
- You want to standardize how a team of agents collaborates on a recurring project type.
- You need a repeatable workflow with built-in quality control and adversarial review.
- You want to package a workflow so another agent (or another engineer) can execute it without you in the loop.

## When NOT To Use It

- Single-file fixes or trivial changes. Use direct tools instead.
- Projects where the workflow already exists and only needs minor edits.
- One-off research questions that do not require a multi-agent package.

## Inputs Expected

The Workflow Designer Agent accepts:

1. **Project objective** (required) — one or two sentences describing what the workflow should accomplish.
2. **Domain** (optional) — e.g., legal, security, marketing, web, product. If omitted, the agent infers it.
3. **Constraints** (optional) — timeline, tools, compliance, team size, budget.
4. **Source materials** (optional) — documents, specs, existing code, links. Attached for the domain-researcher agent to review.
5. **Success criteria** (optional) — what "done" looks like for the generated workflow.

Missing inputs are handled by the intake-analyst agent, which asks only essential clarifying questions and otherwise records labelled assumptions. See `intake.md`.

## Outputs Generated

A complete workflow package with this structure:

```
new-workflow-package/
  README.md
  AGENTS.md
  workflow.md
  intake.md
  research-protocol.md
  quality-control.md
  red-team-review.md
  agents/        (specialized agent definitions)
  skills/        (reusable skill definitions)
  prompts/       (invocation prompts)
  templates/     (fill-in-the-blank structures)
  examples/      (reference outputs)
```

Every generated package includes: workflow purpose, labelled assumptions, intake model, agent architecture, skill architecture, research protocol, execution flow, file structure, QC loop, red-team loop, final deliverable spec, implementation instructions, and known limitations. See `package-output-spec.md` for the full specification.

## How To Run It

### Option A: Use the master prompt

Open `prompts/master-workflow-designer-prompt.md`, paste it into an agent session, and replace the `{{PROJECT_OBJECTIVE}}` placeholder with your objective. The agent will execute the 18-phase workflow defined in `workflow.md` and produce the package.

### Option B: Use the parameterized prompt

Open `prompts/generate-new-agent-package.md`, fill in the parameters (`{{PROJECT_OBJECTIVE}}`, `{{DOMAIN}}`, `{{CONSTRAINTS}}`, `{{SOURCE_MATERIALS}}`), and paste into an agent session.

### Option C: Invoke via implementation guide

Follow the step-by-step instructions in `implementation-guide.md` for attaching source materials, reviewing output, iterating, and promoting a generated workflow into a permanent agent package.

## How To Adapt For Different Domains

The package is domain-agnostic by design. To adapt:

1. **Identify the domain** during intake (Phase 3 of the workflow).
2. **Customize the research protocol** — the `research-protocol.md` supports legal, technical, product, security, design, marketing, and business operations domains out of the box.
3. **Use the example prompts** as starting points:
   - `prompts/website-revamp-workflow-example.md`
   - `prompts/new-app-workflow-example.md`
   - `prompts/security-workflow-example.md`
4. **Reference the example packages** in `examples/` to see how agents and skills are specialized for a domain.

## How To Validate Its Output

Every generated package must pass **four gates** before it is considered final:

1. **Deterministic validation** — run `scripts/validate-package.py`. Checks structure, sections, cross-references, citations, placeholders, and vague verbs mechanically (not LLM-based). Must PASS.
2. **Quality control** — run the quantitative checklist in `quality-control.md`. 15 measurable criteria (Q1-Q15) with numeric thresholds. All must meet targets.
3. **Independent verification** — Phase 11.5: a different model or deterministic script verifies the package without seeing QC results (no anchoring). Must PASS.
4. **Red-team review** — run the FMEA-scored adversarial review in `red-team-review.md`. All 6 perspectives covered. All mandatory (critical/high) issues resolved.

Additionally, **three Oracle gates** provide independent high-reasoning review:
- After Phase 1.5 (requirements formalization)
- After Phase 3 (domain classification)
- After Phase 12 (pre-finalization)

If any gate fails, the workflow enters a revision loop (Phase 13) until all pass or the orchestrator escalates.

### Quick Validation Checklist

- [ ] All required files present (see `package-output-spec.md`).
- [ ] Every agent file has all 10 required sections.
- [ ] Every skill file has all 8 required sections.
- [ ] Assumptions are explicitly labelled, not hidden.
- [ ] Source notes preserved where research was used.
- [ ] QA checklist completed and passed.
- [ ] Red-team review completed with pass/fail recorded.
- [ ] Limitations section present.
- [ ] Package is usable by another agent without additional explanation.

## Package Structure

```
workflow-designer-agent/
  README.md                      (this file)
  AGENTS.md                      (operating instructions)
  workflow.md                    (18-phase end-to-end workflow with Oracle gates)
  intake.md                      (minimal intake model with risk classification)
  research-protocol.md           (source-backed research with chain-of-custody)
  quality-control.md             (QC system with 15 quantitative criteria)
  red-team-review.md             (FMEA-scored adversarial review)
  implementation-guide.md        (how to use this package)
  package-output-spec.md         (what the agent must output)
  requirements.md                (formal requirements with IDs and acceptance criteria)
  fmea.md                        (failure mode and effects analysis with RPN)
  traceability-matrix.md         (requirement-to-deliverable traceability)
  reliability-plan.md            (error budget, metrics, idempotency protocol)
  source-log.md                  (source chain-of-custody with retrieval IDs)
  agents/                        (9 agent definitions)
  skills/                        (10 reusable skills)
  prompts/                       (5 invocation + example prompts)
  templates/                     (18 fill-in templates)
  examples/                      (2 reference package examples)
  tests/                         (regression + idempotency test suite)
```

## Space-Level Reliability

This package implements aerospace-grade reliability controls:

- **Independent Verification (Phase 11.5)**: Breaks same-model self-review blind spot
- **FMEA**: Systematic failure mode analysis with RPN scoring (10 modes tracked)
- **Traceability Matrix**: Every requirement traced to deliverable and verification method (20 requirements)
- **Quantitative QC**: 15 measurable acceptance criteria with numeric thresholds
- **Source Chain-of-Custody**: Every citation has a retrieval ID with fetch metadata
- **Oracle-in-the-Loop Gates**: Independent high-reasoning review at 3 critical points
- **Idempotency Protocol**: temperature=0, pinned model, deterministic output
- **Regression Tests**: Automated test suite verifies package integrity
- **Error Budget**: < 0.1% target error rate, allocated across phases
- **Rollback Protocol**: Versioned drafts with rollback on post-delivery failure

## Limitations

- The Workflow Designer Agent produces workflow packages, not executed deliverables. It designs the workflow; other agents execute it.
- Research quality depends on available sources. The agent will label assumptions when sources are unavailable rather than fabricate facts.
- The first draft is never final. The revision loop (Phase 13) is mandatory.
- The package does not auto-discover project-specific conventions. If your project has existing agent/skill folder conventions, state them during intake so the generated package follows them.

## See Also

- `AGENTS.md` — operating instructions for the agent hierarchy
- `workflow.md` — the 18-phase workflow with Oracle gates
- `implementation-guide.md` — step-by-step usage instructions
- `package-output-spec.md` — output specification