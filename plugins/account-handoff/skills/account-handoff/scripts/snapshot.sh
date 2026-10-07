#!/usr/bin/env bash
# Stable, diff-friendly snapshot of the local state that must survive an account switch.
#   bash snapshot.sh [project-root] [memory-dir]
# Read-only. Prints one line per repo and per extra worktree, sorted, so two runs can be diffed.
set -uo pipefail
ROOT="${1:-$PWD}"
MEM="${2:-}"
cd "$ROOT" || { echo "cannot cd to $ROOT" >&2; exit 1; }
ROOT="$(pwd -P)"

repo_line() {
  local d="$1" rel branch head up ahead behind dirty untracked stash
  rel="${d#"$ROOT"/}"; [ "$d" = "$ROOT" ] && rel="."
  branch="$(git -C "$d" symbolic-ref --quiet --short HEAD 2>/dev/null || echo DETACHED)"
  head="$(git -C "$d" rev-parse --short HEAD 2>/dev/null || echo none)"
  up="$(git -C "$d" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo no-upstream)"
  ahead=0; behind=0
  if [ "$up" != "no-upstream" ]; then
    ahead="$(git -C "$d" rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)"
    behind="$(git -C "$d" rev-list --count 'HEAD..@{u}' 2>/dev/null || echo 0)"
  fi
  dirty="$(git -C "$d" status --porcelain 2>/dev/null | grep -vc '^??' || true)"
  untracked="$(git -C "$d" status --porcelain 2>/dev/null | grep -c '^??' || true)"
  stash="$(git -C "$d" stash list 2>/dev/null | wc -l | tr -d ' ')"
  echo "repo $rel | branch=$branch head=$head upstream=$up ahead=$ahead behind=$behind modified=$dirty untracked=$untracked stashes=$stash"
}

echo "# snapshot root=$ROOT"
{
  # the root itself (if it is a repo) and git repos up to two levels down
  find "$ROOT" -maxdepth 3 -name .git -not -path '*/node_modules/*' 2>/dev/null | while read -r g; do
    d="$(dirname "$g")"
    # a worktree's .git is a file; worktrees are listed under their main repo below
    [ -d "$g" ] || continue
    repo_line "$d"
    git -C "$d" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}' | while read -r w; do
      [ "$w" = "$d" ] && continue
      [ -d "$w" ] || { echo "worktree ${w#"$ROOT"/} | MISSING on disk (of ${d#"$ROOT"/})"; continue; }
      wb="$(git -C "$w" symbolic-ref --quiet --short HEAD 2>/dev/null || echo DETACHED)"
      wh="$(git -C "$w" rev-parse --short HEAD 2>/dev/null || echo none)"
      wd="$(git -C "$w" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
      echo "worktree ${w#"$ROOT"/} | of=${d#"$ROOT"/} branch=$wb head=$wh changes=$wd"
    done
  done
} | sort > "${TMPDIR:-/tmp}/account-handoff-snap.$$"
cat "${TMPDIR:-/tmp}/account-handoff-snap.$$"
awk '
  /^repo /     { r++; if ($0 !~ /modified=0 untracked=0/) rc++; if ($0 !~ / ahead=0 /) ra++; if ($0 !~ /stashes=0/) rs++ }
  /^worktree / { w++; if ($0 !~ /changes=0$/ ) wc++ }
  END { printf "summary | repos=%d repos_with_changes=%d repos_ahead_of_upstream=%d repos_with_stashes=%d worktrees=%d worktrees_with_changes=%d\n", r, rc, ra, rs, w, wc }
' "${TMPDIR:-/tmp}/account-handoff-snap.$$"
rm -f "${TMPDIR:-/tmp}/account-handoff-snap.$$"

if [ -n "$MEM" ] && [ -d "$MEM" ]; then
  n="$(find "$MEM" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
  idx="none"; [ -f "$MEM/MEMORY.md" ] && idx="$(shasum "$MEM/MEMORY.md" | cut -c1-12)"
  bytes="$(cat "$MEM"/*.md 2>/dev/null | wc -c | tr -d ' ')"
  echo "memory $MEM | files=$n bytes=$bytes index_sha=$idx"
else
  echo "memory | none given or not found"
fi
