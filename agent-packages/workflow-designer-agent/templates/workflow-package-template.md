# Workflow Package Template

This template defines the structure for a complete generated workflow package. Fill in all `{{PLACEHOLDERS}}`.

---

# Workflow Package: {{PACKAGE_NAME}}

## Package Structure

```
{{PACKAGE_NAME}}/
  README.md                                    — Package overview, purpose, assumptions, limitations, how-to-run
  AGENTS.md                                    — Operating instructions, agent hierarchy, collaboration model
  CLAUDE.md                                    — Claude Code instructions (imports @AGENTS.md)
  opencode.json                                — Agent registration for OpenCode
  workflow.md                                  — 18-phase workflow with Oracle gates and handoffs
  intake.md                                    — Intake model with assumption risk classification
  research-protocol.md                         — Source hierarchy, citation format, chain-of-custody
  quality-control.md                           — 18 QC dimensions, 15 quantitative criteria, report format
  red-team-review.md                           — FMEA-scored adversarial review process
  requirements.md                              — Formal requirements with IDs and acceptance criteria
  fmea.md                                      — Failure mode and effects analysis with RPN
  traceability-matrix.md                       — Requirement-to-deliverable traceability
  reliability-plan.md                          — Error budget, metrics, idempotency protocol
  source-log.md                                — Source chain-of-custody with retrieval IDs
  improvement-protocol.md                      — Self-improvement rules and safety guardrails
  CHANGELOG.md                                 — Version history (append-only)
  defect-patterns.md                           — Defect log database for improvement signals
  agents/
    {{agent-1}}.md                             — {{one-line role}}
    {{agent-2}}.md                             — {{one-line role}}
    ...
  skills/
    {{skill-1}}.md                             — {{one-line purpose}}
    {{skill-2}}.md                             — {{one-line purpose}}
    ...
  prompts/
    master-prompt.md                           — Main invocation prompt
    {{example-prompt}}.md                      — Example invocation
    ...
  templates/                                   — 18 templates (agent, skill, workflow-package, intake,
                                               qa-checklist, red-team, final-summary, fmea, traceability,
                                               requirements, source-log, command-flowstart, command-resume,
                                               command-maintain, command-update, platform-config,
                                               improvement-protocol, changelog, defect-patterns)
  examples/
    {{example-1}}.md                           — {{one-line description}}
    ...
  tests/
    test_regression.py                         — Regression test suite
    test_idempotency.py                        — Idempotency verification
    golden/                                    — Golden output fixtures
  commands/
    flowstart.md, resume.md, maintain.md, update.md
  .opencode/commands/                          — Platform-specific command files
  .claude/commands/
  .codex/commands/
  .github/commands/
  *.devin.md                                   — Devin playbooks
```

## Required Content Checklist

### Top-Level Files

- [ ] **README.md** — includes: workflow purpose, when to use, inputs, outputs, how to run, file structure, assumptions, limitations, see also.
- [ ] **AGENTS.md** — includes: purpose, agent hierarchy, collaboration model, research behaviour, QC rules, red-team rules, final packaging requirements.
- [ ] **workflow.md** — includes: all phases with purpose, inputs, outputs, responsible agent, validation criteria. Revision loop defined.
- [ ] **intake.md** — includes: intake fields, assumption labelling format, when to ask vs assume.
- [ ] **research-protocol.md** — includes: when research is required, source hierarchy, citation format, conflict handling, tagging rules, time-sensitive claims.
- [ ] **quality-control.md** — includes: 18 QC dimensions, quantitative criteria, checklist, report format, failure handling.
- [ ] **red-team-review.md** — includes: 6 perspectives, 10 challenge areas, report format, pass/fail criteria, domain-specific attack vectors.

### agents/

- [ ] Every agent file has all 10 sections (role, mission, responsibilities, required inputs, expected outputs, operating rules, decision criteria, escalation rules, quality checklist, failure modes to avoid).
- [ ] Agent roles are distinct (no overlap).
- [ ] Agent names are kebab-case and domain-appropriate.

### skills/

- [ ] Every skill file has all 8 sections (purpose, when to use, required inputs, process, output format, validation criteria, common mistakes, example usage).
- [ ] Every skill is reusable (not hardcoded to one project).
- [ ] No skill duplicates another.
- [ ] Skill names are kebab-case.

### prompts/

- [ ] Master prompt exists and is ready to paste into an agent session.
- [ ] At least one example prompt exists.

### templates/

- [ ] All 18 templates present (agent, skill, workflow-package, intake, qa-checklist, red-team, final-summary, fmea, traceability-matrix, requirements, source-log, command-flowstart, command-resume, command-maintain, platform-config, improvement-protocol, changelog, defect-patterns).
- [ ] Templates have `{{PLACEHOLDERS}}` and fill instructions.

### examples/

- [ ] At least one example showing the workflow applied to a specific use case.

## Assumptions Section (for README)

```
## Assumptions

- [ASSUMPTION] {{field}}: {{assumed value}}
  Reasoning: {{why}}
  Confidence: high/medium/low

- [ASSUMPTION] {{field}}: {{assumed value}}
  Reasoning: {{why}}
  Confidence: high/medium/low
```

## Limitations Section (for README)

```
## Limitations

- {{limitation 1}}
- {{limitation 2}}
- {{limitation 3}}
```

## Validation

Before the package is considered final:

1. All checklist items above pass.
2. QC checklist (quality-control.md) completed — all items pass.
3. Red-team review (red-team-review.md) completed — PASS recommendation.
4. Final summary produced (final-summary-template.md).