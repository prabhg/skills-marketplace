# State file

The state file is the orchestrator's only durable memory. Everything a fresh session needs to resume lives
in its top block. Brief/report files are disposable scratch: useful while a ticket is live, never needed
for a takeover.

## Location

Pick the first that applies; record the chosen path in CURRENT STATE.

1. **The owner or a handoff doc names a path** → use it.
2. **The workspace has a temp-handoff convention** (e.g. a planning repo with `temp/` + `local/` folders and
   a `temp/README.md` index, or a `*-handoff*.md` pattern at the workspace root) → state file in the
   committable temp folder (`<planning>/temp/ORCH-<slug>.md`) with the required header snippet and an index
   row; scratch dir in the gitignored local folder (`<planning>/local/orch-<slug>/`). Commit the state file
   in the planning repo at wave boundaries and at handover only, never on every heartbeat.
3. **Otherwise** → `<workspace-root>/.orchestrator/<slug>/STATE.md`, scratch in
   `<workspace-root>/.orchestrator/<slug>/{briefs,reports,wt}/`. Workspace root = the folder holding the
   product repo(s), not inside one. If the only root is itself a product repo, add `.orchestrator/` to
   `.git/info/exclude` (not `.gitignore`, so nothing in the product repo changes).

Rules: never reference the state file, its folder, ticket ids or the planning repo from product repos
(code, commits, repo docs). `<slug>` = short kebab name of the goal. Search for existing state files first:
`ls <root>/.orchestrator/*/STATE.md <planning>/temp/ORCH-*.md 2>/dev/null`.

## Template

Use absolute UTC timestamps (`date -u +%FT%TZ`). Keep lines short; the file must stay small.

```markdown
> Purpose: orchestration ledger for <goal>; the only durable memory of this run.
> Use: the orchestrator rewrites CURRENT STATE on every state change; a new session resumes from it alone.
> Delete when: all tickets done/parked, durable facts moved to their homes, final report sent.
> Owner: <orchestrator session identity> · Created: YYYY-MM-DD

# ORCH <slug>

## CURRENT STATE   (rewritten on every change — resume from this block alone)
- Goal: <one line> · Skill: autonomous-orchestrator
- Mode: ECONOMY | FULL THROTTLE (since <ts>, per owner "<quote>")
- Phase: orient | plan | decisions | wave N dispatch | wave N review | wave N merge | finish
- Tickets: todo a · in_progress b · in_review c · fixing d · approved e · merged f · done g · blocked h · parked i
- In flight: <agent id/name> | <ticket> | <role> | <tier> | started <ts> | expect <min> | <worktree> @ <branch> | report <path>
- Next action: <one line>
- Blockers awaiting owner: <D-ids / none>
- Approvals: "<verbatim owner text>" — <ts> — scope: <exact action>
- Peers: <session> | role | claimed scope | last contact <ts>
- Orchestrator: <session identity> · heartbeat <ts> · repos: <path:integration-branch@sha, …>
- Scratch: <scratch dir> · Worktrees: <root>
- Takeover: 1) read only this block 2) set Orchestrator + heartbeat to yourself 3) retire previous
  orchestrator if alive 4) reconcile tickets vs `git worktree list` / branches / integration-branch log
  5) resolve In flight (report file exists? worktree progress?) then continue at Next action.

## Tickets
| id | title | repo/area | blocked_by | DoD | risk | tier | status | branch / worktree | review | merge sha |
|---|---|---|---|---|---|---|---|---|---|---|

## Waves
- W1: T1, T2 — dispatched <ts> · merged <ts> · green: `<cmd>` exit 0 @ <sha>

## Decisions (critical, owner-answered)
- D1: <question> — answer "<verbatim>" — <ts>

## Rulings
- Ruling: <decision> — <why> — <cost if wrong>
```

DoD cells may point to the spec file section when long (`spec.md §T3`); the checkable list must exist
somewhere the reviewer can read.

## Update rules

- Rewrite CURRENT STATE (and bump heartbeat) on every state change: dispatch, report received, verdict,
  merge, ruling, approval, peer contact. Record a dispatch **before** sending it, so a crash leaves a trace.
- Tickets table: update the affected rows in the same write (status, review verdict, merge sha) — a top
  block that says `done` over a table that says `in_progress` misleads the next session.
  Waves/Decisions/Rulings: append one line each; never essays.
- Keep every template field and column (DoD included); write `none` instead of dropping one.
- Write with one whole-file write or targeted edits; never append duplicates of CURRENT STATE.
- If the file grows past ~250 lines, move finished-wave detail to a one-line summary per wave.

## Abandonment check (any agent can run this on a found state file)

Judge, in order:

1. **Heartbeat** older than max(2 h, 2× the longest expected duration in In flight)?
2. **No live owner session**: the session-listing tool (if any) shows no running session with the
   Orchestrator identity, or a message to it gets no reply within ~10 min.
3. **Ledger vs git** for every repo listed:
   - `git worktree list` — worktrees named in the ledger that still exist, and any not in the ledger.
   - `git branch -a --no-merged <integration>` — unmerged ticket branches (local and remote).
   - `git log --oneline <integration>` — which ticket merge shas actually landed.
   - In each leftover worktree: `git status --short` and `git log <integration>..HEAD --oneline`
     (uncommitted or unmerged work).

Stale heartbeat + no live session = abandoned. If the owner explicitly told you to take over, skip 1–2:
the instruction is the authority.

**Before deleting an abandoned state file**, all must be true: every ticket is merged, parked or
cancelled, or its unmerged work is preserved on a named branch; uncommitted changes in leftover worktrees
are committed to their branch (never discarded); the list of leftover worktrees and branches is reported
to the owner with a recommendation each; any durable facts are moved to their homes. Otherwise take it over
or ask the owner — do not delete.

## Deletion at the end

Only after: all tickets done/parked/cancelled; durable facts moved (repo docs, architecture docs, memory);
cleanup done; final report sent. Then delete the state file and its scratch dir (and its index row, if
the workspace keeps one; `git rm` in a committed temp folder). Deleting a planning-repo temp file is
not product-data deletion and needs no extra approval.
