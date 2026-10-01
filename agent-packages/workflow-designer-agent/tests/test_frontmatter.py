#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_frontmatter import (  # noqa: E402
    extract_frontmatter,
    validate_frontmatter_text,
    validate_generated_workflows_tree,
    validate_package_frontmatter,
)


def load_sync_module():
    path = SCRIPTS / "sync-platform-configs.py"
    spec = importlib.util.spec_from_file_location("sync_platform_configs", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class FrontmatterTests(unittest.TestCase):
    def test_yaml_block_scalar_helper(self):
        if yaml is None:
            self.skipTest("pyyaml not installed")
        mod = load_sync_module()
        out = mod.yaml_block_scalar("Checks API changes. Use when: Phase 4")
        self.assertTrue(out.startswith("|\n"))
        parsed = yaml.safe_load("description: " + out)
        self.assertIsInstance(parsed, dict)
        self.assertIsInstance(parsed["description"], str)
        self.assertIn("Use when: Phase 4", parsed["description"])

    def test_generator_emits_valid_block_scalar_frontmatter(self):
        if yaml is None:
            self.skipTest("pyyaml not installed")
        mod = load_sync_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = [
                {
                    "name": "demo-skill",
                    "description": "Does work. Use when: Phase 1: setup and scan",
                    "body": "# Skill\n\n## Purpose\nDemo\n",
                }
            ]
            agents = [
                {
                    "name": "demo-agent",
                    "description": "Inspects repo: maps packages and boundaries",
                    "body": "# Agent\n\n## Role\nDemo\n",
                }
            ]
            mod.write_skill_files(skills, root)
            mod.write_claude_agents(agents, root)
            mod.write_opencode_agents(agents, root, "demo-agent")
            mod.write_github_agents(agents, root)
            mod.write_devin_agents(agents, root)

            targets = [
                root / ".agents" / "skills" / "demo-skill" / "SKILL.md",
                root / ".claude" / "agents" / "demo-agent.md",
                root / ".opencode" / "agents" / "demo-agent.md",
                root / ".github" / "agents" / "demo-agent.agent.md",
                root / ".devin" / "agents" / "demo-agent" / "AGENT.md",
            ]
            for path in targets:
                self.assertTrue(path.exists(), msg=str(path))
                text = path.read_text()
                self.assertIn("description: |", text)
                self.assertEqual(validate_frontmatter_text(text), [])
                fm, err = extract_frontmatter(text)
                self.assertIsNone(err)
                data = yaml.safe_load(fm)
                self.assertIsInstance(data, dict)
                self.assertIsInstance(data.get("description"), str)

    def test_validator_rejects_invalid_plain_scalar_with_colon(self):
        bad = (
            "---\n"
            "name: broken\n"
            "description: Bad text. Use when: Phase 1\n"
            "---\n\n"
            "# Body\n"
        )
        errs = validate_frontmatter_text(bad)
        self.assertTrue(errs, "expected invalid frontmatter to fail")

    def test_validator_rejects_non_standalone_closing_delimiter(self):
        bad = "---\nname: x\ndescription: ok\n---# Body\n"
        errs = validate_frontmatter_text(bad)
        self.assertTrue(
            any("non-standalone" in e or "closing" in e for e in errs), errs
        )

    def test_repo_root_harness_frontmatter_valid(self):
        report = validate_package_frontmatter(REPO)
        self.assertEqual(report["overall"], "PASS", report.get("errors")[:10])
        self.assertGreater(report["files_with_frontmatter"], 0)

    def test_backend_generated_package_frontmatter_valid(self):
        pkg = REPO / "generated-workflows" / "backend-repo-maintenance-workflow"
        if not pkg.exists():
            self.skipTest("backend generated package absent (gitignored)")
        report = validate_package_frontmatter(pkg)
        self.assertEqual(report["overall"], "PASS", report.get("errors")[:10])
        self.assertGreater(report["files_with_frontmatter"], 0)

    def test_recursive_generated_workflows_scan(self):
        gen_root = REPO / "generated-workflows"
        if not gen_root.exists():
            self.skipTest("generated-workflows/ absent (gitignored)")
        report = validate_generated_workflows_tree(gen_root)
        self.assertEqual(report["overall"], "PASS", report)
        names = {p["name"] for p in report["packages"]}
        if "backend-repo-maintenance-workflow" in names:
            for pkg in report["packages"]:
                self.assertEqual(pkg["overall"], "PASS", pkg)

    def test_generated_tree_scan_fails_on_bad_package(self):
        if yaml is None:
            self.skipTest("pyyaml not installed")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = root / "good-package" / ".agents" / "skills" / "ok"
            good.mkdir(parents=True)
            (good / "SKILL.md").write_text(
                "---\nname: ok\ndescription: |\n  Safe description\n---\n\n# Body\n"
            )
            bad = root / "bad-package" / ".agents" / "skills" / "broken"
            bad.mkdir(parents=True)
            (bad / "SKILL.md").write_text(
                "---\nname: broken\ndescription: Bad text. Use when: Phase 1\n---\n\n# Body\n"
            )
            report = validate_generated_workflows_tree(root)
            self.assertEqual(report["overall"], "FAIL", report)
            by_name = {p["name"]: p for p in report["packages"]}
            self.assertEqual(by_name["good-package"]["overall"], "PASS")
            self.assertEqual(by_name["bad-package"]["overall"], "FAIL")
            self.assertGreater(by_name["bad-package"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()
