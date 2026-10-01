# Red-Team Review Template

This template defines the structure for a red-team review report. Fill in all sections.

---

# Red-Team Review Report: {{PACKAGE_NAME}}

## Review Date

{{YYYY-MM-DD}}

## Perspectives Covered

- [ ] Critic
- [ ] Client
- [ ] Developer
- [ ] Auditor
- [ ] End-user
- [ ] Opposing stakeholder

## Issues Found

### Issue 1

- **Description**: {{what is wrong — specific and actionable}}
- **Perspective**: {{which perspective found it}}
- **Severity**: {{critical / high / medium / low}}
- **Recommended fix**: {{specific action to resolve}}
- **Mandatory / Optional**: {{mandatory / optional}}

### Issue 2

- **Description**: {{what is wrong}}
- **Perspective**: {{which perspective}}
- **Severity**: {{critical / high / medium / low}}
- **Recommended fix**: {{specific action}}
- **Mandatory / Optional**: {{mandatory / optional}}

### Issue {{N}}

{{... add more issues as needed}}

## Domain-Specific Attack Vectors Applied

{{DOMAIN_SPECIFIC_VECTORS — list the domain-specific challenges applied. Example for security:}}

- [ ] Missing threat model category checked
- [ ] Outdated vulnerability data checked
- [ ] Missing compliance framework checked
- [ ] Non-disruptive testing constraint checked

## Summary

- Critical issues: {{N}}
- High issues: {{N}}
- Medium issues: {{N}}
- Low issues: {{N}}
- Mandatory fixes: {{N}}
- Optional fixes: {{N}}

## Final Recommendation

{{PASS / FAIL}}

{{If FAIL: "Package requires revision. Mandatory issues must be resolved before finalization."}}
{{If PASS: "Package is approved for finalization. Optional issues documented for user awareness."}}

## Optional Issues (documented for final summary)

{{If PASS with optional issues, list them here for inclusion in the final summary.}}

- {{optional issue 1}}
- {{optional issue 2}}

---

## Fill Instructions

1. **Cover all 6 perspectives.** Skipping any is a violation.
2. **Every issue must be specific and actionable.** "Could be better" is not an issue.
3. **Severity**: critical (cannot be used as-is), high (will fail in execution), medium (significant weakness), low (improvement).
4. **Mandatory**: critical and high. **Optional**: medium and low.
5. **Apply domain-specific attack vectors** in addition to general challenges.
6. **A review with zero issues is suspicious.** Re-examine before marking PASS.
7. **Final recommendation**: FAIL if any critical or high issues. PASS if only medium and low.

## Validation Criteria (when this template is properly filled)

- [ ] All 6 perspectives checked.
- [ ] Every issue has description, perspective, severity, recommended fix, mandatory/optional.
- [ ] Domain-specific attack vectors applied.
- [ ] Summary counts are accurate.
- [ ] Final recommendation is PASS or FAIL (not "maybe").
- [ ] If PASS with optional issues, they are listed for the final summary.