# Red-Team Review — Workflow Designer Agent

The red-team review is an adversarial review process that challenges the workflow package from multiple stakeholder perspectives. It runs after quality control passes. The red-team-reviewer agent executes this.

## Purpose

Quality control checks for compliance with a checklist. Red-team review checks for usability, robustness, and real-world viability. A package can pass QC and still be polished-but-unusable. Red-team exists to catch that.

## Review Perspectives

The red-team reviewer must evaluate the package from each of these perspectives:

| Perspective | What They Look For |
|-------------|-------------------|
| Critic | Vague instructions, missing detail, overconfident claims, generic outputs. |
| Client | Does this actually solve my problem? Is the deliverable what I asked for? Are assumptions reasonable? |
| Developer | Can I implement this? Are the file structures clean? Are handoffs clear? Is there enough detail to code from? |
| Auditor | Are sources cited? Are assumptions labelled? Is there a trail for every decision? |
| End-user | Will the workflow output be usable? Are the deliverables concrete? |
| Opposing stakeholder | What would someone who disagrees attack? Where are the weak points? What assumptions would they challenge? |

## What The Red-Team Challenges

1. **Unsupported claims** — any factual claim without a source.
2. **Vague workflows** — any phase, step, or instruction that lacks concrete actions.
3. **Missing source support** — any domain-specific claim that should have been researched but was not.
4. **Incomplete agent responsibilities** — any agent whose responsibilities do not cover its stated mission.
5. **Weak file structures** — file trees that are missing files, have orphaned files, or do not match the output spec.
6. **Unclear handoffs** — any agent-to-agent handoff that does not specify what is passed and in what format.
7. **Unrealistic assumptions** — any assumption that is not reasonable or not labelled with confidence level.
8. **Implementation gaps** — anything that looks good in design but would fail in execution.
9. **Domain-specific risks** — risks specific to the domain (e.g., compliance gaps in legal workflows, security holes in security workflows).
10. **Polished-but-unusable outputs** — packages that look complete but cannot be used by another agent without significant additional work.

## Red-Team Report Format

The red-team reviewer produces a structured report:

```
# Red-Team Review Report: <package name>

## Review Date
<YYYY-MM-DD>

## Perspectives Covered
- [x] Critic
- [x] Client
- [x] Developer
- [x] Auditor
- [x] End-user
- [x] Opposing stakeholder

## Issues Found

### Issue 1
- Description: <what is wrong>
- Perspective: <which perspective found it>
- Severity: critical / high / medium / low
- Severity Score: <1-10>
- Occurrence Likelihood: <1-10>
- Detection Difficulty: <1-10>
- RPN: <S x O x D>
- Recommended fix: <specific action to resolve>
- Mandatory / Optional: mandatory / optional
- FMEA Reference: <FM-XXX if this maps to a known failure mode, or "NEW" if novel>

### Issue 2
...

## Summary
- Critical issues: <N>
- High issues: <N>
- Medium issues: <N>
- Low issues: <N>
- Mandatory fixes: <N>
- Optional fixes: <N>
- Average RPN: <N>
- Max RPN: <N>
- New failure modes discovered: <N> (add to fmea.md)

## Quantitative Scoring

| Metric | Target | Actual |
|--------|--------|--------|
| Issues with RPN ≥ 100 | 0 | <N> |
| Issues with RPN ≥ 200 | 0 | <N> |
| Mandatory fix count | 0 | <N> |
| Perspectives covered | 6 | <N> |
| Domain-specific vectors applied | ≥ 3 | <N> |

## FMEA Review

The red-team reviewer must check `fmea.md` for:
- [ ] All failure modes with RPN ≥ 100 have mitigations
- [ ] Mitigations are actually implemented in the package (not just documented)
- [ ] Any new failure modes discovered during review are added to fmea.md
- [ ] Severity/occurrence/detection scores are honest (not inflated or deflated)

## Final Recommendation
PASS / FAIL
```

## Severity Definitions

| Severity | Definition | Action |
|----------|-----------|--------|
| Critical | The package cannot be used as-is. A fundamental flaw. | Mandatory fix. Blocks finalization. |
| High | The package will fail in execution or produce wrong results. | Mandatory fix. Blocks finalization. |
| Medium | The package will work but has a significant weakness. | Optional fix. Documented in final summary. |
| Low | The package is usable but could be improved. | Optional fix. Documented in final summary. |

## Pass/Fail Criteria

- **FAIL** if any critical or high-severity issues exist.
- **PASS** if only medium and low-severity issues exist (these are documented but do not block finalization).
- The red-team reviewer can also **FAIL** the package if, in their judgement, the package is polished-but-unusable even if no single issue is critical. This judgement must be justified in the report.

## Mandatory vs Optional

- **Mandatory**: critical and high-severity issues. The package cannot be finalized until these are resolved.
- **Optional**: medium and low-severity issues. These are documented in the final summary so the user is aware, but they do not block finalization.

## Revision Loop Integration

When red-team returns FAIL:

1. The orchestrator collects all mandatory issues.
2. Routes each issue to the responsible agent for fixing.
3. Collects fixes.
4. Re-runs red-team on the revised package.
5. If PASS → proceed to final packaging (Phase 14).
6. If FAIL → iterate (max 3 times).
7. If still failing after 3 iterations → escalate to user with unresolved issues.

## Domain-Specific Attack Vectors

The red-team reviewer applies domain-specific challenges in addition to the general ones:

| Domain | Additional Attack Vectors |
|--------|--------------------------|
| Legal / litigation | Missing jurisdiction, missing regulatory citation, treating legal info as legal advice, missing conflict-of-interest check |
| Security | Missing threat model, outdated vulnerability data, missing compliance framework, assuming security without verification |
| Web / design | Missing accessibility check, missing SEO baseline, assuming browser compatibility without testing, ignoring performance |
| App / product | Missing user research, assuming user needs without validation, missing scalability check, ignoring platform constraints |
| Compliance | Missing regulatory citation, wrong jurisdiction, missing audit trail, assuming compliance without verification |
| Marketing | Missing market data citation, assuming audience without research, time-sensitive data not flagged |
| Business operations | Missing process validation, assuming workflow without stakeholder input, missing efficiency metrics |

## Anti-Patterns

- Rubber-stamping: marking PASS without finding any issues. A review with zero issues is suspicious — re-examine.
- Vague issues: "the workflow could be better" is not an issue. Every issue must be specific and actionable.
- Missing perspectives: skipping any of the 6 perspectives. All must be covered.
- Inflating severity: marking everything critical. Use severity honestly.
- Deferring fixes: marking mandatory issues as optional to avoid the revision loop. This is a violation.