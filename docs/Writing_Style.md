<!-- source-hash: 057487a29c69 docs/Writing_Style.md -->
# Writing style — a voice model, and the LLM tells to avoid

**Read this before drafting or revising any resume, cover letter, or screening-question
answer.**

Two halves, in this order: **what to aim for**, then **what to avoid**. The second half is longer
because it is a list of specific failures, not because avoidance is the goal. Writing only to dodge
a blacklist is how prose ends up with no identity.

## The positive model — build one from the candidate's own writing

This file cannot ship a voice model, because a voice model belongs to one writer. What it can
ship is the method, and the boundaries that method needed when it was first used.

Take a piece of the candidate's real published writing — an essay, a long post, a report they
actually wrote — and extract **structural moves**, each with a quoted example so it can be
checked. The set that worked in practice, as a template for what to look for:

**1. Concede, then pivot. Never concede and stop.** The most useful move, because
concede-and-stop is the most expensive habit in AI-drafted application documents — see
"Handling gaps" below.

**Scope: this is a gap-sentence move, not a general sentence shape.** Learned by review: used
everywhere, it becomes a mannerism — one test draft came back with **six negative antitheses in
seven paragraphs**, five of them in freshly written sentences. The reviewer's words: *varied
sentence length and monotonous sentence logic.* A reader who notices one notices all six, and the
signature reads as constructed. **Count them before you ship: more than two in a letter means you
are using the move as a tic, not as an argument.**

**2. State a position, then attach concrete conditions** — not "it depends".

**3. Name a hard trade-off rather than smoothing it.** When an ad exposes a real limit, name it
and keep going; don't write around it.

**4. Short declarative sentences, minimal subordination.**

**5. First person used sparingly, and unhedged when used.** "My paper examines X" — not "this
paper will attempt to examine X".

### Boundaries on the voice model — read before using it

- **It licenses no facts.** It describes how to write, never what is true. Your fact library
  remains the only source of claims.
- **It is a voice model, not a register change.** If the source writing is long-form researched
  argument, do not import its block quotes, citations, bulleted sentence fragments, or length
  into a short-form cover letter.
- **Where the model and the prohibitions below conflict, the prohibition wins.** Expect real
  collisions: a writer's natural constructions can read stiff in a letter, academic prose leans
  on dashes harder than the em-dash rule allows, and — observed in testing — the pivot in move 1
  adds words, which tempts a drafter into giving the gap its own paragraph. **"One gap, one
  sentence" still governs.** Concede and pivot *inside* one sentence, inline in a paragraph that
  is about something else. A gap promoted to its own paragraph is more prominent, not less,
  however well the pivot is written.
- **Copy the moves, not the prose surface.** Source writing usually contains real copy-editing
  errors. It is evidence of how the writer structures an argument, not a copy-editing model.

## The letter header block — hard breaks, every new cover letter

`docs/Review_Checklist.md` has stated this convention since early on, but the reviewer reads that
file and the drafter does not, so on the source corpus the same defect recurred across two
separate passes before the rule was restated here, where drafting reads it directly.

Every new cover letter's header and valediction use a trailing backslash (`\`) as a Markdown hard
line break — **not** two trailing spaces, not a blank line:

```
Jane Doe\
Springfield\
+1 555 0100 | jane@example.com | [LinkedIn](https://www.linkedin.com/in/janedoe/)

<addressee>

Re: <role title exactly as advertised>

Dear <salutation>,

...

Regards,\
Jane Doe
```

**Losing the `\` on the name/city lines, or after `Regards,`, collapses the block into one
run-on paragraph when the document renders** — invisible in the markdown source, which is exactly
why it survives an author's own read-through and needs a mechanical check
(`mechanical_checks.py`'s `LETTER HEADER BLOCK` section) rather than eyeballing. Resumes use the
same header line without the hard breaks, since a resume has no valediction.

## The closing line — where a published evidence page is available

Where the candidate has a **published, checkable record** of their career facts, every new cover
letter closes its body with one short paragraph that points at it and offers a call, sitting
immediately above the valediction.

**The three moves, stated as moves. There is deliberately no model sentence here.**

1. Point at the published record — **without characterising what is on it** (see the
   prohibition below; this is the move most likely to go wrong).
2. Offer the reader a next step they can actually take.
3. Give the contact detail.

**Build the paragraph from the three moves. Never from a model sentence.** This section originally
carried one, written as an illustration with an explicit anti-copy warning attached. Its
comparative frame then turned up in three of four independently drafted closers in a single
review — the rule seeded the convergence it exists to prevent, exactly as a fact library will
seed a banned verb into drafts when it uses that verb in its own pre-written bullets. The warned
sentence spread as readily as unwarned phrases did; the warning bought nothing measurable. **A
rule file must not contain a well-formed specimen of a construction it bans, marked or
unmarked** — if a drafter can lift it, a drafter will.

**"Adapt the wording to each letter" was not specific enough, and this is measurable.** Three
drafting agents, working independently on three different ads with no sight of each other's
output, produced the same clause in all three letters with a single word swapped:

> "It is public **precisely so it can be checked rather than taken on faith**"
> "published **precisely so it can be verified rather than taken on faith**"
> "it's public **precisely so it can be checked rather than taken on faith**"

**So four phrasings are retired outright, and none returns:**

- **"rather than taken on faith"**, and the "precisely so it can be [checked|verified]" frame it
  travels with. Convergent from a standing start in 3 of 3 letters.
- **"Happy to talk it through"** — a plain-register stand-in for the banned "I'd welcome the
  opportunity to discuss", sitting in the banned closer's position.
- **"The [record] linked above"** as the closer's opening words. Retired on the same evidence and
  the same terms: three cold drafting instances, three different ads, no shared context, and all
  three closers opened on the identical five words, two of the three differing by one adjective.
  **That the retirement of the previous convergent phrasing was already in this file, and had been
  read by all three agents, is the finding: naming a string retires the string, not the move.** The
  paragraph must now enter from somewhere other than the record — the contact details, the reader's
  own next step, or a specific artefact named earlier in the letter.
- **"the dated, sourced detail behind …"**, and the `[dated|sourced] detail behind every
  [claim|line] above` frame it travels with. **This one was seeded by this very file**: an earlier
  version of the paragraph below prescribed it, in bold, as the replacement for a different
  defect. Measured across a five-letter pass: five letters, three variants, one stem — the last
  from a cold drafting instance explicitly briefed to enter the closer differently, which
  converged anyway. **A bolded imperative in a rule file outranks a prose instruction in a
  brief.** Both patterns are in `banned_patterns.txt` as a backstop; the fix was removing the
  prescription.

**And one thing the closer must never do, found in the same round.** One of those letters wrote
that the page was published "with **the vignettes** those paragraphs were built from" — naming
the project's internal term for its fact library, which tells an external reader the letter was
assembled from one. The closer points at a published page, so it is the exact place the boundary
between *the candidate's published evidence* and *the drafting apparatus* is most likely to be
crossed. **The prohibition: no outgoing document names the fact library, the agents, or the
private corpus.** That is the whole rule — there is no replacement phrase here, for the reason the
fourth retired phrasing above records.

**A second prohibition, and this file seeded this one too.** An earlier version of this paragraph
ended *"say what the page holds in whatever words the letter's own rhythm wants."* **The closer
may point at the published page. It may not describe the page's contents.** Four letters in one
pass took the invitation, and three of them made statements that were false against the published
page as it stood on disk: *"clients, contract values and dates are laid out in full … kept
current"* (the page carried no contract values and had not been reviewed in weeks); *"the dates,
figures and named clients above are all sourced at the link"* (two of them were not on the page);
*"laid out next to where they came from"* (the page carries no provenance, by design). The fifth
letter was correct, and the reason is the rule: it promised nothing checkable. **The mechanism is
structural, not careless.** A published page is hand-authored and lags the fact library by
construction, so a closer that enumerates its contents is a claim about a second document that
nobody re-checks when the first one changes. This is the exact sibling of *never promise the
reader's tooling can reach it*, below: **the closer may not make a claim about anything the letter
itself does not contain.**

**The lesson generalises past these two strings.** Hand several agents the same rule and the same
three moves and they converge on the most obvious way to say it — and the most obvious way is what
a screener reading two of the candidate's letters notices first. **Change the sentence's structure:
where the paragraph enters, what governs the verb, where the contact detail lands. Not just its
adjectives.** A synonym swap is not adaptation. If a phrasing feels like the natural one, that is
the signal another agent already used it.

Four boundaries, and the first matters most:

- **Address the reader, not "your LLM".** The instinct here is to invite an employer's AI screening
  tool to interrogate the link, and the offer itself is sound — published evidence, openly handed
  over for scrutiny, the opposite of gaming a screen. But text addressed in the second person to an
  automated reader is shaped exactly like a prompt-injection attempt, and a recruiter who notices it
  reads it that way whatever it actually says. Wording that covers a screening tool without naming
  one gets the same reach at none of that cost.
- **Never promise the reader's tooling can reach it.** Most ATS and LLM screeners cannot fetch a URL
  at all, and the candidate's own successful fetch proves only that the page exists — not that an
  outside reader, unauthenticated, can open it. Invite scrutiny; never assert an automated check
  will succeed.
- **It is a closer, and "Avoid LLM tells" bans cliché closers.** This paragraph is the banned
  wording's opposite in kind — it hands over evidence and a contact instead of asking for a meeting
  — but it occupies the same position, so check it against that rule every time rather than
  assuming the exception carries. It never becomes "I'd welcome the opportunity to discuss".
- **Not retroactive.** Existing live documents gain the closing line when next touched for another
  reason, never in a sweep.

## The career break on a resume — bill the block for the activity

**Two rules can pull in opposite directions here, and if no file resolves it they will be resolved
differently in the same batch.** That is what happened: a disclosure ruling in the fact library
contemplated a heading reading "Career break (20XX – present)", while "Handling gaps" below says a
gap gets **"never its own heading"**. Two resumes in one batch solved it two different ways and
both drew a finding. The ruling:

**Bill the block for the activity, not the absence.** The heading names what was actually done —
the volunteering, the study, the caring role, with its own dates — that bullet leads, and **the
career-break disclosure is one sentence at the end of the block**. That satisfies both rules at
once: the disclosure is present and plainly worded, and no heading is spent on the gap.

Three things this does **not** license:

- **Do not remove the disclosure.** Whether to disclose is the candidate's decision, not a
  drafter's. Once made, it stands.
- **Do not move the block to bury it.** Its chronological position is defensible; relocating it to
  the end reads as concealment. Position is not the problem, billing is.
- **Do not collapse two different spans into one.** A caring or study commitment that has **ended**
  and a break from full-time work that is **still open** are two facts, and merging them
  misstates both. Write only what the fact library licenses, and never write the underlying
  personal circumstance beyond what the candidate has explicitly approved.

## Avoid LLM tells

Every resume and cover letter generated with model assistance must read as if a person wrote it
under normal time pressure, not as AI-generated copy. Before presenting output, check it against
this list and rewrite anything that trips it:

- No cliché openers ("I'm writing to apply for...") or closers ("I'd welcome the opportunity
  to discuss...", "Thank you for considering my application").
  - **This bans a cliché *closing sentence*. It does not ban the valediction.** Every cover
    letter still ends "Regards," (or similar) above the name. The two were once read as one
    rule, and the result was **six consecutive letters that ran the last body sentence straight
    into the signature name** with nothing between — which reads as a truncated file, not as
    restraint. Two separate checks recorded that sign-off as "checked, clean", because a name
    was present.
- No meta-commentary about the writing itself ("I recognise that... I'm addressing that gap
  directly") — state gaps plainly instead.
- Vary sentence length and paragraph rhythm; don't make every paragraph the same shape/length.
- Cut buzzwords and corporate-speak padding (rigorous, robust, seamless, leverage,
  spearheaded), and the intensifier "genuine"/"genuinely" in any form. These are patterns in
  `banned_patterns.txt`; keep your own record of adjudicated exceptions.
- Limit em-dash usage; don't lean on it as a crutch for every aside. Replace with -.
- Resume professional summaries: no redundant closing sentence stating obvious intent
  ("Seeking to bring this background to an X role" when it's literally the resume for role X).
- Prefer concrete, specific phrasing over dense noun-stacking ("Analytically rigorous
  professional with a background spanning...").
- Attribute AI-directed work accurately — never phrase something an AI agent executed as if
  the candidate did it personally/manually (e.g. "directed the agent to trace every value,"
  not "traced every value by hand"). The candidate directs the AI and verifies the result; the
  AI performs the mechanical step.
- For values/culture-fit screening questions, echo the company's actual stated theme or
  mission rather than answering generically — but don't quote their own tagline back at them
  verbatim, which reads as flattery rather than real alignment.

## Handling gaps — never disqualify the candidate on their own behalf

This section exists because the opposite failure is the one that actually happens with
AI-drafted applications. In the project this file comes from, nine separate times a document
conceded or omitted something the candidate could do; not once was one caught claiming something
they couldn't. The bias runs one way.

**The screener decides who is out. The document's job is to be read.** Every rule below follows
from that.

**Every rule here is a prohibition, so pair them with move 1 above — concede, then pivot.** The
rules tell you what a gap sentence must not do; move 1 is the shape it should take. A gap
sentence that concedes and then stops has satisfied every rule below and still cost the
application.

- **Never write a sentence whose effect is to withdraw the application.** No "if X is a hard
  requirement, this isn't the right match", no "you may prefer someone with...", no "I understand
  if this isn't a fit". These read as pre-emptive self-rejection, and a screener who was
  undecided now has a decision written for them, in the candidate's own words. This is a hard
  rule, not a style preference. Structurally identical closers count: any clause that hands the
  reader a reason to stop is the same move in different words. (These are the `selfdq` category
  in `banned_patterns.txt` — treat hits as hard failures.)
- **One gap, one sentence. Never a paragraph, never its own heading, never the closer.** A gap
  given paragraph-level space reads as more disqualifying than it is. Put it mid-document, not
  in the final position, which is the one the reader remembers.
- **Never announce that you are being honest.** "I'd rather say that plainly than claim a
  competence I haven't earned", "saying that upfront rather than dressing it up" — this is
  meta-commentary, it recurs across letters in near-identical form, and performed honesty reads
  as a formula. State the fact; the plainness is the point, not a thing to point at.
- **Check the ad's own wording before conceding anything.** A *desirable* is not an *essential*.
  A slash ("Power BI/Tableau") is one requirement, not two. "Or similar", "or equivalent
  demonstrated technical capability", "preferably" and "ideally" are escape hatches the
  advertiser wrote deliberately — use them. One recorded ad prefaced its whole requirements
  list with "you will *ideally* bring" and the application conceded against it three times.
- **Never write a concession in the same pass that discovers the gap.** If the fact library
  is silent on something, that means nobody has asked the candidate, not that they lack it.
  Ask, and leave the sentence unwritten until they answer. A concession is the one edit that
  should never be made autonomously.
- **A concession must cite its licence.** Every conceded gap must cite either a known-gaps
  entry in the fact library or an open question the candidate has been asked, or the sentence
  is not written. Adopted after three concessions were written against silence in one pass —
  one of them not merely unlicensed but wrong.
- **The right correction to an over-claim is usually narrower, not zero.** When a claim is too
  strong, cut it to what the fact library supports and keep it. Deleting it outright is how a
  real capability disappears from the record.
- **Constraints are not concessions.** Real limits the candidate wants stated — a lapsed
  clearance, a lapsed certification, no current work in a domain — are stated once, factually,
  with what *is* true attached ("has held one and can reapply"). That is not the same as
  arguing against themselves.
