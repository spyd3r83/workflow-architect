#!/usr/bin/env python3

from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PKG = REPO / "agent-packages" / "workflow-designer-agent"


class DispatchContractTests(unittest.TestCase):
    def test_preflight_script_exists(self):
        preflight = REPO / "scripts" / "preflight-task-check.sh"
        self.assertTrue(preflight.exists(), "preflight-task-check.sh must exist")

    def test_preflight_script_executable(self):
        preflight = REPO / "scripts" / "preflight-task-check.sh"
        if not preflight.exists():
            self.skipTest("preflight missing")
        import os

        self.assertTrue(
            os.access(preflight, os.X_OK),
            "preflight-task-check.sh must be executable",
        )

    def test_preflight_reports_a_known_verdict(self):
        import subprocess

        preflight = REPO / "scripts" / "preflight-task-check.sh"
        if not preflight.exists():
            self.skipTest("preflight missing")
        result = subprocess.run(
            ["bash", str(preflight)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertIn(result.returncode, (0, 1))
        self.assertIn("VERDICT", result.stdout)
        self.assertRegex(result.stdout, r"VERDICT: (PASS|FAIL|UNKNOWN)")

    def test_dispatch_protocol_documents_preflight(self):
        protocol = PKG / "dispatch-protocol.md"
        if not protocol.exists():
            self.skipTest("dispatch-protocol missing")
        text = protocol.read_text()
        self.assertIn(
            "preflight",
            text.lower(),
            "dispatch-protocol.md must document the preflight check requirement",
        )

    def test_dispatch_protocol_forbids_call_omo_agent_primary(self):
        protocol = PKG / "dispatch-protocol.md"
        if not protocol.exists():
            self.skipTest("dispatch-protocol missing")
        text = protocol.read_text()
        self.assertIn("forbidden", text.lower())
        self.assertIn(
            "task(subagent_type",
            text,
            "dispatch-protocol must document task() as the dispatch primitive",
        )
        self.assertNotIn(
            "call_omo_agent() (last resort only)",
            text,
            "dispatch-protocol must not advertise call_omo_agent fallback for OpenCode",
        )

    def test_enforcer_blocks_call_omo_agent(self):
        import subprocess

        enforcer = REPO / "scripts" / "enforcement" / "workflow-enforce.sh"
        if not enforcer.exists():
            enforcer = PKG / "enforcement" / "workflow-enforce.sh"
        if not enforcer.exists():
            self.skipTest("enforcer missing")
        result = subprocess.run(
            ["bash", str(enforcer), "check", "call_omo_agent", "explore"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertIn("block", result.stdout.lower())

    def test_no_oracle_allowlist_in_enforcer(self):
        enforcer = PKG / "enforcement" / "workflow-enforce.sh"
        if not enforcer.exists():
            self.skipTest("enforcer missing")
        text = enforcer.read_text()
        oracle_allow = 'tool_arg" = "oracle"'
        self.assertNotIn(
            oracle_allow,
            text,
            "enforcer must not contain Oracle-only call_omo_agent allowlist",
        )

    STALE_PHRASES = [
        "call_omo_agent() is forbidden as a primary path",
        "call_omo_agent() (last resort only)",
        "Use only when `task()` is confirmed unavailable",
        "[FALLBACK — task() unavailable]",
        "last-resort fallback",
        "as a primary path",
    ]

    def _dispatch_doc_files(self) -> list[Path]:
        files = [
            PKG / "dispatch-protocol.md",
            PKG / "agents" / "workflow-orchestrator.md",
            PKG / "AGENTS.md",
            PKG / "workflow.md",
        ]
        for platform_dir in [
            ".opencode/agents",
            ".claude/agents",
            ".github/agents",
            ".devin/agents",
        ]:
            p = REPO / platform_dir / "workflow-orchestrator.md"
            if p.exists():
                files.append(p)
        toml = REPO / ".codex/agents" / "workflow-orchestrator.toml"
        if toml.exists():
            files.append(toml)
        return files

    def test_no_stale_fallback_wording_in_canonical(self):
        for f in self._dispatch_doc_files():
            if not f.exists():
                continue
            text = f.read_text()
            for phrase in self.STALE_PHRASES:
                self.assertNotIn(
                    phrase,
                    text,
                    f"{f.relative_to(REPO)} contains stale phrase: {phrase!r}",
                )

    def test_no_stale_fallback_in_generated_platform_agents(self):
        gen = REPO / "generated-workflows"
        if not gen.is_dir():
            self.skipTest("no generated-workflows")
        count = 0
        for md in gen.rglob("*.md"):
            text = md.read_text(errors="replace")
            for phrase in self.STALE_PHRASES:
                self.assertNotIn(
                    phrase,
                    text,
                    f"{md.relative_to(REPO)} contains stale phrase: {phrase!r}",
                )
            count += 1
        self.assertGreater(count, 0, "should have scanned at least one generated file")

    def test_preflight_unknown_without_runtime_probe(self):
        import subprocess

        preflight = REPO / "scripts" / "preflight-task-check.sh"
        if not preflight.exists():
            self.skipTest("preflight missing")
        result = subprocess.run(
            ["bash", str(preflight)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("VERDICT: UNKNOWN", result.stdout)

    def test_preflight_fail_on_runtime_probe_fail(self):
        import subprocess

        preflight = REPO / "scripts" / "preflight-task-check.sh"
        if not preflight.exists():
            self.skipTest("preflight missing")
        result = subprocess.run(
            ["bash", str(preflight), "--runtime-probe-result", "fail"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("VERDICT: FAIL", result.stdout)
        self.assertIn("runtime_task_call_failed", result.stdout)

    def test_preflight_fail_on_pass_without_evidence(self):
        import subprocess

        preflight = REPO / "scripts" / "preflight-task-check.sh"
        if not preflight.exists():
            self.skipTest("preflight missing")
        result = subprocess.run(
            ["bash", str(preflight), "--runtime-probe-result", "pass"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("VERDICT: FAIL", result.stdout)
        self.assertIn("runtime_probe_pass_missing_evidence", result.stdout)

    def test_jsonc_slash_inside_string_preserved(self):
        import subprocess, tempfile, os

        preflight = REPO / "scripts" / "preflight-task-check.sh"
        if not preflight.exists():
            self.skipTest("preflight missing")
        jsonc_content = """{
  // This is a comment
  "disabled_tools": [],
  "description": "URL with // inside string: https://example.com/path",
  "trailing": "value",
}"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonc", delete=False, dir=str(REPO)
        ) as f:
            f.write(jsonc_content)
            tmp_path = f.name
        try:
            result = subprocess.run(
                ["bash", str(preflight), "--omo-config", tmp_path],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertNotIn(
                "config_parse_error",
                result.stdout,
                "JSONC with // inside strings must parse without error",
            )
        finally:
            os.unlink(tmp_path)

    def test_preflight_detects_explicit_deny(self):
        import subprocess, tempfile, json

        preflight = REPO / "scripts" / "preflight-task-check.sh"
        if not preflight.exists():
            self.skipTest("preflight missing")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "opencode.json").write_text(
                json.dumps(
                    {
                        "agent": {
                            "workflow-orchestrator": {
                                "mode": "primary",
                                "permission": {"task": "deny"},
                            }
                        }
                    }
                )
            )
            result = subprocess.run(
                ["bash", str(preflight), "--root", str(tmpdir)],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("deny", result.stdout.lower())


class MockOpenCodeServer:
    def __init__(self, agents=None, tool_ids=None, sessions=None, messages=None):
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import threading

        self.agents = agents or []
        self.tool_ids = tool_ids or []
        self.sessions = sessions or {}
        self.messages = messages or {}
        self._server = None
        self._thread = None
        self._BaseHTTPRequestHandler = BaseHTTPRequestHandler
        self._HTTPServer = HTTPServer
        self._threading = threading

    def start(self) -> str:
        agents = self.agents
        tool_ids = self.tool_ids
        sessions = self.sessions
        messages = self.messages

        class Handler(self._BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                import json as _json
                from urllib.parse import urlparse, parse_qs

                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                if parsed.path == "/agent":
                    body = _json.dumps(agents)
                elif parsed.path == "/experimental/tool/ids":
                    body = _json.dumps(tool_ids)
                elif parsed.path == "/experimental/tool":
                    body = _json.dumps([{"id": t} for t in tool_ids])
                elif parsed.path.startswith("/session/"):
                    remainder = parsed.path[len("/session/") :]
                    parts = remainder.split("/", 1)
                    sid = parts[0]
                    if len(parts) == 2 and parts[1] == "message":
                        if sid not in messages:
                            self.send_error(404)
                            return
                        body = _json.dumps(messages[sid])
                    else:
                        sess = sessions.get(sid)
                        if sess is None:
                            self.send_error(404)
                            return
                        body = _json.dumps(sess)
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body.encode())

        self._server = self._HTTPServer(("127.0.0.1", 0), Handler)
        self._thread = self._threading.Thread(
            target=self._server.serve_forever, daemon=True
        )
        self._thread.start()
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()


class MockPreflightTests(unittest.TestCase):
    def setUp(self):
        self.preflight = REPO / "scripts" / "preflight-task-check.sh"
        if not self.preflight.exists():
            self.skipTest("preflight missing")
        self._servers: list[MockOpenCodeServer] = []

    def tearDown(self):
        for s in self._servers:
            s.stop()

    def _make_server(self, **kw) -> tuple[MockOpenCodeServer, str]:
        srv = MockOpenCodeServer(**kw)
        url = srv.start()
        self._servers.append(srv)
        return srv, url

    def _run_preflight(self, server_url, *extra):
        import subprocess

        return subprocess.run(
            ["bash", str(self.preflight), "--server-url", server_url, *extra],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_bogus_evidence_rejected(self):
        srv, url = self._make_server(
            agents=[
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "*", "action": "allow", "pattern": "*"},
                        {"permission": "task", "action": "allow", "pattern": "*"},
                    ],
                }
            ],
            tool_ids=["task"],
            sessions={},
        )
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "totally-fake-session",
            "--parent-session",
            "ses_parent",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("session_not_found", result.stdout)

    def test_wrong_parent_rejected(self):
        srv, url = self._make_server(
            agents=[
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "*", "action": "allow", "pattern": "*"},
                        {"permission": "task", "action": "allow", "pattern": "*"},
                    ],
                }
            ],
            tool_ids=["task"],
            sessions={
                "ses_child": {
                    "id": "ses_child",
                    "parentID": "ses_real_parent",
                    "title": "explore subagent dispatch",
                }
            },
        )
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_wrong_parent",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("parent_mismatch", result.stdout)

    def test_missing_live_task_fails(self):
        srv, url = self._make_server(
            agents=[
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "*", "action": "allow", "pattern": "*"},
                        {"permission": "task", "action": "allow", "pattern": "*"},
                    ],
                }
            ],
            tool_ids=["bash", "read", "edit"],
        )
        result = self._run_preflight(url)
        self.assertEqual(result.returncode, 1)
        self.assertIn("live_server_missing_task", result.stdout)

    def test_duplicate_registration_noted(self):
        srv, url = self._make_server(
            agents=[
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "*", "action": "allow", "pattern": "*"},
                        {"permission": "task", "action": "allow", "pattern": "*"},
                    ],
                }
            ],
            tool_ids=["task", "task"],
            sessions={
                "ses_child": {
                    "id": "ses_child",
                    "parentID": "ses_parent",
                    "title": "subagent dispatch",
                }
            },
        )
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_parent",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("live_task_registrations: 2", result.stdout)
        self.assertIn("duplicate", result.stdout.lower())

    def test_enforcer_not_blocking_fails(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            enf_dir = Path(tmpdir, "scripts", "enforcement")
            enf_dir.mkdir(parents=True, exist_ok=True)
            fake_enforcer = enf_dir / "workflow-enforce.sh"
            fake_enforcer.write_text(
                "#!/usr/bin/env bash\necho 'allow: call_omo_agent'\n"
            )
            fake_enforcer.chmod(0o755)
            srv, url = self._make_server(
                agents=[
                    {
                        "name": "workflow-orchestrator",
                        "mode": "primary",
                        "permission": [
                            {"permission": "*", "action": "allow", "pattern": "*"},
                            {"permission": "task", "action": "allow", "pattern": "*"},
                        ],
                    }
                ],
                tool_ids=["task"],
            )
            result = self._run_preflight(url, "--root", str(tmpdir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("call_omo_agent_not_blocked", result.stdout)

    def test_wildcard_allow_then_task_deny(self):
        srv, url = self._make_server(
            agents=[
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "*", "action": "allow", "pattern": "*"},
                        {"permission": "task", "action": "deny", "pattern": "*"},
                    ],
                }
            ],
            tool_ids=["task"],
        )
        result = self._run_preflight(url)
        self.assertEqual(result.returncode, 1)
        self.assertIn("effective_task_permission_deny", result.stdout)

    def test_narrow_allow_does_not_override_global_deny(self):
        srv, url = self._make_server(
            agents=[
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "task", "action": "deny", "pattern": "*"},
                        {"permission": "task", "action": "allow", "pattern": "explore"},
                    ],
                }
            ],
            tool_ids=["task"],
        )
        result = self._run_preflight(url)
        self.assertEqual(result.returncode, 1)
        self.assertIn("effective_task_permission_deny", result.stdout)

    def test_no_parent_supplied_rejects_pass(self):
        srv, url = self._make_server(
            agents=[
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "*", "action": "allow", "pattern": "*"},
                        {"permission": "task", "action": "allow", "pattern": "*"},
                    ],
                }
            ],
            tool_ids=["task"],
            sessions={
                "ses_child": {
                    "id": "ses_child",
                    "parentID": "ses_parent",
                    "title": "subagent dispatch",
                }
            },
        )
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("parent_session_not_supplied", result.stdout)

    def test_verified_evidence_passes(self):
        srv, url = self._make_server(
            agents=[
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "*", "action": "allow", "pattern": "*"},
                        {"permission": "task", "action": "deny", "pattern": "*"},
                        {"permission": "task", "action": "allow", "pattern": "*"},
                    ],
                }
            ],
            tool_ids=["task"],
            sessions={
                "ses_child": {
                    "id": "ses_child",
                    "parentID": "ses_parent",
                    "title": "explore subagent dispatch",
                }
            },
        )
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_parent",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("VERDICT: PASS", result.stdout)
        self.assertIn("runtime_evidence_verified: yes", result.stdout)

    @staticmethod
    def _ASSISTANT_MSG(provider, model):
        return {
            "info": {"role": "assistant", "providerID": provider, "modelID": model},
            "parts": [],
        }

    _USER_MSG = {"info": {"role": "user"}, "parts": []}

    def _verified_server(
        self,
        provider="umans-ai-coding-plan",
        model="umans-glm-5.2",
        title="Dispatch smoke test: explore (@explore subagent)",
        messages=None,
        **kw,
    ):
        defaults = {
            "agents": [
                {
                    "name": "workflow-orchestrator",
                    "mode": "primary",
                    "permission": [
                        {"permission": "*", "action": "allow", "pattern": "*"},
                        {"permission": "task", "action": "deny", "pattern": "*"},
                        {"permission": "task", "action": "allow", "pattern": "*"},
                    ],
                }
            ],
            "tool_ids": ["task"],
            "sessions": {
                "ses_child": {
                    "id": "ses_child",
                    "parentID": "ses_parent",
                    "title": title,
                }
            },
            "messages": {
                "ses_child": messages
                if messages is not None
                else [
                    self._USER_MSG,
                    self._ASSISTANT_MSG(provider, model),
                ]
            },
        }
        defaults.update(kw)
        return self._make_server(**defaults)

    def test_provider_model_exact_match_passes(self):
        srv, url = self._verified_server()
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_parent",
            "--provider",
            "umans-ai-coding-plan",
            "--model",
            "umans-glm-5.2",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("VERDICT: PASS", result.stdout)

    def test_wrong_provider_rejected(self):
        srv, url = self._verified_server()
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_parent",
            "--provider",
            "definitely-wrong-provider",
            "--model",
            "umans-glm-5.2",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("provider_not_confirmed", result.stdout)

    def test_wrong_model_rejected(self):
        srv, url = self._verified_server()
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_parent",
            "--provider",
            "umans-ai-coding-plan",
            "--model",
            "definitely-wrong-model",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("model_not_confirmed", result.stdout)

    def test_no_assistant_message_rejected(self):
        srv, url = self._verified_server(messages=[self._USER_MSG])
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_parent",
            "--provider",
            "umans-ai-coding-plan",
            "--model",
            "umans-glm-5.2",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("provider_not_confirmed", result.stdout)
        self.assertIn("model_not_confirmed", result.stdout)

    def test_message_endpoint_unreachable_rejected(self):
        srv, url = self._verified_server()
        srv.messages.clear()
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_parent",
            "--provider",
            "umans-ai-coding-plan",
            "--model",
            "umans-glm-5.2",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("message_endpoint", result.stdout)

    def test_title_lacks_markers_rejected_no_crash(self):
        srv, url = self._verified_server(title="Just a regular conversation")
        result = self._run_preflight(
            url,
            "--runtime-probe-result",
            "pass",
            "--runtime-probe-evidence",
            "ses_child",
            "--parent-session",
            "ses_parent",
            "--provider",
            "umans-ai-coding-plan",
            "--model",
            "umans-glm-5.2",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("title_not_task_child", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
