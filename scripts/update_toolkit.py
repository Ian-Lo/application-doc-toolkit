#!/usr/bin/env python3
# source-hash: original
"""Bring the toolkit files in a private copy up to date with the public repository.

    python3 scripts/update_toolkit.py            # fetch, replace, test, report
    python3 scripts/update_toolkit.py --dry-run  # fetch and report; write nothing

A private copy made with GitHub's *Use this template* has no link back to the repository it
came from: no fork relationship, no *Sync fork* button, no shared commit. A change published
to the toolkit therefore never reaches the copy on its own. This script is the link. It
fetches the public repository's `main` branch and replaces the toolkit's own files with the
fetched versions, wholesale, then runs the shipped test suites and reports what changed.

The path split is the whole design, and it lives here as code rather than in prose so that
a test can hold it:

    TOOLKIT_PATHS   replaced on every update. The user is not meant to edit these; an edit
                    they made is overwritten (it stays in git history, it is not gone).
    PERSONAL_PATHS  never read, never written: the fact library, the open questions, the
                    applications and the source documents.

Only files that the fetched tree contains are written. A file tracked in the copy under a
toolkit path but absent upstream is left where it is and named in the report - the update
never deletes anything, even a stale toolkit file, because a user file committed in the
wrong place would be indistinguishable from one. Nothing outside the two lists is touched.

Why replace-from-FETCH_HEAD rather than merge: the two repositories share no commit, so a
merge or rebase has nothing to work from; `git restore --source=FETCH_HEAD` needs only the
fetched tree and works regardless of history.

The report ends with the public README's *What changed* entries that the copy did not have
before the update - one line per published change, newest first. An entry carrying the
token `LIBRARY EDIT:` describes a change the user's own `Fact_Library.md` needs (for
example a header the lint now reads); the orchestrator proposes that edit and never makes
it silently.

Exit codes: 0 updated, or already current; 2 not inside a git repository, or uncommitted
changes under a toolkit path (commit them, or pass --force to overwrite them); 3 the fetch
failed; 4 a shipped test suite failed after the update, and the toolkit files were put back.
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys

SOURCE_URL = "https://github.com/Ian-Lo/application-doc-toolkit"
SOURCE_BRANCH = "main"

# Repository-relative. A directory entry covers everything beneath it.
TOOLKIT_PATHS = (
    "CLAUDE.md",
    "README.md",
    "LICENSE",
    ".gitignore",
    ".claude",
    "docs",
    "scripts",
    "Fact_Library_TEMPLATE.md",
    "Open_Questions_TEMPLATE.md",
)
PERSONAL_PATHS = (
    "Fact_Library.md",
    "Open_Questions.md",
    "Applications",
    "sources",
)

WHAT_CHANGED_HEADING = "## What changed"
LIBRARY_EDIT_TOKEN = "LIBRARY EDIT:"


def under(path: str, roots) -> bool:
    """True when `path` is one of `roots` or lies beneath a directory in it."""
    return any(path == r or path.startswith(r + "/") for r in roots)


def git(root: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True,
                          check=check)


def repo_root(start: str = ".") -> str | None:
    try:
        cp = git(os.path.abspath(start), "rev-parse", "--show-toplevel")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return cp.stdout.strip()


def tracked_files(root: str, rev: str) -> list:
    """Files in `rev` that fall under TOOLKIT_PATHS. `rev` is a commit; nothing here reads
    the working tree, so an uncommitted user edit cannot leak into the list."""
    cp = git(root, "ls-tree", "-r", "--name-only", rev)
    return sorted(p for p in cp.stdout.splitlines() if p and under(p, TOOLKIT_PATHS))


def dirty_toolkit_files(root: str) -> list:
    """Tracked files under a toolkit path with uncommitted changes. Untracked files are not
    counted: the update never writes a path the fetched tree does not name."""
    paths = [p for p in TOOLKIT_PATHS if os.path.lexists(os.path.join(root, p))]
    if not paths:
        return []
    cp = git(root, "status", "--porcelain", "--untracked-files=no", "--", *paths)
    return sorted(line[3:] for line in cp.stdout.splitlines() if line.strip())


def what_changed_entries(text: str) -> list:
    """The bullet lines of the README's *What changed* section, in file order. Returns []
    when the section is absent - an older README is not an error."""
    entries, inside = [], False
    for line in text.splitlines():
        if line.strip() == WHAT_CHANGED_HEADING:
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside and line.startswith("- "):
            entries.append(line[2:].strip())
    return entries


def new_entries(before: str, after: str) -> list:
    """Entries in `after` that `before` lacks - i.e. everything published since the copy
    was last updated, as long as every update commits the README (it does)."""
    seen = set(what_changed_entries(before))
    return [e for e in what_changed_entries(after) if e not in seen]


def show(root: str, rev: str, path: str) -> str:
    cp = git(root, "show", "%s:%s" % (rev, path), check=False)
    return cp.stdout if cp.returncode == 0 else ""


def run_suites(root: str) -> list:
    """Run every scripts/test_*.py in the (updated) tree. Returns [(name, rc, tail)]."""
    results = []
    for path in sorted(glob.glob(os.path.join(root, "scripts", "test_*.py"))):
        cp = subprocess.run([sys.executable, path], cwd=root, text=True, capture_output=True)
        tail = "\n".join((cp.stdout + cp.stderr).splitlines()[-15:])
        results.append((os.path.relpath(path, root), cp.returncode, tail))
    return results


def apply(root: str, incoming: list) -> None:
    """Write the fetched versions of `incoming` into the index and working tree. Explicit
    file paths only - a directory pathspec would make git delete tracked files that the
    source lacks, which is the one thing this script must never do."""
    if incoming:
        git(root, "restore", "--source=FETCH_HEAD", "--staged", "--worktree", "--", *incoming)


def rollback(root: str, present: list, incoming: list) -> None:
    """Undo apply(): HEAD's versions back for what HEAD had, and remove what arrived new."""
    had = [p for p in incoming if p in set(present)]
    new = [p for p in incoming if p not in set(present)]
    if had:
        git(root, "restore", "--source=HEAD", "--staged", "--worktree", "--", *had)
    if new:
        git(root, "rm", "-q", "--force", "--", *new)


def update(root: str, source: str = SOURCE_URL, branch: str = SOURCE_BRANCH,
           dry_run: bool = False, force: bool = False, out=sys.stdout) -> int:
    say = lambda *a: print(*a, file=out)  # noqa: E731

    dirty = dirty_toolkit_files(root)
    if dirty and not force:
        say("Uncommitted changes under toolkit paths; commit them first, or pass --force "
            "to overwrite them:")
        for p in dirty:
            say("    %s" % p)
        return 2

    try:
        git(root, "fetch", "--quiet", source, branch)
    except subprocess.CalledProcessError as exc:
        say("fetch failed: %s %s\n%s" % (source, branch, exc.stderr.strip()))
        return 3
    fetched = git(root, "rev-parse", "--short", "FETCH_HEAD").stdout.strip()

    present = tracked_files(root, "HEAD")
    incoming = tracked_files(root, "FETCH_HEAD")
    orphans = sorted(set(present) - set(incoming))
    diff = git(root, "diff", "--stat", "HEAD", "FETCH_HEAD", "--", *incoming).stdout.rstrip()
    fresh = new_entries(show(root, "HEAD", "README.md"), show(root, "FETCH_HEAD", "README.md"))

    if not diff:
        say("Already up to date with %s at %s." % (source, fetched))
        return 0

    say("%s %s at %s" % ("Would update from" if dry_run else "Updating from", source, fetched))
    say("Toolkit files that change:")
    say(diff)
    if orphans:
        say("Tracked under a toolkit path here but not in the toolkit - left in place:")
        for p in orphans:
            say("    %s" % p)

    if not dry_run:
        apply(root, incoming)
        results = run_suites(root)
        failed = [(n, rc, t) for n, rc, t in results if rc != 0]
        if failed:
            rollback(root, present, incoming)
            say("A shipped test suite failed after the update; the toolkit files were put "
                "back as they were. Report this to the toolkit's author.")
            for name, rc, tail in failed:
                say("  %s (exit %d)\n%s" % (name, rc, tail))
            return 4
        say("Shipped test suites: %s" % ", ".join("%s ok" % n for n, _, _ in results))

    say("What changed, newest first (from README.md):" if fresh
        else "README.md has no new *What changed* entries.")
    for e in fresh:
        flag = "  [needs a Fact_Library.md change - propose it, do not make it silently]" \
            if LIBRARY_EDIT_TOKEN in e else ""
        say("  - %s%s" % (e, flag))
    if not dry_run:
        say("The changes are staged. Personal files were not touched: %s."
            % ", ".join(PERSONAL_PATHS))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="fetch and report; write nothing")
    ap.add_argument("--force", action="store_true",
                    help="overwrite uncommitted edits under toolkit paths")
    ap.add_argument("--source", default=SOURCE_URL, help="repository URL (default: the toolkit)")
    ap.add_argument("--branch", default=SOURCE_BRANCH)
    args = ap.parse_args(argv)

    root = repo_root()
    if not root:
        print("Not inside a git repository.", file=sys.stderr)
        return 2
    return update(root, args.source, args.branch, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
