# Design settled checklist

All must hold. Any "no" means another round (or an explicit owner override, recorded).

- [ ] The last round had **no data or behaviour items** marked DO (only visual), or the last two rounds
      changed no operation signatures.
- [ ] Every launch feature is reachable on a tester build and every screen state works on mocks
      (loading, empty, error, success, offline).
- [ ] No open owner questions that touch data or behaviour.
- [ ] Every LATER item is either visual or explicitly post-launch (listed in the spec's launch scope).
- [ ] The mock registry is complete: every operation the UI calls has a row, consumers filled, id kinds
      declared, mock assumptions noted.
- [ ] Each mutation is one user intent; no component composes writes (grep check).
- [ ] Testers have used the current build for at least {one agreed period} without new data/behaviour asks.

After settling, data/behaviour changes are contract changes: classify additive vs breaking
(fe-to-backend-spec `references/contract-changes.md`) before doing them.
