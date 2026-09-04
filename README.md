# application-doc-toolkit

A toolkit for producing job-application documents — tailored resumes, cover letters and
screening-question answers — with an LLM agent workflow that is **fact-governed by
construction**: every claim traces to a fact-checked library entry, every draft passes a
mechanical lint no agent can misreport, and the roles that write, review and verify are
structurally separated.

Extracted from a real, private application corpus. The measurements quoted in the docs
(failure rates, token costs, review yields) were taken on that corpus; identifying detail has
been removed, the shapes of the failures have not.

## What's in it

| Path | What it is |
|---|---|
| `CLAUDE.md` | The orchestrator's rulebook: workflow order, agent budgets, capture and QA rules |
| `docs/Writing_Style.md` | A voice model built from the candidate's own writing, plus the LLM tells to avoid and the hard rules for handling gaps |
| `docs/Review_Checklist.md` | The reviewer's mechanical controls, including the subtractive accretion diff |
| `docs/Recon_Checklist.md` | Company research: topic list, source rules, reuse rules |
| `docs/Conventions_Rationale.md` | Why each rule exists — the incident behind it, so rules are revised knowingly rather than eroded |
| `scripts/mechanical_checks.py` | One-command document lint: banned strings, header block, link atomicity, duration phrases beside their canonical spans, section headers beside their bodies, and — given `--facts` — the ad vocabulary your fact library does not license |
| `scripts/banned_patterns.txt` | The pattern file, with per-pattern rationale in its comments |
| `scripts/ad_vocab_stoplist.txt` | The ad-vocabulary check's noise floor: function words and role-generic phrases whose adoption carries no claim |
| `scripts/test_mechanical_checks.py` | The lint's test suite — a pattern added without a probe fails by design, and so does a stop-list phrase that would suppress a measured over-claim |
| `.claude/agents/` | Role definitions (drafting, review, recon) for Claude Code, with tool allowlists as enforcement |
| `.claude/settings.json` | A minimal permissions allowlist |

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

The workflow assumes [Claude Code](https://claude.com/claude-code) (the agent definitions and
`CLAUDE.md` load automatically), but the documents and the lint stand alone:

```
python3 scripts/mechanical_checks.py path/to/one-application-folder --facts path/to/your-fact-library.md
python3 scripts/test_mechanical_checks.py
```

The lint finds the outgoing documents by filename (`*Resume*`, `*CoverLetter*`) and the saved
job ad by filename too (`*posting*.md`); with `--facts` it also lists the phrases the ad and
your documents share that your fact library never licensed — the single best predictor of an
over-claim on the corpus this was extracted from.

You supply your own fact library — a single file of atomic, verified achievement entries,
tagged for matching against job-ad requirements. The drafting rules in
`.claude/agents/drafting.md` and `CLAUDE.md` describe its contract: fact-checked entries only,
unconfirmed material lives elsewhere, and facts flow into it the moment they are confirmed.

## Licence

MIT — see `LICENSE`.
