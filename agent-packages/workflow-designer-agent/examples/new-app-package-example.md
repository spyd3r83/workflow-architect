# Example: New App Package

This example shows how the Workflow Designer Agent would create a package for designing a new mobile app. It serves as a reference output.

---

## Project Objective

"Design a workflow to build and launch a new cross-platform fitness tracking mobile app for iOS and Android."

## Assumptions Made

```
[ASSUMPTION] Project type: new app design and development
  Reasoning: Objective mentions "build and launch a new mobile app".
  Confidence: high

[ASSUMPTION] Target audience: fitness enthusiasts who want to track workouts
  Reasoning: Fitness tracking apps target fitness enthusiasts. User did not specify a narrower segment.
  Confidence: medium

[ASSUMPTION] Tools/platforms: cross-platform framework (React Native or Flutter)
  Reasoning: User specified "cross-platform" but not a framework. Workflow will be framework-adaptive.
  Confidence: medium

[ASSUMPTION] Timeline: 6 months
  Reasoning: User did not specify a timeline. 6 months is typical for a cross-platform MVP.
  Confidence: low

[ASSUMPTION] Success criteria: launchable app on both iOS App Store and Google Play
  Reasoning: User said "build and launch". Launch implies app store availability.
  Confidence: high

[ASSUMPTION] Budget: not specified — workflow will be budget-adaptive
  Reasoning: User did not specify a budget.
  Confidence: medium
```

## Domain Classification

- **Domain**: product (mobile app)
- **Sub-domain**: cross-platform fitness app
- **Domain-specific risks**:
  - User adoption uncertainty (fitness app market is crowded)
  - Cross-platform performance gaps
  - App store rejection (guideline violations)
  - Security and privacy (health data is sensitive)
  - Scalability (user growth may outpace architecture)

## Suggested Agents (7)

### 1. product-strategist
- **Role**: Defines product vision, target audience, feature set, and success metrics.
- **Mission**: Produce a product strategy document that aligns the team on what to build and why.
- **Key responsibilities**:
  - Define product vision and value proposition.
  - Define target audience segments.
  - Define MVP feature set (must-have vs nice-to-have).
  - Define success metrics (downloads, retention, engagement).
  - Define competitive positioning.
  - Conduct market analysis using provided research.

### 2. user-researcher
- **Role**: Conducts user research to validate assumptions about target users and their needs.
- **Mission**: Produce user research insights that validate or challenge the product strategy.
- **Key responsibilities**:
  - Design user interview protocol.
  - Synthesize user research into actionable insights.
  - Create user personas based on research.
  - Map user journeys for key flows.
  - Identify pain points and opportunities.
  - Validate product strategy assumptions against research.

### 3. ux-ui-designer
- **Role**: Creates wireframes, user flows, and the visual design system for the app.
- **Mission**: Produce wireframes, user flows, and a design system that delivers a usable, accessible app.
- **Key responsibilities**:
  - Create user flows for key journeys (onboarding, workout tracking, history, settings).
  - Create wireframes for all screens.
  - Create design system (colors, typography, components, icons).
  - Ensure accessibility (WCAG 2.1, iOS HIG, Material Design).
  - Create interactive prototypes for validation.
  - Define animation and micro-interaction specs.

### 4. software-architect
- **Role**: Defines the technical architecture: tech stack, data model, API design, scalability plan.
- **Mission**: Produce an architecture document that the development team can implement from.
- **Key responsibilities**:
  - Evaluate and select cross-platform framework (React Native vs Flutter).
  - Define data model and database schema.
  - Design API contracts between frontend and backend.
  - Define authentication and authorization architecture.
  - Define scalability plan (caching, load balancing, CDN).
  - Define offline-first architecture (fitness tracking needs offline support).
  - Define third-party integrations (health APIs, payment, analytics).

### 5. security-engineer
- **Role**: Defines security requirements, conducts threat modeling, and reviews implementation for security.
- **Mission**: Ensure the app is secure and compliant with health data regulations.
- **Key responsibilities**:
  - Conduct threat modeling using OWASP Mobile Security Project.
  - Define security requirements (encryption, auth, data storage).
  - Define privacy requirements (GDPR, CCPA, HIPAA if applicable).
  - Review architecture for security gaps.
  - Define secure coding guidelines.
  - Plan security testing (SAST, DAST, penetration testing).

### 6. qa-test-engineer
- **Role**: Defines the test strategy and executes testing across functional, performance, and edge cases.
- **Mission**: Produce a test strategy and execute testing to ensure the app is launch-ready.
- **Key responsibilities**:
  - Define test plan covering functional, performance, security, and edge cases.
  - Define test automation strategy (unit, integration, E2E).
  - Define device and OS coverage matrix.
  - Execute manual and automated tests.
  - Track and triage defects.
  - Produce test report with pass/fail per test case.

### 7. launch-readiness-coordinator
- **Role**: Manages pre-launch checklist: app store submissions, marketing, monitoring, and rollout.
- **Mission**: Ensure the app is ready for launch and successfully submitted to both app stores.
- **Key responsibilities**:
  - Create app store submission checklist (iOS App Store, Google Play).
  - Prepare app store assets (screenshots, descriptions, privacy policy).
  - Verify app store guideline compliance.
  - Define monitoring and alerting plan.
  - Define rollout plan (phased rollout vs full launch).
  - Define crash reporting and feedback collection plan.

## Suggested Skills (8)

### 1. market-analysis
- **Purpose**: Analyzes market research to inform product strategy.
- **Used by**: product-strategist

### 2. user-interview-synthesis
- **Purpose**: Synthesizes user research interviews into actionable insights and personas.
- **Used by**: user-researcher

### 3. wireframing
- **Purpose**: Creates wireframes and user flows for app screens.
- **Used by**: ux-ui-designer

### 4. design-system-creation
- **Purpose**: Creates a reusable design system (colors, typography, components, icons).
- **Used by**: ux-ui-designer

### 5. api-contract-design
- **Purpose**: Designs API contracts between frontend and backend.
- **Used by**: software-architect

### 6. threat-modeling
- **Purpose**: Identifies and prioritizes security threats using OWASP Mobile Security Project.
- **Used by**: security-engineer

### 7. test-strategy
- **Purpose**: Defines the test plan covering functional, performance, security, and edge cases.
- **Used by**: qa-test-engineer

### 8. launch-checklist
- **Purpose**: Creates and verifies the pre-launch checklist for app store submissions.
- **Used by**: launch-readiness-coordinator

## Research Requirements

| Topic | Why It Matters | Source Hierarchy |
|-------|---------------|-----------------|
| Cross-platform frameworks (React Native, Flutter) | Tech stack decision | Official docs > practitioner guides > community |
| Apple App Store guidelines | Submission compliance | Apple developer docs |
| Google Play guidelines | Submission compliance | Google Play developer docs |
| OWASP Mobile Security Project | Security baseline | OWASP |
| Health data regulations (HIPAA, GDPR) | Legal compliance | Regulatory text > legal practitioner guides |
| WCAG 2.1 / iOS HIG / Material Design | Accessibility | W3C > Apple > Google |
| Fitness app market trends | Product strategy | Market research reports > app store data |

## Workflow Sequence (12 phases)

| # | Phase | Responsible Agent | Gate |
|---|-------|-------------------|------|
| 1 | Intake | intake-analyst | Intake document accepted |
| 2 | Research | domain-researcher | Research summary with citations accepted |
| 3 | Product Strategy | product-strategist | Product strategy document accepted |
| 4 | User Research | user-researcher | User research insights accepted; strategy assumptions validated |
| 5 | UX/UI Design | ux-ui-designer | Wireframes, flows, and design system accepted |
| 6 | Architecture | software-architect | Architecture document accepted |
| 7 | Security Review | security-engineer | Threat model and security requirements accepted |
| 8 | Implementation Planning | software-architect + frontend lead | Implementation plan accepted |
| 9 | QA Strategy | qa-test-engineer | Test plan accepted |
| 10 | Launch Readiness | launch-readiness-coordinator | Launch checklist completed |
| 11 | QC (validate-package.py + quantitative) | quality-reviewer | 18 dimensions + 15 quantitative criteria pass |
| 11.5 | Independent verification | independent verifier | Independent verification PASS |
| 12 | Red-Team (FMEA-scored) | red-team-reviewer | Red-team PASS; **Oracle gate** |
| 13 | Final Packaging | final-packager | Package assembled + summary delivered |

## File Structure

```
new-app-workflow/
  README.md
  AGENTS.md
  workflow.md
  intake.md
  research-protocol.md
  quality-control.md
  red-team-review.md
  agents/
    product-strategist.md
    user-researcher.md
    ux-ui-designer.md
    software-architect.md
    security-engineer.md
    qa-test-engineer.md
    launch-readiness-coordinator.md
  skills/
    market-analysis.md
    user-interview-synthesis.md
    wireframing.md
    design-system-creation.md
    api-contract-design.md
    threat-modeling.md
    test-strategy.md
    launch-checklist.md
  prompts/
    master-prompt.md
    new-app-example.md
  templates/
    agent-file-template.md
    skill-file-template.md
    workflow-package-template.md
    intake-template.md
    qa-checklist-template.md
    red-team-template.md
    final-summary-template.md
  examples/
    fitness-app-example.md
```

## QA Checks (specific to app design)

- [ ] All 7 agents have distinct roles and all 10 sections.
- [ ] All 8 skills have all 8 sections and are reusable.
- [ ] User research phase validates product strategy assumptions.
- [ ] Security review includes threat modeling (OWASP Mobile sourced).
- [ ] Architecture phase addresses cross-platform requirements.
- [ ] App store guidelines researched and cited (Apple + Google).
- [ ] Launch readiness includes both iOS and Android submission processes.
- [ ] Test strategy covers functional, performance, security, and edge cases.
- [ ] Accessibility guidelines for mobile included (WCAG 2.1, iOS HIG, Material Design).
- [ ] Health data privacy addressed (HIPAA/GDPR if applicable).
- [ ] Offline-first architecture defined (fitness tracking needs offline support).

## Red-Team Checks (specific to app design)

### Critic
- Are any agent descriptions vague? (e.g., "designs the app" without specifics)
- Is the workflow over-engineered for an MVP or under-engineered for a 6-month project?
- Are the success metrics measurable?

### Client
- Does this produce a launchable app on both stores?
- Are the assumptions about target audience validated by user research?
- Is the timeline realistic for the feature set?

### Developer
- Is the architecture detailed enough to implement from?
- Are API contracts defined between frontend and backend?
- Is the offline-first architecture specified?
- Are third-party integrations (health APIs, payment) identified?

### Auditor
- Are security threats identified and prioritized using OWASP?
- Is the threat model sourced?
- Are health data privacy regulations cited (HIPAA, GDPR)?
- Are app store guidelines cited with dates?

### End-user
- Will user research actually validate the product assumptions?
- Is there a feedback loop after launch?
- Will the app be accessible? (WCAG 2.1, iOS HIG, Material Design)
- Will the app work offline? (fitness tracking use case)

### Opposing stakeholder
- What if target users do not adopt the UX? (mitigation: user research before design)
- What if the architecture cannot scale? (mitigation: scalability plan in architecture phase)
- What if security review fails pre-launch? (mitigation: security review in Phase 7, before implementation)
- What if app store review rejects the submission? (mitigation: launch-readiness coordinator verifies guideline compliance)
- What if the cross-platform framework has performance issues? (mitigation: architecture phase evaluates and selects framework)
- What if health data privacy compliance is more complex than expected? (mitigation: security-engineer defines privacy requirements early)

## Reliability Mechanisms

The generated package includes these space-level reliability controls:

- **FMEA**: Failure modes for app development (user adoption failure, scalability limits, security review failure, app store rejection, cross-platform perf issues) with RPN scoring and mitigations.
- **Traceability matrix**: Every requirement (user research validation, security compliance, app store guidelines, accessibility) traced to a deliverable and verification method.
- **Reliability plan**: Error budget < 0.1%, re-verification schedule (security: 30 days, app store guidelines: 60 days, health data regs: 90 days).
- **Source-log**: Retrieval IDs for OWASP Mobile, Apple App Store guidelines, Google Play guidelines, HIPAA/GDPR text, WCAG 2.1.
- **Requirements**: Formal requirements with acceptance criteria covering functional, non-functional, safety, and regulatory.
- **Independent verification**: Phase 11.5 verifies package using deterministic validate-package.py.
- **Oracle gates**: After requirements (Phase 1.5), domain classification (Phase 3), pre-finalization (Phase 12).
- **Self-improvement**: `/update` command analyzes defect patterns from generated packages and improves the workflow.
- **Slash commands**: `/flowstart`, `/resume`, `/maintain`, `/update` available on all 5 platforms.