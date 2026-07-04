# Skill: Red-Team Analysis

## Purpose

Performs adversarial review of a generated workflow package from multiple stakeholder perspectives. Finds weaknesses that QC misses and produces a structured report with severity and fix recommendations.

## When To Use

- Phase 12 (Red-Team Review) of the Workflow Designer Agent workflow.
- When the red-team-reviewer needs to challenge the package after QC passes.

## Required Inputs

- **Draft package** on disk (with passing QC).
- **`red-team-review.md`** — review process, perspectives, domain-specific attack vectors.
- **Intake document** — to verify user-objective alignment from the client perspective.
- **Domain classification** — to apply domain-specific attack vectors.

## Process

1. **Review from the Critic perspective.** Look for: vague instructions, missing detail, overconfident claims, generic outputs. For each finding, record the issue.
2. **Review from the Client perspective.** Look for: does this solve my problem? Are assumptions reasonable? Is the deliverable what I asked for? Record issues.
3. **Review from the Developer perspective.** Look for: can I implement this? Are file structures clean? Are handoffs clear? Is there enough detail to code from? Record issues.
4. **Review from the Auditor perspective.** Look for: are sources cited? Are assumptions labelled? Is there a decision trail? Record issues.
5. **Review from the End-user perspective.** Look for: will the workflow output be usable? Are deliverables concrete? Record issues.
6. **Review from the Opposing stakeholder perspective.** Look for: what would a critic attack? Where are the weak points? What assumptions would they challenge? Record issues.
7. **Apply domain-specific attack vectors.** Based on the domain, apply additional challenges (e.g., missing jurisdiction for legal, outdated vulnerability data for security, missing accessibility check for web).
8. **Assign severity to each issue:**
   - Critical: package cannot be used as-is.
   - High: package will fail in execution.
   - Medium: significant weakness but usable.
   - Low: improvement opportunity.
9. **Determine mandatory vs optional.** Critical and high are mandatory. Medium and low are optional.
10. **Make a pass/fail recommendation.** FAIL if any critical or high issues. PASS if only medium and low.
11. **Produce the red-team report.**

## Output Format

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
- Perspective: <which perspective>
- Severity: critical / high / medium / low
- Recommended fix: <specific action>
- Mandatory / Optional: mandatory / optional

### Issue 2
...

## Summary
- Critical: <N>
- High: <N>
- Medium: <N>
- Low: <N>
- Mandatory fixes: <N>
- Optional fixes: <N>

## Final Recommendation
PASS / FAIL
```

## Validation Criteria

- [ ] All 6 perspectives covered.
- [ ] Every issue has description, perspective, severity, recommended fix, mandatory/optional.
- [ ] Severity assigned honestly.
- [ ] Domain-specific attack vectors applied.
- [ ] Final recommendation is PASS or FAIL.
- [ ] Report is structured.
- [ ] A review with zero issues is re-examined before PASS.

## Common Mistakes

- **Rubber-stamping**: marking PASS without finding issues. A zero-issue review is suspicious.
- **Vague issues**: "could be better" is not an issue. Be specific.
- **Missing perspectives**: skipping one of the 6. All must be covered.
- **Inflating severity**: marking everything critical. Use severity honestly.
- **Deferring mandatory fixes**: marking critical issues as optional to avoid the revision loop.
- **Not applying domain-specific vectors**: only doing general challenges. Apply domain-specific ones too.
- **Narrative report**: writing paragraphs instead of structured issues.

## Example Usage

**Input:**
```
Package: website-revamp-workflow
Domain: web
QC status: PASS
```

**Output (excerpt):**
```
# Red-Team Review Report: website-revamp-workflow

## Perspectives Covered
- [x] Critic
- [x] Client
- [x] Developer
- [x] Auditor
- [x] End-user
- [x] Opposing stakeholder

## Issues Found

### Issue 1
- Description: The accessibility-auditor agent does not specify which WCAG conformance level to target. The research summary mentions WCAG 2.1 AA, but the agent file does not reference it.
- Perspective: Auditor
- Severity: high
- Recommended fix: Add to accessibility-auditor.md: "Target WCAG 2.1 Level AA conformance as defined in the research summary."
- Mandatory / Optional: mandatory

### Issue 2
- Description: The frontend-engineer agent assumes React but the intake document did not specify a framework.
- Perspective: Client
- Severity: medium
- Recommended fix: Make the framework a parameter. State in the agent file: "Use the framework specified in intake; if not specified, label as assumption and ask."
- Mandatory / Optional: optional

### Issue 3
- Description: No performance budget defined for the website. Large images could slow the site.
- Perspective: End-user
- Severity: medium
- Recommended fix: Add a performance requirement phase or note in the SEO requirements.
- Mandatory / Optional: optional

## Summary
- Critical: 0
- High: 1
- Medium: 2
- Low: 0
- Mandatory fixes: 1
- Optional fixes: 2

## Final Recommendation
FAIL (1 high-severity mandatory issue)
```