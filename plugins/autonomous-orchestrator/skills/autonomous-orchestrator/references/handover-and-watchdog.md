# Handover, takeover, watchdog

## Handover (outgoing orchestrator)

Trigger: context reaches the **handoff threshold** recorded in CURRENT STATE (asked in the first decision
batch; default **60%**). No meter visible → proxies: a compaction/summary event (threshold passed); several
waves or many hours; re-reading things or losing track. Also hand over before a long risky stretch you
could not finish under the threshold.

1. Start no new dispatches. Bring in-flight work to a **clean boundary**: land what is approved and nearly
   done, park the rest on its branch with a one-line state.
2. Rewrite CURRENT STATE completely: Next action, In flight (with report paths), Blockers, Approvals,
   Peers, Coordinator, command-ID block + next free ID (coordinated mode). Add a **HANDOFF → `<name> v<n+1>`**
   block at its top: who you are (the successor may message you), the coordinator's name if one runs, what
   is parked and why, owner items pending. Commit it if the state file lives in a committed temp folder.
   A separate handoff file is fine for long briefs; give it the temp-doc header with
   "Delete when: the successor has copied it into the state file".
3. Send the successor's exact start prompt to the coordinator (coordinated mode) or the owner:
   *"Context at <n>%. Start `<name> v<n+1>` with: `Use the autonomous-orchestrator skill. Take over as
   orchestrator from <abs path>. You are "<name> v<n+1>"; report to "<coordinator>"; predecessor
   "<name>" stays open for questions.`"*
4. Keep working until a successor contacts you. On its retire message: stop dispatching, finish any state
   write in progress, reply `RETIRED <ts>; in flight: <ids>; last write <ts>`, and go quiet (no more tool
   calls except reading further messages). In-flight subagents keep writing to their report files.

## Takeover (incoming orchestrator)

Name: the predecessor's name with the next version (`… v2`, `… v3`). Your first messages go to the
coordinator (if named) — `CLAIMED <state path> at <ts>; ID block <block> next <n>` — and to the
predecessor (step 3).

Trigger: owner says "take over as orchestrator from <path>" / "resume orchestration from <path>", or you
found an abandoned state file and the owner agreed. The owner's explicit instruction is the authority —
do not wait for the heartbeat to go stale.

1. **Read only the top block** (CURRENT STATE) — e.g. read the first ~40 lines. Load the ticket table only
   when step 4 needs it.
2. **Claim ownership:** write your identity + a fresh heartbeat into `Orchestrator:` and add a Ruling line
   `Ruling: took over from <old identity> at <ts>`. Your identity must differ from the previous one:
   harness session name/id if exposed, else `orch-<slug>-<yyyymmddHHMM>` from the current time. Bump the
   heartbeat on every later write, so the next abandonment check can tell you are alive.
3. **Retire the previous orchestrator** if it may still be running: message it (session messaging tool)
   `RETIRE: <new identity> owns <state path> from <ts>. Stop dispatching, confirm, go quiet.` Wait up to
   ~5 min for `RETIRED`. No messaging tool or no reply: assume it is dead or stopped, note it, continue —
   and tell the owner to close the old session if he can.
4. **Reconcile ledger vs git** (one small haiku subagent if several repos, else ≤5 commands):
   `git log --oneline <integration>` (which merge shas landed), `git worktree list`,
   `git branch -a`, and per leftover worktree `git status --short` + `git log <integration>..HEAD --oneline`.
   Fix the ledger to match reality: a ticket merged in git is `merged` even if the ledger says
   `approved`; a ledger `merged` with no sha in git is `approved` (re-merge). Never redo merged work.
5. **Resolve In flight** — the subagents reported to the old session, but their output is on disk:
   - Report file exists → process it as if just returned (verdict, merge, etc.).
   - No report, worktree has new commits or changes → old session dead: treat as stuck (watchdog step 3).
     Old session alive and subagent still running: wait one expected-duration window, then decide.
   - No report, no changes → re-dispatch.
6. A separate handoff file: once its binding content is in the state file, delete it (`git rm` + index row
   in a committed temp folder). Never delete the state file on takeover — it carries over.
7. Rewrite CURRENT STATE, then continue at Next action.

**Previous orchestrator was killed** (no reply, heartbeat stale): same steps; step 3 is a no-op. Assume
all its subagents died too unless their worktrees show recent commits (`git log -1 --format=%cr`).

## Watchdog

Record for every dispatch: start ts, expected duration. Defaults: haiku 10 min; sonnet 25 min; opus
40 min; reviewer 15 min; integrator 20 min; scale up for slow builds named in orientation.

1. At **1.5×** expected with no report: poke (status-poke template in `briefs.md`) through the harness's
   agent-messaging tool.
2. At the next check (by **2×**): useful answer with progress → extend once by 1× and log it. No answer, a
   vague one, or no new commits/changes in its worktree → step 3.
3. Stop it (task-stop tool), inspect its worktree: `git status --short`, `git log <base>..HEAD --oneline`.
   Commit uncommitted partial work on its branch (`wip: partial <ticket>`) so nothing is lost. Re-dispatch
   with a smaller scope, a tier up, or the partial branch as starting point. Log a Ruling.

**Keeping the check alive:**
- Harness has a wake-up/scheduling tool (scheduled wake-ups, `/loop`, a monitor tool, background commands
  that re-invoke you when they exit): schedule a wake at the earliest poke deadline across In flight, and
  re-arm after each check. A background `sleep <secs>` command works where background commands notify on
  exit.
- No such tool: check every In-flight deadline whenever any notification arrives and before every
  dispatch; never end your turn with work in flight and no way to be woken — keep one wait mechanism armed.
- Background subagents that finish notify you; do not poll them in a tight loop.
