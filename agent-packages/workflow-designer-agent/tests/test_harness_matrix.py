#!/usr/bin/env python3

from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PKG = REPO / "agent-packages" / "workflow-designer-agent"

STATUS_VALUES = {"RUNTIME-PROVEN", "RUNTIME-PROVEN (partial)", "BLOCKED", "EXCLUDED"}
HARNESSES = {"OpenCode", "Claude Code", "Codex CLI", "Copilot CLI", "Devin"}


class HarnessMatrixTests(unittest.TestCase):
    def test_matrix_file_exists(self):
        matrix = PKG / "harness-compatibility-matrix.md"
        self.assertTrue(matrix.exists(), "harness-compatibility-matrix.md must exist")

    def test_matrix_covers_all_harnesses(self):
        matrix = PKG / "harness-compatibility-matrix.md"
        if not matrix.exists():
            self.skipTest("matrix missing")
        text = matrix.read_text()
        for h in HARNESSES:
            self.assertIn(h, text, f"matrix must cover harness: {h}")

    def test_matrix_has_status_per_harness(self):
        matrix = PKG / "harness-compatibility-matrix.md"
        if not matrix.exists():
            self.skipTest("matrix missing")
        text = matrix.read_text()
        lines = text.splitlines()

        harness_sections: dict[str, list[str]] = {}
        current = None
        for line in lines:
            if line.startswith("### ") and line != "### Status Definitions":
                current = line.removeprefix("### ").strip()
                harness_sections[current] = []
            elif current and "|" in line and "**Status**" in line:
                harness_sections[current].append(line)

        for harness in HARNESSES:
            matching = [k for k in harness_sections if harness.lower() in k.lower()]
            self.assertTrue(
                matching,
                f"matrix must have a section for {harness}",
            )
            status_lines = harness_sections[matching[0]]
            self.assertTrue(
                status_lines,
                f"matrix must have a Status row for {harness}",
            )
            found = False
            for sl in status_lines:
                for sv in STATUS_VALUES:
                    if sv in sl:
                        found = True
                        break
            self.assertTrue(
                found,
                f"matrix must use a recognized status value for {harness}",
            )

    def test_matrix_summary_table_exists(self):
        matrix = PKG / "harness-compatibility-matrix.md"
        if not matrix.exists():
            self.skipTest("matrix missing")
        text = matrix.read_text()
        self.assertIn("Summary Table", text or "")

    def test_no_unjustified_runtime_claims(self):
        matrix = PKG / "harness-compatibility-matrix.md"
        if not matrix.exists():
            self.skipTest("matrix missing")
        text = matrix.read_text()
        self.assertIn("BLOCKED", text, "at least one harness should be BLOCKED")
        self.assertIn(
            "Container runtime",
            text,
            "matrix must reference container runtime per harness",
        )

    def test_matrix_documents_ci_limits(self):
        matrix = PKG / "harness-compatibility-matrix.md"
        if not matrix.exists():
            self.skipTest("matrix missing")
        text = matrix.read_text()
        self.assertIn("cannot", text.lower(), "matrix must document CI limits honestly")


if __name__ == "__main__":
    unittest.main()
