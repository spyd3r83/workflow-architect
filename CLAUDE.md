@AGENTS.md

# Claude Code Specific

This project uses the Workflow Designer Agent package. Skills are in `.agents/skills/` (symlinked from `.claude/skills/`). Agents are in `.claude/agents/`.

To regenerate platform files after editing canonical sources:
```bash
python3 scripts/sync-platform-configs.py
```