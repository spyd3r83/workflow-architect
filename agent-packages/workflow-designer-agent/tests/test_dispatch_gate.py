#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CANONICAL = REPO / "agent-packages" / "workflow-designer-agent" / "enforcement"
ENFORCE_SCRIPT = CANONICAL / "workflow-enforce.sh"


class DispatchGateTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="dispatch-gate-test-")
        self.pkg = Path(self.tmpdir)
        (self.pkg / ".opencode").mkdir()
        (self.pkg / "scripts" / "enforcement").mkdir(parents=True)
        shutil_copy = __import__("shutil").copy2
        shutil_copy(
            ENFORCE_SCRIPT, self.pkg / "scripts" / "enforcement" / "workflow-enforce.sh"
        )
        os.chmod(self.pkg / "scripts" / "enforcement" / "workflow-enforce.sh", 0o755)
        (self.pkg / ".opencode" / "workflow-config.json").write_text(
            json.dumps(
                {
                    "workflow_package": "test-pkg",
                    "total_phases": 18,
                    "implementation_phases": [9, 10],
                    "write_tools": [
                        "write",
                        "edit",
                        "apply_patch",
                        "str_replace_editor",
                        "create",
                    ],
                    "bash_is_conditional": True,
                    "max_revisions": 3,
                    "min_evidence_chars": 20,
                }
            )
        )
        subprocess.run(
            [
                "bash",
                str(self.pkg / "scripts" / "enforcement" / "workflow-enforce.sh"),
                "init",
            ],
            cwd=self.pkg,
            capture_output=True,
            timeout=10,
        )

    def tearDown(self):
        __import__("shutil").rmtree(self.tmpdir, ignore_errors=True)

    def _enforce(self, *args):
        return subprocess.run(
            [
                "bash",
                str(self.pkg / "scripts" / "enforcement" / "workflow-enforce.sh"),
                *args,
            ],
            cwd=self.pkg,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def _state(self):
        return json.loads((self.pkg / ".opencode" / "workflow-state.json").read_text())

    def test_init_sets_dispatch_failed_false(self):
        state = self._state()
        self.assertFalse(state.get("dispatch_failed", True))

    def test_dispatch_failed_sets_flag(self):
        result = self._enforce("dispatch-failed")
        self.assertEqual(result.returncode, 0)
        state = self._state()
        self.assertTrue(state["dispatch_failed"])

    def test_check_blocks_write_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce("check", "write", "/tmp/test.txt")
        self.assertIn("block:Dispatch failure", result.stdout)

    def test_check_blocks_bash_mutation_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce("check", "bash", "echo test > /tmp/test.txt")
        self.assertIn("block:Dispatch failure", result.stdout)

    def test_check_allows_read_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce("check", "read", "")
        self.assertIn("allow", result.stdout.lower())

    def test_check_allows_bash_readonly_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce("check", "bash", "ls -la")
        self.assertIn("allow", result.stdout.lower())

    def test_dispatch_clear_not_callable(self):
        self._enforce("dispatch-failed")
        result = self._enforce("dispatch-clear")
        state = self._state()
        self.assertTrue(
            state.get("dispatch_failed", False),
            "dispatch-clear must not clear the flag; only fail_gate can",
        )

    def test_fail_gate_clears_dispatch_failed(self):
        self._enforce("dispatch-failed")
        result = self._enforce("fail", "10", "test failure")
        self.assertEqual(result.returncode, 0)
        state = self._state()
        self.assertFalse(state.get("dispatch_failed", True))

    def test_pass_gate_blocked_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce(
            "pass",
            "1",
            "evidence that is long enough to pass the minimum char requirement",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dispatch_failed", result.stderr + result.stdout)

    def test_check_blocks_create_tool_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce("check", "create", "/tmp/test.txt")
        self.assertIn("block:Dispatch failure", result.stdout)

    def test_advance_blocked_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce(
            "advance",
            "2",
            "evidence that is long enough to pass the minimum char requirement",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dispatch_failed", result.stderr + result.stdout)

    def test_check_blocks_uppercase_bash_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce("check", "Bash", "echo test > /tmp/test.txt")
        self.assertIn("block:Dispatch failure", result.stdout)

    def test_check_blocks_uppercase_write_after_dispatch_failure(self):
        self._enforce("dispatch-failed")
        result = self._enforce("check", "Write", "/tmp/test.txt")
        self.assertIn("block:Dispatch failure", result.stdout)

    def test_dispatch_clear_not_in_case_statement(self):
        result = self._enforce("dispatch-clear")
        state = self._state()
        self.assertFalse(
            state.get("dispatch_failed", False),
            "dispatch-clear should not modify state when not in case statement",
        )

    def test_compaction_shows_dispatch_failed(self):
        self._enforce("dispatch-failed")
        result = self._enforce("compaction")
        self.assertIn("Dispatch Failed: True", result.stdout)

    def test_hook_script_blocks_after_dispatch_failure(self):
        hook_script = CANONICAL / "dispatch-gate-hook.sh"
        if not hook_script.exists():
            self.skipTest("hook script not found")
        self._enforce("dispatch-failed")
        hook_input = json.dumps(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "bash",
                "tool_input": {"command": "echo test > /tmp/test.txt"},
            }
        )
        result = subprocess.run(
            ["bash", str(hook_script)],
            input=hook_input,
            cwd=self.pkg,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("deny", result.stdout.lower())
        self.assertTrue(len(result.stderr.strip()) > 0)

    def test_hook_script_records_task_error(self):
        hook_script = CANONICAL / "dispatch-gate-hook.sh"
        if not hook_script.exists():
            self.skipTest("hook script not found")
        hook_input = json.dumps(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "task",
                "tool_response": "Skills not found: backend-discovery. Available: ...",
            }
        )
        subprocess.run(
            ["bash", str(hook_script)],
            input=hook_input,
            cwd=self.pkg,
            capture_output=True,
            text=True,
            timeout=10,
        )
        state = self._state()
        self.assertTrue(state.get("dispatch_failed", False))


class HarnessAdapterTests(unittest.TestCase):
    def test_claude_fragment_uses_settings_json_schema(self):
        fragment = CANONICAL / "hooks" / "claude-dispatch-gate-fragment.json"
        self.assertTrue(fragment.exists(), "Claude fragment must exist")
        data = json.loads(fragment.read_text())
        self.assertIn("hooks", data)
        self.assertIn("PreToolUse", data["hooks"])
        pre = data["hooks"]["PreToolUse"][0]
        self.assertIn("matcher", pre)
        self.assertIn("Bash", pre["matcher"])
        self.assertIn("Write", pre["matcher"])
        handler = pre["hooks"][0]
        self.assertEqual(handler["type"], "command")
        self.assertIn("${CLAUDE_PROJECT_DIR}", handler["command"])

    def test_claude_standalone_hooks_file_removed(self):
        standalone = CANONICAL / "hooks" / "claude-dispatch-gate.json"
        self.assertFalse(
            standalone.exists(),
            "Standalone .claude/hooks/*.json is NOT a Claude Code discovery path",
        )

    def test_copilot_uses_version_and_bash_field(self):
        config = CANONICAL / "hooks" / "copilot-dispatch-gate.json"
        self.assertTrue(config.exists())
        data = json.loads(config.read_text())
        self.assertEqual(data["version"], 1)
        self.assertIn("preToolUse", data["hooks"])
        handler = data["hooks"]["preToolUse"][0]
        self.assertIn("bash", handler)
        self.assertIn("timeoutSec", handler)

    def test_codex_uses_hooks_wrapper_and_command_type(self):
        config = CANONICAL / "hooks" / "codex-dispatch-gate.json"
        self.assertTrue(config.exists())
        data = json.loads(config.read_text())
        self.assertIn("hooks", data)
        self.assertIn("PreToolUse", data["hooks"])
        handler = data["hooks"]["PreToolUse"][0]["hooks"][0]
        self.assertEqual(handler["type"], "command")
        self.assertIn("command", handler)

    def test_devin_uses_flat_format_and_exec_tool_name(self):
        config = CANONICAL / "hooks" / "devin-dispatch-gate.json"
        self.assertTrue(config.exists())
        data = json.loads(config.read_text())
        self.assertNotIn(
            "hooks", data, "Devin hooks.v1.json must be flat (no wrapper key)"
        )
        self.assertIn("PreToolUse", data)
        matcher = data["PreToolUse"][0]["matcher"]
        self.assertIn("exec", matcher)
        self.assertIn("edit", matcher)
        self.assertNotIn("Bash", matcher, "Devin uses exec, not Bash")

    def test_dispatch_gate_spec_documents_verified_schemas(self):
        spec = CANONICAL / "dispatch-gate.md"
        self.assertTrue(spec.exists())
        text = spec.read_text()
        self.assertIn("settings.json", text)
        self.assertIn("version", text.lower())
        self.assertIn("trust review", text.lower())
        self.assertNotIn("may be required depending on version", text)

    def test_spec_documents_copilot_toolArgs_and_toolResult(self):
        spec = CANONICAL / "dispatch-gate.md"
        text = spec.read_text()
        self.assertIn("toolArgs", text)
        self.assertIn("toolResult", text)

    def test_spec_documents_claude_agent_tool_name(self):
        spec = CANONICAL / "dispatch-gate.md"
        text = spec.read_text()
        self.assertIn("Agent", text)

    def test_spec_documents_copilot_create_tool(self):
        spec = CANONICAL / "dispatch-gate.md"
        text = spec.read_text()
        self.assertIn("create", text.lower())

    def test_sync_preserves_existing_claude_settings(self):
        import tempfile
        import shutil as _shutil

        tmp = tempfile.mkdtemp()
        pkg = Path(tmp) / "test-pkg"
        pkg.mkdir()
        (pkg / "opencode.json").write_text(json.dumps({"default_agent": "test-agent"}))
        claude_dir = pkg / ".claude"
        claude_dir.mkdir()
        existing_settings = {
            "permissions": {"allow": ["Read"]},
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Read",
                        "hooks": [{"type": "command", "command": "echo hi"}],
                    }
                ]
            },
        }
        (claude_dir / "settings.json").write_text(
            json.dumps(existing_settings, indent=2)
        )
        subprocess.run(
            [
                sys.executable,
                str(REPO / "scripts" / "sync-platform-configs.py"),
                "--package",
                str(pkg),
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        merged = json.loads((claude_dir / "settings.json").read_text())
        self.assertIn("permissions", merged, "Pre-existing settings must be preserved")
        self.assertIn("allow", merged["permissions"])
        pre = merged.get("hooks", {}).get("PreToolUse", [])
        self.assertEqual(
            len(pre), 2, "Should have 2 PreToolUse entries (existing + dispatch-gate)"
        )
        _shutil.rmtree(tmp, ignore_errors=True)

    def test_hook_script_handles_devin_exec_tool_name(self):
        hook_script = CANONICAL / "dispatch-gate-hook.sh"
        if not hook_script.exists():
            self.skipTest("hook script not found")
        tmp = tempfile.mkdtemp()
        pkg = Path(tmp)
        (pkg / ".opencode").mkdir()
        (pkg / "scripts" / "enforcement").mkdir(parents=True)
        shutil_copy = __import__("shutil").copy2
        shutil_copy(
            ENFORCE_SCRIPT, pkg / "scripts" / "enforcement" / "workflow-enforce.sh"
        )
        os.chmod(pkg / "scripts" / "enforcement" / "workflow-enforce.sh", 0o755)
        (pkg / ".opencode" / "workflow-config.json").write_text(
            json.dumps(
                {
                    "workflow_package": "test",
                    "total_phases": 18,
                    "implementation_phases": [9, 10],
                    "write_tools": [
                        "write",
                        "edit",
                        "apply_patch",
                        "str_replace_editor",
                        "create",
                    ],
                    "bash_is_conditional": True,
                    "max_revisions": 3,
                    "min_evidence_chars": 20,
                }
            )
        )
        subprocess.run(
            [
                "bash",
                str(pkg / "scripts" / "enforcement" / "workflow-enforce.sh"),
                "init",
            ],
            cwd=pkg,
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            [
                "bash",
                str(pkg / "scripts" / "enforcement" / "workflow-enforce.sh"),
                "dispatch-failed",
            ],
            cwd=pkg,
            capture_output=True,
            timeout=10,
        )
        devin_input = json.dumps(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "exec",
                "tool_input": {"command": "echo test > /tmp/test.txt"},
                "session_id": "test-session",
            }
        )
        result = subprocess.run(
            ["bash", str(hook_script)],
            input=devin_input,
            cwd=pkg,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("deny", result.stdout.lower())
        __import__("shutil").rmtree(tmp, ignore_errors=True)

    def test_hook_script_handles_devin_posttooluse_object_response(self):
        hook_script = CANONICAL / "dispatch-gate-hook.sh"
        if not hook_script.exists():
            self.skipTest("hook script not found")
        tmp = tempfile.mkdtemp()
        pkg = Path(tmp)
        (pkg / ".opencode").mkdir()
        (pkg / "scripts" / "enforcement").mkdir(parents=True)
        shutil_copy = __import__("shutil").copy2
        shutil_copy(
            ENFORCE_SCRIPT, pkg / "scripts" / "enforcement" / "workflow-enforce.sh"
        )
        os.chmod(pkg / "scripts" / "enforcement" / "workflow-enforce.sh", 0o755)
        (pkg / ".opencode" / "workflow-config.json").write_text(
            json.dumps(
                {
                    "workflow_package": "test",
                    "total_phases": 18,
                    "implementation_phases": [9, 10],
                    "write_tools": [
                        "write",
                        "edit",
                        "apply_patch",
                        "str_replace_editor",
                        "create",
                    ],
                    "bash_is_conditional": True,
                    "max_revisions": 3,
                    "min_evidence_chars": 20,
                }
            )
        )
        subprocess.run(
            [
                "bash",
                str(pkg / "scripts" / "enforcement" / "workflow-enforce.sh"),
                "init",
            ],
            cwd=pkg,
            capture_output=True,
            timeout=10,
        )
        devin_postuse_input = json.dumps(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "task",
                "tool_input": {},
                "tool_response": {
                    "success": False,
                    "output": "",
                    "error": "Skills not found: backend-discovery",
                },
            }
        )
        subprocess.run(
            ["bash", str(hook_script)],
            input=devin_postuse_input,
            cwd=pkg,
            capture_output=True,
            text=True,
            timeout=10,
        )
        state = json.loads((pkg / ".opencode" / "workflow-state.json").read_text())
        self.assertTrue(state.get("dispatch_failed", False))
        __import__("shutil").rmtree(tmp, ignore_errors=True)

    def test_hook_script_handles_copilot_toolArgs_field(self):
        hook_script = CANONICAL / "dispatch-gate-hook.sh"
        if not hook_script.exists():
            self.skipTest("hook script not found")
        tmp = tempfile.mkdtemp()
        pkg = Path(tmp)
        (pkg / ".opencode").mkdir()
        (pkg / "scripts" / "enforcement").mkdir(parents=True)
        shutil_copy = __import__("shutil").copy2
        shutil_copy(
            ENFORCE_SCRIPT, pkg / "scripts" / "enforcement" / "workflow-enforce.sh"
        )
        os.chmod(pkg / "scripts" / "enforcement" / "workflow-enforce.sh", 0o755)
        (pkg / ".opencode" / "workflow-config.json").write_text(
            json.dumps(
                {
                    "workflow_package": "test",
                    "total_phases": 18,
                    "implementation_phases": [9, 10],
                    "write_tools": [
                        "write",
                        "edit",
                        "apply_patch",
                        "str_replace_editor",
                        "create",
                    ],
                    "bash_is_conditional": True,
                    "max_revisions": 3,
                    "min_evidence_chars": 20,
                }
            )
        )
        subprocess.run(
            [
                "bash",
                str(pkg / "scripts" / "enforcement" / "workflow-enforce.sh"),
                "init",
            ],
            cwd=pkg,
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            [
                "bash",
                str(pkg / "scripts" / "enforcement" / "workflow-enforce.sh"),
                "dispatch-failed",
            ],
            cwd=pkg,
            capture_output=True,
            timeout=10,
        )
        copilot_input = json.dumps(
            {
                "hookEventName": "preToolUse",
                "toolName": "create",
                "toolArgs": {"filePath": "/tmp/test.txt"},
            }
        )
        result = subprocess.run(
            ["bash", str(hook_script)],
            input=copilot_input,
            cwd=pkg,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        __import__("shutil").rmtree(tmp, ignore_errors=True)

    def test_hook_script_matches_agent_tool_name(self):
        hook_script = CANONICAL / "dispatch-gate-hook.sh"
        if not hook_script.exists():
            self.skipTest("hook script not found")
        tmp = tempfile.mkdtemp()
        pkg = Path(tmp)
        (pkg / ".opencode").mkdir()
        (pkg / "scripts" / "enforcement").mkdir(parents=True)
        shutil_copy = __import__("shutil").copy2
        shutil_copy(
            ENFORCE_SCRIPT, pkg / "scripts" / "enforcement" / "workflow-enforce.sh"
        )
        os.chmod(pkg / "scripts" / "enforcement" / "workflow-enforce.sh", 0o755)
        (pkg / ".opencode" / "workflow-config.json").write_text(
            json.dumps(
                {
                    "workflow_package": "test",
                    "total_phases": 18,
                    "implementation_phases": [9, 10],
                    "write_tools": [
                        "write",
                        "edit",
                        "apply_patch",
                        "str_replace_editor",
                        "create",
                    ],
                    "bash_is_conditional": True,
                    "max_revisions": 3,
                    "min_evidence_chars": 20,
                }
            )
        )
        subprocess.run(
            [
                "bash",
                str(pkg / "scripts" / "enforcement" / "workflow-enforce.sh"),
                "init",
            ],
            cwd=pkg,
            capture_output=True,
            timeout=10,
        )
        agent_input = json.dumps(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Agent",
                "tool_input": {},
                "tool_response": {"error": "Skills not found: backend-discovery"},
            }
        )
        subprocess.run(
            ["bash", str(hook_script)],
            input=agent_input,
            cwd=pkg,
            capture_output=True,
            text=True,
            timeout=10,
        )
        state = json.loads((pkg / ".opencode" / "workflow-state.json").read_text())
        self.assertTrue(state.get("dispatch_failed", False))
        __import__("shutil").rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
