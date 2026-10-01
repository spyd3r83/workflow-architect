# Example: Website Revamp Package

This example shows how the Workflow Designer Agent would create a package for revamping a marketing website. It serves as a reference output.

---

## Project Objective

"Revamp our marketing website to improve SEO rankings and meet WCAG 2.1 AA accessibility standards."

## Assumptions Made

```
[ASSUMPTION] Project type: website revamp
  Reasoning: Objective mentions "revamp our marketing website".
  Confidence: high

[ASSUMPTION] Target audience: prospective customers visiting the marketing site
  Reasoning: Marketing sites typically target prospects. User did not specify.
  Confidence: medium

[ASSUMPTION] Tools/platforms: tool-agnostic
  Reasoning: User did not specify a CMS or framework. Workflow will be adaptive.
  Confidence: medium

[ASSUMPTION] Timeline: not specified — workflow will be timeline-adaptive
  Reasoning: User did not specify a deadline.
  Confidence: medium

[ASSUMPTION] Success criteria: improved SEO rankings + WCAG 2.1 AA compliance
  Reasoning: Stated in the objective.
  Confidence: high
```

## Domain Classification

- **Domain**: web
- **Sub-domain**: marketing website revamp
- **Domain-specific risks**:
  - SEO ranking drop during migration
  - Content loss during CMS migration
  - Accessibility compliance gaps
  - Performance degradation from new design

## Suggested Agents (7)

### 1. content-auditor
- **Role**: Audits existing website content for quality, accuracy, relevance, and SEO performance.
- **Mission**: Produce a content audit report with keep/revise/remove recommendations per page.
- **Key responsibilities**:
  - Inventory all existing pages.
  - Assess content quality (accuracy, freshness, relevance).
  - Analyze SEO performance per page (traffic, rankings, conversions).
  - Recommend keep/revise/remove per page.
  - Identify content gaps.

### 2. ia-architect
- **Role**: Defines the new information architecture, sitemap, and navigation structure.
- **Mission**: Produce a sitemap and navigation structure that preserves SEO equity and improves user flow.
- **Key responsibilities**:
  - Map existing URL structure.
  - Define new sitemap based on content audit.
  - Plan URL redirects to preserve SEO equity.
  - Define navigation structure.
  - Define internal linking strategy.

### 3. visual-designer
- **Role**: Creates the visual design system and page mockups.
- **Mission**: Produce a design system spec and page mockups that align with brand and accessibility requirements.
- **Key responsibilities**:
  - Create design system (colors, typography, spacing, components).
  - Ensure color contrast meets WCAG 2.1 AA.
  - Create page mockups for all page types.
  - Define responsive breakpoints.
  - Specify interactive states (hover, focus, active).

### 4. seo-specialist
- **Role**: Defines SEO requirements including keywords, meta structure, and performance targets.
- **Mission**: Produce an SEO requirements document that drives the implementation.
- **Key responsibilities**:
  - Define keyword strategy based on content audit and market research.
  - Define meta tag structure (title, description, OG tags).
  - Define URL structure and redirect strategy.
  - Define performance targets (Core Web Vitals).
  - Define structured data requirements (Schema.org).

### 5. accessibility-auditor
- **Role**: Defines accessibility requirements against WCAG 2.1 AA and verifies implementation.
- **Mission**: Ensure the new website meets WCAG 2.1 Level AA conformance.
- **Key responsibilities**:
  - Define WCAG 2.1 AA requirements checklist.
  - Specify automated testing tools.
  - Specify manual testing procedures.
  - Verify implementation against requirements.
  - Produce accessibility compliance report.

### 6. frontend-engineer
- **Role**: Implements the new frontend based on design, SEO, and accessibility requirements.
- **Mission**: Produce the implemented frontend code that meets all requirements.
- **Key responsibilities**:
  - Implement design system as reusable components.
  - Implement page templates from mockups.
  - Implement SEO requirements (meta tags, structured data, performance).
  - Implement accessibility requirements (ARIA, semantic HTML, keyboard nav).
  - Ensure responsive design across breakpoints.

### 7. qa-tester
- **Role**: Tests the implementation against all requirements.
- **Mission**: Produce a QA report confirming the implementation meets SEO, accessibility, performance, and functional requirements.
- **Key responsibilities**:
  - Run automated accessibility tests.
  - Run manual accessibility tests.
  - Run SEO audit (Lighthouse, Screaming Frog).
  - Run performance tests (Core Web Vitals).
  - Run functional tests (links, forms, navigation).
  - Produce QA report with pass/fail per requirement.

## Suggested Skills (6)

### 1. content-audit
- **Purpose**: Inventories and assesses existing content for quality, accuracy, relevance, and SEO performance.
- **Used by**: content-auditor

### 2. ia-mapping
- **Purpose**: Defines sitemap, navigation structure, and URL redirect strategy.
- **Used by**: ia-architect

### 3. visual-system-design
- **Purpose**: Creates a design system (colors, typography, components) that meets accessibility requirements.
- **Used by**: visual-designer

### 4. seo-analysis
- **Purpose**: Defines SEO requirements based on keywords, best practices, and performance targets.
- **Used by**: seo-specialist

### 5. accessibility-validation
- **Purpose**: Tests implementation against WCAG 2.1 AA using automated and manual methods.
- **Used by**: accessibility-auditor, qa-tester

### 6. regression-testing
- **Purpose**: Tests implementation against all requirements (SEO, accessibility, performance, functional).
- **Used by**: qa-tester

## Research Requirements

| Topic | Why It Matters | Source Hierarchy |
|-------|---------------|-----------------|
| WCAG 2.1 Level AA standard | Defines accessibility requirements | W3C > WAI > practitioner guides |
| SEO best practices for marketing sites | Drives SEO requirements | Google Search Central > industry guides |
| Core Web Vitals | Defines performance targets | Google web.dev > Google Search Central |
| ADA / Section 508 accessibility legal requirements | Legal compliance risk | DOJ > legal practitioner guides |
| URL redirect best practices | Preserve SEO equity during migration | Google Search Central > industry guides |

## Workflow Sequence (10 phases)

| # | Phase | Responsible Agent | Gate |
|---|-------|-------------------|------|
| 1 | Intake | intake-analyst | Intake document with risk classification accepted |
| 1.5 | Requirements formalization | intake-analyst | Requirements document accepted; **Oracle gate** |
| 2 | Research | domain-researcher | Research summary + source-log with retrieval IDs accepted |
| 3 | Content Audit + Accessibility Requirements (parallel) | content-auditor, accessibility-auditor | Both deliverables accepted |
| 4 | IA Mapping + SEO Requirements (parallel) | ia-architect, seo-specialist | Both deliverables accepted |
| 5 | Visual Design | visual-designer | Design system + mockups accepted |
| 6 | Frontend Implementation | frontend-engineer | Implemented frontend accepted |
| 7 | QA and Testing | qa-tester | QA report shows all requirements met |
| 8 | QC (validate-package.py + quantitative) | quality-reviewer | 18 dimensions + 15 quantitative criteria pass |
| 8.5 | Independent verification | independent verifier | Independent verification PASS |
| 9 | Red-Team Review (FMEA-scored) | red-team-reviewer | Red-team PASS; **Oracle gate** |
| 10 | Final Packaging | final-packager | Package assembled + summary delivered |

## File Structure

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

## QA Checks (specific to website revamp)

- [ ] All 7 agents have distinct roles and all 10 sections.
- [ ] All 6 skills have all 8 sections and are reusable.
- [ ] Accessibility requirements target WCAG 2.1 AA (sourced from W3C).
- [ ] SEO requirements sourced from Google Search Central or equivalent.
- [ ] URL preservation constraint addressed in IA mapping.
- [ ] Content audit covers all existing pages.
- [ ] Frontend implementation phase references design, SEO, and accessibility requirements.
- [ ] QA phase includes both automated and manual accessibility testing.
- [ ] Performance targets (Core Web Vitals) defined.
- [ ] Redirect strategy defined to preserve SEO equity.

## Red-Team Checks (specific to website revamp)

### Critic
- Are any agent descriptions vague? (e.g., "handles design" without specifics)
- Is the workflow over-engineered for a simple site or under-engineered for a complex one?

### Client
- Does this preserve our URL structure? (constraint)
- Will SEO rankings be maintained during the revamp?
- Are the assumptions about target audience reasonable?

### Developer
- Is there enough detail in the frontend-engineer agent to implement from?
- Are handoffs between visual-designer and frontend-engineer clear?
- Is the design system spec detailed enough (colors, typography, components)?

### Auditor
- Are WCAG and SEO sources cited with dates?
- Are assumptions about the current site labelled?
- Is the research date recorded for time-sensitive claims?

### End-user
- Will the new site be faster? (performance targets defined)
- Will the new site be accessible? (WCAG 2.1 AA targeted)
- Will content be improved? (content audit with keep/revise/remove)

### Opposing stakeholder
- What if the CMS migration loses content? (mitigation: content audit before migration)
- What if SEO rankings drop during the revamp? (mitigation: redirect strategy, pre-launch SEO audit)
- What if accessibility testing reveals major issues late in the process? (mitigation: accessibility requirements defined early in Phase 3)
- What if the design system does not translate to implementation? (mitigation: visual-designer and frontend-engineer handoff includes component specs)

## Reliability Mechanisms

The generated package includes these space-level reliability controls:

- **FMEA**: Failure modes for website revamp (CMS data loss, SEO ranking drop, accessibility gaps, performance regression) with RPN scoring and mitigations.
- **Traceability matrix**: Every requirement (WCAG conformance, SEO targets, URL preservation, performance budgets) traced to a deliverable and verification method.
- **Reliability plan**: Error budget < 0.1%, re-verification schedule (accessibility standards: 180 days, SEO best practices: 60 days).
- **Source-log**: Retrieval IDs for W3C WCAG 2.1, Google Search Central, web.dev Core Web Vitals, ADA/Section 508 guidance.
- **Requirements**: Formal requirements (REQ-001 through REQ-020+) with acceptance criteria.
- **Independent verification**: Phase 11.5 verifies package using deterministic validate-package.py.
- **Oracle gates**: After requirements (Phase 1.5), domain classification (Phase 3), pre-finalization (Phase 9).
- **Self-improvement**: `/update` command analyzes defect patterns from generated packages and improves the workflow.
- **Slash commands**: `/flowstart`, `/resume`, `/maintain`, `/update` available on all 5 platforms.