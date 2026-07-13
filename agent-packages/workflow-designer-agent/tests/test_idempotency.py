#!/usr/bin/env python3

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

    assert json_1 == json_2, (
        f"validate-package.py is not idempotent: "
        f"run1={results_1['summary']} run2={results_2['summary']}"
    )
    assert results_1["overall"] in ("PASS", "FAIL")


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
    assert all_files_1 == all_files_2
    assert len(all_files_1) > 0


if __name__ == "__main__":
    test_validation_idempotency()
    test_file_structure_stable()
    print("Idempotency tests passed")
