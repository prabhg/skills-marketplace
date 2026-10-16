# React Native / Expo

Proven variant (the method was first run here).

| Concern | Choice |
|---|---|
| Cache | TanStack Query; `@tanstack/query-async-storage-persister` or a custom persister |
| Mock storage | MMKV (fast, sync) namespaced per user: `key(userId, "orders")`; one `wipeUserKeys()` on sign-out |
| Sensitive persisted cache | separate encrypted MMKV instance; key in SecureStore, device-only accessibility |
| Internal-build gate | `__DEV__ || isSimulator || buildVariant !== "production"`, unknown variant = false |
| Transport later | GraphQL: codegen from a committed schema snapshot; REST: openapi-typescript client |
| Distribution | dev client for engineers; preview builds + OTA for testers (see feedback-rounds) |

Notes:
- Native modules you add for a mocked feature (camera, picker, compressor) change the native
  fingerprint and force a new build for testers; JS-only mock work ships by OTA. Batch native additions.
- Lazy-`require` optional native modules so stale dev clients and Expo Go do not crash on import;
  degrade the feature instead.
- Keep device mock storage keys in one module so the sign-out wipe and the later mock cleanup can find
  them all.
- Media mocks: keep the local compressed file uri (or a small base64 thumbnail) as the item url so the UI
  renders real picks.
