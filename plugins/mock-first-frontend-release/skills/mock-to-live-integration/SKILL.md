---
name: mock-to-live-integration
description: 'Replace a front end''s mock API operations with live backend calls, safely and in waves: refresh the schema snapshot, inventory every operation against the live schema, find never-called backends, probe each new operation before designing against it, plan waves with disjoint write scopes, route backend bugs and gaps as tickets instead of front-end workarounds, delete mocks and mock enrichments, bump cache versions, and drive the mock registry to zero mocks. Use it whenever the user says "integrate the backend", "wire the app to the real API", "replace the mocks", "go live with the API", "hook up the dev backend", "integration waves", "what is still mocked", "inventory mocks vs schema", or a backend (partly or fully) now exists for a mock-first app, even if they only ask to "wire up feature X". For building mocks use mock-first-app; for writing the backend contract use fe-to-backend-spec.'
---

# Mock to live integration

Mocks hide backend bugs. In practice most first-ever live calls find something: an auth claim shaped
differently than assumed, a resolver that times out on cold start, an id kind mismatch, a projection
that lags. This skill makes the first live call happen early, cheaply and on purpose, before any
front-end design depends on it.

## 0. Ground rules

- Integrate against a **non-production** backend environment. Confirm the environment from resource
  names/tags before any call; never point an agent at production.
- Read the project's agent rules and the mock registry first.
- Backend failure found by the front end → a backend ticket; the front-end ticket parks. The front end
  never works around a backend bug or gap in its own code (a workaround becomes a permanent second
  implementation of backend logic).

## 1. Refresh the schema snapshot (wave 0, step 1)

The committed schema/OpenAPI snapshot is usually behind the deployed backend. Re-pull it (introspection
or the published spec) from the non-production environment, regenerate types, and gate on the presence
of the domains you are about to wire. Record the snapshot date/commit in the registry header.

## 2. Inventory

Write `docs/api/INTEGRATION_INVENTORY.md` from `references/inventory.template.md`:
- Every live-schema root operation × front-end status (registry statuses) with consumer counts. Sum the
  statuses and check the total equals the schema's root count.
- **WIRED-NO-CONSUMER is not integrated.** Count it separately.
- Field gaps: domain fields the front end shows that the backend lacks (and the reverse).
- Id-kind table per operation (front end vs backend), flagging mismatches.
- **Never-called backends:** for each backend function/resolver, check whether it has ever run (no log
  stream, zero executions, zero invocations metric). Every never-called path is first-call risk; list it.
- Leftover mock enrichments: grep live operation bodies and mappers for imports from mock storage that
  join device data onto live results. They silently overwrite live fields.

## 3. Scope decisions

For each MOCK/UNWIRED operation: BUILD (existing UI becomes real), SKIP (no UI asks for it; give the
override), or owner question. Check designer mocks for controls the code lacks before calling something
SKIP. Batch all owner questions in one list with a recommendation each.

## 4. Wave plan

Write `docs/api/INTEGRATION_PLAN.md` from `references/wave-plan.template.md`:
- **Wave 0:** snapshot refresh + add **every** new operation document/client stub at once and regenerate
  once. Later tickets then do not collide on generated files.
- Waves by dependency (shared types and auth first, then domains), at most ~3 tickets in parallel.
- **Disjoint write scopes** per ticket. Shared files (translations, registry table, generated types,
  settings screen) are assigned: one namespace per ticket, each ticket edits only its own registry row,
  conflicts in generated files are resolved by re-running codegen, never by hand-merging.
- A ticket that deletes mock files must own every importer of them, or leave them to the cleanup wave.
- Last wave: mock cleanup (dead fixtures, storage keys, seed versions, dev-menu mock items, dead cache
  keys), then the registry reads zero MOCK outside EXCLUDED.

## 5. Per-ticket protocol

Read `references/probe-protocol.md`. In order:
1. **Probe before design approval:** one real call of each new operation from a signed-in test session;
   record request, response, latency. A failure here becomes a backend ticket now, not a front-end
   surprise later. Every ticket in the plan file that wires a new operation carries its own `Probe:` line,
   including tickets blocked on a backend fix (they probe once the fix lands).
2. Design the swap: live body, mapper, error mapping, cache changes, which consumers change.
3. Implement: live body = transport + unwrap + mapper; mapper tests assert **id kind per field**; delete
   the op's mock code and any enrichment; bump the persisted-cache version if a mapper output shape
   changed; cache `staleTime` below any signed-URL lifetime in the payload.
4. DoD names its **data source** for every check (seeded record, test account, backend dev seed) and marks
   each step agent-run or owner-run. Owner-run: anything needing a fresh or second account, a human
   factor (password, one-time code, camera), a paid third-party call (with a call budget), or an
   irreversible operation (account deletion).
5. Update the registry row in the same commit.

## 6. Routing gaps

Use `references/gap-routing.md`. Three kinds: **BUG** (backend violates its contract), **CONTRACT**
(contract lacks something the UI needs; classify additive/breaking per fe-to-backend-spec), **TOOLING**
(dev seeds, test accounts). Each gets a ticket with operation, observed vs wanted, evidence (probe
output), and the front-end ticket it blocks. If the front end must ship an interim, it lives inside the
operation body with a removal note tied to the backend ticket, never in a component.

## 7. Done

- Registry: zero MOCK outside EXCLUDED; every WIRED row has consumers; snapshot date current.
- `grep` for mock-storage imports in live operation bodies returns nothing.
- Every never-called backend path in scope has had a successful probe.
- Gap tickets filed for everything parked.
