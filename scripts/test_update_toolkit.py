#!/usr/bin/env python3
# source-hash: original
"""Tests for scripts/update_toolkit.py.

Stdlib unittest. The integration tests build two throwaway git repositories under `tempfile`
- a stand-in for the public toolkit and a stand-in for a user's private copy - and run the
update between them over a local path; no network, and never the real repository.

The property that matters most is the path split: an update replaces toolkit files and
touches nothing personal, whatever else is going on. The rest pins the reporting the
orchestrator relies on (the *What changed* entries, the LIBRARY EDIT flag), the refusals
(uncommitted toolkit edits, a failed fetch) and the rollback on a failed shipped suite.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import update_toolkit as u  # noqa: E402

GIT_ID = ["-c", "user.name=test", "-c", "user.email=test@example.invalid"]

README_V1 = """# toolkit

## What changed

<!-- newest first -->
- 2026-01-01 - first entry.

## Using it
"""
README_V2 = """# toolkit

## What changed

<!-- newest first -->
- 2026-02-01 - LIBRARY EDIT: the lint now reads a `Tags:` line; add one to every entry.
- 2026-01-15 - the review checklist gained a section.
- 2026-01-01 - first entry.

## Using it
"""
PASSING_SUITE = "import sys\nsys.exit(0)\n"
FAILING_SUITE = "import sys\nprint('boom')\nsys.exit(1)\n"


def sh(cwd, *args):
    return subprocess.run(["git", *GIT_ID, *args], cwd=cwd, text=True, capture_output=True,
                          check=True).stdout


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def init(root):
    sh(root, "init", "-q", "-b", "main")


def commit_all(root, msg):
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", msg)


TOOLKIT_V1 = {
    "CLAUDE.md": "rules v1\n",
    "README.md": README_V1,
    "docs/Review_Checklist.md": "checklist v1\n",
    "scripts/new_application.py": "print('v1')\n",
    "scripts/test_new_application.py": PASSING_SUITE,
    ".claude/settings.json": "{}\n",
    "Fact_Library_TEMPLATE.md": "template v1\n",
}
TOOLKIT_V2 = dict(TOOLKIT_V1, **{
    "README.md": README_V2,
    "docs/Review_Checklist.md": "checklist v2\n",
    "scripts/update_toolkit.py": "print('new script')\n",
    "scripts/test_update_toolkit.py": PASSING_SUITE,
})
PERSONAL = {
    "Fact_Library.md": "my facts\n",
    "Open_Questions.md": "my questions\n",
    "Applications/2026-01-02_Northwind_Ops/status.md": "in progress\n",
    "sources/old_resume.txt": "old resume text\n",
}


class TestPathSplit(unittest.TestCase):
    def test_personal_paths_are_outside_every_toolkit_path(self):
        for p in u.PERSONAL_PATHS:
            self.assertFalse(u.under(p, u.TOOLKIT_PATHS), p)
        for p in u.TOOLKIT_PATHS:
            self.assertFalse(u.under(p, u.PERSONAL_PATHS), p)

    def test_files_beneath_personal_dirs_are_not_toolkit(self):
        for p in ("Applications/2026-01-02_Co_Role/status.md", "sources/resume.pdf",
                  "Fact_Library.md", "Open_Questions.md"):
            self.assertFalse(u.under(p, u.TOOLKIT_PATHS), p)

    def test_files_beneath_toolkit_dirs_are_toolkit(self):
        for p in ("docs/Writing_Style.md", "scripts/mechanical_checks.py",
                  ".claude/agents/review.md", "CLAUDE.md", "README.md"):
            self.assertTrue(u.under(p, u.TOOLKIT_PATHS), p)

    def test_prefix_is_a_path_component_not_a_string_prefix(self):
        # "docs_private/x" must not count as under "docs".
        self.assertFalse(u.under("docs_private/x.md", ("docs",)))
        self.assertFalse(u.under("Fact_Library.md.bak", ("Fact_Library.md",)))


class TestWhatChanged(unittest.TestCase):
    def test_entries_stop_at_the_next_heading_and_skip_comments(self):
        self.assertEqual(u.what_changed_entries(README_V2), [
            "2026-02-01 - LIBRARY EDIT: the lint now reads a `Tags:` line; add one to every entry.",
            "2026-01-15 - the review checklist gained a section.",
            "2026-01-01 - first entry.",
        ])

    def test_absent_section_is_empty_not_an_error(self):
        self.assertEqual(u.what_changed_entries("# toolkit\n\n## Using it\n- not a change\n"), [])

    def test_new_entries_are_the_after_minus_before_in_after_order(self):
        self.assertEqual(u.new_entries(README_V1, README_V2), [
            "2026-02-01 - LIBRARY EDIT: the lint now reads a `Tags:` line; add one to every entry.",
            "2026-01-15 - the review checklist gained a section.",
        ])
        self.assertEqual(u.new_entries(README_V2, README_V2), [])
        # A copy with no section at all sees every entry as new.
        self.assertEqual(len(u.new_entries("", README_V2)), 3)


class TwoRepos(unittest.TestCase):
    """Upstream at v1 then v2; the copy holds v1 plus personal files and one stray note."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.up = os.path.join(self.td.name, "upstream")
        self.copy = os.path.join(self.td.name, "copy")
        os.makedirs(self.up)
        os.makedirs(self.copy)
        init(self.up)
        for rel, text in TOOLKIT_V1.items():
            write(self.up, rel, text)
        commit_all(self.up, "v1")
        init(self.copy)
        for rel, text in {**TOOLKIT_V1, **PERSONAL}.items():
            write(self.copy, rel, text)
        write(self.copy, "docs/my_notes.md", "a note the user committed under docs/\n")
        commit_all(self.copy, "from template")

    def tearDown(self):
        self.td.cleanup()

    def publish_v2(self, extra=None):
        for rel, text in {**TOOLKIT_V2, **(extra or {})}.items():
            write(self.up, rel, text)
        commit_all(self.up, "v2")

    def run_update(self, **kw):
        out = io.StringIO()
        rc = u.update(self.copy, source=self.up, branch="main", out=out, **kw)
        return rc, out.getvalue()

    def assert_personal_untouched(self):
        for rel, text in PERSONAL.items():
            self.assertEqual(read(self.copy, rel), text, rel)

    def test_update_replaces_toolkit_files_and_nothing_personal(self):
        self.publish_v2()
        rc, out = self.run_update()
        self.assertEqual(rc, 0, out)
        self.assertEqual(read(self.copy, "docs/Review_Checklist.md"), "checklist v2\n")
        self.assertEqual(read(self.copy, "scripts/update_toolkit.py"), "print('new script')\n")
        self.assertEqual(read(self.copy, "README.md"), README_V2)
        self.assert_personal_untouched()
        # The user's stray note under docs/ is kept and named, never deleted.
        self.assertTrue(os.path.exists(os.path.join(self.copy, "docs/my_notes.md")))
        self.assertIn("docs/my_notes.md", out)
        self.assertIn("left in place", out)

    def test_update_stages_the_changes_for_the_commit_row(self):
        self.publish_v2()
        self.run_update()
        staged = sh(self.copy, "diff", "--cached", "--name-only").split()
        self.assertIn("docs/Review_Checklist.md", staged)
        self.assertIn("scripts/update_toolkit.py", staged)
        self.assertNotIn("Fact_Library.md", staged)
        self.assertEqual(sh(self.copy, "status", "--porcelain", "--", "Fact_Library.md",
                            "Applications", "sources"), "")

    def test_report_lists_new_entries_and_flags_library_edits(self):
        self.publish_v2()
        rc, out = self.run_update()
        self.assertIn("the review checklist gained a section", out)
        self.assertIn("LIBRARY EDIT", out)
        self.assertIn("propose it", out)
        self.assertNotIn("first entry", out)  # already in the copy's README

    def test_second_run_is_already_up_to_date(self):
        self.publish_v2()
        self.run_update()
        commit_all(self.copy, "toolkit update")
        rc, out = self.run_update()
        self.assertEqual(rc, 0)
        self.assertIn("Already up to date", out)

    def test_dry_run_writes_nothing(self):
        self.publish_v2()
        rc, out = self.run_update(dry_run=True)
        self.assertEqual(rc, 0, out)
        self.assertIn("Would update", out)
        self.assertIn("docs/Review_Checklist.md", out)
        self.assertIn("the review checklist gained a section", out)
        self.assertEqual(read(self.copy, "docs/Review_Checklist.md"), "checklist v1\n")
        self.assertFalse(os.path.exists(os.path.join(self.copy, "scripts/update_toolkit.py")))
        self.assertEqual(sh(self.copy, "status", "--porcelain"), "")

    def test_uncommitted_toolkit_edit_is_refused_unless_forced(self):
        self.publish_v2()
        write(self.copy, "docs/Review_Checklist.md", "the user edited this\n")
        rc, out = self.run_update()
        self.assertEqual(rc, 2)
        self.assertIn("docs/Review_Checklist.md", out)
        self.assertEqual(read(self.copy, "docs/Review_Checklist.md"), "the user edited this\n")
        rc, out = self.run_update(force=True)
        self.assertEqual(rc, 0, out)
        self.assertEqual(read(self.copy, "docs/Review_Checklist.md"), "checklist v2\n")

    def test_uncommitted_personal_edit_does_not_block(self):
        self.publish_v2()
        write(self.copy, "Fact_Library.md", "my facts, being edited\n")
        rc, out = self.run_update()
        self.assertEqual(rc, 0, out)
        self.assertEqual(read(self.copy, "Fact_Library.md"), "my facts, being edited\n")

    def test_failed_shipped_suite_rolls_back(self):
        self.publish_v2(extra={"scripts/test_update_toolkit.py": FAILING_SUITE})
        rc, out = self.run_update()
        self.assertEqual(rc, 4, out)
        self.assertIn("put back", out)
        self.assertIn("boom", out)
        self.assertEqual(read(self.copy, "docs/Review_Checklist.md"), "checklist v1\n")
        self.assertEqual(read(self.copy, "README.md"), README_V1)
        self.assertFalse(os.path.exists(os.path.join(self.copy, "scripts/update_toolkit.py")))
        self.assertEqual(sh(self.copy, "status", "--porcelain"), "")
        self.assert_personal_untouched()

    def test_failed_fetch_is_exit_3(self):
        rc, out = self.run_update()  # upstream has no v2 yet - but exists
        self.assertEqual(rc, 0)
        out = io.StringIO()
        rc = u.update(self.copy, source=os.path.join(self.td.name, "nowhere"), out=out)
        self.assertEqual(rc, 3)
        self.assertIn("fetch failed", out.getvalue())


class TestRepoRoot(unittest.TestCase):
    def test_outside_a_repository_is_none(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(u.repo_root(td))


if __name__ == "__main__":
    unittest.main(verbosity=1)
