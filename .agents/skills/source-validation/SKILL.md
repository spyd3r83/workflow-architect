---
name: source-validation
description: Evaluates whether sources are authoritative, current, and reliable. Used to validate research findings before they are incorporated into the workflow design. Use when: - During Phase 5 (External Research) after gathering sources.
- Any time a claim's source needs to be verified for authority and freshness.
- When the domain-researcher encounters conflicting sources and needs to determine which is more authoritative.
---

# Skill: Source Validation

## Purpose

Evaluates whether sources are authoritative, current, and reliable. Used to validate research findings before they are incorporated into the workflow design.

## When To Use

- During Phase 5 (External Research) after gathering sources.
- Any time a claim's source needs to be verified for authority and freshness.
- When the domain-researcher encounters conflicting sources and needs to determine which is more authoritative.

## Required Inputs

- **Source to validate** — title, author/organization, date, URL or reference.
- **Domain** — the domain the source relates to (determines what "current" means).
- **Claim being sourced** — what the source is being used to support.

## Process

1. **Identify the source type.** Is it an official standards body, peer-reviewed publication, vendor documentation, practitioner reference, secondary source, or community source?
2. **Check authority:**
   - Is the source the originator of the standard, tool, or regulation?
   - Is it maintained by the responsible organization?
   - Is the author identifiable and credible?
   - Is it cited by other authoritative sources?
3. **Check currency:**
   - What is the publication or last-updated date?
   - Is it recent enough for the domain? (For security: months. For standards: years may be acceptable if the standard has not been superseded.)
   - Has the subject matter changed since publication? (e.g., a 2020 article about a tool that had a major rewrite in 2023 is stale.)
4. **Check relevance:**
   - Does the source actually support the claim being made?
   - Is the claim taken in context (not cherry-picked)?
5. **Assign a reliability rating:**
   - **High**: official source, current, directly supports the claim.
   - **Medium**: reputable source, reasonably current, supports the claim with some interpretation.
   - **Low**: community source, outdated, or only tangentially supports the claim.
   - **Unreliable**: anonymous, outdated for a fast-changing domain, or does not support the claim.
6. **Produce a validation report.**

## Output Format

```
# Source Validation Report

## Source
- Title: <title>
- Author/Org: <author>
- Date: <date>
- URL/Ref: <url>
- Type: <standards body / peer-reviewed / vendor docs / practitioner / secondary / community>

## Validation

### Authority
- Is originator: yes/no
- Maintained by responsible org: yes/no
- Author identifiable: yes/no
- Cross-referenced by other authoritative sources: yes/no

### Currency
- Publication date: <date>
- Domain freshness requirement: <months/years>
- Is current: yes/no
- Subject changed since publication: yes/no/unknown

### Relevance
- Supports the claim: yes/partially/no
- Taken in context: yes/no

## Reliability Rating
High / Medium / Low / Unreliable

## Recommendation
Use as primary source / Use with caveat / Cross-reference needed / Do not use
```

## Validation Criteria

- [ ] Source type identified.
- [ ] Authority checked (all 4 sub-criteria).
- [ ] Currency checked (date, freshness requirement, current status).
- [ ] Relevance checked (supports claim, in context).
- [ ] Reliability rating assigned.
- [ ] Recommendation provided.

## Common Mistakes

- **Accepting vendor blogs as authoritative**: a vendor blog is rank 3-5, not rank 1. Cite the official docs instead.
- **Ignoring publication date**: a 2018 article about a 2024 tool is stale.
- **Cherry-picking**: taking a quote out of context to support a claim it does not actually support.
- **Not cross-referencing community sources**: a Stack Overflow answer should be cross-referenced with official docs.
- **Overrating familiarity**: a well-known blog is still a blog, not an authoritative source.

## Example Usage

**Input:**
```
Source: "React Server Components Explained", Meta React Blog, 2023-03, https://react.dev/blog/2023/03/22/react-labs
Domain: web (frontend)
Claim: React Server Components are a stable feature.
```

**Output:**
```
# Source Validation Report

## Source
- Title: React Server Components Explained
- Author/Org: Meta React Blog
- Date: 2023-03
- URL: https://react.dev/blog/2023/03/22/react-labs
- Type: vendor documentation (rank 3)

## Validation

### Authority
- Is originator: yes (Meta maintains React)
- Maintained by responsible org: yes
- Author identifiable: yes (React Labs team)
- Cross-referenced: yes (cited by React docs)

### Currency
- Publication date: 2023-03
- Domain freshness requirement: months (React evolves rapidly)
- Is current: needs re-verification (research date: 2025-01)
- Subject changed since publication: possibly (React 19 released)

### Relevance
- Supports the claim: partially (the blog discusses RSC but stability status may have changed)
- Taken in context: yes

## Reliability Rating
Medium (authoritative source but potentially outdated for a fast-changing domain)

## Recommendation
Cross-reference with current React official docs to verify stability status as of research date.
```