#!/usr/bin/env python3
# source-hash: e6879dc3fd02 scripts/new_application.py
"""Scaffold an Applications/ folder with the convention files and correct document filenames.

`CLAUDE.md`'s "Application file structure" fixes two naming conventions that are easy to get
subtly wrong by hand and invisible when wrong:

    folder     Applications/YYYY-MM-DD_Company_RoleTitle/
    documents  <candidate>_[Resume|CoverLetter]_[YYMMDD]_[Company abbreviated]_[Role].md

Note the two date formats differ - the folder takes the four-digit year, the document a
two-digit one - and the company field is abbreviated in the document name but not always in
the folder. That asymmetry is the part worth mechanising.

THE CANDIDATE FIELD. `--candidate` is the name that opens every document filename, written
as `First_Last` - letters and digits, one underscore between the parts of the name, nothing
else. It is deliberately a required argument with no default: a script that guessed the name
would put a wrong name on a file that is about to be sent to an employer. The agent reads the
value from the `Name for filenames:` line of `Fact_Library.md` and passes it; the user never
types this flag.

WHY THE OTHER FIELDS ARE VALIDATED RATHER THAN NORMALISED. The convention is CamelCase with no
spaces or underscores *inside* the field, because the underscore is the field separator: a
role written `Senior_Data_Analyst` produces a filename with more fields than the readers
expect, and every downstream pattern that splits on `_` then reads the wrong thing as the
company. Silently CamelCasing it would hide a decision the operator should make (is it
`SeniorDataAnalyst` or `SeniorDataAnalystDataMigration`?), so this refuses instead.

WHAT IT DELIBERATELY DOES NOT DO:

  - **No `Company_Context.md`.** Recon writes that file, and `docs/Recon_Checklist.md`'s reuse
    rule requires a judgement this script cannot make: symlink to an existing company context,
    or break the link because the recon has gone stale. It prints the `ln -s` command and stops.
  - **No `decisions.md`.** `CLAUDE.md` says create it once history accumulates. An empty one
    from day zero is a file that reads as "no decisions were made".
  - **No ad capture.** `posting.md` is seeded with its required headers and nothing else.
    Capture is the orchestrator's job and has a rule this script does not carry: the ad's
    own words, verbatim, never a summary (`CLAUDE.md`, "Job posting capture").

The seeded `status.md` carries only the four things that belong in a status file - status
line, gap notes, open items, screening answers - and stays short so there is room to write.

Usage:
    python3 scripts/new_application.py --candidate Sam_Okafor --company Northwind \\
        --role OperationsCoordinator
    python3 scripts/new_application.py --candidate Sam_Okafor --company "AcmeHospitalityGroup" \\
        --abbrev Acme --role DutyManager --date 2026-03-02 --url https://example.com/jobs/123

Exit codes: 0 created, 2 bad arguments or the folder already exists.
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
APPS = os.path.join(ROOT, "Applications")

FIELD_RE = re.compile(r"^[A-Za-z0-9]+$")
# The candidate field may carry underscores BETWEEN name parts (`Sam_Okafor`), because that
# is how the convention writes a multi-part name. Nothing else: no spaces, hyphens, dots, or
# leading/trailing/doubled underscores.
CANDIDATE_RE = re.compile(r"^[A-Za-z0-9]+(_[A-Za-z0-9]+)*$")


def validate_field(name: str, value: str) -> str:
    """Reject anything that would add or blur a filename field separator."""
    if not value:
        raise ValueError("%s is empty" % name)
    if not FIELD_RE.match(value):
        raise ValueError(
            "%s %r must be CamelCase alphanumerics - no spaces, underscores or hyphens. "
            "The underscore is the filename field separator, so one inside a field silently "
            "shifts every field after it." % (name, value))
    return value


def validate_candidate(value: str) -> str:
    """`First_Last`: letters and digits, single underscores between name parts only."""
    if not value:
        raise ValueError("--candidate is empty")
    if not CANDIDATE_RE.match(value):
        raise ValueError(
            "--candidate %r must be the name parts joined by single underscores, e.g. "
            "Sam_Okafor - letters and digits only, no spaces, hyphens or dots. It is the "
            "first field of every document filename." % value)
    return value


def folder_name(day: str, company: str, role: str) -> str:
    return "%s_%s_%s" % (day, company, role)


def doc_name(kind: str, day: str, abbrev: str, role: str, candidate: str) -> str:
    """kind is 'Resume' or 'CoverLetter'. Date is YYMMDD here, not YYYY-MM-DD."""
    short = day[2:].replace("-", "")
    return "%s_%s_%s_%s_%s.md" % (candidate, kind, short, abbrev, role)


def existing_company_context(apps_dir: str, company: str) -> str:
    """A real Company_Context.md for this company elsewhere in the tree, or ''.

    Returns a path to a regular file, never a symlink - linking to a link is a chain that
    breaks twice as easily, and `docs/Recon_Checklist.md` says one file per company.
    """
    needle = company.lower()
    for entry in sorted(os.listdir(apps_dir) if os.path.isdir(apps_dir) else []):
        path = os.path.join(apps_dir, entry)
        if not os.path.isdir(path):
            continue
        parts = entry.split("_")
        if len(parts) >= 2 and parts[1].lower() == needle:
            ctx = os.path.join(path, "Company_Context.md")
            if os.path.isfile(ctx) and not os.path.islink(ctx):
                return ctx
    return ""


POSTING_SEED = """# {company} — {role}

- **Source**: {url}
- **Fetched**: {day}

## Verbatim ad text

<!-- The ad's OWN WORDS, not a summary. A paraphrase manufactures gaps: it preserves the
     topics and discards the vocabulary, and the vocabulary is what the ATS keyword screen
     and the fact-matching step both run on. Paste the whole ad; see CLAUDE.md,
     "Job posting capture". -->

## Screening questions

<!-- Verbatim, if the ad or the form carries any. -->
"""

STATUS_SEED = """# Application Status — {company}, {role}
<!-- meta: stage=scaffolded -->

**Status**: Scaffolded {day} — ad not yet captured, not yet drafted.

## Gaps to weigh before submitting

1. Not yet assessed.

## Open items

Nothing yet. Application-specific mechanics belong here; a question about the candidate's
own experience goes to `Open_Questions.md` at the project root and is referenced here by
its Q-number.

## Screening answers submitted

None yet.
"""


def scaffold(apps_dir: str, day: str, company: str, abbrev: str, role: str,
             url: str, candidate: str) -> int:
    folder = folder_name(day, company, role)
    dest = os.path.join(apps_dir, folder)
    if os.path.exists(dest):
        sys.stderr.write("already exists: %s\n" % os.path.relpath(dest, ROOT))
        return 2

    os.makedirs(dest)
    written = []
    for name, body in (
        ("posting.md", POSTING_SEED.format(company=company, role=role, url=url, day=day)),
        ("status.md", STATUS_SEED.format(company=company, role=role, day=day)),
    ):
        path = os.path.join(dest, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        written.append(name)
    for kind in ("Resume", "CoverLetter"):
        name = doc_name(kind, day, abbrev, role, candidate)
        path = os.path.join(dest, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("")
        written.append(name)

    print("CREATED  Applications/%s" % folder)
    for name in written:
        print("    %s" % name)

    ctx = existing_company_context(apps_dir, company)
    if ctx:
        rel = os.path.relpath(ctx, dest)
        print("\nRECON ALREADY EXISTS for %s:\n    %s" % (company, os.path.relpath(ctx, ROOT)))
        print("Link it rather than re-researching, per docs/Recon_Checklist.md's reuse rule:")
        print("    ln -s %s %s" % (rel, os.path.join("Applications", folder,
                                                     "Company_Context.md")))
        print("Only copy instead of linking if that recon has genuinely gone stale, and say "
              "why in status.md.")
    else:
        print("\nNo existing Company_Context.md for %s — recon runs fresh." % company)

    print("\nNext: paste the ad verbatim into posting.md (CLAUDE.md, \"Job posting capture\"), "
          "then recon, then drafting.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--candidate", required=True,
                    help="the candidate's name as it opens every document filename, "
                         "e.g. Sam_Okafor - read from Fact_Library.md's 'Name for filenames:' line")
    ap.add_argument("--company", required=True,
                    help="company as it appears in the FOLDER name, CamelCase")
    ap.add_argument("--role", required=True, help="role title, CamelCase, no spaces")
    ap.add_argument("--abbrev", default=None,
                    help="company as it appears in the DOCUMENT names; defaults to --company")
    ap.add_argument("--url", default="TODO — the ad's source URL")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to today")
    ap.add_argument("--apps-dir", default=APPS)
    args = ap.parse_args(argv)

    day = args.date or datetime.date.today().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", day):
        sys.stderr.write("--date must be YYYY-MM-DD, got %r\n" % day)
        return 2
    try:
        candidate = validate_candidate(args.candidate)
        company = validate_field("--company", args.company)
        role = validate_field("--role", args.role)
        abbrev = validate_field("--abbrev", args.abbrev or company)
    except ValueError as exc:
        sys.stderr.write("%s\n" % exc)
        return 2
    return scaffold(args.apps_dir, day, company, abbrev, role, args.url, candidate)


if __name__ == "__main__":
    sys.exit(main())
