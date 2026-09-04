# application-doc-toolkit

A toolkit for producing job-application documents — tailored resumes, cover letters and
screening-question answers — with an LLM agent workflow that is **fact-governed by
construction**: every claim traces to a fact-checked library entry, every draft passes a
mechanical lint no agent can misreport, and the roles that write, review and verify are
structurally separated.

Extracted from a real, private application corpus. The measurements quoted in the docs
(failure rates, token costs, review yields) were taken on that corpus; identifying detail has
been removed, the shapes of the failures have not.

**Start here if you are new:** [`docs/Getting_Started.md`](docs/Getting_Started.md) — from
nothing to a finished resume and cover letter, in the browser, with no installs. Then
[`docs/Fact_Library_Guide.md`](docs/Fact_Library_Guide.md) for the file everything is built from.

## What changed

<!-- One line per publish, newest first, dated. `scripts/update_toolkit.py` prints the lines a
     private copy did not have. A line that needs a matching edit to the user's Fact_Library.md
     carries `LIBRARY EDIT:` followed by the edit. -->
- 2026-09-04 — Toolkit updates for private copies: say *"update the toolkit"*; `scripts/update_toolkit.py` fetches this repository, replaces the toolkit's own files, runs the tests and reports this section's new lines (`docs/Getting_Started.md` §7).
- 2026-09-04 — `docs/Getting_Started.md` §2–§3 corrected against the live github.com and claude.ai/code screens: sign in to GitHub first, the visibility control is a dropdown that defaults to Public, *Continue on web* is the browser route, and the default permission mode is Auto.
- 2026-09-04 — Starter kit: `docs/Getting_Started.md`, `docs/Fact_Library_Guide.md`, the two `_TEMPLATE.md` files, `scripts/new_application.py` with a `--candidate` parameter, and the intent table in `CLAUDE.md`.
- 2026-09-04 — The ad-vocabulary check (`mechanical_checks.py --facts`) and `scripts/ad_vocab_stoplist.txt`; eleven documents re-derived from their private sources.

## What's in it

| Path | What it is |
|---|---|
| `CLAUDE.md` | The orchestrator's rulebook: workflow order, agent budgets, capture and QA rules, and the intent table that maps a user's plain sentences to the scripts |
| `docs/Getting_Started.md` | The from-zero guide, written for a Chromebook user who never opens a terminal |
| `docs/Fact_Library_Guide.md` | How to build the fact library by conversation: what an entry is, where facts come from, the fence, the editing rules |
| `Fact_Library_TEMPLATE.md` | The library's skeleton, with `>>> REPLACE` markers; the worked example is in the guide, not the template |
| `Open_Questions_TEMPLATE.md` | The one file where unconfirmed facts wait |
| `docs/Writing_Style.md` | A voice model built from the candidate's own writing, plus the LLM tells to avoid and the hard rules for handling gaps |
| `docs/Review_Checklist.md` | The reviewer's mechanical controls, including the subtractive accretion diff |
| `docs/Recon_Checklist.md` | Company research: topic list, source rules, reuse rules |
| `docs/Conventions_Rationale.md` | Why each rule exists — the incident behind it, so rules are revised knowingly rather than eroded |
| `scripts/new_application.py` | Scaffolds an application folder with the convention files and correctly-named empty documents; the candidate name is a parameter |
| `scripts/test_new_application.py` | Its test suite |
| `scripts/update_toolkit.py` | Brings a private copy's toolkit files up to date from this repository — explicit path list, never touches personal files, runs the shipped suites and rolls back if one fails |
| `scripts/test_update_toolkit.py` | Its test suite, including the toolkit/personal path split |
| `scripts/mechanical_checks.py` | One-command document lint: banned strings, header block, link atomicity, duration phrases beside their canonical spans, section headers beside their bodies, and — given `--facts` — the ad vocabulary your fact library does not license |
| `scripts/banned_patterns.txt` | The pattern file, with per-pattern rationale in its comments |
| `scripts/ad_vocab_stoplist.txt` | The ad-vocabulary check's noise floor: function words and role-generic phrases whose adoption carries no claim |
| `scripts/test_mechanical_checks.py` | The lint's test suite — a pattern added without a probe fails by design, and so does a stop-list phrase that would suppress a measured over-claim |
| `.claude/agents/` | Role definitions (drafting, review, recon) for Claude Code, with tool allowlists as enforcement |
| `.claude/settings.json` | A permissions allowlist covering every command `CLAUDE.md` makes the agent run, including `git push` |

## The three ideas worth stealing

1. **A self-reported check is not a check.** Agents were observed reporting mechanical checks
   as passed that were false on disk — five times, always in the same direction. So the lint
   runs as a script, by the orchestrator, and its full output is pasted into the reviewer's
   brief. Script output cannot be misreported.
2. **The reviewer never edits.** Its tool allowlist is `Read` alone — findings go back to
   the drafting role, which applies them, so fact-fidelity checking stays in one place. The
   allowlist is the enforcement, not a convention.
3. **Accretion is checked subtractively.** For each claim: list what the fact library licenses,
   list what the sentence asserts, subtract. Checking by recognition finds the drifted verb you
   already know and misses its sibling in the same sentence.

## Using it

Make a **private** copy first (*Use this template → Private*): your copy will hold your
employment history, and git history is permanent. `docs/Getting_Started.md` walks through the
rest by conversation. The workflow assumes [Claude Code](https://claude.com/claude-code) (the
agent definitions and `CLAUDE.md` load automatically), but the scripts stand alone:

```
python3 scripts/new_application.py --candidate Sam_Okafor --company Northwind --role OperationsCoordinator
python3 scripts/mechanical_checks.py Applications/<folder> --facts Fact_Library.md
python3 scripts/test_mechanical_checks.py && python3 scripts/test_new_application.py && python3 scripts/test_update_toolkit.py
python3 scripts/update_toolkit.py --dry-run
```

The lint finds the outgoing documents by filename (`*Resume*`, `*CoverLetter*`) and the saved
job ad by filename too (`*posting*.md`); with `--facts` it also lists the phrases the ad and
your documents share that your fact library never licensed — the single best predictor of an
over-claim on the corpus this was extracted from.

You supply your own fact library — `Fact_Library.md`, a single file of atomic, verified
achievement entries, tagged for matching against job-ad requirements, started from
`Fact_Library_TEMPLATE.md`. The drafting rules in `.claude/agents/drafting.md` and `CLAUDE.md`
describe its contract: fact-checked entries only, unconfirmed material lives in
`Open_Questions.md`, and facts flow into the library the moment they are confirmed. Both files,
and any `sources/` folder of old documents, are personal data: keep the repository private.

## Licence

MIT — see `LICENSE`.
