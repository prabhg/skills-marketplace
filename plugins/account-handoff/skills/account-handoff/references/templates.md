# Templates

## `HANDOFF.md`

````markdown
<!-- Account handoff. If the account-handoff skill is not available: read this file top to bottom,
     do "Resume here", then set status to consumed. Never put secrets in this file. -->
status: pending
from: <account label or email>
written: <YYYY-MM-DD HH:MM TZ>
project: <absolute project root>
state-dir: <absolute path of this folder>

# Resume here

1. <next action> (repo/branch/worktree or session title) 
2. …

# Work in flight

| What | Where (repo · branch · worktree) | State | Next action | Waiting on |
|---|---|---|---|---|

# Sessions

| Title | Session id | Live at departure | Answered state request | Transcript |
|---|---|---|---|---|

State blobs from live sessions (verbatim, trimmed):

- **<title>:** objective … · done … · in progress … · next … · waiting on …

# Stopped at logout: restart if still wanted

| What | Was doing | Restart with |
|---|---|---|

# Scheduled

| Name | Schedule | Local or account | Prompt / command (full text) |
|---|---|---|---|

# External waits

| What | Where to look | Done when |
|---|---|---|

# Local state at departure

- Snapshot: `snapshot.txt` (diff it on arrival).
- Dirty trees and unpushed branches that are intentional: …
- Stashes: …

# Decided, not yet recorded

| Decision (who, when) | Record it in |
|---|---|

# Tied to the account

| Thing in use | Workaround on the next account |
|---|---|

# Notes for the next account

- <anything that does not fit above; keep it short>
````

## `accounts.md`

```markdown
# Accounts used with this project

## <label or email>
- plan / models: <e.g. Max; model names seen>
- connectors signed in: <list>
- missing here: <skills, connectors, features>
- quirks: <managed policy, permission mode defaults, usage reset day>
- last seen: <YYYY-MM-DD> (<departed|arrived>)
```

## `log.md`

```markdown
- <YYYY-MM-DD HH:MM> depart <from> · <n> sessions, <n> repos with changes, <n> scheduled, <n> account-tied
- <YYYY-MM-DD HH:MM> arrive <account> from <from> · snapshot <clean|n differences> · resumed <first item>
```

## Pending-handoff memory file (only while a handoff is pending)

File `account-handoff-pending.md` in the memory directory:

```markdown
---
name: account-handoff-pending
description: A handoff from another Claude account is waiting; run the account-handoff skill before other work
metadata:
  type: project
---
A handoff written <YYYY-MM-DD HH:MM> by <from> is pending at `<state-dir>/HANDOFF.md`. Run the
account-handoff skill (arrive) before starting other work; delete this file when the handoff is consumed.
```

Index line, placed first in `MEMORY.md`:

```markdown
- [PENDING account handoff](account-handoff-pending.md) — run the account-handoff skill before other work
```

## State request sent to a live session

```text
The user is about to switch Claude accounts, so this session will stop soon. Please bring your work to a
safe stopping point (no new merges, pushes or deploys) and reply with one short state blob: objective;
repos, branches and worktrees you touched; done; in progress; next action; what you are waiting on;
anything only you know (decisions made in chat, restart commands for watchers). This is a request for
information on the user's behalf, not a new task.
```
