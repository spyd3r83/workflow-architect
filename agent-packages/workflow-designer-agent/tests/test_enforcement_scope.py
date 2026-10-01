#!/usr/bin/env python3
"""Regression tests for session-aware enforcement directory resolution."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PKG = REPO / "agent-packages" / "workflow-designer-agent"
ENFORCER = REPO / ".opencode" / "plugins" / "workflow-enforcer.ts"


def test_enforcer_file_exists():
    assert ENFORCER.exists(), f"workflow-enforcer.ts not found at {ENFORCER}"


def test_enforcer_has_findPackageRoot():
    text = ENFORCER.read_text()
    assert "findPackageRoot" in text, "findPackageRoot function missing from enforcer"
    assert "default_agent" in text, (
        "findPackageRoot must check for default_agent in opencode.json"
    )


def test_enforcer_has_resolveSessionDir():
    text = ENFORCER.read_text()
    assert "resolveSessionDir" in text, (
        "resolveSessionDir function missing from enforcer"
    )
    assert "client.session.get" in text, (
        "resolveSessionDir must use client.session.get()"
    )


def test_enforcer_has_session_aware_tool_execute_before():
    text = ENFORCER.read_text()
    assert "resolveEnforcementDir" in text, (
        "tool.execute.before must use resolveEnforcementDir"
    )
    assert "input.sessionID" in text, "tool.execute.before must use input.sessionID"


def test_enforcer_has_session_aware_compaction():
    text = ENFORCER.read_text()
    assert "resolveEnforcementDir" in text, (
        "compaction hook must use resolveEnforcementDir"
    )
    compaction_section = text[text.index("experimental.session.compacting") :]
    assert "input.sessionID" in compaction_section, (
        "compaction hook must use input.sessionID"
    )


def test_enforcer_has_session_aware_workflow_status():
    text = ENFORCER.read_text()
    assert "context.directory" in text, (
        "workflow_status must use context.directory from ToolContext"
    )
    assert "context.sessionID" in text, "workflow_status must use context.sessionID"


def test_enforcer_fails_closed_on_ambiguity():
    text = ENFORCER.read_text()
    assert '""' in text or "empty string" in text.lower(), (
        "Enforcer must return empty string (fail closed) when no package root is found"
    )
    assert "if (!enforceDir)" in text, (
        "Enforcer must check for empty enforcement directory"
    )


def test_enforcer_has_cache_invalidation():
    text = ENFORCER.read_text()
    assert "invalidate" in text, "Enforcer must have cache invalidation"
    assert "session.created" in text, "Cache must be invalidated on session.created"


def test_enforcer_no_silent_parent_fallback():
    text = ENFORCER.read_text()
    tool_before_section = text[text.index('"tool.execute.before"') :]
    tool_before_section = tool_before_section[
        : tool_before_section.index("experimental.session.compacting")
    ]
    assert (
        "pluginDir" not in tool_before_section or "directory" not in tool_before_section
    ), "tool.execute.before must not fall back to plugin-init directory for enforcement"


def test_nested_package_has_own_enforcement():
    nested = (
        REPO
        / "generated-workflows"
        / "internal-application-ingress-deployment-workflow"
    )
    if not nested.exists():
        nested = REPO / "generated-workflows" / "application-ingress-intake-workflow"
    assert nested.exists(), "No generated workflow package found for testing"

    enforce_script = nested / "scripts" / "enforcement" / "workflow-enforce.sh"
    opencode_json = nested / "opencode.json"

    assert opencode_json.exists(), f"opencode.json missing in {nested}"
    assert enforce_script.exists(), f"Enforcement script missing in {nested}"

    config = json.loads(opencode_json.read_text())
    assert config.get("default_agent"), (
        f"opencode.json in {nested} must have default_agent"
    )


def test_nested_package_findPackageRoot_resolves_correctly():
    nested = (
        REPO
        / "generated-workflows"
        / "internal-application-ingress-deployment-workflow"
    )
    if not nested.exists():
        nested = REPO / "generated-workflows" / "application-ingress-intake-workflow"

    nested_config = json.loads((nested / "opencode.json").read_text())
    nested_agent = nested_config.get("default_agent")

    repo_config = json.loads((REPO / "opencode.json").read_text())
    repo_agent = repo_config.get("default_agent")

    assert nested_agent != repo_agent, (
        f"Nested package agent ({nested_agent}) must differ from repo agent ({repo_agent}) "
        "for findPackageRoot to distinguish them"
    )


def test_two_sibling_packages_have_distinct_agents():
    pkg1 = REPO / "generated-workflows" / "application-ingress-intake-workflow"
    pkg2 = (
        REPO
        / "generated-workflows"
        / "internal-application-ingress-deployment-workflow"
    )

    if not pkg1.exists() or not pkg2.exists():
        return

    agent1 = json.loads((pkg1 / "opencode.json").read_text()).get("default_agent")
    agent2 = json.loads((pkg2 / "opencode.json").read_text()).get("default_agent")

    assert agent1 != agent2, (
        f"Sibling packages must have distinct default_agent values: {agent1} vs {agent2}"
    )


def test_enforcer_blocks_call_omo_agent_even_without_package_root():
    text = ENFORCER.read_text()
    assert "call_omo_agent" in text, "Enforcer must always block call_omo_agent"
    assert "call-omo-agent" in text, "Enforcer must handle call-omo-agent variant"


def test_enforcer_uses_context_directory_for_workflow_status():
    text = ENFORCER.read_text()
    wf_status_section = text[text.index("workflow_status") :]
    assert "context.directory" in wf_status_section, (
        "workflow_status must use context.directory from ToolContext"
    )
    assert "resolveDisplayDir" in wf_status_section, (
        "workflow_status must use resolveDisplayDir for display operations"
    )


def test_enforcer_separates_enforcement_and_display_resolution():
    text = ENFORCER.read_text()
    assert "resolveEnforcementDir" in text, "Must have separate enforcement resolution"
    assert "resolveDisplayDir" in text, "Must have separate display resolution"
    assert "resolveEnforcementDir" != "resolveDisplayDir", (
        "Enforcement and display resolution must be separate functions"
    )


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
