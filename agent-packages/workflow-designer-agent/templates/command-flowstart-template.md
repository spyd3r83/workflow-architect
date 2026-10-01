# Generated Package Command Template — Flowstart

This template defines the `/flowstart` command for a generated workflow package. The Workflow Designer Agent fills in `{{PLACEHOLDERS}}` when generating a package.

---

Start the {{WORKFLOW_NAME}} workflow.

Usage: /{{COMMAND_NAME}} <project-specific arguments>

## Instructions

You are the {{PRIMARY_AGENT_NAME}} for the {{WORKFLOW_NAME}} workflow. Execute the full workflow defined in `workflow.md` to produce the project deliverable.

### Arguments

$ARGUMENTS

### Steps

1. Read `AGENTS.md` for operating instructions.
2. Read `workflow.md` for the full phase sequence.
3. Treat $ARGUMENTS as the primary input (Phase 1).
4. If $ARGUMENTS is empty, ask the user for {{REQUIRED_INPUT_DESCRIPTION}}.
5. Execute all phases in order, following gates and validation criteria.
6. Run validation checks as specified in `quality-control.md`.
7. Invoke Oracle at designated gates (if specified in workflow.md).
8. Produce the final deliverable and user-facing summary.

### Rules

- Follow `quality-control.md` for acceptance criteria.
- Follow `research-protocol.md` for source-backed research.
- Follow `fmea.md` for failure mode awareness.
- Every assumption must be labelled with risk classification.
- The first draft is never final — revision loop is mandatory if any gate fails.

---

## Fill Instructions

1. **{{WORKFLOW_NAME}}**: The name of the generated workflow (e.g., "Website Revamp Workflow").
2. **{{COMMAND_NAME}}**: The slash command name (e.g., "revamp-site", "launch-app", "audit-security").
3. **{{PRIMARY_AGENT_NAME}}**: The primary coordinating agent for this workflow (e.g., "workflow-orchestrator", "revamp-coordinator").
4. **{{REQUIRED_INPUT_DESCRIPTION}}**: What the workflow needs as input (e.g., "the website URL and revamp goals").

## Validation Criteria

- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] Command name is kebab-case.
- [ ] Primary agent name matches an agent in `agents/`.
- [ ] Steps reference the correct phase count from `workflow.md`.