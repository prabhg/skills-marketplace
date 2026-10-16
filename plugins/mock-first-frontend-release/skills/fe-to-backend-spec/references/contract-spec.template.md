# Contract skeleton

Pick one transport. Keep the per-operation facts from OP_INVENTORY.md as doc comments.

## GraphQL (SDL)

```graphql
"""Order placed by the caller. Auth: signed-in; caller owns the cart."""
type Mutation {
  submitOrder(input: SubmitOrderInput!): Order!
}

type Order {
  id: ID!               # OrderId
  buyerProfileId: ID!   # ProfileId (public)
  status: OrderStatus!
  deliveryWindow: TimeWindow
}

"""Error extensions.code is one of: VALIDATION, CONFLICT, FORBIDDEN, NOT_FOUND, RATE_LIMITED, UNAUTHENTICATED; VALIDATION carries extensions.field."""
```

Lists: `type OrderPage { items: [Order!]!, nextCursor: String }`.

## OpenAPI

```yaml
paths:
  /orders:
    post:
      operationId: submitOrder
      security: [{ bearer: [] }]
      requestBody: { $ref: '#/components/requestBodies/SubmitOrder' }
      responses:
        '200': { $ref: '#/components/responses/Order' }
        '422': { $ref: '#/components/responses/ValidationError' }   # { code, field }
        '409': { $ref: '#/components/responses/Conflict' }
```

## Events / realtime

| Topic | Payload | Published by | Subscribers (auth) | Replay? | Client on reconnect |
|---|---|---|---|---|---|
| user/{accountId}/orders | { orderId, status } | order service | owner only | no | refetch list |

## Permissions

| Operation | Rule | Notes |
|---|---|---|
| submitOrder | caller owns cart | |
| getOrder | caller is buyer or seller | viewer-scoped fields: `canCancel` |

## Media

| Album/purpose | Types | Max size | Max duration | URL lifetime | Flow |
|---|---|---|---|---|---|

## Changelog

| Date | Change | Additive/Breaking | Front-end action |
|---|---|---|---|
