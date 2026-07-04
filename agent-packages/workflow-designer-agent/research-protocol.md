# Research Protocol — Workflow Designer Agent

This protocol governs how the domain-researcher agent gathers, validates, and records information. It applies to all domains: legal, technical, product, security, design, marketing, and business operations.

## When Research Is Required

Research is required when the workflow design depends on any of the following:

- **External facts** — standards, regulations, specifications, market data, scientific findings.
- **Current information** — tool versions, API behaviour, security vulnerabilities, pricing, legal updates.
- **Domain-specific best practices** — established methodologies, frameworks, or conventions.
- **Compliance requirements** — regulatory frameworks, industry standards, legal obligations.

Research is NOT required when:

- The information is purely internal to the project (e.g., the user's existing code structure).
- The workflow design is about process, not facts (e.g., "design a review loop" does not require external research).
- The user explicitly provides all necessary source materials and asks the agent to rely only on those.

## Source Hierarchy

Sources are ranked by authority. Higher-ranked sources override lower-ranked ones when they conflict.

| Rank | Source Type | Examples |
|------|------------|---------|
| 1 | Official standards bodies | W3C, ISO, NIST, IETF, OWASP, ABA, GDPR text |
| 2 | Peer-reviewed publications | Academic journals, conference papers |
| 3 | Official vendor documentation | Tool/platform docs from the maintainer (e.g., React docs from Meta, AWS docs from Amazon) |
| 4 | Established practitioner references | Recognized industry guides, textbooks by known experts |
| 5 | Reputable secondary sources | Major tech publications, established consultancy reports |
| 6 | Community sources | Stack Overflow, GitHub discussions, blog posts (use with caution, always verify) |
| 7 | None | No source found — must be labelled as assumption |

## Identifying Authoritative Sources

A source is authoritative when:

1. **It is the originator** of the standard, tool, or regulation (e.g., W3C for web standards, NIST for security frameworks).
2. **It is maintained** by the organization responsible (e.g., React docs maintained by Meta).
3. **It is current** — the publication or last-updated date is recent enough for the domain. For fast-changing domains, "recent" means months, not years.
4. **It is cited** by other authoritative sources (cross-reference check).

A source is NOT authoritative when:

- It is a blog post summarizing another source without adding verified information.
- It is outdated (e.g., a 2018 article about a tool that has since changed significantly).
- It is anonymous or from an unidentifiable author.
- It conflicts with a higher-ranked source without justification.

## Preserving Citations

Every sourced claim includes a source note in this format:

```
[VERIFIED] <claim> [RET-XXX]
[Source: <title>, <author/org>, <date or version>, <URL or reference>]
```

Every citation must reference a retrieval ID (RET-XXX) from `source-log.md`. The source-log records the fetch timestamp, URL, retrieval status, and content hash for every source retrieved.

### Source Chain-of-Custody

1. **Every source must be logged** in `source-log.md` with a unique retrieval ID (RET-XXX).
2. **Every citation must reference the retrieval ID** — citations without a RET-XXX reference fail QC.
3. **Fetch metadata required**: URL, author/org, date published, date retrieved, retrieval status, content hash (first 16 chars of SHA-256).
4. **Re-verification due date** set per domain schedule in `reliability-plan.md`.
5. **Compliance/regulatory claims require dual-source verification** — a second independent source must confirm the claim. Both sources are logged in source-log.md.

### Dual-Source Verification Rule

For claims about:
- Legal requirements (statutes, regulations, case law)
- Compliance frameworks (GDPR, HIPAA, PCI-DSS, SOC 2)
- Security standards (NIST, ISO 27001, OWASP)
- Safety-critical specifications

A single source is insufficient. Two independent sources from the source hierarchy must confirm the claim. If only one source is found, the claim is labelled `[ASSUMPTION]` with reasoning, not `[VERIFIED]`.
[Source: <title>, <author or organization>, <date or version>, <URL or reference>]
```

Examples:

```
[VERIFIED] WCAG 2.1 Level AA is the current accessibility standard for web content.
[Source: Web Content Accessibility Guidelines (WCAG) 2.1, W3C, 2018, https://www.w3.org/TR/WCAG21/]

[VERIFIED] OAuth 2.0 is the standard framework for authorization.
[Source: The OAuth 2.0 Authorization Framework, IETF RFC 6749, 2012, https://tools.ietf.org/html/rfc6749]
```

Source notes are preserved in:
- The research summary (Phase 5 output).
- Any agent or skill file that references the research.
- The final package's research-protocol.md.

## Handling Conflicting Sources

When sources conflict:

1. **Identify the conflict** — state what the sources disagree on.
2. **Rank by authority** — apply the source hierarchy. The higher-ranked source wins.
3. **If ranks are equal** — present both sources, state the conflict, and label the resolution as a judgement call.
4. **Record the conflict** — include it in the research summary so downstream agents and the user can see it.

Example:

```
[CONFLICT] Source A (vendor blog, 2024) says Feature X is supported. Source B (official docs, 2023) says it is not.
Resolution: Source B is higher authority (official docs vs blog). Treating Feature X as unsupported.
Judgement call: vendor blog may reference a beta feature not yet in official docs. Flagged as time-sensitive.
```

## Separating Verified Facts From Assumptions

Every claim in the research summary is tagged:

- `[VERIFIED]` — the claim is backed by an authoritative source with a citation.
- `[ASSUMPTION]` — the claim is inferred, not sourced. Includes reasoning.
- `[CONFLICT]` — sources disagree. Includes resolution and judgement call note.

No untagged claims are permitted. Untagged claims fail QC.

## Handling Fast-Changing Information

For domains where facts change rapidly (security, APIs, market data, legal updates):

1. **Record the research date** — `Researched: YYYY-MM-DD`.
2. **Flag as time-sensitive** — `[TIME-SENSITIVE]` tag.
3. **Recommend re-verification** — note in the research summary that this claim should be re-verified before the workflow is executed.
4. **Prefer the most recent source** — if multiple sources exist with different dates, prefer the most recent authoritative one.

Example:

```
[VERIFIED] [TIME-SENSITIVE] Node.js 22 is the current LTS version.
[Source: Node.js Release Schedule, OpenJS Foundation, 2024-10-29, https://github.com/nodejs/release]
Researched: 2025-01-15
Re-verify before execution: yes
```

## Avoiding Hallucinated Facts

Rules to prevent fabrication:

1. **No source, no claim.** If you cannot find an authoritative source, state "no authoritative source found" and record an assumption.
2. **Never fabricate URLs.** If you cite a source, the URL must be real. If you are unsure of the exact URL, cite the source by title and organization without a URL.
3. **Never fabricate quotes.** If you quote a source, the quote must be verbatim. If you paraphrase, label it as a paraphrase.
4. **Never fabricate dates or versions.** If you are unsure of a version number, state "version unknown" and label the claim as an assumption.
5. **When in doubt, assume.** It is always better to label something as an assumption than to fabricate a source.

## Producing Reusable Research Summaries

The research summary (Phase 5 output) must be structured for reuse by downstream agents. Format:

```
# Research Summary: <domain>

## Domain
<domain label and sub-domain>

## Research Date
<YYYY-MM-DD>

## Key Findings

### Finding 1: <title>
[VERIFIED] <claim>
[Source: <citation>]

### Finding 2: <title>
[ASSUMPTION] <claim>
Reasoning: <why>
Confidence: high/medium/low

## Conflicts
<any conflicts and resolutions>

## Time-Sensitive Claims
<any claims that need re-verification>

## Gaps
<topics where no authoritative source was found>

## Recommendations for Downstream Agents
<what the workflow-architect, skill-architect, and implementation-planner should know>
```

## Domain-Specific Notes

| Domain | Key Sources | Special Rules |
|--------|------------|---------------|
| Legal / litigation | Statutes, case law, bar association guidelines, regulatory text | Always cite the jurisdiction. Note that legal information is not legal advice. |
| Security | NIST, OWASP, CVE database, vendor security advisories | Always record research date. Security info is time-sensitive. |
| Technical / product | Official vendor docs, standards bodies (W3C, IETF, ISO) | Verify version numbers. Prefer current LTS/stable versions. |
| Design | W3C/WAI for accessibility, Material Design / Human Interface Guidelines for UI | Distinguish standards from conventions. |
| Marketing | Industry reports, platform documentation (Google Ads, Meta Ads) | Market data is time-sensitive. Note research date. |
| Compliance | Regulatory text (GDPR, HIPAA, SOX, PCI-DSS) | Always cite the specific regulation and section. Compliance is jurisdiction-dependent. |
| Business operations | ISO, ITIL, recognized methodology frameworks | Distinguish standards from frameworks. |

## Anti-Patterns

- "Based on general knowledge" without a source. This is an assumption, not a verified fact.
- Citing a blog that summarizes an official source without citing the official source directly.
- Recording a claim as verified when the source is a community forum (rank 6) without cross-referencing.
- Omitting the research date for time-sensitive claims.
- Producing a narrative research summary instead of a structured one.
- Skipping research because "the agent already knows this". If it is a domain-specific fact, it must be sourced.