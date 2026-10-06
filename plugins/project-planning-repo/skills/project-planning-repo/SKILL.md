---
name: project-planning-repo
description: 'Create or maintain a private `project/` delivery-planning git repo (branch `planning`) inside a multi-repo wrapper folder: one central cross-repo ARCHITECTURE.md and BACKLOG.md, temp/local handoff folders with purpose + clean-when headers, a closed-ticket archive agents do not load, and the rules that repos never reference it and that it is re-synced after every dev fetch. Use when the user asks to "set up a project folder", "central backlog/architecture across repos", "planning repo", "move handoffs/research/plans into project/", "scan all repos and list risks as tickets", or to sync/treeshake an existing project/ folder, or to enable/disable GitHub Issues tracking for it.'
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
7. **Optional GitHub Issues tracking** (opt-in, see below). When enabled, issues are the only task status;
   `issues/BACKLOG.md` is a generated, read-only snapshot and replaces `docs/BACKLOG.md` + the closed archive.

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
10a. **Offer GitHub Issues tracking** if `project/` has (or will get) a GitHub remote — see next section.
11. **Memory:** save a feedback memory with the invariants + why, update layout/env memories and fix every path
    you moved. If another memory dir exists for sessions opened inside a repo, mirror the rule there too.
12. **Report** tersely: what moved/trashed (and that Trash is recoverable), critical tickets, memory corrections,
    any blocked step, and y/n questions for repo commits/pushes.

## GitHub Issues tracking (optional)

**Ask; never assume.** When `project/` is (or will be) a git repo with a GitHub remote, ask: "Track tasks as
GitHub Issues on `<owner>/<repo>`? Issues become the single task status; a script pulls them into a committed,
read-only `issues/BACKLOG.md` snapshot so agents can read the backlog offline." Default = off (markdown backlog).

If yes, get each permission explicitly (one y/n list) and record the answers:
1. `gh auth status` shows the right account with `repo` scope (else the user runs `gh auth login` /
   `gh auth refresh -s repo` themselves).
2. OK to create the label set.
3. OK to create, comment on and close issues on their behalf (bulk actions still ask each time).
4. OK to migrate the existing `docs/BACKLOG.md` (and closed archive) into issues.

Then, from `references/templates.md` → *GitHub Issues tracking*:
- Create labels (`type:` · `severity:` · `status:` · `repo:<name>` per repo). Print the list before creating.
- Migrate: for each open ticket, check all-state issues for its marker `<!-- planning-import:<id> -->` first
  (idempotent), create the issue, record `id → URL` in `issues/README.md` immediately. Closed archive rows stay
  as historical lines in that ledger, not new issues. Then `git rm docs/BACKLOG.md docs/archive/BACKLOG-CLOSED.md`.
- Add `management/scripts/refresh_backlog.py`, run it, commit the snapshot.
- Swap in the tracking rules + `## Tracking` block in `project/AGENTS.md` (enabled · date · repo · granted
  permissions) and the issues line in the wrapper `AGENTS.md` section.
- Push only the `planning` branch, never `main`; ask before the first push.

If no: record `github-issues: disabled · <date>` in the `## Tracking` block so later sessions don't re-ask.

## Change tracking later

The user may enable or disable tracking at any time; the `## Tracking` block is the state of record.
- **Enable:** run the full opt-in above (ask + permissions, even if granted before). Ask again before any bulk
  create/close (more than ~5 issues), stating the exact list.
- **Disable:** confirm, then stop all GitHub writes; keep the last `issues/BACKLOG.md` (mark it final + date);
  seed `docs/BACKLOG.md` (open items, keep issue links) and the closed archive from it; restore markdown
  backlog rules in `project/AGENTS.md`; set the block to `disabled · <date>`; commit. **Never delete issues**,
  labels or the snapshot.
- Permissions change only by the user's own words in chat; update the block whenever they do.

## Maintenance (any later session)

- On start: read `project/AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/BACKLOG.md` (or, with tracking on, the
  refreshed `issues/BACKLOG.md`), `temp/README.md`.
- After fetching a repo: run the sync rule; close fixed tickets (archive line with `repo@sha`, or close the issue
  with evidence when tracking is on), add new ones, bump `next id`, commit.
- Sweep `temp/` + `local/`: delete docs whose delete-when holds; if you read a handoff/knowledge-transfer note,
  delete it once its facts are absorbed; add the snippet to any temp doc missing it (or ask the owner).
- Treeshake any main doc you touch; fold superseded doc versions into the current one and delete them.
- **Tracking enabled** (check the `## Tracking` block first):
  - Run `python3 management/scripts/refresh_backlog.py` before reading the backlog; if it fails, call the snapshot
    stale and infer nothing new/resolved from it. Search GitHub before creating an issue; refresh + commit after
    any remote change. Never hand-edit the snapshot.
  - Status lives only in issues — never in docs, handoffs or memory (they may link issues).
  - Close when merged to the integration branch with a green build, with an evidence comment (`repo@sha`, PR,
    verification, limits). Out-of-date → close as *not planned* with the reason. Partly done → dated status
    comment (`YYYY-MM-DD: done … / left …`), keep open.
  - Only actions within the granted permissions; anything else, ask.

## Gotchas

- Subagent claims about branch drift often compare a stale **local** branch with its remote — check `origin/*`.
- A repo doc that names the wrapper folder (`<wrapper>/...`) breaks the never-reference rule once material moves.
- Moving deletes nothing in git for the wrapper (not a repo): deletions go to `~/.Trash`, never `rm`.
- Large binaries (mocks, videos) are fine locally; flag GitHub's 100 MB limit / LFS before adding a remote.
