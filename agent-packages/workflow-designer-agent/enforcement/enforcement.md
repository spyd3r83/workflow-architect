# Workflow Enforcement — Cross-Platform Plugin & Hooks

This package includes programmatic enforcement of the workflow process. The enforcement system ensures that:

1. **Phases execute in order** — no phase begins until the prior phase passes its gate
2. **Write tools are blocked** outside implementation phases until gates pass
3. **State survives context compaction** — workflow state is injected into compaction context
4. **Revision loops are tracked** — max 3 iterations before escalation

## Configuration

The enforcement system reads its configuration from `.opencode/workflow-config.json`:

```json
{
  "workflow_package": "<package-name>",
  "total_phases": 18,
  "implementation_phases": [9, 10],
  "write_tools": ["write", "edit", "bash", "str_replace_editor"],
  "max_revisions": 3
}
```

- `workflow_package` — name of the workflow package
- `total_phases` — number of phases in the workflow
- `implementation_phases` — phases where write tools are allowed while in progress
- `write_tools` — tool names that are blocked outside implementation phases
- `max_revisions` — revision loop limit before escalation

## State File

The enforcement system tracks workflow progression in `.opencode/workflow-state.json` (gitignored). This file is the single source of truth for which phase is current, which gates have passed/failed, and how many revision iterations have occurred.

## Enforcement Logic

| Current Phase | Write Tools | Read Tools |
|---------------|-------------|------------|
| Pre-implementation phases (gate not passed) | Blocked | Allowed |
| Implementation phases (in progress) | Allowed | Allowed |
| Post-implementation phases (gate not passed) | Blocked | Allowed |
| Any phase (gate passed) | Allowed | Allowed |

## Platform Support

| Platform | Method | Tool Blocking | Compaction Survival | Custom Tool |
|----------|--------|---------------|--------------------|----|
| **OpenCode** | Plugin (`.opencode/plugins/workflow-enforcer.ts`) | Yes | Yes | Yes (`workflow_status`) |
| **Claude Code** | Hooks (`.claude/settings.json` + shell scripts) | Yes | Yes | No |
| **Devin CLI** | Reads `.claude/settings.json` hooks | Yes | No | No |
| **Codex CLI** | No hook system | Prompt-only | Prompt-only | No |
| **Copilot CLI** | No hook system | Prompt-only | Prompt-only | No |

## Files

| File | Purpose | Distributed By |
|------|---------|---------------|
| `enforcement/workflow-enforcer.ts` | OpenCode plugin (tool blocking + compaction + custom tool) | sync script |
| `enforcement/workflow-enforce.sh` | Shared state manager (bash) | sync script |
| `enforcement/pre-tool-use.sh` | Claude Code PreToolUse hook | sync script |
| `enforcement/pre-compact.sh` | Claude Code PreCompact hook | sync script |
| `enforcement/settings.json` | Claude Code hooks config template | sync script |
| `enforcement/workflow-config.json` | Config template (parameterized per workflow) | generated per package |
| `.opencode/workflow-config.json` | Config (filled in per package) | generated per package |
| `.opencode/workflow-state.json` | Runtime state (gitignored) | created at runtime |

## Custom Tool: `workflow_status` (OpenCode only)

Agents can call the `workflow_status` tool to:
- **`status`** — check current phase, completed phases, failed gates
- **`advance`** — move to the next phase
- **`pass_gate`** — mark current phase gate as passed
- **`fail_gate`** — mark current phase gate as failed (increments revision count)

## Compaction Survival

When the LLM context is compacted, the enforcement system injects a structured workflow state summary into the compaction context:

```
## WORKFLOW ENFORCEMENT STATE (PERSIST ACROSS COMPACTION)
Workflow: <package-name>
Current Phase: 5
Completed Phases: 1, 1.5, 2, 3, 4
In Progress: 5
Failed Gates: none
Revision Count: 0/3
Escalated: false
IMPORTANT: Do not skip phases. Do not proceed past a failed gate.
```

This ensures that after compaction, the LLM knows exactly where it is in the workflow.
