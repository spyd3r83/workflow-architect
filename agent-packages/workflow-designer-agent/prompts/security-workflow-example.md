# Security Workflow — Example Prompt

This is an example prompt for generating a security engineering workflow package. It shows both the input prompt and the expected package outline.

---

## Input Prompt

You are the Workflow Designer Agent. Design and produce a complete agent workflow package for conducting a security audit of an AWS infrastructure against NIST Cybersecurity Framework standards.

**Objective**: Design a workflow to audit our AWS infrastructure for security compliance against NIST CSF and remediate identified vulnerabilities.
**Domain**: security (cloud infrastructure audit)
**Constraints**: AWS environment. Must follow NIST CSF. Production systems cannot be disrupted. 4-week timeline.
**Source Materials**: AWS account inventory at ./sources/aws-inventory.json, prior audit report at ./sources/audit-2024.pdf
**Output Path**: agent-packages/security-audit-workflow/

---

## Expected Package Outline

### Agents (6)

| Agent | Role |
|-------|------|
| threat-modeler | Identifies and prioritizes threats to the AWS infrastructure using NIST CSF categories. |
| vulnerability-researcher | Researches known vulnerabilities (CVEs) affecting the AWS services in use. |
| security-architect | Defines remediation architecture for identified vulnerabilities. |
| compliance-auditor | Maps findings to NIST CSF controls and produces compliance documentation. |
| penetration-tester | Validates vulnerabilities through controlled testing (non-disruptive). |
| incident-response-planner | Creates or updates the incident response plan based on audit findings. |

### Skills (6)

| Skill | Purpose | Used By |
|-------|---------|---------|
| threat-modeling | Identifies and prioritizes threats using NIST CSF. | threat-modeler |
| vulnerability-research | Researches CVEs and AWS security advisories. | vulnerability-researcher |
| remediation-design | Designs secure architecture remediations. | security-architect |
| compliance-mapping | Maps findings to NIST CSF controls. | compliance-auditor |
| controlled-testing | Validates vulnerabilities non-disruptively. | penetration-tester |
| incident-response-planning | Creates incident response plans. | incident-response-planner |

### Research Requirements

- NIST Cybersecurity Framework (current version, all 5 functions: Identify, Protect, Detect, Respond, Recover).
- AWS Security Best Practices (AWS documentation, AWS Security Hub).
- Current CVEs for AWS services in use (CVE database, AWS security advisories).
- OWASP Cloud Security best practices.
- CIS AWS Benchmark (if applicable).

### Workflow Sequence (10 phases)

1. **Intake** — Capture objective, constraints, AWS inventory, prior audit.
2. **Research** — NIST CSF, AWS security best practices, current CVEs.
3. **Threat Modeling** — Identify and prioritize threats by NIST CSF category.
4. **Vulnerability Research** — Research known CVEs for AWS services in use.
5. **Controlled Testing** — Non-disruptive validation of identified vulnerabilities.
6. **Remediation Design** — Design architecture fixes for confirmed vulnerabilities.
7. **Compliance Mapping** — Map findings to NIST CSF controls; produce compliance report.
8. **Incident Response Planning** — Update IR plan based on findings.
9. **QC + Red-Team** — Quality control and adversarial review.
10. **Final Packaging** — Assemble audit report, remediation plan, compliance documentation, IR plan.

### File Structure

```
security-audit-workflow/
  README.md
  AGENTS.md
  workflow.md
  intake.md
  research-protocol.md
  quality-control.md
  red-team-review.md
  agents/
    threat-modeler.md
    vulnerability-researcher.md
    security-architect.md
    compliance-auditor.md
    penetration-tester.md
    incident-response-planner.md
  skills/
    threat-modeling.md
    vulnerability-research.md
    remediation-design.md
    compliance-mapping.md
    controlled-testing.md
    incident-response-planning.md
  prompts/
    master-prompt.md
    security-audit-example.md
  templates/
    agent-file-template.md
    skill-file-template.md
    workflow-package-template.md
    intake-template.md
    qa-checklist-template.md
    red-team-template.md
    final-summary-template.md
  examples/
    aws-nist-audit-example.md
```

### QA Checks (specific to security audit)

- [ ] All agents have distinct roles.
- [ ] NIST CSF version cited and current.
- [ ] CVE research includes research date (time-sensitive).
- [ ] Threat model covers all 5 NIST CSF functions.
- [ ] Remediation design does not disrupt production (constraint addressed).
- [ ] Compliance mapping covers all relevant NIST CSF controls.
- [ ] Incident response plan addresses findings.
- [ ] Controlled testing explicitly non-disruptive.

### Red-Team Checks (specific to security audit)

- **Critic**: Are any agent descriptions vague? Is the threat model comprehensive?
- **Client**: Does this produce an actionable audit? Are remediations prioritized?
- **Developer**: Can the security-architect's remediations be implemented? Are AWS-specific?
- **Auditor**: Is NIST CSF cited correctly? Are CVEs sourced? Is the research date recorded?
- **End-user**: Will the audit find real vulnerabilities, not just theoretical ones?
- **Opposing stakeholder**: What if a critical vulnerability is found in production and cannot be remediated without disruption? What if the CVE database is outdated? What if the threat model misses a category? What if the compliance mapping is incomplete for the user's specific regulatory requirements?