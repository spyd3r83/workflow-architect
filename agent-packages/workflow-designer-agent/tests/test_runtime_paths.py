import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import importlib.util
import re

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "agent-packages/workflow-designer-agent/enforcement"
sys.path.insert(0, str(SOURCE))
from run_operator import Operator
from run_store import token


class RuntimePaths(unittest.TestCase):
    def migration_case(self, baseline_name):
        self.ready(role="leaf", task_available=False)
        fixtures = Path(__file__).parent / "fixtures/legacy-hooks"
        provenance = json.loads((fixtures / "provenance.json").read_text())[
            baseline_name
        ]
        original = (fixtures / provenance["fixture"]).read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(), provenance["sha256"])
        config = self.store.read("run-one")["data"]["policy_config"]
        config["workflow_package"] = self.root.name
        self.store.update(
            "run-one", token(self.store.read("run-one")), {"policy_config": config}
        )
        local = self.root / "enforcement"
        local.mkdir()
        (local / "workflow-config.json").write_text(json.dumps(config))
        settings = self.root / ".claude/settings.json"
        settings.parent.mkdir()
        document = json.loads(original)
        guard = {
            "type": "command",
            "command": '"${CLAUDE_PROJECT_DIR}/security-domain-approval-check.sh"',
        }
        document["hooks"]["PreToolUse"][1]["hooks"].append(guard)
        document["hooks"]["PreToolUse"][1]["description"] = (
            "must retain security control"
        )
        settings.write_text(json.dumps(document))
        security = self.root / "security-domain-approval-check.sh"
        security.write_text(
            '#!/bin/sh\necho checked >> "$CLAUDE_PROJECT_DIR/security-ran.log"\n'
        )
        security.chmod(0o755)
        spec = importlib.util.spec_from_file_location(
            "sync_hooks", ROOT / "scripts/sync-platform-configs.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.sync_enforcement(self.root, self.root, SOURCE)
        migrated = json.loads(settings.read_text())
        self.assertIn(guard, migrated["hooks"]["PreToolUse"][1]["hooks"])
        self.assertEqual(
            migrated["hooks"]["PreToolUse"][1]["description"],
            "must retain security control",
        )
        self.check_migrated_lifecycle(migrated)
        first = {
            str(p.relative_to(self.root)): p.read_bytes()
            for directory in [".claude", "scripts/enforcement", "enforcement"]
            for p in (self.root / directory).rglob("*")
            if p.is_file()
        }
        module.sync_enforcement(self.root, self.root, SOURCE)
        second = {
            str(p.relative_to(self.root)): p.read_bytes()
            for directory in [".claude", "scripts/enforcement", "enforcement"]
            for p in (self.root / directory).rglob("*")
            if p.is_file()
        }
        self.assertEqual(first, second)

    def matching_hooks(self, settings, event, tool):
        return [
            hook
            for group in settings["hooks"][event]
            if group.get("matcher", "*") == "*" or re.search(group["matcher"], tool)
            for hook in group.get("hooks", [])
        ]

    def check_migrated_lifecycle(self, settings):
        workflow = (
            'bash "$CLAUDE_PROJECT_DIR/scripts/enforcement/dispatch-gate-hook.sh"'
        )
        legacy = {
            "${CLAUDE_PROJECT_DIR}/.claude/hooks/pre-tool-use.sh",
            "${CLAUDE_PROJECT_DIR}/.claude/hooks/pre-compact.sh",
            "${CLAUDE_PROJECT_DIR}/scripts/enforcement/dispatch-gate-hook.sh",
            workflow,
        }
        for event in ["PreToolUse", "PostToolUse", "PostToolUseFailure", "PreCompact"]:
            for tool in ["Write", "Edit", "Read", "apply_patch"]:
                count = sum(
                    hook["command"] in legacy
                    for hook in self.matching_hooks(settings, event, tool)
                )
                self.assertEqual(count, 1, (event, tool, count))
        for path in [
            self.root / ".claude/hooks/pre-tool-use.sh",
            self.root / ".claude/hooks/pre-compact.sh",
            self.root / "scripts/enforcement/dispatch-gate-hook.sh",
        ]:
            self.assertTrue(os.access(path, os.X_OK), path)
        payload = dict(
            cwd=str(self.root),
            session_id="session-one",
            tool_name="Write",
            tool_use_id="migration-write",
            tool_input={"file_path": "fixture.txt", "content": "migrated"},
        )
        self.execute_registered(settings, "PreToolUse", payload)
        self.assertEqual(self.store.read("run-one")["effects"], ["migration-write"])
        (self.root / "fixture.txt").write_text("migrated")
        self.execute_registered(
            settings, "PostToolUse", dict(payload, tool_response={"message": "written"})
        )
        self.assertEqual(self.store.read("run-one")["effects"], [])
        self.assertEqual(
            (self.root / "security-ran.log").read_text().splitlines(), ["checked"]
        )

    def execute_registered(self, settings, event, payload):
        for hook in self.matching_hooks(settings, event, payload["tool_name"]):
            result = subprocess.run(
                ["bash", "-c", hook["command"]],
                cwd=self.root,
                env=dict(
                    os.environ,
                    CLAUDE_PROJECT_DIR=str(self.root),
                    WORKFLOW_WORKSPACE=str(self.root),
                ),
                input=json.dumps(dict(payload, hook_event_name=event)),
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_original_root_settings_migrate_once_with_security_guard(self):
        self.migration_case("root")

    def test_original_network_settings_migrate_once_with_security_guard(self):
        self.migration_case("network")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "scripts/enforcement").mkdir(parents=True)
        (self.root / ".opencode").mkdir()
        (self.root / "opencode.json").write_text('{"default_agent":"coordinator"}')
        self.digest = hashlib.sha256(b"fixture-deliverable").hexdigest()
        names = [
            "run_store.py",
            "run_operator.py",
            "run_effects.py",
            "run_policy.py",
            "run_cli.py",
            "run_hook.py",
            "workflow-enforce.sh",
            "dispatch-gate-hook.sh",
        ]
        for name in names:
            shutil.copy2(SOURCE / name, self.root / "scripts/enforcement" / name)

    def ready(self, network=False, role="coordinator", task_available=True):
        package = ROOT / "generated-workflows/network-infrastructure-execution-workflow"
        config = json.loads((package / ".opencode/workflow-config.json").read_text())
        if not network:
            config.pop("specialist_phase_receipts")
            config.update(implementation_phases=[1], revision_phases=[1])
        shutil.copy2(
            package / "scripts/enforcement/network_policy.py",
            self.root / "scripts/enforcement/network_policy.py",
        )
        (self.root / ".opencode/workflow-config.json").write_text(json.dumps(config))
        self.op = Operator.bootstrap(self.root, b"f" * 32)
        actor = dict(
            role="coordinator",
            task_available=True,
            tools=["write", "apply_patch"],
            agents=["worker", "handoff-authenticator"],
            phases=[1],
            scope={"targets": ["fixture.txt"], "deliverable_digest": self.digest},
            completion_producers=["trusted", "claude-host", "opencode-host"],
            can_reconcile=True,
            host_reconcile=True,
        )
        self.op.create("run-one", "owner", "coordinator", actor, config, (None, 0, 0))
        profile = dict(
            actor,
            role=role,
            task_available=task_available,
            can_reconcile=role == "coordinator",
            host_reconcile=role == "coordinator",
        )
        self.op.enroll(
            "run-one", token(self.op.store.read("run-one")), "session-one", profile
        )
        self.store = self.op.store

    def request(self, action, **fields):
        state = self.store.bound("session-one")
        if action.endswith("-begin"):
            fields.setdefault(
                "arguments",
                {"subagent_type": fields.get("agent")}
                if action == "dispatch-begin"
                else {"filePath": str(self.root / "fixture.txt"), "content": "fixture"},
            )
            fields.setdefault("deliverable_digest", self.digest)
        if action in {"pass", "advance"}:
            fields.setdefault("deliverable_digest", self.digest)
        return dict(
            workspace=str(self.root),
            session_id="session-one",
            run_id="run-one",
            expected=token(state),
            action=action,
            **fields,
        )

    def execute(self, request):
        return subprocess.run(
            ["bash", str(self.root / "scripts/enforcement/workflow-enforce.sh")],
            input=json.dumps(request),
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=3,
        )

    def completion(self, effect):
        proof = self.op.attest(
            "run-one",
            token(self.store.read("run-one")),
            effect,
            "trusted",
            b"fixture completion",
            self.digest,
        )
        record = self.store.read("run-one")["data"]["effect_records"][effect]
        return self.request(
            "dispatch-end",
            dispatch_id=effect,
            effect_token=record["token"],
            identity_digest=record["identity_digest"],
            completion_digest=proof,
        )

    def call_hook(self, payload):
        payload = {
            "cwd": str(self.root),
            "session_id": "session-one",
            "hook_event_name": "PreToolUse",
            **payload,
        }
        return subprocess.run(
            ["bash", str(self.root / "scripts/enforcement/dispatch-gate-hook.sh")],
            cwd=self.root,
            env=dict(os.environ, WORKFLOW_WORKSPACE=str(self.root)),
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=4,
        )

    def test_actual_claude_missing_enforcer_denied(self):
        self.ready()
        (self.root / "scripts/enforcement/workflow-enforce.sh").unlink()
        self.assertNotEqual(
            self.call_hook(
                {
                    "tool_name": "Write",
                    "tool_input": {"file_path": "fixture.txt"},
                    "tool_use_id": "w1",
                }
            ).returncode,
            0,
        )

    def test_actual_dispatch_hook_missing_binding_denied(self):
        self.assertNotEqual(
            self.call_hook(
                {"tool_name": "Write", "tool_input": {"file_path": "fixture.txt"}}
            ).returncode,
            0,
        )

    def test_root_script_does_not_implicitly_initialize(self):
        result = subprocess.run(
            [
                "bash",
                str(self.root / "scripts/enforcement/workflow-enforce.sh"),
                "init",
            ],
            cwd=self.root,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / ".opencode/workflow-state.json").exists())

    def test_leaf_without_task_can_read_but_cannot_delegate(self):
        self.ready(role="leaf", task_available=False)
        self.assertEqual(
            self.execute(
                self.request(
                    "check", tool="read", arguments={"filePath": "fixture.txt"}
                )
            ).returncode,
            0,
        )
        self.assertNotEqual(
            self.execute(self.request("check", tool="task", arguments={})).returncode, 0
        )
        self.assertNotEqual(
            self.execute(
                self.request("pass", evidence="sufficient fixture evidence")
            ).returncode,
            0,
        )

    def test_coordinator_without_task_denied(self):
        self.ready(task_available=False)
        self.assertNotEqual(
            self.execute(self.request("check", tool="task", arguments={})).returncode, 0
        )

    def test_dispatch_agent_outside_handoff_denied(self):
        self.ready()
        self.assertNotEqual(
            self.execute(
                self.request("dispatch-begin", dispatch_id="d2", agent="unassigned")
            ).returncode,
            0,
        )

    def test_tool_end_cannot_consume_dispatch_effect(self):
        self.ready()
        result = self.execute(
            self.request("dispatch-begin", dispatch_id="parent-effect", agent="worker")
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotEqual(
            self.execute(
                self.request("tool-end", dispatch_id="parent-effect")
            ).returncode,
            0,
        )

    def test_network_gate_requires_completed_bound_receipt(self):
        self.ready(network=True)
        self.assertNotEqual(
            self.execute(
                self.request("pass", evidence="sufficient fixture evidence")
            ).returncode,
            0,
        )
        self.assertEqual(
            self.execute(
                self.request(
                    "dispatch-begin", dispatch_id="d1", agent="handoff-authenticator"
                )
            ).returncode,
            0,
        )
        self.assertEqual(self.execute(self.completion("d1")).returncode, 0)
        self.assertEqual(
            self.execute(
                self.request("pass", evidence="sufficient fixture evidence")
            ).returncode,
            0,
        )
        self.assertEqual(
            self.execute(
                self.request("advance", evidence="sufficient fixture evidence")
            ).returncode,
            0,
        )

    def test_network_retry_cannot_reuse_completed_receipt(self):
        self.ready(network=True)
        self.execute(
            self.request(
                "dispatch-begin", dispatch_id="d1", agent="handoff-authenticator"
            )
        )
        self.assertEqual(self.execute(self.completion("d1")).returncode, 0)
        self.assertEqual(
            self.execute(
                self.request("fail", evidence="fixture requires revision")
            ).returncode,
            0,
        )
        self.assertNotEqual(
            self.execute(
                self.request("pass", evidence="old receipt must not pass")
            ).returncode,
            0,
        )

    def test_stale_callback_and_wrong_run_are_byte_preserving(self):
        self.ready()
        self.execute(self.request("dispatch-begin", dispatch_id="d1", agent="worker"))
        callback = self.completion("d1")
        self.store.update("run-one", token(self.store.read("run-one")), {"newer": True})
        before = self.store.path("run-one").read_bytes()
        self.assertNotEqual(self.execute(callback).returncode, 0)
        self.assertEqual(before, self.store.path("run-one").read_bytes())
        self.assertNotEqual(
            self.execute(dict(self.request("status"), run_id="other")).returncode, 0
        )

    def test_corrupt_pointer_and_schema_deny_actual_script(self):
        self.ready()
        request = self.request(
            "check", tool="write", arguments={"filePath": "fixture.txt"}
        )
        (self.store.home / "active.json").write_text("{")
        self.assertNotEqual(self.execute(request).returncode, 0)
        (self.root / ".opencode/workflow-config.json").write_text(
            '{"schema_version":999}'
        )
        self.assertNotEqual(self.execute(request).returncode, 0)

    def test_hook_success_requires_explicit_allow_without_host_permission_override(
        self,
    ):
        self.ready(role="leaf", task_available=False)
        result = self.call_hook(
            {"tool_name": "Read", "tool_input": {"file_path": "fixture.txt"}}
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('"permissionDecision": "allow"', result.stdout)

    def test_hook_callback_uses_durable_identity_not_echoed_context(self):
        self.ready(role="leaf", task_available=False)
        payload = {
            "tool_name": "Write",
            "tool_use_id": "w1",
            "tool_input": {"file_path": "fixture.txt", "content": "fixture"},
        }
        self.assertEqual(self.call_hook(payload).returncode, 0)
        post = dict(
            payload, hook_event_name="PostToolUse", tool_response={"message": "written"}
        )
        self.assertNotEqual(
            self.call_hook(dict(post, tool_use_id="unknown")).returncode, 0
        )
        self.assertEqual(self.call_hook(post).returncode, 0)
        before = self.store.path("run-one").read_bytes()
        self.assertEqual(self.call_hook(post).returncode, 0)
        self.assertEqual(before, self.store.path("run-one").read_bytes())

    def test_hook_registered_failure_lifecycle(self):
        self.ready(role="leaf", task_available=False)
        payload = {
            "tool_name": "Write",
            "tool_use_id": "w1",
            "tool_input": {"file_path": "fixture.txt", "content": "fixture"},
        }
        self.assertEqual(self.call_hook(payload).returncode, 0)
        failed = self.call_hook(
            dict(payload, hook_event_name="PostToolUseFailure", error="fixture error")
        )
        self.assertEqual(failed.returncode, 0, failed.stdout)
        self.assertEqual(
            self.store.read("run-one")["data"]["effect_records"]["w1"]["status"],
            "failed",
        )

    def test_hook_task_adapter_is_explicitly_unsupported(self):
        self.ready()
        result = self.call_hook(
            {"tool_name": "Task", "tool_input": {}, "tool_use_id": "d1"}
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported", result.stdout)

    def test_hook_compaction_keeps_bound_run(self):
        self.ready()
        self.store.create("other", "owner", (None, 0, 0))
        result = self.call_hook({"hook_event_name": "PreCompact"})
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["run_id"], "run-one")

    def test_hook_timeout_and_bad_response_deny(self):
        self.ready()
        for body in ["sleep 3", "printf '{bad'", "exit 1"]:
            (self.root / "scripts/enforcement/workflow-enforce.sh").write_text(body)
            self.assertNotEqual(
                self.call_hook(
                    {"tool_name": "Write", "tool_input": {"file_path": "fixture.txt"}}
                ).returncode,
                0,
            )


if __name__ == "__main__":
    unittest.main()
