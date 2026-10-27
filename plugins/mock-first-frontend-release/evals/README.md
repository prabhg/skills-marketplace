# Evals

Six skill-creator evals (`evals.json`) on three throwaway sample apps (`fixtures/`), each with planted
defects the skills should catch (mixed id kinds, stale registry, multi-write screens, mock data overwriting
live reads, never-called backend functions, annotation ink in feedback). `qa-loop` has no evals yet.

Re-run after real use, or after editing a skill: ask Claude to "run the skill-creator evals in
plugins/mock-first-frontend-release/evals" (with-skill vs no-skill runs, graded against each eval's
assertions). Copy a fixture into a scratch folder per run; never edit fixtures in place.

Last results (2026-10-16): iteration 1 96% vs 67% without the skill; iteration 2 (after edits, + eval 6) 98% vs 66%.
