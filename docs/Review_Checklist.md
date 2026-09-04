<!-- source-hash: 9feda0c17d84 docs/Review_Checklist.md -->
# Application review checklist

**Read this before reviewing any resume or cover letter.** Read `Writing_Style.md` alongside it —
this checklist covers what to verify, that file covers how the prose should read. **Check prose
against both of its halves**: the positive voice model as well as the LLM-tell prohibitions. A
draft can clear every prohibition and still read as nobody in particular, and that is a finding
worth reporting — most usefully as *a gap sentence that concedes and stops where the candidate's
own writing would concede and pivot.*

Everything here was a review finding that had no home until it was written down. The recurring
numbers cited below were measured on one real application corpus; treat them as evidence for the
checks, not as your own baselines.

## Before you start

1. **Confirm the saved job posting is verbatim, not a summary.** If there is no verbatim block,
   stop and say so. Do not review against a paraphrase — a summary preserves the topics and
   discards the vocabulary, and the whole gap analysis then runs on the wrong words. This once
   produced two full review rounds recording a gap the candidate did not have.
2. **Gather all four inputs**: the verbatim ad, the fact library, `Company_Context.md`, and
   the drafted documents. A review missing the fact library cannot check the thing that matters
   most.

## 1. The subtractive activity diff

This is the core control and the one an unstructured review lacks. It is mechanical — do it as a
procedure, not as a judgement.

For each experience claim in the resume or cover letter:

1. Find the fact-library entry that the claim rests on.
2. **Enumerate the activities that entry licenses.** Write them out.
3. **Enumerate the activities the document's sentence asserts.** Write those out too.
4. **Subtract.** Anything asserted and not licensed is a new claim. It needs a new fact-library
   entry, or it comes out.

**Do this subtractively, never by recognition.** Recognition means scanning for verbs you have
already identified as drifting. It finds the instance you have seen and misses its sibling.

The proof, from a real review round. The sentence under review was:

> "profiling the source datasets for quality and completeness first, then producing the mappings
> and transformation logic, then reconciling what landed against what left."

The library licensed three activities; that sentence asserts five. The reviewer caught
"reconciling" and missed "profiling" **in the same sentence**, because it was matching a verb it
had already flagged elsewhere rather than auditing the sentence against the library. The missed
claim then survived a revise-then-submit verdict and sat in a document queued to be sent. A
subtractive diff would have caught it two rounds earlier.

## 2. Flag ad-vocabulary adoption

A term that appears in the ad's essentials but nowhere in the fact library is the highest-risk
phrase in the document. Tailoring to the ad's vocabulary is the method; accretion is that method
overshooting, so the risk concentrates exactly where the method is working hardest.

The drafter is supposed to flag these at draft time. Check anyway — a term it adopted without
noticing is precisely the one it will not have flagged.

## 3. Check both failure directions

They are not symmetrical: the measured rate on one corpus was roughly nine under-claims to zero
over-claims.

**A third direction: check named facts as their own pass.** Two live documents once stated a
migration ran on one cloud platform; the fact library said a different one, twice, in the same
entry — and the ad's first essential was the wrongly named platform. **The subtractive activity
diff does not catch this** — the activity was licensed and only an attribute was falsified. So
for every named client, cloud, platform, date, contract value and headcount in a document, check
the value against the library, not just the verb. It is the cheapest class of error to catch and
the most damaging to be caught at: one question in a screening call exposes it.

**False concession is the dominant direction.** A document concedes or omits something the
candidate can genuinely do. Before accepting any concession in the draft, re-read the ad's own
wording:

- A *desirable* is not an *essential*.
- A slash ("Power BI/Tableau") is one requirement, not two.
- "Or similar", "or equivalent demonstrated technical capability", "preferably" and **"ideally"**
  are escape hatches the advertiser wrote deliberately.
- **Read the preamble above the bullets before reading the bullets.** One recorded ad prefaced
  its entire requirements list with "To be considered for this role, you will *ideally* bring:" —
  **not one stated essential in the whole ad** — and the application conceded against it anyway,
  three times in one pair.
- **An "or" has two doors. Don't close both.** The same ad wrote "certification, **or** a strong
  and demonstrated amount of hands-on experience"; the cover letter denied the experience *and*
  volunteered the missing certification, in one clause, in its second sentence.
- Silence in the fact library means nobody has asked the candidate, not that they lack the skill.
- **`Company_Context.md` has no standing on what an ad requires.** Recon is a paraphrase layer;
  the ad is the source. A recon file once rendered "ideally" as "essential" three times, the
  status notes then reasoned *"But recon reads it as essential regardless"*, and both documents
  were weighted on it. Check requirement *strength* against the ad, never against recon.

When you find a false concession, the correction is usually to narrow the claim, not to delete
it — deleting is how a real capability disappears from the record.

**Over-claiming** is section 1 above.

## 4. Where to check hardest

The disclosure-framing tic is a **pressure response**. In one corpus it went clean for two
review rounds and came back as *"I'd rather give you the honest composition than a number that
flatters either of us."* It resurfaces wherever the document handles an awkward number, a gap,
or a screening-question answer. Those three places get the closest reading, every time.

Related, from `Writing_Style.md`: never announce that you are being honest. Performed honesty
reads as a formula, and it recurs across letters in near-identical form.

## 5. Treat recon as unsourced on biography

`Company_Context.md` covers the company; the fact library covers the candidate. Any claim about
the candidate's own history appearing in a recon file is unsourced unless it cites the library.
A recon file once asserted a job title the candidate has never held, and it reached a cover
letter's opening sentence.

Check the *recommendations* in the recon file too. A correction that fixes a false assertion and
leaves the recommendation derived from it is a half-fix.

## 6. Mechanical checks

Run `python3 mechanical_checks.py <application-dir>` (or have the orchestrating session run it
and paste the report). If the review is being done by an LLM agent, **the report belongs in the
brief** — hand-typed grep patterns are the specific failure the script replaced.

It covers the banned strings, the letter's header block, link atomicity, every duration phrase
printed beside its canonical span from the facts file, every section header printed beside its
block contents, and — when it is run with `--facts` — the ad vocabulary the facts file does not
license, which is section 2's check computed rather than eyeballed.

Three reasons this is a script and not a list of greps you run yourself:

- **Patterns you type are wrong.** An unanchored hand-typed pattern once flooded a review tally
  with false substring hits and produced a tally recorded as clean that was not.
  `banned_patterns.txt` is the only definition; keep your adjudicated exceptions written down,
  and read them before reporting a hit as a finding.
- **A self-reported check is not a check.** Five times in one project a mechanical check was
  reported as passed and was false on disk, every time in the same direction: run against the
  change just made rather than against the rule. A script's output cannot be misreported.
- For an LLM reviewer, **it costs zero tool calls instead of eight**, and every grep result
  pulled into the transcript is re-sent on every later turn of the review.

**But do not treat the report as infallible — spot-check it once, for staleness.** On the source
corpus a report generated earlier in a pass was pasted after a new pattern had been installed in
between, and reported **`clean` on a string the live pattern matches**. The defence costs one
tool call: read `banned_patterns.txt` — it is short — pick one pattern that plainly ought to fire
on the text in front of you, check it by hand, and see whether the report agrees. If it does not,
say so at the top of your report and treat the whole thing as untrusted for that application.
This is a spot-check, not a substitute: reading the pattern file does not let you search the
documents, so the report is still the only pattern search you have.

**Check the letter has a header block before anything else.** A full draft-review-revise cycle
once produced a cover letter with **no name, no contact line, no addressee and no `Re:` line**,
opening straight on the salutation — and neither the drafter nor a round-1 review caught it,
because every other check is about prose. A letter without contact details is unsendable
regardless of how good the argument is. The convention:

```
Jane Doe\
Springfield\
+1 555 0100 | jane@example.com | linkedin.com/in/janedoe/

<addressee — company, or named contact>

Re: <role title exactly as advertised>

Dear <salutation>,
```

Note the trailing `\` hard breaks on the name/city lines and after `Regards,` — losing them
collapses the block into one run-on line when rendered.

- Every `[link text](url)` is on one line. A bracketed span split by a line wrap silently stops
  being a link.
- Numbers are re-derived, not trusted. Verified-number drift was caught in three separate
  rounds, always the same way: a plausible figure produced by a wrong command over a file
  containing prose about its own contents.
- Durations use the canonical figures in the facts file, not arithmetic done fresh.
- A fix applied to the fact library has actually propagated to already-drafted documents.
  Caught live once, where a correction reached the library but not a resume already written
  from it.

## 7. Diff every section header against its own block

Independently requested by **three separate reviewers** before it became a numbered step; it was
the highest-yield check of the batch that promoted it.

The accretion diff in section 1 runs on **sentences**. A Core Skills header is a claim with no
sentence under it, so the diff cannot see it — and a header generalises whatever is beneath it
into a capability noun, which is exactly the move that over-claims.

**The procedure.** For each header in the resume, list the items in its block, then ask what the
header asserts that the block does not evidence. `mechanical_checks.py` prints the pairing; the
judgement is yours.

**Measured yield is predictable from the ad's format.** When the ad is written as abstract
capability nouns — no tools named, no credential gates, requirements phrased as "Budget & Cost
Control" — the drafter tends to adopt the ad's own requirement wording as resume headers, and
the block underneath has not caught up: measured at 3-of-7 and 3-of-5 headers over-claiming on
two such ads, versus 1-of-9 on an artefact-shaped ad. On one application, **5 of 7 headers were
the ad's own requirement wording.** When the ad is artefact-shaped, yield drops and **the
summary and the letter's transitions are the better target** instead.

Two specific shapes to expect:

- A header contradicted by the document's **own** text elsewhere (a "Budget & Cost Control"
  header fifteen lines above a summary stating the candidate was not account-aligned).
- A header contradicted by the application's own status-file gap note — see step 8.

### 7b. Run the same diff on the cover letter's topic sentences

Measured as **the second-highest-yield check** of the review round that added it: three of six
body paragraphs over-claimed this way while **every individual fact underneath them was licensed
and accurately written.**

A resume header generalises the items beneath it into a capability noun. **A cover-letter
paragraph's topic sentence does exactly the same thing to its own list** — and nothing else in
this checklist catches it. The section-1 accretion diff runs on sentences and scores each listed
item clean; the sentence that generalises them is not an item, so it passes.

**Same three steps as step 7:** list the paragraph's items, read its topic sentence, ask what the
sentence asserts that the items do not evidence.

The shape to recognise: a topic sentence claiming *"Explaining a service commitment to the
people who have to work to it runs throughout these roles"* — followed by five deliveries, of
which **exactly one** was about a service commitment. Each was licensed; the generalisation was
not. Note that the defect was **introduced by a round-1 fix** that added the paragraph, so run
this check hardest on paragraphs a previous round created or whose item list changed.

**The narrower claim is usually already available and usually answers the ad better.**

## 8. Diff the status file's gap notes against the documents

Takes about thirty seconds and found a finding the first time it was run.

A concession and its status-file record are assumed to travel together, so that reading the
documents catches both. In one recorded case they **separated**: the status file recorded a
*correct* decision not to concede against a requirement, and the cover letter conceded anyway.
**The status file read clean while the document did not**, so each artefact alone looked fine.

Read the gap notes and the open items, then check each one against what the documents actually
say. All three directions are live findings:

- the status file claims a gap the document quietly concedes anyway;
- the status file claims a requirement is answered while the document is silent on it (**this is
  the direction that hides under-claims**);
- the status file contradicts *itself* — one recorded status file said "no essential requirement
  goes unanswered" directly above an open item logging one as unaddressed.

## Verdicts

Three, and name which one explicitly:

| Verdict | Means |
|---|---|
| **Send** | No changes needed. |
| **Revise and send** | Fixes are mechanical; no re-review required. |
| **Revise and re-review** | Mandatory whenever any question about the candidate's *actual experience* is unresolved. |

The split exists because a single "revise-then-submit" label once carried a live false claim
through to a send-ready document. **Any application with an open factual question about the
candidate's experience goes in the third category automatically**, however small the edit looks.
The size of the fix is not the criterion; the openness of the question is.

## Two standing limits on the reviewer role

- **Report findings; never edit an outgoing document.** Findings go back to whoever drafts,
  who holds the fact-fidelity context and applies them. If the reviewer is an LLM agent, enforce
  this structurally: give it read-only tool access.
- **A skip recommendation is never resolved unilaterally.** Log it, flag it for the candidate's
  decision, and leave it open.
