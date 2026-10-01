# Generated Package Command Template — Resume

This template defines the `/resume` command for a generated workflow package.

---

Resume an in-progress {{WORKFLOW_NAME}} project.

Usage: /{{COMMAND_NAME}}-resume <project name or path>

## Instructions

You are the {{PRIMARY_AGENT_NAME}} for the {{WORKFLOW_NAME}} workflow. Resume an interrupted project.

### Arguments

$ARGUMENTS

### Steps

1. If $ARGUMENTS is empty, list existing project directories and ask the user which to resume.
2. If $ARGUMENTS is a name, look for the project directory by name.
3. If $ARGUMENTS is a path, use it directly.
4. Read `workflow.md` to determine which phases are complete.
5. Check for `validation-report.json` or inspect output files to infer progress.
6. Run validation to assess current state.
7. Continue execution from the identified phase.
8. Apply Oracle gates as specified in `workflow.md`.
9. Produce the final deliverable and summary when complete.

### Rules

- Do not redo completed phases unless validation fails.
- Preserve all existing work that passes validation.
- Run validation before resuming to get a baseline.

---

## Fill Instructions

1. **{{WORKFLOW_NAME}}**: The name of the generated workflow.
2. **{{COMMAND_NAME}}**: The slash command name (same as flowstart).
3. **{{PRIMARY_AGENT_NAME}}**: The primary coordinating agent.

## Validation Criteria

- [ ] No `{{PLACEHOLDER}}` remains.
- [ ] Command name matches the flowstart command name with `-resume` suffix.