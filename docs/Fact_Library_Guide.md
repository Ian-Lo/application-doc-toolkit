<!-- source-hash: original -->
# Building your fact library

The fact library is the one file every resume and cover letter is built from. Nothing goes
into an outgoing document unless it is in here first, and everything in here has been checked
by you. That is the whole method: the agent that drafts is never the agent that decides what is
true.

This guide explains what goes in the file, where the material comes from, and how to build it
by talking to Claude rather than by typing it out. The file itself starts from
`Fact_Library_TEMPLATE.md` at the repository root; the agent copies it to `Fact_Library.md`
for you when you ask it to set up your library. **Every line marked `>>> REPLACE` in the
template is yours to write.** The template holds no example entries, on purpose; the worked
example is in section 1 of this guide.

## 1. What one entry looks like

An entry (the toolkit calls it a *vignette*) is one verifiable fact about your work, written so
that a stranger could check it. It has four parts:

- **The fact**, as one bullet: what you did, with the concrete specifics kept in — the number,
  the named client, the named system, the outcome.
- **Tags**, on the next line, in the form `Tags: rostering, cost-control, hospitality`.
  These are what the drafting agent matches against a job ad's requirements, so use the words
  ads use.
- **Provenance**: where the fact comes from. An old resume, a performance review, a project
  write-up, or *confirmed in conversation* with the date. An entry with no source is a defect,
  not a style.
- **Any bounds** on the claim, stated plainly: "reporting only, did not build the roster
  system"; "co-led with the venue manager"; "figure is from memory, not a document".

An example, from the fictional candidate shown in full below:

```
- **Cut weekly roster overspend at a 120-room hotel from roughly 9% to under 3% within one
  quarter** by moving the roster from a shared spreadsheet to the property's workforce
  system and reviewing forecast-versus-actual hours every Monday.
  Tags: rostering, cost-control, workforce-management, forecasting, hospitality
  Source: 2024 performance review, "operational cost" section. The 9% and 3% figures are
  the review's; the timeframe is from memory.
```

Notice what the specifics do. "Cut overspend from 9% to under 3%" can be checked in a
screening call; "improved roster efficiency" cannot, and reads as filler.

### A worked example, in full

The template deliberately contains no example entries: everything above its fence counts as a
confirmed fact about *you*, so a fictional entry there would be a licensed lie the drafting
agent could put in your resume. The example lives here instead. **Sam Okafor, Harbourline
Hotels and Cove Street Bistro are all invented.**

```
## Identity

Sam Okafor\
Newcastle NSW · +61 400 000 000 · sam.okafor@example.com · linkedin.com/in/sam-okafor-example

Name for filenames: Sam_Okafor

- Australian work rights; no restriction. Two weeks' notice. Will relocate within NSW.
  Tags: work-rights, availability, relocation
  Source: confirmed in conversation 2026-03-02.

## Roles

### Harbourline Hotels — Duty Manager (Mar 2021 – Present)

- **Cut weekly roster overspend at a 120-room hotel from roughly 9% to under 3% within one
  quarter** by moving the roster from a shared spreadsheet to the property's workforce
  system and reviewing forecast-versus-actual hours every Monday.
  Tags: rostering, cost-control, workforce-management, forecasting, hospitality
  Source: 2024 performance review, "operational cost" section. The 9% and 3% figures are
  the review's; the timeframe is from memory.
- **Ran the overnight shift as the senior person on site** — front desk, security escalation
  and guest complaints — for a team of four, across an average of 180 check-ins a night in
  peak season.
  Tags: shift-leadership, escalation, customer-service, people-management, hospitality
  Source: 2023 position description; check-in figure confirmed in conversation 2026-03-02.
- **Coordinated the property's fire-warden training for 40 staff** across two sites.
  Confirmed by Sam 2026-03-02: scheduling and attendance only; the training was delivered
  by an external provider.
  Tags: compliance, training-coordination, whs, scheduling
- **Built the daily handover sheet the property still uses**: one page, filled in at each
  shift change, replacing three separate email threads.
  Tags: process-improvement, documentation, handover, shift-operations
  Source: the sheet itself, and the 2024 review's "initiative" paragraph.

### Cove Street Bistro — Shift Supervisor (Jun 2018 – Feb 2021)

- **Supervised a floor team of up to eight** on a 90-cover restaurant's weekend service,
  including opening and closing the till and reconciling cash and card takings.
  Tags: supervision, cash-handling, reconciliation, hospitality
  Source: 2021 resume; team size confirmed in conversation 2026-03-02.

## Recorded gaps

- No formal project-management certification.
- Has not used the Opera property-management system; the workforce system named above is the
  only one used hands-on.
```

Four entry shapes are in there: an achievement with numbers, a responsibility with a scale, a
bounded claim carrying its confirmation line, and a process fact. The identity block is in the
exact layout the cover-letter header uses — the name line ends with a backslash, and the
contact line carries the email address — because the lint checks for both.

## 2. Where the facts come from

Draw on everything, not only your latest resume:

- Every resume and cover letter you have ever sent, including old ones. Roles that a current
  resume has dropped for length are still facts.
- Performance reviews, promotion cases, and reference letters.
- Project write-ups, handover notes, incident reports, and anything you wrote at work that
  describes what happened.
- Certificates, licences, training records.
- Your own side projects, repositories, or published writing.
- Things you remember but never wrote down. These go in as **open questions** first (section 4)
  until you have decided how confidently you can state them.

The library ends up wider than any single resume, and that is the point. A resume is a
selection made for one audience; the library is the pool every selection is made from. Once a
fact is here it never has to be remembered again.

## 3. Structure

Keep the template's section order; the drafting agent reads the whole file every time, and a
predictable shape helps it find things.

1. **Identity block.** Your name and contact details in exactly the layout the cover letter
   header uses, plus one machine-read line: `Name for filenames: Sam_Okafor`. That line is what
   the agent reads to name your documents (`Sam_Okafor_Resume_260302_Northwind_OperationsCoordinator.md`),
   so it must be letters and digits with a single underscore between the parts of your name —
   nothing else.
2. **Education and credentials.**
3. **One section per role** under the `## Roles` heading, most recent first, headed like
   this:

   ```
   ### Harbourline Hotels — Duty Manager (Mar 2021 – Present)
   ```

   The parenthesised span matters. `mechanical_checks.py --facts Fact_Library.md` reads every
   `(Mon YYYY – Mon YYYY)` span in this file as the canonical length of that role, and lists
   every "five years" or "over a decade" phrase in a draft beside the span it is presumably
   describing, so a duration claim can be checked in one glance. Write the span in that exact
   form and the check works; write "2021 to now" and it is invisible to the check.
4. **Skills, for tag reference.** A plain list of tools, systems and methods you can name. Not
   for pasting into a resume; it is there so the drafting agent has consistent tag vocabulary.
5. **Recorded gaps.** Things you do *not* have that ads commonly ask for, stated as facts: "no
   formal project-management certification"; "have not used the Opera property system". A
   recorded gap is a licensed answer to a question; an unrecorded one is a guess.
6. **The fence.** A short paragraph, kept verbatim from the template, that says everything
   above it is confirmed. Nothing unconfirmed may sit above the fence, and nothing may be
   written below it except that paragraph.

## 4. The fence and the open-questions file

The library's value is one guarantee: **every entry above the fence has been confirmed by
you.** A drafting agent may use anything above it without checking further. One unconfirmed
entry voids that guarantee for the whole file, because the agent cannot tell which one it is.

So anything you are not yet sure of goes somewhere else: `Open_Questions.md`, at the
repository root, copied from `Open_Questions_TEMPLATE.md`. That file holds questions about
your own experience that nobody has answered yet — "did I run the whole migration or one
site?", "what was the actual headcount?" — one entry each, with why it matters and what an
answer would change. Three rules:

- **A question is answered by a two-file edit.** Write the confirmed fact into the library,
  then delete the question. A question that is answered but still listed keeps a fact out of
  your documents.
- **Silence is not a gap.** If an ad names a skill that appears nowhere in the library, that
  means nobody has asked you about it, not that you lack it. The agent should ask; the
  **Recorded gaps** section is the only place a gap is recorded.
- **Answers are not a one-way ratchet.** On the corpus this toolkit was extracted from, about
  half of the answers to open questions *narrowed* a claim. That is the process working: a
  claim narrowed here is a claim that survives a screening call.

When you confirm a bounded fact in conversation, the agent writes the confirmation on its own
line, directly under the claim, with the date and the bound:

```
- **Coordinated the property's fire-warden training for 40 staff** across two sites.
  Confirmed by Sam 2026-03-02: scheduling and attendance only; the training was delivered
  by an external provider.
```

None of the toolkit's markers — `Tags:`, `Source:`, `Confirmed …:` — uses square brackets, on
purpose: a bracketed token split across a line wrap is the same shape as a broken markdown
link, and nothing visible tells you it happened. Brackets in this file mean links, and only
links.

## 5. Building it by conversation

You do not type the library out. You feed old documents in and confirm what the agent proposes.

**Two ways to feed documents in.**

- *Paste.* Open one old resume, copy all of its text, paste it into the chat, and say:
  *"propose vignettes from this."*
- *Upload, for more than one document.* **Upload PDFs.** The agent's cloud computer reads
  PDF and plain text but not Word files; if a document is a `.docx`, open it in Google Docs
  first and choose **File → Download → PDF**. Then on github.com, open your private
  repository at its top level, choose **Add file → Upload files**, drag the PDFs onto the
  page, and press **Commit changes**. They land at the top of the repository — GitHub does
  not ask for a folder. Then say: *"I uploaded my old resumes; move them into sources/ and
  propose vignettes."* The agent files them under `sources/` before reading them.

Either way the agent replies with candidate entries and a question against each one that
needs bounding. You answer in plain sentences: *"yes"*, *"the number was 90, not 120"*, *"that
was a team effort, I ran the night shift only"*, *"not sure, park it"*. The agent writes only
what you confirm; anything parked goes to `Open_Questions.md`.

Expect the first session to produce a dozen or two entries and a handful of open questions.
Later sessions add to it: every time you correct a fact while drafting an application, the
agent writes the correction into the library immediately, so the next application starts from
the corrected version.

## 6. Editing it safely

The library is edited as prose but read as a fact base, and ordinary prose-editing habits
corrupt it. Six rules, each learned the hard way on the source corpus:

1. **Never bulk find-and-replace** a year, an employer or a system name. Adjacent entries carry
   different, nearby dates for different facts. Change one fact at a time, by locating it.
2. **A derived figure does not update itself.** Durations, counts and "N years" phrases are
   restatements of dates written elsewhere. After changing a date, look for anything computed
   from it.
3. **Keep every markdown link on one line.** A `[text](url)` split across a line wrap stops
   being a link with no visible error; the lint checks for it in outgoing documents, but not
   here.
4. **Ask before claiming.** A capability mentioned without a story is not yet an entry. Write
   the narrow version and ask; do not write the generous version and wait to be corrected.
5. **When a fact is corrected, mark the old phrasing dead.** Edit the governing sentence; do
   not stack a correction underneath it and leave the old version live.
6. **A correction is finished only when already-drafted documents are re-checked** for the
   phrasing it killed. Nothing re-checks them automatically.

## 7. Privacy

This file, and everything in `sources/`, is your employment history with names, figures and
dates attached. Keep the repository **private**, and keep it private permanently: git history
is permanent, so a repository that was public for an hour has published its contents for good.
The toolkit never sends the library anywhere; the only reader is the agent working in your own
repository.
