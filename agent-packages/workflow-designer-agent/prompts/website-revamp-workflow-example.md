# Website Revamp Workflow — Example Prompt

This is an example prompt for generating a website revamp workflow package. It shows both the input prompt and the expected package outline.

---

## Input Prompt

You are the Workflow Designer Agent. Design and produce a complete agent workflow package for revamping a marketing website with improved SEO and accessibility.

**Objective**: Revamp our marketing website to improve SEO rankings and meet WCAG 2.1 AA accessibility standards.
**Domain**: web (marketing website)
**Constraints**: Must preserve existing URL structure for SEO. 3-month timeline.
**Source Materials**: Current site map at ./sources/sitemap.xml, analytics data at ./sources/analytics.csv
**Output Path**: agent-packages/website-revamp-workflow/

---

## Expected Package Outline

### Agents (7)

| Agent | Role |
|-------|------|
| content-auditor | Audits existing website content for quality, accuracy, relevance, and SEO performance. |
| ia-architect | Defines the new information architecture, sitemap, and navigation structure. |
| visual-designer | Creates the visual design system (colors, typography, components) and page mockups. |
| seo-specialist | Defines SEO requirements: keyword strategy, meta structure, URL strategy, performance targets. |
| accessibility-auditor | Defines accessibility requirements against WCAG 2.1 AA and verifies implementation. |
| frontend-engineer | Implements the new frontend based on design, SEO, and accessibility requirements. |
| qa-tester | Tests the implementation against all requirements (SEO, accessibility, performance, functionality). |

### Skills (6)

| Skill | Purpose | Used By |
|-------|---------|---------|
| content-audit | Inventories and assesses existing content. | content-auditor |
| ia-mapping | Defines sitemap and navigation structure. | ia-architect |
| visual-system-design | Creates design system (colors, typography, components). | visual-designer |
| seo-analysis | Defines SEO requirements based on keywords and best practices. | seo-specialist |
| accessibility-validation | Tests implementation against WCAG 2.1 AA. | accessibility-auditor, qa-tester |
| regression-testing | Tests implementation against all requirements. | qa-tester |

### Research Requirements

- Current WCAG standard and conformance level (W3C).
- SEO best practices for marketing websites (Google Search Central, industry guides).
- Accessibility legal requirements (ADA, Section 508 if applicable).
- Performance best practices (Core Web Vitals).
- Current frontend framework best practices (if framework specified).

### Workflow Sequence (10 phases)

1. **Intake** — Capture objective, constraints, source materials.
2. **Research** — WCAG standards, SEO best practices, accessibility legal requirements.
3. **Content Audit + Accessibility Requirements** (parallel) — Audit existing content; define WCAG 2.1 AA requirements.
4. **IA Mapping + SEO Requirements** (parallel) — Define new sitemap; define SEO strategy.
5. **Visual Design** — Create design system and mockups.
6. **Frontend Implementation** — Implement based on design, SEO, and accessibility requirements.
7. **QA and Testing** — Test against all requirements.
8. **QC** — Run QC checklist.
9. **Red-Team Review** — Adversarial review.
10. **Final Packaging** — Assemble and deliver.

### File Structure

```
website-revamp-workflow/
  README.md
  AGENTS.md
  workflow.md
  intake.md
  research-protocol.md
  quality-control.md
  red-team-review.md
  agents/
    content-auditor.md
    ia-architect.md
    visual-designer.md
    seo-specialist.md
    accessibility-auditor.md
    frontend-engineer.md
    qa-tester.md
  skills/
    content-audit.md
    ia-mapping.md
    visual-system-design.md
    seo-analysis.md
    accessibility-validation.md
    regression-testing.md
  prompts/
    master-prompt.md
    website-revamp-example.md
  templates/
    agent-file-template.md
    skill-file-template.md
    workflow-package-template.md
    intake-template.md
    qa-checklist-template.md
    red-team-template.md
    final-summary-template.md
  examples/
    marketing-site-revamp.md
```

### QA Checks (specific to website revamp)

- [ ] All agents have distinct roles.
- [ ] Accessibility requirements target WCAG 2.1 AA (sourced from W3C).
- [ ] SEO requirements are sourced from current best practices.
- [ ] URL preservation constraint addressed in IA mapping.
- [ ] Content audit covers all existing pages.
- [ ] Frontend implementation phase references design, SEO, and accessibility requirements.
- [ ] QA phase includes both automated and manual accessibility testing.

### Red-Team Checks (specific to website revamp)

- **Critic**: Are any agent descriptions vague? Is the workflow over- or under-engineered?
- **Client**: Does this preserve our URL structure? Will SEO rankings be maintained during the revamp?
- **Developer**: Is there enough detail in the frontend-engineer agent to implement from? Are handoffs clear?
- **Auditor**: Are WCAG and SEO sources cited? Are assumptions about the current site labelled?
- **End-user**: Will the new site be faster and more accessible? Are performance targets defined?
- **Opposing stakeholder**: What if the CMS migration loses content? What if SEO rankings drop during the revamp? What if accessibility testing reveals major issues late in the process?