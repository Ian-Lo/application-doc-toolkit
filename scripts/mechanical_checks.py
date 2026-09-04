#!/usr/bin/env python3
# source-hash: 15df575b391a scripts/mechanical_checks.py
"""mechanical_checks.py - a document reviewer's mechanical pass, as one command.

    python3 mechanical_checks.py path/to/one-application-folder
    python3 mechanical_checks.py --corpus path/to/applications-root
    python3 mechanical_checks.py --patterns banned_patterns.txt --facts facts.md <folder>

Checks outgoing application documents (resumes and cover letters, matched by filename)
against a banned-pattern file, and prints the mechanical context a reviewer needs:
banned-string hits with line numbers, the cover letter's header block, link and bracketed-
token atomicity, every duration phrase beside the canonical date spans in your facts file,
and every section header beside its block contents.

WHY THIS EXISTS. Two measured problems, one fix.

1. Cost. A review used to run six to ten separate greps, and in an LLM-agent review every
   result stays in the transcript and is re-sent on every later turn. One unanchored grep
   returned 492 lines of which 448 were substrings like "univerSITy".

2. Trust. A mechanical check that an agent (or a person) runs and then *reports on* can be
   misreported - measured five times in the project this tool comes from, every time in the
   same direction: run against the change just made rather than against the rule. A check
   that emits a report cannot be misreported.

WHAT THIS DOES NOT DO. It reports; it never judges and never edits. Banned-string hits can
be licensed - keep an adjudication record of your exceptions and read it before treating a
hit as a finding. Durations are printed beside their canonical spans; the pairing is the
reviewer's judgement, because a duration phrase is sometimes an under-claim whose
correction is *larger*.

FILES.
- The pattern file (default: banned_patterns.txt next to this script) uses one pattern per
  line: bare text for a case-insensitive literal, `re:<regex>` for a regex, `#@ <name>` to
  start a category block, `#` for comments. Categories: `tic` (report for adjudication),
  `tell` (warn - machine-copy tells), `selfdq` (hard - language that withdraws the
  application).
- The facts file (`--facts`, optional) is whatever document holds your verified career
  facts. Every parenthesised span in it of the form `(Mon YYYY - Mon YYYY)` or
  `(Mon YYYY - present)` becomes a canonical duration the report prints for comparison.
- Documents are `*.md` files in the application folder whose names contain `Resume` or
  `CoverLetter`/`Cover_Letter` (case-insensitive).
- The saved posting (any `*.md` in the application folder whose name contains `posting`,
  case-insensitive) and the facts file together drive the AD VOCABULARY section: phrases in
  both the ad and the outgoing documents but absent from the facts file. Its noise floor is
  `ad_vocab_stoplist.txt` beside this script - a separate file for the same reason as the
  pattern file: tunable without editing code.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PATTERNS = os.path.join(HERE, "banned_patterns.txt")

CATEGORIES = ("tic", "tell", "selfdq")
SECTION_ITEM_CAP = 8
SEVERITY = {
    "tic": "report for adjudication",
    "tell": "warn",
    "selfdq": "HARD - withdraws the application",
}

MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), start=1)}

# Duration phrases: digits and spelled-out numbers, plus bare career-length tokens.
NUMWORD = (r"one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|"
           r"fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty")
DURATION_RE = re.compile(
    r"\b(?:(?:\d{1,2}|%s)[\s-]*(?:\+\s*)?(?:years?|yrs?|months?|decades?)"
    r"|(?:a|two|three)\s+decades?|two\s+decades)\b" % NUMWORD, re.I)
SPAN_RE = re.compile(
    r"\(([A-Z][a-z]{2})\s*(\d{4})\s*[–—-]\s*(?:([A-Z][a-z]{2})\s*(\d{4})|present|Present)\)")
LINK_RE = re.compile(r"\[[^\]\n]*\]\([^)\n]*\)")
OPEN_LINK_RE = re.compile(r"\[[^\]\n]*$")
HEADER_RE = re.compile(r"^(#{2,4})\s+(.*)$")
DOC_NAME_RE = re.compile(r".*(Resume|Cover[_ ]?Letter).*\.md$", re.I)


@dataclass
class Pattern:
    raw: str
    is_regex: bool
    rx: "re.Pattern | None" = None
    lit: str = ""


def compile_patterns(lines) -> list:
    """One implementation of the pattern format: `re:` lines become regexes, everything
    else a casefolded literal. Blank lines and `#` comments are skipped."""
    out = []
    for raw in lines:
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        if raw.startswith("re:"):
            body = raw[3:]
            try:
                out.append(Pattern(raw=raw, is_regex=True, rx=re.compile(body, re.I)))
            except re.error as exc:
                raise ValueError("bad regex %r: %s" % (body, exc))
        else:
            out.append(Pattern(raw=raw, is_regex=False, lit=re.sub(r"\s+", " ", raw).casefold()))
    return out


def load_categories(path: str) -> dict:
    """Read the pattern file into {category: [Pattern]}."""
    if not os.path.isfile(path):
        sys.stderr.write("FATAL: %s is missing - there are no patterns to check.\n" % path)
        sys.exit(2)
    blocks: dict = {c: [] for c in CATEGORIES}
    current = None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            stripped = raw.strip()
            if stripped.startswith("#@"):
                current = stripped[2:].strip()
                continue
            if not stripped or stripped.startswith("#"):
                continue
            if current in blocks:
                blocks[current].append(stripped)
    out = {}
    for cat, lines in blocks.items():
        out[cat] = compile_patterns(lines)
    if not any(out.values()):
        sys.stderr.write("FATAL: %s parsed to zero patterns - the file looks truncated.\n" % path)
        sys.exit(2)
    return out


def unwrap_blocks(text: str) -> list:
    """Paragraph-joined view of the text: (start_line, end_line, joined) blocks.

    Blank lines, headers and quotes end a block; a bullet starts one and accumulates its
    continuation lines. Exists so a phrase split by a line wrap is still seen whole: a
    live self-disqualifying sentence once wrapped mid-phrase ("... if the / <gap>
    background is non-negotiable ...") and every per-line scanner passed it — a reading
    reviewer caught it, and a wrap-aware rescan then found three more evading the same
    way. Per-line scanning alone is not a scan of the document; it is a scan of its
    typesetting.
    """
    blocks, lines_in, cur = [], [], []

    def flush():
        if cur:
            blocks.append((lines_in[0], lines_in[-1], " ".join(cur)))
        lines_in.clear()
        cur.clear()

    for n, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if not s or s.startswith(("#", ">")):
            flush()
            continue
        if s.startswith(("-", "*", "•")):
            flush()
        lines_in.append(n)
        cur.append(s)
    flush()
    return blocks


def hits_in(text: str, patterns) -> list:
    """Case-insensitive scan. Returns (lineno, pattern, line).

    Two passes: per line (for exact line numbers), then per unwrapped paragraph, so a
    phrase a line wrap splits is still caught. A wrapped hit is reported once, at its
    block's first line, with the joined text prefixed "(wrapped)" — and only when no
    line inside the block already hit the same pattern, so nothing double-reports.
    """
    found = []
    line_hits = set()
    for n, line in enumerate(text.splitlines(), start=1):
        for p in patterns:
            if p.is_regex:
                if p.rx.search(line):
                    found.append((n, p.raw, line.strip()))
                    line_hits.add((n, p.raw))
            elif p.lit and p.lit in line.casefold():
                found.append((n, p.raw, line.strip()))
                line_hits.add((n, p.raw))
    for start, end, joined in unwrap_blocks(text):
        for p in patterns:
            hit = p.rx.search(joined) if p.is_regex else (p.lit and p.lit in joined.casefold())
            if not hit:
                continue
            if any((n, p.raw) in line_hits for n in range(start, end + 1)):
                continue
            found.append((start, p.raw, "(wrapped) " + joined[:110]))
    found.sort(key=lambda t: t[0])
    return found


def months_between(m1: int, y1: int, m2: int, y2: int) -> int:
    return (y2 - y1) * 12 + (m2 - m1)


def fmt_span(months: int) -> str:
    return "%dy%dm" % (months // 12, months % 12)


def canonical_spans(path: str) -> list:
    """Every parenthesised date span in the facts file, with its computed length."""
    if not path or not os.path.isfile(path):
        return []
    out = []
    today = date.today()
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, start=1):
            for m in SPAN_RE.finditer(line):
                m1, y1, m2, y2 = m.group(1), int(m.group(2)), m.group(3), m.group(4)
                if m1 not in MONTHS:
                    continue
                if m2 is None:
                    em, ey = today.month, today.year
                else:
                    if m2 not in MONTHS:
                        continue
                    em, ey = MONTHS[m2], int(y2)
                total = months_between(MONTHS[m1], y1, em, ey)
                ctx = line.strip()
                if ctx.startswith("#"):
                    ctx = ctx.lstrip("# ").strip()
                out.append((m.group(0), fmt_span(total), ctx[:64], n))
    # de-duplicate on the span text, keeping the first (headings come early)
    seen, uniq = set(), []
    for span, length, ctx, n in out:
        if span in seen:
            continue
        seen.add(span)
        uniq.append((span, length, ctx, n))
    return uniq


def outgoing_docs(app_dir: str) -> list:
    out = []
    for name in sorted(os.listdir(app_dir)):
        if DOC_NAME_RE.match(name):
            out.append(os.path.join(app_dir, name))
    return out


def check_letter_header(text: str) -> list:
    """The cover letter's header block. A full draft-review-revise cycle once produced a
    letter with no name, no contact line and no Re: line - every other check was about
    prose, so nothing caught it. Returns a list of problems."""
    head = "\n".join(text.splitlines()[:14])
    problems = []
    if not re.search(r"^[^\s#|>-][^|]*\\\s*$", head, re.M):
        problems.append("no name/address line with a trailing-backslash hard break")
    if "@" not in head:
        problems.append("no contact line with an email address")
    if not re.search(r"^Re:\s*\S", head, re.M):
        problems.append("no 'Re:' line naming the advertised role")
    if not re.search(r"^Dear\b", head, re.M):
        problems.append("no 'Dear ...' salutation")
    if not re.search(r"^Regards,\\\s*$", text, re.M):
        problems.append("no 'Regards,\\' valediction with its hard break")
    return problems


def check_atomicity(text: str) -> list:
    """Bracketed spans split across a line wrap silently stop being links."""
    problems = []
    for n, line in enumerate(text.splitlines(), start=1):
        if OPEN_LINK_RE.search(line):
            problems.append((n, "markdown link bracket left open at end of line"))
    return problems


# ---------------------------------------------------------------------------
# Ad vocabulary the facts file does not license.
#
# Proposed by a review on the source corpus after measuring the pattern rather than guessing
# it: ad-vocabulary adoption was the single reliable predictor of over-claims in that pass,
# 4 of 10. "data fusion", "reconciliation", "reporting documentation", "translating business
# requirements into dashboards" - each present in the ad's verbatim block and absent from the
# fact library.
#
# The set is computable, and computing it costs the reviewer nothing. It matters more here
# than a check normally would: if the reviewing agent has no pattern-search tool, this report
# is the only pattern search it has.
#
# WARN-STYLE, NEVER A FAILURE. A hit is a question - "does the library license this?" - and
# the honest answers include "yes, in different words". Two of the four measured hits were
# real over-claims; the check does not know which.
# ---------------------------------------------------------------------------

# Same reasoning as SECTION_ITEM_CAP: the check pays off on the first handful, and an
# uncapped list would drown the sections above it in the reviewer's transcript.
AD_VOCAB_CAP = 20
STOPLIST = os.path.join(HERE, "ad_vocab_stoplist.txt")
NGRAM_MIN, NGRAM_MAX = 2, 5
WORD_RE = re.compile(r"[a-z0-9][a-z0-9+#.&/-]*")
# Single words are included too, but only long ones. One of the four measured over-claims was
# the bare word "reconciliation", so a purely multi-word check would have missed a quarter of
# the evidence it was built on. Length is a crude rarity proxy and it is the right kind of
# crude: domain jargon is long ("reconciliation", "provenance" at 10, "orchestration"),
# ordinary connective English is short. Everything long AND generic ("information",
# "requirements", "stakeholders") goes in the stop-list instead.
UNIGRAM_MIN_LEN = 10
COVER_LETTER_RE = re.compile(r"cover[_ ]?letter", re.I)


def load_stoplist(path: str) -> tuple:
    """(single-word stopwords, multi-word suppressed phrases). See the file's own header."""
    words, phrases = set(), set()
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip().lower()
            if not line or line.startswith("#"):
                continue
            (phrases if " " in line else words).add(line)
    return words, phrases


def normalise_words(text: str) -> list:
    """Lowercase word tokens, markdown stripped. Sentence boundaries become gaps.

    Punctuation that ends a clause inserts a gap, so an n-gram never spans a full stop or a
    bullet boundary - "...into dashboards. Reconciliation of..." must not manufacture the
    phrase "dashboards reconciliation".
    """
    out = []
    for chunk in re.split(r"[.;:!?\n\r()\[\]{}|]+", text.lower()):
        chunk = re.sub(r"[*_`>#]+", " ", chunk)
        found = WORD_RE.findall(chunk)
        if found:
            out.append(found)
    return out


def ngrams(runs: list, lo: int = NGRAM_MIN, hi: int = NGRAM_MAX) -> set:
    out = set()
    for run in runs:
        for size in range(lo, hi + 1):
            for i in range(len(run) - size + 1):
                out.add(" ".join(run[i:i + size]))
    return out


def ad_vocabulary(ad_text: str, doc_texts: list, facts_text: str,
                  stopwords: set, phrases: set) -> list:
    """Phrases in the ad AND the documents but NOT in the facts file.

    Longest match wins: a 4-gram that survives suppresses the 2- and 3-grams inside it, so
    "translating business requirements into dashboards" is reported once rather than as six
    overlapping fragments. Boundary stopwords are dropped because a window that merely
    aligns ("of the reporting") is not vocabulary anyone adopted.
    """
    ad_runs = normalise_words(ad_text)
    if not ad_runs:
        return []
    ad = ngrams(ad_runs) | {w for run in ad_runs for w in run if len(w) >= UNIGRAM_MIN_LEN}
    doc_runs = normalise_words(" \n ".join(doc_texts))
    docs = ngrams(doc_runs) | {w for run in doc_runs for w in run}
    facts_runs = normalise_words(facts_text)
    facts = ngrams(facts_runs) | {w for run in facts_runs for w in run}

    kept = []
    for phrase in ad & docs:
        if phrase in facts or phrase in stopwords:
            continue
        # A suppressed phrase suppresses its own fragments too. Without this, stop-listing
        # "full academic transcript" leaves "full academic" and "academic transcript" behind,
        # which is worse than not stop-listing it at all.
        if any(phrase == p or phrase in p for p in phrases):
            continue
        toks = phrase.split()
        if toks[0] in stopwords or toks[-1] in stopwords:
            continue
        if all(t in stopwords for t in toks):
            continue
        kept.append(phrase)

    kept.sort(key=lambda p: (-len(p.split()), p))
    out = []
    for phrase in kept:
        if any(phrase in longer and phrase != longer for longer in out):
            continue
        out.append(phrase)
    return sorted(out, key=lambda p: (-len(p.split()), p))


def locate(phrase: str, text: str) -> tuple:
    """First (lineno, line) whose normalised form contains `phrase`, or (0, "")."""
    for n, line in enumerate(text.splitlines(), start=1):
        for run in normalise_words(line):
            if phrase in " ".join(run):
                return n, line.strip()
    return 0, ""


def claim_text(path: str, text: str) -> str:
    """The part of a document that makes claims, for the ad-vocabulary comparison.

    A cover letter's header block - name, contact lines, `Re:` and the salutation - is
    addressing metadata, never a claim, and it is dense in exactly the proper nouns recon
    supplies. Leaving it in put a hiring manager's name and the company's name in a report
    meant to surface adopted vocabulary. Everything from the salutation onward is kept.
    """
    if not COVER_LETTER_RE.search(os.path.basename(path)):
        return text
    lines = text.splitlines()
    for n, line in enumerate(lines[:14]):
        if re.match(r"\s*Dear\b", line):
            return "\n".join(lines[n + 1:])
    return text


POSTING_NAME_RE = re.compile(r"posting.*\.md$", re.I)


def read_posting(app_dir: str) -> str:
    """The saved ad: the first `*posting*.md` in the folder that is not an outgoing document."""
    for name in sorted(os.listdir(app_dir)):
        if POSTING_NAME_RE.search(name) and not DOC_NAME_RE.match(name):
            with open(os.path.join(app_dir, name), encoding="utf-8") as fh:
                return fh.read()
    return ""


def section_blocks(text: str) -> list:
    """Headers paired with the items beneath them.

    A block may be a bullet list (`-`/`*`/`•`), a middle-dot-separated prose line (skills
    sections are often written this way), or a plain paragraph. All three count as items -
    a header over a prose paragraph is exactly where the header-vs-block check needs to
    look, and skipping it silently was a measured coverage hole.
    """
    out, current, items, prose, saw_bullet = [], None, [], [], False

    def flush_prose():
        if not prose:
            return
        joined = " ".join(prose).strip()
        if "·" in joined:
            items.extend(p.strip() for p in joined.split("·") if p.strip())
        elif joined:
            items.append(joined)
        prose.clear()

    for line in text.splitlines():
        m = HEADER_RE.match(line)
        if m:
            flush_prose()
            if current:
                out.append((current, items))
            current, items, saw_bullet = m.group(2).strip(), [], False
        elif current and line.strip().startswith(("-", "*", "•")):
            if not saw_bullet:
                flush_prose()
            saw_bullet = True
            item = line.strip().lstrip("-*• ").strip()
            item = item.replace("**", "").lstrip("*").strip()
            items.append(item)
        elif current and not saw_bullet and line.strip():
            # Continuation lines under a bullet are intentionally dropped; only lines
            # before the first bullet accumulate as prose.
            prose.append(line.strip())
    flush_prose()
    if current:
        out.append((current, items))
    return out


def report_application(app_dir: str, cats: dict, spans: list, patterns_path: str,
                       facts_path: str = None) -> int:
    app = os.path.basename(app_dir.rstrip("/"))
    docs = outgoing_docs(app_dir)
    print("MECHANICAL CHECKS - %s" % app)
    print("scope: this application only (--corpus for the cross-application sweep)")
    if not docs:
        print("\n  no Resume/CoverLetter documents found - nothing to check")
        return 1

    print("\nBANNED STRINGS   (%s)" % os.path.basename(patterns_path))
    any_hit = False
    for cat in CATEGORIES:
        pats = cats[cat]
        rows = []
        for path in docs:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for n, raw, line in hits_in(text, pats):
                rows.append((os.path.basename(path), n, raw, line))
        if not rows:
            print("  %-7s clean  (%d patterns)" % (cat, len(pats)))
        else:
            any_hit = True
            print("  %-7s %d hit(s)  [%s]" % (cat, len(rows), SEVERITY[cat]))
            for fname, n, raw, line in rows:
                short = "Resume" if "resume" in fname.lower() else "Letter"
                print("      %s L%-4d %-34s %s" % (short, n, raw, line[:70]))
    if any_hit:
        print("  ! Some hits may be LICENSED. Read your adjudicated-exceptions record")
        print("    before reporting any of these as a finding.")

    for path in docs:
        if "resume" in os.path.basename(path).lower():
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        problems = check_letter_header(text)
        print("\nLETTER HEADER BLOCK")
        if problems:
            for p in problems:
                print("  MISSING  %s" % p)
        else:
            print("  complete - name, contact, Re:, salutation, valediction all present")

    print("\nATOMICITY")
    atom = []
    for path in docs:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for n, msg in check_atomicity(text):
            atom.append((os.path.basename(path), n, msg))
        nlinks = len(LINK_RE.findall(text))
        print("  %-46s %d complete link(s)" % (os.path.basename(path)[:46], nlinks))
    for fname, n, msg in atom:
        print("  BROKEN  %s L%d - %s" % (fname, n, msg))
    if not atom:
        print("  no split links")

    print("\nDURATIONS - re-derive each phrase against the canonical spans below")
    found_any = False
    for path in docs:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        short = "Resume" if "resume" in os.path.basename(path).lower() else "Letter"
        for n, line in enumerate(lines, start=1):
            for m in DURATION_RE.finditer(line):
                found_any = True
                start = max(0, m.start() - 34)
                print("  %s L%-4d %-18s ...%s..." % (
                    short, n, m.group(0), line[start:m.end() + 34].strip()))
    if not found_any:
        print("  no duration phrase in either document")
    if spans:
        print("  canonical spans, from the facts file:")
        for span, length, ctx, n in spans:
            print("      %-26s = %-7s  %s" % (span, length, ctx))
    else:
        print("  (no --facts file given, so no canonical spans to compare against)")

    print("\nSECTION HEADERS vs their blocks")
    for path in docs:
        if "resume" not in os.path.basename(path).lower():
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for header, items in section_blocks(text):
            if not items:
                continue
            print("  %s  (%d item%s)" % (header, len(items), "" if len(items) == 1 else "s"))
            # Capped: the check is about whether a header over-claims, which is legible
            # from the first few items. An uncapped experience block drowned the skills
            # section this check actually pays off on.
            for it in items[:SECTION_ITEM_CAP]:
                print("      - %s" % it[:88])
            if len(items) > SECTION_ITEM_CAP:
                print("      ... %d more (read the file if the header looks over-claimed)"
                      % (len(items) - SECTION_ITEM_CAP))
    print("\n  Ask of each header: what does it assert that its block does not evidence?")
    print("  Yield is highest when the ad is written as abstract capability nouns.")

    print("\nAD VOCABULARY NOT LICENSED BY THE FACTS FILE   (warn - a question, not a defect)")
    ad_text = read_posting(app_dir)
    if not ad_text:
        print("  no *posting*.md in the application folder - cannot compare")
    elif not facts_path or not os.path.isfile(facts_path):
        print("  no --facts file given - cannot tell licensed vocabulary from adopted vocabulary")
    elif not os.path.isfile(STOPLIST):
        print("  MISSING %s - the check cannot run without its noise floor"
              % os.path.basename(STOPLIST))
    else:
        doc_texts = []
        for path in docs:
            with open(path, encoding="utf-8") as fh:
                doc_texts.append(claim_text(path, fh.read()))
        with open(facts_path, encoding="utf-8") as fh:
            facts_text = fh.read()
        stopwords, phrases = load_stoplist(STOPLIST)
        found = ad_vocabulary(ad_text, doc_texts, facts_text, stopwords, phrases)
        if not found:
            print("  clean - every phrase shared with the ad also appears in the facts file")
        else:
            print("  %d phrase(s) in the ad AND the documents, absent from the facts file:"
                  % len(found))
            for phrase in found[:AD_VOCAB_CAP]:
                where = []
                for path, text in zip(docs, doc_texts):
                    n, line = locate(phrase, text)
                    if n:
                        short = "Resume" if "resume" in os.path.basename(path).lower() else "Letter"
                        where.append("%s L%d" % (short, n))
                print("      %-52s %s" % (phrase[:52], ", ".join(where)))
            if len(found) > AD_VOCAB_CAP:
                print("      ... %d more" % (len(found) - AD_VOCAB_CAP))
            print("  Ask of each: does the facts file license this claim, in these words or any"
                  " others?")
            print("  A hit is NOT automatically a defect - the library often licenses the same"
                  " claim")
            print("  in different vocabulary. Adoption measured as 4-of-10 over-claims on the"
                  " source corpus.")
            print("  Expect proper nouns here (people, teams, products named by recon). Those"
                  " are")
            print("  usually addressing, not claims - skip them and read the capability"
                  " phrases.")
    return 0


def report_corpus(root: str, cats: dict) -> int:
    print("CORPUS SWEEP - every Resume/CoverLetter document under %s" % root)
    print("This is the deliberate cross-application pass. Say so in your report.\n")
    docs = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in sorted(filenames):
            if DOC_NAME_RE.match(name):
                docs.append(os.path.join(dirpath, name))
    print("documents scanned: %d\n" % len(docs))
    for cat in CATEGORIES:
        per_app: dict = {}
        total = 0
        for path in sorted(docs):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            hs = hits_in(text, cats[cat])
            if hs:
                app = os.path.relpath(os.path.dirname(path), root)
                per_app.setdefault(app, 0)
                per_app[app] += len(hs)
                total += len(hs)
        print("%-7s %d hit(s) across %d application(s)  [%s]" % (
            cat, total, len(per_app), SEVERITY[cat]))
        for app, count in sorted(per_app.items(), key=lambda kv: -kv[1]):
            print("    %-72s %d" % (app[:72], count))
        print()
    print("Licensed hits can exist - check your adjudicated-exceptions record.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("app_dir", nargs="?", help="one application folder to check")
    ap.add_argument("--corpus", metavar="ROOT",
                    help="cross-application sweep over every application under ROOT")
    ap.add_argument("--patterns", default=DEFAULT_PATTERNS,
                    help="pattern file (default: banned_patterns.txt beside this script)")
    ap.add_argument("--facts", default=None,
                    help="facts file whose (Mon YYYY - Mon YYYY) spans become canonical durations")
    args = ap.parse_args()

    cats = load_categories(args.patterns)
    if args.corpus:
        if not os.path.isdir(args.corpus):
            sys.stderr.write("not a directory: %s\n" % args.corpus)
            return 2
        return report_corpus(args.corpus, cats)
    if not args.app_dir:
        ap.error("give an application directory, or --corpus ROOT")
    if not os.path.isdir(args.app_dir):
        sys.stderr.write("not a directory: %s\n" % args.app_dir)
        return 2
    return report_application(args.app_dir, cats, canonical_spans(args.facts), args.patterns,
                              args.facts)


if __name__ == "__main__":
    sys.exit(main())
