---
name: skill-design
description: |
  Creates reusable skill definitions for a specific workflow. Produces skill files that follow the skill-file-template and contain all 8 required sections. Use when: - Phase 8 (Skill Design) of the Workflow Designer Agent workflow.
  - When the skill-architect needs to create reusable skills that agents will invoke.
---

# Skill: Skill Design

## Purpose

Creates reusable skill definitions for a specific workflow. Produces skill files that follow the skill-file-template and contain all 8 required sections.

## When To Use

- Phase 8 (Skill Design) of the Workflow Designer Agent workflow.
- When the skill-architect needs to create reusable skills that agents will invoke.

## Required Inputs

- **Agent definitions** — from Phase 7 (to know what capabilities agents need).
- **Research summary** — domain-specific practices to inform skill processes.
- **`templates/skill-file-template.md`** — the structure to follow.
- **Workstream list** — to understand what skills are needed per workstream.

## Process

1. **Identify reusable capabilities.** For each agent responsibility, ask: "Is this a reusable capability that multiple agents might need, or that could be reused in similar projects?" If yes, create a skill. If it is specific to one agent and one project, inline it into the agent.
2. **For each skill, define:**
   - **Purpose** — one sentence: what this skill does.
   - **When To Use** — specific triggers and phases where this skill applies.
   - **Required Inputs** — what the skill needs to execute.
   - **Process** — step-by-step procedure (numbered list, not narrative).
   - **Output Format** — the structure of the skill's output.
   - **Validation Criteria** — checklist for when the skill's output is valid.
   - **Common Mistakes** — what to avoid when using this skill.
   - **Example Usage** — concrete example with inputs and expected outputs.
3. **Ensure reusability.** Skills must not be hardcoded to one project. Use parameters and domain-adaptive language.
4. **Ensure no duplication.** No two skills should serve the same purpose. If they do, merge them.
5. **Map skills to agents.** Document which agent uses which skill.
6. **Write skill files** following `templates/skill-file-template.md`.

## Output Format

One markdown file per skill, following `templates/skill-file-template.md`. Each file has all 8 sections.

Additionally, produce a skill summary:

```
# Skill Summary

## Skills Created
1. <name> — <purpose> — used by: <agent list>
2. <name> — <purpose> — used by: <agent list>
...

## Skill-to-Agent Mapping
- <agent A>: uses <skill 1>, <skill 2>
- <agent B>: uses <skill 2>, <skill 3>
...

## Duplication Check
- <skill 1> and <skill 2>: distinct (1 does X, 2 does Y)
...
```

## Validation Criteria

- [ ] Every reusable capability has a corresponding skill.
- [ ] Every skill file has all 8 required sections.
- [ ] Every skill is reusable (not hardcoded to one project).
- [ ] No skill duplicates another skill's purpose.
- [ ] Every skill has a concrete example usage with inputs and expected outputs.
- [ ] Every skill's process is step-by-step (not narrative).
- [ ] Skill-to-agent mapping is complete.
- [ ] Skill names are kebab-case.

## Common Mistakes

- **Hardcoded skills**: a skill that only works for one specific project. Make it domain-adaptive.
- **Missing example usage**: a skill without an example is hard for another agent to use.
- **Narrative process**: writing a paragraph instead of numbered steps.
- **Duplicate skills**: two skills that do the same thing. Merge them.
- **Too many skills**: creating a skill for every tiny capability. Only create skills for reusable capabilities.
- **Too few skills**: inlining everything into agents, making agents bloated and non-reusable.
- **Vague purpose**: "helps with research" — helps with what? Be specific.

## Example Usage

**Input:**
```
Agents: content-auditor, seo-specialist, accessibility-auditor, qa-tester
Domain: web
```

**Output (skill summary excerpt):**
```
# Skill Summary

## Skills Created
1. content-audit — Inventories and assesses existing content — used by: content-auditor
2. seo-analysis — Defines SEO requirements based on keywords and best practices — used by: seo-specialist
3. accessibility-validation — Tests implementation against WCAG 2.1 AA — used by: accessibility-auditor, qa-tester
4. regression-testing — Tests implementation against all requirements — used by: qa-tester

## Skill-to-Agent Mapping
- content-auditor: uses content-audit
- seo-specialist: uses seo-analysis
- accessibility-auditor: uses accessibility-validation
- qa-tester: uses accessibility-validation, regression-testing
```

Each skill file is then written following the template with all 8 sections, including a concrete example usage.