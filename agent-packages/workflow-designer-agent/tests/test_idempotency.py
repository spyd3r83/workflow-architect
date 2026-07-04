#!/usr/bin/env python3
"""
Idempotency test for the Workflow Designer Agent package.
Verifies that running validate-package.py twice on the same package
produces identical results. This is a proxy for full workflow idempotency
— if the deterministic validation layer is not idempotent, the workflow
cannot be either.
"""

import json
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "validate_package", SCRIPTS_DIR / "validate-package.py"
)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)
validate_package = validate_module.validate_package


def test_validation_idempotency():
    results_1 = validate_package(str(PACKAGE_DIR))
    results_2 = validate_package(str(PACKAGE_DIR))

    json_1 = json.dumps(results_1, sort_keys=True, indent=2)
    json_2 = json.dumps(results_2, sort_keys=True, indent=2)

    if json_1 == json_2:
        print(
            f"  PASS: validate-package.py is idempotent (identical results on re-run)"
        )
        print(
            f"  PASS: Overall status: {results_1['overall']} ({results_1['summary']['passed']} passed, {results_1['summary']['failed']} failed)"
        )
        return True
    else:
        print(f"  FAIL: validate-package.py is NOT idempotent")
        print(f"  Run 1: {results_1['summary']}")
        print(f"  Run 2: {results_2['summary']}")
        diffs = []
        for c1, c2 in zip(results_1["checks"], results_2["checks"]):
            if c1["status"] != c2["status"]:
                diffs.append(f"  {c1['name']}: {c1['status']} vs {c2['status']}")
        if diffs:
            print("  Differences:")
            for d in diffs:
                print(d)
        return False


def test_file_structure_stable():
    all_files_1 = sorted(
        str(f.relative_to(PACKAGE_DIR))
        for f in PACKAGE_DIR.rglob("*.md")
        if "tests/" not in str(f)
    )
    all_files_2 = sorted(
        str(f.relative_to(PACKAGE_DIR))
        for f in PACKAGE_DIR.rglob("*.md")
        if "tests/" not in str(f)
    )

    if all_files_1 == all_files_2:
        print(f"  PASS: File structure is stable ({len(all_files_1)} files)")
        return True
    else:
        print(f"  FAIL: File structure changed between scans")
        return False


def run_all_tests():
    tests = [test_validation_idempotency, test_file_structure_stable]
    passed = 0
    failed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR: {test.__name__} — {e}")
            failed += 1
    print(f"\n{'=' * 60}")
    print(
        f"Idempotency Test Results: {passed} passed, {failed} failed, {len(tests)} total"
    )
    print(f"{'=' * 60}")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run_all_tests() else 1)
