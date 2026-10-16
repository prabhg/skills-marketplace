# Web (React, Next.js, Vite)

Adapted from the React Native variant; not yet run end to end on a web project.

| Concern | Choice |
|---|---|
| Cache | TanStack Query; persist with `createSyncStoragePersister` (localStorage) only for non-sensitive roots |
| Mock storage | Two options: (a) operation bodies read/write IndexedDB/localStorage, same as native; (b) MSW (Mock Service Worker) intercepting the real transport |
| Internal-build gate | env flag set at build time (`VITE_INTERNAL=1`, `NEXT_PUBLIC_INTERNAL=1`); absent = false |
| Distribution | per-branch preview deploys (Vercel/Netlify/Amplify previews), password or allowlist protected |

Choosing (a) vs (b):
- (a) keeps the rule "mock body = backend spec" literal and works offline. Default.
- (b) exercises the real transport client and serializers early, but the backend logic then lives in MSW
  handlers: treat the handler as the operation's mock body, keep one handler per operation, and keep
  handlers in the same domain folder. Use (b) when the transport/schema is already fixed (e.g. an OpenAPI
  spec exists).

Next.js server components: keep operations callable from both server and client; the mock must not rely
on browser-only storage when called on the server (use an in-memory store seeded per request, or render
mocked screens as client components).
