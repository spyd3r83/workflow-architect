---
name: agent-design
description: Creates specialized agent definitions for a specific workflow. Produces agent files that follow the agent-file-template and contain all 10 required sections. Use when: - Phase 7 (Agent Design) of the Workflow Designer Agent workflow.
- When the skill-architect needs to create agent definitions for the workstreams identified by the workflow-architect.
---

# Skill: Agent Design

## Purpose

Creates specialized agent definitions for a specific workflow. Produces agent files that follow the agent-file-template and contain all 10 required sections.

## When To Use

- Phase 7 (Agent Design) of the Workflow Designer Agent workflow.
- When the skill-architect needs to create agent definitions for the workstreams identified by the workflow-architect.

## Required Inputs

- **Workstream list** — from the workflow-architect (Phase 6).
- **Research summary** — domain-specific practices to inform agent specialization.
- **`templates/agent-file-template.md`** — the structure to follow.
- **Domain classification** — to inform agent names and roles.

## Process

1. **Map workstreams to agents.** For each workstream (or cluster of related workstreams), identify the agent that will own it. One agent per workstream unless workstreams are closely related.
2. **For each agent, define:**
   - **Role** — one phrase describing what this agent does (e.g., "Audits existing website content").
   - **Mission** — one sentence describing what this agent must accomplish.
   - **Responsibilities** — 5-10 concrete actions the agent performs.
   - **Required Inputs** — what the agent needs to do its job.
   - **Expected Outputs** — what the agent produces (concrete deliverables).
   - **Operating Rules** — constraints and rules the agent must follow.
   - **Decision Criteria** — when the agent does X vs Y (table format).
   - **Escalation Rules** — when to escalate to the orchestrator.
   - **Quality Checklist** — what must be true before the agent's output is accepted.
   - **Failure Modes to Avoid** — common mistakes this agent must not make.
3. **Ensure distinct roles.** No two agents should have overlapping responsibilities. If they do, merge or redefine.
4. **Ensure domain-appropriate specialization.** Agent names and roles should reflect the domain (e.g., `content-auditor` for web, `threat-modeler` for security, `compliance-auditor` for legal).
5. **Define handoffs.** For each agent, specify what it passes to the next agent and in what format.
6. **Write agent files** following `templates/agent-file-template.md`.

## Output Format

One markdown file per agent, following `templates/agent-file-template.md`. Each file has all 10 sections. See the template for the exact structure.

Additionally, produce an agent summary:

```
# Agent Summary

## Agents Created
1. <name> — <role> — owns workstream(s): <list>
2. <name> — <role> — owns workstream(s): <list>
...

## Handoff Map
<agent A> → <deliverable> → <agent B>
<agent B> → <deliverable> → <agent C>
...

## Distinct Role Check
- <agent A> and <agent B>: distinct (A does X, B does Y)
...
```

## Validation Criteria

- [ ] Every workstream has at least one responsible agent.
- [ ] Every agent file has all 10 required sections.
- [ ] No agent description is vague ("helps with" is not a role).
- [ ] Agent roles do not overlap (each has a distinct purpose).
- [ ] Every agent has decision criteria (when X vs Y).
- [ ] Every agent has escalation rules.
- [ ] Every agent has a quality checklist.
- [ ] Handoffs between agents are explicit.
- [ ] Agent names are kebab-case and domain-appropriate.

## Common Mistakes

- **Vague roles**: "helps with the project" — helps with what? Be specific.
- **Overlapping responsibilities**: two agents doing the same thing. Merge or redefine.
- **Missing sections**: skipping decision criteria or escalation rules. All 10 sections are required.
- **Generic agents**: an agent named "doer" or "worker". Name agents by their domain role.
- **No handoffs**: agents defined in isolation without specifying what they pass to the next agent.
- **Too many agents**: one agent per tiny task. Cluster related tasks into one agent.
- **Too few agents**: one agent does everything. Split by workstream.

## Example Usage

**Input:**
```
Workstreams: content-audit, ia-mapping, visual-design, seo-analysis, accessibility-audit, frontend-implementation, qa-and-launch
Domain: web
```

**Output (agent summary excerpt):**
```
# Agent Summary

## Agents Created
1. content-auditor — Audits existing website content — owns: content-audit
2. ia-architect — Defines information architecture and navigation — owns: ia-mapping
3. visual-designer — Creates visual design system and mockups — owns: visual-design
4. seo-specialist — Defines SEO requirements — owns: seo-analysis
5. accessibility-auditor — Defines and verifies accessibility requirements — owns: accessibility-audit
6. frontend-engineer — Implements the new frontend — owns: frontend-implementation
7. qa-tester — Tests implementation against all requirements — owns: qa-and-launch

## Handoff Map
content-auditor → content audit report → ia-architect, seo-specialist
ia-architect → sitemap + nav structure → visual-designer
visual-designer → design system + mockups → frontend-engineer
seo-specialist → SEO requirements → frontend-engineer
accessibility-auditor → accessibility checklist → frontend-engineer, qa-tester
frontend-engineer → implemented frontend → qa-tester
qa-tester → QA report → (launch)
```

Each agent file is then written following the template with all 10 sections.