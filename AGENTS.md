# AGENTS.md — workflow-architect

This project contains a **Workflow Designer Agent** package — a meta-agent that designs domain-specific agent workflows on demand.

## Package Location

```
agent-packages/workflow-designer-agent/
```

## What It Does

The Workflow Designer Agent takes a high-level project objective (e.g., "design a workflow to revamp a website") and produces a complete, implementation-ready agent workflow package with specialized agents, reusable skills, a sequenced workflow, intake model, research protocol, QA process, red-team review, templates, and examples.

## How To Invoke

### Slash Commands (all platforms)

| Command | Purpose | Usage |
|---------|---------|-------|
| `/flowstart <objective>` | Start a new workflow design project | `/flowstart Design a workflow to revamp a marketing website` |
| `/resume <project>` | Resume an in-progress workflow | `/resume website-revamp-workflow` |
| `/maintain <project>` | Validate and update an existing workflow | `/maintain website-revamp-workflow` |
| `/update` | Self-improve the Workflow Designer Agent package | `/update` |

### Platform Command Locations

| Platform | Command Path |
|----------|-------------|
| OpenCode | `.opencode/commands/flowstart.md`, `.opencode/commands/resume.md`, `.opencode/commands/maintain.md`, `.opencode/commands/update.md` |
| Claude Code | `.claude/commands/flowstart.md`, `.claude/commands/resume.md`, `.claude/commands/maintain.md`, `.claude/commands/update.md` |
| Codex CLI | `.codex/commands/flowstart.md`, `.codex/commands/resume.md`, `.codex/commands/maintain.md`, `.codex/commands/update.md` |
| Copilot CLI | `.github/commands/flowstart.md`, `.github/commands/resume.md`, `.github/commands/maintain.md`, `.github/commands/update.md` |
| Devin | `flowstart.devin.md`, `resume.devin.md`, `maintain.devin.md`, `update.devin.md` (playbooks) |

### Default Agent

The `opencode.json` file sets `workflow-orchestrator` as the default agent (`default_agent` field) and registers it as `mode: primary`. In OpenCode, the agent is:
- **Default**: automatically used when no agent is specified
- **Primary**: available via `@workflow-orchestrator`
- **Invocable via /flowstart**: the slash command loads the master prompt and fills `$ARGUMENTS` as the objective

All other 8 agents (intake-analyst, domain-researcher, workflow-architect, skill-architect, implementation-planner, quality-reviewer, red-team-reviewer, final-packager) are registered as `mode: subagent` and can be invoked via `@<name>`.

### Manual Invocation (fallback)

If slash commands are not available, open `agent-packages/workflow-designer-agent/prompts/master-workflow-designer-prompt.md`, replace `{{PROJECT_OBJECTIVE}}` and `{{OUTPUT_PATH}}`, and paste into an agent session.

## Platform Compatibility

This package is compatible with OpenCode, Claude Code, Codex CLI, Copilot CLI, and Devin. Platform-native skill and agent files are generated from the canonical markdown source by running:

```bash
python3 scripts/sync-platform-configs.py
```

### Skill Discovery Paths

| Platform | Path |
|----------|------|
| OpenCode, Codex, Copilot, Devin | `.agents/skills/<name>/SKILL.md` |
| Claude Code | `.claude/skills/<name>/SKILL.md` (symlinked to `.agents/skills/`) |

### Agent Discovery Paths

| Platform | Path |
|----------|------|
| OpenCode | `.opencode/agents/<name>.md` |
| Claude Code | `.claude/agents/<name>.md` |
| Codex CLI | `.codex/agents/<name>.toml` |
| Copilot CLI | `.github/agents/<name>.agent.md` |
| Devin | `.devin/agents/<name>/AGENT.md` |

## Project Conventions

- Agent and skill definitions are written in markdown with YAML frontmatter.
- The canonical source lives in `agent-packages/workflow-designer-agent/`.
- Platform-specific files are generated, not hand-edited. Run the sync script after changing canonical files.
- Skills follow the [agentskills.io](https://agentskills.io) open standard (`SKILL.md` with `name` + `description` frontmatter).
- Agents follow per-platform formats (see adapter script for details).

## Build / Test

This is a documentation/package project. No build step. To validate the package:

1. Verify all canonical files exist: `find agent-packages/workflow-designer-agent -type f | wc -l` (should be 64).
2. Run the sync script to generate platform files: `python3 scripts/sync-platform-configs.py`.
3. Verify platform files exist: check `.agents/skills/`, `.claude/agents/`, `.opencode/agents/`, `.github/agents/`, `.devin/agents/`, `.codex/agents/`.

## See Also

- `agent-packages/workflow-designer-agent/README.md` — full package documentation
- `agent-packages/workflow-designer-agent/AGENTS.md` — operating instructions for the Workflow Designer Agent
- `agent-packages/workflow-designer-agent/implementation-guide.md` — step-by-step usage guide