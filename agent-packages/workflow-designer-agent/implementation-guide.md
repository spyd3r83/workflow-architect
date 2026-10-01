# Implementation Guide — Workflow Designer Agent

This guide explains how to use the Workflow Designer Agent package inside a project.

## How To Invoke The Workflow Designer Agent

### Slash Commands (preferred)

| Command | Purpose | Usage |
|---------|---------|-------|
| `/flowstart <objective>` | Start a new workflow design project | `/flowstart Design a workflow to revamp a marketing website` |
| `/resume <project>` | Resume an in-progress workflow | `/resume website-revamp-workflow` |
| `/maintain <project>` | Validate and update an existing workflow | `/maintain website-revamp-workflow` |
| `/update` | Self-improve the Workflow Designer Agent package | `/update` |

Commands are available on OpenCode, Claude Code, Codex CLI, Copilot CLI, and Devin. See root `AGENTS.md` for platform-specific command paths.

### Manual Invocation (fallback)

If slash commands are not available:

### Step 1: Choose your invocation method

| Method | When to use |
|--------|-------------|
| Master prompt | You have a clear objective and want the full 18-phase workflow. |
| Parameterized prompt | You have objective, domain, constraints, and source materials ready. |
| Example prompt | Your domain matches one of the examples (website revamp, new app, security). Start from the example and modify. |

### Step 2: Open the prompt file

- Master prompt: `prompts/master-workflow-designer-prompt.md`
- Parameterized: `prompts/generate-new-agent-package.md`
- Examples: `prompts/website-revamp-workflow-example.md`, `prompts/new-app-workflow-example.md`, `prompts/security-workflow-example.md`

### Step 3: Fill in placeholders

Replace all `{{PLACEHOLDER}}` values with your project details. At minimum, fill `{{PROJECT_OBJECTIVE}}`.

### Step 4: Paste into an agent session

Paste the filled prompt into an OpenCode-style agent session. The agent will execute the 18-phase workflow defined in `workflow.md`.

## How To Provide A Project Objective

The objective should be 1-2 sentences describing what the workflow should accomplish. Examples:

- "Design a workflow to revamp our marketing website with improved SEO and accessibility."
- "Design a workflow to build a new mobile app for fitness tracking on iOS and Android."
- "Design a workflow to conduct a security audit of our AWS infrastructure against NIST standards."
- "Design a workflow to produce compliance documentation for GDPR and CCPA."
- "Design a workflow to research and document competitor pricing strategies in the SaaS tools market."

A good objective is:
- Specific enough to determine agents and skills.
- Scoped (not "design a workflow for everything").
- Outcome-oriented (states what "done" looks like).

## How To Attach Source Materials

If you have documents, specs, existing code, or links that the domain-researcher agent should review:

1. Place them in a known location (e.g., a `sources/` folder in your project).
2. Reference them in the prompt: `Source materials: ./sources/spec.pdf, ./sources/existing-code/`
3. The domain-researcher will inventory and assess them in Phase 4.

If you have no source materials, the agent will rely on external research and label assumptions. This is fine — just state "no source materials provided" in the prompt.

## How To Request A Generated Workflow Package

The prompt instructs the agent to produce a complete package. The package will be created at a path you specify or at a default location. To control the output path:

1. In the prompt, set `{{OUTPUT_PATH}}` to your desired folder (e.g., `agent-packages/website-revamp-workflow/`).
2. The implementation-planner agent will create the folder structure and write all files there.

If you do not specify an output path, the agent will use `generated-workflows/<domain>-workflow/` relative to the current project.

## How To Review Generated Output

After the agent reports completion:

1. **Check the file tree.** Compare against `package-output-spec.md`. All required files should exist.
2. **Read the package README.** It should explain the workflow, assumptions, and limitations.
3. **Read the AGENTS.md.** It should define the agent hierarchy and operating instructions.
4. **Read the workflow.md.** It should define all phases with inputs, outputs, and validation criteria.
5. **Spot-check agent files.** Open 2-3 agent files and verify they have all 10 required sections.
6. **Spot-check skill files.** Open 2-3 skill files and verify they have all 8 required sections.
7. **Read the QC report.** It should show all items passing.
8. **Read the red-team report.** It should show a PASS recommendation or document optional issues.
9. **Read the final summary.** It should tell you where the package is and how to use it.

## How To Iterate

If the generated package needs changes:

### Minor changes
Edit the generated files directly. The package is yours to modify.

### Major changes (different agents, different workflow)
Re-run the Workflow Designer Agent with a revised objective. The agent will produce a new package. You can diff the new package against the old one to see what changed.

### Iterating via the revision loop
If you are not satisfied with the first draft, you can instruct the agent to enter the revision loop (Phase 13) with specific feedback. The agent will fix the issues and re-run QC and red-team.

### Promoting iteration feedback
When giving feedback, be specific:
- "The agent list is missing a dedicated accessibility auditor" → the agent adds one.
- "The workflow skips user research" → the agent adds a user research phase.
- "The assumptions about timeline are wrong — we have 2 weeks, not 2 months" → the agent updates assumptions and adjusts the workflow.

## How To Promote A Generated Workflow Into A Permanent Agent Package

Once you are satisfied with a generated workflow:

1. **Move the folder** into your project's `agent-packages/` directory (or wherever your project stores agent packages).
2. **Update your project's agent registry** if one exists (e.g., add an entry to a top-level AGENTS.md or agents config).
3. **Test the workflow** by invoking it on a real project. Run through the phases and verify the agents produce the expected outputs.
4. **Document the workflow** in your project's README or docs.
5. **Version the workflow** if your project uses versioning. Tag the initial promotion (e.g., `v1.0.0`).

### Promotion Checklist

- [ ] Package folder moved to permanent location.
- [ ] Package registered in project agent registry (if applicable).
- [ ] Package tested on at least one real project.
- [ ] Package documented in project docs.
- [ ] Any domain-specific assumptions verified against current project state.
- [ ] Source materials and citations still valid (re-verify time-sensitive claims).

## Common Issues And Solutions

| Issue | Solution |
|-------|---------|
| Agent asks too many questions during intake | The intake model limits to 5 questions. If the agent asks more, remind it of the intake rules in `intake.md`. |
| Generated package is too generic | The objective may be too vague. Re-run with a more specific objective. Red-team should catch generic outputs. |
| Research summary has no citations | The domain may not have authoritative sources, or the agent skipped research. Check the research protocol and re-run Phase 5. |
| QC fails repeatedly on the same item | Escalation is expected after 3 iterations. The orchestrator should escalate to the user with the specific item. |
| Red-team fails repeatedly | Same — escalation after 3 iterations. The user may need to provide additional context or adjust the objective. |
| Package does not follow project conventions | State your project's conventions during intake. The implementation-planner will follow them. |

## Quick Start

```
1. Open prompts/master-workflow-designer-prompt.md
2. Replace {{PROJECT_OBJECTIVE}} with your objective
3. Replace {{OUTPUT_PATH}} with your desired output folder
4. Paste into an agent session
5. Wait for the 18-phase workflow to complete
6. Review the generated package at the output path
7. Promote to permanent location if satisfied
```