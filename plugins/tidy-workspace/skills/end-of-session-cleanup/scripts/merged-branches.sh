#!/bin/sh
# merged-branches.sh — list branches fully merged into an integration branch, or delete an
# explicit list of them. Dry-run is the default; deleting requires --delete AND a newline-
# separated branch list on stdin, so the listing output can never feed straight back in.
#
# POSIX sh, BSD/macOS-safe: no GNU-only flags, no `sed -i`, no `\|` alternations.
#
# Usage:
#   merged-branches.sh [-C <repo>] [-b <integration>] [-r <remote>] [-p <glob>]... [--include-rebased]
#   merged-branches.sh [same options] --delete < branches.txt
#
# Options:
#   -C <repo>          repo directory (default: cwd)
#   -b <branch>        integration branch; default: discovered from origin/HEAD
#   -r <remote>        remote name (default: origin)
#   -p <glob>          protected branch glob; repeatable. Always implies the integration branch.
#   --include-rebased  also report branches whose content landed via rebase/squash, proven by
#                      `git cherry` (all '-') and an empty range diff. Reported as REBASED.
#   --delete           delete the branches read from stdin (remote then local), one at a time.
#   -h, --help         this text.
#
# Exit codes: 0 ok, 1 usage/setup error, 2 a delete was refused (nothing forced).

set -u

REPO="."
INTEGRATION=""
REMOTE="origin"
PROTECTED=""
INCLUDE_REBASED=0
DO_DELETE=0
STATUS=0
BASE=""
HAVE_REMOTE=1

die() { printf '%s\n' "$*" >&2; exit 1; }

usage() { sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0; }

while [ $# -gt 0 ]; do
  case "$1" in
    -C) REPO="${2:-}"; [ -n "$REPO" ] || die "-C needs a directory"; shift 2 ;;
    -b) INTEGRATION="${2:-}"; [ -n "$INTEGRATION" ] || die "-b needs a branch"; shift 2 ;;
    -r) REMOTE="${2:-}"; [ -n "$REMOTE" ] || die "-r needs a remote"; shift 2 ;;
    -p) [ -n "${2:-}" ] || die "-p needs a glob"; PROTECTED="$PROTECTED
$2"; shift 2 ;;
    --include-rebased) INCLUDE_REBASED=1; shift ;;
    --delete) DO_DELETE=1; shift ;;
    --dry-run) shift ;;                 # accepted and ignored: dry-run is the default
    -h|--help) usage ;;
    *) die "unknown argument: $1 (try --help)" ;;
  esac
done

git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository: $REPO"

if [ -z "$INTEGRATION" ]; then
  INTEGRATION=$(git -C "$REPO" symbolic-ref --quiet --short "refs/remotes/$REMOTE/HEAD" 2>/dev/null \
    | sed "s|^$REMOTE/||")
fi
if [ -z "$INTEGRATION" ]; then
  # Fall back to the local default branch only if it is unambiguous; otherwise refuse to guess.
  for cand in main master trunk; do
    if git -C "$REPO" rev-parse --verify --quiet "refs/heads/$cand" >/dev/null; then
      INTEGRATION="$cand"; break
    fi
  done
fi
[ -n "$INTEGRATION" ] || die "could not discover the integration branch; pass -b <branch>"

# BASE is what "merged" is measured against. Prefer the remote-tracking ref; fall back to the
# local branch so that a repo with no remote (or an unfetched one) still works, minus remote
# deletes.
if git -C "$REPO" rev-parse --verify --quiet "$REMOTE/$INTEGRATION" >/dev/null; then
  BASE="$REMOTE/$INTEGRATION"
  HAVE_REMOTE=1
elif git -C "$REPO" rev-parse --verify --quiet "refs/heads/$INTEGRATION" >/dev/null; then
  BASE="$INTEGRATION"
  HAVE_REMOTE=0
  printf '# note: %s/%s not found — local-only mode, no remote branches listed or deleted\n' \
    "$REMOTE" "$INTEGRATION" >&2
else
  die "neither $REMOTE/$INTEGRATION nor local $INTEGRATION exists; fetch first or pass -b/-r"
fi

CURRENT=$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)

# Branches checked out in any worktree cannot be deleted — collect them up front.
CHECKED_OUT=$(git -C "$REPO" worktree list --porcelain 2>/dev/null \
  | awk '/^branch /{sub("refs/heads/","",$2); print $2}')

is_protected() {
  b="$1"
  [ "$b" = "$INTEGRATION" ] && return 0
  [ "$b" = "HEAD" ] && return 0
  [ -n "$CURRENT" ] && [ "$b" = "$CURRENT" ] && return 0
  for co in $CHECKED_OUT; do
    [ "$b" = "$co" ] && return 0
  done
  # `case` does the glob matching: no regex translation, no alternation pitfalls.
  printf '%s\n' "$PROTECTED" | while IFS= read -r g; do
    [ -n "$g" ] || continue
    case "$b" in $g) exit 9 ;; esac
  done
  [ $? -eq 9 ] && return 0
  return 1
}

# Content already landed on the integration branch, though not as an ancestor?
content_landed() {
  b="$1"
  unapplied=$(git -C "$REPO" cherry "$BASE" "$b" 2>/dev/null | grep -c '^+')
  [ "${unapplied:-1}" -eq 0 ] || return 1
  diffsize=$(git -C "$REPO" diff --name-only "$BASE...$b" 2>/dev/null | wc -l)
  [ "$(printf '%s' "$diffsize" | tr -d ' ')" = "0" ]
}

# ---------------------------------------------------------------- delete mode
if [ "$DO_DELETE" -eq 1 ]; then
  if [ -t 0 ]; then
    die "--delete reads an explicit newline-separated branch list on stdin; none given"
  fi
  while IFS= read -r line; do
    b=$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    case "$b" in ''|'#'*) continue ;; esac
    b=$(printf '%s' "$b" | sed -e "s|^remote/||" -e "s|^$REMOTE/||" -e 's|^local/||')
    if is_protected "$b"; then
      printf 'SKIP  %s (protected, current, or checked out in a worktree)\n' "$b"
      STATUS=2
      continue
    fi
    if [ "$HAVE_REMOTE" -eq 1 ] && git -C "$REPO" rev-parse --verify --quiet "$REMOTE/$b" >/dev/null; then
      printf 'rm remote %s/%s ... ' "$REMOTE" "$b"
      if git -C "$REPO" push "$REMOTE" --delete "$b" >/dev/null 2>&1; then
        printf 'ok\n'
      else
        printf 'FAILED\n'; STATUS=2
      fi
    fi
    if git -C "$REPO" rev-parse --verify --quiet "refs/heads/$b" >/dev/null; then
      printf 'rm local  %s ... ' "$b"
      if git -C "$REPO" branch -d "$b" >/dev/null 2>&1; then
        printf 'ok\n'
      else
        printf 'REFUSED (not merged — left alone, never -D)\n'; STATUS=2
      fi
    fi
  done
  exit $STATUS
fi

# ------------------------------------------------------------------ list mode
printf '# repo:        %s\n' "$(cd "$REPO" 2>/dev/null && pwd)"
printf '# integration: %s\n' "$BASE"
printf '# protected:   %s\n' "$(printf '%s' "$PROTECTED" | tr '\n' ' ' | sed 's/^ *//')"
printf '# mode:        DRY RUN (pipe a chosen subset into --delete to act)\n'
printf '#\n# STATUS  SCOPE   BRANCH   LAST-COMMIT\n'

if [ "$HAVE_REMOTE" -eq 1 ]; then
git -C "$REPO" branch -r --merged "$BASE" --format='%(refname:short)' \
  | grep "^$REMOTE/" \
  | grep -v "^$REMOTE/HEAD$" \
  | sed "s|^$REMOTE/||" \
  | sort -u \
  | while IFS= read -r b; do
      [ -n "$b" ] || continue
      is_protected "$b" && continue
      when=$(git -C "$REPO" log -1 --format=%cs "$REMOTE/$b" 2>/dev/null)
      printf 'MERGED   remote  %s  %s\n' "$b" "$when"
    done
fi

git -C "$REPO" branch --merged "$INTEGRATION" --format='%(refname:short)' 2>/dev/null \
  | sort -u \
  | while IFS= read -r b; do
      [ -n "$b" ] || continue
      is_protected "$b" && continue
      when=$(git -C "$REPO" log -1 --format=%cs "$b" 2>/dev/null)
      printf 'MERGED   local   %s  %s\n' "$b" "$when"
    done

if [ "$INCLUDE_REBASED" -eq 1 ] && [ "$HAVE_REMOTE" -eq 1 ]; then
  git -C "$REPO" branch -r --no-merged "$BASE" --format='%(refname:short)' \
    | grep "^$REMOTE/" \
    | grep -v "^$REMOTE/HEAD$" \
    | sed "s|^$REMOTE/||" \
    | sort -u \
    | while IFS= read -r b; do
        [ -n "$b" ] || continue
        is_protected "$b" && continue
        if content_landed "$REMOTE/$b"; then
          when=$(git -C "$REPO" log -1 --format=%cs "$REMOTE/$b" 2>/dev/null)
          printf 'REBASED  remote  %s  %s\n' "$b" "$when"
        fi
      done
fi

exit 0
