# Register template

```markdown
> Purpose: register of the <date> QA feedback (<n> testers, build <version>) + owner items, with validation class per item
> Use: reviewer + owner, to send questions back, rule product requests and plan fixes
> Delete when: every row is fixed, closed as invalid, or moved to the issue tracker

# QA feedback register, <date>

Sources: <files>. Not filled in by testers: <name / build id / device / OS>.
Build under test: <version> (<tag> = <commit>, <date>). Newer builds since: <list>.

## Bugs and failures

| Id | Tester | Case | Verbatim | Shot | Area | Class |
|---|---|---|---|---|---|---|
| F-01 | A, B | AUTH-03 | A: "…" · B: "…" | screenshot_1 | auth | VALID: <one-line cause> (wave) |

## Test-plan clarity (fix the next plan, no app work)

| Id | Tester | Case | Verbatim |

## Product requests (owner rules first; nothing planned until ruled)

| Id | Tester | Case | Verbatim |

## Owner items

| Id | Verbatim |
```

Verbatim means verbatim: keep the tester's spelling, mark `[illegible]` and `[?guess]`. When two testers disagree on the mark (one Pass, one Fail), keep both in the row.
