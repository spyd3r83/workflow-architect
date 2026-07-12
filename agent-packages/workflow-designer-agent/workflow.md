# Workflow — Workflow Designer Agent

This file defines the end-to-end workflow that the Workflow Designer Agent executes to produce a complete workflow package. The orchestrator manages phase progression. No phase begins until the prior phase passes its validation criteria.

## Subagent Dispatch

The orchestrator dispatches work to subagents using tool calls, not prose descriptions. See `dispatch-protocol.md` for the full specification including tool signatures, examples, and platform fallbacks.

**Two dispatch tools:**

- **`task()`** — for custom subagents registered in `opencode.json` (intake-analyst, domain-researcher, workflow-architect, skill-architect, implementation-planner, quality-reviewer, red-team-reviewer, final-packager). Parameters: `description`, `prompt`, `subagent_type`, `task_id` (optional). Synchronous.
- **`call_omo_agent()`** — for OMO built-in agents (oracle, explore, librarian, hephaestus, momus). Parameters: `description`, `prompt`, `subagent_type`, `run_in_background` (required), `session_id` (optional).

**Dispatch table** (full version in `dispatch-protocol.md`):

| Phase | Tool | Agent | Purpose |
|-------|------|-------|---------|
| 1-3 | `task()` | `intake-analyst` | Intake, requirements, domain |
| 1.5 gate | `call_omo_agent()` | `oracle` | Requirements confirmation |
| 3 gate | `call_omo_agent()` | `oracle` | Domain confirmation |
| 4 | `task()` | `domain-researcher` | Source review |
| 5 | `task()` | `domain-researcher` | External research |
| 6 | `task()` | `workflow-architect` | Workflow decomposition |
| 7-8 | `task()` | `skill-architect` | Agent/skill design |
| 9-10 | `task()` | `implementation-planner` | File structure, draft |
| 11 | `task()` | `quality-reviewer` | Internal QA |
| 11.5 | `validate-package.py` | (deterministic) | Independent verification |
| 12 | `task()` | `red-team-reviewer` | Adversarial review |
| 12 gate | `call_omo_agent()` | `oracle` | Pre-finalization |
| 14-15 | `task()` | `final-packager` | Final packaging |

**Structured handoff format** (included in every dispatch prompt):

```
## Handoff
- Phase: <phase number>
- Deliverable: <what the subagent must produce>
- Context: <prior phase outputs, intake, research>
- Validation Criteria: <what constitutes a passing deliverable>
- Escalation Path: <what to do if the subagent cannot proceed>
```

## Reliability Mechanisms

This workflow implements space-level reliability controls:

- **Phase 1.5**: Requirements formalization with IDs and acceptance criteria
- **Phase 11.5**: Independent verification (different model or deterministic script)
- **Oracle-in-the-loop gates**: At requirements baseline (after Phase 1.5), domain confirmation (after Phase 3), and pre-finalization (after Phase 12). Oracle is a high-reasoning independent consultant that reviews and confirms before the workflow proceeds.
- **Idempotency protocol**: temperature=0, pinned model, fixed seed, deterministic file ordering
- **Rollback protocol**: Every draft versioned; failed post-delivery validation triggers rollback
- **FMEA**: Failure modes tracked in `fmea.md` with RPN scoring and mitigations
- **Traceability matrix**: Every requirement traced to deliverable and verification method
- **Source chain-of-custody**: Every citation has a retrieval ID in `source-log.md`
- **Deterministic validation**: `validate-package.py` runs mechanically before and after QC

## Phase Overview

| # | Phase | Responsible Agent | Gate |
|---|-------|-------------------|------|
| 1 | Intake | intake-analyst | Intake document accepted by orchestrator |
| 1.5 | Requirements formalization | intake-analyst | Requirements document accepted; **Oracle gate** |
| 2 | Objective clarification | intake-analyst | Objective statement confirmed |
| 3 | Domain classification | intake-analyst | Domain labelled with confidence; **Oracle gate** |
| 4 | Source-material review | domain-researcher | Source inventory produced |
| 5 | External research | domain-researcher | Research summary with citations + source-log produced |
| 6 | Workflow decomposition | workflow-architect | Workstreams identified and documented |
| 7 | Agent design | skill-architect (agent-design skill) | Agent files drafted |
| 8 | Skill design | skill-architect | Skill files drafted |
| 9 | Folder/file structure generation | implementation-planner | File tree produced |
| 10 | Draft package creation | implementation-planner | All files written to disk; validate-package.py run |
| 11 | Internal QA | quality-reviewer | QC checklist passed (quantitative criteria) |
| 11.5 | Independent verification | independent verifier | Independent verification passed |
| 12 | Red-team review | red-team-reviewer | Red-team pass recommendation; **Oracle gate** |
| 13 | Revision loop | workflow-orchestrator | All mandatory issues resolved |
| 14 | Final packaging | final-packager | Final package assembled + summary; validate-package.py re-run |
| 15 | User-facing summary | final-packager | Summary delivered to user |

---

## Phase 1: Intake

| Field | Value |
|-------|-------|
| **Purpose** | Capture the project objective and all available context from the user. |
| **Inputs** | User's project objective (required). Optional: domain, constraints, source materials, success criteria. |
| **Outputs** | Intake document following `intake.md` model. Includes labelled assumptions for missing fields. |
| **Responsible Agent** | intake-analyst |
| **Validation Criteria** | (1) Intake document exists. (2) All 11 intake fields addressed (filled or labelled as assumption). (3) Objective is a single clear statement. (4) No more than 5 clarifying questions asked to the user. (5) Every assumption has risk classification (low/medium/high/critical). |

## Phase 1.5: Requirements Formalization

| Field | Value |
|-------|-------|
| **Purpose** | Derive formal requirements from the intake document with unique IDs, acceptance criteria, and priority. Prevents building on unverified foundations. |
| **Inputs** | Intake document from Phase 1. |
| **Outputs** | `requirements.md` with: requirement IDs (REQ-XXX), type, priority, source, description, measurable acceptance criteria, traced deliverable. |
| **Responsible Agent** | intake-analyst |
| **Validation Criteria** | (1) requirements.md exists. (2) Every requirement has unique ID. (3) Acceptance criteria are measurable. (4) Every requirement traces to a deliverable. (5) Coverage check passes (every objective component covered). (6) **Oracle gate: Oracle reviews and confirms requirements before proceeding.** |
| **Oracle Gate** | Oracle (high-reasoning independent consultant) reviews and confirms requirements. High/critical assumptions must be retired (verified) or formally accepted by Oracle before this gate passes. Oracle's review is independent from the intake-analyst. |

## Phase 2: Objective Clarification

| Field | Value |
|-------|-------|
| **Purpose** | Refine the objective into a precise, actionable statement that drives the rest of the workflow. |
| **Inputs** | Intake document from Phase 1. |
| **Outputs** | Confirmed objective statement (1-2 sentences). Scope boundaries (what is in scope, what is out of scope). |
| **Responsible Agent** | intake-analyst |
| **Validation Criteria** | (1) Objective is specific enough to determine agents and skills. (2) Scope boundaries are explicit. (3) Objective is confirmed by the orchestrator (or user if escalation occurred). |

## Phase 3: Domain Classification

| Field | Value |
|-------|-------|
| **Purpose** | Identify the project domain to drive research and agent specialization. |
| **Inputs** | Refined objective from Phase 2. |
| **Outputs** | Domain label (e.g., web, mobile-app, security, legal, compliance, marketing, research, documentation, business-ops). Sub-domain if applicable. Domain-specific risk factors identified. |
| **Responsible Agent** | intake-analyst |
| **Validation Criteria** | (1) Domain is labelled. (2) Domain-specific risks are listed. (3) Domain matches one of the supported domains or is explicitly marked as novel with a research plan. |

## Phase 4: Source-Material Review

| Field | Value |
|-------|-------|
| **Purpose** | Inventory and assess any source materials the user provided. |
| **Inputs** | User-provided source materials (documents, specs, code, links). Intake document. |
| **Outputs** | Source inventory: list of materials, type, relevance, freshness, authority level. |
| **Responsible Agent** | domain-researcher |
| **Validation Criteria** | (1) Every provided material is inventoried. (2) Each material has a relevance note. (3) Stale or low-authority materials are flagged. (4) If no materials provided, this is recorded as an assumption. |

## Phase 5: External Research

| Field | Value |
|-------|-------|
| **Purpose** | Gather source-backed information needed to design an accurate, domain-appropriate workflow. |
| **Inputs** | Domain from Phase 3. Source inventory from Phase 4. Objective from Phase 2. |
| **Outputs** | Research summary with citations. Every claim tagged `[VERIFIED]` or `[ASSUMPTION]`. Conflicts documented. Time-sensitive claims flagged with research date. |
| **Responsible Agent** | domain-researcher |
| **Validation Criteria** | (1) Research summary exists. (2) All factual claims have source tags. (3) No hallucinated sources. (4) Research covers domain-specific standards, best practices, and risks. (5) Summary is reusable by downstream agents (structured, not narrative). |

## Phase 6: Workflow Decomposition

| Field | Value |
|-------|-------|
| **Purpose** | Break the objective into actionable workstreams that will become workflow phases. |
| **Inputs** | Refined objective. Research summary. Domain classification. |
| **Outputs** | List of workstreams. Each workstream has: name, purpose, dependencies, expected deliverable. |
| **Responsible Agent** | workflow-architect |
| **Validation Criteria** | (1) Workstreams cover the full objective. (2) Dependencies are explicit. (3) No workstream is vague (each has a concrete deliverable). (4) Workstreams are ordered logically. |

## Phase 7: Agent Design

| Field | Value |
|-------|-------|
| **Purpose** | Design specialized agents for the workflow. |
| **Inputs** | Workstreams from Phase 6. Research summary. Agent file template (`templates/agent-file-template.md`). |
| **Outputs** | Agent definition files, one per agent. Each file has all 10 required sections (role, mission, responsibilities, required inputs, expected outputs, operating rules, decision criteria, escalation rules, quality checklist, failure modes to avoid). |
| **Responsible Agent** | skill-architect (using agent-design skill) |
| **Validation Criteria** | (1) Every workstream has at least one responsible agent. (2) Every agent file has all 10 sections. (3) No agent description is vague. (4) Agent roles do not overlap (each has a distinct purpose). (5) Handoffs between agents are explicit. |

## Phase 8: Skill Design

| Field | Value |
|-------|-------|
| **Purpose** | Design reusable skills required by the agents. |
| **Inputs** | Agent files from Phase 7. Research summary. Skill file template (`templates/skill-file-template.md`). |
| **Outputs** | Skill definition files, one per skill. Each file has all 8 required sections (purpose, when to use, required inputs, process, output format, validation criteria, common mistakes, example usage). |
| **Responsible Agent** | skill-architect |
| **Validation Criteria** | (1) Every agent responsibility that requires a reusable capability has a corresponding skill. (2) Every skill file has all 8 sections. (3) Skills are reusable (not hardcoded to one project). (4) No skill duplicates another skill's purpose. (5) Each skill has a concrete example usage. |

## Phase 9: Folder/File Structure Generation

| Field | Value |
|-------|-------|
| **Purpose** | Map the workflow design to a concrete, repo-ready folder and file structure. |
| **Inputs** | Agent files. Skill files. Workstream list. `package-output-spec.md`. |
| **Outputs** | File tree showing all files to be created, with one-line descriptions. |
| **Responsible Agent** | implementation-planner |
| **Validation Criteria** | (1) File tree matches `package-output-spec.md` structure. (2) Every file has a description. (3) No file is orphaned. (4) Structure follows project conventions if stated during intake. (5) **File tree includes slash commands** (commands/ + platform command dirs + Devin playbooks). (6) **File tree includes platform config** (opencode.json, CLAUDE.md). (7) **File tree includes command templates** (command-flowstart-template.md, command-resume-template.md, command-maintain-template.md, platform-config-template.md). |

## Phase 10: Draft Package Creation

| Field | Value |
|-------|-------|
| **Purpose** | Write all files to disk as a draft package, including slash commands and platform config. Then run `sync-platform-configs.py` to populate platform-native directories. |
| **Inputs** | File tree from Phase 9. Agent definitions. Skill definitions. Research summary. Templates. Command templates. |
| **Outputs** | Complete draft package on disk with all files populated, including: (a) all content files, (b) slash command files for all 5 platforms, (c) opencode.json with agent registration, (d) CLAUDE.md importing AGENTS.md, (e) platform-specific agent/skill files in `.opencode/agents/`, `.claude/agents/`, `.codex/agents/`, `.github/agents/`, `.devin/agents/`, `.agents/skills/`, (f) platform command files in `.opencode/commands/`, `.claude/commands/`, `.codex/commands/`, `.github/commands/`, (g) Devin playbooks (`.devin.md`). |
| **Responsible Agent** | implementation-planner |
| **Validation Criteria** | (1) All files from the file tree exist on disk. (2) No file is empty or a placeholder. (3) All files follow their respective templates. (4) Cross-references between files are valid. (5) **Slash commands exist for all 5 platforms** (`.opencode/commands/`, `.claude/commands/`, `.codex/commands/`, `.github/commands/`, `*.devin.md`). (6) **opencode.json registers the primary agent** as `default_agent` with all subagents as `mode: subagent`. (7) **CLAUDE.md imports AGENTS.md**. (8) **Command files have no unresolved placeholders**. (9) **Platform agent files exist** in `.opencode/agents/`, `.claude/agents/`, `.codex/agents/`, `.github/agents/`, `.devin/agents/`. (10) **Platform skill files exist** in `.agents/skills/<name>/SKILL.md`. (11) **`sync-platform-configs.py --package <path>` has been run** to populate all platform directories. |

## Phase 11: Internal QA

| Field | Value |
|-------|-------|
| **Purpose** | Check the draft package for correctness, completeness, consistency, and implementation readiness. |
| **Inputs** | Draft package from Phase 10. QC checklist from `quality-control.md`. |
| **Outputs** | QC report: item, status (pass/fail), evidence, required fix. |
| **Responsible Agent** | quality-reviewer |
| **Validation Criteria** | (1) All QC checklist items evaluated using quantitative thresholds. (2) `validate-package.py` passed before LLM-based QC. (3) Every fail item has a required fix. (4) Report is structured (not narrative). (5) If any item fails, proceed to Phase 13 (revision loop). |

## Phase 11.5: Independent Verification

| Field | Value |
|-------|-------|
| **Purpose** | Break the same-model self-review blind spot. Verify the package using a different model, provider, or deterministic script that did not create the draft and did not see QC results. |
| **Inputs** | Draft package from Phase 10 (with passing QC from Phase 11). |
| **Outputs** | Independent verification report: item, status, evidence, discrepancies vs QC. |
| **Responsible Agent** | Independent verifier (different model or `validate-package.py`) |
| **Validation Criteria** | (1) Verifier is structurally independent from the creator and QC agents. (2) Verifier does not see QC results (no anchoring). (3) All structural checks pass (files, sections, cross-references, placeholders, citations). (4) Discrepancies between QC and independent verification are documented. (5) If independent verification fails, proceed to Phase 13. |
| **Independence Rule** | The verifier must be either (a) a different LLM model/provider than the one used for creation and QC, or (b) a deterministic script (`validate-package.py`). Using the same model with a different prompt is NOT independent. |

## Phase 12: Red-Team Review

| Field | Value |
|-------|-------|
| **Purpose** | Adversarially challenge the package from multiple stakeholder perspectives. |
| **Inputs** | Draft package. QC report (must show all items passing). Red-team review process from `red-team-review.md`. |
| **Outputs** | Red-team report: issues found, severity, recommended fix, mandatory/optional, final pass/fail recommendation. |
| **Responsible Agent** | red-team-reviewer |
| **Validation Criteria** | (1) Review covers all required perspectives (critic, client, developer, auditor, user, opposing stakeholder). (2) Every issue has severity and fix recommendation. (3) Critical/high issues are marked mandatory. (4) Final recommendation is pass or fail. (5) If fail, proceed to Phase 13. |

## Phase 13: Revision Loop

| Field | Value |
|-------|-------|
| **Purpose** | Fix all mandatory issues from QC and/or red-team. Re-validate. |
| **Inputs** | QC report and/or red-team report with mandatory issues. Draft package. |
| **Outputs** | Revised package. Updated QC and/or red-team reports. |
| **Responsible Agent** | workflow-orchestrator (coordinates fixes across agents) |
| **Validation Criteria** | (1) All mandatory issues addressed. (2) Re-run QC (Phase 11) and red-team (Phase 12) on revised package. (3) If both pass, proceed to Phase 14. (4) If either fails twice on the same issue, escalate to user. (5) Maximum 3 revision iterations before escalation. |

## Phase 14: Final Packaging

| Field | Value |
|-------|-------|
| **Purpose** | Assemble the final, validated package and produce the implementation summary. |
| **Inputs** | Revised package with passing QC and red-team. `templates/final-summary-template.md`. |
| **Outputs** | Final package on disk. Final summary document. |
| **Responsible Agent** | final-packager |
| **Validation Criteria** | (1) All files present per `package-output-spec.md`. (2) Final summary follows the template. (3) Assumptions and limitations documented. (4) Source notes preserved. (5) Package is self-contained. |

## Phase 15: User-Facing Summary

| Field | Value |
|-------|-------|
| **Purpose** | Deliver a concise summary to the user explaining what was created, where it lives, and how to use it. |
| **Inputs** | Final package. Final summary document. |
| **Outputs** | User-facing summary containing: (1) folder path, (2) files created, (3) purpose, (4) how to invoke, (5) assumptions made, (6) files skipped (if any), (7) recommended next step. |
| **Responsible Agent** | final-packager |
| **Validation Criteria** | (1) Summary contains all 7 required elements. (2) Summary is concise (not a wall of text). (3) Invocation instructions are actionable. (4) Limitations and assumptions are visible to the user. |

## Revision Loop Detail

The revision loop (Phase 13) is mandatory if either QC or red-team fails. The orchestrator:

1. Collects all mandatory issues from the failed report(s).
2. Routes each issue to the responsible agent for fixing.
3. Collects fixes.
4. Re-runs the failed gate(s).
5. If pass → proceed to Phase 14.
6. If fail → iterate (max 3 times).
7. If still failing after 3 iterations → escalate to user with the unresolved issues.

The first draft is never final. Skipping the revision loop when issues exist is a violation of these operating instructions.

### Escalation Report Requirements

When escalation occurs after 3 failed iterations, the escalation report must include:
1. Unresolved defect descriptions with severity.
2. Impact analysis: what happens if this defect ships.
3. Failed fix attempts: what was tried and why it did not work.
4. High/critical defects cannot be user-approved away — they must be fixed.

## Idempotency Protocol

To achieve deterministic output (same input → same output), the following parameters are mandatory:

| Parameter | Required Value |
|-----------|---------------|
| Model temperature | 0 |
| Model | Pinned (specific version, not "latest") |
| Seed | Fixed (if supported by model) |
| File generation order | Alphabetical by path |
| Phase execution | Sequential (no parallel phases in generation mode) |

The idempotency test (`tests/test_idempotency.py`) runs the workflow twice with the same input and compares outputs. Any difference is a failure that blocks finalization.

## Rollback Protocol

Every draft is versioned. If the final package fails post-delivery validation:

1. **Identify the last known good version** from the version log.
2. **Roll back** to that version.
3. **Document the failure**: what defect escaped, why, which gate missed it.
4. **Update FMEA**: add the new failure mode if not already tracked.
5. **Strengthen the gate** that missed the defect (add check, lower threshold, add test case).
6. **Re-run regression tests** to verify the fix does not break other outputs.

## Human-in-the-Loop Gates

Three planned Oracle gates exist in the workflow. These are not fallbacks — they are mandatory checkpoints where Oracle (a high-reasoning independent consultant) reviews and confirms before the workflow proceeds:

| Gate | Location | What Oracle Confirms |
|------|----------|----------------------|
| Requirements gate | After Phase 1.5 | Requirements are correct and complete; high/critical assumptions are accepted or retired |
| Domain gate | After Phase 3 | Domain classification is correct; domain-specific risks are acknowledged |
| Pre-finalization gate | After Phase 12 | Red-team issues are acceptable; package is ready for final packaging |

Skipping an Oracle gate is a violation. The orchestrator must pause and wait for Oracle confirmation before proceeding.