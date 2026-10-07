#!/usr/bin/env python3
# source-hash: original
"""Tests for scripts/run_all_tests.py.

Every case builds its own temporary scripts/ directory and copies the harness into it, so the
harness never discovers the real scripts/ (and so cannot find this suite and recurse).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(HERE, "run_all_tests.py")
PASS = "import sys\nsys.exit(0)\n"
FAIL = "import sys\nprint('boom')\nsys.exit(1)\n"


class TestHarness(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.scripts = os.path.join(self.td.name, "scripts")
        os.makedirs(self.scripts)
        shutil.copy(HARNESS, os.path.join(self.scripts, "run_all_tests.py"))

    def put(self, name, text=PASS):
        with open(os.path.join(self.scripts, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def run_harness(self):
        cp = subprocess.run([sys.executable, os.path.join(self.scripts, "run_all_tests.py")],
                            cwd=self.td.name, text=True, capture_output=True)
        return cp.returncode, cp.stdout + cp.stderr

    def test_all_passing_exits_0(self):
        self.put("tool.py")
        self.put("test_tool.py")
        rc, out = self.run_harness()
        self.assertEqual(rc, 0, out)
        self.assertIn("ok      test_tool.py", out)

    def test_a_failing_suite_exits_1_and_shows_its_output(self):
        self.put("tool.py")
        self.put("test_tool.py", FAIL)
        rc, out = self.run_harness()
        self.assertEqual(rc, 1, out)
        self.assertIn("FAILED  test_tool.py", out)
        self.assertIn("boom", out)

    def test_a_script_with_no_suite_exits_2_and_is_named(self):
        self.put("tool.py")
        self.put("other.py")
        self.put("test_tool.py")
        rc, out = self.run_harness()
        self.assertEqual(rc, 2, out)
        self.assertIn("other.py has no test_other.py", out)
        self.assertNotIn("tool.py has no", out.replace("other.py has no", ""))

    def test_a_failure_outranks_a_missing_suite(self):
        self.put("other.py")
        self.put("test_tool.py", FAIL)
        rc, out = self.run_harness()
        self.assertEqual(rc, 1, out)
        self.assertIn("other.py has no", out)

    def test_the_harness_itself_needs_no_suite_beside_it(self):
        rc, out = self.run_harness()
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
