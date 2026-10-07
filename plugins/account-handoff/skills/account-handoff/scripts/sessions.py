#!/usr/bin/env python3
"""Digest of recent Claude Code sessions for a project, read from local transcripts.

    python3 sessions.py [project-root] [--days 3] [--max 15]

Transcripts live in ~/.claude/projects/<slug>/<session-id>.jsonl and are keyed by folder
path, not by account, so every account on this machine can read them. Read-only.
Prints one block per session: id, last activity, title, turn count, first prompt, last
prompt and the tail of the last assistant message, with two flags: CUT OFF MID-STEP (the
last assistant turn requested a tool and got no result) and ACTIVE IN LAST 30 MIN (may
still be running). Text that looks like a credential is masked, but treat the output as
sensitive anyway: it is raw chat.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path


def project_dirs(root: str) -> list[Path]:
    base = Path.home() / ".claude" / "projects"
    if not base.is_dir():
        return []
    slug = re.sub(r"[^A-Za-z0-9]", "-", root)
    # the project itself plus sessions opened in sub-folders (their slug extends this one)
    return sorted(p for p in base.iterdir() if p.is_dir() and p.name.lower().startswith(slug.lower()))


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


# Transcripts are raw chat: people paste credentials into them. Mask anything that looks like one before
# printing, so a digest can be read (and quoted into a handoff) without spreading it further.
SECRET_PATTERNS = [
    re.compile(r"(?i)\b(pass(?:word|wd|phrase)?|pwd|secret|token|api[_-]?key|access[_-]?key|bearer|authorization)\b(\s*(?:is|=|:)?\s*)(\S+)"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"),  # JWT
    re.compile(r"\b(?:sk|pk|rk)[-_](?:live|test|ant)?[-_]?[A-Za-z0-9_-]{16,}"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\b[A-Fa-f0-9]{40,}\b"),
    re.compile(r"\b[A-Za-z0-9+/]{48,}={0,2}"),
]


def redact(s: str) -> str:
    s = SECRET_PATTERNS[0].sub(lambda m: f"{m.group(1)}{m.group(2)}[redacted]", s)
    for pat in SECRET_PATTERNS[1:]:
        s = pat.sub("[redacted]", s)
    # an email followed by a "/" or ":" separated word is a classic pasted login pair
    return re.sub(r"([\w.+-]+@[\w-]+\.[\w.-]+)\s*[/:|,]\s*\S+", r"\1 / [redacted]", s)


def clip(s: str, n: int) -> str:
    s = redact(re.sub(r"\s+", " ", s).strip())
    return s if len(s) <= n else s[: n - 1] + "…"


def digest(path: Path) -> dict:
    title = first = last_prompt = last_assistant = cwd = ""
    turns = 0
    last_type = ""
    pending_tool = False
    with path.open(errors="replace") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            t = o.get("type")
            cwd = cwd or o.get("cwd") or ""
            if t == "custom-title":
                title = o.get("customTitle") or title
            elif t == "last-prompt":
                last_prompt = o.get("lastPrompt") or last_prompt
            elif t in ("user", "assistant") and not o.get("isSidechain"):
                msg = o.get("message") or {}
                content = msg.get("content")
                txt = text_of(content)
                if t == "user":
                    is_tool_result = isinstance(content, list) and any(
                        isinstance(b, dict) and b.get("type") == "tool_result" for b in content
                    )
                    relayed = txt.lstrip().startswith(("<", "Another Claude session sent a message", "[SYSTEM NOTIFICATION"))
                    if txt and not is_tool_result and not relayed:
                        turns += 1
                        first = first or txt
                        last_prompt = txt
                    if is_tool_result:
                        pending_tool = False
                else:
                    if txt:
                        last_assistant = txt
                    pending_tool = isinstance(content, list) and any(
                        isinstance(b, dict) and b.get("type") == "tool_use" for b in content
                    )
                last_type = t
    return {
        "title": title,
        "turns": turns,
        "first": first,
        "last_prompt": last_prompt,
        "last_assistant": last_assistant,
        "cwd": cwd,
        # the last assistant message asked for a tool and no result followed: it was cut off mid-step
        "cut_off": pending_tool,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=os.getcwd())
    ap.add_argument("--days", type=float, default=3)
    ap.add_argument("--max", type=int, default=15)
    ap.add_argument("--exclude", default="", help="session id to leave out (the session running this)")
    a = ap.parse_args()
    root = os.path.realpath(a.root)
    cutoff = time.time() - a.days * 86400
    files = []
    for d in project_dirs(root):
        files += [f for f in d.glob("*.jsonl") if f.stat().st_mtime >= cutoff and f.stem != a.exclude]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        print(f"no session transcripts modified in the last {a.days:g} days for {root}")
        return 0
    print(f"# {min(len(files), a.max)} of {len(files)} sessions, last {a.days:g} days, newest first ({root})")
    for f in files[: a.max]:
        d = digest(f)
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(f.stat().st_mtime))
        mins = int((time.time() - f.stat().st_mtime) / 60)
        flags = (" · CUT OFF MID-STEP" if d["cut_off"] else "") + (" · ACTIVE IN LAST 30 MIN" if mins <= 30 else "")
        print(f"\n## {d['title'] or '(untitled)'}{flags}")
        print(f"- id: {f.stem} · last activity: {when} · user turns: {d['turns']} · transcript: {f}")
        if d["cwd"] and os.path.realpath(d["cwd"]) != root:
            print(f"- opened in: {d['cwd']}")
        if d["first"]:
            print(f"- started as: {clip(d['first'], 160)}")
        if d["last_prompt"] and d["last_prompt"] != d["first"]:
            print(f"- last prompt: {clip(d['last_prompt'], 200)}")
        if d["last_assistant"]:
            print(f"- last answer ends: {clip(d['last_assistant'][-500:], 320)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
