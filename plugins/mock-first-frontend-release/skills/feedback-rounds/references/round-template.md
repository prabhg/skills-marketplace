# Design round {N}

Build/channel shipped: {version + build id or preview URL} · Opened: {YYYY-MM-DD} · Closed: {date or open}
Sources: {tester notes, annotated files, designer mock version}

## Work list

| Id | Screen | Source | Change | Type | Decision | Done |
|---|---|---|---|---|---|---|
| R{N}-1 | checkout | tester A, note 3 | move total above the button | visual | DO | |
| R{N}-2 | order detail | designer mock v2, p.4 | show delivery window | data | DO: add `deliveryWindow` to `getOrder` mock + registry | |
| R{N}-3 | settings | tester B | dark mode | visual | LATER (R{N+1}) | |
| R{N}-4 | profile | designer mock v2 | public follower count | behaviour | NO: owner, privacy ({date}) | |
| R{N}-5 | home | tester B | "make it feel nicer" | visual | ASK (Q1) | |

## Bugs

| Id | Screen | Source | Symptom | Suspected cause | Done |
|---|---|---|---|---|---|
| R{N}-B1 | board | tester A | card jumps back after drop | mutation patches a key the list does not read | |

## Owner questions (one batch)

1. R{N}-5: what would "nicer" mean to you? Recommendation: …

## Contract changes this round

Operations added/changed (from data/behaviour items): {list, or "none"}.

## Round notes for testers

{Short list of what changed, by item id.}
