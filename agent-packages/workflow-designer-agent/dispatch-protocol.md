# Subagent Dispatch Protocol

This file defines how the orchestrator dispatches work to subagents across all supported platforms. Every generated workflow package must include a `dispatch-protocol.md` that follows this specification, adapted to the package's specific agent roster and phase sequence.

## Design Principle

**One delegation primitive: `task()`.**

The orchestrator is the only agent that communicates with the user. All other agents receive work through structured `task()` calls — not prose "delegate to" descriptions, and not `call_omo_agent()`.

Mixing invocation surfaces breaks session continuity and dispatch routing. `call_omo_agent()` is **forbidden** as a dispatch path in OpenCode workflow packages.

Every dispatch call includes:

1. **Target agent** — which subagent to invoke (`subagent_type` or `category`).
2. **Phase number** — which workflow phase this dispatch belongs to.
3. **Deliverable** — what the subagent must produce.
4. **Context** — intake document, research summaries, prior phase outputs.
5. **Validation criteria** — what constitutes a passing deliverable.

The subagent returns its output to the orchestrator. The orchestrator validates the output before proceeding to the next phase.

## Hard Rules

1. Use `task()` for **all** subagent dispatch — package agents and OMO specialists.
2. On OpenCode, never use `call_omo_agent()`. If `task()` is unavailable or not surfaced at runtime, report `TASK_DISPATCH_UNAVAILABLE` and stop.
3. Sequential dispatch only — wait for each `task()` to return before starting the next.
4. Prefer session reuse via `session_id` / `task_id` for follow-ups to the same specialist.
5. Structured prompts only — every worker prompt answers identity, scope, deliverable, context, validation, escalation.

## Platform Dispatch Mechanisms

### OpenCode (with Oh My OpenAgent)

#### `task()` — Sole Dispatch Primitive

Use `task()` for:

| Kind | Examples | How |
|------|----------|-----|
| Package subagents | `intake-analyst`, `domain-researcher`, `quality-reviewer`, `red-team-reviewer`, `final-packager` | `task(subagent_type="...")` |
| OMO specialists | `oracle`, `explore`, `librarian`, `hephaestus`, `metis`, `momus`, `multimodal-looker` | `task(subagent_type="...")` |
| Category workers (if used) | `qa-testing`, `implementation`, `quick` | `task(category="...")` |

**Parameters (OpenCode / OMO task tool):**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `description` | Yes | Short label (3-5 words) for the dispatch |
| `prompt` | Yes | Full prompt including phase, deliverable, context, validation criteria |
| `subagent_type` | Conditional | Agent name (package agent or OMO specialist). Use when targeting a named agent |
| `category` | Conditional | Worker category route. If both `category` and `subagent_type` are set, category wins |
| `run_in_background` | When required by runtime | `false` for gates and sequential dependencies; `true` for independent long research |
| `session_id` / `task_id` | No | Reuse prior subagent session for follow-ups |
| `load_skills` | When required by runtime | Skills to inject (use `[]` if none) |

**Example — Package agent (intake-analyst):**

```
task(
  description="Phase 1-3: Intake and classification",
  prompt="""
You are the intake-analyst. Execute Phases 1, 1.5, 2, and 3 of the workflow.

## Deliverable
Intake document, requirements.md, domain classification, open questions.

## Context
- Objective: {{OBJECTIVE}}
- User context: {{CONTEXT}}
- Templates: templates/intake-template.md, templates/requirements-template.md

## Validation Criteria
- All intake fields addressed
- Assumptions labelled with reasoning and confidence
- Requirements have unique IDs and measurable acceptance criteria

## Escalation
If inputs are insufficient, return open questions rather than inventing facts.

Return: intake document, requirements.md, domain classification
""",
  subagent_type="intake-analyst",
  run_in_background=false,
  load_skills=[]
)
```

**Example — Oracle gate (specialist via task):**

```
task(
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
3. Should any high/critical assumptions be retired before proceeding?
4. Are there missing requirements that should be added?

## Output Format
- VERDICT: APPROVED / APPROVED_WITH_CONDITIONS / REJECTED
- CONDITIONS: (if applicable)
- RATIONALE: explanation
- MISSING_REQUIREMENTS: (if any)
""",
  subagent_type="oracle",
  run_in_background=false,
  load_skills=[]
)
```

**Example — Explore (specialist via task):**

```
task(
  description="Explore target repo structure",
  prompt="""
Explore the repository at {{REPO_PATH}}. Map:
1. Package/directory structure (top 3 levels)
2. Key configuration files
3. Test infrastructure
4. Build system and scripts
5. Dependency graph between packages (if monorepo)

Return a structured report. Tag claims as [VERIFIED] or [ASSUMPTION].
""",
  subagent_type="explore",
  run_in_background=true,
  load_skills=[]
)
```

**Example — Librarian (specialist via task):**

```
task(
  description="Research domain best practices",
  prompt="""
Research current best practices for {{DOMAIN}}. Focus on:
1. Industry standards and specifications
2. Tool/framework documentation and version requirements
3. Known pitfalls and anti-patterns
4. Security considerations

For each claim: [Source: title, author/org, date or version, URL]
Tag claims as [VERIFIED] or [ASSUMPTION].
""",
  subagent_type="librarian",
  run_in_background=true,
  load_skills=[]
)
```

### Claude Code

Use `@agent_name` mentions or the Task tool:

```
Task(
  description="Phase 1-3: Intake and classification",
  prompt="You are the intake-analyst. ...",
  agent="intake-analyst"
)
```

### Codex CLI

Single-agent mode: the orchestrator adopts each agent role in sequence. No subagent tool.

### Copilot CLI

Use `@agent_name` mentions.

### Devin

Use playbook references (`.devin.md`).

## Meta-Package Dispatch Table

| Phase | Subagent Type | Purpose | Background |
|-------|---------------|---------|------------|
| 1-3 | `intake-analyst` | Intake, requirements, objective, domain | false |
| 1.5 gate | `oracle` | Requirements confirmation | false |
| 3 gate | `oracle` | Domain confirmation | false |
| 4 | `domain-researcher` | Source-material review | false |
| 4 (explore) | `explore` | Codebase/file exploration | true |
| 5 | `domain-researcher` | External research | false |
| 5 (research) | `librarian` | External research lookup | true |
| 6 | `workflow-architect` | Workflow decomposition | false |
| 7-8 | `skill-architect` | Agent and skill design | false |
| 9-10 | `implementation-planner` | File structure and draft creation | false |
| 9-10 (files) | `hephaestus` | Bulk file creation | true |
| 11 | `quality-reviewer` | Internal QA | false |
| 11.5 | `momus` or `validate-package.py` | Independent verification | false |
| 12 | `red-team-reviewer` | Adversarial review | false |
| 12 gate | `oracle` | Pre-finalization confirmation | false |
| 14-15 | `final-packager` | Final packaging and summary | false |

All rows use `task(subagent_type=...)` except deterministic scripts (`validate-package.py`).

## Structured Handoff Format

Every dispatch prompt must include:

```
## Handoff
- Phase: <phase number>
- Deliverable: <what the subagent must produce>
- Context: <prior phase outputs, intake, research>
- Validation Criteria: <what constitutes a passing deliverable>
- Escalation Path: <what to do if the subagent cannot proceed>
```

## Background vs Synchronous

| Mode | When | Parameter |
|------|------|-----------|
| Synchronous | Gate reviews (Oracle), sequential dependent phases | `run_in_background=false` |
| Background | Independent long research/exploration | `run_in_background=true` |

Default to synchronous. Background only when work is independent of the next phase.

## Post-Dispatch Validation

After each `task()` returns, the orchestrator validates:

1. **Deliverable exists**
2. **Validation criteria met**
3. **No unresolved placeholders**
4. **No broken cross-references**
5. **Phase gate condition met** before proceeding

If validation fails, re-dispatch with specific fixes. After 3 failed iterations on the same issue, escalate to the user.

## Preflight Check

Before any dispatch, the orchestrator or package startup runs `scripts/preflight-task-check.sh`. The script distinguishes static registration, live-server registration, agent permission, enforcer state, and a real per-session tool call:

- **PASS**: A real `task()` call succeeded and its session/message identifier was supplied as runtime-probe evidence. Proceed normally.
- **UNKNOWN**: Static/configuration checks found no blocker, but no real call has been proved. Attempt one `task(subagent_type=...)` call and retain the returned session/message identifier. Registration alone is not proof.
- **FAIL**: Agent permission denies a required target, a probed live server does not register `task`, the enforcer permits `call_omo_agent`, or the real `task()` call failed. Report `TASK_DISPATCH_UNAVAILABLE` and stop. Do not switch dispatch surfaces.

`--server-url` (or `OPENCODE_SERVER_URL`) adds live server-registration evidence. A duplicate `task` ID is reported for diagnosis but is not itself a failure because OpenCode can expose a built-in and plugin implementation under the same name. Only a real call proves which implementation the current session can use.

## Fallbacks

### When `task()` is unavailable

| Platform | Fallback |
|----------|----------|
| OpenCode | Stop with `TASK_DISPATCH_UNAVAILABLE`; fix runtime/tool surfacing. Do not fall back to `call_omo_agent()`. |
| Claude Code | `@agent_name` or Task tool |
| Codex CLI | Single-agent role adoption |
| Copilot CLI | `@agent_name` |
| Devin | Playbook reference |
| OpenCode without OMO specialists | Stop with `TASK_DISPATCH_UNAVAILABLE`; fix runtime/tool surfacing. |

## Enforcement

- Canonical docs must not present `call_omo_agent()` as an OpenCode dispatch option, including ambiguous "primary path" wording that implies a fallback.
- `validate-package.py` fails packages that authorize or imply any OpenCode `call_omo_agent()` fallback.
- Runtime enforcer blocks `call_omo_agent` tool calls and redirects to `task(subagent_type=...)`.
- `scripts/preflight-task-check.sh` parses real JSON/JSONC safely, evaluates required-target permissions, queries the live tool endpoint and effective agent permission (including `*` blanket rules and pattern ordering), verifies runtime evidence against the live server (child session exists, parentID matches, task-child metadata), and never treats registration as runtime proof.
- `test_dispatch_contract.py` exercises 29 cases: preflight existence/executability, verdict types (PASS/FAIL/UNKNOWN), preflight documentation, dispatch-protocol forbidden wording, enforcer blocks call_omo_agent, no Oracle allowlist, stale fallback wording (canonical + generated), JSONC safety with `//` inside strings, explicit deny detection, runtime-evidence gate (missing/fail/pass-without-evidence), and 15 mock-server negative cases (bogus evidence, wrong parent, missing live task, duplicate registration, enforcer-not-blocking, wildcard-then-deny ordering, narrow-allow-vs-global-deny, no-parent-supplied, verified-evidence PASS, provider/model exact match, wrong provider, wrong model, no assistant message, message endpoint unreachable, title-lacks-markers crash safety).
