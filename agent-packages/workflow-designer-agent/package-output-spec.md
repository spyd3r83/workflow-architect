# Package Output Specification — Workflow Designer Agent

This file defines exactly what the Workflow Designer Agent must output when asked to create a new workflow package. The output is a complete folder of files, not advice or a description.

## Output Structure

Every generated workflow package must have this structure:

```
<package-name>/
  README.md
  AGENTS.md
  CLAUDE.md
  opencode.json
  workflow.md
  intake.md
  research-protocol.md
  quality-control.md
  red-team-review.md
  requirements.md
  fmea.md
  traceability-matrix.md
  reliability-plan.md
  source-log.md
  improvement-protocol.md
  CHANGELOG.md
  defect-patterns.md
  agents/
    <agent-1>.md
    <agent-2>.md
    ...
  skills/
    <skill-1>.md
    <skill-2>.md
    ...
  prompts/
    <master-prompt>.md
    <example-prompt-1>.md
    ...
  templates/
    agent-file-template.md
    skill-file-template.md
    workflow-package-template.md
    intake-template.md
    qa-checklist-template.md
    red-team-template.md
    final-summary-template.md
    fmea-template.md
    traceability-matrix-template.md
    requirements-template.md
    source-log-template.md
    command-flowstart-template.md
    command-resume-template.md
    command-maintain-template.md
    command-update-template.md
    platform-config-template.md
    improvement-protocol-template.md
    changelog-template.md
    defect-patterns-template.md
  examples/
    <example-1>.md
    ...
  tests/
    test_regression.py
    test_idempotency.py
    golden/
      <golden-output-files>
  commands/
    flowstart.md
    resume.md
    maintain.md
    update.md
  .opencode/
    commands/
      <command-name>.md
      <command-name>-resume.md
      <command-name>-maintain.md
  .claude/
    commands/
      <command-name>.md
      <command-name>-resume.md
      <command-name>-maintain.md
  .codex/
    commands/
      <command-name>.md
      <command-name>-resume.md
      <command-name>-maintain.md
  .github/
    commands/
      <command-name>.md
      <command-name>-resume.md
      <command-name>-maintain.md
  <command-name>.devin.md
  <command-name>-resume.devin.md
  <command-name>-maintain.devin.md
```

## Required Content In Every Generated Package

| # | Content | Where It Lives | Required |
|---|---------|---------------|----------|
| 1 | Workflow purpose | README.md | Yes |
| 2 | Assumptions (with risk classification) | README.md (dedicated section) | Yes |
| 3 | Intake model | intake.md | Yes |
| 4 | Agent architecture | AGENTS.md + agents/ | Yes |
| 5 | Skill architecture | skills/ | Yes |
| 6 | Research protocol | research-protocol.md | Yes |
| 7 | Execution flow | workflow.md | Yes |
| 8 | File structure | README.md (file tree section) | Yes |
| 9 | Quality-control loop (quantitative) | quality-control.md | Yes |
| 10 | Red-team loop (FMEA-scored) | red-team-review.md | Yes |
| 11 | Final deliverable package | The package itself | Yes |
| 12 | Implementation instructions | README.md (how-to section) | Yes |
| 13 | Limitations and risk controls | README.md (dedicated section) | Yes |
| 14 | Formal requirements | requirements.md | Yes |
| 15 | Failure mode analysis | fmea.md | Yes |
| 16 | Traceability matrix | traceability-matrix.md | Yes |
| 17 | Reliability plan | reliability-plan.md | Yes |
| 18 | Source chain-of-custody | source-log.md | Yes |
| 19 | Independent verification | workflow.md (Phase 11.5) | Yes |
| 20 | Oracle-in-the-loop gates | workflow.md | Yes |
| 21 | Idempotency protocol | workflow.md + reliability-plan.md | Yes |
| 22 | Regression tests | tests/ | Yes |
| 23 | Deterministic validation | scripts/validate-package.py | Yes |
| 24 | Slash commands (flowstart, resume, maintain) | commands/ + platform command dirs | Yes |
| 25 | Platform config (opencode.json) | opencode.json | Yes |
| 26 | Claude Code instructions | CLAUDE.md | Yes |
| 27 | Cross-platform command files | .opencode/commands/, .claude/commands/, .codex/commands/, .github/commands/, *.devin.md | Yes |
| 28 | Command templates | templates/command-*-template.md, templates/platform-config-template.md | Yes |
| 29 | Self-improvement protocol | improvement-protocol.md | Yes |
| 30 | Changelog | CHANGELOG.md | Yes |
| 31 | Defect patterns database | defect-patterns.md | Yes |
| 32 | /update command (self-improvement) | commands/ + platform command dirs | Yes |

## File Requirements

### README.md (generated package)

Must include:
- **Workflow purpose** — what this workflow accomplishes.
- **When to use** — scenarios where this workflow applies.
- **Inputs expected** — what the workflow needs to run.
- **Outputs generated** — what the workflow produces.
- **How to run** — step-by-step invocation instructions.
- **File structure** — the complete file tree with descriptions.
- **Assumptions** — all labelled assumptions from intake and research.
- **Limitations** — known limitations and risk controls.
- **See also** — references to other files in the package.

### AGENTS.md (generated package)

Must include:
- **Purpose** — the workflow's purpose.
- **Agent hierarchy** — visual tree of agents.
- **Collaboration model** — how agents hand off work.
- **Research behaviour** — when research is required (reference to research-protocol.md).
- **QC rules** — reference to quality-control.md.
- **Red-team rules** — reference to red-team-review.md.
- **Final packaging requirements** — what "done" looks like.

### workflow.md (generated package)

Must include:
- **All workflow phases** — each with: purpose, inputs, outputs, responsible agent, validation criteria.
- **Phase ordering** — phases are sequential with gates.
- **Revision loop** — explicit description of the revision process.

### intake.md (generated package)

Must include:
- **Intake fields** — all fields relevant to the domain.
- **Assumption labelling format** — `[ASSUMPTION]` with reasoning and confidence.
- **When to ask vs assume** — guidance for the intake agent.

### research-protocol.md (generated package)

Must include:
- **When research is required** — domain-specific triggers.
- **Source hierarchy** — ranked sources for the domain.
- **Citation format** — `[Source: ...]`.
- **Conflict handling** — how to resolve conflicting sources.
- **Verified vs assumption tagging** — `[VERIFIED]` / `[ASSUMPTION]`.
- **Time-sensitive claims** — flagging and re-verification.

### quality-control.md (generated package)

Must include:
- **QC dimensions** — what is checked.
- **QC checklist** — all items with pass/fail.
- **QC report format** — structured output.
- **Failure handling** — revision loop integration.

### red-team-review.md (generated package)

Must include:
- **Review perspectives** — critic, client, developer, auditor, user, opposing stakeholder.
- **What is challenged** — the 10 challenge areas.
- **Report format** — issues with severity, fix, mandatory/optional.
- **Pass/fail criteria** — critical/high = mandatory, medium/low = optional.
- **Domain-specific attack vectors** — challenges specific to the domain.

### agents/ (generated package)

Each agent file must include all 10 sections:
1. Role
2. Mission
3. Responsibilities
4. Required Inputs
5. Expected Outputs
6. Operating Rules
7. Decision Criteria
8. Escalation Rules
9. Quality Checklist
10. Failure Modes to Avoid

The number of agents depends on the domain. Minimum: 3 (orchestrator, doer, reviewer). Typical: 5-9.

### skills/ (generated package)

Each skill file must include all 8 sections:
1. Purpose
2. When to Use
3. Required Inputs
4. Process
5. Output Format
6. Validation Criteria
7. Common Mistakes
8. Example Usage

The number of skills depends on the domain. Minimum: 3. Typical: 5-10.

### prompts/ (generated package)

Must include:
- **Master prompt** — the main invocation prompt for the generated workflow.
- **At least one example prompt** — showing how to invoke the workflow for a specific use case.

### templates/ (generated package)

Must include all 18 templates:
- agent-file-template.md
- skill-file-template.md
- workflow-package-template.md
- intake-template.md
- qa-checklist-template.md
- red-team-template.md
- final-summary-template.md
- fmea-template.md
- traceability-matrix-template.md
- requirements-template.md
- source-log-template.md
- command-flowstart-template.md
- command-resume-template.md
- command-maintain-template.md
- platform-config-template.md
- improvement-protocol-template.md
- changelog-template.md
- defect-patterns-template.md

### examples/ (generated package)

Must include at least one example showing the workflow applied to a specific use case.

## Validation

Before a generated package is considered complete:

1. **File existence check** — all files in the structure above exist.
2. **Section completeness check** — all required sections present in each file.
3. **QC pass** — quality-control.md checklist completed, all items pass.
4. **Red-team pass** — red-team-review.md review completed, PASS recommendation.
5. **Final summary** — produced using final-summary-template.md.

## Naming Conventions

- Package folder: `<domain>-workflow` or `<project-name>-workflow` (kebab-case).
- Agent files: `<role-name>.md` (kebab-case, e.g., `content-auditor.md`).
- Skill files: `<capability-name>.md` (kebab-case, e.g., `content-audit.md`).
- Prompt files: `<purpose>.md` (kebab-case, e.g., `master-prompt.md`).

## Adaptability

If the target project has existing agent/skill folder conventions (stated during intake), the generated package follows those conventions instead of the default structure. The conventions used must be documented in the package README.