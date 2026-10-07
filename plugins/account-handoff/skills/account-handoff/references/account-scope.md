# What follows you across accounts, and what does not

Use this as a checklist in the departure inventory and the arrival capability check. Verify against the
machine when in doubt; products change. Only items the project actually uses belong in the handoff.

## Follows (local, keyed by folder path or machine)

| Thing | Where |
|---|---|
| Repos, worktrees, branches, stashes, uncommitted changes | the project folders |
| Project instructions | `CLAUDE.md`, `AGENTS.md`, `.claude/` in the project |
| Memory directory and its index | `~/.claude/projects/<slug>/memory/` |
| Session transcripts (every account's) | `~/.claude/projects/<slug>/<session-id>.jsonl` |
| User settings, hooks, permissions, keybindings, status line | `~/.claude/settings.json`, `settings.local.json`, `~/.claude/hooks/` |
| Locally installed skills, plugins and marketplaces | `~/.claude/skills/`, `~/.claude/plugins/` |
| Project-configured MCP servers | `.mcp.json` and the local servers they start |
| CLI logins | `git` credentials, `gh`, cloud CLIs, package registries |
| Other local tools' data | local memory plugins, databases, caches |
| This skill's handoff state (at most five small files) | `~/.claude/projects/<slug>/account-handoff/` |

## Does not follow (stored with the account, or alive only while it is logged in)

| Thing | What happens | Workaround to write in the handoff |
|---|---|---|
| Running sessions, subagents, monitors, timers, background shells | stop at logout | state blob + restart command or prompt |
| Desktop sidebar: session list, pins, groups, titles, unread | per account; other account sees none | transcript paths; the session digest |
| Usage limits and plan | per account | note which account has headroom and when the other resets |
| Model availability, fast mode, beta features | per plan / organization | name the model in use and an acceptable fallback |
| Cloud sessions, routines, remote triggers, scheduled cloud agents | stay with the account, keep running or not under it | name, schedule, full prompt; recreate with the user's OK |
| Scheduled tasks stored by the desktop app | check whether listed after the switch | same: name, schedule, prompt |
| Connectors and OAuth-authorized MCP servers (design tools, analytics, issue trackers, drives) | sign-in is per account | list which are needed; the user signs in again |
| Browser extension pairing and browser-pane sign-ins | may need re-pairing; site logins live in the browser profile | note which sites the work needs |
| Published artifacts, hosted docs, shared links | owned by the publishing account; other account may only view | save content locally before leaving; list URLs and owners |
| claude.ai projects, chat history, chat memory, custom styles | per account | anything load-bearing must be written to local files |
| Organization skills, plugin catalog, managed settings and policies | per organization | name the capability that will be missing and a local substitute |
| Pull-request / CI monitors bound to a session | stop with the session | PR numbers and what to watch |

## Signals worth one line to the user

- A managed (work) account may record usage for its organization and can restrict tools. Personal projects on
  a work seat, or work projects on a personal seat, are the user's decision; mention it once per account.
- If durable project state is found in an account-scoped place (an artifact, a cloud session's memory, a chat
  project), recommend moving it into local files or git so the next switch is free.
