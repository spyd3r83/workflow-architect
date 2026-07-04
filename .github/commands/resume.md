Resume an in-progress workflow design project.

Usage: /resume <project name or path>

This command finds a previously generated (or in-progress) workflow package, loads its state, and continues from the last completed phase.

## Instructions

You are the Workflow Designer Agent (workflow-orchestrator). Resume an interrupted workflow package generation.

### Arguments

$ARGUMENTS

### Steps

1. If $ARGUMENTS is empty, list all directories under `generated-workflows/` and ask the user which to resume.
2. If $ARGUMENTS is a name, look for `generated-workflows/<name>-workflow/`.
3. If $ARGUMENTS is a path, use it directly.
4. Read the package's `workflow.md` to determine which phases are complete.
5. Check for a `validation-report.json` or phase progression log to determine the last completed phase.
6. If no state file exists, inspect the package files to infer progress:
   - If `intake.md` exists but `requirements.md` does not → resume at Phase 1.5
   - If `requirements.md` exists but `research-protocol.md` research summary does not → resume at Phase 4
   - If research exists but `agents/` is empty → resume at Phase 7
   - If agents exist but `skills/` is empty → resume at Phase 8
   - If skills exist but package is incomplete → resume at Phase 9-10
   - If package is complete but no QC report → resume at Phase 11
   - If QC passed but no independent verification → resume at Phase 11.5
   - If independent verification passed but no red-team report → resume at Phase 12
   - If red-team passed but no final summary → resume at Phase 14-15
7. Run `python3 scripts/validate-package.py <path>` to assess current state.
8. Continue execution from the identified phase.
9. Apply Oracle gates at Phase 1.5, Phase 3, and Phase 12 as needed.
10. Produce the final summary when complete.

### Rules

- Do not redo completed phases unless validation fails.
- If a completed phase's output is invalid, redo that phase.
- Preserve all existing work that passes validation.
- Run validate-package.py before resuming to get a baseline.