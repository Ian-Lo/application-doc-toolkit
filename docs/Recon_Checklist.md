<!-- source-hash: ca3699650639 docs/Recon_Checklist.md -->
# Company recon checklist

**Read this before starting recon on any company.**

Run recon the first time a job URL or posting is provided for a new company. If you delegate it
to a model, use a small/fast one at low reasoning effort: recon is fact-gathering and
source-checking, not deep synthesis.

A new `Company_Context.md` covers:

- **Hiring manager / recruiter** — named contact from the posting or LinkedIn; if none,
  confirm the absence explicitly and note the fallback application address.
- **Leadership** — CEO/CTO/CPO/board chair, recent transitions, notable backgrounds.
- **Company values / stated mission** — careers page and job posting, plus anything less
  obvious that isn't stated in the posting itself.
- **Products & services** — scoped to where the target role actually operates, not the whole
  portfolio generically.
- **Tech stack** — from the posting plus the company's other current engineering postings.
- **Org structure / who the role reports to** — where findable.
- **Competitors & market position** — who else operates in the space, and the company's actual
  differentiation.
- **Recent news & financials** — funding, earnings, acquisitions, leadership transitions,
  legal matters if material.
- **Hiring manager's own public writing** — posts/articles revealing voice or priorities.
- **Employee reviews & interview experience** — Glassdoor and similar. Treat as a noisy,
  self-selected sample: useful for interview prep and culture calibration, never a citable
  fact in a letter.
- **Team's own public output** — engineering/product blog, changelog, GitHub org, release notes.
- **Benefits & stated perks** — leave policy, remote/hybrid specifics, professional-development
  budget. Feeds "what matters to you" answers and negotiation, separate from salary research.
- **Headcount / hiring trend signals** — concurrent open roles, LinkedIn employee-count trend;
  context for a "why now" angle.

## Never restate what the ad requires

**You research the company. You do not summarise, re-rank, or re-word the ad's requirements.**
The verbatim ad is already captured in its own file, and drafting and review both read it
directly. Anything you write about requirements is a second, lossier copy competing with the
original — and a paraphrase that manufactures a gap is the single most expensive recurring
defect in AI-drafted applications.

The incident that made this a rule: an ad prefaced its whole requirements list with "you will
**ideally** bring", so it stated **no essentials at all**. The recon file rendered one line as
"(essential)" twice and then "essential" a third time. The application's own status notes
correctly spotted the "ideally" escape hatch — and overrode themselves with *"But recon reads it
as essential regardless."* Both outgoing documents were weighted on recon's word: a bolded
resume header, a skills-line disclaimer, and a dedicated cover-letter paragraph conceding a
requirement the advertiser never made.

Three prior recon files over-specified beyond the ad without doing damage (a contact's title, an
office split, "permanent not contract"). The fourth reached a document, so it is now a rule
rather than a habit to watch:

- Don't classify a requirement as essential, mandatory, required, or a deal-breaker. That is the
  ad's wording to carry, not yours.
- If a requirement genuinely matters to the *company* angle — a clearance-heavy government
  practice, say — describe the **company**, not the requirement's strength.
- **Check your recommendations too.** The same recon file recommended a strategy that
  presupposed a credential the candidate does not currently hold. A correction that fixes the
  assertion and leaves the recommendation derived from it is a half-fix, and one is on record.

## Keep recon out of biography

`Company_Context.md` covers the company; the fact library covers the candidate. Any claim about
the candidate's own history appearing in a recon file is unsourced unless it cites the fact
library, and recon carries no provenance discipline to catch it. A recon file once asserted a
job title the candidate has never held, and it reached a cover letter's opening sentence.

## Reuse

When a company already has a `Company_Context.md` in another application folder, don't
re-research the shared sections (leadership, values, products, general news). Instead:

- Symlink the new folder's copy to the original
  (`ln -s ../YYYY-MM-DD_Company_OtherRole/Company_Context.md Company_Context.md`), so content
  isn't duplicated and stays in sync if the original is updated.
- If the company was researched recently, recon only the topics above that are new or specific
  to this application (different team, different product-fit angle, newly found hiring manager).
- Role-specific findings go into the **same** shared file (the symlink target), never a separate
  addendum — one file per company. Where content differs by role, add a labelled subsection
  (e.g. `### Senior Technical Writer`) rather than overwriting the other role's findings.
  Company-wide sections (leadership, values, financials, news) stay unlabelled/shared.
- Only break the symlink (copy instead of link) if recon has genuinely gone stale and needs a
  divergent version — and note why in the application's status file.
