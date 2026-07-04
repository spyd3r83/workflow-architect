#!/usr/bin/env python3
"""
Regression test suite for the Workflow Designer Agent package.
Validates that the canonical package structure is intact and all
required files, sections, and reliability mechanisms are present.
"""

import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import importlib

validate_module = importlib.import_module("validate_package") if False else None
import importlib.util

spec = importlib.util.spec_from_file_location(
    "validate_package", SCRIPTS_DIR / "validate-package.py"
)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)
validate_package = validate_module.validate_package


def test_required_files_exist():
    required = [
        "README.md",
        "AGENTS.md",
        "workflow.md",
        "intake.md",
        "research-protocol.md",
        "quality-control.md",
        "red-team-review.md",
        "package-output-spec.md",
        "implementation-guide.md",
        "fmea.md",
        "traceability-matrix.md",
        "reliability-plan.md",
        "requirements.md",
        "source-log.md",
        "improvement-protocol.md",
        "CHANGELOG.md",
        "defect-patterns.md",
    ]
    failures = []
    for f in required:
        if not (PACKAGE_DIR / f).exists():
            failures.append(f)
    assert not failures, f"Missing required files: {failures}"
    print(f"  PASS: All {len(required)} required top-level files exist")


def test_agents_directory():
    agents_dir = PACKAGE_DIR / "agents"
    assert agents_dir.exists(), "agents/ directory missing"
    agent_files = list(agents_dir.glob("*.md"))
    assert len(agent_files) >= 9, f"Expected ≥9 agent files, found {len(agent_files)}"
    print(f"  PASS: {len(agent_files)} agent files present")


def test_skills_directory():
    skills_dir = PACKAGE_DIR / "skills"
    assert skills_dir.exists(), "skills/ directory missing"
    skill_files = list(skills_dir.glob("*.md"))
    assert len(skill_files) >= 10, f"Expected ≥10 skill files, found {len(skill_files)}"
    print(f"  PASS: {len(skill_files)} skill files present")


def test_templates_directory():
    templates_dir = PACKAGE_DIR / "templates"
    assert templates_dir.exists(), "templates/ directory missing"
    template_files = list(templates_dir.glob("*.md"))
    assert len(template_files) >= 11, (
        f"Expected ≥11 template files, found {len(template_files)}"
    )
    print(f"  PASS: {len(template_files)} template files present")


def test_validation_passes():
    results = validate_package(str(PACKAGE_DIR))
    failed = [c for c in results["checks"] if c["status"] == "FAIL"]
    if failed:
        for c in failed:
            print(f"  FAIL: {c['name']} — {c['evidence']}")
    assert results["overall"] == "PASS", (
        f"Validation failed: {len(failed)} items failed"
    )
    print(
        f"  PASS: validate-package.py reports PASS ({results['summary']['passed']} checks)"
    )


def test_fmea_has_rpn_scoring():
    fmea = (PACKAGE_DIR / "fmea.md").read_text()
    assert "RPN" in fmea, "FMEA missing RPN scoring"
    assert "Severity" in fmea, "FMEA missing Severity"
    assert "Occurrence" in fmea, "FMEA missing Occurrence"
    assert "Detection" in fmea, "FMEA missing Detection"
    assert "Mitigation" in fmea, "FMEA missing Mitigation"
    print("  PASS: FMEA has RPN scoring with S/O/D and mitigations")


def test_traceability_has_requirement_ids():
    trace = (PACKAGE_DIR / "traceability-matrix.md").read_text()
    import re

    req_ids = re.findall(r"REQ-\d{3}", trace)
    assert len(req_ids) >= 10, f"Expected ≥10 requirement IDs, found {len(req_ids)}"
    assert "Verification Method" in trace, (
        "Traceability matrix missing verification method column"
    )
    print(
        f"  PASS: Traceability matrix has {len(req_ids)} requirement IDs with verification"
    )


def test_reliability_plan_has_error_budget():
    plan = (PACKAGE_DIR / "reliability-plan.md").read_text()
    assert "error budget" in plan.lower() or "Error Budget" in plan, (
        "Reliability plan missing error budget"
    )
    assert "0.1%" in plan, "Reliability plan missing 0.1% target"
    assert "idempotency" in plan.lower(), (
        "Reliability plan missing idempotency protocol"
    )
    print(
        "  PASS: Reliability plan has error budget, 0.1% target, and idempotency protocol"
    )


def test_source_log_has_retrieval_ids():
    log = (PACKAGE_DIR / "source-log.md").read_text()
    import re

    ret_ids = re.findall(r"RET-\d{3}", log)
    assert len(ret_ids) >= 2, f"Expected ≥2 retrieval IDs, found {len(ret_ids)}"
    assert "Content Hash" in log, "Source log missing content hash"
    assert "Re-verification" in log or "Re-Verification" in log, (
        "Source log missing re-verification schedule"
    )
    print(
        f"  PASS: Source log has {len(ret_ids)} retrieval IDs with content hashes and re-verification"
    )


def test_requirements_have_acceptance_criteria():
    reqs = (PACKAGE_DIR / "requirements.md").read_text()
    import re

    req_ids = re.findall(r"REQ-\d{3}", reqs)
    assert len(req_ids) >= 20, f"Expected ≥20 requirement IDs, found {len(req_ids)}"
    assert "Acceptance Criteria" in reqs, "Requirements missing acceptance criteria"
    print(
        f"  PASS: Requirements has {len(req_ids)} requirement IDs with acceptance criteria"
    )


def test_workflow_has_oracle_gates():
    workflow = (PACKAGE_DIR / "workflow.md").read_text()
    assert "Oracle gate" in workflow.lower() or "Oracle Gate" in workflow, (
        "Workflow missing Oracle gates"
    )
    assert "Phase 1.5" in workflow, (
        "Workflow missing Phase 1.5 (requirements formalization)"
    )
    assert "Phase 11.5" in workflow, (
        "Workflow missing Phase 11.5 (independent verification)"
    )
    assert "Idempotency" in workflow or "idempotency" in workflow, (
        "Workflow missing idempotency protocol"
    )
    assert "Rollback" in workflow or "rollback" in workflow, (
        "Workflow missing rollback protocol"
    )
    print(
        "  PASS: Workflow has Oracle gates, Phase 1.5, Phase 11.5, idempotency, and rollback"
    )


def test_no_human_in_the_loop():
    import subprocess

    result = subprocess.run(
        ["grep", "-rl", "human-in-the-loop", str(PACKAGE_DIR), "--exclude-dir=tests"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0 or not result.stdout.strip(), (
        f"Found 'human-in-the-loop' references: {result.stdout}"
    )
    print("  PASS: No human-in-the-loop references (all gates are Oracle-in-the-loop)")


def test_quantitative_qc_criteria():
    qc = (PACKAGE_DIR / "quality-control.md").read_text()
    assert "Quantitative Acceptance Criteria" in qc, (
        "QC missing quantitative acceptance criteria"
    )
    assert "Q1" in qc and "Q15" in qc, "QC missing quantitative metrics Q1-Q15"
    assert "validate-package.py" in qc, "QC missing validate-package.py integration"
    print(
        "  PASS: QC has 15 quantitative criteria with validate-package.py integration"
    )


def run_all_tests():
    tests = [
        test_required_files_exist,
        test_agents_directory,
        test_skills_directory,
        test_templates_directory,
        test_validation_passes,
        test_fmea_has_rpn_scoring,
        test_traceability_has_requirement_ids,
        test_reliability_plan_has_error_budget,
        test_source_log_has_retrieval_ids,
        test_requirements_have_acceptance_criteria,
        test_workflow_has_oracle_gates,
        test_no_human_in_the_loop,
        test_quantitative_qc_criteria,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {test.__name__} — {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {test.__name__} — {e}")
            failed += 1
    print(f"\n{'=' * 60}")
    print(
        f"Regression Test Results: {passed} passed, {failed} failed, {len(tests)} total"
    )
    print(f"{'=' * 60}")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run_all_tests() else 1)
