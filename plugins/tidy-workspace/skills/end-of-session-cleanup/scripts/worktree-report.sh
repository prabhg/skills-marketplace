#!/bin/sh
# worktree-report.sh — report on every worktree of a repo so removal candidates can be chosen by
# eye. Read-only; it never removes anything. Removal stays a deliberate per-path
# `git worktree remove "<path>"` issued by the agent.
#
# POSIX sh, BSD/macOS-safe.
#
# Usage:
#   worktree-report.sh [-C <repo>] [-b <integration>] [-r <remote>] [-d <stale-days>] [-x <glob>]...
#
# Options:
#   -C <repo>   repo directory (default: cwd)
#   -b <branch> integration branch; default: discovered from origin/HEAD
#   -r <remote> remote name (default: origin)
#   -d <days>   a clean worktree older than this counts as STALE (default: 14)
#   -x <glob>   foreign-worktree glob, matched against the path and the branch; repeatable.
#               Anything matching is reported FOREIGN and must be left alone.
#   -h, --help  this text.
#
# Columns: VERDICT  DIRTY  AHEAD  AGE(d)  BRANCH  PATH
#   VERDICT is one of CURRENT, MAIN, LOCKED, FOREIGN, DIRTY, AHEAD, MERGED, STALE, KEEP.
#   Only MERGED and STALE are removal candidates, and only after the agent prints and confirms.

set -u

REPO="."
INTEGRATION=""
REMOTE="origin"
STALE_DAYS=14
FOREIGN=""

die() { printf '%s\n' "$*" >&2; exit 1; }
usage() { sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0; }

while [ $# -gt 0 ]; do
  case "$1" in
    -C) REPO="${2:-}"; shift 2 ;;
    -b) INTEGRATION="${2:-}"; shift 2 ;;
    -r) REMOTE="${2:-}"; shift 2 ;;
    -d) STALE_DAYS="${2:-14}"; shift 2 ;;
    -x) [ -n "${2:-}" ] || die "-x needs a glob"; FOREIGN="$FOREIGN
$2"; shift 2 ;;
    -h|--help) usage ;;
    *) die "unknown argument: $1 (try --help)" ;;
  esac
done

git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository: $REPO"

if [ -z "$INTEGRATION" ]; then
  INTEGRATION=$(git -C "$REPO" symbolic-ref --quiet --short "refs/remotes/$REMOTE/HEAD" 2>/dev/null \
    | sed "s|^$REMOTE/||")
fi

BASE=""
if [ -n "$INTEGRATION" ]; then
  if git -C "$REPO" rev-parse --verify --quiet "$REMOTE/$INTEGRATION" >/dev/null; then
    BASE="$REMOTE/$INTEGRATION"
  elif git -C "$REPO" rev-parse --verify --quiet "$INTEGRATION" >/dev/null; then
    BASE="$INTEGRATION"
  fi
fi

HERE=$(pwd)
MAIN_WT=$(git -C "$REPO" rev-parse --path-format=absolute --git-common-dir 2>/dev/null \
  | sed 's|/\.git$||')
NOW=$(date +%s)

matches_foreign() {
  subject="$1"
  printf '%s\n' "$FOREIGN" | while IFS= read -r g; do
    [ -n "$g" ] || continue
    case "$subject" in $g) exit 9 ;; esac
    case "$subject" in */$g) exit 9 ;; esac
  done
  [ $? -eq 9 ]
}

printf '# repo:        %s\n' "$(cd "$REPO" 2>/dev/null && pwd)"
printf '# integration: %s\n' "${BASE:-<unknown — merge status unavailable>}"
printf '# stale after: %s days\n' "$STALE_DAYS"
printf '#\n# VERDICT  DIRTY  AHEAD  AGE(d)  BRANCH  PATH\n'

git -C "$REPO" worktree list --porcelain | awk '
  /^worktree /{ wt=substr($0,10) }
  /^branch /  { br=$2; sub("refs/heads/","",br) }
  /^detached/ { br="(detached)" }
  /^locked/   { lk=1 }
  /^$/        { if (wt != "") printf "%s\t%s\t%s\n", wt, (br==""?"(detached)":br), (lk?"locked":"-"); wt=""; br=""; lk=0 }
  END         { if (wt != "") printf "%s\t%s\t%s\n", wt, (br==""?"(detached)":br), (lk?"locked":"-") }
' | while IFS="$(printf '\t')" read -r wt br lock; do
  [ -n "$wt" ] || continue

  dirty="no"
  if [ -n "$(git -C "$wt" status --porcelain 2>/dev/null)" ]; then dirty="YES"; fi

  ahead=0
  up=$(git -C "$wt" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null)
  if [ -n "$up" ]; then
    ahead=$(git -C "$wt" rev-list --count "$up..HEAD" 2>/dev/null || echo 0)
  elif [ -n "$BASE" ]; then
    # No upstream: anything not already on the integration branch is unpublished work.
    ahead=$(git -C "$REPO" rev-list --count "$BASE..$(git -C "$wt" rev-parse HEAD)" 2>/dev/null || echo 0)
  fi

  last=$(git -C "$wt" log -1 --format=%ct 2>/dev/null)
  if [ -n "$last" ]; then age=$(( (NOW - last) / 86400 )); else age="?"; fi

  merged="no"
  if [ -n "$BASE" ] && [ "$br" != "(detached)" ]; then
    if git -C "$REPO" merge-base --is-ancestor "$br" "$BASE" 2>/dev/null; then merged="yes"; fi
  fi

  verdict="KEEP"
  if   [ "$wt" = "$HERE" ];                       then verdict="CURRENT"
  elif [ -n "$MAIN_WT" ] && [ "$wt" = "$MAIN_WT" ]; then verdict="MAIN"
  elif [ "$lock" = "locked" ];                    then verdict="LOCKED"
  elif matches_foreign "$wt" || matches_foreign "$br"; then verdict="FOREIGN"
  elif [ "$dirty" = "YES" ];                      then verdict="DIRTY"
  elif [ "${ahead:-0}" -gt 0 ];                   then verdict="AHEAD"
  elif [ "$merged" = "yes" ];                     then verdict="MERGED"
  elif [ "$age" != "?" ] && [ "$age" -ge "$STALE_DAYS" ]; then verdict="STALE"
  fi

  printf '%-8s  %-5s  %-5s  %-6s  %s  %s\n' "$verdict" "$dirty" "${ahead:-0}" "$age" "$br" "$wt"
done

exit 0
