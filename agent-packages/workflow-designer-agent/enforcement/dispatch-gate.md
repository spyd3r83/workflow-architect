# Dispatch-Gate Contract

## Invariant

A required named specialist dispatch must succeed before protected phase advancement or mutation. Dispatch failure must fail closed for that workflow/session without generic fallback.

## Mechanism

Two hooks work together:

1. **PostToolUse on dispatch/subagent tool** (`task` in OpenCode/Copilot/Devin, `Agent` in Claude Code): Inspects the dispatch output. If the output contains error patterns (`Skills not found`, `TASK_DISPATCH_UNAVAILABLE`, `Error:`, `error:`), the hook calls `workflow-enforce.sh dispatch-failed`, which sets `dispatch_failed: true` in the workflow state file.

2. **PreToolUse on mutating tools**: Calls `workflow-enforce.sh check <tool> <arg>`. The `check` command checks `dispatch_failed`. If true, it returns `block:Dispatch failure detected...` and the hook denies the tool call. Also checks `pass_gate` and `advance_phase` — both blocked while `dispatch_failed` is true.

## Clearing

The `dispatch_failed` flag is cleared by `workflow_status(action="fail_gate")` — requires a reason, enters revision mode, and clears the flag.

## Harness Adapters

Each supported harness has a thin adapter wired into its native hook system. The shared `dispatch-gate-hook.sh` script is called by all non-OpenCode adapters.

| Harness | Config Discovery Path | Config Schema | PreToolUse Block | PostToolUse Track | Tool Names |
|---------|----------------------|---------------|-----------------|------------------|------------|
| **OpenCode** | `.opencode/plugins/workflow-enforcer.ts` | Plugin `tool.execute.before`/`tool.execute.after` | `throw new Error(...)` | Calls `dispatch-failed` | `bash`, `write`, `edit`, `task` |
| **Claude Code** | `.claude/settings.json` under `hooks` key | `{"hooks": {"PreToolUse": [{"matcher": "...", "hooks": [{"type": "command", "command": "${CLAUDE_PROJECT_DIR}/..."}]}]}}` | JSON: `hookSpecificOutput.permissionDecision: "deny"` + exit 2 | Hook calls `dispatch-gate-hook.sh` | `Bash`, `Write`, `Edit`, `apply_patch`, `Agent` |
| **Copilot CLI** | `.github/hooks/*.json` (repo-level discovery) | `{"version": 1, "hooks": {"preToolUse": [{"type": "command", "bash": "...", "timeoutSec": 10}]}}` | JSON: `permissionDecision: "deny"` + exit 2 | Hook calls `dispatch-gate-hook.sh` | `bash`, `edit`, `write`, `create` |
| **Codex** | `.codex/hooks.json` (repo-level) or inline `[hooks]` in `config.toml` | `{"hooks": {"PreToolUse": [{"matcher": "...", "hooks": [{"type": "command", "command": "..."}]}]}}` | JSON: `hookSpecificOutput.permissionDecision: "deny"` + exit 2 | Hook calls `dispatch-gate-hook.sh` | `Bash`, `apply_patch`, `Edit`, `Write` |
| **Devin CLI** | `.devin/hooks.v1.json` (flat format, no wrapper key) | `{"PreToolUse": [{"matcher": "exec\|edit", "hooks": [{"type": "command", "command": "..."}]}]}` | Exit code 2 + stderr | Hook calls `dispatch-gate-hook.sh` | `exec`, `edit` |

### Hook Input Payloads (verified from official docs)

**Claude Code PreToolUse stdin**: `{"tool_name": "Bash", "tool_input": {"command": "..."}, "session_id": "...", "hook_event_name": "PreToolUse"}`

**Claude Code PostToolUse stdin**: `{"tool_name": "Agent", "tool_input": {...}, "tool_response": "...", "hook_event_name": "PostToolUse"}`

**Copilot preToolUse stdin**: `{"toolName": "bash", "toolArgs": {"command": "..."}, "hookEventName": "preToolUse"}` (CamelCase, `toolArgs` not `toolInput`)

**Copilot postToolUse stdin**: `{"toolName": "task", "toolArgs": {...}, "toolResult": "...", "hookEventName": "postToolUse"}` (CamelCase, `toolResult` not `tool_response`)

**Codex PreToolUse stdin**: `{"tool_name": "Bash", "tool_input": {"command": "..."}, "hook_event_name": "PreToolUse"}`

**Devin PreToolUse stdin**: `{"tool_name": "exec", "tool_input": {"command": "..."}, "session_id": "...", "hook_event_name": "PreToolUse"}`

**Devin PostToolUse stdin**: `{"tool_name": "task", "tool_input": {...}, "tool_response": {"success": false, "output": "...", "error": "..."}, "hook_event_name": "PostToolUse"}`

### Blocking Response (verified from official docs)

- **Claude Code**: JSON stdout `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}` OR exit code 2 + stderr
- **Copilot CLI**: JSON stdout `{"permissionDecision": "deny", "permissionDecisionReason": "..."}` OR exit code 2 + stderr
- **Codex**: Same as Claude Code format
- **Devin CLI**: Exit code 2 + stderr (JSON also supported)

## Non-Destructive Coexistence

- **Claude Code**: The sync script merges the dispatch-gate hooks into existing `.claude/settings.json`, appending to existing hook arrays. Pre-existing settings and hooks are preserved.
- **Copilot CLI**: The adapter file `.github/hooks/dispatch-gate.json` is a separate file. Copilot discovers all `.github/hooks/*.json` files and combines them.
- **Codex**: The adapter file `.codex/hooks.json` is a standalone file. Codex merges all matching hooks from multiple files. Project-local hooks require trust review via `/hooks` command.
- **Devin CLI**: The adapter file `.devin/hooks.v1.json` is a standalone file. Devin reads hooks from the project directory and ancestor directories.

## Activation Requirements

- **Claude Code**: Hooks are active when `.claude/settings.json` is present. No feature flag needed.
- **Copilot CLI**: Hooks are active when `.github/hooks/*.json` files are present. No feature flag needed.
- **Codex**: Hooks are enabled by default. `codex_hooks` is a deprecated alias for `hooks`. Non-managed command hooks require trust review via `/hooks` command before they run. Use `--dangerously-bypass-hook-trust` for one-off automation.
- **Devin CLI**: Hooks are active when `.devin/hooks.v1.json` is present. No feature flag needed.

## Limitations

- Prompt instructions are guidance; deterministic hooks are the authority where supported.
- Cloud Devin enforcement is not claimed; only Devin CLI hooks are documented.
- Non-OpenCode harness adapters are documented and structurally verified but not live-tested in actual harness sessions. Live acceptance testing is a remaining step.
