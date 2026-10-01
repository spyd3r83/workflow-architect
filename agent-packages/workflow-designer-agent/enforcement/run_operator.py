import datetime
import hashlib
import hmac
import os
from pathlib import Path
from run_store import Store, require, identifier, token, sync_directory, read_json
import run_effects as effects


PROFILE_FIELDS = {
    "role",
    "task_available",
    "tools",
    "phases",
    "agents",
    "scope",
    "completion_producers",
    "can_reconcile",
    "parent_effect",
    "actions",
    "child_profiles",
    "host_reconcile",
}


def validate_profile(profile: dict, config):
    require(
        type(profile) is dict and set(profile) <= PROFILE_FIELDS,
        "unknown profile field",
    )
    validate_role(profile)
    validate_lists(profile, config)
    scope = profile.get("scope")
    require(type(scope) is dict and scope.get("targets"), "action scope required")
    for key in ["targets", "read_targets"]:
        values = scope.get(key, [])
        require(type(values) is list and len(values) <= 128, "invalid scope list")
        require(all(isinstance(p, str) and p for p in values), "invalid scope target")
    for agent, child in profile.get("child_profiles", {}).items():
        require(
            agent in profile["agents"] and child["role"] == "leaf",
            "invalid child grant",
        )
        validate_profile(child, config)


def validate_role(profile):
    require(profile.get("role") in {"coordinator", "leaf"}, "invalid actor role")
    require(type(profile.get("task_available")) is bool, "explicit capability required")
    for field in ["can_reconcile", "host_reconcile"]:
        require(
            type(profile.get(field, False)) is bool, "invalid reconciler capability"
        )
    if profile["role"] == "leaf":
        require(not profile["task_available"], "leaf delegation expansion")
        require(not profile.get("can_reconcile"), "leaf reconciliation expansion")
    if profile.get("host_reconcile"):
        require(
            profile.get("can_reconcile"), "host reconciliation needs explicit grant"
        )


def validate_lists(profile, config):
    for field in ["tools", "phases", "agents", "completion_producers"]:
        require(type(profile.get(field)) is list, "profile list required: " + field)
    for field in ["tools", "agents", "completion_producers", "actions"]:
        require(type(profile.get(field, [])) is list, "invalid capability list")
        for name in profile.get(field, []):
            identifier(name)
    for phase in profile["phases"]:
        require(
            type(phase) is int and 1 <= phase <= config["total_phases"], "invalid phase"
        )


def completion_proof(key, record, producer, evidence_bytes, status):
    payload = {k: record[k] for k in ["identity_digest", "token", "deliverable_digest"]}
    payload.update(kind="completion", producer=producer, status=status)
    payload["evidence_digest"] = hashlib.sha256(evidence_bytes).hexdigest()
    payload["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return effects.seal(key, payload)


def replay_observation(state, record, status, evidence):
    signed = state["data"]["completion_proofs"][record["completion_digest"]]
    proof = effects.verify(state["workspace"], signed)
    require(record["status"] == status, "conflicting host outcome")
    require(
        proof["evidence_digest"] == hashlib.sha256(evidence.encode()).hexdigest(),
        "conflicting host evidence",
    )
    return dict(
        completion_digest=record["completion_digest"],
        expected=record["completion_audit"]["expected"],
        replay_audit=record["completion_audit"],
    )


class Operator:
    def __init__(self, root, capability):
        self.store = Store(root)
        self.key = effects.operator_key(root)
        require(
            isinstance(capability, bytes) and hmac.compare_digest(self.key, capability),
            "operator authentication denied",
        )

    @classmethod
    def bootstrap(cls, root, capability, capacity=8):
        require(
            isinstance(capability, bytes) and len(capability) == 32,
            "32-byte inherited operator capability required",
        )
        store = Store(root)
        store.initialize(
            {"schema_version": 1, "capacity": capacity, "filesystem": "local"}
        )
        with store._lock():
            path = Path(root) / ".opencode/workflow-operator.key"
            if not path.exists():
                fd = os.open(
                    path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
                )
                with os.fdopen(fd, "wb") as stream:
                    stream.write(capability)
                    stream.flush()
                    os.fsync(stream.fileno())
                sync_directory(path.parent)
        return cls(root, capability)

    def create(self, run, owner, session, profile, config, expected):
        from run_cli import config_for

        require(config == config_for(self.store.root), "policy pin mismatch")
        validate_profile(profile, config)
        require(profile["role"] == "coordinator", "initial coordinator required")
        identifier(session)
        phases = {
            str(p): dict(
                status="in_progress" if p == 1 else "pending",
                gate="pending",
                attempt=1,
                deliverable_digest=None,
            )
            for p in range(1, config["total_phases"] + 1)
        }
        data = dict(
            policy_config=config,
            current_phase=1,
            phases=phases,
            actors={session: profile},
            revision_count=0,
            authorization={"run_id": run, "revoked": False, "approval_digests": []},
        )
        state = self.store.create(run, owner, expected, data)
        self.store.bind(session, run, token(state))
        return self.store.bound(session)

    def enroll(self, run, expected, session, profile):
        identifier(session)

        def change(state):
            validate_profile(profile, state["data"]["policy_config"])
            if session in state["data"]["actors"]:
                require(
                    state["data"]["actors"][session] == profile,
                    "conflicting actor enrollment",
                )
                return False
            parent = profile.get("parent_effect")
            if parent:
                record = state["data"]["effect_records"][parent]
                require(
                    session in record["child_sessions"]
                    and record["status"] == "running",
                    "child not registered",
                )
            state["data"]["actors"][session] = profile

        state = self.store._change(run, expected, change)
        self.store.bind(session, run, token(state))
        return self.store.bound(session)

    def close_child(self, run, expected, session, reason):
        require(
            isinstance(reason, str) and len(reason) >= 10,
            "child exit evidence required",
        )

        def change(state):
            actor = state["data"]["actors"][session]
            require(actor["role"] == "leaf", "not a child actor")
            pending = [
                r
                for r in state["data"].get("effect_records", {}).values()
                if r["origin_session"] == session
                and r["status"] not in effects.TERMINAL
            ]
            require(not pending, "child has unresolved effects")
            actor.update(terminal=True, exit_evidence=reason)

        return self.store._change(run, expected, change)

    def attest(
        self,
        run,
        expected,
        effect,
        producer,
        evidence_bytes,
        deliverable,
        status="completed",
        return_envelope=False,
    ):
        require(
            isinstance(evidence_bytes, bytes) and evidence_bytes,
            "trusted completion evidence required",
        )
        result = {}
        require(status in effects.TERMINAL, "invalid terminal status")

        def change(state):
            record = state["data"]["effect_records"][effect]
            effects.current(state, record)
            effects.children_terminal(state, record, success=status == "completed")
            require(
                producer in record["completion_producers"], "producer not authorized"
            )
            require(
                effects.sha(deliverable) == record["deliverable_digest"],
                "deliverable substitution",
            )
            proof = completion_proof(self.key, record, producer, evidence_bytes, status)
            result["digest"] = effects.digest(proof)
            state["data"].setdefault("completion_proofs", {})[result["digest"]] = proof

        committed = self.store._change(run, expected, change)
        result.update(completion_digest=result.pop("digest"), expected=token(committed))
        return result if return_envelope else result["completion_digest"]

    def observe(
        self,
        run,
        expected,
        session,
        call,
        tool,
        arguments,
        status,
        evidence,
        producer="opencode-host",
    ):
        state = self.store.read(run)
        self.store._expected(state, expected)
        record = effects.lookup(state, session, call)
        require(record["tool"] == tool, "host tool mismatch")
        require(
            record["invocation_digest"] == effects.digest(arguments),
            "host args mismatch",
        )
        if record["status"] in effects.TERMINAL:
            return replay_observation(state, record, status, evidence)
        return self.attest(
            run,
            expected,
            call,
            producer,
            evidence.encode(),
            record["deliverable_digest"],
            status,
            return_envelope=True,
        )

    def pin_action(self, run, expected, name, definition):
        from run_policy import validate_action_definition, validate_action_files

        identifier(name)
        validate_action_definition(definition)

        def change(state):
            validate_action_files(state, definition)
            require(not state["effects"], "cannot repin action with active effects")
            entry = dict(definition=definition, subject_hash=effects.digest(definition))
            state["data"].setdefault("action_catalog", {})[name] = entry

        return self.store._change(run, expected, change)

    def import_approval(self, run, expected, signed):
        approval = effects.verify(self.store.root, signed)
        require(type(approval.get("revoked", False)) is bool, "bad revocation flag")
        require(
            approval.get("kind") == "human-approval" and approval.get("run_id") == run,
            "wrong approval type/run",
        )
        require(
            approval.get("workspace") == str(self.store.root),
            "wrong approval workspace",
        )
        require(
            all(
                approval.get(k)
                for k in ["action", "target", "scope", "human_identity", "reason"]
            ),
            "approval fields missing",
        )
        effects.sha(approval.get("subject_hash"))
        expiry = datetime.datetime.fromisoformat(approval["expires_at"])
        require(
            expiry > datetime.datetime.now(datetime.timezone.utc), "expired approval"
        )

        def change(state):
            key = effects.digest(signed)
            if key in state["data"].get("human_approvals", {}):
                require(
                    state["data"]["human_approvals"][key] == signed,
                    "conflicting approval replay",
                )
                return False
            state["data"].setdefault("human_approvals", {})[key] = signed
            state["data"]["authorization"]["approval_digests"].append(key)
            if approval.get("revoked"):
                revoked = state["data"]["authorization"].setdefault(
                    "revoked_approvals", []
                )
                revoked.append(approval["subject_hash"])

        return self.store._change(run, expected, change)

    def recover(self, run, expected, phase, deliverable, reason):
        require(
            isinstance(reason, str) and len(reason) >= 20,
            "recovery provenance required",
        )

        def change(state):
            require(
                not state["effects"] and state["data"]["current_phase"] == phase,
                "recovery cannot clear effects or skip phases",
            )
            effects.invalidate_attempt(state, phase)
            state["data"]["phases"][str(phase)].update(
                status="in_progress",
                gate="pending",
                deliverable_digest=effects.sha(deliverable),
            )
            state["data"].update(
                revision_mode=True, dispatch_failed=False, recovery_reason=reason
            )

        return self.store._change(run, expected, change)

    def clear_hold(self, run, expected, hold, reason, additional_revisions=0):
        require(hold in {"escalated", "revoked"}, "unsupported operator clearance")
        require(
            isinstance(reason, str) and len(reason.strip()) >= 20,
            "clearance provenance required",
        )

        def change(state):
            self.store._quiet(state, reason)
            data = state["data"]
            if hold == "escalated":
                require(data.get("escalated"), "escalation hold absent")
                require(
                    type(additional_revisions) is int
                    and 0
                    < additional_revisions
                    <= data["policy_config"]["max_revisions"],
                    "invalid revision extension",
                )
                data.update(
                    escalated=False,
                    revision_limit=data["revision_count"] + additional_revisions,
                )
            else:
                require(
                    data["authorization"].get("revoked") is True,
                    "revocation hold absent",
                )
                require(
                    additional_revisions == 0,
                    "revocation clearance cannot extend revisions",
                )
                data["authorization"].update(
                    revoked=False, clearance_version=state["state_version"] + 1
                )
            audit = dict(
                hold=hold,
                reason=reason,
                expected=list(expected),
                run_id=run,
                workspace=state["workspace"],
            )
            data.setdefault("operator_clearances", []).append(
                effects.seal(self.key, audit)
            )
            effects.invalidate_attempt(state, data["current_phase"])
            data["phases"][str(data["current_phase"])].update(
                gate="pending", status="in_progress"
            )

        return self.store._change(run, expected, change)
