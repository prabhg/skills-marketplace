---
name: account-handoff
description: 'Carry a project across Claude account logins on the same machine so work continues uninterrupted. Run it in a fresh session BEFORE logging out of one Claude account (it captures work in flight, live and recent sessions, git/worktree state, and everything that is tied to the account and will not follow), then run it AGAIN in a fresh session after logging in with the other account (it verifies nothing was lost, re-primes memory and project context, checks what this account can and cannot do, and resumes the work). Use whenever the user says they are about to switch, change or log out of their Claude account, hit a usage limit and will move to their work/personal/second account, "prepare this project for an account switch", "I am back on my other account", "warm up this account", "continue where the other account left off", or asks to transfer knowledge, memory, progress or in-flight work between Claude accounts. Works for any number of accounts and repeated round trips.'
license: MIT
metadata:
  category: productivity
  tags: [accounts, handoff, memory, continuity, sessions]
---

# Account handoff

One person, one machine, several Claude accounts (personal Max, a work seat, a second Max). When a usage
limit runs out they log out of one and into another, and want the same project to keep moving.

**The principle that makes this possible:** almost everything that matters is a local file keyed by the
folder path, not by the account: the repos, worktrees, uncommitted changes, the memory directory, `CLAUDE.md`
/ `AGENTS.md`, planning docs, local plugins and skills, CLI logins (`git`, `gh`, cloud CLIs), and every session
transcript. What does **not** follow is short: running processes and sessions, and anything stored with the
account (see [references/account-scope.md](references/account-scope.md)). So a switch needs two things only:
write down what lives in heads and processes before they stop, and re-create or route around what is tied
to the account. This skill does the first on the way out and the second on the way in.

It runs in two phases with the same command. Work out the phase from the files; ask only in the one case
the table below names.

## Where the handoff lives

State directory: the sibling of the project's memory directory, `<memory-dir>/../account-handoff/`
(normally `~/.claude/projects/<project-slug>/account-handoff/`). Use the memory directory named in this
session's system prompt; if there is none, derive the slug from the project root (every non-alphanumeric
character becomes `-`) and confirm the folder exists. It is local, outside every git repo, and shared by all
accounts on this machine. Never put the handoff inside a repository: it names accounts and unfinished work.

| File | Exists | Purpose |
|---|---|---|
| `HANDOFF.md` | only while a handoff is pending | the one pending handoff |
| `snapshot.txt` | only while a handoff is pending | git/worktree/memory snapshot taken at departure, for the arrival diff |
| `accounts.md` | always | one section per account: label, what it has (plan, models, connectors signed in, quirks), last seen |
| `log.md` | always | one line per departure and arrival, newest last, capped at 20 lines |
| `last-handoff.md` | always after the first arrival | the most recent consumed handoff, overwritten each time (a safety copy, not an archive) |

The folder never holds more than these five files. Arrival cleans up after itself; nothing accumulates
from one switch to the next, because the durable record of past work is the session transcripts and the
project's own docs, not old handoffs.

Templates for all of them: [references/templates.md](references/templates.md).

## Decide the phase

1. Identify the current account: the user's account email from session context is the label. If the session
   does not expose one, ask once for a short label ("personal", "work") and reuse the labels already in
   `accounts.md`.
2. Read `HANDOFF.md` if it exists (its header has `status`, `from`, `written`).

| Found | Phase |
|---|---|
| no file, or `status: consumed` | **Depart** |
| `status: pending`, `from` = current account | **Depart again** (the user kept working after the last run): refresh it and say so |
| `status: pending`, `from` ≠ current account | **Arrive** |
| cannot tell the account | ask one question: "Are you about to switch away, or did you just switch in?" |

The user can force a phase by saying "depart", "arrive" or "status" (status = print the table above with
what was found, change nothing).

---

## Phase 1: Depart (before logging out)

Goal: after this, logging out loses nothing. Budget: a few minutes. Do not start new work, merges or deploys.

### 1. Collect what is in flight

Run these read-only collectors first; they are cheap and deterministic:

```bash
bash <skill-dir>/scripts/snapshot.sh "<project-root>" "<memory-dir>" > "<state-dir>/snapshot.txt"
python3 <skill-dir>/scripts/sessions.py "<project-root>" --days 3
```

`snapshot.sh` lists every repo and worktree under the project (branch, head, ahead/behind, modified,
untracked, stashes) and ends with a `summary` line. `sessions.py` digests recent session transcripts (title,
first and last prompt, how the last answer ended; flags `CUT OFF MID-STEP` and `ACTIVE IN LAST 30 MIN`). Pass
`--exclude <this-session-id>` when you know it. The digest is raw chat with credential-looking text masked:
still never copy anything that looks like a login or key into the handoff. Then fill the gaps that only
live in running sessions:

- **Live sessions.** List the other sessions running for this user (`ListAgents` or the session list tool).
  If no such tool exists, treat every session flagged `ACTIVE IN LAST 30 MIN` as possibly live, do not
  message anyone, and ask the user to stop or finish those sessions before logging out. They stop when the account logs out, and each knows things nobody wrote down. Message
  each one once: say the user is about to switch accounts and the session will stop, ask it to bring its
  work to a safe stopping point (no new merges, pushes or deploys; commit work in progress on its own
  branch if the project's rules allow) and to reply with a state blob: objective, repos/branches/worktrees,
  done, in progress, next action, anything it is waiting on, anything only it knows. Wait briefly; a session
  that does not answer is covered by its transcript digest. Tell the user which sessions answered.
- **Background work in this session and others:** subagents, monitors, timers, background shells, dev
  servers. Record what each was doing and the exact command or prompt to restart it. They do not survive.
- **Scheduled work:** cron-style jobs, scheduled tasks, cloud routines or triggers. For each: name, schedule,
  the full prompt, and whether it is local (keeps running) or stored with the account (will not fire for the
  other account). Capture the prompt text now; it cannot be read from the other account.
- **External waits:** CI runs, deploys, open pull requests, reviews requested, questions put to the user
  that are still unanswered, approvals pending. Note where to look and what "done" looks like.
- **The project's own conventions.** If the project keeps a planning folder, an orchestration ledger or a
  handoff directory with its own rules, follow those rules for the detail and link to them from the
  handoff instead of copying. Read enough of each ledger to state its owner and its next action in "Resume
  here". This skill's handoff is the index across accounts, not a second source.

### 2. Make the durable things durable

- **Memory:** save any correction, preference or durable fact from recent work that is not in the memory
  directory yet, following that directory's own rules (one fact per file, index line). Status and progress do
  not belong in memory; they go in the handoff.
- **Code:** uncommitted changes and unpushed commits stay on disk and survive the switch. Do not commit,
  push or stash on the user's behalf just because of the switch. List dirty trees and unpushed branches in
  the handoff so the next session knows they are intentional. Never run a bare `git stash`: stashes are easy
  to lose and the stack is shared by every worktree.
- **Decisions in chat:** anything the user decided in conversation that is not yet in a doc, an issue or
  memory goes into the handoff under "Decided, not yet recorded", with where it should end up.

### 3. Inventory what is tied to the account

Read [references/account-scope.md](references/account-scope.md) and check each item **that this project
actually uses**. For each one in use, write the workaround for the other account: sign the connector in
again, recreate the routine from the saved prompt, open the artifact link while still logged in and save
its content locally, and so on. Skip what the project does not use; an empty section is fine.

### 4. Write the handoff

Write `HANDOFF.md` from the template (header `status: pending`, `from`, `written` with an absolute date and
time). Rules that keep it useful:

- Lead with **"Resume here"**: the three to seven next actions in priority order. Each item names a concrete
  action and the place it happens (repo, branch, worktree, ledger or session). "See the transcripts" is not
  an action. Someone who reads only this section can continue.
- Large workspaces: list only repos and worktrees that have changes, are ahead of their upstream, or belong
  to work in flight. Everything else is already in `snapshot.txt`; give the `summary` line and move on.
- State what may still move: if a session will keep running until logout, say its worktree is expected to
  differ on arrival, so the arrival diff is read as progress and not as damage.
- One line per fact, absolute dates, exact names (branches, worktree paths, issue numbers, shas, job ids).
- No secrets, tokens or passwords, and no session JWTs. Name where a credential lives, never its value.
- Keep it under about 150 lines. Link to transcripts, ledgers and docs by path for detail.
- The first lines of the file must say how to use it without this skill (plugins can be restricted on a
  managed account), as in the template.

Then:

1. Start clean: overwrite any existing `HANDOFF.md` and `snapshot.txt`; write nothing else into the state
   directory (script output goes to the conversation, not to extra files there).
2. Update this account's section in `accounts.md` (create the file on first use). Record only what this
   session can observe: the model it runs on, which connectors and tools are connected or asking for
   sign-in, anything the project needed that was missing. Write "unknown" for the rest; do not interview
   the user about their plan.
3. Append one line to `log.md`.
4. If a memory directory exists, add the pending-handoff memory file and its one index line at the top of
   `MEMORY.md` (template). The index is loaded into every new session, so the next account's first session
   sees the handoff even if the user forgets to run this skill.

### 5. Tell the user it is safe to switch

Reply with a short checklist, nothing else:

1. What was captured (counts: sessions, repos with changes, scheduled items, account-tied items).
2. Anything the user must do **before** logging out (only they can do it): e.g. save an artifact, answer a
   pending prompt in another session, let a running deploy finish.
3. The switch itself: log out, log in with the other account, open a new session **in the same folder**,
   run this skill again.
4. What will be different on the other side, if `accounts.md` already knows that account.

---

## Phase 2: Arrive (after logging in with another account)

Goal: this account knows what the last one knew, and work resumes. Read before acting; change nothing until
step 4.

### 1. Verify nothing was lost

- Confirm the memory index is in this session's context and the memory directory is readable. If the index
  is missing, the session was opened in a different folder: say so and stop (the path is the key).
- Read `HANDOFF.md` fully.
- Take a fresh snapshot and diff it against the saved one:

  ```bash
  bash <skill-dir>/scripts/snapshot.sh "<project-root>" "<memory-dir>" | diff "<state-dir>/snapshot.txt" - 
  ```

  No output means the disk is exactly as it was left. Any difference (a moved head, a new or missing
  worktree, a changed memory index) happened between the two sessions: another tool, a teammate's push
  fetched in, or a session that kept running. Report differences plainly; do not "fix" them.
- If the handoff is more than a few days old, say so and trust the fresh snapshot over the handoff's
  description of state.

### 2. Check what this account can do

Compare against the handoff's "Tied to the account" section and this account's entry in `accounts.md`:

- Models and plan: is the model the work was using available here? If not, name the closest one.
- Connectors and MCP servers the project needs: connected, or waiting for sign-in? List the ones the user
  must authorize (you cannot do it for them). Local servers from the project's own config are unaffected.
- Skills and plugins: locally installed ones are present; account-provided ones may differ. Note any the
  handoff relied on that are missing, and the fallback.
- CLI logins (`gh auth status`, the cloud CLI's identity call) are local and normally still valid: check the
  ones the next actions need, read-only.
- Organization policy: a work seat may log usage to its organization or restrict features. If this account
  is a managed one and the project is personal (or the reverse), remind the user once; it is their call.

### 3. Re-prime, cheaply

Read in this order and stop when the next action is clear: the memory index (already loaded), the project's
entry files (`CLAUDE.md` / `AGENTS.md` and what they tell a new session to read), the handoff, then only
the memory files, docs and transcript tails that "Resume here" points at. Do not re-read the whole corpus:
the point of the handoff is that the next account does not pay for it again.

Session lists in the desktop app are per account, so earlier sessions will not appear in the sidebar. Their
transcripts are still on disk at the paths in the handoff; read the tail of one when a detail is needed.

### 4. Resume

- Show the "Resume here" list with anything that changed since it was written, and start on the first item
  unless the user picks another.
- Restart what stopped, only where the handoff says it should keep running: watchers, timers, dev servers,
  an orchestrator taking over a ledger. Use the recorded command or prompt.
- Re-create account-tied items (scheduled routines, connector sign-ins) only with the user's go-ahead, one
  at a time; creating a routine on a different account is a new outward-facing thing.
- Anything in "Decided, not yet recorded": record it where the handoff says, now. A local doc or memory
  file needs no further go-ahead (the decision was already made); filing an issue, pushing or messaging
  someone does.

### 5. Close the handoff

1. Set the header to `status: consumed`, add `arrived` (date, account), and rename the file to
   `last-handoff.md`, replacing the previous one. Move `snapshot.txt` to the system trash
   (`mv <file> ~/.Trash/` on macOS, `gio trash <file>` on Linux; not `rm`).
2. Sweep the folder: anything other than `accounts.md`, `log.md` and `last-handoff.md` (old `history/`
   folders from earlier versions, stray copies of script output, temp files) goes to the system trash.
   Trim `log.md` to its newest 20 lines.
3. Remove the pending-handoff memory file and its index line.
4. Update this account's section in `accounts.md` with what "Check what this account can do" found (so the
   next arrival here is faster) and append the arrival to `log.md`. Keep each account's section to a few
   lines of current facts: rewrite it, do not append history to it.
5. Report in under ten lines: verified or what differed, what this account lacks, what was resumed, what
   needs the user (sign-ins, decisions).

---

## Things that go wrong

- **The user kept working after departing.** The handoff is stale. That is why "pending from the same
  account" means refresh, and why arrival always diffs a fresh snapshot.
- **Two sessions both ran the departure.** The later one wins (one `HANDOFF.md`); the earlier content is
  still in the transcripts. Prefer running it in one fresh session that polls the others.
- **A session of the old account is still open after the switch.** It may keep writing files with stale
  assumptions. If the arrival diff shows movement nobody on this account made, look for it and tell the user.
- **Cloud or remote sessions.** They keep their memory and state with the account. Work that must cross
  accounts should run in local sessions; say so if the handoff shows cloud sessions holding project state.
- **A different machine.** This skill covers one machine. On another machine the local files are not there:
  that is a job for git and dotfiles sync, and the handoff file would have to travel with them.
- **Never** copy tokens, cookies or app data between account folders to "merge" accounts. The handoff works
  by writing things down, not by impersonating the other login.
