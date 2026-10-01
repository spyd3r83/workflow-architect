import hashlib
from pathlib import Path
import run_effects as effects
from run_store import require, identifier

READ_TOOLS = {
    "read",
    "glob",
    "grep",
    "lsp_diagnostics",
    "lsp_symbols",
    "workflow_status",
}


def actor_for(state, session) -> dict:
    actor = state["data"].get("actors", {}).get(session)
    require(
        type(actor) is dict and actor.get("role") in {"coordinator", "leaf"},
        "missing actor handoff",
    )
    return actor


def phase_for(state, config):
    phase = state["data"].get("current_phase")
    require(
        type(phase) is int and 1 <= phase <= config["total_phases"], "invalid phase"
    )
    item = state["data"].get("phases", {}).get(str(phase))
    require(type(item) is dict, "missing phase")
    return phase, item


def check(state, config, request):
    actor = actor_for(state, request["session_id"])
    name = request.get("tool", "").lower()
    require(name not in {"call_omo_agent", "call-omo-agent"}, "task-only dispatch")
    if name == "task":
        progression_authority(state, config)
        require(
            actor["role"] == "coordinator" and actor.get("task_available") is True,
            "TASK_DISPATCH_UNAVAILABLE",
        )
        return
    if name == "workflow_status":
        return
    if name == "workflow_action":
        exact_action(state, request)
        return
    require(
        name not in {"bash", "exec"}, "use registered workflow_action; raw shell denied"
    )
    mediate_targets(state, request)
    if name in READ_TOOLS:
        return
    require(name in actor.get("tools", []), "tool outside assigned handoff")
    mutable_phase(state, config, actor)


def progression_authority(state, config):
    effects.authorization(state)
    count = state["data"].get("revision_count", 0)
    limit = state["data"].get("revision_limit", config["max_revisions"])
    require(
        type(count) is int and type(limit) is int and limit > 0,
        "invalid revision budget",
    )
    require(
        not state["data"].get("escalated") and count < limit,
        "revision budget exhausted",
    )


def mutable_phase(state, config, actor):
    progression_authority(state, config)
    phase, item = phase_for(state, config)
    require(not state["data"].get("dispatch_failed"), "dispatch failure unresolved")
    require(
        not config.get("specialist_phase_receipts") or actor["role"] == "leaf",
        "coordinator cannot implement specialist work",
    )
    require(phase in actor.get("phases", []), "phase outside handoff")
    allowed = (
        config["revision_phases"]
        if state["data"].get("revision_mode")
        else config["implementation_phases"]
    )
    require(
        phase in allowed and item.get("status") == "in_progress", "phase is not mutable"
    )
    prior = [state["data"]["phases"][str(p)] for p in range(1, phase)]
    require(all(p.get("gate") == "passed" for p in prior), "prior gates incomplete")


def coordinator(state, request):
    require(
        actor_for(state, request["session_id"])["role"] == "coordinator",
        "coordinator-only transition",
    )


def evidence(request, config):
    value = request.get("evidence", "")
    require(
        isinstance(value, str) and len(value.strip()) >= config["min_evidence_chars"],
        "insufficient evidence",
    )
    return value


def gate(state, config, request):
    coordinator(state, request)
    phase, item = phase_for(state, config)
    require(request.get("phase", phase) == phase, "phase mismatch")
    text = evidence(request, config)
    action = request["action"]
    if action == "fail":
        require(not state["effects"], "cannot reopen while effects remain active")
        effects.invalidate_attempt(state, phase)
        item.update(gate="failed", status="in_progress", evidence=text)
        state["data"].update(dispatch_failed=False, revision_mode=True)
        state["data"]["revision_count"] = state["data"].get("revision_count", 0) + 1
        state["data"]["escalated"] = state["data"]["revision_count"] >= state[
            "data"
        ].get("revision_limit", config["max_revisions"])
        return
    progression_authority(state, config)
    require(
        not state["data"].get("dispatch_failed") and not state["effects"],
        "unresolved dispatch",
    )
    if config.get("specialist_phase_receipts"):
        from network_policy import verify_specialist

        verify_specialist(state, config, phase)
    finish_gate(state, config, request, item, phase, text)


def finish_gate(state, config, request, item, phase, text):
    require(
        item.get("deliverable_digest") == request.get("deliverable_digest")
        and request.get("deliverable_digest"),
        "current deliverable digest required",
    )
    if request["action"] == "pass":
        item.update(gate="passed", status="completed", evidence=text)
    else:
        require(
            item.get("gate") == "passed" and phase < config["total_phases"],
            "advance gate/bounds",
        )
        state["data"]["current_phase"] = phase + 1
        state["data"]["phases"][str(phase + 1)]["status"] = "in_progress"


def dispatch_begin(state, config, request):
    check(state, config, dict(request, tool="task"))
    agent = identifier(request.get("agent"))
    require(
        agent in actor_for(state, request["session_id"]).get("agents", []),
        "agent outside coordinator handoff",
    )
    effects.begin(state, request, "dispatch")


def dispatch_end(state, config, request):
    effects.complete(state, request)


def transition(state, config, request):
    action = request["action"]
    if action in {"pass", "fail", "advance"}:
        gate(state, config, request)
    elif action == "dispatch-begin":
        dispatch_begin(state, config, request)
    elif action in {"dispatch-end", "reconcile-effect"}:
        dispatch_end(state, config, request)
    elif action == "tool-begin":
        check(state, config, request)
        request = dict(request, target_paths=mediate_targets(state, request))
        effects.begin(state, request, "tool")
    elif action == "tool-end":
        effects.complete(state, request)
    else:
        raise ValueError("unsupported transition; legacy writers disabled")


PROTECTED = {
    ".git",
    ".opencode",
    ".claude",
    ".codex",
    ".github",
    ".devin",
    ".agents",
    "enforcement",
    "opencode.json",
    "AGENTS.md",
    "workflow-config.json",
    "workflow-operator.key",
}
PATH_KEYS = ("filePath", "file_path", "path", "file", "directory")
PATCH_PREFIXES = (
    "*** Add File: ",
    "*** Update File: ",
    "*** Delete File: ",
    "*** Move to: ",
)
ACTION_FIELDS = {
    "argv",
    "cwd",
    "classification",
    "scope",
    "inputs",
    "outputs",
    "timeout_ms",
    "executable_sha256",
}


def canonical_target(root, raw):
    require(
        isinstance(raw, str) and raw.strip() == raw and raw, "explicit target required"
    )
    path = Path(raw)
    require(".." not in path.parts, "path traversal denied")
    path = path if path.is_absolute() else root / path
    relative = path.relative_to(root)
    require(
        not any(p in PROTECTED or p.startswith(".env") for p in relative.parts),
        "protected enforcement/config target",
    )
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        require(not cursor.is_symlink(), "symlink target denied")
    require(path.resolve().is_relative_to(root), "target escapes workspace")
    if path.exists() and path.is_file():
        require(path.stat().st_nlink == 1, "hardlinked target denied")
    return path


def patch_targets(text):
    require(isinstance(text, str), "patch text required")
    lines = text.splitlines()
    require(
        lines and lines[0] == "*** Begin Patch" and lines[-1] == "*** End Patch",
        "unsupported patch format",
    )
    paths = []
    for line in lines[1:-1]:
        prefix = next((p for p in PATCH_PREFIXES if line.startswith(p)), None)
        if prefix:
            paths.append(line[len(prefix) :])
        elif line.startswith("***"):
            raise ValueError("unknown patch operation")
    require(0 < len(paths) <= 100, "patch target count invalid")
    return paths


def argument_targets(tool, args):
    require(type(args) is dict, "complete tool arguments required")
    if tool == "apply_patch":
        return patch_targets(args.get("patchText", args.get("patch")))
    paths = [args[key] for key in PATH_KEYS if key in args]
    require(paths, "target missing; implicit cwd denied")
    if tool == "glob":
        pattern = args.get("pattern", "")
        require(
            not Path(pattern).is_absolute() and ".." not in Path(pattern).parts,
            "glob escape denied",
        )
    return paths


def within_scope(root, path, scope):
    for raw in scope:
        allowed = canonical_target(root, raw)
        if path == allowed or (str(raw).endswith("/") and path.is_relative_to(allowed)):
            return True
    return False


def scan_target(root, path):
    if not path.is_dir():
        return
    for index, child in enumerate(path.rglob("*")):
        require(index < 1000, "directory scan exceeds bounded scope")
        canonical_target(root, str(child))


def mediate_targets(state, request):
    root = Path(state["workspace"])
    tool = request["tool"].lower()
    actor = actor_for(state, request["session_id"])
    scope = actor["scope"]["targets"]
    if tool in READ_TOOLS:
        scope = actor["scope"].get("read_targets", scope)
    targets = [
        canonical_target(root, p)
        for p in argument_targets(tool, request.get("arguments"))
    ]
    require(
        all(within_scope(root, p, scope) for p in targets),
        "target outside approved handoff",
    )
    for path in targets:
        scan_target(root, path)
    unlocked_targets(state, [str(p.relative_to(root)) for p in targets])
    return [str(p.relative_to(root)) for p in targets]


def lease_paths(state, targets):
    root = Path(state["workspace"])
    return sorted(
        {str(canonical_target(root, path).relative_to(root)) for path in targets}
    )


def unlocked_targets(state, targets):
    targets = lease_paths(state, targets)
    for key in state["effects"]:
        record = state["data"].get("effect_records", {}).get(key, {})
        for existing in lease_paths(state, record.get("target_paths", [])):
            overlap = any(
                p == "."
                or existing == "."
                or p == existing
                or p.startswith(existing + "/")
                or existing.startswith(p + "/")
                for p in targets
            )
            require(not overlap, "target reserved by active effect")


def exact_action(state, request):
    effects.authorization(state)
    actor = actor_for(state, request["session_id"])
    args = request.get("arguments", {})
    require(set(args) == {"action_id"}, "exact action ID only; no argv override")
    name = identifier(args["action_id"])
    require(name in actor.get("actions", []), "action outside actor grant")
    spec = state["data"].get("action_catalog", {}).get(name)
    require(
        spec and spec["subject_hash"] == effects.digest(spec["definition"]),
        "unpinned action",
    )
    validate_action_files(state, spec["definition"])
    require("workflow_action" in actor["tools"], "action tool not granted")
    action_scope(state, actor, spec["definition"])
    if spec["definition"]["classification"] == "mutation":
        mutable_phase(state, state["data"]["policy_config"], actor)
        approved_action(state, name, spec)
    return spec["definition"]


def action_scope(state, actor, definition):
    root = Path(state["workspace"])
    for raw in definition["outputs"]:
        require(
            within_scope(root, root / raw, actor["scope"]["targets"]),
            "action output outside handoff",
        )
    for raw in definition["inputs"]:
        scope = actor["scope"].get("read_targets", actor["scope"]["targets"])
        require(within_scope(root, root / raw, scope), "action input outside handoff")


def validate_action_definition(spec: dict):
    require(type(spec) is dict and set(spec) == ACTION_FIELDS, "action schema mismatch")
    require(type(spec["argv"]) is list and spec["argv"], "exact argv required")
    require(all(isinstance(x, str) and x for x in spec["argv"]), "invalid argv")
    require(
        spec["classification"] in {"diagnostic", "test", "mutation"},
        "invalid action class",
    )
    collections = type(spec["inputs"]) is dict and type(spec["outputs"]) is list
    require(collections, "pinned inputs/outputs required")
    require(
        type(spec["timeout_ms"]) is int and 1 <= spec["timeout_ms"] <= 30000,
        "bounded timeout required",
    )
    require(
        spec["classification"] == "mutation" or not spec["outputs"],
        "mutation misclassified",
    )
    validate_executable_form(spec)


def validate_executable_form(spec):
    forbidden = {"sh", "bash", "dash", "zsh", "fish", "env", "sudo", "su"}
    require(
        Path(spec["argv"][0]).name not in forbidden, "shell/wrapper executable denied"
    )
    require(
        not any(x in {"-c", "-e", "--eval", "-Command"} for x in spec["argv"][1:]),
        "inline evaluation denied",
    )
    effects.sha(spec["executable_sha256"])


def validate_action_files(state, spec):
    executable = Path(spec["argv"][0])
    require(
        executable.is_absolute() and executable.resolve() == executable,
        "canonical executable required",
    )
    require(
        hashlib.sha256(executable.read_bytes()).hexdigest()
        == spec["executable_sha256"],
        "executable changed",
    )
    root = Path(state["workspace"])
    for path, expected in spec["inputs"].items():
        target = canonical_target(root, path)
        require(
            hashlib.sha256(target.read_bytes()).hexdigest() == expected,
            "pinned input changed",
        )
    for path in spec["outputs"]:
        canonical_target(root, path)


def approved_action(state, name, spec):
    import datetime

    revoked = state["data"]["authorization"].get("revoked_approvals", [])
    require(spec["subject_hash"] not in revoked, "human approval revoked")
    for signed in state["data"].get("human_approvals", {}).values():
        approval = effects.verify(state["workspace"], signed)
        valid = approval_matches(state, name, spec, approval)
        if valid and datetime.datetime.fromisoformat(
            approval["expires_at"]
        ) > datetime.datetime.now(datetime.timezone.utc):
            return
    raise ValueError("current exact-action human approval required")


def approval_matches(state, name, spec, approval):
    phase = state["data"]["current_phase"]
    expected = dict(
        action=name,
        subject_hash=spec["subject_hash"],
        run_id=state["run_id"],
        workspace=state["workspace"],
        target=spec["definition"]["cwd"],
        scope=spec["definition"]["scope"],
        owner_epoch=state["owner_epoch"],
        phase=phase,
        phase_attempt=state["data"]["phases"][str(phase)]["attempt"],
    )
    return all(
        type(approval.get(k)) is type(v) and approval.get(k) == v
        for k, v in expected.items()
    )
