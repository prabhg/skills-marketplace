# mock-first-frontend-release

Build the front end first, on a mocked API layer that behaves like the real backend, ship it to testers,
settle the design, then build the backend from the contract the front end proved, and integrate it
wave by wave.

```bash
claude plugin install mock-first-frontend-release@prabhg-plugins
```

```
mock-first-app ──► feedback-rounds ──► fe-to-backend-spec ──► (backend build) ──► mock-to-live-integration
   (phase 1)          (phase 2, loop)       (phase 3)          process-prd-to-tech-spec      (phase 4)

qa-loop: test plan → tester PDFs → extract → validate → questions → fix plan → release → next plan
         (any phase once testers run preview builds)
```

| Skill | Use when |
|---|---|
| `mock-first-app` | Starting an app (or a feature) before its backend exists; setting up the API layer, fixtures, cache, mock registry |
| `feedback-rounds` | Shipping preview builds to testers, running design rounds, deciding the design is settled |
| `fe-to-backend-spec` | Turning the settled mock layer into the backend contract and a PRD for `process-prd-to-tech-spec` |
| `mock-to-live-integration` | A backend exists (partly or fully) and mocks must be replaced by live calls |
| `qa-loop` | Writing the per-screen test plan for testers, then extracting, validating and planning their filled-in feedback, and writing the next plan |

One artifact runs through all four phases: the **mock registry** (`docs/api/MOCK_REGISTRY.md` by default), a
table of every operation with its status. Phase 1 creates it, phase 3 reads it as the op inventory,
phase 4 drives it to zero mocks.

The method in one line: **the mock fetcher body is the backend spec.**
