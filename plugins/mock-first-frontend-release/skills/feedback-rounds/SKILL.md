---
name: feedback-rounds
description: 'Run the tester-and-designer feedback loop on a front end that is built on mocks (or partly live): ship preview builds or over-the-air updates to testers, collect feedback (tester notes, annotated screenshots/PDFs, designer mock files), triage it into a numbered round work list, implement and re-ship, and decide when the design is "settled" enough to derive the backend contract. Use it whenever the user says "send a build to testers", "ship a preview/TestFlight/internal build", "push an OTA", "here is feedback from testers/the designer", "design round", "design refresh", "apply this feedback", "work through these annotations", "is the design settled/frozen", or hands over screenshots, PDFs or mock files with change requests, even without the word "round". For building the mocked app itself use mock-first-app; for writing the backend contract once settled use fe-to-backend-spec.'
---

# Feedback rounds

Turn feedback into numbered, bounded rounds. Each round has a written work list, ships to the same
testers, and ends with a decision: another round, or design settled.

## 1. Ship

Pick the cheapest channel that carries the change (`references/distribution.md`):

- **JS/asset-only change** on a platform with OTA → publish an update to the preview channel.
- **Native change** (new native module, permission string, config plugin, SDK bump) → full preview build.
  Decide by comparing the native fingerprint (or equivalent) with the last tester build, not by guessing;
  keep a manual "force build" override for when the check is wrong.
- **Web** → a protected preview deploy per round.

Every tester build shows its version/build id and channel somewhere testers can read (settings footer),
so feedback can be pinned to a build. Tell testers what changed (round notes from the work list).

## 2. Collect

Accept any form: chat notes, screenshots, annotated PDFs, recorded sessions, designer mock files.
Before reading annotations as design:
- **Annotation ink is not design.** A reviewer's pen colour (often pure `#ff0000`) marks a change; it is
  not a new brand colour. Sample real design colours only from the rendered product or the designer's
  token file, and map to existing tokens before adding new ones.
- Designer mock bundles (exported HTML prototypes, Figma exports) may be packed; extract the real source
  or tokens instead of eyeballing pixels. Record the extraction recipe in the project docs once.
- A designer mock may contain much more than this round asks for; the round's scope is the work list,
  not the whole mock.

## 3. Triage into a round work list

Write `docs/design-rounds/round-N.md` from `references/round-template.md`. Each item gets:
id (`R{N}-{k}`), screen, source (who/which file/page), change, type, and decision.

Types:
| Type | Example | Effect on backend contract |
|---|---|---|
| visual | spacing, colour, copy, motion | none |
| flow | step order, new screen, removed step | may change operations |
| data | new field, new list, new filter | changes the contract: update the mock body + registry |
| behaviour | rule change (who can see what, limits) | changes the contract |
| bug | "card jumps back", crash, wrong count | none unless the cause is a contract gap; does not count against "settled" |

Keep bugs in their own section of the round file, with the suspected cause, so they are not mistaken for
design churn.

Decisions: DO this round, LATER (with round number), NO (with reason, recorded), ASK. Vague or ambiguous
feedback ("make it more fun") is never decided by you, neither guessed into a concrete change nor marked
NO: it is ASK, and goes into the round's single batched owner-questions list with a recommendation. Do not
start ASK items.

For every data/behaviour item, open the operations it touches (mock body, types, registry row) before
writing the item. Record what you find there as items too: registry drift (ops missing or stale), spec
comments the types do not match (a field the body stamps but the type lacks, paging promised but a bare
list returned), generic patch operations that let the client set server-owned fields, and id-kind mixes
in fixtures. These are cheap now and expensive after the backend is built.

## 4. Implement

- One branch per round (or per large item); merge when the round's items pass review.
- **data/behaviour items change the mock layer first**: operation body (the backend spec), types, fixtures,
  registry row. Then the UI.
- Removing UI "for now": comment out the entry point, keep the logic wired, note it in the round file.
- Re-ship (§1) and post round notes listing item ids.

## 5. Decide: another round or settled

Run `references/design-settled-checklist.md`. Settled means the contract is stable enough that a
backend built from it will not be rebuilt next month. Visual items may continue after settlement;
data/behaviour items after settlement go through the change process in `fe-to-backend-spec`
(additive vs breaking).

When settled: record it at the top of the registry (`Design settled: {date}, round N`) and move on to
`fe-to-backend-spec`.
