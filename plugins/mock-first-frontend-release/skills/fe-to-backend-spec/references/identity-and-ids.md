# Identity and ids

Most contract breaks found at integration were not logic bugs but **identity-shape mismatches**: the
front end held one kind of id and the backend expected another, and the mocks never noticed because
mock lookups accept any string.

Typical shapes:
- An auth/account id (private, from the identity provider) vs a public profile id (shown to others).
- A share/display code (short, human) vs the profile id it resolves to.
- A field named `userId` that actually carries a profile id (or the reverse).
- Own-record reads returning a different type (own profile) than other-people reads (public profile),
  with different fields: a field present on one is silently missing on the other.
- Rows whose author is implied (1:1 conversation rows with a null author and a `mine` flag): a mapper
  that requires an author blanks the thread.

Rules for the spec:
1. One named kind per identifier; fields named after their kind (`requesterProfileId`).
2. Public surfaces carry public ids only. If the backend needs the account id it resolves it server-side.
3. "Me" operations take identity from the token, never from arguments.
4. Own-record and others-record types: list the fields each carries, side by side, for every entity
   that has both. Any field the UI shows on both must exist on both or be explicitly derived.
5. Nullable ids are documented with when and why they are null.
6. Mapper tests (later, in mock-to-live-integration) assert the kind of every id field; reviewers treat
   any cast between kinds as a defect unless commented.
