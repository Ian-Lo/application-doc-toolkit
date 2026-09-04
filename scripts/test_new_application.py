#!/usr/bin/env python3
# source-hash: 475284a33980 scripts/test_new_application.py
"""Tests for scripts/new_application.py.

Stdlib unittest, no network, and every test writes into a `tempfile` tree - never the real
Applications/, which this script would otherwise be very easy to pollute with fixture folders.

The properties worth pinning are the naming conventions in `CLAUDE.md`, because they fail
silently: the folder takes a four-digit year and the document a two-digit one, an underscore
inside the role field shifts every filename field after it, and the candidate field is the
one place an underscore is allowed - between the parts of a name.

Every company in these fixtures is invented.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import new_application as n  # noqa: E402

CAND = "Sam_Okafor"


class TestFieldValidation(unittest.TestCase):
    def test_camelcase_is_accepted(self):
        self.assertEqual(n.validate_field("--role", "SeniorDataAnalyst"), "SeniorDataAnalyst")

    def test_digits_are_accepted(self):
        self.assertEqual(n.validate_field("--company", "Acme3"), "Acme3")

    def test_underscore_is_refused(self):
        """The separator inside a field is the failure this validation exists for."""
        with self.assertRaises(ValueError):
            n.validate_field("--role", "Senior_Data_Analyst")

    def test_space_is_refused(self):
        with self.assertRaises(ValueError):
            n.validate_field("--role", "Senior Data Analyst")

    def test_hyphen_is_refused(self):
        with self.assertRaises(ValueError):
            n.validate_field("--company", "North-Wind")

    def test_empty_is_refused(self):
        with self.assertRaises(ValueError):
            n.validate_field("--company", "")

    def test_refusal_names_the_argument(self):
        with self.assertRaises(ValueError) as ctx:
            n.validate_field("--role", "a b")
        self.assertIn("--role", str(ctx.exception))


class TestCandidateValidation(unittest.TestCase):
    def test_candidate_underscore_between_parts_is_accepted(self):
        """The one field where an underscore belongs: it joins the parts of a name."""
        self.assertEqual(n.validate_candidate("Sam_Okafor"), "Sam_Okafor")
        self.assertEqual(n.validate_candidate("Ana_Maria_Costa"), "Ana_Maria_Costa")

    def test_single_part_name_is_accepted(self):
        self.assertEqual(n.validate_candidate("Sam"), "Sam")

    def test_candidate_with_space_is_refused(self):
        with self.assertRaises(ValueError):
            n.validate_candidate("Sam Okafor")

    def test_hyphen_dot_and_edge_underscores_are_refused(self):
        for bad in ("Sam-Okafor", "Sam.Okafor", "_Sam_Okafor", "Sam_Okafor_", "Sam__Okafor"):
            with self.assertRaises(ValueError, msg=bad):
                n.validate_candidate(bad)

    def test_empty_is_refused(self):
        with self.assertRaises(ValueError):
            n.validate_candidate("")


class TestNaming(unittest.TestCase):
    def test_folder_uses_the_four_digit_year(self):
        self.assertEqual(n.folder_name("2026-03-02", "Northwind", "OperationsCoordinator"),
                         "2026-03-02_Northwind_OperationsCoordinator")

    def test_document_uses_the_two_digit_year(self):
        """The two date formats differ, which is the part worth mechanising."""
        self.assertEqual(
            n.doc_name("Resume", "2026-03-02", "Northwind", "OperationsCoordinator", CAND),
            "Sam_Okafor_Resume_260302_Northwind_OperationsCoordinator.md")

    def test_cover_letter_kind(self):
        self.assertEqual(
            n.doc_name("CoverLetter", "2026-03-02", "Acme", "DutyManager", CAND),
            "Sam_Okafor_CoverLetter_260302_Acme_DutyManager.md")

    def test_document_name_matches_the_convention_in_claude_md(self):
        """CLAUDE.md's worked example, reproduced exactly."""
        self.assertEqual(
            n.doc_name("Resume", "2026-03-02", "Northwind", "OperationsCoordinator", CAND),
            "Sam_Okafor_Resume_260302_Northwind_OperationsCoordinator.md")

    def test_document_name_opens_with_the_candidate(self):
        name = n.doc_name("Resume", "2026-03-02", "Acme", "DutyManager", CAND)
        self.assertTrue(name.startswith(CAND + "_"))

    def test_document_name_field_count(self):
        name = n.doc_name("Resume", "2026-03-02", "Acme", "DutyManager", CAND)
        # Sam, Okafor, kind, date, company, role
        self.assertEqual(len(os.path.splitext(name)[0].split("_")), 6)

    def test_document_name_matches_the_lint_pattern(self):
        """The lint finds outgoing documents by *Resume* / *CoverLetter*; keep them findable."""
        import re
        doc_re = re.compile(r".*(Resume|Cover[_ ]?Letter).*\.md$", re.I)
        for kind in ("Resume", "CoverLetter"):
            self.assertRegex(n.doc_name(kind, "2026-03-02", "Acme", "DutyManager", CAND), doc_re)


class TreeCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.apps = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, *parts):
        with open(os.path.join(self.apps, *parts), encoding="utf-8") as fh:
            return fh.read()

    def make(self, company="Acme", abbrev="Acme", role="DutyManager", day="2026-03-02",
             url="https://example.com/jobs/1"):
        return n.scaffold(self.apps, day, company, abbrev, role, url, CAND)


class TestScaffold(TreeCase):
    def test_creates_the_four_convention_files(self):
        rc = self.make()
        self.assertEqual(rc, 0)
        folder = os.path.join(self.apps, "2026-03-02_Acme_DutyManager")
        for name in ("posting.md", "status.md",
                     "Sam_Okafor_Resume_260302_Acme_DutyManager.md",
                     "Sam_Okafor_CoverLetter_260302_Acme_DutyManager.md"):
            self.assertTrue(os.path.isfile(os.path.join(folder, name)), name)

    def test_abbrev_applies_to_documents_only(self):
        self.make(company="AcmeHospitalityGroup", abbrev="Acme")
        folder = os.path.join(self.apps, "2026-03-02_AcmeHospitalityGroup_DutyManager")
        self.assertTrue(os.path.isdir(folder))
        self.assertTrue(os.path.isfile(
            os.path.join(folder, "Sam_Okafor_Resume_260302_Acme_DutyManager.md")))

    def test_documents_are_created_empty(self):
        self.make()
        body = self.read("2026-03-02_Acme_DutyManager",
                         "Sam_Okafor_Resume_260302_Acme_DutyManager.md")
        self.assertEqual(body, "")

    def test_no_decisions_file_or_company_context(self):
        """Both are deliberate omissions, not oversights."""
        self.make()
        folder = os.path.join(self.apps, "2026-03-02_Acme_DutyManager")
        self.assertFalse(os.path.exists(os.path.join(folder, "decisions.md")))
        self.assertFalse(os.path.exists(os.path.join(folder, "Company_Context.md")))

    def test_posting_seed_carries_source_and_verbatim_marker(self):
        self.make(url="https://example.com/jobs/999")
        body = self.read("2026-03-02_Acme_DutyManager", "posting.md")
        self.assertIn("**Source**: https://example.com/jobs/999", body)
        self.assertIn("## Verbatim ad text", body)

    def test_posting_file_is_found_by_the_lint_pattern(self):
        """mechanical_checks.py finds the ad by *posting*.md; the seed must match."""
        import re
        self.make()
        names = os.listdir(os.path.join(self.apps, "2026-03-02_Acme_DutyManager"))
        self.assertTrue(any(re.match(r"posting.*\.md$", x, re.I) for x in names), names)

    def test_status_seed_parses_as_a_status_line(self):
        import re
        self.make()
        body = self.read("2026-03-02_Acme_DutyManager", "status.md")
        self.assertTrue(re.search(r"^-? *\*\*Status[:*]|^- *Status:", body, re.M))

    def test_status_seed_is_short(self):
        """A seed must leave room to write; a status file is not a changelog."""
        self.make()
        body = self.read("2026-03-02_Acme_DutyManager", "status.md")
        self.assertLess(len(body.split()), 150)

    def test_status_seed_points_open_questions_at_the_shared_file(self):
        self.make()
        body = self.read("2026-03-02_Acme_DutyManager", "status.md")
        self.assertIn("Open_Questions.md", body)

    def test_refuses_an_existing_folder(self):
        self.make()
        self.assertEqual(self.make(), 2)


class TestRecs(TreeCase):
    def _with_context(self, folder):
        os.makedirs(os.path.join(self.apps, folder))
        path = os.path.join(self.apps, folder, "Company_Context.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("recon\n")
        return path

    def test_finds_an_existing_company_context(self):
        want = self._with_context("2026-02-01_Acme_OtherRole")
        self.assertEqual(n.existing_company_context(self.apps, "Acme"), want)

    def test_match_is_case_insensitive(self):
        self._with_context("2026-02-01_ACME_OtherRole")
        self.assertTrue(n.existing_company_context(self.apps, "acme"))

    def test_a_different_company_is_not_matched(self):
        self._with_context("2026-02-01_Northwind_OtherRole")
        self.assertEqual(n.existing_company_context(self.apps, "Acme"), "")

    def test_a_symlink_is_not_offered_as_a_link_target(self):
        """One file per company: linking to a link is a chain that breaks twice as easily."""
        real = self._with_context("2026-02-01_Acme_OtherRole")
        os.makedirs(os.path.join(self.apps, "2026-02-02_Acme_ThirdRole"))
        os.symlink("../2026-02-01_Acme_OtherRole/Company_Context.md",
                   os.path.join(self.apps, "2026-02-02_Acme_ThirdRole", "Company_Context.md"))
        self.assertEqual(n.existing_company_context(self.apps, "Acme"), real)

    def test_no_context_anywhere_returns_empty(self):
        self.assertEqual(n.existing_company_context(self.apps, "Acme"), "")


class TestMain(TreeCase):
    def test_bad_role_exits_2(self):
        rc = n.main(["--candidate", CAND, "--company", "Acme", "--role", "Duty Manager",
                     "--apps-dir", self.apps])
        self.assertEqual(rc, 2)

    def test_bad_candidate_exits_2(self):
        rc = n.main(["--candidate", "Sam Okafor", "--company", "Acme", "--role", "DutyManager",
                     "--apps-dir", self.apps])
        self.assertEqual(rc, 2)

    def test_missing_candidate_is_refused(self):
        """No default: a guessed name on an outgoing document is the worst failure here."""
        with self.assertRaises(SystemExit):
            n.main(["--company", "Acme", "--role", "DutyManager", "--apps-dir", self.apps])

    def test_bad_date_exits_2(self):
        rc = n.main(["--candidate", CAND, "--company", "Acme", "--role", "DutyManager",
                     "--date", "02-03-2026", "--apps-dir", self.apps])
        self.assertEqual(rc, 2)

    def test_abbrev_defaults_to_company(self):
        rc = n.main(["--candidate", CAND, "--company", "Acme", "--role", "DutyManager",
                     "--date", "2026-03-02", "--apps-dir", self.apps])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(os.path.join(
            self.apps, "2026-03-02_Acme_DutyManager",
            "Sam_Okafor_Resume_260302_Acme_DutyManager.md")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
