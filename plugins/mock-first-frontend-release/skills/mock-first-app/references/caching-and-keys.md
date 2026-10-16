# Caching and keys

## Keys module

```ts
export const queryKeys = {
  account: { me: () => ["account", "me"] as const },
  orders: {
    all: () => ["orders"] as const,
    list: (filter?: OrderFilter) => ["orders", "list", filter ?? {}] as const,
    detail: (id: OrderId) => ["orders", "detail", id] as const,
  },
} as const;
```
- Hierarchical so `invalidateQueries({ queryKey: queryKeys.orders.all() })` hits everything in a domain.
- Viewer-scoped data (anything whose answer depends on who asks) is keyed under the signed-in identity
  or cleared on identity change. Two accounts on one device must never see each other's cache.
- Dead keys are deleted with the hook that used them; keep the module greppable.

## Defaults

| Setting | Default | Note |
|---|---|---|
| staleTime | 30 s - 5 min per domain | lower than any signed-URL lifetime in the payload |
| gcTime | 24 h if persisted, else 5 min | |
| retry | 2 for network/timeout only | |
| refetchOnFocus/foreground | on for lists, off for heavy detail | |

## Persistence

Only if the product needs instant start or offline reads.

- Allowlist roots (e.g. lists and the newest N items of a thread), not the whole cache.
- Only `status === "success"` queries.
- `maxAge` (e.g. 7 days) and a **`CACHE_SCHEMA_VERSION`** constant as the buster.
- Bump the version when: a mapper output shape changes, an id kind changes, a mock body is replaced by
  a live body with a different shape. A stale persisted shape crashes screens at hydrate time, and only
  on devices that were already installed, so it slips past fresh-install testing.
- Sensitive content (messages, private media metadata) goes in encrypted storage with a device-only key,
  never in default plaintext/backed-up storage.
- Wipe on every sign-out path, after the sign-out call.

## Optimistic updates

For toggles and reorderings: patch, call, roll back on error, then re-read once. For creates that need a
server id: insert a temporary row keyed by a client id and replace it from the response.
