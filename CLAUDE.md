<!-- source-hash: 3ce8e4126eb9 CLAUDE.md -->
# Project Instructions

Rules only. The reasoning behind them, and the incidents that produced them, are in
`docs/Conventions_Rationale.md` — read that if a rule looks arbitrary or you're tempted to make
an exception, not on every run.

**Applies to:** orchestrator (main session). Every other section carries its own audience tag.
Most sections are orchestrator-only; a subagent brief that pastes one of those into a role that
can't act on it is wasting the brief, not scoping it.

Three rule files live outside this file and **must be read before the work they govern**:

- `docs/Writing_Style.md` — before drafting or revising any resume, cover letter, or
  screening-question answer. Governs every outgoing document; there is no default that
  substitutes for it.
- `docs/Recon_Checklist.md` — before starting company recon. Includes the recon-reuse rules.
- `docs/Review_Checklist.md` — before reviewing any drafted resume or cover letter. Holds the
  subtractive accretion diff and the verdict rules.

When briefing a subagent for drafting, recon or review, name the relevant file in the brief. A
brief that omits the pointer loses those rules silently. Spawning the agent by its
`.claude/agents/` type carries the pointer structurally and is the preferred route.

## Document QA

**Applies to:** whichever role is presenting — orchestrator normally; drafting and review need to
know it exists.

Runs inline, in whichever session/agent is doing the presenting — never a separate spawn.
Before presenting a finished resume, cover letter, or artifact:

- Confirm the saved job posting holds the ad's **verbatim** text, not a summary. If it's a
  summary, re-fetch and replace it *before* reviewing — see "Job posting capture" below. A
  review against a paraphrase produces specific, confident, wrong findings.
- Check every `[link text](url)` stays atomic on one line — bracketed text split across a line
  wrap silently breaks the link with no visible error. Re-check after any edit near a link.
- Check the draft against `docs/Writing_Style.md`.

## Mechanical checks — the orchestrator runs them, always

**Applies to:** orchestrator. Drafting and review both depend on it and **neither can run it**:
their tool allowlists have no Bash, deliberately, and the reviewer's `Read`-only limit is
what enforces findings-never-edits. Don't add Bash to either to save a round-trip.

**Run `python3 scripts/mechanical_checks.py <application-dir>` and paste its output into the
brief** — before every review spawn or message to a running reviewer, and again for drafting
after it applies a round of findings, which is when the report catches what the fixes just
introduced. Use `--corpus` only for a deliberate cross-application sweep.

**Paste the whole report, never a head of it.** A truncated report has already cost a review to
a phantom bug (`docs/Conventions_Rationale.md`) — and if your subagents cannot run pattern
searches themselves, the pasted report is the only pattern search they have.

It reports banned-string hits with line numbers, the cover letter's header block, link and
bracketed-token atomicity, every duration phrase beside its canonical span from the fact
library, and every section header beside its block contents.

Two reasons this is the orchestrator's job rather than a checklist item for the reviewer: **a
self-reported check is not a check** (five instances on one real corpus, all failing the same
way — `docs/Conventions_Rationale.md`), and **it costs the reviewer zero tool calls instead of
eight**.

This section is the canonical statement of the mechanical-checks rule; the copies in
`docs/Review_Checklist.md`, `.claude/agents/drafting.md` and `.claude/agents/review.md` are
deliberate role-facing duplicates — keep them in sync with this one.

Patterns live in `scripts/banned_patterns.txt` and nowhere else; the comments in that file hold
the rationale, and **a hit is not automatically a defect** — read the pattern's comment before
adjudicating one. After changing the pattern file or the script, run
`python3 scripts/test_mechanical_checks.py`: a pattern added without a probe fails that suite
by design.

## Tests

**Applies to:** orchestrator. Subagents have no Bash and cannot run these.

Run the test suite after changing anything in `scripts/`, and before committing such a change —
not after application work; no test touches application documents. **Adding a script is a
two-file change: the script and its `test_<name>.py`.**

## Job posting capture — verbatim, always

**Applies to:** orchestrator — capture is the orchestrator's job, never a subagent's.

The saved job posting holds the **ad's own words**. Paraphrasing preserves the topics and
discards the vocabulary, and the vocabulary is what both the ATS keyword screen and the
fact-matching step run on. A summary doesn't just lose detail; it manufactures gaps.

Beware fetch layers that summarise: a model-mediated page fetch *is* a paraphrase layer even
when prompted for verbatim output. Prefer a structural extraction with no model involved
wherever the board server-renders the ad; where a model-mediated fetch is the only option, check
manually that nothing was compressed.

**On first capture:**

- Save the responsibilities, requirements, and "about the role" sections **verbatim**, quoted
  or block-quoted, under a heading that says so. Don't compress bullets, don't merge them,
  don't substitute synonyms, don't drop a requirement because it looks boilerplate.
- Always record the **source URL** and the fetch date. A posting without a URL cannot be
  re-captured later, and job ads expire within weeks.
- A short summary on top is fine and useful. It goes **above** the verbatim block, clearly
  labelled, never instead of it.
- Keep screening questions verbatim too — their exact wording drives the answer.

**On review, re-capture.** If asked to review, revise, or QA a resume or cover letter for a
role whose saved posting is a summary, re-fetch the original posting and replace the summary
before reviewing. Do this without being asked. If the URL is dead, say so plainly and note in
the application's status file that the review ran against a summary.

## Status files are status, not changelogs

**Applies to:** orchestrator.

An application's status file holds four things and nothing else: the current status line, gap
notes, open items to verify before submitting, and the final screening-question answers. Cap it
(a few hundred words) and **move history out** — review rounds, drafting rationale, superseded
gap analysis — to a sibling decision log with no cap, read only when the history is actually
needed. An uncapped status file becomes an append-only changelog that every review, handoff and
revisit re-reads in full to find the three lines that are current.

Questions about the **candidate's own experience** go to a single shared open-questions file at
the project root, referenced from status files by number — those recur across applications, and
one living in a single status file is the failure the shared file exists to prevent.

## Drafting resumes and cover letters from a fact library

**Applies to:** drafting. The full version is `.claude/agents/drafting.md` plus
`docs/Writing_Style.md`; this section is the orchestrator's summary of what it delegates.

Read `docs/Writing_Style.md` first.

Don't start a tailored resume from any single master resume and trim it down. Build up instead
from a fact library — a pre-distilled, tagged collection of atomic, fact-checked achievement
entries ("vignettes"). Select the vignettes whose tags match the job ad's stated requirements,
write the summary around what actually matched, and don't paraphrase away the concrete
specifics (numbers, named clients, named platforms) that make a vignette verifiable. Prioritise
match to the ad first, token usage second — **read the whole fact library each time.** Selective
reading is how a corpus under-claims, and later drafts in a batch have measurably drifted into
re-using the previous draft's selection (`docs/Conventions_Rationale.md`). A fresh full scan per
ad is the point of respawning the drafting agent, not a cost of it.

**Unconfirmed facts live outside the library**, in a shared open-questions file. The library
holds only fact-checked material, and states that guarantee inside itself. Don't use an open
question until the candidate answers it, and never write a new one into the library: one
unconfirmed entry voids the trust guarantee for the whole file. The open-questions file is also
**the only place open items live**; other files keep pointers. Parallel open-item lists diverge
— on the corpus this toolkit comes from, four parallel lists had already diverged badly before
the rule existed.

When the candidate corrects or adds a fact in conversation, add it to the library as a new or
amended vignette immediately — don't let it live only in one application's status file, or the
next application will under-state the same fact and need the same correction twice.

## Company recon

### Spawning recon — **applies to:** orchestrator

Run recon automatically the first time a job URL or posting is provided for a new company; that
counts as "asked" for the web-search rule below. Delegate to the `recon` agent type on a
small/fast model at low reasoning effort, and name `docs/Recon_Checklist.md` in the brief. Its
tool access is research (WebFetch/WebSearch/Read) plus writing only to that company's
`Company_Context.md` — it should never touch resume, cover-letter, or status files. If your
`Write` allowlist can't be scoped by path, state that limit as prose in the agent definition.

### Doing recon — **applies to:** recon agent

Follow `docs/Recon_Checklist.md`. It holds the topic list and the reuse rules, and it lives
only in that file — there is no summary of it here.

## Workflow order

Spawn specs are the orchestrator's; the behaviour rules below them belong to the roles named.

### Spawn specs — **applies to:** orchestrator

- **Model/effort, always** (batch or single-application, including re-review passes): recon =
  small/fast model, low effort; drafting = mid-tier model, medium effort; review = strongest
  model, high effort. Spawning by agent type pins this in frontmatter; a generic spawn with a
  prose brief does not, so name the type.
- **Retire the drafting agent after ONE new application, or at ~200K tokens, whichever comes
  first.** The budget counts **only new applications**, because that is the work where a stale
  instance actually does damage:

  ```
  COUNTS    one first-draft pair (resume + cover letter) for one application
  FREE      a revision pass applying one round of reviewer findings
  FREE      status-file / decision-log writes
  FREE      a new or amended fact-library entry
  FREE      a cross-application sweep touching ≤3 applications
  ```

  **Maximum ONE new application per instance, and one application per brief.** The second new
  application starts on a fresh agent, never the old one — and a single brief must never cover
  two applications. The failure mode is **per-brief**, not per-instance: one brief covering two
  applications measurably matched the second ad against the first draft's selection, costing two
  under-claims, and the per-brief saving is given up deliberately — a known bounded cost traded
  against an unbounded silent one (full narrative in `docs/Conventions_Rationale.md`). **This
  applies to drafting only** — batching a review across applications is cheaper and carries no
  measured quality cost.

  **Reuse the same instance freely for revisions.** Applying review findings is not budgeted at
  all. A single instance may legitimately do one new application and then six rounds of
  revisions on it.

  **The exemption's reason: a well-structured review externalises the context a reviser needs.**
  Measured on a real corpus — a cold instance applied 32 findings across two applications it had
  not drafted, cleanly (`docs/Conventions_Rationale.md`). Stated the old way ("the instance
  holds the drafting context"), the exemption would eventually be claimed for a badly-structured
  review, where it does not hold.

  **The ~200K token trigger overrides both.** Retire on crossing roughly 200K subagent tokens
  even mid-budget, and even if every remaining item is a revision — transcript growth is real,
  is not offset, and has cost missed vignettes (series in `docs/Conventions_Rationale.md`).

  Retire gracefully, never mid-application: let the work in flight finish, ask the outgoing
  instance for its final queue echo and its cross-application observations, then spawn a fresh
  drafting agent briefed with the remaining queue, that echo, and the observations. The fresh
  instance re-scans the fact library per ad — that is a feature of the respawn, not a cost of it.

  **This budget is drafting-only.** See the review rule immediately below for why the same
  instrument is wrong there.
- **The review agent is not budgeted. Retire it at batch boundaries, not at a unit count** — and
  early on an observed trigger: report quality visibly dropping, or **a single review crossing
  ~200K subagent tokens**, which is worth a respawn on cost alone. Reasoning, re-checked against
  a full six-application pass:
  - *Blast radius* is much smaller than drafting's. The reviewer's allowlist is `Read` alone, so
    an interrupted review costs one regenerable report; an interrupted drafting instance costs
    unwritten edits.
  - *Transcript growth is real and is not offset*, and a cold replacement re-briefed from the
    tally table has produced the strongest review of a pass at ~40% of the warm cost —
    cross-application findings included (series and detail in `docs/Conventions_Rationale.md`).
  - So the compounding state is held by **the table, not the instance**. Don't keep a reviewer
    alive to preserve something a file already holds.
- **Write the reviewer's cross-application tallies into a tally table in a shared batch status
  file after every returned review; put the review's *narrative* in a separate review log.**
  This is the orchestrator's job, not the reviewer's — the reviewer has no Write access by
  design. **The tally table is the load-bearing rule of the two**, not a backup: a respawn is
  cheap exactly to the degree the tallies are current, and the table is the only thing that
  survives when the orchestrator session dies alongside the agent. Write it completely enough
  that a replacement briefed from nothing else still knows what is settled. **If you find
  yourself writing a paragraph of review reasoning into the status file, it belongs in the
  review log.** Keep the status file small; move history, never compress it.
- **If an agent reports stopping on an instruction you have no record of sending**, treat an
  external interrupt as the first hypothesis — a CLI stop reaches in-flight subagents and never
  appears in your own sent-message log. Ask the user whether they stopped it, then re-issue the
  outstanding queue explicitly. Do not diagnose the agent as unreliable before ruling that out.

### Behaviour rules

- **Recon before drafting** (*orchestrator*). Don't generate the resume or cover letter until
  `Company_Context.md` is complete — recon findings (a real hiring-manager name, an ad-relevant
  company detail, a red flag about the listing) can and should change what the documents say. If
  recon is running as a background subagent, wait for its completion notification rather than
  drafting in parallel.
- **HR/hiring-manager review after the first draft** (*orchestrator*), automatically, before
  presenting the application as ready — don't wait to be asked. Act only on concrete,
  non-fabricating suggestions; log both what was acted on and what wasn't.
- **The review agent reports findings, it never edits outgoing documents** (*review*). No
  Edit/Write tool access on a review spawn — the `tools: Read` allowlist in
  `.claude/agents/review.md` is the enforcement, so don't add Write to it. Findings go back to
  the drafting agent, which applies them so fact-fidelity checking stays in one place. What the
  review checks is in **`docs/Review_Checklist.md`**, which the reviewer must read before
  reviewing anything, the same way drafting must read `docs/Writing_Style.md`.
- **A reviewer recommendation to skip is never resolved unilaterally** (*orchestrator*) — log
  it and flag it for the candidate's decision.

## Web search

**Applies to:** all roles.

Don't run web searches (job boards, live postings, etc.) on your own initiative. Wait to be
asked, or for a job ad URL/text to be provided directly. Recon is the one exception: its
searching is pre-authorised by `docs/Recon_Checklist.md` for the company it was handed, and only
that company.

## Batch processing multiple applications (3+ job URLs in one request)

**Applies to:** orchestrator.

**Process in sub-batches of 3, never the whole list at once** — and within a sub-batch, one
drafting agent and one brief per application (see the drafting budget above). Keep a single
shared batch status file, and **check it first** on receiving a batch — if it shows a pass
already in flight, resume from the first incomplete row rather than starting over.
