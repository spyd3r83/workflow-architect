# Subagent Dispatch Protocol

This file defines how the orchestrator dispatches work to subagents across all supported platforms. Every generated workflow package must include a `dispatch-protocol.md` that follows this specification, adapted to the package's specific agent roster and phase sequence.

## Design Principle

The orchestrator is the only agent that communicates with the user. All other agents receive work through structured dispatch calls — not prose "delegate to" descriptions. The dispatch call includes:

1. **Target agent** — which subagent to invoke.
2. **Phase number** — which workflow phase this dispatch belongs to.
3. **Deliverable** — what the subagent must produce.
4. **Context** — intake document, research summaries, prior phase outputs.
5. **Validation criteria** — what constitutes a passing deliverable.

The subagent returns its output to the orchestrator. The orchestrator validates the output before proceeding to the next phase.

## Platform Dispatch Mechanisms

### OpenCode (with Oh My OpenAgent)

OpenCode provides two dispatch tools. The orchestrator selects based on the target agent type:

#### `task()` — Custom Subagent Dispatch

Use `task()` for agents registered in `opencode.json` as `mode: subagent`. These are the package's own specialized agents (e.g., `intake-analyst`, `domain-researcher`, `quality-reviewer`).

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `description` | Yes | Short label (3-5 words) for the dispatch |
| `prompt` | Yes | Full prompt including phase, deliverable, context, validation criteria |
| `subagent_type` | Yes | Agent name matching `opencode.json` registration |
| `task_id` | No | Optional ID for tracking/resumption |

**Example — Dispatching to intake-analyst:**

```
task(
  description="Phase 1-3: Intake and classification",
  prompt="""
You are the intake-analyst. Execute Phases 1, 1.5, 2, and 3 of the workflow.

## Phase 1: Intake
- Project objective: {{OBJECTIVE}}
- User-provided context: {{CONTEXT}}
- Produce an intake document using templates/intake-template.md
- Label all missing fields as [ASSUMPTION] with risk classification

## Phase 1.5: Requirements Formalization
- Derive formal requirements (REQ-XXX) with acceptance criteria
- Trace each requirement to a deliverable

## Phase 2: Objective Clarification
- Refine the objective into a precise 1-2 sentence statement
- Define scope boundaries

## Phase 3: Domain Classification
- Classify the domain with confidence score
- Identify domain-specific risks

## Validation Criteria
- All 11 intake fields addressed
- No more than 5 clarifying questions
- Every assumption labelled with reasoning and confidence
- Requirements have unique IDs and measurable acceptance criteria
- Domain is classified with risks identified

## Context
- Workflow definition: workflow.md
- Intake model: intake.md
- Requirements template: templates/requirements-template.md

Return: intake document, requirements.md, domain classification, open questions list
""",
  subagent_type="intake-analyst"
)
```

**Example — Dispatching to quality-reviewer:**

```
task(
  description="Phase 11: Internal QA",
  prompt="""
You are the quality-reviewer. Execute Phase 11 of the workflow.

## Deliverable
Run the QC checklist from quality-control.md against the draft package at {{PACKAGE_PATH}}.

## Context
- Draft package location: {{PACKAGE_PATH}}
- QC checklist: quality-control.md
- validate-package.py has already been run and passed

## Validation Criteria
- All 15 quantitative criteria evaluated with numeric thresholds
- Every fail item has a required fix
- Report is structured (not narrative)
- If any item fails, list mandatory fixes for revision loop

Return: QC report with pass/fail per criterion, evidence, and required fixes
""",
  subagent_type="quality-reviewer"
)
```

#### `call_omo_agent()` — OMO Built-in Agent Dispatch

Use `call_omo_agent()` for OMO's built-in high-reasoning agents. These are not custom agents — they are platform-provided specialists available in any OMO environment.

**Available agents:**

| Agent | Use Case |
|-------|----------|
| `oracle` | High-reasoning independent review at Oracle gates |
| `explore` | Codebase exploration, file discovery, structure mapping |
| `librarian` | External research, documentation lookup, best practices |
| `hephaestus` | File creation, code generation, artifact building |
| `metis` | Strategic planning, decision analysis |
| `momus` | Critique, quality assessment, adversarial review |
| `multimodal-looker` | Visual analysis, screenshot review, UI inspection |

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `description` | Yes | Short label (3-5 words) |
| `prompt` | Yes | Full prompt with context and expected output |
| `subagent_type` | Yes | One of the 7 allowed agent names |
| `run_in_background` | Yes | `true` for async, `false` for sync (sync recommended for gate reviews) |
| `session_id` | No | Existing session ID to continue prior context |

**Example — Oracle Gate Review:**

```
call_omo_agent(
  description="Oracle gate: requirements review",
  prompt="""
You are the Oracle — a high-reasoning independent consultant. Review the following requirements for completeness, correctness, and risk.

## Requirements Document
{{REQUIREMENTS_CONTENT}}

## Intake Assumptions
{{ASSUMPTIONS_CONTENT}}

## What Oracle Must Confirm
1. Are the requirements correct and complete relative to the objective?
2. Are high/critical assumptions properly identified?
3. Should any high/critical assumptions be retired (verified) before proceeding?
4. Are there missing requirements that should be added?

## Output Format
- VERDICT: APPROVED / APPROVED_WITH_CONDITIONS / REJECTED
- CONDITIONS: (if applicable) list of conditions that must be met
- RATIONALE: explanation of the verdict
- MISSING_REQUIREMENTS: (if any) requirements that should be added
""",
  subagent_type="oracle",
  run_in_background=false
)
```

**Example — Explore for Codebase Discovery:**

```
call_omo_agent(
  description="Explore target repo structure",
  prompt="""
Explore the repository at {{REPO_PATH}}. Map:
1. Package/directory structure (top 3 levels)
2. Key configuration files (package.json, tsconfig, AGENTS.md, etc.)
3. Test infrastructure (test runner, test file patterns)
4. Build system and scripts
5. Dependency graph between packages (if monorepo)

Return a structured report with file paths and observations. Tag all claims as [VERIFIED] (inspected) or [ASSUMPTION] (inferred).
""",
  subagent_type="explore",
  run_in_background=true
)
```

**Example — Librarian for External Research:**

```
call_omo_agent(
  description="Research domain best practices",
  prompt="""
Research current best practices for {{DOMAIN}}. Focus on:
1. Industry standards and specifications
2. Tool/framework documentation and version requirements
3. Known pitfalls and anti-patterns
4. Security considerations
5. Compliance requirements (if any)

For each claim, provide: [Source: title, author/org, date or version, URL]
Tag each claim as [VERIFIED] (sourced) or [ASSUMPTION] (inferred).
Flag time-sensitive claims with the research date.
""",
  subagent_type="librarian",
  run_in_background=true
)
```

### Claude Code

Claude Code uses `@agent_name` mentions for interactive dispatch and the Task tool for programmatic dispatch.

**Interactive dispatch:**
```
@intake-analyst Please execute Phases 1-3 for the following objective: {{OBJECTIVE}}...
```

**Programmatic dispatch (Task tool):**
```
Task(
  description="Phase 1-3: Intake and classification",
  prompt="You are the intake-analyst. ...",
  agent="intake-analyst"
)
```

For Oracle-equivalent review, Claude Code uses a subagent with `model: opus` or equivalent high-reasoning model.

### Codex CLI

Codex CLI operates as a single agent. There is no subagent dispatch mechanism. The orchestrator performs all phases itself, following the agent definitions as role-specific instructions rather than separate agent invocations.

**Pattern:** The orchestrator reads each agent definition file, adopts that agent's role and constraints for the duration of the phase, produces the deliverable, then switches to the next role.

### Copilot CLI

Copilot CLI uses `@agent_name` mentions for dispatch, similar to Claude Code.

**Dispatch pattern:**
```
@quality-reviewer Please run the QC checklist against the draft package at {{PACKAGE_PATH}}...
```

### Devin

Devin uses playbook references. Each agent is a playbook file (`.devin.md`). The orchestrator references the playbook by name.

**Dispatch pattern:**
```
Run the intake-analyst playbook with the following context:
- Objective: {{OBJECTIVE}}
- Context: {{CONTEXT}}
```

## Dispatch Table

The orchestrator uses this table to determine which tool and agent to use for each phase. Generated packages must include their own dispatch table mapping their phases to their agents.

### Meta-Package Dispatch Table

| Phase | Agent | Tool | Subagent Type |
|-------|-------|------|----------------|
| 1 | intake-analyst | `task()` | `intake-analyst` |
| 1.5 | intake-analyst | `task()` | `intake-analyst` |
| 1.5 Oracle Gate | oracle | `call_omo_agent()` | `oracle` |
| 2 | intake-analyst | `task()` | `intake-analyst` |
| 3 | intake-analyst | `task()` | `intake-analyst` |
| 3 Oracle Gate | oracle | `call_omo_agent()` | `oracle` |
| 4 | domain-researcher | `task()` | `domain-researcher` |
| 4 (exploration) | explore | `call_omo_agent()` | `explore` |
| 5 | domain-researcher | `task()` | `domain-researcher` |
| 5 (research) | librarian | `call_omo_agent()` | `librarian` |
| 6 | workflow-architect | `task()` | `workflow-architect` |
| 7 | skill-architect | `task()` | `skill-architect` |
| 8 | skill-architect | `task()` | `skill-architect` |
| 9 | implementation-planner | `task()` | `implementation-planner` |
| 9 (file creation) | hephaestus | `call_omo_agent()` | `hephaestus` |
| 10 | implementation-planner | `task()` | `implementation-planner` |
| 10 (file creation) | hephaestus | `call_omo_agent()` | `hephaestus` |
| 11 | quality-reviewer | `task()` | `quality-reviewer` |
| 11.5 | independent verifier | `task()` or `validate-package.py` | (external) |
| 12 | red-team-reviewer | `task()` | `red-team-reviewer` |
| 12 Oracle Gate | oracle | `call_omo_agent()` | `oracle` |
| 13 | workflow-orchestrator | (self) | (self) |
| 14 | final-packager | `task()` | `final-packager` |
| 15 | final-packager | `task()` | `final-packager` |

## Structured Handoff Format

Every dispatch call must include a structured handoff in the prompt. The format:

```
## Handoff
- Phase: <phase number>
- Deliverable: <what the subagent must produce>
- Context: <intake document, research summaries, prior phase outputs>
- Validation Criteria: <what constitutes a passing deliverable>
- Escalation Path: <what to do if the subagent cannot proceed>
```

## Background vs Synchronous Dispatch

| Mode | When to Use | Tool Parameter |
|------|-------------|----------------|
| Synchronous | Gate reviews (Oracle), sequential phases with dependencies | `run_in_background=false` (call_omo_agent) or default (task) |
| Background | Long-running research, codebase exploration, file creation | `run_in_background=true` (call_omo_agent) |

Synchronous is the default. Background is used only when:
1. The subagent's work is independent of the next phase.
2. The orchestrator has other work to do while waiting.
3. The result will be collected via `background_output`.

## Dispatch Validation

After each dispatch returns, the orchestrator must validate:

1. **Deliverable exists** — the expected output was produced.
2. **Validation criteria met** — all criteria from the workflow phase are satisfied.
3. **No unresolved placeholders** — no `{{...}}` patterns in the output.
4. **No broken cross-references** — all file references in the output resolve.
5. **Phase gate passed** — the phase's gate condition is met before proceeding.

If validation fails, the orchestrator routes the issues back to the subagent with specific fixes required. After 3 failed iterations on the same issue, the orchestrator escalates to the user.

## Platform-Specific Notes

### OpenCode Without OMO

If running in OpenCode without the OMO plugin, `call_omo_agent()` is not available. In this case:
- Oracle gates: the orchestrator performs a self-review with a different prompt and notes the reduced independence.
- Exploration: the orchestrator uses `Read`, `Glob`, and `Grep` tools directly.
- Research: the orchestrator uses `websearch` or `webfetch` tools directly.
- File creation: the orchestrator uses `Write` tool directly.

### Multi-Model Independence (Phase 11.5)

For independent verification, the orchestrator must use a different model than the one used for creation and QC. Options:
1. Dispatch to a subagent configured with a different model in `opencode.json`.
2. Run `validate-package.py` as the deterministic independent verifier.
3. Use `call_omo_agent()` with `subagent_type="momus"` (critique agent) as an independent reviewer.

Option 2 is preferred — deterministic verification has no model bias.
