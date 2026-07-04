---
name: resume
description: Resume an in-progress workflow design project. Finds a previously generated package, loads its state, and continues from the last completed phase.
triggers:
  - "resume workflow"
  - "continue workflow"
  - "resume project"
argument-hint: <project name or path>
---

# Resume — Continue an In-Progress Workflow Design Project

You are the Workflow Designer Agent (workflow-orchestrator). Resume an interrupted workflow package generation.

## Target

$ARGUMENTS

## Steps

1. If $ARGUMENTS is empty, list all directories under `generated-workflows/` and ask the user which to resume.
2. If $ARGUMENTS is a name, look for `generated-workflows/<name>-workflow/`.
3. If $ARGUMENTS is a path, use it directly.
4. Read the package's `workflow.md` to determine which phases are complete.
5. Check for `validation-report.json` or inspect files to infer progress.
6. Run `python3 scripts/validate-package.py <path>` to assess current state.
7. Continue execution from the identified phase.
8. Apply Oracle gates at Phase 1.5, Phase 3, and Phase 12 as needed.
9. Produce the final summary when complete.

## Rules

- Do not redo completed phases unless validation fails.
- Preserve all existing work that passes validation.
- Run validate-package.py before resuming to get a baseline.