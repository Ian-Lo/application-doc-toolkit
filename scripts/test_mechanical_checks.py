#!/usr/bin/env python3
# source-hash: fa5b664a9a38 scripts/test_mechanical_checks.py
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

import contextlib
import hashlib
import io
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
    r"\b(your ad|the ad|this role|this posting)\b[a-z' ]{0,15}\b(asks?|is asking|needs|wants) for someone": (
        ["your ad asks for someone who", "the ad is asking for someone with",
         "this posting wants for someone", "this role needs for someone able to"],
        ["your advice asks for clarity", "the address needs someone to confirm it",
         "this role is demanding but rewarding"],
    ),
    r"\b(asks?|is asking|wants) for someone who\b": (
        ["asks for someone who can", "is asking for someone who has",
         "wants for someone who understands"],
        ["asks for clarification on the role", "wants someone with the right background"],
    ),
    r"\ba role like this one\b": (
        ["a role like this one rewards", "in a role like this one"],
        ["a role unlike anything I've held", "this one role stood out"],
    ),
    r"\bthe same\b[^.]{0,40}\byour\b": (
        # The four nouns an earlier, narrower alternation named, all still caught...
        ["the same discipline your external-worker provisioning work needs",
         "the same rhythm your team's release cycle runs on",
         "the same shape your audit process takes",
         "the same instinct your escalation path relies on",
         # ...plus the live instance the narrower alternation MISSED: it was caught only
         # because `(your|this) ad` happened to fire on the same sentence, and a version
         # grading against something the ad merely implied would have escaped.
         "the same willingness to learn and develop your ad asks for"],
        # The formula is specifically the second-person comparison. "the same X" on its own,
        # or attached to a third-party noun rather than "your", must not trip - and neither
        # must a "your" that lands beyond the 40-character proximity window.
        ["the same discipline I brought to the platform migration",
         "the same rhythm as the previous engagement", "a similar discipline to theirs",
         "the same team, and after a long paragraph of quite unrelated intervening prose,"
         " your name came up"],
    ),
    r"\banswers?\b[^.]{0,20}\bthe ad's\b": (
        ["answer the ad's interest in high-throughput processing directly",
         "answers the ad's non-functional-testing bar"],
        ["answers a genuine question", "the ad's own wording is direct",
         "answer to the selection criteria"],
    ),
    r"\b(your|this) ad\b": (
        ["your ad names Procurement directly", "this ad's essential-experience list",
         "in your ad", "reading this ad closely"],
        ["your advice was useful", "this address is current", "your address book"],
    ),
    "the closest thing on my record to": (
        ["the closest thing on my record to a formal writing sample"],
        ["the closest match on my record"],
    ),
    r"\bsign-?off\b": (
        ["procurement sign-off", "went to signoff", "sign-off was granted"],
        ["signed off on it", "signing the contract", "design office"],
    ),
    r"\b(dated|sourced)[a-z, ]{0,20}\bdetail behind\b": (
        # The three variants measured across one pass, plus the retired style-guide
        # prescription that seeded all of them.
        ["The dated detail behind every claim above",
         "the dated, sourced detail behind every line above",
         "the dated, sourced detail behind those paragraphs"],
        # "detail behind" on its own is ordinary English and must not trip; nor may either
        # adjective when it is not attached to that noun phrase.
        ["the detail behind the number", "sourced from the vendor's own figures",
         "a dated reference in the appendix",
         "dated, sourced, and checked against the transcript"],
    ),
    r"\b(detail|record|evidence|backing|substance|version)\b[a-z, ]{0,15}\bbehind (each|every|those)\b": (
        # The two measured evasions of the narrower pattern above, plus the retired stem itself.
        ["the fuller record behind each claim above",
         "the dated, sourced detail behind every claim above",
         "the evidence behind those paragraphs"],
        # "behind" without the frame, and the frame without a definite quantifier, must not trip.
        ["the record behind the decision", "the story behind every claim",
         "the reasoning behind each recommendation", "left the paperwork behind"],
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


class TestBodyVsCompression(unittest.TestCase):
    """BODY vs COMPRESSION: a summary sentence, a Core Skills entry or a letter's topic
    sentence often generalises over an experience bullet in words that assert something
    different from it - every fact underneath licensed, the generalisation over them not.

    It is a PAIRING PRINTER, not a pass/fail test: the premise is that the words changed, so
    the tests assert what gets PRINTED, never a verdict.
    """

    EXPERIENCE = (
        "## Experience\n\n"
        "### Acme Print Co - Solutions Architect (2007 - 2012)\n\n"
        "- Designed managed print solutions for enterprise accounts, sizing device fleets\n"
        "  against measured page volumes.\n"
        "- Relocated a Meridian service bureau from Springfield to Shelbyville, rebuilding\n"
        "  the server and network estate in the destination datacentre.\n"
    )

    def setUp(self):
        self.stopwords, _phrases = mc.load_stoplist(mc.STOPLIST)

    def pairs(self, resume, letter=""):
        return mc.compression_pairs(resume, letter, self.stopwords)

    def test_a_pair_whose_nouns_changed_is_printed_with_both_word_sets(self):
        """Every fact underneath was licensed; the noun swap was not."""
        resume = (
            "## Core Skills\n\n"
            "- Enterprise document services and device fleet sizing for enterprise accounts\n\n"
            + self.EXPERIENCE
        )
        rows, _clean, _unpaired = self.pairs(resume)
        self.assertEqual(len(rows), 1, rows)
        label, line, bullet, only_line, only_bullet = rows[0]
        self.assertEqual(label, "Core Skills")
        self.assertIn("Enterprise document services", line)
        self.assertIn("managed print", bullet)
        self.assertIn("document", only_line)
        self.assertIn("print", only_bullet)

    def test_a_geography_swap_is_printed(self):
        """The second measured shape: a correct-looking line naming the wrong axis."""
        resume = (
            "## Core Skills\n\n"
            "- Datacentre relocation for a Meridian service bureau, production to DR\n\n"
            + self.EXPERIENCE
        )
        rows, _clean, _unpaired = self.pairs(resume)
        self.assertEqual(len(rows), 1, rows)
        _label, _line, bullet, only_line, only_bullet = rows[0]
        self.assertIn("Springfield to Shelbyville", bullet)
        self.assertIn("production", only_line)
        self.assertIn("springfield", only_bullet)
        self.assertIn("shelbyville", only_bullet)

    def test_a_faithful_pair_is_not_printed_but_is_counted_clean(self):
        """Output size is a hard constraint: a faithful pair costs one shared line, not five."""
        resume = (
            "## Core Skills\n\n"
            "- Designed managed print solutions for enterprise accounts, sizing device fleets\n\n"
            + self.EXPERIENCE
        )
        rows, clean, _unpaired = self.pairs(resume)
        self.assertEqual(rows, [])
        self.assertEqual(clean, 1)

    def test_a_derived_line_with_no_plausible_bullet_is_left_unpaired(self):
        """Guessing a pair trains the ignore habit. An unsupported claim is a different
        finding and this section must not invent one."""
        resume = (
            "## Core Skills\n\n"
            "- Actuarial reserving, mortality modelling and Solvency II capital reporting\n\n"
            + self.EXPERIENCE
        )
        rows, clean, unpaired = self.pairs(resume)
        self.assertEqual(rows, [])
        self.assertEqual(clean, 0)
        self.assertEqual(unpaired, 1)

    def render(self, resume):
        """The printed BODY vs COMPRESSION section for a resume, via the real report."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "Jane_Doe_Resume_260101_Acme_Role.md"), "w",
                      encoding="utf-8") as fh:
                fh.write(resume)
            r = subprocess.run([sys.executable, CHECKS, tmp],
                               capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        body = r.stdout.split("BODY vs COMPRESSION", 1)[1]
        return body.split("\nAD VOCABULARY", 1)[0]

    def test_the_cap_holds_and_the_overflow_is_announced(self):
        """PAIR_CAP. The whole report is pasted into every subagent brief."""
        skills = "".join(
            "- Enterprise document service %d and device fleet sizing for enterprise accounts\n"
            % i for i in range(mc.PAIR_CAP + 4))
        resume = "## Core Skills\n\n" + skills + "\n" + self.EXPERIENCE
        rows, _clean, _unpaired = self.pairs(resume)
        self.assertGreater(len(rows), mc.PAIR_CAP)
        out = self.render(resume)
        printed = [l for l in out.splitlines() if l.startswith("      line ")]
        self.assertEqual(len(printed), mc.PAIR_CAP)
        self.assertIn("more differing pair(s) not shown", out)

    def test_a_letter_topic_sentence_is_paired_against_resume_bullets(self):
        """Both directions: sometimes the letter is right and the resume wrong, sometimes
        the reverse - so the letter's topic sentences are derived lines too."""
        resume = "## Core Skills\n\n- Unrelated skill entry about nothing at all\n\n" + self.EXPERIENCE
        letter = ("Enterprise document services ran through the Acme years, sizing device\n"
                  "fleets for enterprise accounts. A second sentence that must be ignored.\n")
        rows, _clean, _unpaired = self.pairs(resume, letter)
        labels = [r[0] for r in rows]
        self.assertIn("Letter topic sentence", labels)
        row = rows[labels.index("Letter topic sentence")]
        self.assertTrue(row[1].startswith("Enterprise document services"), row[1])
        self.assertNotIn("second sentence", row[1])

    def test_only_the_first_sentence_of_a_letter_paragraph_is_taken(self):
        letter = "First sentence here about print solutions. Second sentence here.\n"
        lines = mc.derived_lines("", letter)
        self.assertEqual(lines, [("Letter topic sentence",
                                  "First sentence here about print solutions.")])

    def test_the_valediction_ends_the_letter_body(self):
        letter = ("A real body paragraph about managed print solutions.\n\n"
                  "Regards,\\\n\nJane Doe\n")
        lines = mc.derived_lines("", letter)
        self.assertEqual(len(lines), 1, lines)

    def test_the_summary_paragraph_is_split_into_sentences(self):
        resume = ("## Professional Summary\n\n"
                  "First claim about print. Second claim about datacentres.\n\n"
                  "## Core Skills\n\n- A skills entry\n")
        lines = [l for lab, l in mc.derived_lines(resume, "") if lab == "Professional Summary"]
        self.assertEqual(lines, ["First claim about print.",
                                 "Second claim about datacentres."])

    def test_education_and_certifications_are_not_source_bullets(self):
        """They make no achievement claims, so nothing in them can be a source."""
        resume = (self.EXPERIENCE +
                  "\n## Education\n\n- Master of Engineering, State University\n"
                  "\n## Certifications and training\n\n- ITIL Foundation certificate\n")
        bullets = mc.source_bullets(resume)
        self.assertTrue(any("managed print" in b for b in bullets))
        self.assertFalse(any("Master of Engineering" in b for b in bullets), bullets)
        self.assertFalse(any("ITIL" in b for b in bullets), bullets)

    def test_a_date_fragment_is_never_offered_as_a_source_bullet(self):
        """A bare date range is five tokens and would otherwise pair with a whole summary
        sentence on the year alone. PAIR_MIN_CONTENT is the guard."""
        score, bullet, _a, _b = mc.best_source(
            "Delivered enterprise infrastructure across Sep 2019 engagements in Springfield",
            ["Sep 2016 - Sep 2019"], self.stopwords)
        self.assertEqual((score, bullet), (0.0, ""))

    def test_plural_only_stemming(self):
        """service/services must not read as a difference; verb forms are left alone on
        purpose, because a crude stem is a word the reader cannot read back."""
        self.assertEqual(mc.word_stem("services"), mc.word_stem("service"))
        self.assertEqual(mc.word_stem("capabilities"), "capability")
        self.assertEqual(mc.word_stem("business"), "business")
        self.assertEqual(mc.word_stem("analysis"), "analysis")

    def test_the_section_labels_and_explains_itself(self):
        out = self.render("## Core Skills\n\n- A skills entry with several content words\n\n"
                          + self.EXPERIENCE)
        self.assertIn("DIRECTION IS NOT STABLE", out)
        self.assertIn("matched cleanly", out)


class TestClaimSplitOffset(unittest.TestCase):
    """AD VOCABULARY once reported cover-letter lines low by the header block's own length.

    `claim_split()` drops the header block and `locate()` then numbers from line 1 of what
    remains; every other section of the same report numbered the same letter correctly,
    which is what pins the defect to this one path. A wrong anchor still looks like a
    finding, and this report is meant to be the one pattern search a Read-only reviewer has.
    """

    HEADER = ("Jane Doe\n"
              "Springfield · jane@example.com\n"
              "0400 000 000\n"
              "\n"
              "10 September 2026\n"
              "\n"
              "Re: Senior Data Analyst\n"
              "\n"
              "Dear Hiring Manager,\n")          # 9 lines; the body starts at line 10

    BODY = "I have delivered bearings power transmission work in regulated environments.\n"

    def test_the_offset_is_the_number_of_lines_dropped(self):
        offset, body = mc.claim_split("Jane_Doe_CoverLetter_260910_Acme_Role.md",
                                      self.HEADER + self.BODY)
        self.assertEqual(offset, 9)
        self.assertTrue(body.startswith("I have delivered"))

    def test_a_body_phrase_reports_its_whole_file_line(self):
        """The defect itself. locate() alone says 1; locate() + offset says 10."""
        text = self.HEADER + self.BODY
        offset, body = mc.claim_split("Jane_Doe_CoverLetter_260910_Acme_Role.md", text)
        n, _line = mc.locate("bearings power transmission", body)
        self.assertEqual(n, 1)                   # numbering the body alone - the bug
        self.assertEqual(n + offset, 10)         # the whole-file line - what is reported
        self.assertIn("bearings power transmission", text.splitlines()[9].lower())

    def test_a_resume_gets_offset_zero(self):
        """First fallthrough. Nothing is dropped, so adding the offset must be a no-op."""
        text = "# Jane Doe\n\n## Professional Experience\n\n### Acme Print Co - CSE\n"
        offset, body = mc.claim_split("Jane_Doe_Resume_260910_Acme_Role.md", text)
        self.assertEqual(offset, 0)
        self.assertEqual(body, text)

    def test_a_letter_with_no_salutation_gets_offset_zero(self):
        """Second fallthrough. A letter with no `Dear` in the first 14 lines keeps every
        line, so an offset here would double-count into thin air."""
        text = "Jane Doe\nSpringfield\n\nI have delivered data fusion work.\n"
        offset, body = mc.claim_split("Jane_Doe_CoverLetter_260910_Acme_Role.md", text)
        self.assertEqual(offset, 0)
        self.assertEqual(body, text)

    def test_claim_text_still_returns_the_body_alone(self):
        """The wrapper the one non-reporting call site still uses."""
        text = self.HEADER + self.BODY
        self.assertEqual(mc.claim_text("Jane_Doe_CoverLetter_260910_Acme_Role.md", text),
                         mc.claim_split("Jane_Doe_CoverLetter_260910_Acme_Role.md", text)[1])


class TestInputStamp(unittest.TestCase):
    """The report used to carry no record of when it ran or what it read, so a stale paste
    (a document edited, or the pattern file changed, after the paste was taken) was
    invisible to a Read-only reviewer. The stamp makes that legible, not impossible: the
    reviewer can read it but cannot regenerate it.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.app = os.path.join(self._tmp.name, "2026-01-01_Acme_DataAnalyst")
        os.makedirs(self.app)
        self.resume = os.path.join(self.app, "Jane_Doe_Resume_260101_Acme_Role.md")
        self.letter = os.path.join(self.app, "Jane_Doe_CoverLetter_260101_Acme_Role.md")
        with open(self.resume, "w", encoding="utf-8") as fh:
            fh.write("# Jane Doe\n\n## Professional Experience\n\n- A bullet.\n")
        with open(self.letter, "w", encoding="utf-8") as fh:
            fh.write("Jane Doe\\\njane@example.com\n\nRe: Data Analyst\n\nDear Hiring Manager,\n\n"
                      "Body.\n\nRegards,\\\nJane Doe\n")

    def report(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mc.report_application(self.app, mc.load_categories(BANNED), [], BANNED)
        return buf.getvalue()

    def test_stamp_names_the_pattern_file_fingerprint(self):
        out = self.report()
        with open(BANNED, "rb") as fh:
            expected = hashlib.sha256(fh.read()).hexdigest()[:12]
        self.assertIn(expected, out)

    def test_pattern_file_edit_changes_the_fingerprint(self):
        """The break-it probe."""
        tmp_banned = os.path.join(self._tmp.name, "banned_patterns.txt")
        with open(BANNED, "rb") as fh:
            original = fh.read()
        with open(tmp_banned, "wb") as fh:
            fh.write(original)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mc.report_application(self.app, mc.load_categories(tmp_banned), [], tmp_banned)
        out1 = buf.getvalue()
        fp1 = hashlib.sha256(original).hexdigest()[:12]
        self.assertIn(fp1, out1)

        with open(tmp_banned, "ab") as fh:
            fh.write(b"\n# probe comment\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mc.report_application(self.app, mc.load_categories(tmp_banned), [], tmp_banned)
        out2 = buf.getvalue()
        with open(tmp_banned, "rb") as fh:
            fp2 = hashlib.sha256(fh.read()).hexdigest()[:12]
        self.assertNotEqual(fp1, fp2)
        self.assertIn(fp2, out2)

    def test_every_document_read_is_listed_with_its_mtime(self):
        fixed = 1700000000
        os.utime(self.resume, (fixed, fixed))
        os.utime(self.letter, (fixed, fixed))
        expected_mtime = mc.datetime.fromtimestamp(fixed).astimezone().strftime(
            "%Y-%m-%d %H:%M:%S %z")
        out = self.report()
        self.assertIn("%s  mtime %s" % (os.path.basename(self.resume), expected_mtime), out)
        self.assertIn("%s  mtime %s" % (os.path.basename(self.letter), expected_mtime), out)

    def test_corpus_banner_carries_the_stamp(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mc.report_corpus(self._tmp.name, mc.load_categories(BANNED), BANNED)
        out = buf.getvalue()
        self.assertIn("generated ", out)
        self.assertIn("patterns ", out)

    def test_stamp_is_bounded(self):
        out = self.report()
        lines = out.splitlines()
        start = next(i for i, l in enumerate(lines) if l.startswith("generated "))
        # inputs printed: resume, letter - no posting and no --facts given in this fixture,
        # and both must be skipped rather than printed as missing.
        block = []
        for l in lines[start + 1:]:
            if not l.startswith("  "):
                break
            block.append(l)
        self.assertEqual(len(block), 2)


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
            for section in ("BANNED STRINGS", "ATOMICITY", "DURATIONS", "SECTION HEADERS",
                            "AD VOCABULARY"):
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


class TestAdVocabulary(unittest.TestCase):
    """Phrases in the ad AND the documents, absent from the facts file.

    The four measured cases are the specification, not an illustration: on the source corpus
    this pattern predicted 4 of 10 over-claims in one pass, and one of the four
    ("reconciliation") is a single word, which is why the check is not purely multi-word.
    """

    MEASURED = ["data fusion", "reconciliation", "reporting documentation",
                "translating business requirements into dashboards"]

    def setUp(self):
        self.stopwords, self.phrases = mc.load_stoplist(mc.STOPLIST)

    def run_check(self, ad, doc, facts="Nothing relevant here."):
        return mc.ad_vocabulary(ad, [doc], facts, self.stopwords, self.phrases)

    def test_the_four_measured_phrases_are_all_surfaced(self):
        """The regression that matters. If this ever goes quiet, the check is decorative."""
        for phrase in self.MEASURED:
            with self.subTest(phrase=phrase):
                ad = "The role requires %s across the group." % phrase
                doc = "I have delivered %s in regulated environments." % phrase
                self.assertIn(phrase, self.run_check(ad, doc))

    def test_a_phrase_the_facts_file_licenses_is_not_reported(self):
        ad = "We need data fusion across sources."
        doc = "I delivered data fusion work."
        self.assertEqual(
            self.run_check(ad, doc, "The candidate delivered data fusion at a regulator."), [])

    def test_a_phrase_only_in_the_ad_is_not_reported(self):
        """The check is about adoption. An unadopted ad phrase is not a finding."""
        ad = "We need data fusion across sources."
        doc = "I built reporting pipelines."
        self.assertEqual(self.run_check(ad, doc), [])

    def test_a_phrase_only_in_the_documents_is_not_reported(self):
        ad = "We need reporting pipelines."
        doc = "I delivered data fusion work."
        self.assertEqual(self.run_check(ad, doc), [])

    def test_longest_match_wins(self):
        phrase = "translating business requirements into dashboards"
        found = self.run_check("The role is %s." % phrase, "I did %s." % phrase)
        self.assertIn(phrase, found)
        self.assertNotIn("business requirements", found)
        self.assertNotIn("requirements into dashboards", found)

    def test_ngrams_do_not_span_a_sentence_boundary(self):
        ad = "We build dashboards. Reconciliation matters here."
        doc = "I build dashboards. Reconciliation matters here."
        self.assertNotIn("dashboards reconciliation", self.run_check(ad, doc))

    def test_short_words_are_not_reported_alone(self):
        """UNIGRAM_MIN_LEN. Without it every shared short word is a hit."""
        ad = "We need reports and charts."
        doc = "I built reports and charts."
        found = self.run_check(ad, doc)
        self.assertNotIn("reports", found)
        self.assertNotIn("charts", found)

    def test_a_phrase_may_not_start_or_end_with_a_stopword(self):
        ad = "Responsible for the reporting of results."
        doc = "Responsible for the reporting of results."
        for phrase in self.run_check(ad, doc):
            toks = phrase.split()
            self.assertNotIn(toks[0], self.stopwords, phrase)
            self.assertNotIn(toks[-1], self.stopwords, phrase)

    def test_cover_letter_header_block_is_excluded(self):
        """Addressing metadata is dense in recon's proper nouns and makes no claims."""
        letter = ("# Jane Doe\n\nSpringfield\n\nRe: Data Analyst\n\n"
                  "Dear Alex Example,\n\nI have delivered data fusion work.\n")
        for name in ("Jane_Doe_CoverLetter_260101_X_Y.md", "Jane_Doe_Cover_Letter_260101_X_Y.md",
                     "jane-doe-coverletter.md"):
            with self.subTest(name=name):
                kept = mc.claim_text(name, letter)
                self.assertNotIn("Alex", kept)
                self.assertIn("data fusion", kept)

    def test_resume_is_never_truncated_by_claim_text(self):
        resume = "# Jane Doe\n\nDear reader, this line stays.\n\nExperience.\n"
        self.assertEqual(mc.claim_text("Jane_Doe_Resume_260101_X_Y.md", resume), resume)

    def test_no_posting_yields_no_crash(self):
        self.assertEqual(mc.ad_vocabulary("", ["anything"], "", self.stopwords, self.phrases), [])


class TestAdVocabStoplist(unittest.TestCase):
    """Two gates on ad_vocab_stoplist.txt, guarding opposite failures.

    Under-suppression is noise, which is annoying. OVER-suppression is a silent false clean,
    which is the failure mode this whole script exists to prevent - so the second test pins
    the four measured phrases against the stop-list permanently.
    """

    def setUp(self):
        self.stopwords, self.phrases = mc.load_stoplist(mc.STOPLIST)

    def test_every_multi_word_entry_is_actually_suppressed(self):
        """Per-entry probe. Adding an entry probes it; there is no unprobed entry."""
        for phrase in sorted(self.phrases):
            with self.subTest(phrase=phrase):
                ad = "The role involves %s daily." % phrase
                doc = "I have done %s daily." % phrase
                found = mc.ad_vocabulary(ad, [doc], "irrelevant", self.stopwords, self.phrases)
                self.assertNotIn(phrase, found)

    def test_the_stoplist_never_suppresses_a_measured_over_claim(self):
        """The over-suppression gate. These four are why the check exists."""
        for phrase in TestAdVocabulary.MEASURED:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.phrases)
                for token in phrase.split():
                    self.assertNotIn(token, self.phrases)
                if " " not in phrase:
                    self.assertNotIn(phrase, self.stopwords)

    def test_entries_are_lowercase_and_unique(self):
        seen = []
        with open(mc.STOPLIST, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                self.assertEqual(line, line.lower(), "not lowercase: %r" % line)
                self.assertNotIn(line, seen, "duplicate entry: %r" % line)
                seen.append(line)

    def test_both_kinds_of_entry_are_present(self):
        self.assertTrue(self.stopwords, "no single-word entries parsed")
        self.assertTrue(self.phrases, "no multi-word entries parsed")


class TestScriptRunsAdVocab(unittest.TestCase):
    """The AD VOCABULARY section end to end, on a throwaway fixture with a posting."""

    POSTING = "# Acme - Data Analyst\n\nThe role requires data fusion across the group.\n"
    RESUME = ("# Jane Doe\n\n## Experience\n\n"
              "- Delivered data fusion work (Jan 2020 – Jun 2022).\n")
    FACTS = "## Acme — Analyst (Jan 2020 – Jun 2022)\n\n- Built reporting pipelines.\n"

    def _fixture(self, td, posting=True):
        app = os.path.join(td, "2026-01-01_Acme_DataAnalyst")
        os.makedirs(app)
        with open(os.path.join(app, "Jane_Doe_Resume_260101_Acme.md"), "w") as fh:
            fh.write(self.RESUME)
        if posting:
            with open(os.path.join(app, "posting.md"), "w") as fh:
                fh.write(self.POSTING)
        facts = os.path.join(td, "facts.md")
        with open(facts, "w") as fh:
            fh.write(self.FACTS)
        return app, facts

    def test_adopted_phrase_is_reported_with_facts(self):
        with tempfile.TemporaryDirectory() as td:
            app, facts = self._fixture(td)
            r = subprocess.run([sys.executable, CHECKS, app, "--facts", facts],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("AD VOCABULARY NOT LICENSED BY THE FACTS FILE", r.stdout)
            self.assertIn("data fusion", r.stdout)
            self.assertIn("warn", r.stdout)

    def test_without_facts_the_section_says_why_it_cannot_compare(self):
        with tempfile.TemporaryDirectory() as td:
            app, _facts = self._fixture(td)
            r = subprocess.run([sys.executable, CHECKS, app], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("no --facts file given", r.stdout)

    def test_without_posting_the_section_says_so(self):
        with tempfile.TemporaryDirectory() as td:
            app, facts = self._fixture(td, posting=False)
            r = subprocess.run([sys.executable, CHECKS, app, "--facts", facts],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("no *posting*.md", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
