<!-- source-hash: original -->
# Getting started — from a Chromebook, in the browser

**If you have a Mac, a Windows or a Linux computer, use `docs/Getting_Started_CLI.md`
instead.** Installing Claude Code on your own computer is the preferred route: it is more
flexible, and its behaviour is the best understood, because the method was built and is run
that way. This browser route has been tested from a Chromebook and it works, but with
limitations the other guide lists: every save needs a pull request, the role definitions did
not register in the browser session, and the last step through Google Docs could not be
tested from the session. Use this guide when a Chromebook is the only computer you have.

This guide takes you from nothing to a finished resume and cover letter, as PDF and Word
files, without installing anything. You will use three websites: github.com (where your
private copy of the toolkit lives), claude.ai/code (where Claude does the work), and Google
Docs (which turns the finished documents into PDF or Word). You never open a terminal, and
you never type a command; you type sentences to Claude, and the toolkit's rules tell it what
to run.

Facts about the services below were checked on 2026-09-04. If a screen does not match this
guide, the service has probably changed its layout; the sentence to type is the part that
matters.

## 1. What you need, once

- **A Google account.** Google Docs is the last step.
- **A GitHub account** (free) at github.com. It stores your private copy.
- **A Claude subscription.** Claude Code is not available on the free plan; a **Pro** plan is
  enough to start.
- **About limits, plainly:** Claude Code shares your subscription's usage limit with everything
  else you do with Claude. One full run — research the company, draft, review — can use a
  sizeable share of a Pro plan's five-hour window, because the method was tuned on a larger
  plan. Do one application first and see how far the limit goes before queueing several.

## 2. Make your own private copy

Your copy will hold your employment history, so it must be **private**, and it must stay
private: git history is permanent, and a repository that was public for an hour has published
its contents for good.

1. **Sign in to github.com first** (create an account if you have none). Signed out, the
   toolkit's page shows only *Fork* and *Star*; the button you need does not appear.
2. Open the toolkit's page on github.com (the link you were sent).
3. Press the green **Use this template** button, then **Create a new repository**.
4. Give it a name (`job-applications` is fine).
5. Find the **Choose visibility** box. It shows a button that says **Public** with a small
   arrow and looks like a label; press it and change it to **Private**. This is the one
   step in this guide that cannot be undone later, so check it says Private before you go on.
6. Press **Create repository**.

You now have your own copy. Nothing you do in it is visible to anyone else, including the
toolkit's author.

## 3. Connect Claude Code to it, once

1. Open **claude.ai/code** and sign in with your Claude account. The page is headed *Set up
   and start coding* and shows a large **Download** card with buttons for Terminal, VS Code
   and others. Ignore all of that: the browser route is the small **Continue on web** link
   at the bottom of the page.
2. Connect GitHub. The next page says *Code with Claude anywhere* and offers **Continue with
   GitHub**; press it (do **not** press *Skip for now* — if you did, a blue box titled *Two
   steps to work in your repo* appears later with a **Connect GitHub** button, which does the
   same thing). Sign in to GitHub if asked. When GitHub asks which repositories the **Claude
   GitHub App** may access, choose the private repository you just made, then press
   **Install** or **Authorize**. This is how Claude reads and writes your copy.
3. Press **Select repository** under the message box and choose your repository. The first
   thing you see is a box asking what to work on, not a chat: type the first sentence from
   section 4 into it and press **Enter** (there is no Start button). After that it is a
   conversation. The message box sometimes shows a greyed suggestion inside it, such as
   *fix the three findings*: that is a hint, not text you have typed — write your own sentence
   over it.
4. Permissions. On first visit a notice explains that **Auto mode** is the default: Claude
   runs the actions it judges lower-risk and blocks the rest. Press **Got it** and leave it
   on Auto to begin with. The toolkit pre-approves every command this guide will make Claude
   run, and the web searches and page fetches that company research needs.

If Claude reports that an action was **blocked**, switch the mode selector next to the message
box from **Auto** to **Default** and type the same sentence again. In Default mode a box may
ask permission: if it names a file in your project or a website, choose **Allow**. You can
choose "always allow" safely — this project runs in a separate cloud computer with only your
private copy on it.

## 4. Build your fact library, by conversation

The fact library is the one file every document is built from, and the toolkit will not put a
claim in a resume that is not in it. What it is and why it is shaped the way it is:
`docs/Fact_Library_Guide.md`. Here is how to build it. Type these sentences into the Claude
session, one at a time:

1. **"Set up my fact library from the template."** Claude copies the two templates into
   `Fact_Library.md` and `Open_Questions.md`, and asks you for your identity block: your name
   as it should appear on a cover letter, your contact line, and the short form of your name
   used in filenames (for example `Sam_Okafor`). Answer in the chat. It writes them in.
2. **Feed in your history.** Either:
   - open an old resume, copy all of its text, paste it into the chat, and type
     **"propose vignettes from this"**; or, for several documents,
   - **upload PDFs.** The cloud computer Claude works in reads PDF and plain text but not
     Word files, so if an old resume is a `.docx`, open it in Google Docs first and choose
     **File → Download → PDF**. Then on github.com, open your repository at its top level,
     press **Add file → Upload files**, drag the PDFs onto the page, and press **Commit
     changes**. They land at the top of the repository; GitHub does not ask for a folder.
     Back in Claude, type **"I uploaded my old resumes; move them into sources/ and propose
     vignettes."**
3. **Answer its questions.** Claude proposes entries and asks you to confirm or correct each
   one: *"yes"*, *"the number was 90, not 120"*, *"I ran the night shift only"*, *"not sure,
   park it"*. It writes only what you confirm; anything parked goes into `Open_Questions.md`
   for later.

Do this in one or two sittings. You can add to the library any time by pasting another
document and repeating step 2.

## 5. Your first application, by conversation

1. **"Start a new application for Northwind, Operations Coordinator."** Say the real
   company and role. Claude creates a folder for it and tells you the folder's name.
2. **Paste the whole job ad** — select everything on the ad's page, copy, paste into the
   chat — and type **"this is the ad, save it verbatim."** The ad's own words matter: the
   method matches your facts against the ad's vocabulary, so a summary would lose exactly
   the words it needs.
3. **"Research the company, then draft the resume and cover letter, then review them."**
   Three roles run in turn — a researcher, a writer, and a reviewer who can read but never
   edit. Expect questions back, usually about a claim that needs bounding. Answer them.
4. **"Run the checks."** A mechanical lint reads the drafts and reports anything that needs
   attention: a missing header line, a phrase from the ad that your fact library never
   licensed, a duration that does not match your dates. Claude reports the result in full and
   fixes what it can.
5. **"Commit and push."** Claude saves the files to a working branch of its own in your
   repository (its name starts with `claude/`) and tells you so. Two more clicks put them on
   your main branch: press the **Create PR** button on the bar just above the message box
   (one click, no form), then on github.com press the green **Merge pull request** button and,
   when the page expands, the green **Confirm merge** button. The bar in Claude turns purple and
   reads *Merged*. GitHub then offers **Delete branch**; you can ignore it. Every later "commit
   and push" works the same way: a fresh push, then the same two clicks.

<details>
<summary>What Claude runs for you, if you are curious</summary>

```
python3 scripts/new_application.py --candidate Sam_Okafor --company Northwind --role OperationsCoordinator
python3 scripts/mechanical_checks.py Applications/<folder> --facts Fact_Library.md
git add … && git commit … && git push
```

The `.claude/agents/` folder holds the three role definitions, and `CLAUDE.md` holds the
rules that map your sentences to these commands. If Claude mentions that those role
definitions are *not registered* in its environment, it still runs the three roles, carrying
each one's limits in its instructions instead; nothing is lost for you.
</details>

## 6. Get the documents onto your Chromebook, click by click

The resume and cover letter are plain-text files (`.md`). Google Docs opens them directly.
Merge first (step 5.5): github.com shows your main branch, and the files are only there once
the pull request is merged.

1. On github.com, open your repository, then the `Applications` folder, then the folder Claude
   named in step 5.1. Click the resume file — its name starts with your name and `Resume`.
2. Press the **download** button at the top right of the file view (an arrow pointing down
   into a tray). The file lands in your **Downloads** folder.
3. Open **drive.google.com**. Press **New → File upload** and choose the file from Downloads,
   or drag the file from the Files app onto the Drive page.
4. In Drive, right-click the uploaded file and choose **Open with → Google Docs**. You now
   have an editable document with the headings and bullets intact. Tidy anything you like.
5. In Docs, choose **File → Download → PDF Document (.pdf)**, or **Microsoft Word (.docx)** if
   the application form asks for Word. Many do.
6. Repeat for the cover letter.

Check the PDF before you upload it anywhere: it is your name on it.

## 7. Keep the toolkit up to date

The toolkit's author keeps improving it, but your private copy has no link back to the
original: it is a copy, not a fork, so nothing updates it on its own. When you want the
latest version, type:

**"Update the toolkit from github.com/Ian-Lo/application-doc-toolkit."**

Claude fetches the toolkit and replaces its own files — the rules, the guides, the scripts and
the templates — with the current versions, runs their tests, and tells you what changed since
your copy was last updated. Then say **"commit and push"** as usual, and merge the pull
request with the same two clicks as in step 5.5.

Three things to know:

- **Your own files are never touched:** `Fact_Library.md`, `Open_Questions.md`, everything
  under `Applications/` and everything under `sources/`.
- **Toolkit files are replaced whole.** You are not meant to edit them; if you did, the edit
  is overwritten (it stays in your repository's history, so nothing is lost for good). If
  Claude says it refused because a toolkit file has uncommitted changes, say "commit and push"
  first, then ask again.
- **Occasionally a change needs a matching edit to your fact library** — a new line the checks
  read, say. The update names it, and Claude proposes the edit and waits for your yes.

## 8. What the toolkit never does

It never submits anything. Every application form is yours to fill in, and every document is
yours to read before it goes anywhere. The reviewer role is thorough, but it is checking the
draft against *your* fact library; if a fact in the library is wrong, the reviewer will defend
the wrong fact. The library is the thing to keep true.

---

## Appendix — if you are comfortable with a terminal

Everything above runs in the browser. If you would rather work locally, ChromeOS can run a
Linux container: **Settings → About ChromeOS → Developers → Linux development environment →
Turn on**. It is Debian, which Claude Code supports; it needs roughly 10 GB free, and it is
disabled on some school- or work-managed Chromebooks. Once it is running:

```
curl -fsSL https://claude.ai/install.sh | bash
git clone https://github.com/<your-account>/<your-repo>.git
cd <your-repo>
claude
```

Python 3 is already present in the container, and the scripts need nothing else. The same
sentences from sections 4 and 5 work in the terminal session. None of this is required for
anything above.
