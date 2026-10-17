---
name: compactor
description: 'Compact a long Claude Code session without losing what matters. Before compaction it saves the session''s goal, user decisions (verbatim), current state, in-flight work, key paths/ids and next steps: durable facts go to the memory system, the working state goes to a small token-named file on disk. After /compact (manual or auto), the plugin''s SessionStart hook injects that file back into context and deletes it, so the session resumes with its key context intact. Use whenever the user says "compact", "compactor", "prepare to compact", "save state before compacting", "my context is getting full", "checkpoint this session", "rehydrate", or asks to keep decisions/state across a /compact. Also use when you notice the context is nearly full and the user agrees to compact.'
license: MIT
metadata:
  category: productivity
  tags: [compaction, context, memory, continuity, sessions]
---

# Compactor

Compaction replaces the conversation with a summary. The summary keeps the gist but drops exact user
wording, ids, paths, half-finished steps and the "why" behind decisions. This skill writes those down
first, and the plugin's hooks put them back right after compaction.

Two layers, because they live for different lengths of time:

| Layer | What goes there | Lifetime |
|---|---|---|
| **Memory** (the harness's persistent memory, e.g. the auto-memory directory and its `MEMORY.md` index) | Durable facts worth knowing in *future* sessions: user preferences and corrections, project facts not in the repo, environment mappings, standing rules | Kept; follows the memory system's own rules |
| **State file** `~/.claude/compactor/pending/<token>.md` | This session's working state: goal, decisions, state, in-flight, next steps | Deleted automatically once re-injected after compaction |

How the hooks find the right file without knowing the session id: the file name is a random token, and
the token lands in this session's transcript when you write the file. The `PreCompact` hook claims every
pending file whose token appears in its transcript; the `SessionStart` hook (source `compact`) injects it
and deletes it. Hook script: `${CLAUDE_PLUGIN_ROOT}/scripts/compactor_hook.py`.

## Phase 1: save (when the user runs the skill)

1. **Collect the state from the conversation**, not from memory of a summary. Re-read recent turns and any
   state/ledger files the session keeps. Capture:
   - **Goal**: what the user asked for, in their words, and the definition of done.
   - **User decisions**: every ruling, preference or approval, *verbatim* with date, and its scope (what it
     covers, what it doesn't). Peer or tool claims are not user decisions; label them.
   - **Current state**: what is done (with commit shas, PR/issue links, file paths), what is verified and
     what is not.
   - **In flight**: running sessions, subagents, background jobs, builds, held messages; who/what to wait on.
   - **Next steps**: the ordered plan from here, and what is blocked on whom.
   - **Key references**: absolute paths, ids, URLs, branch names, env/resource names, command IDs.
   - **Constraints and gotchas**: rules that bit this session, refusals and their workaround, things not to do.
   - **Open questions** for the user.
2. **Write durable facts to memory** (only if the session has a memory system): facts that would help a
   *future* session, following that system's rules (one fact per file, update instead of duplicate, no
   secrets, nothing the repo already records). Skip anything that only matters to this session.
3. **Write the state file.** Keep it under **8,000 characters** (the hook can inline about 9,000; larger
   files are left on disk with an instruction to read them). Prefer bullets; link to files on disk instead of
   copying them. Never put secrets or credentials in it. Write it in ONE Bash call so the token is in the
   transcript:

   ```bash
   TOKEN="cmp-$(uuidgen | tr 'A-Z' 'a-z')" && mkdir -p ~/.claude/compactor/pending && cat > ~/.claude/compactor/pending/"$TOKEN".md <<'COMPACTOR_EOF'
   # Session state (saved by compactor, <YYYY-MM-DD HH:MM>)
   cwd: <working directory>
   ## Goal
   ...
   ## User decisions (verbatim)
   ...
   ## Current state
   ...
   ## In flight
   ...
   ## Next steps
   ...
   ## Key references
   ...
   ## Constraints / gotchas
   ...
   ## Open questions
   ...
   COMPACTOR_EOF
   echo "compactor token: $TOKEN" && wc -c ~/.claude/compactor/pending/"$TOKEN".md
   ```

   Repeat the printed `compactor token: …` line in your reply (it makes the transcript match certain).
   Do not list or read `~/.claude/compactor/` otherwise: another session's token in your transcript would
   make your hook claim its file.
4. **Tell the user** in two lines: what was saved (memory files + state file size), and to run `/compact`
   now. You cannot run `/compact` yourself. Optionally suggest focus text, e.g.
   `/compact keep the decisions list and next steps`. Then stop and wait.

## Phase 2: rehydrate (automatic after compaction)

After compaction the `SessionStart` hook adds a `[compactor] This session was just compacted…` block to
context and deletes the file. When you see that block:

1. Re-adopt the goal, decisions and next steps from it. Re-read any memory files or state files it names
   if you need their detail.
2. If the block says the state was too large to inline: read the named file fully with the Read tool, then
   delete it with the `rm -f` command it gives.
3. Tell the user in one line that the session was rehydrated, and continue with the next step (or ask the
   open question if the next step waits on them).

**Manual fallback** (the plugin's hooks are disabled, or the user runs the skill again after compacting
and no `[compactor]` block appeared): look for the token line in the compaction summary or the visible
conversation, read `~/.claude/compactor/pending/<token>.md` (or `~/.claude/compactor/claimed/*.md` whose
content clearly matches this session), adopt it, then delete exactly that file. Never read or delete files
that belong to another session; if unsure which file is yours, ask the user.

## Rules

- One state file per save; saving again before compacting simply adds a newer file (the hook concatenates
  them oldest first, newest last). If the user saves twice, the newer one wins on conflicts.
- Stale files (older than 7 days) are swept by the hook. Nothing else is written outside `~/.claude/compactor/`
  and the memory directory.
- No secrets, tokens or credentials in either layer.
- Absolute dates only ("2026-10-17", not "yesterday").
