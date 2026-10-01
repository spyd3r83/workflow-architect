import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile


class Denied(ValueError):
    pass


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


EFFECT_ID_FIELDS = {
    "workspace",
    "run_id",
    "owner",
    "owner_epoch",
    "origin_session",
    "call_id",
    "dispatch_id",
    "kind",
    "tool",
    "phase",
    "phase_attempt",
    "token",
    "start_version",
    "start_token",
    "action_scope_digest",
    "authorization_digest",
    "deliverable_digest",
}


def validate_effect_identity(record: dict):
    require(type(record) is dict, "invalid effect object")
    version = record.get("schema_version")
    require(type(version) is int and version == 1, "effect schema unsupported")
    fixed = record.get("identity")
    require(
        type(fixed) is dict and EFFECT_ID_FIELDS <= fixed.keys(),
        "incomplete effect identity",
    )
    require(
        digest(fixed) == record.get("identity_digest"),
        "effect identity digest mismatch",
    )
    require(
        all(record.get(k) == v for k, v in fixed.items()),
        "effect identity fields changed",
    )


def validate_effect_record(state, key, record):
    validate_effect_identity(record)
    require(
        record.get("dispatch_id") == key and record.get("call_id") == key,
        "effect index key mismatch",
    )
    require(
        record.get("workspace") == state["workspace"]
        and record.get("run_id") == state["run_id"],
        "effect run mismatch",
    )
    require(record.get("kind") in {"tool", "dispatch"}, "invalid effect kind")
    require(
        record.get("status") in {"running", "completed", "failed", "cancelled"},
        "invalid effect status",
    )
    if record["status"] == "running":
        require(
            record["owner"] == state["owner"]
            and record["owner_epoch"] == state["owner_epoch"],
            "running effect owner mismatch",
        )


def validate_effect_index(state):
    records = state["data"].get("effect_records", {})
    require(type(records) is dict, "invalid effect registry")
    for key, record in records.items():
        identifier(key)
        validate_effect_record(state, key, record)
    running = {key for key, record in records.items() if record["status"] == "running"}
    require(
        set(state["effects"]) == running,
        "active effect index disagrees with typed registry",
    )
    require(
        not running or state["lifecycle"] == "active",
        "terminal run has running effects",
    )


def require(condition, reason):
    if not condition:
        raise Denied(reason)


def identifier(value):
    require(
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", value),
        "invalid identifier",
    )
    return value


def token(state):
    return state["owner"], state["owner_epoch"], state["state_version"]


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read_json(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd) as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "not regular file")
        value = json.load(stream)
    require(type(value) is dict, "expected object")
    return value


def validate_config(config):
    require(
        type(config.get("schema_version")) is int and config["schema_version"] == 1,
        "unsupported config schema",
    )
    require(
        type(config.get("capacity")) is int and config["capacity"] > 0,
        "invalid capacity",
    )
    require(
        config.get("filesystem") == "local",
        "only local single-host filesystem supported",
    )


class Store:
    def __init__(self, workspace):
        root = Path(workspace)
        require(
            root.is_absolute() and root == root.resolve(strict=True),
            "exact canonical workspace required",
        )
        require(
            read_json(root / "opencode.json").get("default_agent"),
            "package marker required",
        )
        self.root = root
        self.home = root / ".opencode" / "workflow-runs"
        self.fault = lambda stage: None

    def _directories(self):
        for path in [self.root / ".opencode", self.home]:
            require(
                not path.is_symlink() and path.is_dir(), "missing or redirected store"
            )

    @contextlib.contextmanager
    def _lock(self):
        self._directories()
        fd = os.open(
            self.home / "store.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600
        )
        try:
            require(stat.S_ISREG(os.fstat(fd).st_mode), "invalid lock")
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            require(
                os.fstat(fd).st_ino == (self.home / "store.lock").stat().st_ino,
                "lock replaced",
            )
            yield
        finally:
            os.close(fd)

    def initialize(self, config):
        validate_config(config)
        parent = self.root / ".opencode"
        require(
            not parent.is_symlink() and not self.home.is_symlink(), "redirected store"
        )
        parent.mkdir(exist_ok=True)
        self.home.mkdir(exist_ok=True, mode=0o700)
        sync_directory(self.root)
        sync_directory(parent)
        with self._lock():
            target = self.home / "config.json"
            if target.exists():
                require(read_json(target) == config, "config cannot be replaced")
            else:
                self._atomic(target, config)

    def _atomic(self, target, value):
        require(
            target.parent == self.home and not target.is_symlink(),
            "invalid destination",
        )
        fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=self.home)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(value, stream, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            self.fault("before_replace")
            os.replace(temporary, target)
            sync_directory(self.home)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def path(self, run_id):
        return self.home / (identifier(run_id) + ".run.json")

    def _config(self):
        config = read_json(self.home / "config.json")
        validate_config(config)
        return config

    def _read(self, run_id, unpublished=False):
        self._config()
        state = read_json(self.path(run_id))
        require(
            type(state.get("schema_version")) is int and state["schema_version"] == 1,
            "invalid state schema",
        )
        require(
            state.get("workspace") == str(self.root) and state.get("run_id") == run_id,
            "invalid state binding",
        )
        self._validate_state(state, unpublished)
        return state

    def _validate_state(self, state, unpublished):
        identifier(state.get("owner"))
        for key in ["owner_epoch", "state_version"]:
            require(type(state.get(key)) is int and state[key] > 0, "invalid version")
        require(
            type(state.get("published")) is bool
            and (state["published"] or unpublished),
            "unpublished run",
        )
        require(state.get("lifecycle") in ["active", "terminal"], "invalid lifecycle")
        require(
            type(state.get("effects")) is list
            and len(set(state["effects"])) == len(state["effects"]),
            "invalid effects",
        )
        for effect in state["effects"]:
            identifier(effect)
        require(type(state.get("data")) is dict, "invalid domain state")
        validate_effect_index(state)

    def read(self, run_id):
        with self._lock():
            return self._read(run_id)

    def _expected(self, state, expected):
        require(type(expected) is tuple and len(expected) == 3, "explicit CAS required")
        require(all(type(x) is int for x in expected[1:]), "invalid CAS versions")
        require(token(state) == expected, "stale owner/epoch/version")

    def _admit(self, run_id, expected):
        require(
            type(expected) is tuple and expected == (None, 0, 0),
            "creation requires absent-state CAS",
        )
        require(all(type(x) is int for x in expected[1:]), "invalid CAS versions")
        require(not self.path(run_id).exists(), "run already exists")
        require(not (self.home / (run_id + ".retired.json")).exists(), "retired run ID")
        if (self.home / "active.json").exists():
            self._read(self._pointer())
        capacity = self._config()["capacity"]
        runs = list(self.home.glob("*.run.json"))
        history = len(runs) + sum(1 for _ in self.home.glob("*.retired.json"))
        require(history < capacity * 4, "lifetime admission cap exhausted")
        require(len(runs) < capacity, "protected capacity exhausted")

    def _new(self, run_id, owner, expected, data=None, legacy=None):
        self._admit(run_id, expected)
        return {
            "schema_version": 1,
            "workspace": str(self.root),
            "run_id": run_id,
            "owner": identifier(owner),
            "owner_epoch": 1,
            "state_version": 1,
            "published": False,
            "lifecycle": "active",
            "effects": [],
            "data": data or {},
            "legacy_digest": legacy,
        }

    def _publish(self, state):
        self._validate_state(state, unpublished=True)
        self._atomic(self.path(state["run_id"]), state)
        self.fault("state_published")
        self._atomic(
            self.home / "active.json",
            {
                "schema_version": 1,
                "workspace": str(self.root),
                "run_id": state["run_id"],
            },
        )
        state["published"] = True
        state["state_version"] += 1
        self._atomic(self.path(state["run_id"]), state)
        return state

    def create(self, run_id, owner, expected, initial_data=None):
        with self._lock():
            return self._publish(self._new(run_id, owner, expected, initial_data))

    def _pointer(self):
        pointer = read_json(self.home / "active.json")
        require(
            type(pointer.get("schema_version")) is int
            and pointer["schema_version"] == 1,
            "invalid pointer schema",
        )
        require(pointer.get("workspace") == str(self.root), "invalid pointer workspace")
        identifier(pointer.get("run_id"))
        return pointer["run_id"]

    def discover(self):
        with self._lock():
            return self._read(self._pointer())

    def _binding_path(self, session_id):
        return self.home / (identifier(session_id) + ".binding.json")

    def _binding(self, session_id, state):
        return {
            "schema_version": 1,
            "workspace": str(self.root),
            "session_id": identifier(session_id),
            "run_id": state["run_id"],
            "owner": state["owner"],
            "owner_epoch": state["owner_epoch"],
        }

    def bind(self, session_id, run_id, expected):
        with self._lock():
            self._read(self._pointer())
            state = self._read(run_id)
            self._expected(state, expected)
            require(state["lifecycle"] == "active", "cannot bind terminal run")
            target = self._binding_path(session_id)
            binding = self._binding(session_id, state)
            if target.exists():
                require(read_json(target) == binding, "session already bound")
                return binding
            state["state_version"] += 1
            self._atomic(self.path(run_id), state)
            self._atomic(target, binding)
            return binding

    def bound(self, session_id):
        with self._lock():
            binding = read_json(self._binding_path(session_id))
            state = self._read(binding.get("run_id"))
            require(
                binding == self._binding(session_id, state),
                "stale or invalid session binding",
            )
            return state

    def _change(self, run_id, expected, action, replay=None):
        with self._lock():
            self._read(self._pointer())
            state = self._read(run_id)
            if replay is not None and replay(state):
                return state
            self._expected(state, expected)
            require(state["lifecycle"] == "active", "terminal run is immutable")
            if action(state) is False:
                self._validate_state(state, unpublished=False)
                return state
            state["state_version"] += 1
            self._validate_state(state, unpublished=False)
            self._atomic(self.path(run_id), state)
            return state

    def update(self, run_id, expected, data):
        require(type(data) is dict, "domain state must be object")
        return self._change(run_id, expected, lambda state: state["data"].update(data))

    def effect(self, run_id, expected, dispatch_id, begin):
        raise Denied("bare effect API disabled; typed origin-bound lifecycle required")

    def _quiet(self, state, evidence):
        require(
            isinstance(evidence, str) and evidence.strip(),
            "explicit quiescence evidence required",
        )
        require(not state["effects"], "effects still in flight")

    def transfer(self, run_id, expected, owner, evidence):
        identifier(owner)

        def change(state):
            self._quiet(state, evidence)
            require(owner != state["owner"], "owner unchanged")
            state.update(
                owner=owner,
                owner_epoch=state["owner_epoch"] + 1,
                retirement_evidence=evidence,
            )

        return self._change(run_id, expected, change)

    def finish(self, run_id, expected, evidence):
        def change(state):
            self._quiet(state, evidence)
            state.update(lifecycle="terminal", quiescence_evidence=evidence)

        return self._change(run_id, expected, change)

    def remove(self, run_id, expected):
        with self._lock():
            state = self._read(run_id)
            self._expected(state, expected)
            self._quiet(state, state.get("quiescence_evidence"))
            self._read(self._pointer())
            require(
                state["lifecycle"] == "terminal" and self._pointer() != run_id,
                "protected run",
            )
            self._atomic(
                self.home / (run_id + ".retired.json"),
                {
                    "schema_version": 1,
                    "retired_token": token(state),
                },
            )
            self.path(run_id).unlink()
            sync_directory(self.home)

    def _legacy(self, run_id, quiescence):
        self._quiet({"effects": []}, quiescence)
        legacy = read_json(self.root / ".opencode" / "workflow-state.json")
        require(
            legacy.get("run_id") == identifier(run_id),
            "explicit matching legacy run required",
        )
        digest = hashlib.sha256(json.dumps(legacy, sort_keys=True).encode()).hexdigest()
        return legacy, digest

    def import_legacy(self, run_id, owner, expected, quiescence):
        with self._lock():
            legacy, digest = self._legacy(run_id, quiescence)
            if self.path(run_id).exists():
                state = self._read(run_id, unpublished=True)
                self._expected(state, expected)
                require(
                    state.get("legacy_digest") == digest and state["owner"] == owner,
                    "import conflict",
                )
                return state if state["published"] else self._publish(state)
            state = self._new(run_id, owner, expected, legacy, digest)
            state["legacy_quiescence_evidence"] = quiescence
            return self._publish(state)
