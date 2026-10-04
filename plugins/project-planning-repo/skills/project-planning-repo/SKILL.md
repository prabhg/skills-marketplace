---
name: project-planning-repo
description: 'Create or maintain a private `project/` delivery-planning git repo (branch `planning`) inside a multi-repo wrapper folder: one central cross-repo ARCHITECTURE.md and BACKLOG.md, temp/local handoff folders with purpose + clean-when headers, a closed-ticket archive agents do not load, and the rules that repos never reference it and that it is re-synced after every dev fetch. Use when the user asks to "set up a project folder", "central backlog/architecture across repos", "planning repo", "move handoffs/research/plans into project/", "scan all repos and list risks as tickets", or to sync/treeshake an existing project/ folder.'
license: MIT
metadata:
  category: productivity
  tags: [planning, backlog, architecture, handoffs, multi-repo, docs-hygiene]
---

# project/ — delivery-planning repo

A wrapper folder (usually **not** a git repo) holds several product repos. `project/` sits directly under it and
is a **separate git repo on branch `planning`** that is **not part of the product**. It holds planning and
management docs needed only by whoever leads delivery (the owner, maybe one senior engineer) — never the team.

## Invariants (state these to the user and encode them in `project/AGENTS.md`)

1. **No repo ever references `project/`** — no paths, ticket ids or doc names in code, comments, commits, PR
   bodies or repo docs. Each product repo keeps its own reference docs (incl. its own architecture doc) in its own
   `docs/`. Repo docs *may* reference another product repo's docs but ideally don't (it may not be cloned).
2. **Delivery-planning docs live in `project/docs/`** (cross-repo architecture, backlog, backend/system designs
   and their research, feature plans/task briefs not needed by repo devs).
3. **Sync on fetch** — any agent that fetches/pulls `dev` (or the integration branch) of any repo, or scans it for
   latest code, runs `git log <synced sha>..origin/<branch>`, updates ARCHITECTURE/BACKLOG, bumps the `synced:`
   stamp, and commits in `project/`. Repo code wins over these docs.
4. **Temp docs** (`temp/` committable, `local/` gitignored) — enforced by every agent that reads or writes
   `project/`: each starts with a `> Purpose / > Use / > Delete when / > Owner · Created` snippet (temp/ ones also
   indexed in `temp/README.md`). Delete as soon as not needed: session-state handoffs (pre-`/compact`,
   agent→agent) and knowledge-transfer notes are deleted by the **next agent right after reading** (durable facts
   go to a main doc / repo doc / memory first). Every touch of `project/` sweeps both folders for docs whose
   delete-when holds. Delete = `git rm` (temp/) or `~/.Trash` (local/).
4a. **Small and few.** Every doc costs context for every agent that reads it: prefer editing an existing doc,
   delete what no longer earns its place, never keep superseded versions of a doc (fold what's still true into
   the current one, then delete the old).
5. **Treeshake** main docs on every edit: current state only, no decision history (cite `repo@sha`), compressed,
   link into repo docs instead of restating. ARCHITECTURE ≤ ~200 lines; BACKLOG = open tickets only; closed
   tickets move to `docs/archive/BACKLOG-CLOSED.md` (one line each, never loaded on start).
6. No secrets in `project/`; absolute dates only.

## Setup workflow

Do these in order. Read-only discovery first; anything destructive is printed and confirmed.

1. **Orient.** Confirm the wrapper root (`ls -la`, which children have `.git`). Read the wrapper `AGENTS.md`/
   `CLAUDE.md` and each repo's agent rules. Recall project memory. `git fetch --prune` each repo; note branch,
   ahead/behind, stashes, worktrees.
2. **Inventory loose material** at the wrapper root: handoff docs, plans, research folders, design mocks.
   Grep every hardcoded path to them first (memory files, wrapper `AGENTS.md`, scheduled routines/triggers, skills,
   tool READMEs, symlinks) — moving breaks these silently.
3. **Create the skeleton** from `references/templates.md`: `project/{AGENTS.md,.gitignore}`,
   `docs/{ARCHITECTURE.md,BACKLOG.md}`, `docs/archive/BACKLOG-CLOSED.md`, `temp/README.md`, `local/README.md`.
   Gitignore `local/*` (keep its README) and anything that is someone else's confidential material.
4. **Move** loose material in (`mv`, keep folder names to limit broken references). Then **triage each handoff**
   against the current code/branches: still valid → `temp/` + snippet + index row (add a dated drift note if facts
   moved); superseded or done → port open items to BACKLOG, record in the closed archive, move file to `~/.Trash`.
   If a read of a doc is blocked, track its metadata in `temp/README.md` instead and tell the user.
5. **Scan repos** with parallel read-only subagents (one per repo/area: app code, shared packages, CI/release +
   docs drift, design docs). Ask each for (A) a compressed architecture summary with paths and (B) risk findings
   with severity, `file:line` evidence, why, fix, and PLAUSIBLE for unverified claims. Correct any wrong premise in
   your own prompt (e.g. local vs remote branch drift) before ticketing.
6. **Verify** every critical/high claim by reading the cited lines yourself; downgrade or mark PLAUSIBLE otherwise.
7. **Write ARCHITECTURE.md** (bird's-eye: repo map incl. planned repos, per-repo shape, delivery pipeline,
   environments, cross-repo contracts/invariants, section index into long design docs) and **BACKLOG.md**
   (tickets `P-###`, severity, repos, gate, evidence `path:line @sha`, fix; group lows into bundles). Stamp both
   with `synced: <repo> <branch> @ <sha> · <date>`.
8. **Move planning docs out of repos** only when the user asks or confirms which: move files into
   `project/docs/<same subpath>`, `git rm` in the repo, rewrite repo docs that pointed at them (no path to
   `project/`), commit on the repo's working branch locally; **ask before pushing**. Repoint paths inside the moved
   docs and in ARCHITECTURE/BACKLOG/memory.
9. **Wrapper rules:** add a short always-applies section to the wrapper `AGENTS.md` (read-on-load list, sync rule,
   never-reference rule, commit-in-project rule) — `project/AGENTS.md` only loads lazily.
10. **Git:** `git -C project init -b planning && git -C project add -A && git -C project commit -m "chore: initial planning repo"`.
    Check `git check-ignore` on confidential files and sizes (`find project -size +20M`) before committing.
11. **Memory:** save a feedback memory with the invariants + why, update layout/env memories and fix every path
    you moved. If another memory dir exists for sessions opened inside a repo, mirror the rule there too.
12. **Report** tersely: what moved/trashed (and that Trash is recoverable), critical tickets, memory corrections,
    any blocked step, and y/n questions for repo commits/pushes.

## Maintenance (any later session)

- On start: read `project/AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/BACKLOG.md`, `temp/README.md`.
- After fetching a repo: run the sync rule; close fixed tickets (archive line with `repo@sha`), add new ones,
  bump `next id`, commit.
- Sweep `temp/` + `local/`: delete docs whose delete-when holds; if you read a handoff/knowledge-transfer note,
  delete it once its facts are absorbed; add the snippet to any temp doc missing it (or ask the owner).
- Treeshake any main doc you touch; fold superseded doc versions into the current one and delete them.

## Gotchas

- Subagent claims about branch drift often compare a stale **local** branch with its remote — check `origin/*`.
- A repo doc that names the wrapper folder (`<wrapper>/...`) breaks the never-reference rule once material moves.
- Moving deletes nothing in git for the wrapper (not a repo): deletions go to `~/.Trash`, never `rm`.
- Large binaries (mocks, videos) are fine locally; flag GitHub's 100 MB limit / LFS before adding a remote.
