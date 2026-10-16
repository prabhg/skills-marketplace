# Distribution channels

| Platform | Tester channel | JS-only change | Native change |
|---|---|---|---|
| React Native / Expo | EAS build `preview` profile → TestFlight / internal track | `eas update` to the preview channel (runtime version must match) | new preview build |
| Web | protected preview deploy | redeploy | n/a |
| Native iOS | TestFlight internal/external group | n/a (every change is a build) | build |
| Native Android | Play internal testing / Firebase App Distribution | n/a | build |

Rules:
- **Build vs OTA by fingerprint.** Compute the native fingerprint (Expo: `@expo/fingerprint`) of the
  candidate commit and compare with the tester build's. Match → OTA; mismatch → build. Keep a force-build
  override (label, commit marker or dispatch input) for when the check is wrong.
- The built commit must equal the tagged/recorded commit, so feedback maps to source.
- Automate the release path (CI workflow) once you ship more than ~1 round a week; until then a written
  runbook in the repo.
- Show build id + channel in the app (settings footer). Testers quote it in feedback.
- Testers sign in to mock accounts that the mock layer creates on first sign-in; if the auth provider is
  real already, give testers their own accounts (never shared credentials in chat).
