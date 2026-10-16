# Native iOS (Swift) / Android (Kotlin)

Concept map only; untested. Confirm library choices against the project before using.

| Concept | Swift | Kotlin |
|---|---|---|
| Operation interface | `protocol OrdersAPI { func submitOrder(_:) async throws -> Order }` | `interface OrdersApi { suspend fun submitOrder(...): Order }` |
| Mock / live bodies | `MockOrdersAPI`, `LiveOrdersAPI` conforming to the protocol | `MockOrdersApi`, `LiveOrdersApi` implementing the interface |
| Selection | per-domain, in the DI container / environment (`@Environment` or a factory) | Hilt/Koin module per domain |
| Cache + keys | an observable repository layer keyed by a `CacheKey` enum; or SwiftData/Core Data as the read cache | Repository + Room as the read cache; Flow for observation; or Store5 |
| Error taxonomy | `enum APIError: Error { case network, timeout, … }` | `sealed class ApiError` |
| Branded ids | `struct ProfileID: Hashable { let raw: String }` | `@JvmInline value class ProfileId(val raw: String)` |
| Mock storage | files/UserDefaults/SwiftData seeded from bundled JSON | DataStore/Room seeded from assets JSON |
| Internal gate | `#if DEBUG` or a build-configuration flag; release = false | `BuildConfig.DEBUG` or a flavor flag |
| Distribution | TestFlight internal/external groups | Play internal testing / Firebase App Distribution |

Differences from the JS variants: per-operation swap is per-domain implementation (whole protocol)
unless you split protocols finely; prefer one protocol per domain and track op status in the registry.
No OTA for native code, so every tester change is a build: batch rounds accordingly.
