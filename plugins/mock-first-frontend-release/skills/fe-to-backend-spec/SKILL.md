---
name: fe-to-backend-spec
description: 'Derive the backend contract from a front end that already works on a mocked API layer: inventory every operation from the mock layer and registry, then write the backend contract (GraphQL SDL or OpenAPI, events/realtime topics, permissions per operation, data model with explicit id kinds, derived fields and fan-out per mutation, error codes, per-feature launch scope) plus a PRD that the process-prd-to-tech-spec skill turns into the engineering spec. Use it whenever the user says "spec the backend from the frontend", "what backend do we need", "turn the mocks into an API spec", "generate the schema/OpenAPI from the app", "backend contract", "design settled, start the backend", "write the PRD for the backend", or wants to start backend work on a mock-first app, even if they do not name the mock layer. Also use it for contract changes after the design is settled (additive vs breaking). Not for wiring a built backend into the app: that is mock-to-live-integration.'
---

# Front end to backend spec

The settled mock layer already contains the backend: each mock operation body lists the records it
writes, the fields it derives and the rules it enforces. This skill extracts that into a contract the
backend team (or agents) can build without reading front-end code, and hands a PRD to
`process-prd-to-tech-spec` for architecture.

## Inputs

- The mock registry (from `mock-first-app`); if missing, build it first (§1 does the same scan).
- The operation modules and their mock bodies; domain types; fixtures.
- Round files and owner rulings (what is launch scope, what is later).
- Platform constraints already decided (auth provider, transport style, hosting) if any.

## 1. Op inventory

Produce `docs/api/OP_INVENTORY.md` from `references/op-inventory.template.md`. For every operation:
name, kind, input, output, **records written**, **derived fields** it sets, side effects (notifications,
events, emails), authorization rule (who may call, on whose data), error kinds, consumers, launch scope.

How: read each operation body; the numbered comment is the source. Where a body lacks one, derive it
from the mock storage writes and ask the owner about anything inferred. Grep components for writes the
body does not own (a component composing two mutations, computing a flag). For each hit, name the single
intent operation that replaces the whole sequence (e.g. one setup call taking every input the wizard
collects), put it in the contract, and list the front-end change in the fix list. Fixing only the derived
flag still leaves a half-done state when a later call in the sequence fails.

Cross-check the inventory against the UI: an operation with zero consumers is either dead (delete) or a
planned feature (mark the launch scope, do not spec it as launch).

Inventory from the code, not only the registry: registries drift, so list every exported operation and
note rows the registry lacks. Where a spec comment and the types disagree (a field stamped but not in the
type, paging promised but a bare list returned), the contract records the intended behaviour and the
front-end fix goes in the inventory's fix list.

## 2. Identity and data model

Read `references/identity-and-ids.md`. Before any schema:
- List every identifier kind (account/auth id, public profile id, share/display code, resource ids).
- For every field that holds an id, write its kind. Name fields after the kind (`ownerProfileId`, not
  `ownerId`/`userId`). Ambiguous names were the largest source of integration breakage.
- Decide per operation which identity the caller supplies and which the server derives from the token.
  The client never sends its own account id as an argument for "me" operations.
- Viewer-scoped reads (answers depend on who asks: access status, "is mine", counts visible to viewer)
  take the viewer from the token, and the spec says so.

Then the data model: entities, owner service/table, keys, indexes for each list the UI shows (with sort
and page size), retention, and which fields are denormalized for reads (and who maintains them).

## 3. Contract

Write `docs/api/CONTRACT.graphql` (SDL) or `docs/api/openapi.yaml` from `references/contract-spec.template.md`:
- Operations named as in the front end where possible (renames cost a mapper line each; fine, but list them).
- Input validation rules (lengths, ranges, enums) copied from the mock body and forms.
- Error codes = the front end's error taxonomy, with field names for validation.
- Pagination shape per list.
- Events/realtime: for each push the UI expects (new message, badge counts, status change), the topic,
  payload, who may subscribe, and whether there is replay (if not, the client refetches on reconnect).
- Media: upload flow (presign → put → register → poll status), size/duration limits, URL lifetime.
- Dev-only operations (stand-ins for review/verification/payment) marked non-production.

## 4. Launch scope per feature

Table of features × BUILD / LATER / EXCLUDED (kept mock, with reason). An UNWIRED operation the backend
team offers but no UI uses is LATER, not launch. Batch every scope question to the owner in one list.

## 5. PRD for process-prd-to-tech-spec

The backend gets **its own PRD**, separate from the product PRD: write it with `references/prd-handoff.md`
(headings match that skill's PRD template) at `docs/backend/PRD.md` (or the folder the project keeps
feature PRDs in). Link the contract and inventory from it; do not paste them. Add one line to the main
product PRD under its scope or dependencies, linking the backend PRD; if no main PRD exists, say so and
do not create one. Then tell the user to run `process-prd-to-tech-spec` with that path (it searches the
current folder, `.misc/features/*/` and `docs/` only, so give the path or run it from `docs/backend/`).

## 6. Contract changes after this point

Every later change is classified with `references/contract-changes.md` (additive vs breaking) and
recorded in the contract's changelog. Front-end feedback rounds keep going; data/behaviour items now
go through this classification first.

## Output checklist

- [ ] OP_INVENTORY.md complete; every registry row present
- [ ] every id field has a kind; no bare `id`/`userId` ambiguity on cross-entity references
- [ ] CONTRACT (SDL/OpenAPI) with errors, pagination, auth rule per op
- [ ] events/realtime table
- [ ] launch scope table; owner questions batched
- [ ] PRD written; user told to run process-prd-to-tech-spec
