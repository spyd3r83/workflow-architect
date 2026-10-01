import importlib.util
import fcntl
import json
import multiprocessing
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "enforcement/run_store.py"


def load():
    spec = importlib.util.spec_from_file_location("run_store", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def claim(workspace, queue):
    try:
        load().Store(workspace).create("race", "owner", (None, 0, 0))
        queue.put("won")
    except Exception:
        queue.put("denied")


def compete(workspace, operation, run_id, expected, queue):
    try:
        store = load().Store(workspace)
        if operation == "update":
            store.update(run_id, expected, {"winner": True})
        else:
            store.remove(run_id, expected)
        queue.put("won")
    except Exception:
        queue.put("denied")


class RunStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "opencode.json").write_text('{"default_agent":"fixture"}')
        self.api = load()
        self.store = self.api.Store(self.root)
        self.store.initialize(
            {"schema_version": 1, "capacity": 3, "filesystem": "local"}
        )

    def create(self, name="one"):
        return self.store.create(name, "owner", (None, 0, 0))

    def test_missing_store_never_initializes(self):
        other = self.root / "nested"
        other.mkdir()
        with self.assertRaises(Exception):
            self.api.Store(other).read("one")
        self.assertFalse((other / ".opencode").exists())

    def test_retirement_history_refuses_admission_at_lifetime_cap(self):
        previous = None
        for index in range(12):
            state = self.create("bounded-" + str(index))
            if previous:
                self.store.remove(previous["run_id"], self.api.token(previous))
            previous = self.store.finish(
                state["run_id"], self.api.token(state), "fixture quiescent terminal"
            )
        before = {p.name: p.read_bytes() for p in self.store.home.glob("*.json")}
        with self.assertRaises(self.api.Denied):
            self.create("beyond-lifetime-cap")
        self.assertEqual(
            before, {p.name: p.read_bytes() for p in self.store.home.glob("*.json")}
        )

    def test_lock_contention_denies_without_replacing_inode(self):
        lock = self.store.home / "store.lock"
        inode = lock.stat().st_ino
        with lock.open("r+") as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):
                self.create()
        self.create()
        self.assertEqual(inode, lock.stat().st_ino)

    def run_competitors(self, operation, state):
        queue = multiprocessing.Queue()
        args = (
            str(self.root),
            operation,
            state["run_id"],
            self.api.token(state),
            queue,
        )
        workers = [multiprocessing.Process(target=compete, args=args) for _ in range(2)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(5)
            self.assertFalse(worker.is_alive())
        self.assertEqual(
            sorted(queue.get(timeout=2) for _ in workers), ["denied", "won"]
        )

    def test_multiprocess_update_cas_one_winner(self):
        self.run_competitors("update", self.create())

    def test_multiprocess_retention_one_winner(self):
        one = self.create()
        done = self.store.finish("one", self.api.token(one), "fixture quiet")
        self.create("two")
        self.run_competitors("remove", done)

    def test_retired_id_cannot_be_reused(self):
        one = self.create()
        done = self.store.finish("one", self.api.token(one), "fixture quiet")
        self.create("two")
        self.store.remove("one", self.api.token(done))
        with self.assertRaises(self.api.Denied):
            self.create("one")

    def test_bad_config_denies_mutation_unchanged(self):
        state = self.create()
        before = self.store.path("one").read_bytes()
        (self.store.home / "config.json").write_text('{"schema_version":2}')
        with self.assertRaises(self.api.Denied):
            self.store.update("one", self.api.token(state), {"x": 1})
        self.assertEqual(before, self.store.path("one").read_bytes())

    def test_corrupt_pointer_cannot_be_overwritten_by_admission(self):
        self.create()
        pointer = self.store.home / "active.json"
        pointer.write_text("{")
        with self.assertRaises(Exception):
            self.create("two")
        self.assertEqual(pointer.read_text(), "{")
        self.assertFalse(self.store.path("two").exists())

    def test_two_updates_race_with_same_token(self):
        state = self.create()
        other = self.api.Store(self.root)
        self.store.update("one", self.api.token(state), {"first": True})
        with self.assertRaises(self.api.Denied):
            other.update("one", self.api.token(state), {"second": True})
        self.assertEqual(other.read("one")["data"], {"first": True})

    def test_binding_rejects_foreign_workspace_state(self):
        state = self.create()
        state["workspace"] = "/another/package"
        self.store.path("one").write_text(json.dumps(state))
        with self.assertRaises(self.api.Denied):
            self.store.read("one")

    def test_session_binding_survives_pointer_change_and_restart(self):
        state = self.create()
        self.store.bind("session-1", "one", self.api.token(state))
        self.create("two")
        restarted = self.api.Store(self.root)
        self.assertEqual(restarted.bound("session-1")["run_id"], "one")
        with self.assertRaises(self.api.Denied):
            restarted.bind("session-1", "two", self.api.token(restarted.read("two")))

    def test_missing_binding_never_uses_pointer(self):
        self.create()
        with self.assertRaises(FileNotFoundError):
            self.store.bound("unbound-session")

    def test_atomic_write_flush_order(self):
        state = self.create()
        calls = []
        original_sync, original_replace = self.api.os.fsync, self.api.os.replace

        def sync(fd):
            calls.append("sync")
            return original_sync(fd)

        def replace(source, target):
            calls.append("replace")
            return original_replace(source, target)

        with (
            mock.patch.object(self.api.os, "fsync", sync),
            mock.patch.object(self.api.os, "replace", replace),
        ):
            self.store.update("one", self.api.token(state), {})
        self.assertEqual(calls, ["sync", "replace", "sync"])

    def test_after_pointer_failure_remains_inert(self):
        original = self.store._atomic

        def fail_final(target, value):
            if value.get("published") is True:
                raise OSError("fixture final-state failure")
            return original(target, value)

        with mock.patch.object(self.store, "_atomic", fail_final):
            with self.assertRaises(OSError):
                self.create()
        with self.assertRaises(self.api.Denied):
            self.store.discover()
        with self.assertRaises(self.api.Denied):
            self.store.read("one")

    def test_pointer_cannot_retarget_binding(self):
        first = self.create()
        self.create("two")
        self.assertEqual(self.store.read(first["run_id"])["run_id"], "one")
        self.assertEqual(self.store.discover()["run_id"], "two")

    def test_stale_cas_unchanged(self):
        state = self.create()
        token = self.api.token(state)
        self.store.update("one", token, {"dispatch_failed": True})
        before = self.store.path("one").read_bytes()
        with self.assertRaises(Exception):
            self.store.update("one", token, {"dispatch_failed": False})
        self.assertEqual(before, self.store.path("one").read_bytes())

    def test_concurrent_claim_one_winner(self):
        queue = multiprocessing.Queue()
        workers = [
            multiprocessing.Process(target=claim, args=(str(self.root), queue))
            for _ in range(2)
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(5)
            self.assertFalse(worker.is_alive())
        self.assertEqual(
            sorted(queue.get(timeout=2) for _ in workers), ["denied", "won"]
        )

    def test_transfer_requires_quiescence_and_fences_owner(self):
        old = self.create()
        with self.assertRaises(self.api.Denied):
            self.store.effect("one", self.api.token(old), "untyped", True)
        with self.assertRaises(Exception):
            self.store.transfer("one", self.api.token(old), "next", "")
        new = self.store.transfer(
            "one", self.api.token(old), "next", "fixture retirement"
        )
        self.assertEqual(new["owner_epoch"], 2)
        with self.assertRaises(Exception):
            self.store.update("one", self.api.token(old), {})

    def test_ids_schema_and_symlinks_denied(self):
        for name in ["../escape", "/tmp/x", "", "a/b", ".."]:
            with self.assertRaises(Exception):
                self.create(name)
        state = self.create()
        state["schema_version"] = 999
        self.store.path("one").write_text(json.dumps(state))
        with self.assertRaises(Exception):
            self.store.read("one")
        self.store.path("link").symlink_to(self.store.path("one"))
        with self.assertRaises(Exception):
            self.store.read("link")

    def test_publication_fault_leaves_inert_run(self):
        self.store.fault = (
            lambda stage: (_ for _ in ()).throw(OSError("fixture"))
            if stage == "state_published"
            else None
        )
        with self.assertRaises(OSError):
            self.create()
        with self.assertRaises(Exception):
            self.store.read("one")
        with self.assertRaises(Exception):
            self.store.discover()

    def test_atomic_write_failure_preserves_previous_bytes(self):
        state = self.create()
        before = self.store.path("one").read_bytes()
        self.store.fault = (
            lambda stage: (_ for _ in ()).throw(OSError("fixture"))
            if stage == "before_replace"
            else None
        )
        with self.assertRaises(OSError):
            self.store.update("one", self.api.token(state), {"x": 1})
        self.assertEqual(before, self.store.path("one").read_bytes())

    def test_corrupt_and_dangling_pointer_deny_discovery(self):
        self.create()
        for value in ["{", '{"schema_version":1,"run_id":"absent"}']:
            (self.store.home / "active.json").write_text(value)
            with self.assertRaises(Exception):
                self.store.discover()

    def test_retention_protects_active_and_busy_runs(self):
        one = self.create()
        with self.assertRaises(Exception):
            self.store.remove("one", self.api.token(one))
        done = self.store.finish("one", self.api.token(one), "fixture quiescence")
        self.create("two")
        self.store.remove("one", self.api.token(done))
        self.assertFalse(self.store.path("one").exists())
        self.create("three")
        self.create("four")
        with self.assertRaises(Exception):
            self.create("five")

    def test_legacy_import_idempotent_and_source_preserved(self):
        legacy = self.root / ".opencode/workflow-state.json"
        original = '{"run_id":"legacy","phases":{"1":{"gate":"passed"}}}'
        legacy.write_text(original)
        with self.assertRaises(Exception):
            self.store.import_legacy("legacy", "owner", (None, 0, 0), "")
        first = self.store.import_legacy(
            "legacy", "owner", (None, 0, 0), "fixture-only writers stopped"
        )
        again = self.store.import_legacy(
            "legacy", "owner", self.api.token(first), "fixture-only writers stopped"
        )
        self.assertEqual(first, again)
        self.assertEqual(legacy.read_text(), original)
        fresh = self.create("fresh")
        self.assertEqual(fresh["data"], {})

    def test_interrupted_legacy_import_resumes_matching_only(self):
        (self.root / ".opencode/workflow-state.json").write_text('{"run_id":"legacy"}')
        self.store.fault = (
            lambda stage: (_ for _ in ()).throw(OSError("fixture"))
            if stage == "state_published"
            else None
        )
        with self.assertRaises(OSError):
            self.store.import_legacy(
                "legacy", "owner", (None, 0, 0), "fixture quiescence"
            )
        pending = json.loads(self.store.path("legacy").read_text())
        self.store.fault = lambda stage: None
        result = self.store.import_legacy(
            "legacy", "owner", self.api.token(pending), "fixture quiescence"
        )
        self.assertTrue(result["published"])


if __name__ == "__main__":
    unittest.main()
