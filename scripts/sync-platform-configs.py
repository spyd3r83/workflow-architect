#!/usr/bin/env python3
"""
sync-platform-configs.py — Generate platform-native skill and agent files
from the canonical Workflow Designer Agent package.

Canonical source:
  agent-packages/workflow-designer-agent/skills/*.md
  agent-packages/workflow-designer-agent/agents/*.md

Generated outputs:
  .agents/skills/<name>/SKILL.md          (Codex, Copilot, OpenCode, Devin)
  .claude/skills/<name>/SKILL.md          (Claude Code — symlinked)
  .claude/agents/<name>.md                (Claude Code)
  .opencode/agents/<name>.md              (OpenCode)
  .github/agents/<name>.agent.md          (Copilot CLI)
  .devin/agents/<name>/AGENT.md           (Devin)
  .codex/agents/<name>.toml               (Codex CLI)

Usage:
  python3 scripts/sync-platform-configs.py
"""

import os
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = REPO_ROOT / "agent-packages" / "workflow-designer-agent"
SKILLS_SRC = PACKAGE_DIR / "skills"
AGENTS_SRC = PACKAGE_DIR / "agents"

SKILLS_OUT = REPO_ROOT / ".agents" / "skills"
CLAUDE_SKILLS_OUT = REPO_ROOT / ".claude" / "skills"
CLAUDE_AGENTS_OUT = REPO_ROOT / ".claude" / "agents"
OPENCODE_AGENTS_OUT = REPO_ROOT / ".opencode" / "agents"
GITHUB_AGENTS_OUT = REPO_ROOT / ".github" / "agents"
DEVIN_AGENTS_OUT = REPO_ROOT / ".devin" / "agents"
CODEX_AGENTS_OUT = REPO_ROOT / ".codex" / "agents"

COMMANDS = ["flowstart", "resume", "maintain", "update"]
COMMAND_DIRS = {
    "opencode": REPO_ROOT / ".opencode" / "commands",
    "claude": REPO_ROOT / ".claude" / "commands",
    "codex": REPO_ROOT / ".codex" / "commands",
    "github": REPO_ROOT / ".github" / "commands",
}


def extract_section(markdown: str, header: str) -> str:
    """Extract the content under a markdown H2 header."""
    pattern = rf"^## {re.escape(header)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, markdown, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_h1_title(markdown: str) -> str:
    """Extract the first H1 title."""
    match = re.match(r"^#\s+(.+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_skill_file(filepath: Path) -> dict:
    """Parse a canonical skill file into structured data."""
    content = filepath.read_text()
    name = filepath.stem
    purpose = extract_section(content, "Purpose")
    when_to_use = extract_section(content, "When To Use")
    description = purpose or f"Skill: {name}"
    if when_to_use:
        description = f"{description} Use when: {when_to_use}"
    if len(description) > 1024:
        description = description[:1021] + "..."
    return {
        "name": name,
        "description": description,
        "body": content,
    }


def parse_agent_file(filepath: Path) -> dict:
    """Parse a canonical agent file into structured data."""
    content = filepath.read_text()
    name = filepath.stem
    role = extract_section(content, "Role")
    mission = extract_section(content, "Mission")
    description = role or mission or f"Agent: {name}"
    if len(description) > 1024:
        description = description[:1021] + "..."
    return {
        "name": name,
        "description": description,
        "role": role,
        "mission": mission,
        "body": content,
    }


def write_skill_files(skills: list):
    """Write SKILL.md files to .agents/skills/<name>/ and symlink .claude/skills/."""
    if SKILLS_OUT.exists():
        shutil.rmtree(SKILLS_OUT)
    SKILLS_OUT.mkdir(parents=True, exist_ok=True)

    for skill in skills:
        skill_dir = SKILLS_OUT / skill["name"]
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        frontmatter = (
            f"---\nname: {skill['name']}\ndescription: {skill['description']}\n---\n\n"
        )
        skill_file.write_text(frontmatter + skill["body"])

    claude_skills = CLAUDE_SKILLS_OUT
    if claude_skills.is_symlink() or claude_skills.exists():
        if claude_skills.is_symlink() or claude_skills.is_dir():
            try:
                claude_skills.unlink()
            except OSError:
                shutil.rmtree(claude_skills, ignore_errors=True)
                claude_skills.unlink(missing_ok=True)
    claude_skills.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(os.path.relpath(SKILLS_OUT, CLAUDE_SKILLS_OUT.parent), CLAUDE_SKILLS_OUT)

    print(f"  Skills: {len(skills)} SKILL.md files in .agents/skills/")
    print(f"  Skills: .claude/skills/ -> .agents/skills/ (symlink)")


def write_claude_agents(agents: list):
    """Write .claude/agents/<name>.md with YAML frontmatter."""
    CLAUDE_AGENTS_OUT.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = CLAUDE_AGENTS_OUT / f"{agent['name']}.md"
        frontmatter = (
            f"---\nname: {agent['name']}\ndescription: {agent['description']}\n---\n\n"
        )
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .claude/agents/")


def write_opencode_agents(agents: list):
    """Write .opencode/agents/<name>.md with YAML frontmatter."""
    OPENCODE_AGENTS_OUT.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = OPENCODE_AGENTS_OUT / f"{agent['name']}.md"
        mode = "primary" if agent["name"] == "workflow-orchestrator" else "subagent"
        frontmatter = f"---\ndescription: {agent['description']}\nmode: {mode}\n---\n\n"
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .opencode/agents/")


def write_github_agents(agents: list):
    """Write .github/agents/<name>.agent.md for Copilot CLI."""
    GITHUB_AGENTS_OUT.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = GITHUB_AGENTS_OUT / f"{agent['name']}.agent.md"
        frontmatter = (
            f"---\nname: {agent['name']}\ndescription: {agent['description']}\n---\n\n"
        )
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .github/agents/")


def write_devin_agents(agents: list):
    """Write .devin/agents/<name>/AGENT.md for Devin."""
    DEVIN_AGENTS_OUT.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        agent_dir = DEVIN_AGENTS_OUT / agent["name"]
        agent_dir.mkdir(parents=True, exist_ok=True)
        filepath = agent_dir / "AGENT.md"
        frontmatter = (
            f"---\nname: {agent['name']}\ndescription: {agent['description']}\n---\n\n"
        )
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .devin/agents/")


def write_codex_agents(agents: list):
    """Write .codex/agents/<name>.toml for Codex CLI with full agent body."""
    CODEX_AGENTS_OUT.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = CODEX_AGENTS_OUT / f"{agent['name']}.toml"
        desc = agent["description"].replace('"', '\\"')
        body = agent["body"].replace('"""', '\\"\\"\\"')
        toml_content = (
            f'name = "{agent["name"]}"\n'
            f'description = "{desc}"\n'
            f'sandbox_mode = "read-only"\n'
            f'developer_instructions = """\n{body}\n"""\n'
        )
        filepath.write_text(toml_content)
    print(f"  Agents: {len(agents)} files in .codex/agents/")


def sync_commands():
    canonical = COMMAND_DIRS["opencode"]
    total = 0
    for platform, cmd_dir in COMMAND_DIRS.items():
        cmd_dir.mkdir(parents=True, exist_ok=True)
        for cmd in COMMANDS:
            cmd_file = cmd_dir / f"{cmd}.md"
            if platform != "opencode":
                src = canonical / f"{cmd}.md"
                if src.exists():
                    shutil.copy2(src, cmd_file)
                    total += 1
            elif cmd_file.exists():
                total += 1
            else:
                print(
                    f"  WARNING: {platform}/commands/{cmd}.md missing — create manually"
                )
    devin_playbooks = [REPO_ROOT / f"{cmd}.devin.md" for cmd in COMMANDS]
    for pb in devin_playbooks:
        if pb.exists():
            total += 1
    print(f"  Commands: {total} command files synced across all platforms")


def main():
    print("Syncing platform configs from canonical package...")

    skills = []
    if SKILLS_SRC.exists():
        for filepath in sorted(SKILLS_SRC.glob("*.md")):
            skills.append(parse_skill_file(filepath))
    print(f"Parsed {len(skills)} skills from canonical source.")

    agents = []
    if AGENTS_SRC.exists():
        for filepath in sorted(AGENTS_SRC.glob("*.md")):
            agents.append(parse_agent_file(filepath))
    print(f"Parsed {len(agents)} agents from canonical source.")

    print("\nGenerating platform-native files:")
    write_skill_files(skills)
    write_claude_agents(agents)
    write_opencode_agents(agents)
    write_github_agents(agents)
    write_devin_agents(agents)
    write_codex_agents(agents)
    sync_commands()

    print("\nDone. Platform configs synced.")
    print("\nNext steps:")
    print(
        "  - Verify: ls .agents/skills/ .claude/agents/ .opencode/agents/ .github/agents/ .devin/agents/ .codex/agents/"
    )
    print(
        "  - Verify commands: ls .opencode/commands/ .claude/commands/ .codex/commands/ .github/commands/"
    )
    print("  - Devin playbooks: ls *.devin.md")
    print(
        "  - Re-run this script after editing canonical files in agent-packages/workflow-designer-agent/"
    )


if __name__ == "__main__":
    main()
