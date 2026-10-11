# Messages between coordinator and lane agents

Short, one topic each, first line self-contained (the receiver's owner may only see the first line).
Prefix: `[COORD→<agent>]` from you, `[<agent>→COORD]` to you. Reply to a peer with its `from` address.

## Coordinator → agent

- **HELLO**: `I'm "<coordinator name>", coordinator. Your lane: <repos>. Command IDs: <block>, next <n>.
  Rulings: <path>. Handoff at <n>% context. Coordinated mode: report to me, minimal text in your session,
  owner questions + commands via me, context % in every status. Send me every approval you need, one list.`
- **RULING**: `R<n> (verbatim in <path>): "<text>". For you this means: <1–3 lines>. Copy it into your ledger.`
- **ROUTE**: `BUG from <lane>: <op> <error> <evidence path>. Yours because <repo>. Fix as a reviewed
  ticket; send me the fix sha.` / `CONTRACT from <lane>: <what changed, field names, example>; act: <…>.`
- **GRANT / LOCK / RELEASE**: `Lane grant: <repo> for <ticket> only, conditions: <owner approval covers
  pushes there; serialise>.` / `Lock <resource> held by <lane> until <condition>.`
- **HOLD**: `HOLD <ticket/sha>: <reason>. Don't push/merge. Keep the branch; I'm asking the owner.`
- **PARK / RESUME**: `Park at a clean boundary, start nothing new, commit the ledger, reply with a
  one-line parked state.` / `Resume: re-check remote state first, then continue <queue>.`
- **HANDOVER**: `You're at <n>%: stop at a clean boundary, write the handoff for "<lane> v<n+1>", send
  me its start prompt. Stay open for its questions, then retire.`

## Agent → coordinator

- `STATUS <ctx %>: landed <sha/ticket>; in flight <…>; next <…>; needs owner: <none | …>`
- `ASK: <decision>, options a|b, recommend a because …, cost if wrong …` (you batch these for the owner)
- `CMD request: <cwd> · <command> · why · success looks like` (you assign/confirm the ID and print it)
- `BUG <op> <error> <repo guess> · evidence <path>`
- `REFUSED: <action> was refused by <classifier/harness>; parked; owner route: <command or non-auto session>`
- `PARKED: <one line>` / `HANDOFF READY: <path>; start prompt: <text>`

## Successor introduction

A successor's first messages: to the coordinator `[<lane> vN→COORD] CLAIMED <ledger path> at <ts>; ID
block <block> next <n>` and to its predecessor `RETIRE: <successor> owns <ledger> from <ts>; confirm and
go quiet.` The coordinator updates its ledger (agent name, ID block, last contact).
