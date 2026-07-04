# Platform Config Template — Generated Package

This template defines the platform configuration files a generated package must include so it is immediately invocable on all 5 platforms (OpenCode, Claude Code, Codex CLI, Copilot CLI, Devin).

---

## Required Platform Files

Every generated package must include these files at the package root:

### opencode.json

```json
{
  "agent": {
    "{{PRIMARY_AGENT_NAME}}": {
      "description": "{{WORKFLOW_DESCRIPTION}}",
      "mode": "primary",
      "prompt": "{file:./prompts/master-prompt.md}"
    }
  },
  "instructions": [
    "AGENTS.md"
  ]
}
```

### Slash Commands

Place command files in these directories (create them at the project root where the package is installed):

| Platform | Command Directory | Files |
|----------|------------------|-------|
| OpenCode | `.opencode/commands/` | `{{COMMAND_NAME}}.md`, `{{COMMAND_NAME}}-resume.md`, `{{COMMAND_NAME}}-maintain.md` |
| Claude Code | `.claude/commands/` | Same 3 files |
| Codex CLI | `.codex/commands/` | Same 3 files |
| Copilot CLI | `.github/commands/` | Same 3 files |
| Devin | Package root | `{{COMMAND_NAME}}.devin.md`, `{{COMMAND_NAME}}-resume.devin.md`, `{{COMMAND_NAME}}-maintain.devin.md` |

### Agent Discovery Files

| Platform | Path | Format |
|----------|------|--------|
| OpenCode | `.opencode/agents/{{agent-name}}.md` | Markdown + YAML frontmatter |
| Claude Code | `.claude/agents/{{agent-name}}.md` | Markdown + YAML frontmatter |
| Codex CLI | `.codex/agents/{{agent-name}}.toml` | TOML |
| Copilot CLI | `.github/agents/{{agent-name}}.agent.md` | Markdown + YAML frontmatter |
| Devin | `.devin/agents/{{agent-name}}/AGENT.md` | Markdown + YAML frontmatter |

### Skill Discovery Files

| Platform | Path |
|----------|------|
| OpenCode, Codex, Copilot, Devin | `.agents/skills/{{skill-name}}/SKILL.md` |
| Claude Code | `.claude/skills/{{skill-name}}/SKILL.md` (symlink to `.agents/skills/`) |

### Instructions File

| Platform | File |
|----------|------|
| OpenCode, Codex, Copilot, Devin | `AGENTS.md` (at package root) |
| Claude Code | `CLAUDE.md` (imports `@AGENTS.md`) |

---

## Fill Instructions

1. **{{PRIMARY_AGENT_NAME}}**: The kebab-case name of the primary coordinating agent.
2. **{{WORKFLOW_DESCRIPTION}}**: One-line description of the workflow.
3. **{{COMMAND_NAME}}**: The kebab-case slash command name (e.g., "revamp-site", "launch-app").

## Validation Criteria

- [ ] `opencode.json` exists with agent registration.
- [ ] 3 command files exist per platform (15 total).
- [ ] Agent files exist per platform.
- [ ] Skill files exist in `.agents/skills/` with `SKILL.md` format.
- [ ] `AGENTS.md` exists at package root.
- [ ] `CLAUDE.md` exists and imports `@AGENTS.md`.
- [ ] No `{{PLACEHOLDER}}` remains in any file.