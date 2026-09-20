---
name: end-of-session-cleanup
description: 'End-of-session workspace tidy for any project: prune stale git worktrees, delete branches already merged into the integration branch, reclaim disk from package-manager stores and build caches, fold temp handoff/log/scratch docs into the files of record and delete them, and consolidate dated agent-memory files. Use when the user says "tidy the workspace", "clean up before I stop", "end of session cleanup", "prune worktrees", "delete merged branches", "free up disk", "clean up the handoff docs", or wraps up a long working session. Destructive-adjacent, so it is invoked explicitly, never auto-fired.'
disable-model-invocation: true
license: MIT
metadata:
  category: productivity
  tags: [git, worktrees, branches, housekeeping, memory, disk]
---

# End-of-session cleanup

A repeatable tidy pass over a working directory at the end of a session. Nothing here is
project-specific: every target comes from discovery or from an optional config block, never from
an assumption about how this project is laid out.

**The loop, applied to every one of the six steps below:**

1. **Discover** — enumerate candidates with a read-only command.
2. **Print the literal target list** — full paths, full branch names, one per line. No
   "and 12 others". If the list is empty, say so and move on.
3. **Confirm the rules** — restate which rule admitted each target (merged / stale / superseded)
   and which exclusions were applied.
4. **Act one target at a time** — one command per target, never a chained sweep.
5. **Verify** — re-run the discovery command and show it is gone.
6. **Report** — before/after numbers, plus anything skipped and why.

Steps 1 and 2 are ordered deliberately: a branch checked out in a live worktree cannot be
deleted, so worktrees go first.

## Safety rules that never bend

- **Print before you delete.** A target the user has not seen printed is not a target yet.
- **Never touch a protected branch**, whatever the merge status says.
- **Never force-push. Never `git push --force`, `--force-with-lease`, or `git branch -D`.**
  `git branch -d` only; if it refuses, the branch is not merged and you stop.
- **Never delete unmerged work.** "Merged" means proven, not assumed — see step 2.
- **Other agents' worktrees and branches are read-only.** Anything matching the foreign globs is
  listed in the report as skipped and otherwise untouched.
- **When unsure, skip and report.** An unreclaimed gigabyte costs nothing; a deleted branch costs
  an afternoon.
- **Commit, never push.** Any snapshot commit this routine makes stays local and needs the user's
  explicit yes first.
- **Work one repo at a time** and show the repo path before its targets, so a target list is never
  ambiguous about which repo it belongs to.

## Shell portability

Assume zsh with BSD userland. No GNU-only flags.

- `grep -E` for alternation. Never `\|` in a basic-grep pattern — BSD grep treats it literally.
- Avoid `sed -i` entirely: write to a temp file and `mv` it into place. If you truly need in-place,
  BSD requires a backup suffix argument: `sed -i '' -e '…' file`.
- No `find -printf`, no `readlink -f`, no `date -d`, no `xargs -r`, no `stat -c`.
  Use `stat -f` on BSD, or `git log -1 --format=%cI` for a branch's age.
- `du -sk` (not `--block-size`), `sort -n`.
- Quote every path expansion; worktree paths contain spaces more often than you expect.

## Delegate the reading

The orchestrator's job is the target lists and the confirmations. The bulk reading — step 4's
temp documents and step 5's memory files — is what blows up context. Dispatch a subagent per
document (or per small batch) with instructions to return only: durable facts worth keeping, the
file of record each belongs in, and a verdict of keep / fold / delete. The orchestrator then makes
the edits and the deletions itself, so that the destructive half stays under one pair of eyes.

## Configuration

Everything is discovered by default. A project can pin values by dropping a `tidy` block into its
`CLAUDE.md` or a `.claude/tidy.json` file at the repo root. Read `.claude/tidy.json` first, then
the `CLAUDE.md` block, then fall back to discovery. Full schema and discovery fallbacks:
`references/config.md`.

```json
{
  "integrationBranch": "main",
  "protectedBranchGlobs": ["main", "master", "release/*", "*-prod"],
  "worktreeRoots": ["../worktrees", "~/code/worktrees"],
  "foreignWorktreeGlobs": [".worktrees/*", "feat/agent-*"],
  "tempDocGlobs": ["temp/**", "**/*HANDOFF*", "**/*_LOG_*", "**/*_20??-??-??.md", "**/scratch*"],
  "filesOfRecord": ["docs/ENVIRONMENTS.md", "docs/DECISIONS.md"],
  "issueTracker": "github",
  "memoryDir": "~/.claude/projects/<slug>/memory",
  "staleDays": 14,
  "neverTouch": []
}
```

Never guess `integrationBranch`. Discover it from
`git symbolic-ref refs/remotes/origin/HEAD` (or ask), and say out loud which branch you settled on
before any branch or worktree is judged against it.

---

## Step 1 — Worktrees

```
git worktree list --porcelain
```

per repo, plus a listing of each configured worktree root (some worktrees are registered to a repo
you have not visited yet — `git -C <dir> rev-parse --git-common-dir` tells you which repo a
stray directory belongs to).

A worktree is a candidate only if **either**:

- its branch is merged into the integration branch (see step 2's proof rules), **or**
- it is clean (`git -C <wt> status --porcelain` is empty, no stashes, no unpushed commits versus
  its upstream) **and** its last commit is older than `staleDays`.

Exclude, always: the current working tree, the main worktree, anything matching
`foreignWorktreeGlobs`, anything locked (`git worktree list --porcelain` prints `locked`), and
anything with uncommitted changes or unpushed commits. Print those as skipped with the reason.

Remove one at a time with `git worktree remove "<path>"` — no `--force`. Then
`git worktree prune` and re-list to verify.

`scripts/worktree-report.sh` produces the candidate table (dirty flag, unpushed count, age in days,
merge status) without deleting anything.

## Step 2 — Branches

Merged is a claim you have to prove. Two proofs, in order:

**Ancestry** — `git branch -r --merged "<remote>/<integration>"` and
`git branch --merged "<integration>"`. Anything listed here is genuinely contained.

**Patch identity** — a rebased or squash-merged branch is not an ancestor and will not appear
above. Before treating it as merged, prove the content already landed:

```
git cherry "<remote>/<integration>" "<branch>"       # every line starts with '-' → all applied
git diff "<remote>/<integration>...<branch>"          # empty → nothing unique left
```

Require both signals, or leave the branch alone.

Exclusions: `protectedBranchGlobs`, the integration branch itself, the current branch, any branch
checked out in a live worktree (`git worktree list` names them), branches matching the foreign
globs, and any branch with an open pull/merge request. Match globs with `case "$b" in …)` or
`grep -E` — never with `\|`.

Then, one command per branch, never chained onto the previous one's success:

```
git push origin --delete "<branch>"
git branch -d "<branch>"
```

Delete the remote first, then the local. If `git branch -d` refuses, that branch was not merged
after all — stop, report it, and do not reach for `-D`.

`scripts/merged-branches.sh` lists candidates; it only deletes when given `--delete` *and* an
explicit newline-separated branch list on stdin, so its output can never feed straight back into
itself by accident.

## Step 3 — Disk

Measure first: `du -sk` on the repo root and on any cache directory you intend to touch, saved so
the report can show before and after.

- Package-manager stores, only for managers actually detected in the project (lockfile present or
  binary on `PATH`): `pnpm store prune`, `npm cache verify`, `yarn cache clean`,
  `cargo cache --autoclean`, `pip cache purge`, `go clean -modcache` (this last one is expensive to
  rebuild — confirm it separately).
- `git gc --auto` per repo. Plain `git gc --prune=now` only if the user asks; it discards
  reflog-reachable recovery.
- Build caches (`node_modules`, `dist`, `.next`, `target`, `.turbo`, `__pycache__`) **only** inside
  worktrees already removed in step 1 and inside this session's scratchpad directory. Never inside
  a live checkout — that is the user's next build, not garbage.

Report reclaimed bytes per location and the total.

## Step 4 — Temp documents

Find them with `tempDocGlobs` (discover with the defaults in `references/config.md` if unset).
Typical shapes: a `temp/` or `scratch/` directory, filenames containing `HANDOFF`, `_LOG_`,
`NOTES`, `WIP`, or a trailing date such as `_2024-07-02.md`.

Per document:

1. **Read it fully.** (Delegate: one subagent per doc, returning facts + verdict only.)
2. **Extract the durable facts** — decisions with consequences, environment and pipeline state,
   gotchas that cost someone hours, identifiers that are not derivable — and write them into the
   project's **existing** files of record. Never into a new temp file; that just moves the problem.
3. **Task status belongs in the issue tracker, not in a file.** If a document only restates what
   the tracker already says, it carries nothing durable: delete it. If it holds status the tracker
   is missing, open or update the issue first, then delete.
4. **Snapshot-commit before deleting**, if the documents live in a git repo and the user says yes:
   `git add -A && git commit -m "snapshot before tidy"`. Local only — never push. The point is that
   `git show` can recover anything the extraction missed.
5. **Delete**, one file at a time.
6. **Grep for dangling references** to every deleted filename across the workspace, and repoint
   each hit at the file of record that now holds the content. A pointer to a deleted document is
   worse than no pointer.

## Step 5 — Agent memory

Operate on the memory directory from config or discovery. Do not invent a path; if you cannot
identify it with confidence, skip the step and say so.

- Merge superseded dated state files into **one current-state file per topic**. Keep the newest
  facts, keep anything still open, drop what later files contradict, and note the dates the
  merged content came from.
- Rewrite the index to **one line per remaining file**: filename, then what it answers.
- Repoint every `[[wiki-link]]` that pointed at a merged file.
- **Never delete `feedback`- or `user`-type memories** — those record preferences, not state, and
  nothing supersedes them.
- Keep frontmatter valid on every file you rewrite. Re-read one edited file to confirm the
  delimiters survived.
- Delete the merged-away files only after the index and links are correct.

## Step 6 — Report

Close with a compact table and nothing else:

| Area | Removed / merged | Before | After |
| --- | --- | --- | --- |
| Worktrees | 3 removed | 11 | 8 |
| Branches | 6 remote, 6 local | 24 | 18 |
| Disk | pnpm store, 2 build caches | 41.2 GB | 33.8 GB |
| Temp docs | 4 folded into 2 files of record | 3,410 lines | 0 |
| Memory | 7 files merged into 3 | 61 KB | 28 KB |

Then a **Skipped** list: every candidate that was not acted on, with its one-line reason. That
list is the most useful part of the report — it is the record of what the next session still has
to decide.

Tick through `references/checklist.md` as you go; it is the same routine in checkbox form.
