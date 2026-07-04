# Final Summary Template

This template defines the structure for the final package summary. Fill in all `{{PLACEHOLDERS}}`.

---

# Final Summary: {{PACKAGE_NAME}}

## Package Name

{{PACKAGE_NAME}}

## Objective

{{OBJECTIVE — the refined objective statement}}

## Domain

{{DOMAIN — domain label and sub-domain}}

## Agents Created

| # | Agent | Role |
|---|-------|------|
| 1 | {{agent name}} | {{one-line role}} |
| 2 | {{agent name}} | {{one-line role}} |
| ... | ... | ... |

## Skills Created

| # | Skill | Purpose | Used By |
|---|-------|---------|---------|
| 1 | {{skill name}} | {{one-line purpose}} | {{agent list}} |
| 2 | {{skill name}} | {{one-line purpose}} | {{agent list}} |
| ... | ... | ... | ... |

## Workflow Phases

| # | Phase | Responsible Agent | Gate |
|---|-------|-------------------|------|
| 1 | {{phase name}} | {{agent}} | {{gate description}} |
| 2 | {{phase name}} | {{agent}} | {{gate description}} |
| ... | ... | ... | ... |

## File Structure

```
{{PACKAGE_NAME}}/
  README.md, AGENTS.md, CLAUDE.md, opencode.json
  workflow.md, intake.md, research-protocol.md, quality-control.md, red-team-review.md
  requirements.md, fmea.md, traceability-matrix.md, reliability-plan.md, source-log.md
  improvement-protocol.md, CHANGELOG.md, defect-patterns.md
  agents/ ({{N}} agent files)
  skills/ ({{N}} skill files)
  prompts/ ({{N}} prompt files)
  templates/ (18 template files)
  examples/ ({{N}} example files)
  tests/ (regression + idempotency)
  commands/ (flowstart, resume, maintain, update)
  .opencode/commands/, .claude/commands/, .codex/commands/, .github/commands/
  *.devin.md (Devin playbooks)
```

**Total files**: {{N}}

## Assumptions

All labelled assumptions from intake and research:

- [ASSUMPTION] {{field}}: {{value}} — Confidence: {{high/medium/low}}
- [ASSUMPTION] {{field}}: {{value}} — Confidence: {{high/medium/low}}
- ...

## Limitations

Known limitations and risk controls:

- {{limitation 1}}
- {{limitation 2}}
- ...

## Validation Status

- **QC**: {{PASS}} (all {{N}} items passed)
- **Red-Team**: {{PASS}} (with {{N}} optional issues documented) / {{FAIL}} (mandatory issues resolved in revision)

## Usage Instructions

1. {{step 1 — e.g., "Open prompts/master-prompt.md"}}
2. {{step 2 — e.g., "Fill in {{PROJECT_OBJECTIVE}} with your project goal"}}
3. {{step 3 — e.g., "Paste into an agent session"}}
4. {{step 4 — e.g., "Review the generated output"}}
5. {{step 5 — e.g., "Promote to permanent location if satisfied"}}

## Optional Issues (from red-team)

{{If red-team passed with optional issues, list them here. If none, write "None".}}

- {{optional issue 1 (or "None")}}
- {{optional issue 2}}

## Research Sources

Key sources used in the research summary:

- {{source 1 — title, org, date, URL}}
- {{source 2 — title, org, date, URL}}
- ...

---

## Fill Instructions

1. **Package name**: kebab-case, matches the folder name.
2. **Objective**: the refined objective from intake.
3. **Agents/Skills**: list all with one-line descriptions.
4. **Workflow phases**: list all with responsible agent and gate.
5. **File structure**: show the actual file tree with file count.
6. **Assumptions**: list ALL labelled assumptions from intake and research.
7. **Limitations**: list all known limitations. Be honest.
8. **Validation status**: record QC and red-team results.
9. **Usage instructions**: step-by-step, actionable.
10. **Optional issues**: from red-team, if any.
11. **Research sources**: key sources cited in the research summary.

## Validation Criteria (when this template is properly filled)

- [ ] All sections populated.
- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] All agents and skills listed.
- [ ] All workflow phases listed.
- [ ] All assumptions documented.
- [ ] Limitations are honest and specific.
- [ ] Usage instructions are actionable.
- [ ] Research sources cited.