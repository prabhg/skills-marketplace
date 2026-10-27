---
name: qa-loop
description: 'Run the QA loop on an app testers use from preview builds, where feedback comes back against a test plan (case ids, Pass/Fail marks, notes): write the per-screen test plan testers follow (a private page they print or save as PDF), extract their filled-in feedback (handwritten or typed PDF annotations, screenshots, chat notes), validate each item against the code and a simulator, emulator or browser, send plain-language questions back, plan the accepted fixes in reviewed waves, and write the next test plan after release. Use it whenever the user says "write a test plan / test cases for QA", "testers filled in the test plan", "here is QA feedback", "review the tester PDFs", "validate the test-plan results", "what should we send back to the testers", "summarize the feedback for my review meeting", "plan the QA fixes", "next test plan", or hands over annotated test-plan PDFs, even without the word QA. For design rounds on a mocked front end use feedback-rounds.'
---

# QA loop

One cycle: **test plan → tester feedback → extract → validate → questions back → fix plan → implement → release → next test plan.** Each cycle is named (`QA-<date>`) and leaves three docs: the register, the tester questions and the fix plan. The test plan of cycle N+1 is written from cycle N's outcome.

Roles: by default you (the reviewer session) plan and do not implement; implementation runs in a separate implementer session or orchestrator from the approved plan, unless the owner asks you to implement. Agents never create accounts, type credentials or type verification codes: anything that needs a signed-in account is the owner's step.

## 1. Test plan

Follow `references/test-plan.md`. In short: per screen in the order a new user meets them, each case with an id (`AREA-NN`), steps, one expected result, and Pass / Fail / Blocked / N/A boxes plus a note line. Front matter: build under test and how testers read the build id in the app, accounts needed, dev shortcuts, how to file a bug, "Fixed in this build: re-test", "Not real yet" and "Not in this build". Publish it as a **private** page (an HTML artifact); the owner saves it as PDF and sends it. Never fill in tester credentials or test codes yourself.

## 2. Extract

Testers write on the PDF (pen, pencil, typed text boxes) and may send screenshots labelled with case ids.

- Find the plan the feedback was written on (often the PDF itself; `pdftotext` returns nothing for a printed page, so render pages: `pdftoppm -r 110 -png`).
- Split pages across extraction subagents (strong vision model; handwriting needs it), one tester and ~25 pages each. Each returns a table: case id, title, printed expected result, mark (Pass/Fail/Blocked/N/A/blank/unclear), note **verbatim** with `[illegible]` / `[?word]`, page. Free-form marks and screenshot references separately. Tell them to zoom (crop + upscale) instead of guessing.
- Pair screenshots with cases from the label drawn on them. Do not copy personal data visible in screenshots (emails, phone numbers, codes) into any doc. Rendered pages and copies of screenshots stay in scratch space, are never published, and are deleted at the end of the cycle.
- Record what the testers did not fill in (name, build id, device, OS); it becomes a question.
- Write the **register** (`references/register-template.md`): one row per distinct issue, merged across testers, stable ids `F-nn`; product requests `P-nn`; test-plan clarity `T-nn`; owner items `O-nn`; anything the owner relays verbally becomes a row with its source. Positive notes and plain passes are not rows.

## 3. Validate

Before classifying, pin the build: find the tag/commit the testers ran and list what changed since on the integration branch. Validate against the code that will ship (the integration branch head), and say per item whether it changed since the tested build.

Group items by area (e.g. errors/offline, navigation/links, sign-in, media, the rest) and send one validation subagent per group (mid-tier model for simple areas, strongest for root-cause hunts). Each brief: the register, the test-plan expectations, repo rules, read-only, and the classes:

| Class | Meaning | Next |
|---|---|---|
| VALID | reproduced, or the code clearly does what the tester describes / contradicts the expected result | fix plan |
| INVALID | works as designed; cite code or doc | tell the tester why |
| ASK | note missing, ambiguous, or code shows no path to it | exact plain-language question |
| CONFIG | not app code (dashboard, store, certificate, account setup) | owner action |
| DUPLICATE | same as another row or an open issue | link it |
| DECIDE | product request, not a bug | owner rules; plan nothing until ruled |

Rules that keep validation honest:
- **Fail with no note is ASK**, not VALID, unless the code proves it anyway.
- **Look for one root cause behind a cluster** (e.g. every offline case "slow or no error"): test one hypothesis with one agent before nine agents re-derive it.
- **Read the installed dependency version**, not memory, for library behaviour (auth SDK retries, router semantics).
- **A case listed "fixed in this build" that comes back Fail** is the highest priority: the fix did not work.
- **Mock-era behaviour**: if the tested build still mocked a feature, failures that the mock caused are INVALID for that build; say what changes in the next build, and add a T-row so the next plan lists it under "Not real yet" or re-tests it.
- **Repro on a simulator, emulator or browser** where it is possible without credentials (layout, large text, unauthenticated screens). Never take over a device or dev-server port another session is using. Signed-in repros wait for the owner to sign in; do not block the cycle on them.

## 4. Questions back

`references/questions-template.md`: grouped per tester, plain language, no internal ids in the sentences (ids in brackets for you), one question per unclear item, plus "answers we already have" for INVALID items so testers learn without replying. Ask every tester for build id, device and OS when missing.

## 5. Owner review page

Right after validation (before or alongside the fix plan), give the owner two temporary files for their review meeting, per `references/review-page.md`:

- **Review page**: one self-contained HTML file (no external scripts, light and dark theme, screenshots inlined) in a local, untracked place: at a glance (counts, top issues), what worked well (cases passed, by area, from the testers' marks), issues by area (id, tester, verbatim quote, verdict, one-line "what we'll do", screenshot), decisions the owner must make, questions going to the testers, test-plan fixes. Generate it from the register and the extracts with a small script, so it can be regenerated when answers come back.
- **Chat-ready questions**: the tester questions as plain text for a chat app (no tables or markdown headings; short numbered lines; grouped per tester with @name placeholders; friendly; the "answers we already have" list at the end). Paste it in your reply too.

Both are temporary: delete them after the meeting and once the answers are in the register.

## 6. Fix plan

For every VALID item and owner feature: root cause (`file:line` at the commit you name), approach, files, tests, risk, effort, whether it needs a native build or only an OTA/web deploy, and backend work. Backend gaps become **contract asks** (repo, operation, input, guard, result) routed to whoever owns that backend. Group into waves: no-code steps first (owner: config, product rulings; you: the next test plan's fixes), then independent small fixes in parallel (disjoint files; one writer at a time for shared files such as locale files), then larger items, then contract asks. Cut anything speculative.

Get an **independent review** from the strongest model at high effort (give it the plan, the register, the validation notes and the code; ask for APPROVE or CHANGES with evidence). Apply CHANGES and re-review until APPROVE.

## 7. Hand off

Send the owner (or the coordinating session) counts per class, the three doc paths and the two review files from §5. The owner sends the questions and starts the implementer. When answers come back, update the register (ASK → VALID / INVALID / DECIDE) and the plan, and re-review only what changed.

## 8. Release and the next plan

After the fixes ship in a preview build or OTA: write the next test plan from this cycle: re-test every VALID item ("Fixed in this build: re-test", with the case ids), rewrite cases testers did not understand, remove or reword cases that tested mock-era behaviour, add cases for new features, and keep the build id instructions. Then the loop starts again.

## Files

Keep cycle docs in the project's planning location if it has one, else `docs/qa/QA-<date>/`; each is marked temporary with a delete-when condition: the register and plan close when every row is fixed, closed or moved to the issue tracker.
