---
name: mock-first-app
description: 'Build a fully working front end (web, React Native/Expo, or native iOS/Android) on a typed, per-operation mock API layer before any backend exists, so testers can use it and each mock later swaps for a live call without touching screens. Sets up: per-operation mock/live bodies, one-intent mutations whose mock body is the backend spec, a query cache (TanStack Query or platform equivalent) with central keys and a persist version, seeded fixtures with distinct id kinds, latency/error simulation, fail-closed dev shortcuts, and a mock registry of every operation. Use it whenever the user says "build the front end first", "mock the API", "frontend-only prototype/POC", "we have no backend yet", "fake the backend", "mock-first", "set up the API layer", "add a mocked feature", or starts a new app or feature whose backend does not exist or is not ready, even if they never say "mock". For replacing mocks with a real backend use mock-to-live-integration; for deriving the backend spec use fe-to-backend-spec.'
---

# Mock-first app

Build the product's real front end against a mock backend that is shaped exactly like the backend you
will build later. Testers use it as if it were live. When the backend lands, each operation swaps its
body; screens, hooks and cache keys stay.

The method stands on one rule: **the mock body of an operation is the specification of its backend
resolver.** Everything below exists to keep that true.

## 0. Before writing code

1. Find the project's own rules (agent docs, CLAUDE.md, coding standards). They win over this skill.
2. Pick the platform reference and read it:
   - React Native / Expo: `references/platform-react-native.md`
   - Web (React, Next.js, Vite): `references/platform-web.md`
   - Native iOS / Android: `references/platform-native-mobile.md`
3. Read `references/api-layer-pattern.md` (always) and `references/fixtures-and-simulation.md` (before
   writing the first fixture).
4. Decide the transport you expect later (GraphQL, REST, RPC). Name operations in that style now
   (`getThing`, `createThing` or `GET /things`), but do not build the transport client yet.

## 1. Layer shape

```
screen / component
  └─ hook (useThingQuery / useCreateThingMutation)   ← cache keys, optimistic updates, invalidation
       └─ operation (fetcher)                         ← ONE function per backend op; mock OR live body
            ├─ mock body: device storage + fixtures + simulated latency/errors
            └─ live body: transport call + unwrap + pure mapper
```

Rules, each with its reason:

- **One user intent, one mutation.** A component calls exactly one mutation per user action
  ("submit application", "complete step 3"). It never composes writes, sequences records, computes
  derived/denormalized flags, or refetches to reconcile. The operation body does all fan-out and returns
  the fresh authoritative state. *Why:* the backend will do this fan-out in one resolver; if a component
  does it, the backend spec is split across UI files and the swap breaks call sites.
- **Operations are per-domain modules** (`api/<domain>/operations.ts`, `hooks.ts`, `mappers.ts`,
  `mock/`). Mock-only code lives under `mock/` and is imported only by operation bodies. *Why:* when an
  op goes live, deleting its mock folder must not break anything else.
- **Typed domain models, separate from wire types.** Screens see domain types only. The live body maps
  wire → domain through a pure mapper. *Why:* the backend's names will differ; the mapper absorbs it.
- **The transport result never throws into screens.** Live bodies return or throw a typed error from a
  small taxonomy (network, timeout, unauthenticated, forbidden, validation{field}, conflict, rate_limited,
  not_found, server). The mock throws the same taxonomy. Timeout is retried like network.
- **Identity kinds are explicit.** If the product has more than one identifier for a person or thing
  (account id vs public profile id, internal id vs share code), give each its own branded type and its
  own fixture prefix. *Why:* mixing them is the most common contract break at integration and mocks hide
  it, because a mock happily looks up any string.

## 2. Cache from day one

Read `references/caching-and-keys.md`. Summary:

- All query keys come from one keys module (`queryKeys.thing.detail(id)`); no inline arrays.
- Mutations update the cache from the returned authoritative state (or optimistic patch + rollback);
  they do not refetch-after-mutate as a default.
- If you persist the cache, persist an allowlist of roots, only successful queries, with a max age and a
  **schema version constant**. Bump the version whenever a mapper's output shape changes. Wipe the
  persisted cache on sign-out.
- Short-lived URLs (signed media links) must not outlive their expiry in cache: set `staleTime` below the
  link lifetime or refetch on expiry.

## 3. Fixtures and simulation

Read `references/fixtures-and-simulation.md`. Summary:

- Deterministic seeded fixtures, versioned with a `MOCK_SEED_VERSION` so a fixture change re-seeds
  devices.
- Rows that reference "the current user" cannot be static JSON (the user's id exists only at runtime):
  seed them on first read, relative to the signed-in identity.
- Simulated latency (default 150-600 ms jitter) and an error-injection switch per operation, so loading
  and error states are built now, not discovered at integration.
- Time-based server behaviour (approval after review, expiry) is simulated inside the operation body,
  and documented there as backend behaviour.

## 4. Dev-only shortcuts

Third-party or human steps the tester cannot do (identity check, staff review, payment) get a dev
operation (`devApproveApplication`, `devSetTier`) that the backend will also expose on non-production
environments only. Reach them only from an internal-build gate that **fails closed** (unknown build
variant = not internal). When a shortcut's effect reaches the read model through a lagging projection,
re-read until the change is visible (bounded retries with growing waits) instead of returning stale
state.

## 5. Mock registry

Create `docs/api/MOCK_REGISTRY.md` from `references/mock-registry.template.md` (or the path the project
prefers) in the same change as the first operation, and update it in the same commit as every new or
changed operation. One row per operation: domain, kind, status, consumers, id kinds, notes. Status values:

| Status | Meaning |
|---|---|
| MOCK | body uses device storage/fixtures |
| WIRED | live body; at least one UI consumer |
| WIRED-NO-CONSUMER | live body exists, nothing in the UI calls it (do not count as integrated) |
| UNWIRED | backend op exists, no front-end operation yet |
| DEV-ONLY | shortcut op, internal builds only |
| EXCLUDED | deliberately kept mock (with reason and owner ruling) |

*Why the consumer column:* "N operations wired" overstates integration whenever a hook exists but no
screen calls it.

Optional: a lint script that lists operations whose body still imports from `mock/` and diffs that
against the registry. Add it when the registry passes ~30 rows.

## 6. Feature flags

Use flags to hide unfinished features from testers, not to switch mock vs live (that switch is per
operation, in code). Keep a hidden feature's logic wired; comment out the entry point.

## 7. Definition of done for a mocked feature

- Every screen state works on mocks: loading, empty, error (inject it), success, offline.
- Each mutation is one intent; its mock body documents every record it writes and every derived field.
- Domain types, mapper stub and registry row exist.
- No mock import outside `api/<domain>/mock/`.
- Testers can reach it on a preview build (see `feedback-rounds`).
- Mutations are safe to retry (a repeat after a timeout returns the current state, not an error), and
  their cache update patches the affected keys instead of invalidating everything.
- Limits or rules you had to invent (max counts, allowed date ranges) are marked `ASSUMED` in the body and
  listed as owner questions, not presented as product decisions.
- Pure logic the backend will copy (streaks, date rules, derived counts) has at least a quick test run,
  even when the app itself cannot be run.

## 8. Adding to an existing mock layer

Before adding a feature, reconcile the layer it lands in and **report** what will hurt at integration.
Fix only what the feature's own path needs (its registry rows, a broken helper it calls) or what the user
asked to fix; when the user only asks what will bite, answer with the list and leave other screens and
operation signatures alone, because those changes need their own review. Look for:
- registry rows missing, stale, or listing consumers that do not exist (fix the registry in the same change);
- components that compose several writes or compute server-owned flags (one-intent rule, §1);
- generic patch operations that accept fields the server should own (owner, membership, status flags);
- spec comments the types do not match (stamped fields missing from the type, paging promised but a
  bare list returned);
- fixtures that put one id kind where another belongs;
- refetch-after-mutate or blanket cache invalidation;
- simulation helpers that do not work on the platform (e.g. CommonJS `require` in an ESM bundle).
Bump the persisted-cache version when the feature changes a domain type's shape.

## Next

Ship to testers with `feedback-rounds`. When the design is settled, run `fe-to-backend-spec`.
