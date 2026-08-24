<!-- source-hash: 42444b24c0f4 docs/Writing_Style.md -->
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
  A slash ("Google Sheets/Excel") is one requirement, not two. "Or similar", "or equivalent
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
