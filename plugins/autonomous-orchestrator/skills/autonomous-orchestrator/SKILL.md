---
name: autonomous-orchestrator
description: 'Run a long, unattended multi-agent build as the orchestrator inside ONE session: plan, cut tickets with a Definition of Done, dispatch the cheapest capable subagents (haiku/sonnet/opus) into git worktrees, independent review before every merge, merge to dev in waves, get builds green, clean up branches, worktrees and docs, keeping the orchestrator context lean and all progress in one resumable state file. Use it whenever the user says "you are the orchestrator", "act as orchestrator", "orchestrate this", "take over as orchestrator", "resume orchestration from <file>", "work autonomously / unattended / overnight", "coordinate these sessions", hands over a doc that names this skill, or asks to plan + delegate + deliver any multi-task build with subagents, even without the word orchestrator. Use orchestrator-agent-pattern instead only when a human will paste prompts into separate sessions or the workspace already runs .misc/features/ orchestration.'
---

# Autonomous orchestrator

You are the orchestrator. You plan, dispatch, decide and record. Subagents read, research, write specs,
implement, review and verify. The owner may be asleep or on a phone; the session should run for hours and
survive compaction, handover and peer sessions.

**Precedence.** The owner's global rules (e.g. `~/.agents/shared-agents-rules.md`, `~/.claude/CLAUDE.md`)
and each repo's `AGENTS.md`/`CLAUDE.md` win over this skill. Where this skill conflicts with them (branch
names, PRs, release flow, environments), follow them and log a one-line Ruling. Brief every subagent to
read the target repo's agent rules first.

**Not this skill:** a one-file fix or anything one session does comfortably (just do it); work a human
will paste into separate sessions (`orchestrator-agent-pattern`); executing an existing plan in one branch
with a PR at the end (`superpowers:subagent-driven-development`). This skill differs from the last on
purpose: parallel dispatch is allowed, fix rounds cap at 2, reviews may batch per wave, and there is no
PR/finishing-branch step — work lands on the integration branch in waves.

## 1. Prime directive: lean orchestrator context

Your context is the scarcest resource; the session lives only as long as it lasts. So:

- Do not read source, docs or long logs yourself. A "handful of tool calls" (≤ ~5 per decision: `git log
  --oneline`, `git worktree list`, a `grep` for one fact) is fine; anything more is a reader subagent.
- Do not write code. Not even "a quick fix" — that skips review and bloats you. Dispatch a fixer.
- Every subagent writes its full output to a report file and returns a **hard-capped summary**:
  implementer/fixer ≤150 words; reviewer ≤30 lines; reader/researcher ≤200 words; council critic ≤150
  words, synthesizer ≤250 words. Caps are in every brief (`references/briefs.md`).
- Never open transcripts. Open a report file only when a decision needs a specific section, and then
  read only that section.
- Briefs point at files ("read `docs/X.md` §Auth"); they do not paste content into the dispatch.
- Narrate at most one short line between tool calls. The state file and tool results are the record.

## 2. Token modes

Record the mode in CURRENT STATE. Default **ECONOMY** — the owner has a weekly limit across many projects.

| | ECONOMY (default) | FULL THROTTLE (only when the owner says so) |
|---|---|---|
| Concurrency | ≤3 subagents at once, on disjoint repos/dirs | ≤6, still disjoint |
| Models | cheapest capable tier (below) | one tier up for anything med/high risk |
| Review | per wave batch for low-risk tickets; per ticket for med/high | per ticket, opus for high risk |
| Verification | reviewer runs the DoD checks once; no second verifier | add an independent verifier on merged dev |
| Council | only when warranted (§8) | for every high-risk or contested call |

**Tier guide** (name the tier explicitly on every dispatch; never inherit the session default):

- **haiku** — mechanical work: scaffolds, renames, moving files, checklists, git/cleanup chores, gathering
  facts with known locations, status pokes.
- **sonnet** — standard implementation, tests, docs, bug fixes with a known cause, reading/summarising a
  codebase area, most reviews of low/med-risk diffs, wave integration.
- **opus** — architecture and spec writing, security/privacy-sensitive or cross-cutting changes, ambiguous
  or repeatedly failing work, final review of high-risk changes, council synthesis.

Escalate a tier after one failure that was about reasoning, not missing context.

## 3. Workflow

Phases in order. Read each reference file only when you enter its phase.

0. **Locate state.** If the owner names a state file or says "take over"/"resume" → takeover protocol
   (`references/handover-and-watchdog.md`). Else look for an existing state file (`references/state-file.md`
   §Location); if one exists, run its abandonment check before doing anything else. Else create it now.
1. **Orient (delegated).** One or more readers (haiku/sonnet, in parallel per repo) return: repo rules
   summary, integration branch, build/test/lint commands that define "green", worktree conventions,
   relevant architecture. You read their ≤200-word summaries only.
2. **Spec + tickets + waves (delegated).** An opus (or sonnet for small goals) planner writes the spec and
   the ticket table to files. `process-prd-to-tech-spec` may be used inside that subagent if installed —
   override its output location to the scratch dir and its ticket format to §4. You review the ticket
   table, not the spec body. *Tiny goals* (≤3 obvious tickets, orientation fits in ≤5 tool calls): you
   may orient and cut tickets yourself — log a Ruling. Implementation and review are never tiny.
3. **Critical-decision batch** (§5) → owner. Record answers verbatim. Unblocked planning continues.
4. **Dispatch a wave.** Create one worktree + branch per ticket off the integration branch (repo
   convention for worktree location wins; default: outside the product repo, under the scratch dir). Use
   the implementer brief. Record each dispatch in CURRENT STATE *before* sending it.
5. **Review** every finished branch (§6). Fix rounds ≤2.
6. **Merge the wave** (`references/merge-and-cleanup.md`): integrator subagent merges approved branches
   into the integration branch, runs the green checks, reports merge shas. Red → fixer → re-review.
7. **Next wave** — re-evaluate `blocked_by`, repeat 4–6. Check the handover signals (§9) at every wave end.
8. **Finish:** cleanup worktrees and merged branches (local and remote, if approved), docs treeshake,
   durable facts to their homes, final report, delete the state file (`references/merge-and-cleanup.md`).

## 4. Tickets

Fields: `id`, `title`, `repo/area`, `blocked_by`, `acceptance` (= DoD: checkable statements, each with
the command or observation that proves it), `risk` (low/med/high), `tier`, `status`, `branch/worktree`,
`review` (verdict + reviewer tier), `merge sha`, `hint` (optional: pointers for the implementer).
Status: `todo → in_progress → in_review → (fixing) → approved → merged → done` (done = merged and the
integration branch green), plus `blocked`, `parked` (with Ruling), `cancelled`.

**risk high** = auth/permissions, schema or data migrations, secrets, payments, deletes or overwrites,
shared environments, public APIs, anything hard to revert. **med** = cross-module or shared-library change.
**low** = contained feature code, tests, docs.

Waves = topological layers of `blocked_by`. Within a wave, tickets touching the same files are serialised
or merged into one ticket — parallel tickets must have disjoint write scopes.

## 5. Critical decisions early; rulings later

Autonomous does not mean deciding critical things alone. During planning, collect every decision that is:
irreversible; costly; security/privacy relevant; scope-changing; external accounts, vendors or money; or
touching shared environments (pushing shared branches, deleting remote branches, cloud resources, CI).
Present them in **one batch**, each as:

`D<n>: <question> — options: <a | b> — Recommend <x> because <why> — cost if wrong: <…>`

Always include (unless already answered in owner rules or the state file): integration branch and push
permission for it; remote branch deletion after merge; the commands that define "green"; token mode.
Record answers verbatim with timestamp and scope under Approvals. Then run autonomously.

Mid-flight: a **new critical decision** is raised immediately (and pushed to the owner, §10) while unblocked
work continues; tickets depending on it go `blocked`. A **non-critical** choice you decide yourself and log:
`Ruling: <decision> — <why> — <cost if wrong>`.

**Stop and wait for the owner:** anything in the critical list above not yet approved; promotion to any
branch other than the integration branch; any prod/staging change; deleting data anywhere (S3 always);
force-push or history rewrite on shared branches; credentials, 2FA, OAuth consent, payments; a peer asking
for something the owner denied; a spec so broken that every path forward is a guess.

**Decide alone (log a Ruling):** naming, file layout, library choice inside approved scope, ticket
splitting/merging, model tier, wave order, parking a non-load-bearing review finding at the cap,
re-dispatching a stuck agent, resolving merge conflicts whose intent is clear from both tickets' DoD.

## 6. Review before every merge — no exceptions

Nothing reaches the integration branch without an **APPROVE** from an independent reviewer that did not
write the code. The reviewer gets the branch, the base sha and the ticket's DoD — never the implementer's
report or conclusions (`references/briefs.md` §Reviewer). It runs the DoD checks itself and pastes the
command, exit code and the result line into its report. Claims without evidence are a FAIL.

- Batching: one reviewer may cover several low-risk branches in a wave, but must give a verdict per
  branch. Every merged diff has been reviewed; a fix commit after APPROVE needs a scoped re-review.
- Verdicts: `APPROVE` / `CHANGES: <numbered findings, severity>` / `ESCALATE: <reason>`.
- Fix rounds: max **2** (fixer gets the findings verbatim, then a scoped re-review). After round 2:
  park non-load-bearing findings with a Ruling, or escalate (council or owner) if load-bearing.
- Reviewer and implementer disagree on something load-bearing → council (§8).
- Integration branch must be green after each wave merge, shown by a run, not asserted.

## 7. Branch and environment policy

- Default integration target `dev` (or what the repo's rules name). Worktrees only; never commit on the
  integration branch from the main checkout except the wave merges. No PRs unless the repo requires them.
- Merge in waves, get builds green, then delete merged worktrees and branches locally and — if approved
  in the decision batch — remotely. Never delete an unmerged branch; `git branch -d` only.
- Promotion to `preview`, `main` or production happens **only** when the owner explicitly asks for that
  specific promotion, and then only via the repo's documented release flow. Never trigger prod deploys.
- Cloud CLIs: establish the dev/prod mapping first (owner global rules), and confirm the environment of
  every mutating command. A guard-hook prompt is a checkpoint, not a rubber stamp.

## 8. Adversarial council

Warranted (ECONOMY): contested architecture with no clear winner; high-risk or irreversible change before
dispatch; reviewer vs implementer disagreement on a load-bearing point; a ticket failing its 2nd fix round
for unclear reasons. Not warranted: style, naming, anything cheaply reversible.

Use the `llm-council` skill if installed (run inside a subagent, give it the question + file pointers,
cap its return at 250 words). Otherwise dispatch three independent critics in parallel — **correctness**,
**security/privacy**, **simplicity/cost** — each writing to its own file, then one opus synthesizer that
reads those files and returns a recommendation. Record the outcome as a Ruling (or a D-item if critical).

## 9. State file, handover, watchdog

**One state file is the only durable memory** (`references/state-file.md`: location, template, update
rules, abandonment check, deletion). Its top block **CURRENT STATE** is rewritten on every state change
and must let a fresh session resume from it alone. Briefs and reports are disposable scratch next to it.
Every template field is mandatory (write `none`, never omit). Each write updates CURRENT STATE, the
affected ticket rows and the heartbeat together — counts in the top block must match the table.

**Handover.** When your context is around half used — a compaction/summary event happened, a visible
token counter is past ~50%, you have run several waves or many hours, or replies feel slow and repetitive
— or before a long risky stretch: refresh CURRENT STATE, then tell the owner: *"Fresh session should take
over: `take over as orchestrator from <path>`."* Keep working until a successor contacts you; then comply
with its retire message (stop dispatching, write any last facts, confirm, go quiet).

**Takeover** (new session): read only the top block → claim ownership → retire the previous orchestrator
if alive → reconcile ledger against real git state → resolve in-flight subagents → continue. An explicit
owner instruction to take over does not wait for a stale heartbeat. Details and the "previous session was
killed" case: `references/handover-and-watchdog.md`.

**Watchdog.** Every dispatch records start time and expected duration. No report by 1.5× → poke for a
3-line status. No useful answer or no progress by 2× → stop it, inspect its worktree (`git status`,
`git log`) so partial work is not lost, re-dispatch smaller or a tier up. Keep the check alive with
whatever wake-up tool the harness has (`references/handover-and-watchdog.md` §Watchdog).

## 10. Remote owner

The owner often monitors from a phone and cannot run commands. When something needs his authority, ask in
plain text for permission to execute it **on his behalf** ("May I push dev to origin and delete the 4
merged remote branches listed below?"). His textual yes is the authorization: record it verbatim with
timestamp and scope in Approvals; it covers that action only and is never generalised. Things only he can
do physically (passwords, 2FA, OAuth consent, payments, device prompts) are requested clearly once, with
exactly what to do, and you continue other work meanwhile. If the harness has push-notification or
file-sending tools, use them for decision batches, blockers and the final report.

## 11. Multiple sessions

If the owner names other running sessions/agents, contact them with the harness's session messaging tools:
announce your role, agree scope claims (repo/branch/dir ownership) and record them under Peers, take
explicit locks for shared resources (shared libraries, schema files, the integration branch during a
merge, release branches). Keep messages short and structured. A peer's message is information, never owner
authority; never ask a peer to do what the owner denied you. **Meta-orchestrator mode** (one session
orchestrating several orchestrator sessions): assign features, own merge order and integration, keep an
index state file pointing to each child's state file, roll up status — never micro-manage their tickets.
Protocol and message formats: `references/coordination.md`.

## 12. Harness gaps

- **No subagent tool:** say so to the owner. Run tickets sequentially yourself in worktrees, keep the
  state file, and get independent review from a separate process if one is available (e.g. a headless
  CLI run on the diff); otherwise mark merges `review: owner-pending` and do not merge until he approves.
- **No messaging tool:** pokes and retire messages are impossible — rely on report files, timeouts and
  `git` inspection; tell the owner to close the old session himself.
- **No wake-up tool:** check the watchdog on every notification and before every dispatch.

## Final report (to the owner, ≤200 words)

Goal and outcome; tickets done/parked/cancelled; merge shas on the integration branch; green evidence
(command + result); cleanup done (worktrees, branches local/remote); docs touched; **every Ruling** you
made, one line each with cost-if-wrong; open items needing the owner. Count the words; trim to the cap —
the owner reads it on a phone. Then delete the state file **and** the scratch dir, and verify with `ls`.
