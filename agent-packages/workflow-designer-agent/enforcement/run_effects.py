import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
from run_store import require, identifier, digest
from run_store import validate_effect_identity as integrity

TERMINAL = {"completed", "failed", "cancelled"}
SUBSTITUTION_FIELDS = (
    "kind",
    "tool",
    "phase",
    "phase_attempt",
    "agent",
    "parent_effect",
    "action_scope_digest",
    "deliverable_digest",
)
AUDIT_FIELDS = ("action", "expected", "session_id", "reason", "reason_provenance")


def sha(value):
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value),
        "invalid digest",
    )
    return value


def operator_key(root):
    fd = os.open(
        Path(root) / ".opencode/workflow-operator.key", os.O_RDONLY | os.O_NOFOLLOW
    )
    with os.fdopen(fd, "rb") as stream:
        key = stream.read(33)
    require(len(key) == 32, "invalid operator capability")
    return key


def seal(key, payload):
    return {
        "payload": payload,
        "signature": hmac.new(
            key, digest(payload).encode(), hashlib.sha256
        ).hexdigest(),
    }


def verify(root, proof: dict) -> dict:
    require(
        type(proof) is dict and type(proof.get("payload")) is dict,
        "invalid signed evidence",
    )
    expected = seal(operator_key(root), proof["payload"])["signature"]
    require(
        hmac.compare_digest(expected, str(proof.get("signature", ""))),
        "unauthenticated evidence",
    )
    return proof["payload"]


def authorization(state):
    value = state["data"].get("authorization")
    require(
        type(value) is dict and value.get("revoked") is False,
        "authorization absent or revoked",
    )
    return digest(value)


def actor_scope(actor):
    return digest(
        {
            key: actor.get(key)
            for key in [
                "role",
                "tools",
                "phases",
                "agents",
                "scope",
                "completion_producers",
                "parent_effect",
                "actions",
                "child_profiles",
            ]
        }
    )


def current(state, record, completed=False):
    integrity(record)
    owner = (record["owner"], record["owner_epoch"])
    require(owner == (state["owner"], state["owner_epoch"]), "owner fence changed")
    phase = state["data"]["current_phase"]
    item = state["data"]["phases"][str(phase)]
    attempt = (record["phase"], record["phase_attempt"])
    require(attempt == (phase, item.get("attempt")), "phase attempt changed")
    auth = authorization(state)
    require(record["authorization_digest"] == auth, "authorization changed")
    actor = state["data"]["actors"][record["origin_session"]]
    scope = actor_scope(actor)
    require(record["action_scope_digest"] == scope, "action scope changed")
    require(record["current_attempt"] and not record.get("revoked"), "retired effect")
    statuses = TERMINAL if completed else {"running"}
    require(record["status"] in statuses, "effect not completable")


def children_terminal(state, record, success=True):
    for session in record["child_sessions"]:
        child = state["data"]["actors"].get(session)
        require(
            child
            and child.get("terminal") is True
            and child.get("parent_effect") == record["dispatch_id"],
            "registered child not terminal or rebound",
        )
    for child in state["data"]["effect_records"].values():
        if child["parent_effect"] == record["dispatch_id"]:
            require(
                child["status"] in ({"completed"} if success else TERMINAL),
                "child effect unfinished or conflicted",
            )


def begin(state, request, kind):
    actor = state["data"]["actors"][request["session_id"]]
    require(not actor.get("terminal"), "terminal actor cannot start effects")
    call = identifier(request.get("dispatch_id"))
    records = state["data"].setdefault("effect_records", {})
    require(call not in records, "effect ID reused")
    phase = state["data"]["current_phase"]
    item = state["data"]["phases"][str(phase)]
    deliverable = sha(request.get("deliverable_digest"))
    require(
        item.get("deliverable_digest") in {None, deliverable}, "deliverable conflict"
    )
    item["deliverable_digest"] = deliverable
    record = make_record(state, request, actor, kind, item)
    register_parent(state, record)
    publish_effect(state, record)


def publish_effect(state, record):
    record["identity"] = {
        k: v for k, v in record.items() if k not in {"status", "current_attempt"}
    }
    record["identity_digest"] = digest(record["identity"])
    call = record["dispatch_id"]
    state["data"]["effect_records"][call] = record
    state["effects"].append(call)
    if record["kind"] == "dispatch":
        state["data"].setdefault("dispatches", {})[call] = record


def registered_children(request):
    children = request.get("child_sessions", [])
    require(
        type(children) is list and len(set(children)) == len(children),
        "invalid child registrations",
    )
    for session in children:
        identifier(session)
    return children


def call_identity(state, request, kind):
    record = {k: state[k] for k in ["workspace", "run_id", "owner", "owner_epoch"]}
    record.update(
        schema_version=1,
        start_version=state["state_version"] + 1,
        start_token=[state["owner"], state["owner_epoch"], state["state_version"] + 1],
        invocation_digest=digest(request.get("arguments", {})),
        target_paths=request.get("target_paths", []),
        origin_session=request["session_id"],
        call_id=request["dispatch_id"],
        dispatch_id=request["dispatch_id"],
        kind=kind,
        tool="task" if kind == "dispatch" else request["tool"],
        agent=request.get("agent"),
        token=secrets.token_hex(32),
        dispatch="task()" if kind == "dispatch" else "tool",
        receipt_id=request["dispatch_id"],
    )
    return record


def make_record(state, request, actor, kind, item):
    children = registered_children(request)
    record = call_identity(state, request, kind)
    record.update(
        phase=state["data"]["current_phase"],
        phase_attempt=item["attempt"],
        child_session=children[0] if children else None,
        child_sessions=children,
        parent_effect=actor.get("parent_effect"),
        action_scope_digest=actor_scope(actor),
        authorization_digest=authorization(state),
        completion_producers=actor["completion_producers"],
        status="running",
        deliverable_digest=request["deliverable_digest"],
        current_attempt=True,
    )
    return record


def register_parent(state, record):
    parent_id = record["parent_effect"]
    if parent_id:
        parent = state["data"]["effect_records"].get(parent_id)
        require(
            parent and parent["kind"] == "dispatch" and parent["status"] == "running",
            "invalid parent effect",
        )
        require(
            record["origin_session"] in parent["child_sessions"], "unregistered child"
        )
        require(
            parent["phase_attempt"] == record["phase_attempt"],
            "parent attempt mismatch",
        )


def lookup(state, session, call):
    record = state["data"].get("effect_records", {}).get(identifier(call))
    require(
        record and record["origin_session"] == session and record["call_id"] == call,
        "unknown immutable session/call",
    )
    integrity(record)
    return record


def identity(state, request):
    record = state["data"].get("effect_records", {}).get(request.get("dispatch_id"))
    require(
        record
        and record["workspace"] == request["workspace"]
        and record["run_id"] == request["run_id"],
        "effect identity mismatch",
    )
    require(
        record["token"] == request.get("effect_token")
        and record["identity_digest"] == request.get("identity_digest"),
        "effect token/identity mismatch",
    )
    integrity(record)
    for key in SUBSTITUTION_FIELDS:
        require(
            key not in request or request[key] == record[key],
            "completion field substitution: " + key,
        )
    return record


def matching_proof(state, request, record):
    reference = sha(request.get("completion_digest"))
    signed = state["data"].get("completion_proofs", {}).get(reference)
    require(
        signed and digest(signed) == reference, "unknown completion evidence digest"
    )
    proof = verify(state["workspace"], signed)
    require(proof.get("kind") == "completion", "wrong evidence kind")
    for key in ["identity_digest", "token", "deliverable_digest"]:
        require(proof[key] == record[key], "proof binding mismatch")
    require(
        proof["producer"] in record["completion_producers"]
        and proof["status"] in TERMINAL,
        "completion producer/status denied",
    )
    sha(proof["evidence_digest"])
    return proof


def permit_completion(state, request, record):
    actor = state["data"]["actors"][request["session_id"]]
    if request["action"] == "reconcile-effect":
        reconcile_authority(actor, request)
    else:
        kind = "dispatch" if request["action"] == "dispatch-end" else "tool"
        require(
            record["kind"] == kind
            and record["origin_session"] == request["session_id"],
            "completion origin/kind mismatch",
        )
    require(record["owner_epoch"] == state["owner_epoch"], "late owner")


def reconcile_authority(actor, request):
    allowed = actor.get("can_reconcile") is True and actor["role"] == "coordinator"
    require(allowed, "reconciler not authorized")
    require(
        len(request.get("reason", "").strip()) >= 20, "reconciliation reason required"
    )
    provenance = request.get("reason_provenance", {})
    require(
        provenance.get("reference") == request["completion_digest"],
        "proof provenance mismatch",
    )
    require(provenance.get("source"), "reason source required")


def replay(state, request):
    record = identity(state, request)
    permit_completion(state, request, record)
    matching_proof(state, request, record)
    if record["status"] in TERMINAL:
        current(state, record, completed=True)
        require(
            record.get("completion_request_digest") == digest(request),
            "conflicting completion replay",
        )
        return True
    return False


def complete(state, request):
    record = identity(state, request)
    permit_completion(state, request, record)
    current(state, record)
    proof = matching_proof(state, request, record)
    children_terminal(state, record, success=proof["status"] == "completed")
    record.update(
        status=proof["status"],
        completion_request_digest=digest(request),
        completion_digest=request["completion_digest"],
        evidence_path="sha256:" + proof["evidence_digest"],
        timestamp=proof["timestamp"],
    )
    state["effects"].remove(record["dispatch_id"])
    record["completion_audit"] = {k: request.get(k) for k in AUDIT_FIELDS}
    if proof["status"] != "completed":
        state["data"]["dispatch_failed"] = True
    if record["kind"] == "dispatch":
        state["data"]["dispatches"][record["dispatch_id"]] = dict(record)


def invalidate_attempt(state, phase):
    item = state["data"]["phases"][str(phase)]
    item["attempt"] = item.get("attempt", 1) + 1
    item["deliverable_digest"] = None
    for records in ["effect_records", "dispatches"]:
        for record in state["data"].get(records, {}).values():
            if record.get("phase") == phase:
                record["current_attempt"] = False
