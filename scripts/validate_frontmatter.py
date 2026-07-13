#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

HARNESS_RELATIVE_DIRS = (
    ".agents/skills",
    ".agent/skills",
    ".claude/skills",
    ".claude/agents",
    ".opencode/agents",
    ".opencode/skills",
    ".devin/agents",
    ".github/agents",
    "skills",
    "agents",
)


def extract_frontmatter(text: str) -> tuple[str | None, str | None]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing opening delimiter '---'"
    for i, line in enumerate(lines[1:], start=1):
        if line == "---":
            return "\n".join(lines[1:i]), None
        if line.startswith("---") and line != "---":
            return None, f"non-standalone closing delimiter at line {i + 1}: {line!r}"
    return None, "missing standalone closing delimiter '---'"


def iter_markdown_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files: list[Path] = []
    for pattern in ("SKILL.md", "AGENT.md", "*.agent.md", "*.md"):
        files.extend(root.rglob(pattern))
    uniq: list[Path] = []
    seen: set[str] = set()
    for path in files:
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        uniq.append(path)
    return sorted(uniq)


def validate_frontmatter_text(
    text: str, *, require_description_str: bool = True
) -> list[str]:
    errors: list[str] = []
    if not text.startswith("---"):
        return errors
    fm, err = extract_frontmatter(text)
    if err:
        return [err]
    if yaml is None:
        return ["PyYAML is required for frontmatter validation"]
    try:
        data = yaml.safe_load(fm)
    except Exception as exc:
        return [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return [f"frontmatter must be a mapping, got {type(data).__name__}"]
    if (
        require_description_str
        and "description" in data
        and not isinstance(data["description"], str)
    ):
        errors.append(
            f"description must be a string, got {type(data['description']).__name__}"
        )
    return errors


def collect_harness_roots(package_dir: Path) -> list[Path]:
    roots: list[Path] = []
    for rel in HARNESS_RELATIVE_DIRS:
        path = package_dir / rel
        if path.exists():
            roots.append(path)
    if package_dir.name == "workflow-designer-agent":
        repo_root = package_dir.parent.parent
        for rel in HARNESS_RELATIVE_DIRS:
            path = repo_root / rel
            if path.exists() and path not in roots:
                roots.append(path)
    return roots


def validate_package_frontmatter(package_dir: str | Path) -> dict[str, Any]:
    pkg = Path(package_dir).resolve()
    results: dict[str, Any] = {
        "package": str(pkg),
        "roots": [],
        "files_scanned": 0,
        "files_with_frontmatter": 0,
        "passed": 0,
        "failed": 0,
        "errors": [],
        "overall": "PASS",
    }
    for root in collect_harness_roots(pkg):
        try:
            root_label = str(root.relative_to(pkg))
        except ValueError:
            root_label = str(root)
        root_result = {
            "root": root_label,
            "files": 0,
            "with_frontmatter": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
        }
        for path in iter_markdown_files(root):
            root_result["files"] += 1
            results["files_scanned"] += 1
            text = path.read_text(errors="replace")
            if not text.startswith("---"):
                continue
            root_result["with_frontmatter"] += 1
            results["files_with_frontmatter"] += 1
            try:
                rel = str(path.relative_to(pkg))
            except ValueError:
                rel = str(path)
            errs = validate_frontmatter_text(text)
            if errs:
                root_result["failed"] += 1
                results["failed"] += 1
                for err in errs:
                    item = {"file": rel, "error": err}
                    root_result["errors"].append(item)
                    results["errors"].append(item)
            else:
                root_result["passed"] += 1
                results["passed"] += 1
        results["roots"].append(root_result)

    if results["failed"] > 0:
        results["overall"] = "FAIL"
    return results


def validate_generated_workflows_tree(generated_root: str | Path) -> dict[str, Any]:
    root = Path(generated_root).resolve()
    summary: dict[str, Any] = {
        "generated_root": str(root),
        "packages": [],
        "passed": 0,
        "failed": 0,
        "overall": "PASS",
    }
    if not root.exists():
        summary["overall"] = "PASS"
        summary["note"] = "generated-workflows directory missing"
        return summary
    for pkg in sorted(p for p in root.iterdir() if p.is_dir()):
        result = validate_package_frontmatter(pkg)
        summary["packages"].append(
            {
                "name": pkg.name,
                "overall": result["overall"],
                "files_with_frontmatter": result["files_with_frontmatter"],
                "passed": result["passed"],
                "failed": result["failed"],
                "errors": result["errors"][:20],
            }
        )
        if result["overall"] == "PASS":
            summary["passed"] += 1
        else:
            summary["failed"] += 1
    if summary["failed"] > 0:
        summary["overall"] = "FAIL"
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate markdown YAML front matter")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Package directory or generated-workflows directory",
    )
    parser.add_argument(
        "--generated-tree",
        action="store_true",
        help="Treat path as generated-workflows root and scan every package",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args(argv)

    target = Path(args.path)
    if args.generated_tree or target.name == "generated-workflows":
        report = validate_generated_workflows_tree(target)
    else:
        report = validate_package_frontmatter(target)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if "packages" in report:
            print(f"Generated workflows scan: {report['overall']}")
            for pkg in report["packages"]:
                print(
                    f"  {pkg['name']}: {pkg['overall']} "
                    f"(fm={pkg['files_with_frontmatter']} ok={pkg['passed']} fail={pkg['failed']})"
                )
                for err in pkg.get("errors", [])[:5]:
                    print(f"    - {err['file']}: {err['error']}")
        else:
            print(
                f"Frontmatter validation: {report['overall']} "
                f"(scanned={report['files_scanned']} fm={report['files_with_frontmatter']} "
                f"ok={report['passed']} fail={report['failed']})"
            )
            for err in report.get("errors", [])[:20]:
                print(f"  - {err['file']}: {err['error']}")

    return 0 if report.get("overall") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
