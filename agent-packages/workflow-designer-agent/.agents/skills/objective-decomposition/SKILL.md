---
name: objective-decomposition
description: |
  Breaks a high-level project goal into actionable workstreams that can be assigned to agents and sequenced into a workflow. Use when: - Phase 6 (Workflow Decomposition) of the Workflow Designer Agent workflow.
  - Any time a project objective needs to be broken into manageable pieces before agent design.
  - When the workflow-architect needs to determine what agents and phases are required.
---

# Skill: Objective Decomposition

## Purpose

Breaks a high-level project goal into actionable workstreams that can be assigned to agents and sequenced into a workflow.

## When To Use

- Phase 6 (Workflow Decomposition) of the Workflow Designer Agent workflow.
- Any time a project objective needs to be broken into manageable pieces before agent design.
- When the workflow-architect needs to determine what agents and phases are required.

## Required Inputs

- **Project objective** — the refined 1-2 sentence objective from intake.
- **Domain classification** — the domain label and sub-domain.
- **Research summary** — domain-specific findings that inform what workstreams are needed.
- **Scope boundaries** — what is in scope and out of scope.

## Process

1. **Read the objective and scope.** Identify what the workflow must produce (the deliverable).
2. **Identify the major workstreams.** A workstream is a cluster of work that produces a distinct sub-deliverable. Ask: "What are the 3-10 major chunks of work needed to produce the final deliverable?"
3. **For each workstream, define:**
   - Name (kebab-case, action-oriented, e.g., "content-audit", "visual-design").
   - Purpose (one sentence: what this workstream produces).
   - Dependencies (which other workstreams must complete first).
   - Expected deliverable (concrete output, e.g., "audited content inventory", "design system spec").
4. **Order workstreams by dependencies.** If A depends on B, B comes first. If A and B are independent, note they can run in parallel.
5. **Verify coverage.** Does every part of the objective map to at least one workstream? If not, add the missing workstream. If a workstream does not serve the objective, remove it.
6. **Check for granularity.** If a workstream is too vague ("handle design"), split it. If it is too narrow ("pick a font"), merge it into a broader workstream.
7. **Produce the workstream list.** Structured output with all fields above.

## Output Format

```
# Workstream Decomposition: <objective>

## Objective
<the refined objective>

## Workstreams

### Workstream 1: <name>
- Purpose: <one sentence>
- Dependencies: <none / list of workstream names>
- Deliverable: <concrete output>
- Parallelizable with: <none / list of workstream names>

### Workstream 2: <name>
...

## Coverage Check
- Objective part 1: covered by workstream(s) <list>
- Objective part 2: covered by workstream(s) <list>
...

## Ordering
1. <workstream> (no dependencies)
2. <workstream> (depends on 1)
3. <workstream> and <workstream> (parallel, depend on 2)
...
```

## Validation Criteria

- [ ] Every workstream has a concrete deliverable (not "manage" or "handle").
- [ ] Workstream dependencies are explicit.
- [ ] Every part of the objective is covered by at least one workstream.
- [ ] No workstream is orphaned (does not serve the objective).
- [ ] Workstreams are ordered by dependencies.
- [ ] Parallelizable workstreams are identified.
- [ ] Granularity is appropriate (not too vague, not too narrow).

## Common Mistakes

- **Vague workstreams**: "handle the design phase" — handle what? Split into specific workstreams.
- **Missing dependencies**: workstream B depends on A's output but A is listed after B.
- **Over-decomposition**: 20 workstreams for a simple objective. Merge related ones.
- **Under-decomposition**: 2 workstreams for a complex objective. Split into specific sub-deliverables.
- **Orphaned workstreams**: a workstream that does not serve the objective. Remove it.
- **No coverage check**: not verifying that every part of the objective is addressed.

## Example Usage

**Input:**
```
Objective: Design a workflow to revamp a marketing website with improved SEO and accessibility.
Domain: web
Scope: in scope — content, design, frontend, SEO, accessibility. Out of scope — backend, database, e-commerce.
```

**Output:**
```
# Workstream Decomposition: Revamp marketing website with improved SEO and accessibility

## Workstreams

### Workstream 1: content-audit
- Purpose: Inventory and assess existing website content for quality, accuracy, and relevance.
- Dependencies: none
- Deliverable: Content audit report with keep/revise/remove recommendations per page.

### Workstream 2: ia-mapping
- Purpose: Define the new information architecture and page structure.
- Dependencies: content-audit
- Deliverable: Sitemap and navigation structure document.

### Workstream 3: visual-design
- Purpose: Create the visual design system and page mockups.
- Dependencies: ia-mapping
- Deliverable: Design system spec (colors, typography, components) + page mockups.

### Workstream 4: seo-analysis
- Purpose: Define SEO requirements including keywords, meta structure, and performance targets.
- Dependencies: content-audit
- Deliverable: SEO requirements document.
- Parallelizable with: visual-design

### Workstream 5: accessibility-audit
- Purpose: Define accessibility requirements against WCAG 2.1 AA.
- Dependencies: none
- Deliverable: Accessibility requirements checklist.
- Parallelizable with: content-audit, ia-mapping

### Workstream 6: frontend-implementation
- Purpose: Implement the new frontend based on design, SEO, and accessibility requirements.
- Dependencies: visual-design, seo-analysis, accessibility-audit
- Deliverable: Implemented frontend code.

### Workstream 7: qa-and-launch
- Purpose: Test the implementation against all requirements and launch.
- Dependencies: frontend-implementation
- Deliverable: QA report + launched website.

## Coverage Check
- Content revamp: covered by content-audit
- SEO improvement: covered by seo-analysis
- Accessibility improvement: covered by accessibility-audit
- Visual design: covered by visual-design
- Implementation: covered by frontend-implementation
- Launch: covered by qa-and-launch
```