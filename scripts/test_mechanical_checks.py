#!/usr/bin/env python3
# source-hash: 7643c21fe4f4 scripts/test_mechanical_checks.py
"""Tests for banned_patterns.txt and mechanical_checks.py.

    python3 test_mechanical_checks.py

The load-bearing test is test_every_regex_has_a_probe. A regex added to
banned_patterns.txt without a probe below FAILS THIS SUITE BY DESIGN. That convention is
the only reason a pattern file stays trustworthy as it grows.

The reason it matters is on the record of the project this toolkit comes from. Its
most-used pattern travelled between reviewers unanchored, matching 492 lines of which 448
were substrings - 266 of them the word "univerSITy". Nobody probed it, so nobody noticed
until the noise had already produced a review tally recorded as clean that was not. Every
NEGATIVE probe below is a false positive somebody would otherwise have had to read.
"""

import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
BANNED = os.path.join(HERE, "banned_patterns.txt")
CHECKS = os.path.join(HERE, "mechanical_checks.py")

sys.path.insert(0, HERE)
import mechanical_checks as mc  # noqa: E402

# raw pattern -> (must match, must NOT match)
PROBES = {
    # --- tic ---
    r"\b(sit|sits|sitting|sat)\b": (
        ["the layer sits underneath", "sitting behind it", "sat inside the team",
         "a tool that sits alongside", "where the role sits in the org"],
        ["university of sydney", "the position was", "data visualisation",
         "optimisation work", "sensitive data", "the site was", "repositories"],
    ),
    r"\bthis role (asks for|needs|runs on|is about)\b": (
        ["the discipline this role runs on", "the coordination this role needs",
         "what this role asks for", "the work this role is about"],
        ["this roles needs", "the role needs a writer", "this role, needs"],
    ),
    "the closest thing on my record to": (
        ["the closest thing on my record to a formal writing sample"],
        ["the closest match on my record"],
    ),
    r"\bsign-?off\b": (
        ["procurement sign-off", "went to signoff", "sign-off was granted"],
        ["signed off on it", "signing the contract", "design office"],
    ),
    # --- tell ---
    "I'm writing to apply": (["I'm writing to apply for the role"], ["I am applying for"]),
    "I would welcome the opportunity": (["I would welcome the opportunity to talk"], ["I welcome feedback"]),
    "I'd welcome the opportunity": (["I'd welcome the opportunity to talk"], ["I welcome feedback"]),
    "thank you for considering": (["thank you for considering my application"], ["thanks for reading"]),
    "opportunity to discuss": (["an opportunity to discuss the role"], ["a chance to talk it through"]),
    "I recognise that": (["I recognise that the ad asks for"], ["I recognise the pattern"]),
    r"\bleverag(e|es|ed|ing)\b": (
        # a bare-substring version MISSES "leveraging" and MATCHES "deleverage";
        # both are fixed by this pattern and both are probed here.
        ["we leverage the platform", "leveraged the platform", "leveraging it", "it leverages"],
        ["deleverage the balance sheet", "leverageable"],
    ),
    r"\bseamless(ly)?\b": (["seamless integration", "seamlessly integrated"], ["seamlessness of it"]),
    r"\brobust(ly|ness)?\b": (["a robust pipeline", "robustly tested", "robustness matters"], ["robusta coffee"]),
    r"\brigorous(ly)?\b": (["rigorous testing", "rigorously tested"], ["rigour matters"]),
    r"\bspearhead(s|ed|ing)?\b": (
        ["spearhead the work", "spearheaded the work", "spearheading it", "she spearheads it"],
        ["spearfishing trip", "the spear was headed north"],
    ),
    r"\bgenuine(ly)?\b": (
        ["a genuine interest in the sector", "genuinely want to be adjacent to it",
         "a genuine constraint"],
        # "genuineness" and "ingenuity" both fail \b on the trailing / leading side.
        # The selfdq pattern "genuine gap, stated plainly" has "a genuine gap in the
        # record" as ITS negative; probes are per-pattern, so this one matching that
        # string is correct and intended - the bare intensifier is the thing flagged.
        ["genuineness of the claim", "ingenuity under pressure"],
    ),
    # --- selfdq --- each one withdraws the application
    r"isn't the right (match|fit|hire)": (["if that isn't the right fit"], ["it is the right fit"]),
    r"is not the right (match|fit|hire)": (["this is not the right match"], ["this is the right match"]),
    r"if .{0,60}(hard requirement|non-negotiable|deal-?breaker)": (
        ["if the certificate is a hard requirement", "if that is a dealbreaker for you"],
        ["a hard requirement is listed"],
    ),
    r"you (may|might|would) prefer": (["you may prefer a candidate with"], ["you prefer clarity"]),
    r"may prefer someone": (["you may prefer someone with more"], ["prefers someone senior"]),
    r"understand if this": (["I understand if this rules me out"], ["I understand this role"]),
    r"rules me out": (["if that rules me out"], ["the rule is out of date"]),
    r"counts me out": (["if that counts me out"], ["the count is out"]),
    # The regex only catches the unhedged phrasing: "may not be the candidate" is hedged
    # and deliberately not matched.
    r"not the candidate": (["I am not the candidate you need"], ["another candidate"]),
    r"waste anyone's": (["I won't waste anyone's time"], ["a waste of effort"]),
    r"waste your time": (["rather than waste your time"], ["a waste of effort"]),
    r"rather say (so|that) (now|plainly)": (["I would rather say so now"], ["I would rather say nothing"]),
    r"stating that plainly": (["stating that plainly upfront"], ["stated plainly in the resume"]),
    r"saying that upfront": (["saying that upfront matters"], ["said upfront"]),
    r"rather than dressing it up": (["rather than dressing it up"], ["dressed up language"]),
    r"genuine gap, stated plainly": (["a genuine gap, stated plainly"], ["a genuine gap in the record"]),
    r"competence I haven't earned": (["claiming competence I haven't earned"], ["competence I have earned"]),
    r"before we go further": (["before we go further, one gap"], ["we went further"]),
}


class TestPatternFile(unittest.TestCase):
    def setUp(self):
        self.cats = mc.load_categories(BANNED)
        self.all = [p for pats in self.cats.values() for p in pats]

    def test_file_parses_into_all_three_categories(self):
        for cat in mc.CATEGORIES:
            self.assertTrue(self.cats[cat], "category %r parsed to zero patterns" % cat)

    def test_every_regex_has_a_probe(self):
        """The load-bearing test. Add a pattern, add a probe, or this fails."""
        missing = [p.raw.replace("re:", "", 1) for p in self.all
                   if p.raw.replace("re:", "", 1) not in PROBES]
        self.assertEqual(missing, [], "patterns with no probe in PROBES: %r" % missing)

    def test_probes_are_not_stale(self):
        """A probe for a pattern no longer in the file is dead weight - remove it."""
        live = {p.raw.replace("re:", "", 1) for p in self.all}
        stale = sorted(set(PROBES) - live)
        self.assertEqual(stale, [], "probes for patterns not in the file: %r" % stale)

    def test_positive_probes_match(self):
        for raw, (positives, _neg) in PROBES.items():
            rx = re.compile(raw, re.I)
            for s in positives:
                self.assertTrue(rx.search(s), "pattern %r should match %r" % (raw, s))

    def test_negative_probes_do_not_match(self):
        for raw, (_pos, negatives) in PROBES.items():
            rx = re.compile(raw, re.I)
            for s in negatives:
                self.assertFalse(rx.search(s), "pattern %r must NOT match %r" % (raw, s))

    def test_every_pattern_is_anchored_or_multiword(self):
        """A short single-word pattern with no \\b is the univerSITy defect. Block it."""
        for p in self.all:
            body = p.raw.replace("re:", "", 1)
            if " " in body or "\\b" in body or len(body) > 24:
                continue
            self.fail("pattern %r is short, single-word and unanchored - add \\b" % body)


class TestSitFamilyRegression(unittest.TestCase):
    """The specific defect this whole suite exists for, pinned as a test."""

    SIT = r"\b(sit|sits|sitting|sat)\b"

    def test_anchored_alternation_beats_both_predecessors(self):
        corpus = ("the university of sydney ran a data visualisation optimisation "
                  "position review; the layer sits underneath, sitting behind it, sat inside")
        narrow = len(re.findall(r"\bsits?\b", corpus, re.I))
        unanchored = len(re.findall(r"sit|sits|sitting|sat", corpus, re.I))
        anchored = len(re.findall(self.SIT, corpus, re.I))
        self.assertEqual(anchored, 3, "should find sits/sitting/sat and nothing else")
        self.assertLess(narrow, anchored, "the narrow fix misses sitting/sat")
        self.assertGreater(unanchored, anchored, "the unanchored version matches substrings")

    def test_university_is_not_a_hit(self):
        self.assertIsNone(re.search(self.SIT, "University of Sydney", re.I))


class TestWrappedPhraseRegression(unittest.TestCase):
    """A live self-disqualifying sentence once wrapped mid-phrase and the per-line scan
    passed it; a reading reviewer caught it, and a wrap-aware rescan found three more
    evading identically. hits_in now scans an unwrapped paragraph view as well."""

    def setUp(self):
        self.cats = mc.load_categories(BANNED)

    def test_wrapped_selfdq_is_caught(self):
        text = ("A paragraph that starts safely; if the\n"
                "background requirement is non-negotiable, that's a fair call.\n")
        hits = mc.hits_in(text, self.cats["selfdq"])
        self.assertTrue(any(line.startswith("(wrapped)") for _, _, line in hits), hits)

    def test_single_line_hit_is_not_double_reported(self):
        text = "One line: if that is a deal-breaker for you, fine.\n"
        hits = mc.hits_in(text, self.cats["selfdq"])
        self.assertEqual(len(hits), 1, hits)

    def test_bullet_continuation_wrap_is_caught(self):
        text = ("- A bullet whose sentence wraps; if the\n"
                "  clearance is non-negotiable, noted.\n")
        hits = mc.hits_in(text, self.cats["selfdq"])
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("(wrapped)", hits[0][2])

    def test_phrases_do_not_join_across_blank_lines(self):
        text = "This mentions if the\n\nnon-negotiable point separately.\n"
        self.assertEqual(mc.hits_in(text, self.cats["selfdq"]), [])


class TestSectionBlocksProseRegression(unittest.TestCase):
    """A skills block written as middle-dot-separated prose (no bullet lines) once
    recorded zero items and was silently skipped by the header-vs-block check - in the
    one section that check pays off on most. Pin the fix."""

    def test_middle_dot_prose_block_is_split_into_items(self):
        text = (
            "## Core Skills\n\n"
            "Data warehousing & ETL (Spark) · Data visualisation (Tableau) · "
            "Advanced Excel\n\n"
            "## Next Section\n\nignored\n"
        )
        blocks = dict(mc.section_blocks(text))
        self.assertIn("Core Skills", blocks)
        self.assertEqual(len(blocks["Core Skills"]), 3)
        self.assertIn("Data warehousing & ETL (Spark)", blocks["Core Skills"])

    def test_plain_paragraph_block_is_not_skipped(self):
        text = "## Professional Summary\n\nData analyst with a Master of Engineering.\n\n## Next\n\nignored\n"
        blocks = dict(mc.section_blocks(text))
        self.assertIn("Professional Summary", blocks)
        self.assertEqual(blocks["Professional Summary"],
                         ["Data analyst with a Master of Engineering."])

    def test_bullet_continuation_lines_still_ignored(self):
        text = (
            "## Selected Analysis\n\n"
            "Intro paragraph before the bullets.\n\n"
            "- First item wraps\n  onto a continuation line that must not become its own item.\n"
            "- Second item\n"
            "## Next\n\nignored\n"
        )
        items = dict(mc.section_blocks(text))["Selected Analysis"]
        self.assertEqual(items, [
            "Intro paragraph before the bullets.",
            "First item wraps",
            "Second item",
        ])

    def test_header_with_no_content_still_skipped_by_report(self):
        text = "## Professional Experience\n\n### Role One\n\n- a bullet\n"
        blocks = dict(mc.section_blocks(text))
        self.assertEqual(blocks["Professional Experience"], [])


class TestScriptRuns(unittest.TestCase):
    """End-to-end runs against a throwaway fixture application."""

    RESUME = (
        "# Jane Doe\n\n## Summary\n\nTwo years of data work.\n\n"
        "## Experience\n\n- Built reporting pipelines (Jan 2020 – Jun 2022).\n"
    )
    LETTER = (
        "Jane Doe\\\nSpringfield\\\n555-0100 | jane@example.com\n\nAcme Pty Ltd\n\n"
        "Re: Data Analyst\n\nDear Hiring Manager,\n\nMy background is in reporting.\n\n"
        "Regards,\\\nJane Doe\n"
    )

    def _fixture(self, td):
        app = os.path.join(td, "2026-01-01_Acme_DataAnalyst")
        os.makedirs(app)
        with open(os.path.join(app, "Jane_Doe_Resume_260101_Acme.md"), "w") as fh:
            fh.write(self.RESUME)
        with open(os.path.join(app, "Jane_Doe_CoverLetter_260101_Acme.md"), "w") as fh:
            fh.write(self.LETTER)
        return app

    def test_single_application_exits_clean(self):
        with tempfile.TemporaryDirectory() as td:
            app = self._fixture(td)
            r = subprocess.run([sys.executable, CHECKS, app],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            for section in ("BANNED STRINGS", "ATOMICITY", "DURATIONS", "SECTION HEADERS"):
                self.assertIn(section, r.stdout)

    def test_corpus_sweep_exits_clean(self):
        with tempfile.TemporaryDirectory() as td:
            self._fixture(td)
            r = subprocess.run([sys.executable, CHECKS, "--corpus", td],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("CORPUS SWEEP", r.stdout)

    def test_missing_pattern_file_is_fatal_not_silent(self):
        """A missing pattern file must stop the run, never pass as 'clean'."""
        r = subprocess.run([sys.executable, "-c",
                            "import sys; sys.path.insert(0, %r);"
                            "import mechanical_checks as mc;"
                            "mc.load_categories('/nonexistent/banned_patterns.txt')" % HERE],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("FATAL", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
