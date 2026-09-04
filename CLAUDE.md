<!-- source-hash: c1b613a67066 CLAUDE.md -->
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

## Working by conversation

**Applies to:** orchestrator.

The user of this repository may never open a terminal: they type sentences, and this section
maps what they *mean* to what you run. **It is an intent table, not a string table** — the
paraphrases in each row show the pattern, and the user's wording is not constrained. One rule
above the table: **if the intent is unclear, ask exactly one question.** Never guess a company
or role name into a folder, and never guess a filename field.

| The user means | What you do |
|---|---|
| *Set up my fact library* — "set up my fact library from the template", "start my library", "I want to build my fact file" | Copy `Fact_Library_TEMPLATE.md` to `Fact_Library.md` and `Open_Questions_TEMPLATE.md` to `Open_Questions.md`, both at the project root, if they do not exist. Then ask, in one message, for the identity block: the name as it should appear on a cover letter, the contact line, and the `Name for filenames:` value (letters and digits, one underscore between name parts). Write them in, replacing the `>>> REPLACE` markers. |
| *Propose vignettes* — "propose vignettes from this", "here is my old resume", "I uploaded my old resumes; move them into sources/ and propose vignettes" | If document files (PDF, text, Word) are lying loose at the repository root, move them into `sources/` first — GitHub's upload lands files wherever the user was standing, usually the root. Read the pasted text or every file under `sources/` (PDF and text read directly; a `.docx` cannot be read here — ask the user to re-upload it as PDF via Google Docs). Propose candidate entries in the template's shape, each with the question that would bound it. Write into `Fact_Library.md` **only what the user confirms**; park anything unsure in `Open_Questions.md`. |
| *New application* — "start a new application for Northwind, Operations Coordinator", "I want to apply for X at Y", "another one for Acme" | Read the first `Name for filenames:` line in `Fact_Library.md`; if it still carries `>>> REPLACE`, ask for it first. Derive CamelCase company and role fields, run `python3 scripts/new_application.py --candidate <name> --company <Co> --role <Role>` (with `--abbrev` when the company name is long), and echo the folder name. |
| *This is the ad* — "this is the ad, save it verbatim", "here's the job posting" | Write the pasted text into that folder's `posting.md` under **Verbatim ad text**, unchanged. No summary in its place. |
| *Research, draft, review* — "research the company, then draft, then review", "write the resume and cover letter" | The workflow-order rules below: recon, then drafting, then review, with the mechanical checks pasted into every review brief. |
| *Run the checks* — "run the checks", "lint it", "is it clean?" | `python3 scripts/mechanical_checks.py Applications/<folder> --facts Fact_Library.md`. Report the whole output, fix what drafting can fix, and say what remains. |
| *Commit and push* — "commit and push", "save it to GitHub", "push it" | Commit the application folder and any library edits, then push. **In a claude.ai/code session the push lands on the session's own `claude/…` branch, never on `main`** — the session is pinned to it. Say so in one line, every time, and tell the user the two clicks that follow: *press **Create PR** on the bar above the message box, then on github.com press **Merge pull request** and then **Confirm merge***. In a terminal session with no such branch, push to the repository's default branch: this is a private single-user repository with no reviewer to make a branch for. |
| *Update the toolkit* — "update the toolkit from github.com/Ian-Lo/application-doc-toolkit", "get the latest toolkit", "is there a newer version?" | `python3 scripts/update_toolkit.py`. It fetches the public repository and replaces the toolkit's own files wholesale (`CLAUDE.md`, `README.md`, `LICENSE`, `.gitignore`, `.claude/`, `docs/`, `scripts/`, the two templates), runs the shipped test suites, and prints a diff summary plus the README's *What changed* entries this copy did not have. Report those entries to the user in full. An entry marked `LIBRARY EDIT:` names a change `Fact_Library.md` needs — **propose the edit and wait for a yes**; never make it silently. The script never touches `Fact_Library.md`, `Open_Questions.md`, `Applications/` or `sources/`. If it refuses because a toolkit file has uncommitted changes, do *commit and push* first and run it again. Afterwards the user says *commit and push* as usual. |
| *PDF / printable / Word version* | There is no script for this. Point at the Google Docs route: `docs/Getting_Started_CLI.md` section 8 in a terminal session (the `.md` is on the user's disk; upload it to Drive, open with Google Docs, export PDF or DOCX), or `docs/Getting_Started.md` section 6 in a claude.ai/code session (download the `.md` from github.com first). |

Two standing rules that hold whether or not the user says the sentence:

- **Always run the mechanical checks before presenting any draft as ready**, asked or not.
- **Never write above the fence in `Fact_Library.md` without a fact the user confirmed in this
  conversation.** A proposal is not a confirmation.

`Fact_Library.md`, `Open_Questions.md` and `sources/` are the user's personal data. The
repository stays private; nothing in it is published anywhere by this workflow.

**Two kinds of file, and the split is load-bearing.** Personal data lives only at the root
(`Fact_Library.md`, `Open_Questions.md`) and under `Applications/` and `sources/`; toolkit
files live only under the paths the update replaces (`CLAUDE.md`, `README.md`, `LICENSE`,
`.gitignore`, `.claude/`, `docs/`, `scripts/`, the two templates). `scripts/update_toolkit.py`
holds both lists as code and its test suite holds them disjoint. **No rule in this file or in
the guide may ever put user data under `docs/`, `scripts/` or `.claude/`**, and the user is not
meant to edit toolkit files: an update overwrites them (why: `docs/Conventions_Rationale.md`).

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

**Run `python3 scripts/mechanical_checks.py <application-dir> --facts Fact_Library.md` and paste
its output into the brief** — before every review spawn or message to a running reviewer, and
again for drafting after it applies a round of findings, which is when the report catches what
the fixes just introduced. Use `--corpus` only for a deliberate cross-application sweep.

**Paste the whole report, never a head of it.** A truncated report has already cost a review to
a phantom bug (`docs/Conventions_Rationale.md`) — and if your subagents cannot run pattern
searches themselves, the pasted report is the only pattern search they have.

**Generate it in the same breath as the paste. A report is stale the moment either input
changes** — the documents, or `scripts/banned_patterns.txt`. On the source corpus a report
generated early in a pass was pasted into a review brief later in the same pass, after a new
pattern had been installed in between: it reported `clean` on a string the live pattern matches,
and the reviewer opened its report by saying the brief could not be trusted. The orchestrator
holds both inputs and is the only role that can see them diverge. **Never carry a report forward
across a pattern-file edit; re-run it.**

**The same asymmetry, generalised: a subagent's file read is a snapshot, and a long review
outlives it. When an agent reports that a file does not contain something, check the file before
acting.** On the source corpus, a parallel session committed a batch of answered questions into
the fact library while two reviews were in flight; both had read the file at spawn, and one
asserted as a blocking finding that the answers had not been written, instructing that drafting
stop. The content was on disk the whole time. A subagent cannot detect this and should not be
asked to — re-reading a large library at the end of every review is not affordable — and
messaging in-flight agents about the change is worth doing but is not a control: both were
messaged, and neither acted on it before finishing. A confidently-argued negative is the shape
most likely to trigger expensive remediation, which is exactly why it earns the one status check
and one search that settle it.

It reports banned-string hits with line numbers, the cover letter's header block, link and
bracketed-token atomicity, every duration phrase beside its canonical span from the fact
library, every section header beside its block contents, and — when `--facts` names the
library — **ad vocabulary the library does not license**: phrases in both the saved posting
and the outgoing documents but absent from the library, which predicted 4 of 10 over-claims
when measured on the source corpus. That last one is warn-style: a hit is a question for the
reviewer, not a defect, and proper nouns from recon show up in it routinely.

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
two-file change: the script and its `test_<name>.py`.** `scripts/update_toolkit.py` runs every
`scripts/test_*.py` after an update and rolls the update back if one fails, so a shipped suite
must pass in a copy that holds no application work.

## Application file structure

**Applies to:** orchestrator; the filename convention is drafting's and is repeated in
`.claude/agents/drafting.md`.

For every job application:

```
Applications/YYYY-MM-DD_Company_RoleTitle/
    posting.md                                       (saved ad content, source URL, screening questions)
    <candidate>_Resume_YYMMDD_Company_Role.md
    <candidate>_CoverLetter_YYMMDD_Company_Role.md
    status.md                                        (status, gap notes, things to verify before submitting)
    decisions.md                                     (optional; dated updates once they accumulate)
    Company_Context.md                               (written by recon; symlinked when the company recurs)
```

Resume/cover-letter filename field order is fixed:
**[candidate]_[Resume|CoverLetter]_[date YYMMDD]_[company, abbreviated]_[role]**, e.g.
`Sam_Okafor_Resume_260302_Northwind_OperationsCoordinator.md`. The candidate field comes from
the `Name for filenames:` line in `Fact_Library.md`; company and role are CamelCase with no
spaces or underscores inside the field, because the underscore is the field separator.

**Scaffold with `python3 scripts/new_application.py --candidate <name> --company <Co> --role
<Role> [--abbrev <Co>]`**, never by hand — it gets both date formats right (the folder takes
the four-digit year, the document a two-digit one) and refuses a role containing a space or
underscore, which would silently shift every filename field after it. It creates `posting.md`
and `status.md` seeds plus the two correctly-named empty documents, and deliberately does
**not** create `Company_Context.md` or `decisions.md`; where recon for that company already
exists it prints the `ln -s` command and leaves the reuse-vs-stale judgement to you.

`Fact_Library.md`, `Open_Questions.md` and `sources/` stay at the project root, shared across
applications — never duplicated per-folder.

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

**The fact library is `Fact_Library.md` at the project root** — one file, built from
`Fact_Library_TEMPLATE.md` by the procedure in `docs/Fact_Library_Guide.md`. Its identity
block is the source of the cover-letter header and of the candidate field in every filename.

Don't start a tailored resume from any single master resume and trim it down. Build up instead
from the fact library — a pre-distilled, tagged collection of atomic, fact-checked achievement
entries ("vignettes"). Select the vignettes whose tags match the job ad's stated requirements,
write the summary around what actually matched, and don't paraphrase away the concrete
specifics (numbers, named clients, named platforms) that make a vignette verifiable. Prioritise
match to the ad first, token usage second — **read the whole fact library each time.** Selective
reading is how a corpus under-claims, and later drafts in a batch have measurably drifted into
re-using the previous draft's selection (`docs/Conventions_Rationale.md`). A fresh full scan per
ad is the point of respawning the drafting agent, not a cost of it.

**Unconfirmed facts live outside the library**, in `Open_Questions.md` at the project root. The library
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
- **If the agent types are not registered** — the spawn fails with *Agent type 'recon' not
  found*, which a claude.ai/code session has done (2026-09-04) — spawn generically and carry
  into the brief everything the definition in `.claude/agents/` would have pinned: the model
  and effort, the `docs/` file the role must read first, and the tool limits. Tell the user in
  one line that this happened. The limit that matters most is the reviewer's: **a generic
  review spawn gets no Edit or Write tool**, and the brief says it reports findings and never
  edits — without the registered type, that sentence is the only enforcement there is.
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
  `.claude/agents/review.md` is the enforcement, so don't add Write to it (and where the type
  does not register, the spawn's own tool list is — see the spawn specs). Findings go back to
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
