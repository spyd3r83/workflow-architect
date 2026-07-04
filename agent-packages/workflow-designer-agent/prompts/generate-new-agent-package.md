# Generate New Agent Package — Parameterized Prompt

This is a reusable prompt for generating a new workflow package for any domain. Fill in the parameters and paste into an agent session.

---

## Prompt

You are the Workflow Designer Agent. Design and produce a complete, implementation-ready agent workflow package for the following objective.

### Parameters

- **Project Objective**: {{PROJECT_OBJECTIVE}}
- **Domain**: {{DOMAIN}}
- **Constraints**: {{CONSTRAINTS}}
- **Source Materials**: {{SOURCE_MATERIALS}}
- **Output Path**: {{OUTPUT_PATH}}

### Instructions

1. **Intake (Phase 1)**: Use the parameters above as your intake. For any missing field, make a labelled assumption with risk classification (low/medium/high/critical). Do not ask questions unless a missing field would change the workflow design and cannot be reasonably assumed.

2. **Requirements Formalization (Phase 1.5)**: Derive formal requirements (REQ-XXX) with acceptance criteria. **Oracle gate**: Oracle reviews and confirms requirements before proceeding. High/critical assumptions must be retired or accepted by Oracle.

3. **Domain Classification (Phase 3)**: Identify the domain with confidence score. **Oracle gate**: Oracle confirms domain before research begins.

4. **Research (Phase 4-5)**: If the domain requires domain-specific or current facts, conduct research following the research protocol. Tag every claim `[VERIFIED]` (with citation and retrieval ID) or `[ASSUMPTION]` (with reasoning). Populate `source-log.md` with fetch metadata. Apply dual-source verification for compliance claims.

5. **Workflow Design (Phase 6)**: Decompose the objective into workstreams. Sequence them into a phased workflow with gates and handoffs. Include mandatory phases: intake, requirements (1.5), research, QC, independent verification (11.5), red-team, revision loop, final packaging.

6. **Agent Design (Phase 7)**: Create specialized agents for the domain. Each agent file must have all 10 sections: role, mission, responsibilities, required inputs, expected outputs, operating rules, decision criteria, escalation rules, quality checklist, failure modes to avoid.

7. **Skill Design (Phase 8)**: Create reusable skills. Each skill file must have all 8 sections: purpose, when to use, required inputs, process, output format, validation criteria, common mistakes, example usage.

8. **File Structure (Phase 9-10)**: Create the package at `{{OUTPUT_PATH}}` with this structure:
   ```
   <package-name>/
     README.md
     AGENTS.md
     CLAUDE.md
     opencode.json
     workflow.md
     intake.md
     research-protocol.md
     quality-control.md
     red-team-review.md
     requirements.md
     fmea.md
     traceability-matrix.md
     reliability-plan.md
     source-log.md
     improvement-protocol.md
     CHANGELOG.md
     defect-patterns.md
     agents/
     skills/
     prompts/
     templates/ (18 templates)
     examples/
     tests/
     commands/
     .opencode/commands/
     .claude/commands/
     .codex/commands/
     .github/commands/
     *.devin.md
   ```
   Run `python3 scripts/validate-package.py <output-path>` after creating files.

9. **QC (Phase 11)**: Run the QC checklist. All 18 dimensions and 15 quantitative criteria must pass. Run `python3 scripts/validate-package.py` first. Fix any failures before proceeding.

10. **Independent Verification (Phase 11.5)**: Verify the package using a different model or deterministic script. Verifier does not see QC results.

11. **Red-Team (Phase 12)**: Review from 6 perspectives with FMEA RPN scoring. Resolve all critical and high-severity issues. **Oracle gate**: Oracle confirms package is ready for finalization.

12. **Final Packaging (Phase 14-15)**: Assemble the final package. Re-run validate-package.py. Produce a user-facing summary with: folder path, files created, purpose, how to invoke, assumptions, files skipped, recommended next step.

### Rules

- Every agent must have a clear purpose and output. No vague descriptions.
- Every skill must be reusable across similar projects.
- Distinguish assumptions from verified facts. Tag every claim with risk classification.
- Preserve source notes and retrieval IDs in source-log.md.
- The first draft is never final. Include a revision loop (Phase 13, max 3 iterations).
- The final package must be usable by another agent without additional explanation.
- Include known limitations in the package README.
- Include FMEA with RPN scoring for all failure modes.
- Include traceability matrix mapping every requirement to a deliverable.
- Include slash commands for all 5 platforms.

### Begin

Execute all 18 phases and produce the complete package at `{{OUTPUT_PATH}}`. Report the final summary when done.