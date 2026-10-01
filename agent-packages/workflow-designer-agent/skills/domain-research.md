# Skill: Domain Research

## Purpose

Identifies what research is needed for a given domain and how to gather it following the research protocol. Produces a structured research plan and executes it to produce a cited research summary.

## When To Use

- Phase 5 (External Research) of the Workflow Designer Agent workflow.
- Any time domain-specific or current information is needed to design an accurate workflow.
- When the domain-researcher agent needs to determine what to research and how.

## Required Inputs

- **Domain classification** — the domain label and sub-domain.
- **Objective** — the project objective (determines what research is relevant).
- **Source inventory** — user-provided source materials (if any).
- **`research-protocol.md`** — source hierarchy, citation format, tagging rules.

## Process

1. **Identify research topics.** Based on the domain and objective, list the specific topics that need research. Ask: "What domain-specific facts, standards, or best practices does the workflow design depend on?"
2. **For each topic, determine:**
   - Is research required? (If the topic is about internal project state, no. If it is about external facts, standards, or best practices, yes.)
   - What is the source hierarchy for this topic? (e.g., for web accessibility: W3C > vendor docs > practitioner guides.)
   - Is the information time-sensitive? (If yes, research date must be recorded.)
3. **Gather information.** For each topic:
   - Search authoritative sources following the hierarchy.
   - Record findings with citations: `[Source: <title>, <author/org>, <date>, <URL>]`.
   - Tag each claim `[VERIFIED]` or `[ASSUMPTION]`.
   - If no source is found, state "no authoritative source found" and label as assumption.
4. **Handle conflicts.** If sources disagree, document the conflict, apply the source hierarchy, and label the resolution.
5. **Flag time-sensitive claims.** Add `[TIME-SENSITIVE]` tag and research date.
6. **Produce the research summary.** Structured document with: domain, research date, key findings (tagged), conflicts, time-sensitive claims, gaps, recommendations for downstream agents.

## Output Format

```
# Research Summary: <domain>

## Domain
<domain label and sub-domain>

## Research Date
<YYYY-MM-DD>

## Research Topics
1. <topic 1>
2. <topic 2>
...

## Key Findings

### Finding 1: <title>
[VERIFIED] <claim>
[Source: <citation>]

### Finding 2: <title>
[ASSUMPTION] <claim>
Reasoning: <why>
Confidence: high/medium/low

## Conflicts
<conflicts and resolutions, or "none">

## Time-Sensitive Claims
<claims with research dates, or "none">

## Gaps
<topics where no authoritative source was found, or "none">

## Recommendations for Downstream Agents
<what the workflow-architect, skill-architect, and implementation-planner should know>
```

## Validation Criteria

- [ ] Research topics identified and justified.
- [ ] Every factual claim tagged `[VERIFIED]` or `[ASSUMPTION]`.
- [ ] All `[VERIFIED]` claims have citations in correct format.
- [ ] No fabricated sources, URLs, quotes, dates, or versions.
- [ ] Conflicts documented with resolutions.
- [ ] Time-sensitive claims flagged with research dates.
- [ ] Gaps documented.
- [ ] Research summary is structured (not narrative).
- [ ] Recommendations for downstream agents included.

## Common Mistakes

- **Skipping research**: "I already know this" — if it is a domain-specific fact, it must be sourced.
- **Fabricating sources**: inventing URLs or citations to fill gaps. State the gap instead.
- **Narrative summary**: writing a paragraph instead of structured findings.
- **Missing tags**: untagged claims fail QC.
- **Wrong source hierarchy**: citing a blog over an official standard. Apply the hierarchy.
- **No research date**: omitting the date for time-sensitive claims.
- **No gaps section**: hiding topics where no source was found. Document them.

## Example Usage

**Input:**
```
Domain: web (sub-domain: accessibility)
Objective: Revamp a marketing website with improved accessibility.
Source inventory: none provided.
```

**Output (excerpt):**
```
# Research Summary: web (accessibility)

## Research Date
2025-01-15

## Research Topics
1. Current WCAG standard and conformance level for marketing websites
2. Legal accessibility requirements (ADA, Section 508)
3. Accessibility testing tools and methods

## Key Findings

### Finding 1: WCAG 2.1 Level AA is the current standard
[VERIFIED] WCAG 2.1 Level AA is the recommended conformance level for web content.
[Source: Web Content Accessibility Guidelines (WCAG) 2.1, W3C, 2018, https://www.w3.org/TR/WCAG21/]

### Finding 2: ADA applies to websites
[VERIFIED] The ADA requires public accommodations to provide accessible websites.
[Source: Accessibility of Web Information and Services, DOJ, 2024, https://www.ada.gov/resources/web-guidance/]
[TIME-SENSITIVE] Researched: 2025-01-15. Legal interpretations may evolve.

### Finding 3: Automated testing covers ~30-40% of WCAG criteria
[ASSUMPTION] Automated testing tools catch approximately 30-40% of WCAG 2.1 AA criteria; manual testing is required for the rest.
Reasoning: Common practitioner knowledge, but exact percentage varies by tool and interpretation.
Confidence: medium

## Gaps
- Specific case law for the user's jurisdiction not researched (user did not specify jurisdiction).

## Recommendations for Downstream Agents
- Workflow must include both automated and manual accessibility testing phases.
- Accessibility requirements should target WCAG 2.1 Level AA at minimum.
- Legal review recommended if the user's jurisdiction has specific accessibility laws.
```