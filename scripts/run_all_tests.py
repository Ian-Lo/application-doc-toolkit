#!/usr/bin/env python3
# source-hash: original
"""Run every shipped test suite: each scripts/test_*.py, one process apiece.

    python3 scripts/run_all_tests.py

Exit codes: 0 every suite passed; 1 at least one suite failed; 2 a scripts/*.py has no
test_<name>.py beside it (reported even when every suite passes - a script nothing tests is a
script nothing will notice breaking). A failure outranks a missing suite for the exit code.
The directory searched is the one this file sits in, so it can be run from anywhere and a test
can run a copy of it on a tree of its own.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def untested(scripts_dir: str) -> list:
    """Scripts with no suite beside them. Suites themselves and this harness are exempt."""
    missing = []
    for path in sorted(glob.glob(os.path.join(scripts_dir, "*.py"))):
        name = os.path.basename(path)
        if name.startswith("test_") or name == "run_all_tests.py":
            continue
        if not os.path.exists(os.path.join(scripts_dir, "test_" + name)):
            missing.append(name)
    return missing


def main(scripts_dir: str = HERE) -> int:
    suites = sorted(glob.glob(os.path.join(scripts_dir, "test_*.py")))
    failed = []
    for path in suites:
        name = os.path.basename(path)
        cp = subprocess.run([sys.executable, path], cwd=os.path.dirname(scripts_dir) or ".",
                            text=True, capture_output=True)
        if cp.returncode == 0:
            print("ok      %s" % name)
        else:
            failed.append(name)
            print("FAILED  %s (exit %d)" % (name, cp.returncode))
            print("\n".join((cp.stdout + cp.stderr).splitlines()[-15:]))
    missing = untested(scripts_dir)
    for name in missing:
        print("NO SUITE  %s has no test_%s" % (name, name))
    print("%d suite(s), %d failed, %d script(s) without a suite"
          % (len(suites), len(failed), len(missing)))
    return 1 if failed else (2 if missing else 0)


if __name__ == "__main__":
    sys.exit(main())
