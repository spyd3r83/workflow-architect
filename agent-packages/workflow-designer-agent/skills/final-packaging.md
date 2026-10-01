# Skill: Final Packaging

## Purpose

Assembles the final, validated workflow package and produces the implementation summary. Ensures all files are present, all gates have passed, and the package is immediately usable.

## When To Use

- Phase 14 (Final Packaging) and Phase 15 (User-Facing Summary) of the Workflow Designer Agent workflow.
- When the final-packager needs to assemble the deliverable after QC and red-team pass.

## Required Inputs

- **Revised package** on disk (QC and red-team passing).
- **QC report** (final, showing PASS).
- **Red-team report** (final, showing PASS or PASS-with-optional-issues).
- **`templates/final-summary-template.md`** — for the summary structure.
- **`package-output-spec.md`** — for final verification.

## Process

1. **Verify file completeness.** Check every file from `package-output-spec.md` exists on disk. List any missing files. If any are missing, block finalization and escalate.
2. **Verify agent section completeness.** For each agent file, verify all 10 sections exist and are populated (not empty). List any missing sections. Block if any are missing.
3. **Verify skill section completeness.** For each skill file, verify all 8 sections exist and are populated. List any missing sections. Block if any are missing.
4. **Verify assumptions are documented.** Check the package README has a dedicated assumptions section with all labelled assumptions from intake and research. Block if missing.
5. **Verify limitations are documented.** Check the package README has a dedicated limitations section. Block if missing.
6. **Verify source notes are preserved.** Check the research summary and any file that references research has intact citations. Block if stripped.
7. **Verify the package is self-contained.** The package must be usable without reading this meta-package. Check that the README explains how to use the package, the workflow defines all phases, and templates are fillable.
8. **Document optional red-team issues.** If red-team passed with optional issues, document them in the final summary so the user is aware.
9. **Produce the final summary.** Use `templates/final-summary-template.md`. Include: package name, objective, domain, agents created, skills created, workflow phases, file structure, assumptions, limitations, validation status, usage instructions.
10. **Produce the user-facing summary.** Concise document with all 7 required elements:
    1. Folder path created.
    2. Files created (count + list).
    3. Purpose of the package.
    4. How to invoke.
    5. Assumptions made.
    6. Files skipped (if any).
    7. Recommended next step.

## Output Format

### Final Summary (follows template)

```
# Final Summary: <package name>

## Package Name
<name>

## Objective
<objective>

## Domain
<domain>

## Agents Created
<list with roles>

## Skills Created
<list with purposes>

## Workflow Phases
<list>

## File Structure
<file tree>

## Assumptions
<all labelled assumptions>

## Limitations
<known limitations>

## Validation Status
- QC: PASS
- Red-Team: PASS (with <N> optional issues documented)

## Usage Instructions
<how to use the package>

## Optional Issues (from red-team)
<list, if any>
```

### User-Facing Summary

```
# Workflow Package Created

## Folder Path
<path>

## Files Created
<N> files created:
- <file list>

## Purpose
<one paragraph>

## How To Invoke
<step-by-step>

## Assumptions Made
<list>

## Files Skipped
<none / list with reason>

## Recommended Next Step
<specific action to test the package>
```

## Validation Criteria

- [ ] All files from `package-output-spec.md` present.
- [ ] All agent files have 10 populated sections.
- [ ] All skill files have 8 populated sections.
- [ ] Assumptions documented in package README.
- [ ] Limitations documented in package README.
- [ ] Source notes preserved.
- [ ] Package is self-contained.
- [ ] Final summary follows the template.
- [ ] User-facing summary has all 7 required elements.
- [ ] Optional red-team issues documented.

## Common Mistakes

- **Finalizing with missing files**: not blocking when a file is missing.
- **Missing sections**: not verifying all 10/8 sections are populated.
- **Omitting assumptions or limitations**: these are required in the README.
- **Stripping source notes**: losing citations during packaging.
- **Verbose user-facing summary**: writing a wall of text instead of a concise summary.
- **No usage instructions**: the user-facing summary must tell the user how to invoke the workflow.
- **Finalizing before gates pass**: QC and red-team must both pass before packaging.

## Example Usage

**Input:**
```
Package: website-revamp-workflow
QC: PASS
Red-Team: PASS (2 optional issues)
Files: 25 files on disk
```

**Output (user-facing summary excerpt):**
```
# Workflow Package Created

## Folder Path
agent-packages/website-revamp-workflow/

## Files Created
25 files created:
- README.md, AGENTS.md, workflow.md, intake.md, research-protocol.md, quality-control.md, red-team-review.md
- agents/: content-auditor.md, ia-architect.md, visual-designer.md, seo-specialist.md, accessibility-auditor.md, frontend-engineer.md, qa-tester.md
- skills/: content-audit.md, ia-mapping.md, visual-system-design.md, seo-analysis.md, accessibility-validation.md, regression-testing.md
- prompts/: master-prompt.md, website-revamp-example.md
- templates/: (18 template files)
- examples/: marketing-site-revamp.md

## Purpose
A workflow package for revamping marketing websites with improved SEO and accessibility. Contains 7 specialized agents, 6 reusable skills, and a 10-phase workflow from intake to launch.

## How To Invoke
1. Open prompts/master-prompt.md
2. Fill in {{PROJECT_OBJECTIVE}} with your website revamp goal
3. Paste into an agent session
4. Review the generated output

## Assumptions Made
- [ASSUMPTION] Target WCAG 2.1 Level AA (user did not specify conformance level)
- [ASSUMPTION] Framework: tool-agnostic (user did not specify a frontend framework)

## Files Skipped
None

## Recommended Next Step
Test the package by invoking it on a real website revamp project. Verify the content-auditor agent produces a usable content audit report and the accessibility-auditor targets WCAG 2.1 AA correctly.
```