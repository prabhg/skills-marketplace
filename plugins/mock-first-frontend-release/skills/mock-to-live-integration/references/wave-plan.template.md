# Integration plan

> Inputs: INTEGRATION_INVENTORY.md ({date}). Base: {branch}@{sha}.

## Wave 0
**W0-1 Schema + documents** · write scope: schema snapshot, operation documents/client stubs for every
BUILD op, generated types · DoD: generated types contain {domains}; typecheck green.

## Wave 1..n
**{ID} {feature}** · write scope: {files/dirs, disjoint} · blocked_by: {ids, owner questions} · risk: {low/med/high} · tier: {model/reviewer}
- Ops: {list}
- Probe: {op → expected result; call budget if paid/rate-limited}
- Data source: {seed id / test account / backend dev seed request}
- DoD: unit (mapper id kinds, error mapping) · gate (lint/typecheck/tests, tree clean after formatter) · dependency fingerprint unchanged or build planned · device/sim check {agent-run | owner-run}
- Registry rows: {ops}

## Last wave: mock cleanup
Delete fixtures, mock storage/keys, seed version, dev-menu mock items, dead cache keys; registry = zero MOCK outside EXCLUDED.

## Backend gaps (filed / to file)
| Id | Kind (BUG/CONTRACT/TOOLING) | Operation | Observed vs wanted | Blocks |
|---|---|---|---|---|

## Owner questions (one batch)
| Id | Question | Recommendation | Blocks |
|---|---|---|---|

## Risks
- First-ever backend calls: {list}; budget backend fix loops.
- Short-lived URLs vs cache times.
- Id kind mismatches: {list}.
- Irreversible operations: owner-run only.
- Shared device/simulator between parallel tickets: one ticket on it at a time.
