# Writing the test plan

Audience: testers who are not engineers, on their own phones or browsers, printing or annotating a PDF. Every case must be doable from the plan alone.

## Gather

- The build under test: version, build number, channel, and where the app shows it (settings footer). The tag or commit it was built from.
- The screen map from the code at that commit (routes, screens, sheets, dev-only screens), in the order a new user meets them: launch → sign-up/sign-in → consent → onboarding → main tabs → each tab's sub-screens → settings → cross-cutting (links, notifications, accessibility, offline).
- What is real and what is still mocked or simulated in this build (from the project's API/mock registry), and what is deliberately not in the build.
- Dev shortcuts testers may use (e.g. skipping a third-party check, approving a pending state, a fake payment, switching plans), and where they are.
- Last cycle's register: VALID items fixed since, cases testers did not understand.

Use subagents to map screen groups in parallel from a worktree of the tested commit; each returns per screen: entry point, visible elements, actions, success result, error results, gated variants (e.g. a plan or role, an internal build).

## Structure

1. **Header**: title, build under test, how the build id reads in the app, backend environment, date.
2. **Before you start**: who is testing (blank line), install and update steps (e.g. relaunch to pick up an over-the-air update, or reload the preview URL), accounts needed (how many devices for 2-person cases; a plus-address tip for email), dev shortcuts, how to file a bug (case id, build footer block, device + OS, steps / expected / actual, screenshot or recording with time).
3. **Fixed in this build: please re-test**: case ids from last cycle.
4. **Not real yet**: features that only work on one device or are simulated; say what to ignore.
5. **Not in this build**: deliberate gaps, so they are not filed.
6. **Sections per area** with case ids `AREA-NN` (stable across cycles; new cases get new numbers, removed numbers are not reused). Each case: title, tags (P0, NEW, MOCK, KNOWN, accounts needed), numbered steps, one expected result written as what the tester sees (exact copy in quotes), then `Pass ☐ Fail ☐ Blocked ☐ N/A ☐` and a `Note:` line with room to write.

## Rules

- One expected result per case; split cases that test two things.
- Offline cases say exactly how to go offline (e.g. Airplane mode with Wi-Fi off, or the browser's offline mode) and what counts as "at once".
- Cases that need several accounts say how many and suggest pairing testers; cases needing more accounts than testers have are marked so testers can mark N/A.
- Never put real credentials, test phone numbers or codes in the plan.
- Accessibility (largest text sizes, reduce motion), slow network and notification taps get their own cases.
- Leave the physical layout printable: no case split across pages if avoidable, enough space under each Note line.

## Publish

Render as one self-contained HTML page (print styles: page breaks between sections, checkbox glyphs that print) and publish it **private**. The owner downloads it as PDF and sends it with the build invite. Keep the source HTML with the cycle docs so the next plan is an edit, not a rewrite.
