import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import multiprocessing
import os
import shutil
import subprocess
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "enforcement"
sys.path.insert(0, str(SOURCE))
NETWORK = (
    Path(__file__).resolve().parents[3]
    / "generated-workflows/network-infrastructure-execution-workflow"
)
sys.path.append(str(NETWORK / "scripts/enforcement"))
from run_store import token
import run_cli


def reconcile_worker(root, request, queue):
    try:
        run_cli.execute_for(Path(root), request)
        queue.put("accepted")
    except Exception:
        queue.put("denied")


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        from run_operator import Operator

        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "opencode.json").write_text('{"default_agent":"coordinator"}')
        self.op = Operator.bootstrap(self.root, b"f" * 32)
        self.config = {
            "schema_version": 1,
            "total_phases": 2,
            "min_evidence_chars": 20,
            "max_revisions": 3,
            "implementation_phases": [1],
            "revision_phases": [1],
        }
        (self.root / ".opencode/workflow-config.json").write_text(
            json.dumps(self.config)
        )
        self.profile = {
            "can_reconcile": True,
            "role": "coordinator",
            "task_available": True,
            "tools": ["write"],
            "phases": [1],
            "agents": ["worker"],
            "scope": {"targets": ["fixture.txt", "wa.txt", "wb.txt"]},
            "completion_producers": ["trusted"],
        }
        self.op.create("r1", "owner", "parent", self.profile, self.config, (None, 0, 0))
        self.store = self.op.store
        self.digest = hashlib.sha256(b"deliverable").hexdigest()

    def request(self, action, session="parent", **extra):
        if action == "tool-begin" and "arguments" not in extra:
            name = extra.get("dispatch_id")
            path = name + ".txt" if name in {"wa", "wb"} else "fixture.txt"
            extra["arguments"] = {
                "filePath": str(self.root / path),
                "content": "fixture",
            }
        state = self.store.bound(session)
        return dict(
            workspace=str(self.root),
            run_id="r1",
            session_id=session,
            expected=list(token(state)),
            action=action,
            **extra,
        )

    def execute(self, request):
        return run_cli.execute_for(self.root, request)

    def begin(self, children=("child",)):
        self.execute(
            self.request(
                "dispatch-begin",
                dispatch_id="d1",
                agent="worker",
                child_sessions=list(children),
                deliverable_digest=self.digest,
            )
        )
        return self.store.read("r1")["data"]["effect_records"]["d1"]

    def enroll(self, session):
        profile = dict(
            self.profile,
            role="leaf",
            can_reconcile=False,
            task_available=False,
            agents=[],
            parent_effect="d1",
        )
        self.op.enroll("r1", token(self.store.read("r1")), session, profile)

    def attest(self, effect, session="parent"):
        return self.op.attest(
            "r1",
            token(self.store.read("r1")),
            effect,
            "trusted",
            b"fixture verified completion",
            self.digest,
        )

    def complete(self, effect, session, proof, reconcile=False):
        record = self.store.read("r1")["data"]["effect_records"][effect]
        action = (
            "reconcile-effect"
            if reconcile
            else ("dispatch-end" if record["kind"] == "dispatch" else "tool-end")
        )
        return self.request(
            action,
            session,
            dispatch_id=effect,
            effect_token=record["token"],
            identity_digest=record["identity_digest"],
            completion_digest=proof,
            reason="explicit fixture reconciliation with witnessed completion",
            reason_provenance={"source": "operator attestation", "reference": proof},
        )

    def child_done(self, session, call):
        self.execute(
            self.request(
                "tool-begin",
                session,
                dispatch_id=call,
                tool="write",
                deliverable_digest=self.digest,
            )
        )
        proof = self.attest(call, session)
        self.execute(self.complete(call, session, proof))
        self.op.close_child(
            "r1", token(self.store.read("r1")), session, "fixture child exited"
        )

    def test_nested_stale_original_then_explicit_reconcile(self):
        record = self.begin()
        stale = self.request(
            "dispatch-end",
            dispatch_id="d1",
            effect_token=record["token"],
            identity_digest=record["identity_digest"],
        )
        self.enroll("child")
        self.child_done("child", "write1")
        proof = self.attest("d1")
        before = self.store.path("r1").read_bytes()
        with self.assertRaises(Exception):
            self.execute(dict(stale, completion_digest=proof))
        self.assertEqual(before, self.store.path("r1").read_bytes())
        request = self.complete("d1", "parent", proof, True)
        version = self.store.read("r1")["state_version"]
        self.execute(request)
        self.assertEqual(self.store.read("r1")["state_version"], version + 1)
        self.assertEqual(self.store.read("r1")["data"]["revision_count"], 0)
        before = self.store.path("r1").read_bytes()
        self.execute(request)
        self.assertEqual(before, self.store.path("r1").read_bytes())
        self.assertEqual(self.store.read("r1")["effects"], [])
        self.execute(
            self.request(
                "pass",
                evidence="verified fixture delivery gate",
                deliverable_digest=self.digest,
            )
        )

    def test_reverse_children_and_conflicting_replay(self):
        self.begin(("a", "b"))
        self.enroll("a")
        self.enroll("b")
        self.execute(
            self.request(
                "tool-begin",
                "a",
                dispatch_id="wa",
                tool="write",
                deliverable_digest=self.digest,
            )
        )
        self.execute(
            self.request(
                "tool-begin",
                "b",
                dispatch_id="wb",
                tool="write",
                deliverable_digest=self.digest,
            )
        )
        self.execute(self.complete("wb", "b", self.attest("wb")))
        self.op.close_child(
            "r1", token(self.store.read("r1")), "b", "fixture child b exited"
        )
        with self.assertRaises(Exception):
            self.attest("d1")
        self.execute(self.complete("wa", "a", self.attest("wa")))
        self.op.close_child(
            "r1", token(self.store.read("r1")), "a", "fixture child a exited"
        )
        proof = self.attest("d1")
        request = self.complete("d1", "parent", proof, True)
        self.execute(request)
        with self.assertRaises(Exception):
            self.execute(dict(request, reason="conflicting replay"))

    def test_leaf_cannot_complete_parent_or_substitute_identity(self):
        record = self.begin()
        self.enroll("child")
        before = self.store.path("r1").read_bytes()
        for field, value in [
            ("effect_token", "forged"),
            ("identity_digest", "0" * 64),
            ("completion_digest", "0" * 64),
        ]:
            request = self.request(
                "tool-end",
                "child",
                dispatch_id="d1",
                effect_token=record["token"],
                identity_digest=record["identity_digest"],
            )
            with self.assertRaises(Exception):
                self.execute(dict(request, **{field: value}))
        self.assertEqual(before, self.store.path("r1").read_bytes())

    def test_restart_lookup_and_unknown_effect_denied(self):
        record = self.begin(())
        found = self.execute(self.request("effect-status", call_id="d1"))
        self.assertEqual(found["token"], record["token"])
        with self.assertRaises(Exception):
            self.execute(self.request("effect-status", call_id="missing"))

    def test_reopen_invalidates_previous_attempt(self):
        self.begin(())
        proof = self.attest("d1")
        self.execute(self.complete("d1", "parent", proof, True))
        self.execute(
            self.request("fail", evidence="fixture deliverable requires revision")
        )
        state = self.store.read("r1")
        self.assertEqual(state["data"]["phases"]["1"]["attempt"], 2)
        self.assertFalse(state["data"]["effect_records"]["d1"]["current_attempt"])

    def test_operator_auth_and_model_creation_denied(self):
        from run_operator import Operator

        with self.assertRaises(Exception):
            Operator(self.root, b"x" * 32)
        with self.assertRaises(Exception):
            self.execute(self.request("init"))
        with self.assertRaises(Exception):
            self.execute(self.request("approve"))

    def test_network_old_attempt_receipt_denied(self):
        from network_policy import verify_specialist

        self.begin(())
        proof = self.attest("d1")
        self.execute(self.complete("d1", "parent", proof, True))
        network_config = dict(self.config, specialist_phase_receipts={"1": "worker"})
        verify_specialist(self.store.read("r1"), network_config, 1)
        self.execute(
            self.request("fail", evidence="fixture requires new delivery attempt")
        )
        with self.assertRaises(Exception):
            verify_specialist(self.store.read("r1"), network_config, 1)

    def test_valid_proof_substitutions_preserve_bytes(self):
        self.begin(())
        proof = self.attest("d1")
        request = self.complete("d1", "parent", proof, True)
        before = self.store.path("r1").read_bytes()
        for field, value in [
            ("run_id", "other"),
            ("session_id", "unknown"),
            ("kind", "tool"),
            ("phase_attempt", 2),
            ("effect_token", "bad"),
            ("deliverable_digest", "0" * 64),
            ("completion_digest", "0" * 64),
            ("identity_digest", "0" * 64),
            ("action_scope_digest", "0" * 64),
        ]:
            with self.subTest(field=field), self.assertRaises(Exception):
                self.execute(dict(request, **{field: value}))
            self.assertEqual(before, self.store.path("r1").read_bytes())

    def test_racing_reconciliation_only_one_version_increment(self):
        self.begin(())
        proof = self.attest("d1")
        request = self.complete("d1", "parent", proof, True)
        before = self.store.read("r1")["state_version"]
        queue = multiprocessing.Queue()
        workers = [
            multiprocessing.Process(
                target=reconcile_worker, args=(str(self.root), request, queue)
            )
            for _ in range(2)
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(5)
            self.assertFalse(worker.is_alive())
        self.assertIn("accepted", [queue.get(timeout=2) for _ in workers])
        self.execute(request)
        self.assertEqual(self.store.read("r1")["state_version"], before + 1)

    def test_crash_after_commit_then_exact_replay(self):
        from run_store import Store

        self.begin(())
        request = self.complete("d1", "parent", self.attest("d1"), True)
        original = Store._atomic

        def interrupted(store, path, value):
            original(store, path, value)
            raise OSError("fixture lost response after durable publication")

        with (
            mock.patch.object(Store, "_atomic", interrupted),
            self.assertRaises(OSError),
        ):
            self.execute(request)
        before = self.store.path("r1").read_bytes()
        self.execute(request)
        self.assertEqual(before, self.store.path("r1").read_bytes())

    def test_unauthenticated_or_unallowed_producer_denied(self):
        self.begin(())
        with self.assertRaises(Exception):
            self.op.attest(
                "r1",
                token(self.store.read("r1")),
                "d1",
                "intruder",
                b"evidence",
                self.digest,
            )
        proof = self.attest("d1")
        state = self.store.read("r1")
        proofs = state["data"]["completion_proofs"]
        proofs[proof]["signature"] = "0" * 64
        self.store.update("r1", token(state), {"completion_proofs": proofs})
        with self.assertRaises(Exception):
            self.execute(self.complete("d1", "parent", proof, True))

    def test_authorization_change_blocks_reconciliation(self):
        self.begin(())
        proof = self.attest("d1")
        state = self.store.read("r1")
        authorization = dict(state["data"]["authorization"], revoked=True)
        self.store.update("r1", token(state), {"authorization": authorization})
        with self.assertRaises(Exception):
            self.execute(self.complete("d1", "parent", proof, True))

    def test_operator_cli_enrollment_requires_inherited_capability(self):
        scripts = self.root / "scripts/enforcement"
        scripts.mkdir(parents=True)
        for name in [
            "operator_cli.py",
            "run_operator.py",
            "run_effects.py",
            "run_store.py",
            "run_cli.py",
            "run_policy.py",
        ]:
            shutil.copy2(SOURCE / name, scripts / name)
        request = dict(
            workspace=str(self.root),
            action="enroll",
            run_id="r1",
            expected=token(self.store.read("r1")),
            session_id="reviewer",
            profile=dict(
                self.profile,
                role="leaf",
                can_reconcile=False,
                task_available=False,
                agents=[],
            ),
        )
        command = [sys.executable, "-B", str(scripts / "operator_cli.py")]
        denied = subprocess.run(
            command,
            cwd=self.root,
            input=json.dumps(request),
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(denied.returncode, 0)
        read_fd, write_fd = os.pipe()
        os.write(write_fd, b"f" * 32)
        os.close(write_fd)
        try:
            result = subprocess.run(
                command,
                cwd=self.root,
                input=json.dumps(request),
                text=True,
                capture_output=True,
                pass_fds=(read_fd,),
                env=dict(os.environ, WORKFLOW_OPERATOR_FD=str(read_fd)),
            )
        finally:
            os.close(read_fd)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_bounded_recovery_and_human_approval_import(self):
        import run_effects
        import datetime

        approval = dict(
            kind="human-approval",
            run_id="r1",
            workspace=str(self.root),
            action="fixture-test",
            target="fixture.txt",
            scope="local fixture",
            human_identity="fixture-human",
            reason="fixture approval",
            subject_hash=self.digest,
            expires_at=(
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=1)
            ).isoformat(),
        )
        signed = run_effects.seal(b"f" * 32, approval)
        self.op.import_approval("r1", token(self.store.read("r1")), signed)
        self.op.recover(
            "r1",
            token(self.store.read("r1")),
            1,
            self.digest,
            "fixture same-phase bounded recovery",
        )
        self.assertEqual(self.store.read("r1")["data"]["phases"]["1"]["attempt"], 2)
        self.begin(())
        with self.assertRaises(Exception):
            self.op.recover(
                "r1",
                token(self.store.read("r1")),
                1,
                self.digest,
                "must not clear running effects",
            )

    def test_nested_flow_through_actual_json_shell(self):
        scripts = self.root / "scripts/enforcement"
        scripts.mkdir(parents=True)
        for name in [
            "run_store.py",
            "run_effects.py",
            "run_operator.py",
            "run_cli.py",
            "run_policy.py",
            "workflow-enforce.sh",
        ]:
            shutil.copy2(SOURCE / name, scripts / name)

        def via_shell(request):
            result = subprocess.run(
                ["bash", str(scripts / "workflow-enforce.sh")],
                cwd=self.root,
                input=json.dumps(request),
                text=True,
                capture_output=True,
                timeout=3,
            )
            response = json.loads(result.stdout)
            if result.returncode or response.get("ok") is not True:
                raise ValueError(response.get("error"))
            return response["result"]

        with mock.patch.object(self, "execute", via_shell):
            self.test_nested_stale_original_then_explicit_reconcile()

    def test_unknown_operator_profile_fields_denied(self):
        profile = dict(self.profile, bypass_gates=True)
        with self.assertRaises(Exception):
            self.op.enroll("r1", token(self.store.read("r1")), "unexpected", profile)

    def test_model_file_tools_cannot_touch_protected_or_unassigned_targets(self):
        for target in [
            ".opencode/workflow-operator.key",
            ".opencode/workflow-runs/store.lock",
            ".opencode/workflow-config.json",
            "scripts/enforcement/run_cli.py",
            "../outside",
            "other.txt",
        ]:
            with self.subTest(target=target), self.assertRaises(Exception):
                self.execute(
                    self.request(
                        "check",
                        tool="write",
                        arguments={
                            "filePath": str(self.root / target),
                            "content": "denied",
                        },
                    )
                )

    def test_patch_all_targets_and_symlinks_checked(self):
        (self.root / "fixture.txt").write_text("fixture")
        (self.root / "alias").symlink_to(self.root / "fixture.txt")
        for arguments in [
            {
                "patchText": "*** Begin Patch\n*** Update File: fixture.txt\n@@\n-x\n+y\n*** Add File: .opencode/evil\n+evil\n*** End Patch"
            },
            {
                "patchText": "*** Begin Patch\n*** Update File: fixture.txt\n*** Move to: other.txt\n@@\n-x\n+y\n*** End Patch"
            },
            {"filePath": str(self.root / "alias"), "content": "x"},
        ]:
            tool = "apply_patch" if "patchText" in arguments else "write"
            with self.subTest(arguments=arguments), self.assertRaises(Exception):
                self.execute(self.request("check", tool=tool, arguments=arguments))

    def test_protected_read_denied_and_approved_write_allowed(self):
        self.execute(
            self.request(
                "check",
                tool="write",
                arguments={
                    "filePath": str(self.root / "fixture.txt"),
                    "content": "allowed",
                },
            )
        )
        with self.assertRaises(Exception):
            self.execute(
                self.request(
                    "check",
                    tool="read",
                    arguments={
                        "filePath": str(self.root / ".opencode/workflow-operator.key")
                    },
                )
            )

    def test_exact_action_diagnostic_executes_without_shell(self):
        script = self.root / "diagnostic.py"
        script.write_text('print("fixture-diagnostic")\n')
        executable = str(Path(sys.executable).resolve())
        spec = dict(
            argv=[executable, "-I", "-B", str(script)],
            cwd=".",
            classification="diagnostic",
            scope="fixture",
            inputs={"diagnostic.py": hashlib.sha256(script.read_bytes()).hexdigest()},
            outputs=[],
            timeout_ms=1000,
            executable_sha256=hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
        )
        self.op.pin_action("r1", token(self.store.read("r1")), "diagnostic", spec)
        profile = dict(self.profile, actions=["diagnostic"], tools=["workflow_action"])
        profile["scope"] = dict(profile["scope"], read_targets=["diagnostic.py"])
        self.op.enroll("r1", token(self.store.read("r1")), "runner", profile)
        request = self.request(
            "run-action",
            "runner",
            tool="workflow_action",
            arguments={"action_id": "diagnostic"},
            dispatch_id="diag1",
            deliverable_digest=self.digest,
        )
        result = self.execute(request)
        self.assertEqual(result["output"].strip(), "fixture-diagnostic")
        self.assertEqual(result["status"], "completed")
        with self.assertRaises(Exception):
            self.execute(
                dict(
                    request,
                    arguments={"action_id": "diagnostic", "argv": ["sh", "-c", "bad"]},
                )
            )

    def mutation_fixture(
        self,
        body='from pathlib import Path\nPath("fixture.txt").write_text("authorized")\n',
    ):
        import run_effects
        import datetime

        script = self.root / "mutation.py"
        script.write_text(body)
        executable = str(Path(sys.executable).resolve())
        spec = dict(
            argv=[executable, "-I", "-B", str(script)],
            cwd=".",
            classification="mutation",
            scope="fixture",
            inputs={"mutation.py": hashlib.sha256(script.read_bytes()).hexdigest()},
            outputs=["fixture.txt"],
            timeout_ms=150,
            executable_sha256=hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
        )
        self.op.pin_action("r1", token(self.store.read("r1")), "mutation", spec)
        profile = dict(
            self.profile, actions=["mutation"], tools=["workflow_action"], phases=[1, 2]
        )
        profile["scope"] = dict(self.profile["scope"], read_targets=["mutation.py"])
        self.op.enroll("r1", token(self.store.read("r1")), "runner", profile)
        receipt = dict(
            kind="human-approval",
            run_id="r1",
            workspace=str(self.root),
            action="mutation",
            target=".",
            scope="fixture",
            human_identity="fixture-human",
            reason="fixture explicit mutation",
            subject_hash=run_effects.digest(spec),
            phase=1,
            phase_attempt=1,
            owner_epoch=1,
            expires_at=(
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=1)
            ).isoformat(),
        )
        return script, run_effects.seal(b"f" * 32, receipt)

    def mutation_request(self):
        return self.request(
            "run-action",
            "runner",
            tool="workflow_action",
            arguments={"action_id": "mutation"},
            dispatch_id="mutation1",
            deliverable_digest=self.digest,
        )

    def test_mutation_requires_exact_human_receipt_then_executes(self):
        _, receipt = self.mutation_fixture()
        with self.assertRaises(Exception):
            self.execute(self.mutation_request())
        self.op.import_approval("r1", token(self.store.read("r1")), receipt)
        result = self.execute(self.mutation_request())
        self.assertEqual(result["status"], "completed")
        self.assertEqual((self.root / "fixture.txt").read_text(), "authorized")

    def test_mutation_phase_revision_and_domain_denials(self):
        _, receipt = self.mutation_fixture()
        self.op.import_approval("r1", token(self.store.read("r1")), receipt)
        base = self.store.read("r1")["data"]
        for patch in [
            {"current_phase": 2},
            {"revision_mode": True, "escalated": True},
            {
                "policy_config": dict(
                    self.config, specialist_phase_receipts={"1": "worker"}
                )
            },
        ]:
            data = dict(base, **patch)
            (self.root / ".opencode/workflow-config.json").write_text(
                json.dumps(data["policy_config"])
            )
            self.store.update("r1", token(self.store.read("r1")), data)
            before = self.store.path("r1").read_bytes()
            with self.subTest(patch=patch), self.assertRaises(Exception):
                self.execute(self.mutation_request())
            self.assertEqual(before, self.store.path("r1").read_bytes())

    def test_mutation_input_drift_denies_before_effect(self):
        script, receipt = self.mutation_fixture()
        self.op.import_approval("r1", token(self.store.read("r1")), receipt)
        script.write_text('raise RuntimeError("changed")')
        with self.assertRaises(Exception):
            self.execute(self.mutation_request())
        self.assertEqual(self.store.read("r1")["effects"], [])

    def test_exact_action_timeout_retains_effect_for_failure_receipt(self):
        _, receipt = self.mutation_fixture("import time\ntime.sleep(2)\n")
        self.op.import_approval("r1", token(self.store.read("r1")), receipt)
        result = self.execute(self.mutation_request())
        self.assertEqual(result["status"], "failed")
        self.assertEqual(self.store.read("r1")["effects"], ["mutation1"])

    def test_positive_multi_file_rename_search_and_substitution(self):
        (self.root / "src").mkdir()
        (self.root / "src/file.txt").write_text("fixture")
        profile = dict(
            self.profile,
            tools=["apply_patch", "write"],
            scope={"targets": ["fixture.txt", "second.txt", "renamed.txt", "src/"]},
        )
        self.op.enroll("r1", token(self.store.read("r1")), "editor", profile)
        patch = "*** Begin Patch\n*** Update File: fixture.txt\n*** Move to: renamed.txt\n@@\n-a\n+b\n*** Add File: second.txt\n+second\n*** End Patch"
        self.execute(
            self.request(
                "check", "editor", tool="apply_patch", arguments={"patchText": patch}
            )
        )
        self.execute(
            self.request(
                "check",
                "editor",
                tool="glob",
                arguments={"path": "src", "pattern": "**/*.txt"},
            )
        )
        self.execute(
            self.request(
                "check",
                "editor",
                tool="grep",
                arguments={"path": "src", "pattern": "fixture"},
            )
        )
        with self.assertRaises(Exception):
            self.execute(
                self.request(
                    "check",
                    "editor",
                    tool="write",
                    arguments={
                        "filePath": "fixture.txt",
                        "path": ".opencode/workflow-operator.key",
                    },
                )
            )

    def test_filesystem_change_before_begin_is_rechecked(self):
        path = self.root / "fixture.txt"
        path.write_text("safe")
        args = {"filePath": str(path), "content": "fixture"}
        self.execute(self.request("check", tool="write", arguments=args))
        path.unlink()
        path.symlink_to(self.root / ".opencode/workflow-operator.key")
        with self.assertRaises(Exception):
            self.execute(
                self.request(
                    "tool-begin",
                    tool="write",
                    arguments=args,
                    dispatch_id="race1",
                    deliverable_digest=self.digest,
                )
            )
        self.assertEqual(self.store.read("r1")["effects"], [])

    def test_revision_action_needs_fresh_phase_bound_receipt(self):
        import run_effects

        _, receipt = self.mutation_fixture()
        data = self.store.read("r1")["data"]
        config = dict(self.config, revision_phases=[2])
        data.update(current_phase=2, revision_mode=True, policy_config=config)
        data["phases"]["1"].update(gate="passed", status="completed")
        data["phases"]["2"]["status"] = "in_progress"
        (self.root / ".opencode/workflow-config.json").write_text(json.dumps(config))
        self.store.update("r1", token(self.store.read("r1")), data)
        self.op.import_approval("r1", token(self.store.read("r1")), receipt)
        with self.assertRaises(Exception):
            self.execute(self.mutation_request())
        fresh = run_effects.seal(b"f" * 32, dict(receipt["payload"], phase=2))
        self.op.import_approval("r1", token(self.store.read("r1")), fresh)
        self.assertEqual(self.execute(self.mutation_request())["status"], "completed")

    def test_active_target_lease_blocks_competing_mutation(self):
        args = {"filePath": "fixture.txt", "content": "first"}
        self.execute(
            self.request(
                "tool-begin",
                tool="write",
                arguments=args,
                dispatch_id="first",
                deliverable_digest=self.digest,
            )
        )
        before = self.store.path("r1").read_bytes()
        with self.assertRaises(Exception):
            self.execute(
                self.request(
                    "tool-begin",
                    tool="write",
                    arguments=args,
                    dispatch_id="second",
                    deliverable_digest=self.digest,
                )
            )
        self.assertEqual(before, self.store.path("r1").read_bytes())

    def test_signed_revocation_disables_prior_approval(self):
        import run_effects

        _, receipt = self.mutation_fixture()
        self.op.import_approval("r1", token(self.store.read("r1")), receipt)
        revoked = run_effects.seal(b"f" * 32, dict(receipt["payload"], revoked=True))
        self.op.import_approval("r1", token(self.store.read("r1")), revoked)
        with self.assertRaises(Exception):
            self.execute(self.mutation_request())

    def test_approval_phase_type_and_scope_substitution_denied(self):
        import run_effects

        _, receipt = self.mutation_fixture()
        for fields in [{"phase": True}, {"scope": "different"}, {"owner_epoch": 2}]:
            invalid = run_effects.seal(b"f" * 32, dict(receipt["payload"], **fields))
            self.op.import_approval("r1", token(self.store.read("r1")), invalid)
            with self.subTest(fields=fields), self.assertRaises(Exception):
                self.execute(self.mutation_request())

    def test_q1_action_aliases_reserve_inputs_outputs_and_allow_disjoint(self):
        import run_effects

        script, receipt = self.mutation_fixture()
        spec = self.store.read("r1")["data"]["action_catalog"]["mutation"]["definition"]
        spec["inputs"] = {str(script): spec["inputs"]["mutation.py"]}
        spec["outputs"] = ["./fixture.txt"]
        self.op.pin_action("r1", token(self.store.read("r1")), "mutation", spec)
        signed = run_effects.seal(
            b"f" * 32, dict(receipt["payload"], subject_hash=run_effects.digest(spec))
        )
        self.op.import_approval("r1", token(self.store.read("r1")), signed)
        profile = dict(
            self.profile, scope={"targets": ["mutation.py", "fixture.txt", "free.txt"]}
        )
        self.op.enroll("r1", token(self.store.read("r1")), "writer", profile)
        self.execute(self.mutation_request())
        before = self.store.path("r1").read_bytes()
        for target in ["fixture.txt", "./fixture.txt", str(script), "mutation.py"]:
            with self.subTest(target=target), self.assertRaises(Exception):
                self.execute(
                    self.request(
                        "check",
                        "writer",
                        tool="write",
                        arguments={"filePath": target, "content": "denied"},
                    )
                )
            self.assertEqual(before, self.store.path("r1").read_bytes())
        self.execute(
            self.request(
                "check",
                "writer",
                tool="write",
                arguments={"filePath": "free.txt", "content": "allowed"},
            )
        )

    def test_q2_corrupt_effect_indexes_deny_reads_transfer_finish_and_gates(self):
        self.begin(())
        path = self.store.path("r1")
        original = json.loads(path.read_text())
        variants = []
        for index in [[], ["orphan"], ["d1", "orphan"]]:
            value = json.loads(json.dumps(original))
            value["effects"] = index
            variants.append(value)
        value = json.loads(json.dumps(original))
        del value["effects"]
        variants.append(value)
        value = json.loads(json.dumps(original))
        value["data"]["effect_records"]["renamed"] = value["data"][
            "effect_records"
        ].pop("d1")
        variants.append(value)
        value = json.loads(json.dumps(original))
        value["data"]["effect_records"] = {}
        variants.append(value)
        value = json.loads(json.dumps(original))
        value["data"]["effect_records"]["d1"]["status"] = "completed"
        variants.append(value)
        for value in variants:
            path.write_text(json.dumps(value))
            before = path.read_bytes()
            for action in [
                lambda: self.store.read("r1"),
                lambda: self.store.transfer(
                    "r1", token(original), "new-owner", "fixture quiescence"
                ),
                lambda: self.store.finish("r1", token(original), "fixture quiescence"),
                lambda: self.store.remove("r1", token(original)),
            ]:
                with (
                    self.subTest(index=value.get("effects")),
                    self.assertRaises(Exception),
                ):
                    action()
                self.assertEqual(before, path.read_bytes())

    def test_q3_network_gate_requires_resolvable_authenticated_proof(self):
        from network_policy import verify_specialist

        self.begin(())
        proof = self.attest("d1")
        self.execute(self.complete("d1", "parent", proof, True))
        state = self.store.read("r1")
        config = dict(self.config, specialist_phase_receipts={"1": "worker"})
        verify_specialist(state, config, 1)
        for mutation in ["missing", "signature", "orphan", "identity", "owner"]:
            value = json.loads(json.dumps(state))
            if mutation == "missing":
                value["data"]["completion_proofs"] = {}
            if mutation == "signature":
                value["data"]["completion_proofs"][proof]["signature"] = "0" * 64
            if mutation == "orphan":
                value["data"]["effect_records"] = {}
            if mutation == "identity":
                value["data"]["dispatches"]["d1"]["token"] = "wrong"
            if mutation == "owner":
                value["owner_epoch"] += 1
            with self.subTest(mutation=mutation), self.assertRaises(Exception):
                verify_specialist(value, config, 1)

    def test_q4_three_real_failures_deny_dispatch_pass_and_advance(self):
        for _ in range(3):
            self.execute(
                self.request("fail", evidence="fixture review rejected current attempt")
            )
        self.op.recover(
            "r1",
            token(self.store.read("r1")),
            1,
            self.digest,
            "fixture cleanup does not clear escalation",
        )
        before = self.store.path("r1").read_bytes()
        for request in [
            self.request(
                "dispatch-begin",
                dispatch_id="d1",
                agent="worker",
                child_sessions=[],
                deliverable_digest=self.digest,
            ),
            self.request(
                "pass",
                evidence="fixture must remain escalated",
                deliverable_digest=self.digest,
            ),
            self.request(
                "advance",
                evidence="fixture must remain escalated",
                deliverable_digest=self.digest,
            ),
        ]:
            with self.subTest(action=request["action"]), self.assertRaises(Exception):
                self.execute(request)
            self.assertEqual(before, self.store.path("r1").read_bytes())

    def test_q4_revocation_between_completion_and_gate_denies_progress(self):
        self.begin(())
        self.execute(self.complete("d1", "parent", self.attest("d1"), True))
        state = self.store.read("r1")
        self.store.update(
            "r1",
            token(state),
            {"authorization": dict(state["data"]["authorization"], revoked=True)},
        )
        before = self.store.path("r1").read_bytes()
        with self.assertRaises(Exception):
            self.execute(
                self.request(
                    "pass",
                    evidence="revoked authority cannot pass",
                    deliverable_digest=self.digest,
                )
            )
        self.assertEqual(before, self.store.path("r1").read_bytes())

    def test_q2_consistent_running_record_blocks_transfer_until_completion(self):
        self.begin(())
        with self.assertRaises(Exception):
            self.store.transfer(
                "r1", token(self.store.read("r1")), "next", "fixture quiescence claim"
            )
        self.execute(self.complete("d1", "parent", self.attest("d1"), True))
        state = self.store.transfer(
            "r1",
            token(self.store.read("r1")),
            "next",
            "fixture actual terminal evidence",
        )
        self.assertEqual(state["owner_epoch"], 2)

    def test_q4_only_audited_operator_clearance_restores_dispatch_budget(self):
        for _ in range(3):
            self.execute(
                self.request("fail", evidence="fixture review rejects current attempt")
            )
        with self.assertRaises(Exception):
            self.execute(
                self.request(
                    "clear-hold",
                    hold="escalated",
                    reason="model cannot clear operator hold",
                    additional_revisions=1,
                )
            )
        state = self.op.clear_hold(
            "r1",
            token(self.store.read("r1")),
            "escalated",
            "fixture owner grants one additional revision",
            1,
        )
        self.assertEqual(state["data"]["revision_count"], 3)
        self.assertEqual(state["data"]["revision_limit"], 4)
        self.assertTrue(state["data"]["operator_clearances"])
        self.begin(())

    def test_q1_directory_lease_uses_canonical_namespace(self):
        import run_effects

        self.root.joinpath("src").mkdir()
        _, receipt = self.mutation_fixture(
            'from pathlib import Path\nPath("src/x").write_text("fixture")\n'
        )
        spec = self.store.read("r1")["data"]["action_catalog"]["mutation"]["definition"]
        spec["outputs"] = [str(self.root / "src") + "/"]
        self.op.pin_action("r1", token(self.store.read("r1")), "mutation", spec)
        signed = run_effects.seal(
            b"f" * 32, dict(receipt["payload"], subject_hash=run_effects.digest(spec))
        )
        self.op.import_approval("r1", token(self.store.read("r1")), signed)
        profile = dict(
            self.profile,
            tools=["write", "workflow_action"],
            actions=["mutation"],
            scope={"targets": ["src/", "free.txt"], "read_targets": ["mutation.py"]},
        )
        self.op.enroll("r1", token(self.store.read("r1")), "directory-worker", profile)
        self.execute(
            self.request(
                "run-action",
                "directory-worker",
                tool="workflow_action",
                arguments={"action_id": "mutation"},
                dispatch_id="dir1",
                deliverable_digest=self.digest,
            )
        )
        self.assertEqual(
            self.store.read("r1")["data"]["effect_records"]["dir1"]["target_paths"],
            ["mutation.py", "src"],
        )
        before = self.store.path("r1").read_bytes()
        with self.assertRaises(Exception):
            self.execute(
                self.request(
                    "tool-begin",
                    "directory-worker",
                    tool="write",
                    arguments={"filePath": "./src/next", "content": "blocked"},
                    dispatch_id="collision",
                    deliverable_digest=self.digest,
                )
            )
        self.assertEqual(before, self.store.path("r1").read_bytes())
        self.execute(
            self.request(
                "check",
                "directory-worker",
                tool="write",
                arguments={"filePath": "free.txt", "content": "disjoint"},
            )
        )

    def test_q3_validly_signed_wrong_outcome_and_changed_authority_deny(self):
        from network_policy import verify_specialist
        import run_effects

        self.begin(())
        proof = self.attest("d1")
        self.execute(self.complete("d1", "parent", proof, True))
        original = self.store.read("r1")
        config = dict(self.config, specialist_phase_receipts={"1": "worker"})
        for variant in ["outcome", "producer", "authorization", "deliverable"]:
            state = json.loads(json.dumps(original))
            if variant in {"outcome", "producer"}:
                payload = dict(state["data"]["completion_proofs"][proof]["payload"])
                payload.update(
                    {"status": "failed"}
                    if variant == "outcome"
                    else {"producer": "unassigned"}
                )
                signed = run_effects.seal(b"f" * 32, payload)
                reference = run_effects.digest(signed)
                state["data"]["completion_proofs"][reference] = signed
                state["data"]["effect_records"]["d1"]["completion_digest"] = reference
                state["data"]["dispatches"]["d1"]["completion_digest"] = reference
            if variant == "authorization":
                state["data"]["authorization"]["changed"] = True
            if variant == "deliverable":
                state["data"]["phases"]["1"]["deliverable_digest"] = "0" * 64
            with self.subTest(variant=variant), self.assertRaises(Exception):
                verify_specialist(state, config, 1)


if __name__ == "__main__":
    unittest.main()
