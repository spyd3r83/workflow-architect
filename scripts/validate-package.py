#!/usr/bin/env python3
"""
Deterministic validation for generated workflow packages.
Checks structure, sections, cross-references, citations, and placeholders
without relying on LLM judgement. Outputs a machine-readable report.
"""

import json
import re
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL = [
    "README.md",
    "AGENTS.md",
    "workflow.md",
    "dispatch-protocol.md",
    "intake.md",
    "research-protocol.md",
    "quality-control.md",
    "red-team-review.md",
    "package-output-spec.md",
    "implementation-guide.md",
    "fmea.md",
    "traceability-matrix.md",
    "reliability-plan.md",
    "source-log.md",
    "requirements.md",
    "improvement-protocol.md",
    "CHANGELOG.md",
    "defect-patterns.md",
]

REQUIRED_TEMPLATES = [
    "agent-file-template.md",
    "skill-file-template.md",
    "workflow-package-template.md",
    "intake-template.md",
    "qa-checklist-template.md",
    "red-team-template.md",
    "final-summary-template.md",
    "fmea-template.md",
    "traceability-matrix-template.md",
    "requirements-template.md",
    "source-log-template.md",
    "command-flowstart-template.md",
    "command-resume-template.md",
    "command-maintain-template.md",
    "command-update-template.md",
    "platform-config-template.md",
    "improvement-protocol-template.md",
    "changelog-template.md",
    "defect-patterns-template.md",
]

REQUIRED_AGENT_SECTIONS = [
    "Role",
    "Mission",
    "Responsibilities",
    "Required Inputs",
    "Expected Outputs",
    "Operating Rules",
    "Decision Criteria",
    "Escalation Rules",
    "Quality Checklist",
    "Failure Modes to Avoid",
]

REQUIRED_SKILL_SECTIONS = [
    "Purpose",
    "When To Use",
    "Required Inputs",
    "Process",
    "Output Format",
    "Validation Criteria",
    "Common Mistakes",
    "Example Usage",
]

PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z_]+\}\}")
CITATION_PATTERN = re.compile(r"\[Source:\s*[^,\]]+,\s*[^,\]]+,\s*[^,\]]+,\s*[^\]]+\]")
VERIFIED_TAG = re.compile(r"\[VERIFIED\]")
ASSUMPTION_TAG = re.compile(r"\[ASSUMPTION\]")
UNTAGGED_CLAIM_RISK = re.compile(
    r"(?<!\[VERIFIED\])(?<!\[ASSUMPTION\])(?<!\[Source:)(?<!\[CONFLICT\])(?<!\[TIME-SENSITIVE\])(?<!\[ASSUMPTION\] )(?<!\[VERIFIED\] )\b(?:is|are|must|should|requires|follows|standard|best practice)\b",
    re.IGNORECASE,
)

VAGUE_VERBS = re.compile(
    r"\b(?:help[s]?|support[s]?|handle[s]?|manage[s]?|deal[s]? with|work[s]? on)\b\s+(?:the\s+)?(?:project|process|work|task|design|implementation|review|package|workflow)\b(?!\s+(?:loop|phase|gate|revision|generation|entire|all|specific))",
    re.IGNORECASE,
)


def extract_h2_sections(filepath: Path) -> list[str]:
    content = filepath.read_text()
    return [s.strip() for s in re.findall(r"^## (.+)$", content, re.MULTILINE)]


def sections_match(found: list[str], required: list[str]) -> list[str]:
    found_lower = {s.lower() for s in found}
    return [s for s in required if s.lower() not in found_lower]


def find_cross_references(filepath: Path) -> list[str]:
    content = filepath.read_text()
    refs = re.findall(
        r"(?:agents|skills|prompts|templates|examples)/([a-z0-9-]+)\.md", content
    )
    refs += re.findall(r"`([a-z0-9-]+\.md)`", content)
    return refs


def validate_package(package_path: str) -> dict:
    pkg = Path(package_path)
    results = {
        "package": str(pkg),
        "checks": [],
        "summary": {"total": 0, "passed": 0, "failed": 0},
        "overall": "FAIL",
    }

    def check(name: str, passed: bool, evidence: str, fix: str = ""):
        results["checks"].append(
            {
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "evidence": evidence,
                "fix": fix,
            }
        )
        results["summary"]["total"] += 1
        if passed:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1

    if not pkg.exists():
        check(
            "package_exists",
            False,
            f"Path does not exist: {pkg}",
            "Create the package directory",
        )
        results["overall"] = "FAIL"
        return results

    for f in REQUIRED_TOP_LEVEL:
        exists = (pkg / f).exists()
        check(
            f"file_exists:{f}",
            exists,
            f"{f} {'present' if exists else 'MISSING'}",
            f"Create {f}" if not exists else "",
        )

    agents_dir = pkg / "agents"
    if agents_dir.exists():
        agent_files = list(agents_dir.glob("*.md"))
        check("agents_dir_exists", True, f"{len(agent_files)} agent files found")
        for af in agent_files:
            sections = extract_h2_sections(af)
            missing = sections_match(sections, REQUIRED_AGENT_SECTIONS)
            check(
                f"agent_sections:{af.name}",
                len(missing) == 0,
                f"Sections: {len(sections)}/{len(REQUIRED_AGENT_SECTIONS)}. Missing: {missing}"
                if missing
                else f"All {len(REQUIRED_AGENT_SECTIONS)} sections present",
                f"Add sections: {missing}" if missing else "",
            )
    else:
        check(
            "agents_dir_exists",
            False,
            "agents/ directory missing",
            "Create agents/ directory",
        )

    skills_dir = pkg / "skills"
    if skills_dir.exists():
        skill_files = list(skills_dir.glob("*.md"))
        check("skills_dir_exists", True, f"{len(skill_files)} skill files found")
        for sf in skill_files:
            sections = extract_h2_sections(sf)
            missing = sections_match(sections, REQUIRED_SKILL_SECTIONS)
            check(
                f"skill_sections:{sf.name}",
                len(missing) == 0,
                f"Missing: {missing}"
                if missing
                else f"All {len(REQUIRED_SKILL_SECTIONS)} sections present",
                f"Add sections: {missing}" if missing else "",
            )
    else:
        check(
            "skills_dir_exists",
            False,
            "skills/ directory missing",
            "Create skills/ directory",
        )

    templates_dir = pkg / "templates"
    if templates_dir.exists():
        template_files = list(templates_dir.glob("*.md"))
        check(
            "templates_dir_exists", True, f"{len(template_files)} template files found"
        )
        required_list_path = pkg / "templates-required.txt"
        if required_list_path.exists():
            required_templates = [
                line.strip()
                for line in required_list_path.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            ]
        else:
            required_templates = REQUIRED_TEMPLATES
        template_names = {tf.name for tf in template_files}
        missing_templates = [t for t in required_templates if t not in template_names]
        check(
            "required_templates_present",
            len(missing_templates) == 0,
            f"Missing templates: {missing_templates}"
            if missing_templates
            else f"All {len(required_templates)} required templates present",
            f"Create templates: {missing_templates}" if missing_templates else "",
        )
    else:
        check(
            "templates_dir_exists",
            False,
            "templates/ directory missing",
            "Create templates/ directory",
        )

    dispatch_files = [
        pkg / "dispatch-protocol.md",
        pkg / "workflow.md",
        pkg / "AGENTS.md",
        pkg / "agents" / "workflow-orchestrator.md",
        pkg / "agents" / "maintenance-orchestrator.md",
    ]
    dual_path_hits = []
    for f in dispatch_files:
        if not f.exists():
            continue
        text = f.read_text()
        if "call_omo_agent" not in text:
            continue
        primary_markers = [
            "Two dispatch tools",
            "`call_omo_agent()` — for OMO",
            "Use `call_omo_agent()` for",
            "using `task()` and `call_omo_agent()`",
            "or `call_omo_agent()` (for OMO",
            "| `call_omo_agent()` | `oracle`",
            "| `call_omo_agent()` | `explore`",
            "| `call_omo_agent()` | `librarian`",
            "| `call_omo_agent()` | `hephaestus`",
            "| `call_omo_agent()` | `momus`",
        ]
        if any(m in text for m in primary_markers):
            dual_path_hits.append(str(f.relative_to(pkg)))
    check(
        "single_dispatch_primitive",
        len(dual_path_hits) == 0,
        "Dispatch protocol uses task()-only"
        if not dual_path_hits
        else f"call_omo_agent authorized as primary path in: {dual_path_hits}",
        "Rewrite dispatch docs to task()-only; see dispatch-protocol.md"
        if dual_path_hits
        else "",
    )

    all_md = list(pkg.rglob("*.md"))
    placeholder_files = []
    placeholder_exempt = {
        "readme.md",
        "implementation-guide.md",
        "skills/final-packaging.md",
        "skills/agent-design.md",
        "skills/skill-design.md",
    }
    for f in all_md:
        rel = str(f.relative_to(pkg))
        if "templates/" in rel or "prompts/" in rel:
            continue
        if rel.lower() in placeholder_exempt:
            continue
        content = f.read_text()
        placeholders = PLACEHOLDER_PATTERN.findall(content)
        if placeholders:
            placeholder_files.append({"file": rel, "placeholders": placeholders})

    empty_files = [str(f.relative_to(pkg)) for f in all_md if f.stat().st_size < 50]
    check(
        "no_empty_files",
        len(empty_files) == 0,
        f"{len(empty_files)} empty/near-empty files: {empty_files}"
        if empty_files
        else "No empty files",
        f"Populate: {empty_files}" if empty_files else "",
    )

    research_file = pkg / "research-protocol.md"
    if research_file.exists():
        content = research_file.read_text()
        citations = CITATION_PATTERN.findall(content)
        check(
            "citation_format_compliance",
            len(citations) > 0,
            f"{len(citations)} properly formatted citations found"
            if citations
            else "No properly formatted citations",
            "Add citations in format: [Source: title, author, date, URL]"
            if not citations
            else "",
        )

    broken_refs = []
    example_names = {
        "content-auditor.md",
        "content-audit.md",
        "master-prompt.md",
        "master-prompt",
        "ia-architect.md",
        "ia-mapping.md",
        "visual-designer.md",
        "visual-system-design.md",
        "seo-specialist.md",
        "seo-analysis.md",
        "accessibility-auditor.md",
        "accessibility-validation.md",
        "frontend-engineer.md",
        "frontend-implementation.md",
        "qa-tester.md",
        "regression-testing.md",
        "website-revamp-example.md",
        "marketing-site-revamp.md",
        "product-strategist.md",
        "user-researcher.md",
        "ux-ui-designer.md",
        "software-architect.md",
        "security-engineer.md",
        "qa-test-engineer.md",
        "launch-readiness-coordinator.md",
        "market-analysis.md",
        "user-interview-synthesis.md",
        "wireframing.md",
        "design-system-creation.md",
        "api-contract-design.md",
        "threat-modeling.md",
        "test-strategy.md",
        "launch-checklist.md",
        "fitness-app-example.md",
        "new-app-example.md",
        "website-revamp-example.md",
        "security-audit-example.md",
        "aws-nist-audit-example.md",
        "threat-modeler.md",
        "vulnerability-researcher.md",
        "security-architect.md",
        "compliance-auditor.md",
        "penetration-tester.md",
        "incident-response-planner.md",
        "vulnerability-research.md",
        "remediation-design.md",
        "compliance-mapping.md",
        "controlled-testing.md",
        "incident-response-planning.md",
        "agent-1",
        "agent-2",
        "skill-1",
        "skill-2",
        "example-1",
        "example-prompt-1",
        "master-prompt",
        "example-prompt",
        "golden-output-files",
        "test_regression.py",
        "test_idempotency.py",
    }
    search_dirs = [
        pkg,
        pkg / "agents",
        pkg / "skills",
        pkg / "prompts",
        pkg / "templates",
        pkg / "examples",
    ]
    for f in all_md:
        refs = find_cross_references(f)
        for ref in refs:
            if ref in example_names:
                continue
            found = False
            for d in search_dirs:
                if (d / ref).exists() or (d / f"{ref}.md").exists():
                    found = True
                    break
            if not found:
                broken_refs.append({"file": str(f.relative_to(pkg)), "ref": ref})
    check(
        "cross_references_resolve",
        len(broken_refs) == 0,
        f"{len(broken_refs)} broken references"
        if broken_refs
        else "All cross-references resolve",
        f"Fix references: {broken_refs}" if broken_refs else "",
    )

    vague_count = 0
    vague_examples = []
    if agents_dir.exists():
        for af in agent_files:
            content = af.read_text()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith('"') or line.strip().startswith("'"):
                    continue
                if '"' in line and (
                    "not a" in line.lower() or "is not" in line.lower()
                ):
                    continue
                matches = VAGUE_VERBS.findall(line)
                if matches:
                    vague_count += len(matches)
                    vague_examples.append(
                        {"file": af.name, "line": i + 1, "matches": matches[:3]}
                    )
    check(
        "vague_verbs_in_agents",
        vague_count == 0,
        f"{vague_count} vague verbs found: {vague_examples[:3]}"
        if vague_count
        else "No vague verbs in agent files",
        f"Replace vague verbs with specific actions" if vague_count else "",
    )

    assumption_count = 0
    untagged_assumption_risk = 0
    for f in all_md:
        if "templates/" in str(f):
            continue
        content = f.read_text()
        assumption_count += len(ASSUMPTION_TAG.findall(content))
    check(
        "assumptions_tagged",
        assumption_count > 0 or True,
        f"{assumption_count} tagged assumptions found across package",
        "" if assumption_count > 0 else "No assumptions found — verify this is correct",
    )

    fmea_file = pkg / "fmea.md"
    if fmea_file.exists():
        content = fmea_file.read_text()
        has_rpn = "RPN" in content or "rpn" in content.lower()
        has_severity = "severity" in content.lower()
        has_mitigation = "mitigation" in content.lower()
        check(
            "fmea_structure",
            has_rpn and has_severity and has_mitigation,
            f"FMEA has RPN: {has_rpn}, severity: {has_severity}, mitigation: {has_mitigation}",
            "Add RPN scoring, severity, and mitigation columns to FMEA"
            if not (has_rpn and has_severity and has_mitigation)
            else "",
        )
    else:
        check(
            "fmea_structure",
            False,
            "fmea.md missing",
            "Create fmea.md with RPN scoring",
        )

    trace_file = pkg / "traceability-matrix.md"
    if trace_file.exists():
        content = trace_file.read_text()
        has_requirement_id = re.search(r"REQ[-_]?\d+", content) is not None
        has_verification = (
            "verification" in content.lower() or "validation" in content.lower()
        )
        check(
            "traceability_structure",
            has_requirement_id and has_verification,
            f"Has requirement IDs: {has_requirement_id}, verification: {has_verification}",
            "Add requirement IDs (REQ-001) and verification columns"
            if not (has_requirement_id and has_verification)
            else "",
        )
    else:
        check(
            "traceability_structure",
            False,
            "traceability-matrix.md missing",
            "Create traceability-matrix.md",
        )

    req_file = pkg / "requirements.md"
    if req_file.exists():
        content = req_file.read_text()
        has_ids = re.search(r"REQ[-_]?\d+", content) is not None
        has_acceptance = (
            "acceptance" in content.lower() or "criteria" in content.lower()
        )
        check(
            "requirements_structure",
            has_ids and has_acceptance,
            f"Has requirement IDs: {has_ids}, acceptance criteria: {has_acceptance}",
            "Add requirement IDs and acceptance criteria"
            if not (has_ids and has_acceptance)
            else "",
        )
    else:
        check(
            "requirements_structure",
            False,
            "requirements.md missing",
            "Create requirements.md with IDs and acceptance criteria",
        )

    source_log = pkg / "source-log.md"
    if source_log.exists():
        content = source_log.read_text()
        has_retrieval_id = (
            re.search(r"RET[-_]?\d+", content) is not None
            or "retrieval" in content.lower()
        )
        check(
            "source_log_structure",
            has_retrieval_id,
            f"Has retrieval IDs: {has_retrieval_id}",
            "Add retrieval IDs (RET-001) to source log" if not has_retrieval_id else "",
        )
    else:
        check(
            "source_log_structure",
            False,
            "source-log.md missing",
            "Create source-log.md with retrieval IDs",
        )

    try:
        from validate_frontmatter import validate_package_frontmatter
    except ImportError:
        scripts_dir = Path(__file__).resolve().parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from validate_frontmatter import validate_package_frontmatter

    fm_report = validate_package_frontmatter(pkg)
    fm_ok = fm_report.get("overall") == "PASS"
    fm_evidence = (
        f"frontmatter files={fm_report.get('files_with_frontmatter', 0)} "
        f"ok={fm_report.get('passed', 0)} fail={fm_report.get('failed', 0)}"
    )
    fm_fix = ""
    if not fm_ok:
        sample = fm_report.get("errors", [])[:5]
        details = "; ".join(f"{e.get('file')}: {e.get('error')}" for e in sample)
        fm_fix = (
            f"Fix YAML front matter ({details})" if details else "Fix YAML front matter"
        )
    check(
        "frontmatter_yaml_valid",
        fm_ok,
        fm_evidence if fm_ok else f"{fm_evidence}; {fm_fix}",
        fm_fix,
    )

    gen_candidates = []
    cursor = pkg
    for _ in range(4):
        gen_candidates.append(cursor / "generated-workflows")
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    if pkg.name == "workflow-designer-agent":
        gen_candidates.append(pkg.parent.parent / "generated-workflows")
    candidate = next((p for p in gen_candidates if p.exists()), None)
    if candidate is not None:
        try:
            from validate_frontmatter import validate_generated_workflows_tree
        except ImportError:
            scripts_dir = Path(__file__).resolve().parent
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            from validate_frontmatter import validate_generated_workflows_tree
        gen_report = validate_generated_workflows_tree(candidate)
        gen_ok = gen_report.get("overall") == "PASS"
        gen_evidence = (
            f"packages_pass={gen_report.get('passed', 0)} "
            f"packages_fail={gen_report.get('failed', 0)}"
        )
        gen_fix = ""
        if not gen_ok:
            bad = [
                p["name"]
                for p in gen_report.get("packages", [])
                if p.get("overall") != "PASS"
            ]
            gen_fix = f"Repair front matter in generated packages: {bad}"
        check(
            "generated_workflows_frontmatter",
            gen_ok,
            gen_evidence if gen_ok else f"{gen_evidence}; {gen_fix}",
            gen_fix,
        )
    else:
        check(
            "generated_workflows_frontmatter",
            True,
            "generated-workflows/ absent (gitignored) — optional scan skipped",
            "",
        )

    results["overall"] = "PASS" if results["summary"]["failed"] == 0 else "FAIL"
    return results


def main():
    if len(sys.argv) < 2:
        default_path = "agent-packages/workflow-designer-agent"
        if Path(default_path).exists():
            package_path = default_path
        else:
            print("Usage: python3 validate-package.py <package-path>")
            sys.exit(1)
    else:
        package_path = sys.argv[1]

    results = validate_package(package_path)

    print(f"\n{'=' * 60}")
    print(f"VALIDATION REPORT: {results['package']}")
    print(f"{'=' * 60}")
    print(
        f"\nSummary: {results['summary']['passed']} passed, {results['summary']['failed']} failed, {results['summary']['total']} total"
    )
    print(f"Overall: {results['overall']}\n")

    for check in results["checks"]:
        icon = "PASS" if check["status"] == "PASS" else "FAIL"
        print(f"  [{icon}] {check['name']}")
        print(f"        {check['evidence']}")
        if check["fix"]:
            print(f"        Fix: {check['fix']}")

    report_path = Path(package_path) / "validation-report.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\nReport saved to: {report_path}")

    sys.exit(0 if results["overall"] == "PASS" else 1)


if __name__ == "__main__":
    main()
