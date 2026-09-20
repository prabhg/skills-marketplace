# Config schema and discovery fallbacks

Configuration is optional. Every key has a discovery fallback, and a key that cannot be discovered
with confidence disables its step rather than guessing.

## Where it lives

1. `.claude/tidy.json` at the repo root — the JSON object below, verbatim.
2. A fenced `json` block in `CLAUDE.md` introduced by a line containing `tidy config` — same
   object. Useful when a project prefers one file of instructions.
3. Neither present → pure discovery.

Later sources never override earlier ones; `.claude/tidy.json` wins.

## Keys

| Key | Type | Meaning | Discovery fallback |
| --- | --- | --- | --- |
| `integrationBranch` | string | The branch that "merged" is measured against. | `git symbolic-ref --short refs/remotes/origin/HEAD` → strip the remote prefix. If that fails, `git remote show origin` → `HEAD branch`. If still unknown, **ask**; never default. |
| `protectedBranchGlobs` | string[] | Branches that are never deleted, merge status notwithstanding. | The integration branch, `main`, `master`, plus any branch protected on the forge (`gh api repos/{owner}/{repo}/branches --jq '.[]\|select(.protected)\|.name'` when a forge CLI is authenticated). |
| `worktreeRoots` | string[] | Directories that hold worktrees for this project, in addition to whatever `git worktree list` reports. | `git worktree list --porcelain` only. |
| `foreignWorktreeGlobs` | string[] | Worktree paths and branch names belonging to other agents or other people. Read-only, always. | Empty. Absent config, treat a worktree as foreign when its HEAD moved within the last hour and it is not the current one. |
| `tempDocGlobs` | string[] | Scratch documents eligible for folding and deletion. | `temp/**`, `tmp/**`, `scratch/**`, `**/*HANDOFF*`, `**/*_LOG_*`, `**/*NOTES*`, `**/*WIP*`, `**/*_20??-??-??.md`, `**/scratch*`. Always intersected with tracked-or-untracked files inside the repo; never outside it. |
| `filesOfRecord` | string[] | The durable documents that extracted facts get written into. Order matters — the first is the default destination. | Top-level `docs/*.md` that are referenced from `README.md` or `CLAUDE.md`. If none can be identified, **skip step 4's extraction** and report it; deleting without a destination loses information. |
| `issueTracker` | string | `github`, `gitlab`, `linear`, `jira`, `none`. Decides where status goes instead of a file. | A forge remote implies that forge's issues. `none` means status stays in a file of record, not a temp doc. |
| `memoryDir` | string | The agent memory directory for this project. | The harness's per-project memory directory, if one exists and contains an index file. Otherwise skip step 5. |
| `staleDays` | number | Age past which a clean worktree counts as abandoned. | `14`. |
| `neverTouch` | string[] | Absolute-path escape hatch. Anything matching is excluded from every step. | Empty. |

## Glob matching

Match with shell `case` or `grep -E`. Convert a glob to a regex by escaping `.`, turning `*` into
`[^/]*` and `**` into `.*`, and anchoring both ends. Never build an alternation with `\|` — BSD
basic grep reads it literally and the pattern silently matches nothing, which fails open into
deleting protected branches.

## Worked example

```json
{
  "integrationBranch": "develop",
  "protectedBranchGlobs": ["develop", "main", "release/*"],
  "worktreeRoots": ["../project-worktrees"],
  "foreignWorktreeGlobs": [".worktrees/*", "bot/*"],
  "tempDocGlobs": ["notes/scratch/**", "**/*HANDOFF*.md"],
  "filesOfRecord": ["docs/STATE.md", "docs/DECISIONS.md"],
  "issueTracker": "github",
  "memoryDir": "~/.agent-memory/this-project",
  "staleDays": 21,
  "neverTouch": ["/Volumes/external/archive"]
}
```
