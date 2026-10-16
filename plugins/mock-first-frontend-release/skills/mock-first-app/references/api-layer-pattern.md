# API layer pattern (TypeScript example; native equivalents in platform-native-mobile.md)

## Folder shape

```
src/api/
  _shared/
    errors.ts          # ApiError taxonomy
    ids.ts             # branded id types
    simulate.ts        # mockLatency(), maybeInjectError(op)
  orders/
    types.ts           # domain types (what screens see)
    operations.ts      # one exported async function per backend op
    hooks.ts           # useOrdersQuery, useCreateOrderMutation …
    mappers.ts         # wire → domain (pure; tested when the live body lands)
    mock/
      storage.ts       # device-local tables for this domain
      seed.ts          # fixtures, seeded relative to the current identity
```

## Branded ids

```ts
export type AccountId = string & { readonly __kind: "AccountId" };
export type ProfileId = string & { readonly __kind: "ProfileId" };
```
Fixtures use visibly different prefixes (`acc_…`, `prf_…`). A function that takes a `ProfileId` cannot
be handed an `AccountId` without a cast, and a cast is a review flag.

## Error taxonomy

```ts
export type ApiErrorKind =
  | "network" | "timeout" | "unauthenticated" | "forbidden"
  | "validation" | "conflict" | "rate_limited" | "not_found" | "server";
export class ApiError extends Error {
  constructor(public kind: ApiErrorKind, public detail?: { field?: string; code?: string }) { super(kind); }
}
```
Screens branch on `kind` (and `detail.field` for inline validation). Retry policy: retry `network` and
`timeout`, never `validation`/`forbidden`/`conflict`.

## An operation: mock body now, live body later

```ts
// operations.ts
export async function submitOrder(input: SubmitOrderInput): Promise<Order> {
  // MOCK — this body is the backend spec for `submitOrder`:
  //  1. validate: cart not empty, address present           → validation{field}
  //  2. write Order(status=submitted), clear Cart
  //  3. derive Account.hasOpenOrder = true
  //  4. return the fresh Order
  await mockLatency();
  maybeInjectError("submitOrder");
  return mockSubmitOrder(input);       // from ./mock/storage
}
```

Live, the body becomes:

```ts
export async function submitOrder(input: SubmitOrderInput): Promise<Order> {
  const data = await transport.request(SubmitOrderDocument, toWire(input)); // throws ApiError
  return mapOrder(data.submitOrder);
}
```

Signature unchanged, hook unchanged, screen unchanged. The numbered comment moves into the backend spec
(fe-to-backend-spec) and is deleted from the code once live.

## Hooks

```ts
export function useSubmitOrderMutation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: submitOrder,
    onSuccess: (order) => {
      qc.setQueryData(queryKeys.orders.detail(order.id), order);
      qc.invalidateQueries({ queryKey: queryKeys.orders.list() });
      qc.setQueryData(queryKeys.account.me(), (me) => me && { ...me, hasOpenOrder: true });
    },
  });
}
```
Cache patches mirror the fan-out declared in the operation body. If the patch list grows long, the
operation should return the changed records instead.

## What never goes in a component

- two mutation calls for one tap
- `await a(); await b();` record sequencing
- computing a flag the backend owns (`stepCompleted`, `isUnlocked`)
- `refetch()` right after a mutation to "make sure"
- a mock import

## Swap checklist (used later by mock-to-live-integration)

1. Live body = transport call + unwrap + mapper; mapper unit test asserts each id field's kind.
2. Delete the op's mock code; delete any mock enrichment that joins device data onto a live read.
3. If the mapper's output shape changed, bump the persisted-cache version.
4. Update the registry row (status, consumers).
