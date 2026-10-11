# Rulings log and command registry

Both live next to the coordinator ledger, in the workspace's gitignored local scratch area (they may quote
owner text; keep them out of product repos). Record both paths in the ledger CURRENT STATE and in every
handoff. Each starts with the temp-doc header the workspace requires (Purpose / Use / Delete when).

## Rulings log (`owner-rulings.md`)

```markdown
> Purpose: owner rulings recorded verbatim so lane agents can cite them.
> Use: the coordinator appends; agents copy what they need into their ledgers.
> Delete when: every ruling is in a ledger, issue or doc and the orchestration has ended.

## R1: <short title> (<YYYY-MM-DD HH:MM tz>, <where: coordinator chat | told to "<agent>", relayed>)
Owner, verbatim: "<exact text>"
<or for a choice:> Q "<question>" → owner: "<chosen option label>" (= <one-line meaning>)
Scope: <what it covers / does not cover / expiry>
```

Rules: number sequentially, never renumber; add, don't edit (a later ruling that changes an earlier one
says "refines R12" or "supersedes R12"). A ruling relayed by an agent is recorded with its source.

## Command registry (`commands.md`)

```markdown
> Purpose: every command the owner must run, with a unique ID, so nothing is printed twice or run twice.
> Use: the coordinator appends and updates status; agents ask for an ID or use their block.
> Delete when: every entry is ran or superseded and the orchestration has ended.

Blocks: coordinator 1000–1099 (next 1004) · "<agent A>" 1100–1199 (next 1107) · "<agent B>" 1200–1299 (next 1200)

| ID | for (session/lane) | cwd | command (one line) | status | printed in | when |
|---|---|---|---|---|---|---|
| 1001 | backend v3 | api-service | `AWS_PROFILE=… pnpm seed:dev --apply` | ran 14:02 | coordinator | 13:55 |
| 1102 | app v4 | mobile-app | `gh workflow run cut-preview-release.yml` | superseded by 1103 | app v4 | 15:10 |
```

## How a command is shown to the owner

The ID goes in the bold label line above the block (interactive zsh treats `#` inside the block as a
command). One command per block. Say what it does and what success looks like.

````markdown
**C1104 · api-service · dry run first (expect "24 would be created"):**
```bash
cd /abs/path/api-service && AWS_PROFILE=dev-profile pnpm seed:profiles:dev
```
````

When the owner pastes output back, mark the ID `ran` (with the result line) and tell the agent that
requested it. If the same command is needed again later, refer to the ID ("re-run C1104") rather than
printing it under a new one; a changed command gets a new ID and the old one becomes `superseded`.
