# workflow-architect

A **Workflow Designer Agent** — a meta-agent that designs domain-specific agent workflows on demand. Give it a high-level project objective (e.g., "design a workflow to revamp a marketing website") and it produces a complete, implementation-ready agent workflow package with specialized agents, reusable skills, a sequenced workflow, intake model, research protocol, QA process, red-team review, templates, and examples.

## What It Does

The Workflow Designer Agent runs an 18-phase workflow:

1. **Intake** — clarifies the objective, labels assumptions with risk classification
2. **Domain research** — gathers sourced facts (statutes, tooling, pricing, case law) with citations
3. **Workflow decomposition** — designs the sequenced phase structure
4. **Agent + skill design** — defines the agent roster (10 sections each) and reusable skills (8 sections each)
5. **Implementation planning** — turns the design into a file/folder package on disk
6. **Quality control** — runs 15 quantitative criteria via `scripts/validate-package.py`
7. **Red-team review** — adversarial review from 6 stakeholder perspectives
8. **Final packaging** — assembles the deliverable and produces a user-facing summary

Three **Oracle gates** (high-reasoning independent review) enforce quality at: requirements confirmation, domain classification, and pre-finalization.

## Quick Start

### Slash Commands (all platforms)

| Command | Purpose | Usage |
|---------|---------|-------|
| `/flowstart <objective>` | Start a new workflow design project | `/flowstart Design a workflow to revamp a marketing website` |
| `/resume <project>` | Resume an in-progress workflow | `/resume website-revamp-workflow` |
| `/maintain <project>` | Validate and update an existing workflow | `/maintain website-revamp-workflow` |
| `/update` | Self-improve the Workflow Designer Agent package | `/update` |

### Manual Invocation (fallback)

If slash commands are not available:

1. Open `agent-packages/workflow-designer-agent/prompts/master-workflow-designer-prompt.md`.
2. Replace `{{PROJECT_OBJECTIVE}}` with your project goal.
3. Replace `{{OUTPUT_PATH}}` with your desired output path.
4. Paste the result into an agent session.

## Repository Structure

```
workflow-architect/
  AGENTS.md                              # Master notice file (read this first)
  CLAUDE.md                              # Claude Code loader (imports AGENTS.md)
  opencode.json                          # OpenCode config (default agent: workflow-orchestrator)
  README.md                              # This file
  .gitignore                             # Ignores generated-workflows/, snapshots, pycache
  agent-packages/
    workflow-designer-agent/            # Canonical source (64+ files)
      AGENTS.md                          # Operating instructions for the agent
      README.md                          # Full package documentation
      implementation-guide.md            # Step-by-step usage guide
      workflow.md                        # Full 18-phase workflow definition
      quality-control.md                 # Quantitative acceptance criteria
      research-protocol.md               # Source-backed research rules
      fmea.md                            # Failure mode analysis
      requirements.md                    # Formal requirements
      intake.md                          # Intake model
      agents/                            # 9 agent definitions
      skills/                            # 10 reusable skills
      templates/                         # 19 template files
      prompts/                           # Master + example prompts
      examples/                          # Worked examples
      tests/                             # Regression + idempotency tests
  generated-workflows/                   # Output of /flowstart runs (gitignored)
  scripts/
    sync-platform-configs.py             # Regenerates platform-specific files
    validate-package.py                  # Validates a generated package (49+ checks)
  .agents/skills/                        # OpenCode/Codex/Copilot/Devin skill discovery
  .claude/agents/                        # Claude Code agent definitions
  .claude/commands/                      # Claude Code slash commands
  .claude/skills -> ../.agents/skills    # Symlinked skill discovery
  .codex/agents/                         # Codex CLI agent definitions
  .codex/commands/                       # Codex CLI slash commands
  .github/agents/                        # Copilot CLI agent definitions
  .github/commands/                      # Copilot CLI slash commands
  .opencode/agents/                      # OpenCode agent definitions
  .opencode/commands/                    # OpenCode slash commands
  *.devin.md                              # Devin playbooks
```

## Platform Compatibility

This package works with **OpenCode**, **Claude Code**, **Codex CLI**, **Copilot CLI**, and **Devin**. Platform-native skill and agent files are generated from the canonical markdown source by running:

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

## The 9 Agents

The `workflow-orchestrator` is the primary coordinating agent (default in OpenCode). The other 8 are subagents invoked via `@<name>`:

| Agent | Role |
|-------|------|
| `workflow-orchestrator` | Coordinates all 18 phases, enforces gates, tracks progression |
| `intake-analyst` | Phase 1-3: intake, clarification, domain classification |
| `domain-researcher` | Phase 4-5: source review, external research |
| `workflow-architect` | Phase 6: workflow decomposition |
| `skill-architect` | Phase 7-8: agent and skill design |
| `implementation-planner` | Phase 9-10: file structure, draft creation |
| `quality-reviewer` | Phase 11: internal QC (runs `validate-package.py`) |
| `red-team-reviewer` | Phase 12: adversarial review |
| `final-packager` | Phase 14-15: final packaging, user summary |

## Build / Test / Validate

This is a documentation/package project — no build step. To validate:

```bash
# 1. Verify canonical file count (should be 64+)
find agent-packages/workflow-designer-agent -type f | wc -l

# 2. Regenerate platform-specific files after changing canonical source
python3 scripts/sync-platform-configs.py

# 3. Validate a generated workflow package
python3 scripts/validate-package.py generated-workflows/<package-name>

# 4. Verify platform files exist
ls .agents/skills/ .claude/agents/ .opencode/agents/ .github/agents/ .devin/agents/ .codex/agents/
```

## Conventions

- Agent and skill definitions are **markdown with YAML frontmatter**.
- The canonical source lives in `agent-packages/workflow-designer-agent/`.
- Platform-specific files (`.claude/`, `.codex/`, `.github/`, `.devin/`, `.opencode/`) are **generated** — never hand-edit them. Run the sync script after changing canonical files.
- Skills follow the [agentskills.io](https://agentskills.io) open standard (`SKILL.md` with `name` + `description` frontmatter).
- Output of `/flowstart` runs goes to `generated-workflows/<domain>-workflow/` (gitignored).

## Generated Workflow Packages

Running `/flowstart` produces a complete workflow package under `generated-workflows/`. Each package includes:

- Agent roster (10+ agents, each with 10 required sections)
- Reusable skills (8+ skills, each with 8 required sections)
- 18-phase workflow definition with gates
- Intake model with labelled assumptions
- Sourced research protocol with citations
- Quality control (15 quantitative criteria)
- Red-team review (6 perspectives)
- FMEA, traceability matrix, reliability plan
- Email templates, pricing recommendation, MVP roadmap
- Implementation guide

Generated packages are **gitignored** — they are outputs, not source.

## See Also

- `AGENTS.md` — master notice file (platform loaders import this)
- `agent-packages/workflow-designer-agent/README.md` — full package documentation
- `agent-packages/workflow-designer-agent/AGENTS.md` — operating instructions for the agent
- `agent-packages/workflow-designer-agent/implementation-guide.md` — step-by-step usage guide

## License

See the repository for license information.
