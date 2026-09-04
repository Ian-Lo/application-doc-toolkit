<!-- source-hash: eb7877818bab docs/Conventions_Rationale.md -->
# Why the conventions exist

Background for the rules in `CLAUDE.md`. Read this when a rule looks arbitrary or you're
tempted to make an exception — not on every run. Each entry records the incident, on the real
application corpus this toolkit was extracted from, that produced the rule — so the rule can be
revised knowingly rather than eroded by accident. Company names, dates and file paths specific
to that corpus have been removed; the shapes of the failures have not.

## Job posting capture must be verbatim

A saved job posting was once a paraphrase. Two full persona-review rounds scored the
application against it, and both recorded a **real gap** in an area the candidate had genuinely
built and could evidence.

The live ad asked for several named practices; the paraphrase had flattened them into one
generic phrase. The false gap then propagated into the cover letter as a written concession
against a *required* qualification.

The lesson: a summary preserves the topics and discards the vocabulary, and the vocabulary is
what both the ATS keyword screen and the fact-matching step run on. A summary doesn't just
lose detail; it manufactures gaps.

## Don't fetch ads through a summarising layer

A model-mediated page fetch runs the page through a summarising model, so it *is* a paraphrase
layer. Tested on a live ad with an explicit "reproduce verbatim" prompt: it returned a
re-summarised version with selective quote marks, which is worse than an obvious summary
because the quote marks imply fidelity that isn't there.

Where a job board server-renders the full ad, a structural extractor with no model involved is
the right capture tool. Postings with no structural route still need the model-mediated fetch,
hence the manual compression check in `CLAUDE.md`'s capture rules.

## Markdown links break silently

A `[link text](url)` whose bracketed text is split across a line wrap stops being a link, with
no visible error in the source and no error at render time. This has broken real links in
outgoing documents more than once, which is why the QA step calls it out specifically.

## Status files are status, not changelogs

Status files had become append-only changelogs. One application's status file reached 6,209
words across 19 dated update sections, so every review, handoff, or revisit re-read all of it
to find the three lines that were current.

Splitting current state (the status file) from history (a sibling decision log) keeps the
routinely-read file small without discarding the reasoning trail, which has real value on
revisits and cold-call prep.

**Why a word cap needs mechanical enforcement.** The cap went unenforced at first, by which
point 51 of 64 files had breached it and the largest was over 3,000 words; the status files
collectively outweighed every rule and reference document in the project. A documented cap with
no check is what that looks like.

## Checklists live in `docs/`, not `CLAUDE.md`

`CLAUDE.md` is re-sent in full to every subagent, and a batch pipeline spawns four or more.
The writing-style and recon checklists are each used by exactly one agent, so holding them
inline meant every other agent paid for them.

The tradeoff accepted: an agent brief that forgets to point at the file loses those rules with
no error. Mitigated by making the read an explicit step in the workflow-order rules, and by
spawning agents by their `.claude/agents/` type, which carries the pointer structurally.

## A CLI stop reaches subagents, and the orchestrator can't see it

Deep into a nine-application batch, the drafting agent replied *"Per your instruction, I'm
stopping here"* and left two applications and a cross-application sweep undone. The review
agent sent a similar "Stopped. I've halted my review pass" shortly after. The coordinating
session searched its own sent messages, found no stop instruction in either case, and concluded
the agents had lost track of what they'd been told — context pressure at ~300K subagent tokens,
an agent backfilling a plausible justification. That diagnosis was written into the handoff
file and committed.

It was wrong. The user had pressed stop in the CLI. Both agents were reporting a real
interrupt, accurately.

The trap is structural, not a one-off: **a CLI stop propagates to in-flight subagents and never
appears in the orchestrator's record of messages it sent.** So the obvious verification —
"check whether I actually sent that" — returns the same answer for a truthful report of an
external interrupt as it does for an invented one. An orchestrator that treats "not in my log"
as proof of confabulation will reach the wrong conclusion every single time this happens.

Hence the rule in `CLAUDE.md` ("Workflow order" → spawn specs): an external interrupt is the
**first** hypothesis, ask the user, then re-issue the outstanding queue explicitly. The older
advice — cross-check the claimed instruction against the sent messages — is still worth doing;
it just isn't sufficient on its own.

Worth noting how close this came to hardening: the wrong cause was recorded in a handoff,
which is the file a cold session reads first, and it carried a general claim about persistent
subagents being untrustworthy. One more session and it would have been treated as settled.

## Why the orchestrator runs the mechanical checks, and pastes the whole report

Both halves of the rule in `CLAUDE.md`'s "Mechanical checks" section trace to measured failures
on the real corpus.

**The truncation incident.** The orchestrator once truncated the report, dropping a whole
section; the reviewer noticed the absence and spent part of its report asking whether the
script was broken and warning that a checklist step might be running unassisted across the
batch. The script was fine. A truncated report costs reviewer attention and invites a phantom
bug — hence "paste the whole report, never a head of it."

**Why the orchestrator and not the reviewer.** Two reasons, both measured:

- **A self-reported check is not a check.** Five times a mechanical check was reported as
  passed and was false on disk, every time in the same direction — run against the change just
  made rather than against the rule. Script output cannot be misreported.
- **It costs the reviewer zero tool calls instead of eight**, and every search result a
  subagent pulls in is re-sent on every later turn of that review.

## Why the drafting agent is budgeted, and why the budget changed

*Originally "retired after six work units", then "3 new applications". **Current rule: ONE new
application, revisions free, hard stop at ~200K tokens.** The earlier revisions are kept below
because each builds on its predecessor rather than discarding it — and because the 3 → 1 cut is
only legible against what 3 was chosen for.*

One drafting instance once carried an entire nine-application batch — 9 first drafts plus 3
review-and-fix rounds, ~300K+ subagent tokens. Three things support bounding an instance:

1. **Selection drift, which is measured.** High-value fact-library material was used
   inconsistently *within* a single batch — a strong piece of integration evidence appeared on
   one resume and was cut from the one ad in the batch that named that exact capability. That
   reads as each draft starting from the previous draft's selection rather than from the ad. A
   cold instance cannot inherit a selection it never made, so the respawn is a fix for this,
   not a cost.
2. **Interrupt blast radius.** An interrupt — from the user, a crash, a session ending — costs
   whatever undocumented state the instance was holding. Bounding the instance bounds the loss,
   whoever or whatever caused it.
3. **Transcript growth is real** even where its effects aren't proven. A respawn is cheap: the
   agent definition and two checklists reload from cold, and everything else the replacement
   needs already lives in files.

The counting rule is coarse on purpose. A precise budget the agent has to compute is a budget
it will get wrong; the number only has to be roughly right to do its job.

### Revised: 3 new applications, revisions free, hard stop at ~200K tokens

The flat unit budget priced a first draft and a revision pass identically. They are not alike,
and the three justifications above apply to them very unevenly:

- **Selection drift only threatens new applications.** A revision pass isn't selecting
  vignettes against a fresh ad; it is applying named findings to documents the instance already
  wrote. The drift argument — the strongest of the three — has no purchase there. Meanwhile the
  instance holds exactly the context a revision needs: why each vignette was chosen, and what
  was deliberately withheld. Respawning before a revision *loses* something; respawning before
  a new application *gains* something. A single budget covering both got the sign wrong in one
  direction.
- **So the budget now counts only what it was ever really about.** 3 new applications per
  instance, revisions unbudgeted, and the sub-batch size set to 3 to match — one sub-batch is
  one instance's allowance, which removes the arithmetic instead of asking an agent to track
  it.
- **The ~200K token trigger is promoted to a hard stop**, and it overrides the count in both
  directions — including on an instance doing nothing but free revisions. Per-unit spend on one
  instance ran 119K → 152K → 193K → 233K, and it was retired mid-budget on cost alone. Its
  replacement's first unit cost 116K and **found an unused vignette the warm instance had not
  reached for** — the clearest single measurement in this project that transcript growth costs
  output quality, not just money.

**Why 3 and not 4 or 6.** Partly that a smaller number is safer given the above, but mainly
that it makes the sub-batch, the drafting instance and the reviewer's first tally window the
same boundary. A mismatch — 6-unit instances inside 9-application batches — means retirement
lands mid-batch and has to be sequenced by hand every time.

### Revised again: ONE new application — the budget was counting the wrong unit

A later measurement corrected the budget's **unit**, not its reasoning. Everything above about
selection drift is right; what it got wrong is where drift happens.

**The old budget counted instances. The failure happens per brief.** One drafting instance was
given a single brief covering two applications — 2 of 3, comfortably inside the allowance,
retired well under the token trigger. The review found this anyway: the library was clearly
read, and the second ad was then matched against the first draft's selection rather than
freshly against the library. Two under-claims came out of it — one vignette placed in the
weaker of the two applications, another absent from both against the ad that named it.

**So the drift does not need a long transcript to appear.** It appears as soon as one context
holds two ads, which a multi-application allowance not only permits but invites. Setting the
maximum to one closes the instance count and the brief shape together; stating only "one per
instance" would leave the same hole, which is why the rule says **one application per brief**
in the same breath.

**What it costs, stated plainly, because it is not free.** The two-in-one-brief shape saved
roughly 11-13% of the whole-cycle per-application cost, and that saving is given up
deliberately. The trade is a known bounded cost against an unbounded silent one: an
under-claim that ships is a screening call nobody hears about, and this kind of corpus fails
in that direction at roughly 9:1.

**The evidence under-counts itself, which is the real argument.** Only the misses the review
*caught* are observable. A shared read that caused a miss the review did not spot leaves no
trace anywhere. "The backstop worked" is therefore the weakest available reassurance, because
a working backstop is the only outcome this kind of project is able to see.

**What did not change, and must not be cut with it.** Revisions stay free and unbudgeted. The
same pass measured a cold instance applying 19 findings across two applications, having
drafted neither, with none declined — so the earlier finding that revision is cheap for a cold
instance given a well-structured review held again. Cutting the revision exemption alongside
the count would turn a quality fix into a net loss.

**This is drafting-only.** The same amortisation on the *review* side carried no measured
quality cost — the reviewer checks written claims against their licensing sentence, which is a
lookup, where drafting *selects*, which is a search.

## Why the review agent is not budgeted, and its tallies are

The drafting budget prompted the obvious follow-up: should review get one too? Two things came
out of measuring it across a six-application review pass.

**No.** Cost per review grew (92K → 132K → 159K → 190K subagent tokens across four
applications) while findings got *sharper*, not blunter. Review 2 corrected review 1's own
undercount unprompted. Review 3 caught a false gap that had propagated from a scoped
fact-library caveat into a status file, a decision log and a live cover letter. Review 4 read a
decision log to establish that an earlier sweep had touched a sentence and fixed only its
symptom. Each of those findings requires holding several applications in view at once.

**But the compounding state was one interrupted session away from being lost**, which is the
real risk the question exposed — a durability problem, not a lifespan one. The tallies existed
only in the reviewer's transcript and the orchestrator's context. So the rule is: the
orchestrator writes them into the shared batch status file after every returned review.

### Reviewed at the end of the batch, as promised — and one half of it was wrong

The rule above was written after four reviews and said it would be re-checked with all six. The
sixth arrived by an unplanned route: the reviewer died to an API session limit mid-assignment,
and a **cold replacement** did the last application after being re-briefed from the tally
table. That is the experiment the original entry could not run.

**The "no budget" half holds. The "a respawn causes selection drift" half does not.**

| | predecessor (warm) | replacement (cold, briefed from the table) |
|---|---|---|
| subagent tokens per review | 92K → 132K → 159K → 190K → 218K | **86K** |
| cross-application findings | yes | **yes** — and it *escalated* a row from habit to document-damage vector |
| classification continuity | n/a | **adopted it**, and merged a row its predecessor had duplicated |

The cold instance produced the strongest review of the pass at roughly **40% of the warm
instance's cost**. It did not re-litigate settled findings; it inherited the settled/unsettled
split from the file and added a "stop re-checking these" list of its own.

So the compounding state was never really held by the instance — it was held by the **table**,
from the moment the table started being written. **A respawn is cheap exactly to the degree the
tallies are current.** Writing them after every review is therefore not a backup against losing
the instance — it is the thing that makes the instance replaceable, and it is the load-bearing
rule here.

Two things not to over-read from a single data point. The replacement got an unusually detailed
hand-off, written by an orchestrator that still held the predecessor's five reports in context;
if the orchestrator session dies too, the table is the *only* survivor, which raises the bar on
how completely it is written. And the last application is the easiest place to look good,
because five applications' worth of patterns are already named.

**Net change to the rule:** still no unit budget, still retire at batch boundaries — but the
observed trigger has a number attached. A review crossing **~200K subagent tokens** is worth a
respawn on cost alone, because a cold instance delivered equivalent-or-better quality at 86K.

## Ask twice, write it down

Adopted as a trigger rather than a preference: **any question asked twice about the project's
own setup becomes a rule the same day.** Treat "the config is unspecified" coming up in
conversation as a bug report against the config.

This is the rule that would have caught a real gap two sessions before it was caught — drafting
and review had been inheriting whatever model the parent session happened to be running, and
the question "which model does review use?" had come up more than once before anything was
written down. It sits in this file rather than `CLAUDE.md` because it is a rule about when to
write a rule.

## Don't put a git repository under a cloud-sync client

Two full sessions of work once stacked up uncommitted because every git command that touched
the object store failed with `fatal: mmap failed: Operation timed out` — including
`git status`.

**What it actually was.** The sync client had dehydrated 148 loose objects under `.git/objects`
into cloud-only placeholders. Git reads loose objects by `mmap`, and an `mmap` cannot drive a
sync client's on-demand hydration the way an ordinary `read()` can, so it stalls until the
kernel returns `ETIMEDOUT`.

**Why it was misdiagnosed for a day.** An earlier session tested `dd` on `.git/index`, saw it
read at full speed, and concluded the files were fine. Both halves of that were true and the
conclusion still didn't follow: `read()` hydrates, `mmap` doesn't, so a file can be perfectly
readable and still unmappable. Narrowing by pathspec showed `git diff` (worktree vs index)
passing while `git diff --cached` (index vs HEAD, which reads objects) failed, which is what
located the object store.

**How it was cleared.** Reading all 148 files in a loop hydrated them; 54 timed out on the
first pass and all 54 succeeded on a second, so throttling is transient and a retry loop is the
fix, not a repack. Nothing destructive was needed.

**Why hydration is not the fix that matters.** It restores git until the client next evicts,
which it will. Keep the repository outside any cloud-synced directory.

## The drafting pre-flight list, consolidated

The pre-flight list in `.claude/agents/drafting.md` was added with nine numbered items and
reached fourteen within two days. **At around twenty items nobody executes them faithfully** —
five recorded instances of a mechanical check self-reported as passed and false on disk are
what that failure looks like. A list long enough to be skimmed is a list that gets skimmed.

The consolidation rule: **retire nothing whose lesson is not preserved.** Every retired item is
traceable to the script check or the surviving item that absorbed it. Three merges were the
substantive ones, and each joined items that were the same defect wearing different symptoms:

- The duration items merged because *write endpoints instead of durations* is the single move
  that prevents all of them, so it leads and the failures follow as evidence for why.
- The generic-letter check joined the templated-closer check: a letter that names nothing about
  the company and a closer with the nouns swapped are one failure — **if the letter would read
  identically addressed to a different employer, it is not finished.**
- The public-sector capability-name sanction became an exception clause rather than a peer
  item. As a standalone item it read as a standing licence to quote ad vocabulary; attached to
  the headers-are-claims rule it reads as the narrow exception it is, with its limit — header
  only, never the body sentence — attached to the rule it qualifies.

**What the script now covers, so the list no longer restates it:** banned strings with line
numbers, the letter's header block, link and bracketed-token atomicity, every duration phrase
beside its canonical span, and every section header beside its block contents. The list keeps
only the judgements `scripts/mechanical_checks.py` cannot make — it reports, it never judges.

## Per-line scanning is a scan of the typesetting, not the document

Every banned-string check originally scanned line by line. A phrase split by a markdown line
wrap is invisible to all of them.

The incident: a cover letter carried a self-disqualifying sentence — *"if the … background is
non-negotiable, that's a fair call and I'd rather hear it now"* — wrapped exactly at the point
that broke the pattern across two lines. The checks printed PASS over it, and it was caught
only because a sweep agent happened to read the file whole. A wrap-aware rescan then found
**four more** live hits evading the same way, in letters sitting at "ready".

The project had already solved this once: a sibling scanner ran its patterns over whole text in
multiple folds precisely because "a secret split across a line break is invisible to a per-line
scan". The banned-patterns tooling never inherited the fix — a lesson written into one tool and
not carried to its sibling.

The fix: `unwrap_blocks()` in `scripts/mechanical_checks.py` gives every banned-string scan a
paragraph-joined second pass (bullets accumulate their continuation lines; blank lines, headers
and quotes stay boundaries). Wrapped hits are reported once, marked `(wrapped)`, without
double-reporting single-line hits. Regression tests pin the incident's exact shape.

## Stage by explicit paths, and check status at the moment of staging

A version-control rule said "check `git status` before committing and stage the paths this pass
actually touched". It was followed and still failed: the status check passed early in a long
pass, a parallel session then moved a folder, and a directory-level `git add` at commit time
swept the whole move into an unrelated commit whose message did not describe it.

The gap is the window between enumeration and staging — with parallel sessions normal, the tree
is allowed to change inside a pass. So: re-check status **immediately before** `git add`, and
prefer explicit file lists over directory adds whenever a peer session is busy. A directory add
is a claim that everything under it belongs to this pass, and no earlier status check can make
that claim true at staging time.

**The index itself is shared, not just the tree.** Mid-pass, a peer session staged its own
files and then committed; its commit machinery reset this session's already-staged entries (a
staged rename reverted to delete-plus-untracked). Even a correctly-staged explicit list can be
unstaged by a peer between `git add` and `git commit`, and the tempting race-proof form,
`git commit -- <paths>`, **cannot commit a staged rename**. It recurred in the opposite role a
day later — this session's commit consumed the index between the peer's `git add` and its
`git commit`, and the peer's commit aborted with *"no changes added to commit"*. Two things the
second instance established: **the hazard is symmetric**, so "let the peer commit first" is
advice both sides need and neither can time from inside; and **the window is not observable
from either session** — a status check at the moment of staging is measured *before* the window
opens. That is why the rule is now "stage, verify the staged list against the paths you meant,
and commit as one uninterrupted step", rather than another instruction to check earlier.

## Recon cites its dates and figures, or writes "could not confirm"

`docs/Recon_Checklist.md` has a "Cite it or don't write it" section, and `.claude/agents/recon.md`
a short restatement of it. The rule: any regulatory date, commencement date, statutory deadline,
named figure, headcount, revenue or funding number, or named individual's title carries an inline
source URL and read-date, or recon writes *"could not confirm"* instead of asserting.

**Two measured instances on the source corpus, and both reached a live cover letter.** A recon
file asserted a job title the candidate has never held, which surfaced in a letter's opening
sentence. Later, a recon file asserted three times that a regulator's prudential standard had
commenced a year later than it actually had, citing no page from the regulator — the later date
was real, but it belonged to a transitional arrangement for pre-existing contracts. It propagated
into the status file, into a live cover letter's opening clause addressed to a financial-services
**risk** function, and into a second application's recon file by cross-reference. Corrected in
five places.

**Why the fix is at the source rather than at review.** Both instances were caught by
`docs/Review_Checklist.md` step 5, which already tells the reviewer to distrust recon — so review
is working, and telling it to work harder buys nothing. The asymmetry is structural: the other
two inputs to drafting are fenced (the fact library guarantees fact-checked contents and states
that guarantee in its own text; the saved posting is verbatim by construction) and recon is not,
while drafting reads all three alike. A check that fires at review fires after the claim is
written; provenance discipline is the only thing that stops it being written.
