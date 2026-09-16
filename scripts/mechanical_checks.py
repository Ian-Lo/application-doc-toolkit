#!/usr/bin/env python3
# source-hash: e0e8b28b635f scripts/mechanical_checks.py
"""mechanical_checks.py - a document reviewer's mechanical pass, as one command.

    python3 mechanical_checks.py path/to/one-application-folder
    python3 mechanical_checks.py --corpus path/to/applications-root
    python3 mechanical_checks.py --patterns banned_patterns.txt --facts facts.md <folder>

Checks outgoing application documents (resumes and cover letters, matched by filename)
against a banned-pattern file, and prints the mechanical context a reviewer needs:
a staleness stamp naming when the report ran and the fingerprint of every input it read,
banned-string hits with line numbers, the cover letter's header block, link and bracketed-
token atomicity, every duration phrase beside the canonical date spans in your facts file,
every section header beside its block contents, and every derived summary/skills/topic-
sentence line beside the experience bullet it compresses.

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
import hashlib
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime

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


def fingerprint(path: str) -> str:
    """First 12 hex of sha256 - so a reader can tell whether the pattern file or the facts
    file changed since a report was generated, the same shape a source-derived file's own
    provenance header uses."""
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:12]


def print_input_stamp(patterns_path: str, doc_paths: list) -> None:
    """One header line plus one line per input actually read - the report's own
    staleness stamp.

    A report generated before a pattern-file edit, or before a document was last saved,
    looks identical to a fresh one unless it says when it ran and what it read. A stale
    paste has reported 'clean' on a live match before - the mechanism this guards against.

    A listed path that does not exist (no posting saved yet, no --facts given) is skipped,
    never printed as missing - the report's own sections already say so.
    """
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    stamp = "generated %s | patterns %s@%s" % (
        now, os.path.basename(patterns_path), fingerprint(patterns_path))
    if os.path.isfile(STOPLIST):
        stamp += " | stoplist %s@%s" % (os.path.basename(STOPLIST), fingerprint(STOPLIST))
    print(stamp)
    for path in doc_paths:
        if not path or not os.path.exists(path):
            continue
        mtime = datetime.fromtimestamp(os.path.getmtime(path)).astimezone().strftime(
            "%Y-%m-%d %H:%M:%S %z")
        print("  %s  mtime %s" % (os.path.basename(path), mtime))


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


def claim_split(path: str, text: str) -> tuple:
    """`(offset, body)` - the claim-making part of a document, and the number of lines
    dropped before it.

    A cover letter's header block - name, contact lines, `Re:` and the salutation - is
    addressing metadata, never a claim, and it is dense in exactly the proper nouns recon
    supplies. Leaving it in put a hiring manager's name and the company's name in a report
    meant to surface adopted vocabulary. Everything from the salutation onward is kept.

    THE OFFSET IS THE WHOLE POINT of returning a pair rather than the body alone. A caller
    that reports a line number must add it back: `locate()` numbers from line 1 of whatever
    it is handed, so numbering the body alone reports every letter line low by the length of
    the dropped header block - a real defect, caught only because every other section of the
    same report numbered the same letter correctly.

    Offset 0 on both fallthrough paths (a resume, or a letter with no salutation in the first
    14 lines) - nothing was dropped on either, so adding the offset back is a no-op.
    """
    if not COVER_LETTER_RE.search(os.path.basename(path)):
        return 0, text
    lines = text.splitlines()
    for n, line in enumerate(lines[:14]):
        if re.match(r"\s*Dear\b", line):
            return n + 1, "\n".join(lines[n + 1:])
    return 0, text


def claim_text(path: str, text: str) -> str:
    """`claim_split()`'s body alone, for a caller that reports no line number.

    Any NEW caller that prints a line number wants `claim_split()` and its offset, not this.
    """
    return claim_split(path, text)[1]


POSTING_NAME_RE = re.compile(r"posting.*\.md$", re.I)


def posting_path(app_dir: str) -> "str | None":
    """The saved ad's own path, for the input stamp - `read_posting()` returns content only."""
    for name in sorted(os.listdir(app_dir)):
        if POSTING_NAME_RE.search(name) and not DOC_NAME_RE.match(name):
            return os.path.join(app_dir, name)
    return None


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


# ---------------------------------------------------------------------------
# Body vs compression: the derived line beside the bullet it compresses.
#
# A summary sentence, a Core Skills entry or a cover-letter topic sentence often says
# something DIFFERENT from the resume bullet it was compressing - a generalisation over an
# accurate fact that is not itself accurate. Every fact underneath can be licensed while the
# generalisation over them is not.
#
# IT IS A PAIRING PRINTER, NOT A PASS/FAIL TEST. The whole premise is that the words
# changed, so exact matching cannot work. Print the pair, print what is on one side only,
# and let the reader judge - the same posture as SECTION HEADERS vs their blocks.
#
# DIRECTION IS NOT STABLE. Sometimes the letter is right and the resume wrong, sometimes
# the reverse. Nothing here assumes which side is canonical, and the section's own closing
# prompt says so.
#
# NOTHING IS PRINTED BELOW THE FLOOR. A derived line with no plausible source bullet is a
# different finding (an unsupported claim), and inventing a pair for it would train the
# reader to skim the section.
# ---------------------------------------------------------------------------

# Overlap of a derived line's content words with a bullet's, as a fraction of the smaller set.
# Below this, no bullet is offered as the source.
PAIR_FLOOR = 0.30
# Two shared content words is coincidence, not derivation - a Core Skills entry that names an
# employer pairs with any bullet naming the same one on that strength alone below this floor.
PAIR_MIN_SHARED = 3
# Per-side word list length. The pair is the finding; an exhaustive diff is not.
PAIR_WORDS_CAP = 10
# A derived line needs enough content to be worth pairing; a bullet needs enough to be a
# plausible source. Counted in content words, not raw tokens: a bare date range is five
# tokens and would otherwise pair with a whole summary sentence on the year alone.
PAIR_MIN_DERIVED_WORDS = 3
PAIR_MIN_CONTENT = 5
# The report is pasted whole into every review; an uncapped run would double its length.
PAIR_CAP = 8

DERIVED_HEADER_RE = re.compile(
    r"^(professional summary|summary|profile|core skills|key skills|skills)\b", re.I)
SUMMARY_HEADER_RE = re.compile(r"^(professional summary|summary|profile)\b", re.I)
# Sections that make no achievement claims, so nothing in them can be a source bullet.
NON_SOURCE_HEADER_RE = re.compile(
    r"^(education|certification|training|referee|reference|interest|contact|career break)", re.I)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[\"'(\[]?[A-Z0-9])")
VALEDICTION_RE = re.compile(r"^\s*(regards|sincerely|yours|kind regards|best)\b", re.I)


def word_stem(word: str) -> str:
    """Plural-only stemming, deliberately not a general stemmer.

    "service"/"services" and "solution"/"solutions" differing is noise, not a finding, and
    it would fill every printed word set. Verb inflection is left alone on purpose: a crude
    -ed/-ing stripper yields stems ("manag", "migrat") a reader cannot read back to a word,
    and this section's whole output is words a reader reads.
    """
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def content_words(text: str, stopwords: set) -> dict:
    """{stem: surface form} for the text, stop-listed. Reuses normalise_words()."""
    out = {}
    for run in normalise_words(text):
        for w in run:
            if w in stopwords or len(w) < 2:
                continue
            out.setdefault(word_stem(w), w)
    return out


def split_sentences(text: str) -> list:
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]


def derived_lines(resume_text: str, letter_body: str) -> list:
    """(label, line) for every line that compresses something else.

    Resume: each sentence of the Professional Summary paragraph, and every Core Skills
    item. The summary is split by sentence rather than paired whole because a paragraph
    derives from many bullets at once, so a whole-paragraph pairing scores below any floor.

    Letter: the first sentence of each body paragraph - the topic sentence. Pass
    `claim_text()` output in; the header block should already be gone.
    """
    out = []
    for header, items in section_blocks(resume_text):
        head = header.strip()
        if not DERIVED_HEADER_RE.match(head):
            continue
        for item in items:
            if SUMMARY_HEADER_RE.match(head):
                out.extend((head, s) for s in split_sentences(item))
            else:
                out.append((head, item))
    for para in re.split(r"\n\s*\n", letter_body or ""):
        para = " ".join(row.strip() for row in para.splitlines() if row.strip())
        if not para or para.startswith(("#", ">", "|")):
            continue
        if VALEDICTION_RE.match(para):
            break
        sentences = split_sentences(para)
        if sentences:
            out.append(("Letter topic sentence", sentences[0]))
    return out


def source_bullets(resume_text: str) -> list:
    """The resume's experience-section bullets, from the same section_blocks() call.

    Everything that is not a derived-line section and not a non-claiming section
    (education, certifications) counts - which is how a personal-projects block stays in.
    """
    out = []
    for header, items in section_blocks(resume_text):
        head = header.strip()
        if DERIVED_HEADER_RE.match(head) or NON_SOURCE_HEADER_RE.match(head):
            continue
        out.extend(items)
    return out


def best_source(line: str, bullets: list, stopwords: set) -> tuple:
    """(score, bullet, only_in_line, only_in_bullet) for the single best-scoring bullet.

    Score is shared content words over the smaller of the two sets, so a short Core Skills
    entry is not penalised for pairing with a long bullet. Returns (0.0, "", [], []) when
    nothing clears PAIR_FLOOR.
    """
    a = content_words(line, stopwords)
    if len(a) < PAIR_MIN_DERIVED_WORDS:
        return 0.0, "", [], []
    best = (0.0, "", {}, {})
    for bullet in bullets:
        b = content_words(bullet, stopwords)
        if len(b) < PAIR_MIN_CONTENT:
            continue
        shared = set(a) & set(b)
        if len(shared) < PAIR_MIN_SHARED:
            continue
        score = len(shared) / min(len(a), len(b))
        if score > best[0]:
            best = (score, bullet, a, b)
    if best[0] < PAIR_FLOOR:
        return 0.0, "", [], []
    score, bullet, a, b = best
    only_a = sorted(a[s] for s in set(a) - set(b))
    only_b = sorted(b[s] for s in set(b) - set(a))
    return score, bullet, only_a, only_b


def locate_item(item: str, text: str) -> tuple:
    """Line number of a derived line or bullet, via locate() on its opening words.

    Narrowing widths because locate() matches within a single line: a summary sentence that
    starts mid-line in a wrapped paragraph has no six-word window on any one line. When even
    a two-word window fails, fall back to the paragraph's first line using unwrap_blocks() -
    the same joined view hits_in() uses, so there is one unwrapping implementation, not two.
    """
    runs = normalise_words(item)
    if not runs or not runs[0]:
        return 0, ""
    heads = [" ".join(runs[0][:width]) for width in (6, 4, 3, 2)]
    for phrase in heads:
        n, line = locate(phrase, text)
        if n:
            return n, line
    for start, _end, joined in unwrap_blocks(text):
        for run in normalise_words(joined):
            flat = " ".join(run)
            if any(p in flat for p in heads):
                return start, joined[:80]
    return 0, ""


def fmt_words(words: list) -> str:
    shown = ", ".join(words[:PAIR_WORDS_CAP])
    if len(words) > PAIR_WORDS_CAP:
        shown += ", +%d more" % (len(words) - PAIR_WORDS_CAP)
    return shown


def compression_pairs(resume_text: str, letter_body: str, stopwords: set) -> tuple:
    """(rows, clean, unpaired). A row is (label, line, bullet, only_line, only_bullet).

    Only pairs with content words on BOTH sides are rows: a derived line that merely drops
    words asserts nothing new, and printing it would cost five lines to say "faithful". Those
    are counted in `clean` instead, so a clean application costs one line and the reader
    still knows the check ran.
    """
    bullets = source_bullets(resume_text)
    rows, clean, unpaired = [], 0, 0
    for label, line in derived_lines(resume_text, letter_body):
        if len(content_words(line, stopwords)) < PAIR_MIN_DERIVED_WORDS:
            continue  # a bare skills token ("Advanced Excel") compresses nothing
        score, bullet, only_a, only_b = best_source(line, bullets, stopwords)
        if not bullet:
            unpaired += 1
            continue
        if only_a and only_b:
            rows.append((label, line, bullet, only_a, only_b))
        else:
            clean += 1
    return rows, clean, unpaired


def report_application(app_dir: str, cats: dict, spans: list, patterns_path: str,
                       facts_path: str = None) -> int:
    app = os.path.basename(app_dir.rstrip("/"))
    docs = outgoing_docs(app_dir)
    print("MECHANICAL CHECKS - %s" % app)
    print("scope: this application only (--corpus for the cross-application sweep)")
    if not docs:
        print("\n  no Resume/CoverLetter documents found - nothing to check")
        return 1

    print_input_stamp(patterns_path, docs + [posting_path(app_dir), facts_path])

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

    print("\nBODY vs COMPRESSION - the derived line beside the bullet it compresses")
    print("  A summary sentence, a Core Skills entry and a letter's topic sentence each")
    print("  generalise bullets written elsewhere. Printed per pair: the derived line, its")
    print("  best-matching experience bullet, then the content words on ONE side only")
    print("  (+line / +bullet). A pair with nothing one-sided is counted, not printed.")
    resume_text = letter_text = letter_body = ""
    for path in docs:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if "resume" in os.path.basename(path).lower():
            resume_text = text
        else:
            # The body drives the pairing; line numbers are reported against the whole
            # file, because claim_text() has already dropped the header block and an
            # offset into the remainder would send the reader to the wrong line.
            letter_text, letter_body = text, claim_text(path, text)
    if not resume_text:
        print("  no resume found - nothing to pair against")
    elif not os.path.isfile(STOPLIST):
        print("  MISSING %s - the check cannot run without its noise floor"
              % os.path.basename(STOPLIST))
    else:
        stopwords, _phrases = load_stoplist(STOPLIST)
        rows, clean, unpaired = compression_pairs(resume_text, letter_body, stopwords)
        for label, line, bullet, only_a, only_b in rows[:PAIR_CAP]:
            ln, _ = locate_item(line, letter_text if label == "Letter topic sentence"
                                else resume_text)
            bn, _ = locate_item(bullet, resume_text)
            src = "Letter" if label == "Letter topic sentence" else "Resume"
            print("  %s  [%s L%d]" % (label, src, ln))
            print("      line    %s" % line[:88])
            print("      bullet  %s   (Resume L%d)" % (bullet[:80], bn))
            print("      +line   %s" % fmt_words(only_a))
            print("      +bullet %s" % fmt_words(only_b))
        if len(rows) > PAIR_CAP:
            print("      ... %d more differing pair(s) not shown (cap %d)"
                  % (len(rows) - PAIR_CAP, PAIR_CAP))
        print("  %d pair(s) matched cleanly; %d derived line(s) had no source bullet above"
              " the overlap floor" % (clean, unpaired))
    print("  Ask of each pair: does the derived line assert something its bullet does not?")
    print("  DIRECTION IS NOT STABLE - the bullet is the wrong side as often as the line is,")
    print("  so settle which side the facts file licenses before changing either. An")
    print("  unpaired line is a different finding - a claim with no bullet under it.")

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
        # The offset comes back with the body because the line numbers printed below are
        # reported against the WHOLE file - a letter's header block carries the role title
        # and company name verbatim in its `Re:` line, and re-locating there would anchor
        # this section to the header, the exact contamination dropping the block prevents.
        splits = []
        for path in docs:
            with open(path, encoding="utf-8") as fh:
                splits.append(claim_split(path, fh.read()))
        with open(facts_path, encoding="utf-8") as fh:
            facts_text = fh.read()
        stopwords, phrases = load_stoplist(STOPLIST)
        found = ad_vocabulary(ad_text, [body for _offset, body in splits],
                              facts_text, stopwords, phrases)
        if not found:
            print("  clean - every phrase shared with the ad also appears in the facts file")
        else:
            print("  %d phrase(s) in the ad AND the documents, absent from the facts file:"
                  % len(found))
            for phrase in found[:AD_VOCAB_CAP]:
                where = []
                for path, (offset, body) in zip(docs, splits):
                    n, line = locate(phrase, body)
                    if n:
                        n += offset
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


def report_corpus(root: str, cats: dict, patterns_path: str, facts_path: str = None) -> int:
    print("CORPUS SWEEP - every Resume/CoverLetter document under %s" % root)
    print("This is the deliberate cross-application pass. Say so in your report.\n")
    print_input_stamp(patterns_path, [facts_path] if facts_path else [])
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
        return report_corpus(args.corpus, cats, args.patterns, args.facts)
    if not args.app_dir:
        ap.error("give an application directory, or --corpus ROOT")
    if not os.path.isdir(args.app_dir):
        sys.stderr.write("not a directory: %s\n" % args.app_dir)
        return 2
    return report_application(args.app_dir, cats, canonical_spans(args.facts), args.patterns,
                              args.facts)


if __name__ == "__main__":
    sys.exit(main())
