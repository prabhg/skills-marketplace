# Brief templates

Every dispatch: explicit tier, a brief file written to `<scratch>/briefs/<ticket>-<role>-<n>.md` (the
dispatch message just says "Read and follow <brief path>"), and a report path
`<scratch>/reports/<ticket>-<role>-<n>.md`. Briefs carry pointers, not pasted content. One brief = one
focused job with a clear finish line. Never let a subagent inherit your conversation.

Status line every subagent returns first: `DONE` | `DONE_WITH_CONCERNS` | `BLOCKED: <why>` |
`NEEDS_CONTEXT: <what>`. On BLOCKED/NEEDS_CONTEXT change something before re-dispatching (context, tier,
scope); never retry unchanged.

## Implementer / fixer (cap: ≤150 words returned)

```
ROLE: implementer for ticket <id> — <title>. Tier: <haiku|sonnet|opus>.
GOAL: <one or two sentences: the outcome, not the steps>.
WORKTREE: <abs path> on branch <branch> (based on <integration>@<sha>). Work and commit only here; never write in
  the main checkout or any other path (stray files there block the merge).
FIRST READ: <repo>/AGENTS.md or CLAUDE.md (repo rules win); then <pointers: file paths / doc §sections>.
SCOPE: may change <dirs/files>. Must not touch <shared files / other tickets' areas / integration branch>.
DEFINITION OF DONE (each must be proven by a command you ran):
  1. <checkable statement> — proof: `<command>`
  2. ...
CONSTRAINTS: no pushes, no merges, no PRs, no branch deletes, no cloud/env mutations, no new dependencies
  unless listed here, no secrets in code or logs. Commit in small commits: "<repo commit style>".
  If something needs owner authority or contradicts the spec: stop and report BLOCKED.
VERIFY: run <build/test/lint commands> in the worktree. Paste command, exit code and result line in the report.
REPORT FILE: <path> — files changed, commits (sha + subject), verification evidence, deviations, concerns.
RETURN (≤150 words): status line; head sha; DoD items 1..n pass/fail with one-line evidence; concerns.
```

Fixer = same brief plus `FINDINGS TO FIX (verbatim from review): …` and `Do not change anything else.`

## Reviewer (cap: ≤30 lines returned)

The reviewer must not have written the code and must not see the implementer's report.

```
ROLE: independent reviewer. Tier: <sonnet|opus>. You did not write this code.
TARGET: repo <path>, branch <branch>, base <integration>@<sha>. Diff: `git diff <base>...<branch>`.
  (Batch: list each branch with its ticket; give one verdict per branch.)
TICKET DoD: <paste the DoD list, or pointer to spec §ticket>.
FIRST READ: <repo>/AGENTS.md or CLAUDE.md, and only the code needed to judge the diff.
CHECK: each DoD item — run its proof command yourself (in the worktree, or `git worktree add` a
  temporary checkout under <scratch>/wt/ and remove it after; any scratch files you make (mutation
  copies etc.) go under <scratch> only). Then correctness, security/privacy, scope creep (changes
  outside the ticket), tests that actually test the behaviour, repo conventions.
DO NOT: fix code, commit, merge, push, or read the implementer's report.
REPORT FILE: <path> — evidence per DoD item (command, exit code, result line), findings with file:line.
RETURN (≤30 lines): VERDICT: APPROVE | CHANGES | ESCALATE; per DoD item pass/fail + evidence;
  findings numbered with severity (critical/important/minor). Minor-only → APPROVE with notes.
```

Scoped re-review: same, with `SCOPE: only verify findings <n..> are fixed in <fix sha range>; new issues on
untouched code go under "noted", not into the verdict.`

## Reader / researcher (cap: ≤200 words returned)

```
ROLE: reader. Tier: <haiku for known locations | sonnet for synthesis>.
QUESTION: <exact questions to answer, numbered>.
WHERE: <paths, docs, urls>. Read-only: do not modify anything.
REPORT FILE: <path> — answers with file:line or url evidence.
RETURN (≤200 words): numbered answers, each one line, plus "UNSURE:" items.
```

Orientation readers answer: repo agent rules (summary), integration branch, release/promotion flow,
build/test/lint commands and how long they take, worktree conventions, protected branches, relevant
architecture for the goal, anything that would make a decision critical (shared envs, schemas, secrets).

## Planner (cap: ≤200 words returned)

```
ROLE: planner. Tier: opus (sonnet for small goals).
GOAL: <owner's goal verbatim>. INPUTS: <orientation report paths>, <PRD/spec paths if any>.
PRODUCE: <scratch>/spec.md (approach, interfaces, risks) and <scratch>/tickets.md with the ticket table
  (fields: id, title, repo/area, blocked_by, DoD with proof commands, risk, tier, hint) grouped into waves
  with disjoint write scopes per wave; plus a list of critical decisions, each with options and a
  recommendation (irreversible, costly, security/privacy, scope, external accounts/money, shared envs).
RETURN (≤200 words): ticket count per wave, the critical decisions (one line each), top 3 risks.
```

## Integrator (cap: ≤100 words returned) — see merge-and-cleanup.md

## Council critic / synthesizer

Critic (≤150 words): `LENS: <correctness | security/privacy | simplicity/cost>. QUESTION: … INPUTS:
<paths>. Argue only from your lens; find what breaks. Write full critique to <path>.`
Synthesizer (opus, ≤250 words): `Read <critic report paths>. Return: recommendation, strongest objection,
what would change your mind, cost if wrong.`

## Status poke (watchdog)

`Status check from the orchestrator: reply in ≤3 lines — done so far / what you are doing now / ETA or
blocker. Do not stop working unless told to.`
