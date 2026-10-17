#!/usr/bin/env python3
"""compact-prepare hooks.

The compact-prepare skill writes ~/.claude/compact-prepare/pending/<token>.md, and the token appears in the
session transcript (the Bash call that wrote the file). Hooks receive session_id and transcript_path
on stdin, so they can tell which pending file belongs to this session without the skill knowing
its session id.

  precompact  PreCompact hook: move this session's pending file(s) to claimed/<session_id>.md.
  rehydrate   SessionStart(compact) hook: print the claimed (or still pending) state into context,
              then delete it. Oversized state is left on disk with an instruction to read it.

Never fails the session: any error exits 0 with no output.
"""

import json
import os
import sys
import time

ROOT = os.path.join(os.path.expanduser("~"), ".claude", "compact-prepare")
PENDING = os.path.join(ROOT, "pending")
CLAIMED = os.path.join(ROOT, "claimed")
MAX_INLINE = 9000  # Claude Code caps hook additionalContext at 10,000 chars
STALE_SECONDS = 7 * 24 * 3600


def read_stdin():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def transcript_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def matching_pending(transcript):
    """Pending files whose token appears in this session's transcript, oldest first."""
    if not transcript or not os.path.isdir(PENDING):
        return []
    hits = []
    for name in os.listdir(PENDING):
        if not name.endswith(".md"):
            continue
        token = name[:-3]
        if len(token) >= 8 and token in transcript:
            p = os.path.join(PENDING, name)
            hits.append((os.path.getmtime(p), p))
    return [p for _, p in sorted(hits)]


def safe_id(session_id):
    return "".join(c for c in session_id if c.isalnum() or c in "-_")


def claim(session_id, transcript):
    """Append matching pending files into claimed/<session_id>.md (newest last) and remove them."""
    files = matching_pending(transcript)
    if not files or not session_id:
        return None
    os.makedirs(CLAIMED, exist_ok=True)
    dest = os.path.join(CLAIMED, safe_id(session_id) + ".md")
    with open(dest, "a", encoding="utf-8") as out:
        for p in files:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                out.write(f.read().rstrip() + "\n\n")
            os.remove(p)
    return dest


def sweep_stale():
    now = time.time()
    for d in (PENDING, CLAIMED):
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            p = os.path.join(d, name)
            try:
                if now - os.path.getmtime(p) > STALE_SECONDS:
                    os.remove(p)
            except Exception:
                pass


def emit(context):
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}
    }))


def has_pending():
    return os.path.isdir(PENDING) and any(n.endswith(".md") for n in os.listdir(PENDING))


def precompact(data):
    if not has_pending():  # skip reading a multi-MB transcript on every unrelated compaction
        return
    claim(data.get("session_id", ""), transcript_text(data.get("transcript_path", "")))


def rehydrate(data):
    session_id = data.get("session_id", "")
    dest = os.path.join(CLAIMED, safe_id(session_id) + ".md") if session_id else None
    if (not dest or not os.path.exists(dest)) and has_pending():
        # PreCompact did not run (or ran in an older plugin version): claim now.
        dest = claim(session_id, transcript_text(data.get("transcript_path", "")))
    sweep_stale()
    if not dest or not os.path.exists(dest):
        return
    with open(dest, "r", encoding="utf-8", errors="ignore") as f:
        state = f.read().strip()
    if not state:
        os.remove(dest)
        return
    header = (
        "[compact-prepare] This session was just compacted. Below is the state you saved with the compact-prepare "
        "skill before compaction. Treat it as your own notes: re-adopt the goal, decisions, state and next "
        "steps, and continue the work. User rulings quoted inside are the user's words. Also re-read any "
        "memory files it names if you need their detail.\n\n"
    )
    if len(header) + len(state) <= MAX_INLINE:
        emit(header + state)
        os.remove(dest)
    else:
        emit(
            header
            + "The saved state is too large to inline (" + str(len(state)) + " chars). Read the whole file now: "
            + dest
            + "\nAfter you have read it, delete it with: rm -f '" + dest + "'\n\nFirst part:\n\n"
            + state[: MAX_INLINE - len(header) - 600]
        )


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    data = read_stdin()
    try:
        if mode == "precompact":
            precompact(data)
        elif mode == "rehydrate":
            rehydrate(data)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
