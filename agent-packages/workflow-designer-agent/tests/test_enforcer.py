#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO
    / "agent-packages"
    / "workflow-designer-agent"
    / "enforcement"
    / "workflow-enforce.sh"
)
CONFIG_TEMPLATE = {
    "workflow_package": "test-package",
    "total_phases": 15,
    "implementation_phases": [9, 10],
    "revision_phases": [9, 10, 11, 12, 13],
    "write_tools": ["write", "edit", "apply_patch", "str_replace_editor"],
    "bash_is_conditional": True,
    "max_revisions": 3,
    "min_evidence_chars": 20,
}


class EnforcerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".opencode").mkdir()
        self.config = self.root / ".opencode" / "workflow-config.json"
        self.state = self.root / ".opencode" / "workflow-state.json"
        self.config.write_text(json.dumps(CONFIG_TEMPLATE, indent=2))
        self.env = os.environ.copy()
        self.env["WORKFLOW_CONFIG_FILE"] = str(self.config)
        self.env["WORKFLOW_STATE_FILE"] = str(self.state)

    def tearDown(self):
        self.tmp.cleanup()

    def run_enforce(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(SCRIPT), *args],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def check(self, tool: str, arg: str = "") -> str:
        cp = self.run_enforce("check", tool, arg)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        return cp.stdout.strip()

    def test_init_and_readonly_blocks_write(self):
        cp = self.run_enforce("init")
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(self.check("write").startswith("block:"))
        self.assertTrue(self.check("edit").startswith("block:"))
        self.assertTrue(self.check("apply_patch").startswith("block:"))
        self.assertEqual(self.check("bash", "git status"), "allow")
        self.assertEqual(self.check("read"), "allow")

    def test_implementation_phase_allows_local_mutation(self):
        self.run_enforce("init")
        state = json.loads(self.state.read_text())
        state["current_phase"] = 9
        state["phases"]["9"] = {"status": "in_progress", "gate": "pending"}
        self.state.write_text(json.dumps(state, indent=2))
        self.assertEqual(self.check("write"), "allow")
        self.assertEqual(self.check("apply_patch"), "allow")
        self.assertEqual(self.check("bash", "git add ."), "allow")

    def test_revision_mode_allows_local_mutation_after_fail(self):
        self.run_enforce("init")
        state = json.loads(self.state.read_text())
        state["current_phase"] = 11
        state["phases"]["11"] = {"status": "in_progress", "gate": "pending"}
        self.state.write_text(json.dumps(state, indent=2))
        self.assertTrue(self.check("write").startswith("block:"))
        cp = self.run_enforce("fail", "11", "QC failed needs repair")
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("revision_mode=true", cp.stdout)
        self.assertEqual(self.check("write"), "allow")
        self.assertEqual(self.check("edit"), "allow")
        self.assertEqual(self.check("apply_patch"), "allow")

    def test_enter_revision_and_recover_deadlock(self):
        self.run_enforce("init")
        self.assertTrue(self.check("write").startswith("block:"))
        cp = self.run_enforce(
            "enter_revision",
            "13",
            "Revision loop authorized after QC failure with concrete fixes pending",
        )
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertEqual(self.check("write"), "allow")

        state = json.loads(self.state.read_text())
        state["revision_mode"] = False
        state["current_phase"] = 1
        state["phases"]["1"] = {"status": "in_progress", "gate": "pending"}
        self.state.write_text(json.dumps(state, indent=2))
        self.assertTrue(self.check("write").startswith("block:"))
        cp = self.run_enforce(
            "recover",
            "Recovered stale deadlock by re-entering revision at implementation phase",
        )
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertEqual(self.check("write"), "allow")
        state = json.loads(self.state.read_text())
        self.assertTrue(state["revision_mode"])
        self.assertEqual(state["current_phase"], 9)

    def test_external_push_requires_approval_even_in_revision(self):
        self.run_enforce("init")
        self.run_enforce(
            "enter_revision",
            "9",
            "Revision authorized for local repairs after red-team findings",
        )
        self.assertEqual(self.check("write"), "allow")
        self.assertTrue(
            self.check("bash", "git push origin master").startswith("block:")
        )
        self.assertTrue(self.check("bash", "gh release create v1").startswith("block:"))
        cp = self.run_enforce(
            "approve",
            "external_actions",
            "User approved external push for release after local validation passed",
        )
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertEqual(self.check("bash", "git push origin master"), "allow")

    def test_call_omo_agent_always_blocked(self):
        self.run_enforce("init")
        out = self.check("call_omo_agent")
        self.assertTrue(out.startswith("block:"))
        self.assertIn("task(subagent_type", out)


if __name__ == "__main__":
    unittest.main()
