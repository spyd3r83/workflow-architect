---
name: file-structure-design
description: |
  Creates a repo-ready folder and file structure for a generated workflow package. Maps the workflow design, agents, skills, and templates to a concrete file tree. Use when: - Phase 9 (Folder/File Structure Generation) of the Workflow Designer Agent workflow.
  - When the implementation-planner needs to produce the file tree before writing files.
---

# Skill: File Structure Design

## Purpose

Creates a repo-ready folder and file structure for a generated workflow package. Maps the workflow design, agents, skills, and templates to a concrete file tree.

## When To Use

- Phase 9 (Folder/File Structure Generation) of the Workflow Designer Agent workflow.
- When the implementation-planner needs to produce the file tree before writing files.

## Required Inputs

- **Workflow design** — phases, agents, skills.
- **Agent definitions** — list of agent files to create.
- **Skill definitions** — list of skill files to create.
- **`package-output-spec.md`** — required structure.
- **Project conventions** — if stated during intake, the folder structure follows them.

## Process

1. **Start with the output spec.** The base structure from `package-output-spec.md` is:
   ```
   <package-name>/
     README.md
     AGENTS.md
     workflow.md
     intake.md
     research-protocol.md
      quality-control.md
      red-team-review.md
      agents/
      skills/
      prompts/
      templates/
      examples/
      commands/
      .opencode/commands/
      .claude/commands/
      .codex/commands/
      .github/commands/
    ```
2. **Add agent files.** For each agent in the design, add a file under `agents/` (kebab-case, e.g., `content-auditor.md`).
3. **Add skill files.** For each skill in the design, add a file under `skills/` (kebab-case, e.g., `content-audit.md`).
4. **Add prompt files.** At minimum: a master prompt and one example prompt. Add domain-specific example prompts as needed.
5. **Add template files.** All required templates (agent, skill, workflow-package, intake, qa-checklist, red-team, final-summary, fmea, traceability-matrix, requirements, source-log, command-flowstart, command-resume, command-maintain, platform-config).
6. **Add example files.** At least one example showing the workflow applied to a specific use case.
7. **Add slash commands.** Create 3 command files (flowstart, resume, maintain) for each platform: `.opencode/commands/`, `.claude/commands/`, `.codex/commands/`, `.github/commands/`, and 3 Devin playbooks (`*.devin.md`). Use the command templates as starting points. Fill in `{{COMMAND_NAME}}`, `{{PRIMARY_AGENT_NAME}}`, `{{WORKFLOW_NAME}}`.
8. **Add platform config.** Create `opencode.json` registering the primary agent. Create `CLAUDE.md` importing `@AGENTS.md`.
9. **Add domain-specific files if needed.** Some domains may require additional files. Add them and document in the README.
10. **Apply project conventions.** If the project uses a different folder structure (stated during intake), adapt. Document the conventions used.
9. **Produce the file tree.** Complete structure with one-line descriptions per file.

## Output Format

```
# File Structure: <package-name>

## File Tree

<package-name>/
  README.md                                    — Package overview, purpose, assumptions, limitations, how-to-run
  AGENTS.md                                    — Operating instructions, agent hierarchy, collaboration model
  workflow.md                                  — Phased workflow with gates and handoffs
  intake.md                                    — Intake model with assumption labelling
  research-protocol.md                         — Source hierarchy, citation format, tagging rules
  quality-control.md                           — QC dimensions, checklist, report format
  red-team-review.md                           — Adversarial review process, perspectives, report format
  agents/
    <agent-1>.md                               — <one-line role description>
    <agent-2>.md                               — <one-line role description>
    ...
  skills/
    <skill-1>.md                               — <one-line purpose description>
    <skill-2>.md                               — <one-line purpose description>
    ...
  prompts/
    master-prompt.md                           — Main invocation prompt
    <example-prompt>.md                        — Example invocation for a specific use case
    ...
  templates/
    agent-file-template.md                     — Reusable agent definition structure
    skill-file-template.md                     — Reusable skill definition structure
    workflow-package-template.md               — Reusable package structure
    intake-template.md                         — Reusable intake form
    qa-checklist-template.md                   — Reusable QC checklist
    red-team-template.md                       — Reusable red-team review form
    final-summary-template.md                  — Reusable final summary structure
  examples/
    <example-1>.md                             — <one-line example description>
    ...

## Conventions Used
<default structure / project-specific conventions>

## Domain-Specific Additions
<any files added beyond the standard spec, with justification>
```

## Validation Criteria

- [ ] File tree matches `package-output-spec.md` base structure.
- [ ] Every agent in the design has a file under `agents/`.
- [ ] Every skill in the design has a file under `skills/`.
- [ ] All 18 template files present.
- [ ] At least one example file present.
- [ ] Every file has a one-line description.
- [ ] No file is orphaned (every file is referenced by an agent, the workflow, or the README).
- [ ] Project conventions applied if stated during intake.
- [ ] Domain-specific additions documented.

## Common Mistakes

- **Missing files from the spec**: forgetting a template or a top-level doc. Cross-check against the spec.
- **Orphaned files**: a file that no agent or workflow references. Either reference it or remove it.
- **No descriptions**: listing files without one-line descriptions. The file tree must be self-documenting.
- **Wrong naming**: using spaces or PascalCase in filenames. Use kebab-case.
- **Ignoring project conventions**: using the default structure when the project has its own conventions.
- **Inventing files without justification**: adding files not in the spec without documenting why.

## Example Usage

**Input:**
```
Package name: website-revamp-workflow
Agents: content-auditor, ia-architect, visual-designer, seo-specialist, accessibility-auditor, frontend-engineer, qa-tester
Skills: content-audit, ia-mapping, visual-system-design, seo-analysis, accessibility-validation, regression-testing
Domain: web
Project conventions: none stated
```

**Output:**
```
# File Structure: website-revamp-workflow

website-revamp-workflow/
  README.md
  AGENTS.md
  workflow.md
  intake.md
  research-protocol.md
  quality-control.md
  red-team-review.md
  agents/
    content-auditor.md          — Audits existing website content
    ia-architect.md             — Defines information architecture and navigation
    visual-designer.md          — Creates visual design system and mockups
    seo-specialist.md           — Defines SEO requirements
    accessibility-auditor.md    — Defines and verifies accessibility requirements
    frontend-engineer.md        — Implements the new frontend
    qa-tester.md                — Tests implementation against all requirements
  skills/
    content-audit.md            — Inventories and assesses existing content
    ia-mapping.md               — Defines sitemap and navigation structure
    visual-system-design.md     — Creates design system (colors, typography, components)
    seo-analysis.md             — Defines SEO requirements based on keywords and best practices
    accessibility-validation.md — Tests implementation against WCAG 2.1 AA
    regression-testing.md       — Tests implementation against all requirements
  prompts/
    master-prompt.md            — Main invocation prompt
    website-revamp-example.md   — Example invocation for a website revamp
  templates/
    agent-file-template.md
    skill-file-template.md
    workflow-package-template.md
    intake-template.md
    qa-checklist-template.md
    red-team-template.md
    final-summary-template.md
  examples/
    marketing-site-revamp.md    — Example: revamping a marketing website

## Conventions Used
Default structure from package-output-spec.md

## Domain-Specific Additions
None
```