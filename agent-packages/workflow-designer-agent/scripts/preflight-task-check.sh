#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

exec python3 - "$SCRIPT_DIR" "$@" <<'PY'
from __future__ import annotations

import argparse
import base64
import fnmatch
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def strip_jsonc(raw: str) -> str:
    """Remove JSONC comments and trailing commas without changing strings."""
    without_comments: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(raw):
        char = raw[index]
        next_char = raw[index + 1] if index + 1 < len(raw) else ""
        if in_string:
            without_comments.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            without_comments.append(char)
            index += 1
            continue
        if char == "/" and next_char == "/":
            index += 2
            while index < len(raw) and raw[index] not in "\r\n":
                index += 1
            continue
        if char == "/" and next_char == "*":
            index += 2
            while index + 1 < len(raw) and raw[index : index + 2] != "*/":
                index += 1
            index += 2
            continue
        without_comments.append(char)
        index += 1

    text = "".join(without_comments)
    without_trailing_commas: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            without_trailing_commas.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            without_trailing_commas.append(char)
            index += 1
            continue
        if char == ",":
            lookahead = index + 1
            while lookahead < len(text) and text[lookahead].isspace():
                lookahead += 1
            if lookahead < len(text) and text[lookahead] in "}]":
                index += 1
                continue
        without_trailing_commas.append(char)
        index += 1
    return "".join(without_trailing_commas)


def load_jsonc(path: Path, diagnostics: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as error:
        diagnostics.append(f"config_parse_error:{path}:{type(error).__name__}")
        return None
    if not isinstance(data, dict):
        diagnostics.append(f"config_not_object:{path}")
        return None
    return data


def evaluate_task_policy(policy: Any, targets: list[str]) -> tuple[str, list[str]]:
    if policy is None:
        return "implicit-allow", []
    if policy is False or str(policy).lower() == "deny":
        return "deny", targets
    if policy is True or str(policy).lower() in {"allow", "ask"}:
        return str(policy).lower(), []
    if not isinstance(policy, dict):
        return "unknown", []

    denied: list[str] = []
    for target in targets:
        decision = "allow"
        for pattern, action in policy.items():
            if fnmatch.fnmatchcase(target, str(pattern)):
                decision = str(action).lower()
        if decision == "deny":
            denied.append(target)
    return ("deny-partial" if denied else "allow"), denied


def configured_plugin_paths(configs: list[dict[str, Any]]) -> list[Path]:
    result: list[Path] = []
    for config in configs:
        plugins = config.get("plugin", [])
        if not isinstance(plugins, list):
            continue
        for value in plugins:
            if not isinstance(value, str) or not value.startswith("file://"):
                continue
            parsed = urllib.parse.urlparse(value)
            result.append(Path(urllib.parse.unquote(parsed.path)))
    return result


def _build_request(url: str) -> urllib.request.Request:
    request = urllib.request.Request(url)
    password = os.environ.get("OPENCODE_SERVER_PASSWORD")
    if password:
        username = os.environ.get("OPENCODE_SERVER_USERNAME", "opencode")
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        request.add_header("Authorization", f"Basic {token}")
    return request


def query_live_tools(
    server_url: str,
    directory: Path,
    provider: str | None,
    model: str | None,
    agent: str,
) -> tuple[list[str] | None, str | None]:
    query: dict[str, str] = {"directory": str(directory), "agent": agent}
    if provider and model:
        query.update({"provider": provider, "model": model})
        endpoint = "/experimental/tool"
    else:
        endpoint = "/experimental/tool/ids"
    url = server_url.rstrip("/") + endpoint + "?" + urllib.parse.urlencode(query)
    try:
        with urllib.request.urlopen(_build_request(url), timeout=5) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        return None, f"{type(error).__name__}:{error}"
    if not isinstance(payload, list):
        return None, "unexpected_response"
    ids: list[str] = []
    for item in payload:
        if isinstance(item, str):
            ids.append(item)
        elif isinstance(item, dict) and isinstance(item.get("id"), str):
            ids.append(item["id"])
    return ids, None


def query_live_agent_permission(
    server_url: str,
    directory: Path,
    agent: str,
    required_targets: list[str] | None = None,
) -> tuple[str | None, list[str], str | None]:
    query = urllib.parse.urlencode({"directory": str(directory)})
    url = server_url.rstrip("/") + "/agent?" + query
    try:
        with urllib.request.urlopen(_build_request(url), timeout=5) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        return None, [], f"{type(error).__name__}:{error}"
    if not isinstance(payload, list):
        return None, [], "unexpected_response"
    found_agent = False
    agent_perms: list[dict[str, Any]] = []
    for entry in payload:
        if not isinstance(entry, dict) or entry.get("name") != agent:
            continue
        found_agent = True
        agent_perms = entry.get("permission", [])
    if not found_agent:
        return None, [], "agent-not-found"
    targets = required_targets or ["*"]
    denied: list[str] = []
    for target in targets:
        decision = "allow"
        for perm in agent_perms:
            if not isinstance(perm, dict):
                continue
            perm_name = str(perm.get("permission", ""))
            action = str(perm.get("action", "")).lower()
            pattern = str(perm.get("pattern", "*"))
            if perm_name in ("*", "task") and fnmatch.fnmatchcase(target, pattern):
                decision = action
        if decision == "deny":
            denied.append(target)
    effective = "deny" if denied else "allow"
    return effective, denied, None


def auto_detect_server_url() -> str | None:
    """Try to discover the running OpenCode server URL."""
    env = os.environ.get("OPENCODE_SERVER_URL")
    if env:
        return env
    for var in ("OPENCODE_PORT", "OPENCODE_SERVER_PORT"):
        port = os.environ.get(var)
        if port:
            return f"http://127.0.0.1:{port}"
    # Scan ss/netstat for the opencode process
    try:
        result = subprocess.run(
            ["ss", "-tlnp"], capture_output=True, text=True, timeout=5, check=False
        )
        for line in result.stdout.splitlines():
            if "opencode" in line:
                match = re.search(r"(\d+\.\d+\.\d+\.\d+):(\d+)", line)
                if not match:
                    match = re.search(r"127\.0\.0\.1:(\d+)", line)
                if match:
                    full = match.group(0)
                    return f"http://{full}"
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def verify_runtime_evidence(
    server_url: str,
    evidence_id: str,
    parent_session: str | None,
    provider: str | None,
    model: str | None,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    url = server_url.rstrip("/") + "/session/" + urllib.parse.quote(evidence_id)
    try:
        with urllib.request.urlopen(_build_request(url), timeout=5) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return False, ["session_not_found"]
        return False, [f"session_http_error:{error.code}"]
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        return False, [f"session_unreachable:{type(error).__name__}"]
    if not isinstance(payload, dict) or not payload.get("id"):
        return False, ["session_not_found"]

    session_parent = payload.get("parentID") or payload.get("parentId") or payload.get("parent_id")
    title = str(payload.get("title", "")).lower()
    has_task_child_marker = any(
        marker in title for marker in ("omo-subagent", "subagent", "task")
    )
    if not has_task_child_marker:
        errors.append("title_not_task_child")
    if parent_session:
        if session_parent and session_parent != parent_session:
            errors.append(f"parent_mismatch:expected={parent_session},actual={session_parent}")
        elif not session_parent:
            errors.append("parent_not_exposed")
    else:
        errors.append("parent_session_not_supplied")

    if provider and model:
        msg_url = server_url.rstrip("/") + "/session/" + urllib.parse.quote(evidence_id) + "/message"
        try:
            with urllib.request.urlopen(_build_request(msg_url), timeout=5) as response:
                msg_payload = json.load(response)
        except urllib.error.HTTPError as error:
            errors.append(f"message_endpoint_http_error:{error.code}")
            msg_payload = None
        except (OSError, urllib.error.URLError, json.JSONDecodeError):
            errors.append("message_endpoint_unreachable")
            msg_payload = None
        if msg_payload is not None:
            msg_items = msg_payload if isinstance(msg_payload, list) else msg_payload.get("messages", msg_payload.get("data", []))
            confirmed_provider = False
            confirmed_model = False
            for msg in msg_items:
                if not isinstance(msg, dict):
                    continue
                info = msg.get("info", {})
                if not isinstance(info, dict):
                    continue
                if info.get("role") != "assistant":
                    continue
                msg_provider = str(info.get("providerID", ""))
                msg_model = str(info.get("modelID", ""))
                if msg_provider == provider:
                    confirmed_provider = True
                if msg_model == model:
                    confirmed_model = True
            if not confirmed_provider:
                errors.append(f"provider_not_confirmed:{provider}")
            if not confirmed_model:
                errors.append(f"model_not_confirmed:{model}")

    return len(errors) == 0, errors


parser = argparse.ArgumentParser(description="Evidence-gated OpenCode task dispatch preflight")
parser.add_argument("--root", help="Workflow package or repository root")
parser.add_argument("--home", help="Home directory used to resolve global OpenCode config")
parser.add_argument("--agent", default=os.environ.get("OPENCODE_AGENT", "workflow-orchestrator"))
parser.add_argument("--provider", default=os.environ.get("OPENCODE_PROVIDER"))
parser.add_argument("--model", default=os.environ.get("OPENCODE_MODEL"))
parser.add_argument("--server-url", default=os.environ.get("OPENCODE_SERVER_URL"))
parser.add_argument("--omo-config")
parser.add_argument("--omo-dist")
parser.add_argument(
    "--required-targets",
    default="intake-analyst,domain-researcher,workflow-architect,skill-architect,"
    "implementation-planner,quality-reviewer,red-team-reviewer,final-packager,"
    "oracle,explore,librarian",
)
parser.add_argument(
    "--runtime-probe-result",
    choices=("not-run", "pass", "fail"),
    default="not-run",
)
parser.add_argument("--runtime-probe-evidence")
parser.add_argument("--parent-session", default=os.environ.get("OPENCODE_PARENT_SESSION"))
args = parser.parse_args(sys.argv[2:])

script_dir = Path(sys.argv[1]).resolve()
root = Path(args.root).resolve() if args.root else script_dir.parent
home = Path(args.home).resolve() if args.home else Path.home()
targets = [item.strip() for item in args.required_targets.split(",") if item.strip()]
diagnostics: list[str] = []
failures: list[str] = []

config_paths = [
    home / ".config" / "opencode" / "opencode.json",
    home / ".config" / "opencode" / "opencode.jsonc",
    root / "opencode.json",
    root / "opencode.jsonc",
]
configs = [config for path in config_paths if (config := load_jsonc(path, diagnostics))]

task_policy: Any = None
legacy_task_enabled: bool | None = None
for config in configs:
    permission = config.get("permission")
    if isinstance(permission, dict) and "task" in permission:
        task_policy = permission["task"]
    tools = config.get("tools")
    if isinstance(tools, dict) and "task" in tools:
        legacy_task_enabled = bool(tools["task"])
    agents = config.get("agent")
    agent_config = agents.get(args.agent) if isinstance(agents, dict) else None
    if isinstance(agent_config, dict):
        agent_permission = agent_config.get("permission")
        if isinstance(agent_permission, dict) and "task" in agent_permission:
            task_policy = agent_permission["task"]
        agent_tools = agent_config.get("tools")
        if isinstance(agent_tools, dict) and "task" in agent_tools:
            legacy_task_enabled = bool(agent_tools["task"])

policy_status, denied_targets = evaluate_task_policy(task_policy, targets)
if denied_targets:
    failures.append("task_permission_denies:" + ",".join(denied_targets))
if legacy_task_enabled is False:
    failures.append("legacy_tools_task_false")

omo_config_path = (
    Path(args.omo_config).resolve()
    if args.omo_config
    else home / ".config" / "opencode" / "oh-my-openagent.jsonc"
)
omo_config = load_jsonc(omo_config_path, diagnostics)
disabled_tools = omo_config.get("disabled_tools", []) if omo_config else []
omo_task_disabled = isinstance(disabled_tools, list) and "task" in disabled_tools

plugin_candidates: list[Path] = []
if args.omo_dist:
    plugin_candidates.append(Path(args.omo_dist).resolve())
plugin_candidates.extend(configured_plugin_paths(configs))
plugin_candidates.append(home / "GitHub" / "oh-my-openagent" / "dist" / "index.js")
plugin_candidates = list(dict.fromkeys(plugin_candidates))

omo_source_status = "not-found"
omo_source_path = ""
for candidate in plugin_candidates:
    if not candidate.is_file():
        continue
    omo_source_path = str(candidate)
    try:
        source = candidate.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        diagnostics.append(f"source_read_error:{candidate}:{type(error).__name__}")
        continue
    if re.search(r"\btask\s*:\s*delegateTask\b", source):
        omo_source_status = "registered"
    else:
        omo_source_status = "not-confirmed"
    break

enforcer_candidates = [
    root / "scripts" / "enforcement" / "workflow-enforce.sh",
    root / "enforcement" / "workflow-enforce.sh",
]
enforcer_path = next((path for path in enforcer_candidates if path.is_file()), None)
call_omo_status = "enforcer-not-found"
if enforcer_path:
    result = subprocess.run(
        ["bash", str(enforcer_path), "check", "call_omo_agent", "explore"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    output = (result.stdout or result.stderr).strip()
    call_omo_status = "blocked" if output.startswith("block:") else "allowed"
if call_omo_status != "blocked":
    failures.append("call_omo_agent_not_blocked")

live_ids: list[str] | None = None
live_error: str | None = None
effective_task: str | None = None
effective_error: str | None = None
server_url = args.server_url or auto_detect_server_url()
if server_url:
    live_ids, live_error = query_live_tools(
        server_url,
        root,
        args.provider,
        args.model,
        args.agent,
    )
    if live_ids is not None and "task" not in live_ids:
        failures.append("live_server_missing_task")
    effective_task, denied_targets_live, effective_error = query_live_agent_permission(
        server_url, root, args.agent, targets
    )
    if effective_task == "deny":
        failures.append("effective_task_permission_deny:" + ",".join(denied_targets_live))
    elif effective_task is None and effective_error:
        diagnostics.append(f"live_agent_permission:{effective_error}")

runtime_verified = False
runtime_verify_errors: list[str] = []
if args.runtime_probe_result == "pass":
    if not args.runtime_probe_evidence:
        failures.append("runtime_probe_pass_missing_evidence")
    elif not server_url:
        failures.append("runtime_evidence_unverifiable:no_server_url")
    else:
        runtime_verified, runtime_verify_errors = verify_runtime_evidence(
            server_url,
            args.runtime_probe_evidence,
            args.parent_session,
            args.provider,
            args.model,
        )
        if not runtime_verified:
            failures.append("runtime_evidence_verification_failed:" + ";".join(runtime_verify_errors))
elif args.runtime_probe_result == "fail":
    failures.append("runtime_task_call_failed")

print("=== TASK DISPATCH PREFLIGHT ===")
print(f"root: {root}")
print(f"agent: {args.agent}")
print(f"task_permission: {policy_status}")
print(f"denied_targets: {','.join(denied_targets) if denied_targets else 'none'}")
print(f"omo_task_disabled: {'yes' if omo_task_disabled else 'no'}")
print(f"omo_source_registration: {omo_source_status}")
print(f"omo_source_path: {omo_source_path or 'none'}")
if server_url:
    if live_ids is None:
        print(f"live_tool_endpoint: unreachable ({live_error})")
    else:
        task_count = live_ids.count("task")
        print("live_tool_endpoint: reachable")
        print(f"live_task_registrations: {task_count}")
        if task_count > 1:
            print("live_task_registration_note: duplicate IDs reported; verify plugin precedence with a real call")
    if effective_task is not None:
        print(f"effective_task_permission: {effective_task}")
    elif effective_error:
        print(f"effective_task_permission: unreachable ({effective_error})")
else:
    print("live_tool_endpoint: not-probed")
    print("effective_task_permission: not-probed")
print(f"call_omo_agent: {call_omo_status}")
print(f"runtime_task_call: {args.runtime_probe_result}")
print(f"runtime_probe_evidence: {args.runtime_probe_evidence or 'none'}")
print(f"runtime_evidence_verified: {'yes' if runtime_verified else 'no'}")
if runtime_verify_errors:
    print(f"runtime_verify_errors: {';'.join(runtime_verify_errors)}")
for diagnostic in diagnostics:
    print(f"diagnostic: {diagnostic}")

if failures:
    print("VERDICT: FAIL - TASK_DISPATCH_UNAVAILABLE")
    for failure in failures:
        print(f"blocker: {failure}")
    print("Do not fall back to call_omo_agent.")
    raise SystemExit(1)

if args.runtime_probe_result == "pass" and runtime_verified:
    print("VERDICT: PASS - runtime task call verified")
    raise SystemExit(0)

print("VERDICT: UNKNOWN - real task call required")
print("Static or server registration does not prove that this agent session can invoke task().")
print("Attempt one real task(subagent_type=...) call and retain its session/message ID as evidence.")
raise SystemExit(0)
PY
