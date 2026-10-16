# Probe protocol

A probe is one real call of one operation against the non-production backend, before the front-end
design for it is approved.

## Why
Mocks never exercise: auth claim shapes, permission rules, cold starts and timeouts between services,
projection lag, real payload shapes, id kinds, rate limits. Backends that have never been called fail
at a high rate on first call. Finding that during design costs one ticket; finding it after the UI is
built costs a redesign.

## How
1. Confirm the environment (resource tag/name says non-production).
2. Use a signed-in test session (token from the app's dev tools or a test harness). Never use or print a
   real user's credentials; never put tokens in files that get committed.
3. Call with the contract's example input. Record: request, status, response (redacted), latency,
   cold vs warm (call twice).
4. Compare the response with the front-end domain type field by field, including **id kinds** and
   nullability.
5. Order: free reads first, then idempotent writes, then non-idempotent writes, then paid or
   rate-limited calls within a stated budget. Irreversible calls are owner-run.

## Outcome
| Result | Action |
|---|---|
| matches contract | design proceeds |
| contract violated | BUG ticket to backend; front-end ticket parks |
| contract lacks a need | CONTRACT ticket (additive/breaking) |
| needs data that does not exist | TOOLING ticket (dev seed / test account) or owner-run step |
| slow cold start / timeout | backend ticket; check caller timeouts cover callee cold starts |

## Lagging projections
If a write is visible only after an async projection, the operation re-reads until visible (bounded:
e.g. up to 7 reads, waits growing 0.5 s, 1 s, 1.5 s …) and returns the last read either way. Document the
lag in the contract.
