# Operation inventory

> Derived from the front-end mock layer on {date} at commit {sha}. Source of truth for the backend
> contract. Regenerate (not hand-edit) when the mock layer changes.

## Identity kinds

| Kind | Example | Issued by | Visible to other users? |
|---|---|---|---|
| AccountId | acc_… | auth provider / account service | no |
| ProfileId | prf_… | profile service | yes |

## Operations

### {domain}.{operation} ({Q|M|S})

- **Input:** `{ field: type (kind) … }`
- **Output:** `{Type}`; id fields: `id (OrderId)`, `buyerProfileId (ProfileId)`
- **Caller / auth:** signed-in; caller must own the order (`order.buyerAccountId = token.accountId`)
- **Records written:** Order(create), Cart(clear)
- **Derived fields:** Account.hasOpenOrder = true
- **Side effects:** event `ORDER_SUBMITTED`; notify seller
- **Errors:** validation{cart, address}, conflict (cart changed), rate_limited
- **Consumers:** checkout-screen
- **Mock assumptions to verify live:** {from registry notes}
- **Launch scope:** BUILD

(repeat per operation)

## Components writing outside an operation (fix before spec)

| File | What it does | Fix |
|---|---|---|
