<!-- source-hash: original -->
# Getting started — on your own computer, with the Claude Code CLI

**This is the preferred way to set up the toolkit.** You install Claude Code on a Mac, a
Windows or a Linux computer, keep your private copy of the toolkit in a folder on that
computer, and type sentences to Claude in a terminal window. Nothing here needs you to know
what the commands do; the guide gives every one of them, and there are about ten in total,
typed once.

There is a second route, `docs/Getting_Started.md`, which runs entirely in the browser on a
Chromebook. It has been tested from a reader's seat and it works, but with limitations that
this route does not have:

- Every save has to go through a pull request: the browser session works on a branch of its
  own and cannot write to your main branch, so each "commit and push" is followed by three
  clicks on two websites.
- The three role definitions the toolkit ships did not register in the browser session, so
  the roles ran from instructions carried in prose instead.
- Your files live on a cloud computer. Old resumes go in through GitHub's upload page, and
  finished documents come out through GitHub's download button, one file at a time.
- The last step, turning a document into PDF or Word through Google Docs, could not be tested
  from the browser session at all.

The CLI has none of these: it writes to your main branch, the roles load from
`.claude/agents/` as designed, your files are ordinary files on your own disk, and the whole
method was built and is run daily this way, so its behaviour is the best understood. Use the
browser route only if a Chromebook is the only computer you have.

Facts about the services and installers below were checked on 2026-09-04. If a screen or a
message does not match this guide, the service has probably changed its wording; the command
or the sentence to type is the part that matters.

## 1. What you need, once

- **A computer running macOS 13 or later, Windows 10 or later, or Ubuntu 20.04 / Debian 10 or
  later**, with 4 GB of memory and an internet connection. On Windows the toolkit runs inside
  WSL (Windows Subsystem for Linux), which section 3 sets up; running it on Windows directly
  is untested with this toolkit.
- **A GitHub account** (free) at github.com. It holds the backup of your private copy and is
  how toolkit updates reach you.
- **A Claude subscription.** Claude Code is not available on the free plan; a **Pro** plan is
  enough to start.
- **A Google account**, only for the last step: Google Docs turns the finished documents into
  PDF or Word.
- **About limits, plainly:** Claude Code shares your subscription's usage limit with everything
  else you do with Claude. One full run — research the company, draft, review — can use a
  sizeable share of a Pro plan's five-hour window, because the method was tuned on a larger
  plan. Do one application first and see how far the limit goes before queueing several.

## 2. Make your own private copy on GitHub

Your copy will hold your employment history, so it must be **private**, and it must stay
private: git history is permanent, and a repository that was public for an hour has published
its contents for good.

1. **Sign in to github.com first** (create an account if you have none). Signed out, the
   toolkit's page shows only *Fork* and *Star*; the button you need does not appear.
2. Open the toolkit's page on github.com (the link you were sent).
3. Press the green **Use this template** button, then **Create a new repository**.
4. Give it a name (`job-applications` is fine). The rest of this guide assumes that name.
5. Find the **Choose visibility** box. It shows a button that says **Public** with a small
   arrow and looks like a label; press it and change it to **Private**. This is the one
   step in this guide that cannot be undone later, so check it says Private before you go on.
6. Press **Create repository**.

You now have your own copy. Nothing you do in it is visible to anyone else, including the
toolkit's author.

## 3. Install the tools, once

You need four things on the computer: **git** (keeps the history and talks to GitHub),
**Python 3** (runs the toolkit's small scripts), **the GitHub command-line tool** (`gh`, which
signs you in to GitHub once so that git never asks for a password), and **Claude Code**. Open
a terminal and type the lines for your system, one at a time, pressing Enter after each.

**How to open a terminal.** macOS: press Cmd+Space, type `Terminal`, press Enter. Windows:
after the WSL step below, open the **Ubuntu** app from the Start menu; that *is* your
terminal for everything in this guide. Ubuntu: press Ctrl+Alt+T.

### macOS

1. Type `git --version`. If a dialog offers to install the *command line developer tools*,
   press **Install** and wait; it brings git and Python 3 together. When it finishes, type the
   line again and it prints a version.
2. Install the GitHub tool: download and run the macOS installer from
   [cli.github.com](https://cli.github.com), or, if you already use Homebrew, type
   `brew install gh`.
3. Install Claude Code:

   ```
   curl -fsSL https://claude.ai/install.sh | bash
   ```

   Close the terminal window and open a new one, so the `claude` command is found.

### Windows, through WSL

1. Open **PowerShell as administrator** (right-click the Start button → *Terminal (Admin)* or
   *Windows PowerShell (Admin)*) and type `wsl --install`. Restart the computer when it asks.
   After the restart an **Ubuntu** window opens and asks you to choose a username and a
   password for Linux; they are separate from your Windows login. From here on, every command
   in this guide is typed into that Ubuntu window, never into PowerShell.
2. In the Ubuntu window:

   ```
   sudo apt update && sudo apt install -y git python3 gh curl
   ```

   `sudo` asks for the Linux password you just chose. Nothing appears while you type it;
   that is normal.
3. Install Claude Code, still in the Ubuntu window:

   ```
   curl -fsSL https://claude.ai/install.sh | bash
   ```

   Close the Ubuntu window and open it again.

One thing to know about WSL: your files live in the Linux part of the computer. Windows
Explorer shows them under **Linux → Ubuntu → home → your username** in its left sidebar, and
you will need that path in section 8 to hand a finished document to Google Docs.

### Ubuntu or Debian

```
sudo apt update && sudo apt install -y git python3 gh curl
curl -fsSL https://claude.ai/install.sh | bash
```

Close the terminal and open a new one.

### Check, on any system

```
claude --version
```

prints a version number such as `2.1.211 (Claude Code)`. If it says *command not found*, open
a fresh terminal window and try again; if it still fails, type `claude doctor` and follow its
suggestion. Claude Code installed this way updates itself in the background; you never
reinstall it.

## 4. Put your copy on the computer, once

1. Sign in to GitHub from the terminal:

   ```
   gh auth login
   ```

   It asks a few questions. Choose **GitHub.com**, **HTTPS**, answer **Yes** to
   *Authenticate Git with your GitHub credentials*, and choose **Login with a web browser**.
   It shows an eight-character code and opens github.com; type the code there and approve.
   This is done once; from now on git can reach your private repository without asking.

2. Tell git who you are. Use the name and the email address of your GitHub account:

   ```
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```

3. Download your copy. Replace `your-account` with your GitHub username:

   ```
   gh repo clone your-account/job-applications
   cd job-applications
   ```

   You now have a folder called `job-applications` in your home folder. Everything the
   toolkit does happens inside it, and `cd job-applications` is how you step into it: type it
   at the start of every session before typing `claude`.

## 5. Start Claude Code in the folder, once

1. Type `claude` and press Enter. The first time, it asks you to log in: choose the
   **Claude account with subscription** option, a browser page opens, sign in, and come back
   to the terminal.
2. It then asks whether you trust the files in this folder. Answer **Yes**: the folder is your
   own copy, and the toolkit's rules in `CLAUDE.md` load from it.
3. You are now in a conversation. Type sentences at the prompt at the bottom; Claude answers
   above it. Pressing **Esc** stops whatever it is doing; typing `/exit` ends the session.
   Closing the terminal window ends it too, and nothing is lost: the files are on disk.

**Permissions.** Claude asks before it does most things. The toolkit ships a permissions file
that pre-approves every command this guide will make it run — the scripts, the git commands,
and the web searches and page fetches that company research needs — so those run without a
question. It still asks before editing a file. The first time it does, a box appears naming
the file; choose **Yes**. You may see an option to allow edits for the rest of the session;
choosing it is safe, because everything in this folder is yours. Another way to say the same
thing: press **Shift+Tab** once and the line under the prompt reads *accept edits on*; press it
again to go back.

If Claude ever asks permission for something you do not understand, say **No** and ask it, in
plain words, what it was about to do and why. It will tell you, and nothing has happened yet.

## 6. Build your fact library, by conversation

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
   - **put the files in a `sources` folder.** In Finder or Explorer, open the
     `job-applications` folder, make a new folder inside it called `sources`, and copy your
     old resumes and cover letters into it. Claude reads PDF and plain text but not Word
     files; if an old resume is a `.docx`, open it in Word or Google Docs first and save it
     as PDF. Then type **"read my old resumes in sources/ and propose vignettes."**
3. **Answer its questions.** Claude proposes entries and asks you to confirm or correct each
   one: *"yes"*, *"the number was 90, not 120"*, *"I ran the night shift only"*, *"not sure,
   park it"*. It writes only what you confirm; anything parked goes into `Open_Questions.md`
   for later.

Do this in one or two sittings. You can add to the library any time by pasting another
document or dropping another file into `sources/` and repeating step 2.

When the library has taken shape, type **"commit and push."** Claude saves the files to your
repository on GitHub, straight to your main branch. It is a private repository with a single
author, so there is no pull request and nothing to click on github.com.

## 7. Your first application, by conversation

1. **"Start a new application for Northwind, Operations Coordinator."** Say the real
   company and role. Claude creates a folder for it under `Applications/` and tells you the
   folder's name.
2. **Paste the whole job ad** — select everything on the ad's page, copy, paste into the
   chat — and type **"this is the ad, save it verbatim."** The ad's own words matter: the
   method matches your facts against the ad's vocabulary, so a summary would lose exactly
   the words it needs.
3. **"Research the company, then draft the resume and cover letter, then review them."**
   Three roles run in turn — a researcher, a writer, and a reviewer who can read but never
   edit. Their definitions load from `.claude/agents/`, and in a terminal session they do
   register, so Claude names them as it hands over. Expect questions back, usually about a
   claim that needs bounding. Answer them.
4. **"Run the checks."** A mechanical lint reads the drafts and reports anything that needs
   attention: a missing header line, a phrase from the ad that your fact library never
   licensed, a duration that does not match your dates. Claude reports the result in full and
   fixes what it can.
5. **"Commit and push."** The application folder and any library edits go to your main
   branch on GitHub. Done.

<details>
<summary>What Claude runs for you, if you are curious</summary>

```
python3 scripts/new_application.py --candidate Sam_Okafor --company Northwind --role OperationsCoordinator
python3 scripts/mechanical_checks.py Applications/<folder> --facts Fact_Library.md
git add … && git commit … && git push
```

`CLAUDE.md` holds the rules that map your sentences to these commands, and `.claude/agents/`
holds the three role definitions with their tool limits. You can read both; you are not meant
to edit them, because section 9 replaces them.
</details>

## 8. Turn the documents into PDF or Word

The resume and cover letter are plain-text files (`.md`) in the application's folder under
`Applications/`, on your own disk. Google Docs opens them directly and exports both formats.

1. Find the folder. macOS and Ubuntu: your home folder → `job-applications` → `Applications`
   → the folder Claude named in step 7.1. Windows: in Explorer's left sidebar, **Linux →
   Ubuntu → home → your username → job-applications → Applications**, then that folder.
2. Open **drive.google.com**. Drag the resume file — its name starts with your name and
   `Resume` — onto the Drive page, or press **New → File upload** and choose it.
3. In Drive, right-click the uploaded file and choose **Open with → Google Docs**. You now
   have an editable document with the headings and bullets intact. Tidy anything you like.
4. In Docs, choose **File → Download → PDF Document (.pdf)**, or **Microsoft Word (.docx)** if
   the application form asks for Word. Many do.
5. Repeat for the cover letter.

Check the PDF before you upload it anywhere: it is your name on it.

## 9. Keep the toolkit up to date

The toolkit's author keeps improving it, but your private copy has no link back to the
original: it is a copy, not a fork, so nothing updates it on its own. When you want the
latest version, type:

**"Update the toolkit from github.com/Ian-Lo/application-doc-toolkit."**

Claude fetches the toolkit and replaces its own files — the rules, the guides, the scripts and
the templates — with the current versions, runs their tests, and tells you what changed since
your copy was last updated. Then say **"commit and push"** as usual.

Three things to know:

- **Your own files are never touched:** `Fact_Library.md`, `Open_Questions.md`, everything
  under `Applications/` and everything under `sources/`.
- **Toolkit files are replaced whole.** You are not meant to edit them; if you did, the edit
  is overwritten (it stays in your repository's history, so nothing is lost for good). If
  Claude says it refused because a toolkit file has uncommitted changes, say "commit and push"
  first, then ask again.
- **Occasionally a change needs a matching edit to your fact library** — a new line the checks
  read, say. The update names it, and Claude proposes the edit and waits for your yes.

## 10. Every later session

Open a terminal, then:

```
cd job-applications
claude
```

Type `claude -c` instead of `claude` to pick up the previous conversation where it stopped,
for instance a fact-library session you paused halfway. Nothing else needs repeating: the
login, the trust answer and the GitHub sign-in from sections 4 and 5 are remembered.

## 11. What the toolkit never does

It never submits anything. Every application form is yours to fill in, and every document is
yours to read before it goes anywhere. The reviewer role is thorough, but it is checking the
draft against *your* fact library; if a fact in the library is wrong, the reviewer will defend
the wrong fact. The library is the thing to keep true.
