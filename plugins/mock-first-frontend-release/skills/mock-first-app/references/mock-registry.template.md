# Mock registry

> Every API operation the front end knows, and how real it is. Updated in the same commit as any
> operation change. Read by fe-to-backend-spec (op inventory) and mock-to-live-integration (progress).

Last reconciled: {YYYY-MM-DD} against {backend schema snapshot / "no backend yet"}

## Summary

| Status | Count |
|---|---|
| MOCK | 0 |
| WIRED | 0 |
| WIRED-NO-CONSUMER | 0 |
| UNWIRED | 0 |
| DEV-ONLY | 0 |
| EXCLUDED | 0 |

## Operations

| Domain | Operation | Kind | Status | Consumers | Id fields (kind) | Mock assumptions / notes |
|---|---|---|---|---|---|---|
| orders | getOrders | Q | MOCK | orders-screen, home-badge | id (OrderId), buyerId (AccountId) | 50 seeded rows; no pagination limit simulated |
| orders | submitOrder | M | MOCK | checkout-screen | id (OrderId) | fan-out: clears cart, sets account.hasOpenOrder |
| account | devApproveAccount | M | DEV-ONLY | dev menu | | stands in for staff review |

Kind: Q query, M mutation, S subscription/event. Consumers: screens/components that call the hook
(grep). Status definitions: mock-first-app SKILL.md §5.

## Excluded (kept mock on purpose)

| Operation | Why | Decided by / date |
|---|---|---|
