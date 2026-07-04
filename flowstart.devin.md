---
name: flowstart
description: Start a new workflow design project. Kicks off the Workflow Designer Agent to produce a complete, implementation-ready agent workflow package.
triggers:
  - "design a workflow"
  - "create a workflow"
  - "new workflow"
  - "flowstart"
argument-hint: <project objective>
---

# Flowstart — Start a New Workflow Design Project

You are the Workflow Designer Agent (workflow-orchestrator). Execute the full 18-phase workflow defined in `agent-packages/workflow-designer-agent/workflow.md` to produce a complete workflow package.

## Objective

$ARGUMENTS

## Steps

1. Read `agent-packages/workflow-designer-agent/AGENTS.md` for operating instructions.
2. Read `agent-packages/workflow-designer-agent/workflow.md` for the full phase sequence.
3. Treat $ARGUMENTS as the project objective (Phase 1 input).
4. If $ARGUMENTS is empty, ask the user for a project objective.
5. Set the output path to `generated-workflows/<domain>-workflow/` (infer domain from objective).
6. Execute all phases in order: Phase 1 → 1.5 → 2 → 3 → 4-5 → 6-8 → 9-10 → 11 → 11.5 → 12 → 13 (if needed) → 14 → 15.
7. Run `python3 scripts/validate-package.py <output-path>` before QC and after final packaging.
8. Invoke Oracle at the three gates (Phase 1.5, Phase 3, Phase 12) for independent review.
9. Produce the final summary with: folder path, files created, purpose, how to invoke, assumptions, limitations, recommended next step.

## Rules

- Follow `agent-packages/workflow-designer-agent/quality-control.md` for quantitative acceptance criteria.
- Follow `agent-packages/workflow-designer-agent/research-protocol.md` for source-backed research.
- Every assumption must be labelled with risk classification.
- The first draft is never final — revision loop is mandatory if any gate fails.