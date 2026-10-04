# Templates

Replace `<…>`. Keep them short — these files load on every session start.

## project/AGENTS.md

````markdown
# project/ — delivery-planning repo

A special git repo (branch **`planning`**, no `main`, local only unless the owner adds a remote). It is
**not part of the product**: it holds the project's planning and management docs, needed only by whoever
leads delivery and planning. **Not for the team.**

Doc placement across repos:
- Each product repo keeps its own reference docs (incl. its own architecture doc) in its own `docs/`.
- A repo's docs *may* reference another product repo's docs, but ideally don't (that repo may not be cloned).
- **No repo ever references `project/`.** Cross-repo architecture, backlog, handoffs and delivery-planning
  docs live here.

Commit here after any doc change.

**Keep planning docs small and few.** Every doc adds to the context of every agent that reads it. Prefer
editing an existing doc over adding one; delete what no longer earns its place.

## Load on start

1. `docs/ARCHITECTURE.md` — bird's-eye view across repos.
2. `docs/BACKLOG.md` — open tickets only.
3. `temp/README.md` — index of live handoffs (open one only if your task touches it).

Do **not** load `docs/archive/` unless looking up a specific closed id.

## Layout

| Path | What | Git |
|---|---|---|
| `docs/` | ARCHITECTURE, BACKLOG (read on load) + planning docs moved out of repos | commit |
| `docs/archive/` | Closed tickets, one line each. Not read on load | commit |
| `temp/` | Short-term handoffs / progress docs | commit |
| `local/` | Scratch, logs, sensitive or machine-specific temp files | gitignored |
| `<research>/`, `<mocks>/` | <what> | <commit / ignored> |

## Rules

1. **Never reference `project/` from a repo** (paths, ticket ids, doc names) in code, comments, commits,
   PR bodies or repo docs. When a repo needs a fact, write it into that repo's `docs/`.
2. **Sync on fetch.** Any agent that fetches/pulls `<integration branch>` of any repo, or scans it for latest
   code: `git log <synced sha>..origin/<branch>` per repo → update ARCHITECTURE / BACKLOG → bump `synced:` →
   commit. Repo code wins over these docs.
3. **Temp docs** (`temp/`, `local/`) — every agent that reads or writes in `project/` enforces this:
   - Each starts with this snippet (and `temp/` docs get a row in `temp/README.md`):
     ```
     > Purpose: <why this doc exists>
     > Use: <who reads it, for what, when>
     > Delete when: <checkable condition, e.g. "next agent has read it" or "origin/dev contains the X merge">
     > Owner: <agent/session> · Created: YYYY-MM-DD
     ```
   - **Delete as soon as it is no longer needed.** Session-state handoffs (e.g. before `/compact`, or
     agent→agent) and pure knowledge-transfer notes are deleted by the **next agent right after reading**
     — move durable facts into a main doc, repo doc or memory first.
   - Keep `temp/` and `local/` uncluttered: whenever you touch `project/`, delete docs whose delete-when
     holds; add the snippet to any doc missing it if its purpose is clear, else ask the owner.
   - Delete = `git rm` in `temp/`, move to `~/.Trash` in `local/`.
4. **Treeshake** on every edit: current state only, no decision history (cite `repo@sha`), compressed,
   link into repo docs. ARCHITECTURE ≤ ~200 lines; BACKLOG open tickets only.
5. **Backlog hygiene.** Ticket = id, title, severity, repos, gate, evidence (`path:line @sha`), fix. Closed →
   remove from BACKLOG, append `id | title | closed date | repo@sha or reason` to `docs/archive/BACKLOG-CLOSED.md`.
   Never reopen in place. Next free id lives in the BACKLOG header.
6. **No secrets** (names fine, values never). **Absolute dates** only.
7. Paths are relative to the named repo (`<repo>: path`), or to `project/` when prefixed `project/`.
````

## project/.gitignore

```
local/*
!local/README.md
.DS_Store
<confidential third-party material>
```

## docs/ARCHITECTURE.md

```markdown
# <Project> — cross-repo architecture (bird's-eye)

> synced: <repo> <branch> @ `<sha>` · <date> — run `git log <sha>..origin/<branch>` before trusting details.
> Current state only. Detail lives in repo docs (linked); history lives in git.

## 1. Repos            (table: repo | exists/planned | role)
## 2. <repo> …          (stack + versions, structure, key flows, state, auth, env, tests — paths, not prose)
## 3. Delivery pipeline (branches, workflows, build/deploy, versioning, current release state)
## 4. Planned systems   (design doc path + section index with line numbers)
## 5. Environments      (dev/staging/prod identifiers per repo; how to tell them apart)
## 6. Cross-repo invariants
```

## docs/BACKLOG.md

```markdown
# Backlog — open tickets only

> synced: <repo> <branch> @ `<sha>` · <date> · next id: **P-001**
> Evidence paths are repo-relative @ `<sha>` unless noted. Closed → one line in `archive/BACKLOG-CLOSED.md`.
> Severity: **critical** = fix before any prod release · high · medium · low. "Gate" = latest moment to fix.

## Critical
**P-001 · critical · <repos> · gate: <when>** — <title>
- <evidence path:line> <what is wrong>
- Fix: <one line>

## High
## Medium
## Low
```

## docs/archive/BACKLOG-CLOSED.md

```markdown
# Closed tickets (not read on load)

`id | title | closed | repo@sha or reason`
```

## temp/README.md

```markdown
# temp/ — live handoffs index

> Purpose: index of live temp docs so agents can judge them without opening each one.
> Use: read on load; add a row when creating a temp doc, remove it when deleting one.
> Delete when: never (permanent index).

| Doc | Purpose | Use | Delete when | Owner / created |
|---|---|---|---|---|

## Drift notes (<date>) — read before executing
```

## local/README.md

```markdown
# local/

> Purpose: explains this gitignored folder.
> Use: read when creating a local temp doc.
> Delete when: never (permanent).

Gitignored scratch: logs, machine-specific notes, sensitive temp files. Same snippet and deletion rules as
`temp/` (see `../AGENTS.md` rule 3); delete by moving to `~/.Trash`.
```

## Wrapper AGENTS.md section

```markdown
## `project/` (planning docs) — always applies

- On session start read `project/AGENTS.md`, `project/docs/ARCHITECTURE.md`, `project/docs/BACKLOG.md`.
  Never load `project/docs/archive/` unless looking up a closed ticket.
- **Sync rule:** after fetching/pulling `<branch>` of any repo, or scanning it for latest code, run
  `git log <synced sha>..origin/<branch>` and update ARCHITECTURE/BACKLOG + `synced:`, then commit in `project/`.
- **Never reference `project/`** from any repo. Each repo keeps its own facts in its own `docs/`; repo docs may
  point at another product repo's docs but ideally don't.
```
