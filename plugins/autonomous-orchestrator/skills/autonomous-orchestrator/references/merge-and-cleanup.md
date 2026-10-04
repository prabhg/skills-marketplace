# Merge waves, green builds, cleanup, finish

## Worktrees

- Location: repo convention first (its AGENTS.md may name one). Default: `<scratch>/wt/<repo>-<ticket>`,
  created by you or a haiku helper: `git -C <repo> worktree add <path> -b <branch> <integration>`.
  Branch name: repo convention, else `orch/<slug>/<ticket>`.
- A harness "isolated worktree" option is fine if the subagent reports the branch and path; record them.
- Install dependencies per worktree only as the repo documents; note slow installs in expected durations.

## Merging a wave (integrator subagent, sonnet; haiku for trivial single-repo waves)

Only branches with `review: APPROVE` (and a scoped re-review for any later commit) are merged.

```
ROLE: integrator. Tier: <sonnet|haiku>. Repo <path>, integration branch <name> (main checkout <path>).
MERGE IN ORDER: <branch → ticket>, … (each was reviewed and approved at head <sha>; refuse any branch
  whose head differs).
STEPS: ensure the main checkout is clean and on <integration>; `git merge --no-ff <branch> -m "<repo
  merge style>"` for each; on conflict: resolve only if both sides' intent is clear from the tickets'
  DoD (<pointers>), else `git merge --abort` and report BLOCKED with the conflicting files.
GREEN: run <build/test/lint commands> on the merged integration branch. Paste command, exit code, result line.
PUSH: <only if Approvals allow: `git push origin <integration>`; else "do not push">.
DO NOT: force-push, rebase shared branches, delete anything, touch other branches.
REPORT FILE: <path>. RETURN (≤100 words): merge sha per ticket, green evidence, conflicts resolved (files).
```

Then you verify with one command (`git log --oneline -n <k> <integration>`), set tickets `merged` → `done`
when green, and log the wave line. A conflict resolution counts as new code: have it reviewed (scoped)
before marking done.

**Red after merge:** dispatch a fixer on a new branch off the integration branch with the failing output
path, review it, merge it. Do not start the next wave on a red integration branch unless the next wave's
tickets cannot be affected (log a Ruling).

## Cleanup (after the final wave is green; a haiku helper can do it)

Print the exact target list first (paths and branch names), then act one target at a time:

1. `git worktree remove <path>` for every ticket worktree whose branch is merged; then `git worktree prune`.
2. `git branch -d <branch>` for merged ticket branches (`-d` only; refusal = not merged = stop and report).
3. Remote: `git push origin --delete <branch>` only if approved in Approvals; otherwise list them in the
   final report as a request.
4. Never touch branches or worktrees the ledger does not own (peers, other sessions, the owner's own).
5. Verify: re-run `git worktree list` and `git branch -a` and show they are gone.

## Docs treeshake (sonnet docs subagent)

Brief: update the repo docs that the delivered work made stale (READMEs, architecture docs, env docs)
to describe the current state only; remove superseded sections and duplicate content; link instead of
restating; no decision history (cite `repo@sha` where needed); keep each doc short. Durable facts that
belong in agent memory (env mappings, gotchas, conventions) go to memory files, one fact per file per
the harness's memory conventions. Commit in the repo on the integration branch per its rules — it is a
code change like any other: reviewed before merge (a doc-only diff can share a batch review).

Temp docs created by this run (briefs, reports, spec, ticket drafts) are not kept: fold anything durable
into the docs above, then delete the scratch dir.

## Finish

1. All tickets `done`, `parked` (with Ruling) or `cancelled`; integration branch green with evidence.
2. Cleanup + treeshake done.
3. Final report to the owner (format in SKILL.md) — includes every Ruling.
4. Delete the state file and scratch dir (and its index row / `git rm` in a committed temp folder).
5. If the run was a takeover, confirm the old session is retired or tell the owner it can be closed.
