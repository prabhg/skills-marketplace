# Tidy checklist

Tick each line. A line you cannot tick is a line you report as skipped.

## Before anything

- [ ] Working tree of the current repo is committed or deliberately left dirty (and noted).
- [ ] Config loaded from `.claude/tidy.json` / `CLAUDE.md`, or discovery fallbacks recorded.
- [ ] Integration branch identified and stated out loud.
- [ ] Protected globs, foreign globs and `neverTouch` listed before any candidate is judged.
- [ ] `du -sk` baseline captured for the repo roots and cache dirs in scope.

## 1. Worktrees

- [ ] `git worktree list --porcelain` run per repo; configured worktree roots also listed.
- [ ] Candidate table printed: path, branch, dirty?, unpushed count, age, merged?.
- [ ] Locked, dirty, unpushed, current, main and foreign worktrees excluded with reasons shown.
- [ ] Each removal a separate `git worktree remove "<path>"`, no `--force`.
- [ ] `git worktree prune` run; list re-read to verify.

## 2. Branches

- [ ] Ancestry pass: `git branch -r --merged` and `git branch --merged`.
- [ ] Rebased/squashed candidates proven by **both** `git cherry` (all `-`) and an empty
      `git diff <integration>...<branch>`.
- [ ] Protected, current, worktree-checked-out, foreign and open-PR branches excluded.
- [ ] Literal branch list printed and confirmed before the first delete.
- [ ] One `git push origin --delete <b>` per command; not chained after a merge or another delete.
- [ ] Local deletes use `git branch -d` only. A refusal stops the branch, no `-D`.
- [ ] Remote and local branch counts re-read after.

## 3. Disk

- [ ] Only detected package managers pruned; `go clean -modcache` confirmed separately if used.
- [ ] `git gc --auto` per repo (aggressive/`--prune=now` only on explicit request).
- [ ] Build caches touched only in removed worktrees and the session scratchpad.
- [ ] `du -sk` after; reclaimed bytes per location recorded.

## 4. Temp docs

- [ ] Candidate list printed with line counts.
- [ ] Every doc read in full (delegated to subagents; only facts + verdict returned).
- [ ] Durable facts written into existing files of record — no new temp file created.
- [ ] Status moved to the issue tracker; docs that only restate the tracker marked for deletion.
- [ ] Snapshot commit made (local only, never pushed) with the user's yes.
- [ ] Deletions done one file at a time.
- [ ] `grep -R` for each deleted filename; every dangling reference repointed.

## 5. Memory

- [ ] Memory dir identified with confidence, or step skipped and reported.
- [ ] Dated/superseded files merged into one current-state file per topic.
- [ ] Index rewritten to one line per remaining file.
- [ ] `[[links]]` repointed.
- [ ] `feedback` / `user` memories untouched.
- [ ] Frontmatter valid on every rewritten file (one re-read to confirm).
- [ ] Merged-away files deleted only after index and links are correct.

## 6. Report

- [ ] Table of removed/merged with before and after counts, bytes and lines.
- [ ] Skipped list with a one-line reason per item.
- [ ] Nothing was force-pushed, force-deleted, or pushed at all.
