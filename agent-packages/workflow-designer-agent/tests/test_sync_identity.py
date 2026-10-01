#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SYNC_SCRIPT = REPO / "scripts" / "sync-platform-configs.py"
CANONICAL_ENFORCEMENT = (
    REPO / "agent-packages" / "workflow-designer-agent" / "enforcement"
)


class SyncIdentityTests(unittest.TestCase):
    def test_q5_mixed_hook_groups_preserve_unrelated_controls(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("sync", SYNC_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        target = Path(self.tmpdir) / "settings.json"
        owned = json.loads((CANONICAL_ENFORCEMENT / "settings.json").read_text())[
            "hooks"
        ]["PreToolUse"][0]["hooks"][0]
        guard = {"type": "command", "command": "security-domain-approval-check"}
        similar = {"type": "command", "command": "bash custom/pre-tool-use.sh.guard"}
        groups = [
            {
                "matcher": "Bash",
                "description": "domain guard",
                "hooks": [owned, guard, similar],
            },
            {"matcher": "Edit", "custom_metadata": "retain", "hooks": [owned]},
            {
                "matcher": "*",
                "hooks": [
                    {
                        "type": "command",
                        "command": "echo dispatch-gate-hook.sh && security-check",
                    }
                ],
            },
        ]
        target.write_text(json.dumps({"hooks": {"PreToolUse": groups}}))
        module.merge_runtime_hooks(CANONICAL_ENFORCEMENT / "settings.json", target)
        first = target.read_bytes()
        result = json.loads(first)["hooks"]["PreToolUse"]
        self.assertIn(guard, result[0]["hooks"])
        self.assertIn(similar, result[0]["hooks"])
        self.assertEqual(result[0]["description"], "domain guard")
        self.assertEqual(result[1]["custom_metadata"], "retain")
        self.assertIn("security-check", json.dumps(result))
        module.merge_runtime_hooks(CANONICAL_ENFORCEMENT / "settings.json", target)
        self.assertEqual(first, target.read_bytes())

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(
            prefix="sync-identity-test-", dir=Path(__file__).parent
        )

    def test_runtime_dependencies_and_local_policy_survive_two_syncs(self):
        pkg = self._make_minimal_package("network-fixture")
        local = pkg / "enforcement"
        local.mkdir()
        config = json.loads(
            (CANONICAL_ENFORCEMENT / "workflow-config.json").read_text()
        )
        config.update(
            workflow_package="network-fixture",
            total_phases=17,
            specialist_phase_receipts={"1": "specialist"},
        )
        (local / "workflow-config.json").write_text(json.dumps(config))
        (local / "network_policy.py").write_text('POLICY = "retained specialist"\n')
        command = [
            sys.executable,
            "-B",
            str(SYNC_SCRIPT),
            "--package",
            str(pkg),
            "--runtime-source",
            str(CANONICAL_ENFORCEMENT),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        first = {
            str(p.relative_to(pkg)): p.read_bytes()
            for p in pkg.rglob("*")
            if p.is_file()
        }
        subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(
            first,
            {
                str(p.relative_to(pkg)): p.read_bytes()
                for p in pkg.rglob("*")
                if p.is_file()
            },
        )
        self.assertTrue((pkg / "scripts/enforcement/run_store.py").exists())
        self.assertEqual(
            (pkg / "scripts/enforcement/network_policy.py").read_text(),
            'POLICY = "retained specialist"\n',
        )
        self.assertEqual(
            json.loads((pkg / ".opencode/workflow-config.json").read_text())[
                "specialist_phase_receipts"
            ],
            {"1": "specialist"},
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_minimal_package(self, name: str) -> Path:
        pkg = Path(self.tmpdir, name)
        pkg.mkdir(parents=True)
        (pkg / "opencode.json").write_text(
            json.dumps(
                {
                    "default_agent": "test-agent",
                    "agent": {"test-agent": {"mode": "primary"}},
                }
            )
        )
        return pkg

    def test_synced_config_has_package_name_not_workflow_designer(self):
        pkg = self._make_minimal_package("my-deployment-workflow")
        result = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), "--package", str(pkg)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        config_path = pkg / ".opencode" / "workflow-config.json"
        self.assertTrue(config_path.exists(), "workflow-config.json must be synced")
        data = json.loads(config_path.read_text())
        self.assertEqual(
            data["workflow_package"],
            "my-deployment-workflow",
            "workflow_package must be derived from the output directory name, not copied from canonical source",
        )
        config_path = pkg / ".opencode" / "workflow-config.json"
        self.assertTrue(config_path.exists(), "workflow-config.json must be synced")
        data = json.loads(config_path.read_text())
        self.assertEqual(
            data["workflow_package"],
            "my-deployment-workflow",
            "workflow_package must be derived from the output directory name, not copied from canonical source",
        )

    def test_canonical_source_has_workflow_designer_agent(self):
        config = CANONICAL_ENFORCEMENT / "workflow-config.json"
        self.assertTrue(config.exists(), "canonical workflow-config.json must exist")
        data = json.loads(config.read_text())
        self.assertEqual(
            data["workflow_package"],
            "workflow-designer-agent",
            "canonical source should have workflow-designer-agent as its package name",
        )

    def test_two_different_packages_get_different_identity(self):
        pkg_a = self._make_minimal_package("alpha-workflow")
        pkg_b = self._make_minimal_package("beta-workflow")
        for pkg in [pkg_a, pkg_b]:
            subprocess.run(
                [sys.executable, str(SYNC_SCRIPT), "--package", str(pkg)],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=30,
            )
        config_a = json.loads(
            (pkg_a / ".opencode" / "workflow-config.json").read_text()
        )
        config_b = json.loads(
            (pkg_b / ".opencode" / "workflow-config.json").read_text()
        )
        self.assertEqual(config_a["workflow_package"], "alpha-workflow")
        self.assertEqual(config_b["workflow_package"], "beta-workflow")
        self.assertNotEqual(config_a["workflow_package"], config_b["workflow_package"])

    def test_existing_deployment_package_config_has_correct_identity(self):
        dep = (
            REPO
            / "generated-workflows"
            / "internal-application-ingress-deployment-workflow"
        )
        if not dep.is_dir():
            self.skipTest("deployment package not found")
        config = dep / ".opencode" / "workflow-config.json"
        if not config.exists():
            self.skipTest("deployment config not found")
        data = json.loads(config.read_text())
        self.assertEqual(
            data["workflow_package"],
            "internal-application-ingress-deployment-workflow",
            "existing deployment package must have its own identity, not workflow-designer-agent",
        )


if __name__ == "__main__":
    unittest.main()
