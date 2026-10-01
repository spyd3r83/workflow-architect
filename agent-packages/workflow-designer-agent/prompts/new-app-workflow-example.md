# New App Workflow — Example Prompt

This is an example prompt for generating a new app design workflow package. It shows both the input prompt and the expected package outline.

---

## Input Prompt

You are the Workflow Designer Agent. Design and produce a complete agent workflow package for designing and launching a new mobile app for fitness tracking on iOS and Android.

**Objective**: Design a workflow to build and launch a new cross-platform fitness tracking mobile app.
**Domain**: product (mobile app)
**Constraints**: Cross-platform (iOS and Android). 6-month timeline. Must include user research, security review, and launch readiness.
**Source Materials**: Market research summary at ./sources/market-research.pdf
**Output Path**: agent-packages/new-app-workflow/

---

## Expected Package Outline

### Agents (7)

| Agent | Role |
|-------|------|
| product-strategist | Defines product vision, target audience, feature set, and success metrics. |
| user-researcher | Conducts user research to validate assumptions about target users and their needs. |
| ux-ui-designer | Creates wireframes, user flows, and the visual design system for the app. |
| software-architect | Defines the technical architecture: tech stack, data model, API design, scalability plan. |
| security-engineer | Defines security requirements, conducts threat modeling, and reviews implementation for security. |
| qa-test-engineer | Defines the test strategy and executes testing across functional, performance, and edge cases. |
| launch-readiness-coordinator | Manages pre-launch checklist: app store submissions, marketing, monitoring, and rollout. |

### Skills (7)

| Skill | Purpose | Used By |
|-------|---------|---------|
| market-analysis | Analyzes market research to inform product strategy. | product-strategist |
| user-interview-synthesis | Synthesizes user research into actionable insights. | user-researcher |
| wireframing | Creates wireframes and user flows. | ux-ui-designer |
| design-system-creation | Creates a reusable design system (colors, typography, components). | ux-ui-designer |
| api-contract-design | Designs API contracts between frontend and backend. | software-architect |
| threat-modeling | Identifies and prioritizes security threats. | security-engineer |
| test-strategy | Defines the test plan covering functional, performance, and edge cases. | qa-test-engineer |
| launch-checklist | Creates and verifies the pre-launch checklist. | launch-readiness-coordinator |

### Research Requirements

- Cross-platform mobile development frameworks (React Native, Flutter, native) — current state, pros/cons.
- App store guidelines (Apple App Store, Google Play) — current requirements.
- Mobile security best practices (OWASP Mobile Security Project).
- Fitness app market trends and competitor analysis.
- Accessibility guidelines for mobile apps (WCAG 2.1, iOS HIG, Material Design).

### Workflow Sequence (12 phases)

1. **Intake** — Capture objective, constraints, source materials.
2. **Research** — Market analysis, tech stack evaluation, security baselines, app store guidelines.
3. **Product Strategy** — Define vision, target audience, feature set, success metrics.
4. **User Research** — Validate assumptions about target users.
5. **UX/UI Design** — Wireframes, user flows, design system.
6. **Architecture** — Tech stack, data model, API design, scalability plan.
7. **Security Review** — Threat model, security requirements.
8. **Implementation Planning** — Map design and architecture to implementation tasks.
9. **QA Strategy** — Test plan covering functional, performance, edge cases.
10. **Launch Readiness** — App store submissions, marketing, monitoring, rollout plan.
11. **QC + Red-Team** — Quality control and adversarial review.
12. **Final Packaging** — Assemble and deliver.

### File Structure

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

### QA Checks (specific to app design)

- [ ] All agents have distinct roles.
- [ ] User research phase validates product strategy assumptions.
- [ ] Security review includes threat modeling (OWASP Mobile).
- [ ] Architecture phase addresses cross-platform requirements.
- [ ] App store guidelines researched and cited.
- [ ] Launch readiness includes both iOS and Android submission processes.
- [ ] Test strategy covers functional, performance, and edge cases.
- [ ] Accessibility guidelines for mobile included.

### Red-Team Checks (specific to app design)

- **Critic**: Are any agent descriptions vague? Is the workflow over- or under-engineered for a 6-month timeline?
- **Client**: Does this produce a launchable app? Are the success metrics measurable?
- **Developer**: Is the architecture detailed enough to implement from? Are API contracts defined?
- **Auditor**: Are security threats identified and prioritized? Is the threat model sourced from OWASP?
- **End-user**: Will user research actually validate the product assumptions? Is there a feedback loop?
- **Opposing stakeholder**: What if target users do not adopt the UX? What if the architecture cannot scale? What if security review fails pre-launch? What if app store review rejects the submission?