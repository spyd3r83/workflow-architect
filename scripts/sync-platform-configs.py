#!/usr/bin/env python3
"""
sync-platform-configs.py — Generate platform-native skill, agent, and command files
from a canonical agent package.

Supports two modes:
  1. Meta-package (default): syncs agent-packages/workflow-designer-agent/ to repo-level
     platform directories (.opencode/, .claude/, .codex/, .github/, .devin/, .agents/).
  2. Any package: syncs <package-dir>/ to platform directories WITHIN that package.

Usage:
  python3 scripts/sync-platform-configs.py                          # meta-package (default)
  python3 scripts/sync-platform-configs.py --package <path>         # any package
  python3 scripts/sync-platform-configs.py generated-workflows/backend-repo-maintenance-workflow

Canonical source (per package):
  <package>/skills/*.md      — skill definitions
  <package>/agents/*.md      — agent definitions
  <package>/commands/*.md     — slash command definitions (excluding README.md)

Generated outputs (within the package or at repo root for meta-package):
  .agents/skills/<name>/SKILL.md          (Codex, Copilot, OpenCode, Devin)
  .claude/skills/                         (Claude Code — symlinked to .agents/skills/)
  .claude/agents/<name>.md                (Claude Code)
  .opencode/agents/<name>.md              (OpenCode)
  .github/agents/<name>.agent.md          (Copilot CLI)
  .devin/agents/<name>/AGENT.md           (Devin)
  .codex/agents/<name>.toml               (Codex CLI)
  .opencode/commands/<cmd>.md             (OpenCode)
  .claude/commands/<cmd>.md               (Claude Code)
  .codex/commands/<cmd>.md                (Codex CLI)
  .github/commands/<cmd>.md               (Copilot CLI)
  <cmd>.devin.md                           (Devin playbooks, at package root)
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def extract_section(markdown: str, header: str) -> str:
    """Extract the content under a markdown H2 header."""
    pattern = rf"^## {re.escape(header)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, markdown, re.MULTILINE | re.DOTALL)
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


def detect_primary_agent(package_dir: Path) -> str:
    """Detect the primary agent from the package's opencode.json."""
    opencode_json = package_dir / "opencode.json"
    if opencode_json.exists():
        try:
            config = json.loads(opencode_json.read_text())
            default_agent = config.get("default_agent")
            if default_agent:
                return default_agent
        except (json.JSONDecodeError, KeyError):
            pass
    agents_dir = package_dir / "agents"
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            if "orchestrator" in f.stem.lower():
                return f.stem
    if agents_dir.exists():
        files = sorted(agents_dir.glob("*.md"))
        if files:
            return files[0].stem
    return "workflow-orchestrator"


def discover_commands(commands_dir: Path) -> list[str]:
    """Discover command names from a commands/ directory (excluding README.md)."""
    if not commands_dir.exists():
        return []
    commands = []
    for f in sorted(commands_dir.glob("*.md")):
        if f.stem.lower() != "readme":
            commands.append(f.stem)
    return commands


def write_skill_files(skills: list, output_root: Path):
    """Write SKILL.md files to .agents/skills/<name>/ and symlink .claude/skills/."""
    skills_out = output_root / ".agents" / "skills"
    claude_skills_out = output_root / ".claude" / "skills"

    if skills_out.exists():
        shutil.rmtree(skills_out)
    skills_out.mkdir(parents=True, exist_ok=True)

    for skill in skills:
        skill_dir = skills_out / skill["name"]
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        frontmatter = (
            f"---\nname: {skill['name']}\ndescription: {skill['description']}\n---\n\n"
        )
        skill_file.write_text(frontmatter + skill["body"])

    if claude_skills_out.is_symlink() or claude_skills_out.exists():
        if claude_skills_out.is_symlink() or claude_skills_out.is_dir():
            try:
                claude_skills_out.unlink()
            except OSError:
                shutil.rmtree(claude_skills_out, ignore_errors=True)
                claude_skills_out.unlink(missing_ok=True)
    claude_skills_out.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(
        os.path.relpath(skills_out, claude_skills_out.parent),
        claude_skills_out,
    )

    print(f"  Skills: {len(skills)} SKILL.md files in .agents/skills/")
    print(f"  Skills: .claude/skills/ -> .agents/skills/ (symlink)")


def write_claude_agents(agents: list, output_root: Path):
    """Write .claude/agents/<name>.md with YAML frontmatter."""
    out_dir = output_root / ".claude" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = out_dir / f"{agent['name']}.md"
        frontmatter = (
            f"---\nname: {agent['name']}\ndescription: {agent['description']}\n---\n\n"
        )
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .claude/agents/")


def write_opencode_agents(agents: list, output_root: Path, primary_agent: str):
    """Write .opencode/agents/<name>.md with YAML frontmatter."""
    out_dir = output_root / ".opencode" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = out_dir / f"{agent['name']}.md"
        mode = "primary" if agent["name"] == primary_agent else "subagent"
        frontmatter = f"---\ndescription: {agent['description']}\nmode: {mode}\n---\n\n"
        filepath.write_text(frontmatter + agent["body"])
    print(
        f"  Agents: {len(agents)} files in .opencode/agents/ (primary: {primary_agent})"
    )


def write_github_agents(agents: list, output_root: Path):
    """Write .github/agents/<name>.agent.md for Copilot CLI."""
    out_dir = output_root / ".github" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = out_dir / f"{agent['name']}.agent.md"
        frontmatter = (
            f"---\nname: {agent['name']}\ndescription: {agent['description']}\n---\n\n"
        )
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .github/agents/")


def write_devin_agents(agents: list, output_root: Path):
    """Write .devin/agents/<name>/AGENT.md for Devin."""
    out_dir = output_root / ".devin" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        agent_dir = out_dir / agent["name"]
        agent_dir.mkdir(parents=True, exist_ok=True)
        filepath = agent_dir / "AGENT.md"
        frontmatter = (
            f"---\nname: {agent['name']}\ndescription: {agent['description']}\n---\n\n"
        )
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .devin/agents/")


def write_codex_agents(agents: list, output_root: Path):
    """Write .codex/agents/<name>.toml for Codex CLI with full agent body."""
    out_dir = output_root / ".codex" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = out_dir / f"{agent['name']}.toml"
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


def sync_commands(commands_src: Path, command_names: list[str], output_root: Path):
    """Sync command files to all platform command directories + Devin playbooks."""
    command_dirs = {
        "opencode": output_root / ".opencode" / "commands",
        "claude": output_root / ".claude" / "commands",
        "codex": output_root / ".codex" / "commands",
        "github": output_root / ".github" / "commands",
    }

    total = 0
    for platform, cmd_dir in command_dirs.items():
        cmd_dir.mkdir(parents=True, exist_ok=True)
        for cmd in command_names:
            src_file = commands_src / f"{cmd}.md"
            if not src_file.exists():
                print(f"  WARNING: {platform}/commands/{cmd}.md source missing")
                continue
            dest_file = cmd_dir / f"{cmd}.md"
            if src_file.resolve() == dest_file.resolve():
                total += 1
                continue
            shutil.copy2(src_file, dest_file)
            total += 1

    for cmd in command_names:
        src_file = commands_src / f"{cmd}.md"
        if src_file.exists():
            dest_file = output_root / f"{cmd}.devin.md"
            shutil.copy2(src_file, dest_file)
            total += 1

    print(
        f"  Commands: {total} command files synced across all platforms ({len(command_names)} commands)"
    )


def sync_package(package_dir: Path, output_root: Path, label: str):
    """Sync a single package's agents, skills, and commands to platform directories."""
    skills_src = package_dir / "skills"
    agents_src = package_dir / "agents"
    commands_src = package_dir / "commands"

    skills = []
    if skills_src.exists():
        for filepath in sorted(skills_src.glob("*.md")):
            skills.append(parse_skill_file(filepath))
    print(f"Parsed {len(skills)} skills from {label}.")

    agents = []
    if agents_src.exists():
        for filepath in sorted(agents_src.glob("*.md")):
            agents.append(parse_agent_file(filepath))
    print(f"Parsed {len(agents)} agents from {label}.")

    primary_agent = detect_primary_agent(package_dir)
    print(f"Primary agent: {primary_agent}")

    command_names = discover_commands(commands_src)
    print(f"Discovered {len(command_names)} commands: {command_names}")

    print(f"\nGenerating platform-native files for {label}:")
    if skills:
        write_skill_files(skills, output_root)
    if agents:
        write_claude_agents(agents, output_root)
        write_opencode_agents(agents, output_root, primary_agent)
        write_github_agents(agents, output_root)
        write_devin_agents(agents, output_root)
        write_codex_agents(agents, output_root)
    if command_names:
        sync_commands(commands_src, command_names, output_root)


def main():
    parser = argparse.ArgumentParser(
        description="Sync platform-native files from a canonical agent package."
    )
    parser.add_argument(
        "package",
        nargs="?",
        default=None,
        help="Path to the package to sync (default: meta-package at agent-packages/workflow-designer-agent)",
    )
    parser.add_argument(
        "--package",
        dest="package_flag",
        default=None,
        help="Path to the package to sync (alternative to positional argument)",
    )
    args = parser.parse_args()

    package_arg = args.package_flag or args.package

    if package_arg:
        package_dir = Path(package_arg).resolve()
        if not package_dir.exists():
            print(f"ERROR: Package directory does not exist: {package_dir}")
            sys.exit(1)
        print(f"Syncing package: {package_dir}")
        sync_package(package_dir, package_dir, package_dir.name)
    else:
        package_dir = REPO_ROOT / "agent-packages" / "workflow-designer-agent"
        if not package_dir.exists():
            print(f"ERROR: Default meta-package not found at {package_dir}")
            sys.exit(1)
        print(f"Syncing meta-package: {package_dir}")
        sync_package(package_dir, REPO_ROOT, "meta-package")

    print("\nDone. Platform configs synced.")
    print("\nNext steps:")
    print(
        "  - Verify agents: ls .opencode/agents/ .claude/agents/ .github/agents/ .devin/agents/ .codex/agents/"
    )
    print("  - Verify skills: ls .agents/skills/")
    print(
        "  - Verify commands: ls .opencode/commands/ .claude/commands/ .codex/commands/ .github/commands/"
    )
    print("  - Devin playbooks: ls *.devin.md")
    print("  - Re-run after editing canonical source files.")


if __name__ == "__main__":
    main()
