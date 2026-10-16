# PRD for the backend (input to process-prd-to-tech-spec)

Headings match that skill's PRD template. This is the backend's own PRD: write it at `docs/backend/PRD.md`
and add a link line to the main product PRD (e.g. `- Backend: see [backend PRD](backend/PRD.md)`).

```markdown
# {Product} backend — Product Requirements

> Derived from the settled front end (mock layer at commit {sha}, design settled {date}, round {N}).
> Contract: docs/api/CONTRACT.{graphql|openapi.yaml}. Inventory: docs/api/OP_INVENTORY.md.

## What this is
The backend that replaces the front end's mock layer: {N} operations across {domains}, {events}, media.

## Why it exists (problem / opportunity)
Testers use a complete front end on mocks; launch needs real data, auth, permissions and persistence.

## Who's the user / who benefits
{End users of the app; the front-end team integrating it; ops/staff tools if any.}

## Scope
- Every operation marked BUILD in the inventory's launch scope (list by domain with counts)
- Events/realtime topics in the contract
- Media pipeline: {flows and limits}
- Dev-only operations for non-production environments: {list}

## Non-goals (explicitly NOT building this round)
- Operations marked LATER / EXCLUDED, with reasons

## Success criteria
- [ ] Every BUILD operation passes a live probe from the front end with the contract's input/output
- [ ] Mock registry shows zero MOCK rows outside EXCLUDED
- [ ] Every id field carries the kind the contract declares (mapper tests green)
- [ ] {latency / scale targets from the owner}

## Milestones
| Milestone | Target date | Owner | Notes |
|---|---|---|---|
| Contract frozen | | | |
| Backend dev env deployed | | | |
| Integration waves done (mock-to-live-integration) | | | |

## External dependencies
- {identity provider, payment, verification vendor, push credentials, app review — with lead times}

## Open questions for stakeholders
- [ ] {batched owner questions from launch scope}

## Answered questions
| Date | Question | Answer |
|---|---|---|
```
