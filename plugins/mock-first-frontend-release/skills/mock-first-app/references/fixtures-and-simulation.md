# Fixtures and simulation

## Fixtures

- Store fixtures as typed TS/JSON in `api/<domain>/mock/`, generated once from a fixed seed so every
  tester sees the same world. Commit them.
- `MOCK_SEED_VERSION`: bump when fixtures change; on mismatch the mock storage is wiped and re-seeded.
  Without it testers keep stale records and report bugs that do not exist.
- Use realistic volumes (a list of 3 hides pagination and empty-state bugs; seed 50-150 rows where the
  real product will have many).
- Id prefixes per kind (`acc_`, `prf_`, `ord_`). Never reuse one id value across two kinds.
- **Runtime-relative seeding:** rows that point at the signed-in user (requests received, shared items)
  cannot be static, because the user's id exists only after sign-in. The first read seeds them relative
  to the current identity and records that it did.
- Media: use local or bundled assets. A mock upload may keep the local file uri so picked media renders;
  note in the registry that such uris die when the OS purges caches.

## Simulation helpers

```ts
export async function mockLatency(min = 150, max = 600) { /* await random delay */ }
export function maybeInjectError(op: string) {
  const forced = devErrorSwitches.get(op);          // set from a dev menu
  if (forced) throw new ApiError(forced);
}
```
- A dev menu (internal builds only) lists operations and lets a tester force an error kind or extra
  latency per operation, and reset or re-seed mock data.
- Simulate time-based backend behaviour in the operation body (e.g. "approved 30 s after submit",
  "link expires after 5 min"). Write it as a numbered backend rule in the body comment.

## Where mocks lie (write these down as you go)

Mocks cannot show: authorization failures, rate limits, eventual consistency/projection lag, real
payload sizes, concurrent edits, cold starts, third-party behaviour. Record each such assumption in the
registry `notes` column; mock-to-live-integration probes them first.
