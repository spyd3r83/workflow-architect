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


def yaml_block_scalar(value: str) -> str:
    text = (value or "").replace("\r\n", "\n").strip("\n")
    if not text:
        return '""'
    lines = text.split("\n")
    return "|\n" + "\n".join(f"  {line}" if line else "" for line in lines)


def write_skill_files(skills: list, output_root: Path):
    """Write SKILL.md files to .agents/skills/<name>/ and symlink .claude/skills/."""
    skills_out = output_root / ".agents" / "skills"
    claude_skills_out = output_root / ".claude" / "skills"

    if skills_out.is_symlink():
        raise ValueError("skill output must not redirect outside the package")
    skills_out.mkdir(parents=True, exist_ok=True)

    for skill in skills:
        skill_dir = skills_out / skill["name"]
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        desc = yaml_block_scalar(skill["description"])
        frontmatter = f"---\nname: {skill['name']}\ndescription: {desc}\n---\n\n"
        skill_file.write_text(frontmatter + skill["body"])

    if claude_skills_out.is_symlink():
        if claude_skills_out.resolve() != skills_out.resolve():
            raise ValueError("existing Claude skills link targets another package")
    elif claude_skills_out.exists():
        for skill in skills:
            copy_managed(
                skills_out / skill["name"] / "SKILL.md",
                claude_skills_out / skill["name"] / "SKILL.md",
            )
    else:
        claude_skills_out.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(
            os.path.relpath(skills_out, claude_skills_out.parent), claude_skills_out
        )

    print(f"  Skills: {len(skills)} SKILL.md files in .agents/skills/")
    print(f"  Skills: .claude/skills/ -> .agents/skills/ (symlink)")


def write_claude_agents(agents: list, output_root: Path):
    out_dir = output_root / ".claude" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = out_dir / f"{agent['name']}.md"
        desc = yaml_block_scalar(agent["description"])
        frontmatter = f"---\nname: {agent['name']}\ndescription: {desc}\n---\n\n"
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .claude/agents/")


def write_opencode_agents(agents: list, output_root: Path, primary_agent: str):
    out_dir = output_root / ".opencode" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = out_dir / f"{agent['name']}.md"
        mode = "primary" if agent["name"] == primary_agent else "subagent"
        desc = yaml_block_scalar(agent["description"])
        task = "true" if mode == "primary" else "false"
        frontmatter = (
            f"---\ndescription: {desc}\nmode: {mode}\ntools:\n  task: {task}\n---\n\n"
        )
        filepath.write_text(frontmatter + agent["body"])
    print(
        f"  Agents: {len(agents)} files in .opencode/agents/ (primary: {primary_agent})"
    )


def write_github_agents(agents: list, output_root: Path):
    out_dir = output_root / ".github" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        filepath = out_dir / f"{agent['name']}.agent.md"
        desc = yaml_block_scalar(agent["description"])
        frontmatter = f"---\nname: {agent['name']}\ndescription: {desc}\n---\n\n"
        filepath.write_text(frontmatter + agent["body"])
    print(f"  Agents: {len(agents)} files in .github/agents/")


def write_devin_agents(agents: list, output_root: Path):
    out_dir = output_root / ".devin" / "agents"
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        agent_dir = out_dir / agent["name"]
        agent_dir.mkdir(parents=True, exist_ok=True)
        filepath = agent_dir / "AGENT.md"
        desc = yaml_block_scalar(agent["description"])
        frontmatter = f"---\nname: {agent['name']}\ndescription: {desc}\n---\n\n"
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


def sync_package(package_dir: Path, output_root: Path, label: str, runtime_source=None):
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
    sync_enforcement(package_dir, output_root, runtime_source)


RUNTIME_FILES = [
    "workflow-enforce.sh",
    "run_store.py",
    "run_effects.py",
    "run_policy.py",
    "run_operator.py",
    "operator_cli.py",
    "run_cli.py",
    "run_hook.py",
    "dispatch-gate-hook.sh",
    "workflow-enforcer.ts",
    "pre-tool-use.sh",
    "pre-compact.sh",
    "settings.json",
    "run-binding.md",
]


def copy_managed(source, target):
    if not source.is_file():
        raise ValueError(f"missing canonical runtime file: {source}")
    if source.resolve() == target.resolve():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        raise ValueError(f"refuse redirected generated target: {target}")
    shutil.copy2(source, target)
    if target.suffix == ".sh":
        target.chmod(0o755)


def runtime_sources(package_dir, upstream):
    local = package_dir / "enforcement"
    default = REPO_ROOT / "agent-packages/workflow-designer-agent/enforcement"
    source = (
        Path(upstream).resolve() if upstream else (local if local.is_dir() else default)
    )
    if upstream:
        if not (local / "workflow-config.json").is_file():
            raise ValueError(
                "local phase/config policy required before shared runtime refresh"
            )
        for name in RUNTIME_FILES:
            copy_managed(source / name, local / name)
    return local if local.is_dir() else source


LEGACY_HOOK_COMMANDS = {
    "${CLAUDE_PROJECT_DIR}/.claude/hooks/pre-tool-use.sh",
    "${CLAUDE_PROJECT_DIR}/.claude/hooks/pre-compact.sh",
    "${CLAUDE_PROJECT_DIR}/scripts/enforcement/dispatch-gate-hook.sh",
    'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use.sh"',
    'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact.sh"',
    "bash .claude/hooks/pre-tool-use.sh",
    "bash .claude/hooks/pre-compact.sh",
}


def hook_signature(hook):
    return json.dumps(
        [hook.get("type"), hook.get("command"), hook.get("args")], sort_keys=True
    )


def merge_hook_groups(old, wanted):
    owned = {hook_signature(h) for group in wanted for h in group["hooks"]}
    owned.update(
        hook_signature(dict(type="command", command=c)) for c in LEGACY_HOOK_COMMANDS
    )
    groups = [
        dict(g, hooks=[h for h in g.get("hooks", []) if hook_signature(h) not in owned])
        for g in old
    ]
    for desired in wanted:
        metadata = {k: v for k, v in desired.items() if k != "hooks"}
        group = next(
            (
                g
                for g in groups
                if {k: v for k, v in g.items() if k != "hooks"} == metadata
            ),
            None,
        )
        if group is None:
            group = dict(metadata, hooks=[])
            groups.append(group)
        group["hooks"].extend(desired["hooks"])
    return groups


def merge_runtime_hooks(source, target):
    wanted = json.loads(source.read_text())["hooks"]
    settings = json.loads(target.read_text()) if target.exists() else {}
    for event, groups in wanted.items():
        old = settings.setdefault("hooks", {}).get(event, [])
        settings["hooks"][event] = merge_hook_groups(old, groups)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(settings, indent=2) + "\n")


def sync_runtime_config(source, output_root):
    config = json.loads((source / "workflow-config.json").read_text())
    config["workflow_package"] = output_root.name
    target = output_root / ".opencode/workflow-config.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, indent=2) + "\n")


def sync_enforcement(package_dir: Path, output_root: Path, runtime_source=None):
    source = runtime_sources(package_dir, runtime_source)
    for name in RUNTIME_FILES:
        if name.endswith(".py") or name in {
            "workflow-enforce.sh",
            "dispatch-gate-hook.sh",
        }:
            copy_managed(source / name, output_root / "scripts/enforcement" / name)
    for extra in source.glob("*_policy.py"):
        copy_managed(extra, output_root / "scripts/enforcement" / extra.name)
    copy_managed(
        source / "workflow-enforcer.ts",
        output_root / ".opencode/plugins/workflow-enforcer.ts",
    )
    for name in ["pre-tool-use.sh", "pre-compact.sh"]:
        copy_managed(source / name, output_root / ".claude/hooks" / name)
    merge_runtime_hooks(source / "settings.json", output_root / ".claude/settings.json")
    sync_runtime_config(source, output_root)
    for name in ["run-binding.md", "enforcement.md", "dispatch-gate.md"]:
        if (source / name).is_file():
            copy_managed(source / name, output_root / name)
    preflight = REPO_ROOT / "scripts/preflight-task-check.sh"
    if preflight.is_file() and not (output_root / "scripts" / preflight.name).exists():
        copy_managed(preflight, output_root / "scripts" / preflight.name)
    print(
        "  Enforcement: complete run-scoped runtime; local phase/specialist policy preserved"
    )


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
    parser.add_argument(
        "--runtime-source",
        help="Explicit shared runtime source; preserves package-local config/policy",
    )
    args = parser.parse_args()

    package_arg = args.package_flag or args.package

    if package_arg:
        package_dir = Path(package_arg).resolve()
        if not package_dir.exists():
            print(f"ERROR: Package directory does not exist: {package_dir}")
            sys.exit(1)
        print(f"Syncing package: {package_dir}")
        sync_package(package_dir, package_dir, package_dir.name, args.runtime_source)
    else:
        package_dir = REPO_ROOT / "agent-packages" / "workflow-designer-agent"
        if not package_dir.exists():
            print(f"ERROR: Default meta-package not found at {package_dir}")
            sys.exit(1)
        print(f"Syncing meta-package: {package_dir}")
        sync_package(package_dir, REPO_ROOT, "meta-package", args.runtime_source)

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
