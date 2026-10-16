# Routing backend gaps

## Ticket shape

```
{BUG|CONTRACT|TOOLING}: {service} {operation}
Observed: {probe output, redacted}
Wanted:   {contract line or need}
Class:    {additive|breaking}   (CONTRACT only; see fe-to-backend-spec contract-changes.md)
Blocks:   {front-end ticket id(s)}
Evidence: {request id / log reference / commit}
```

## Rules
- File BUG only after a probe reproduces it; "may fail" goes in risks, not tickets.
- One ticket per root cause, not per symptom.
- Do not file "by design" behaviour as a bug: check the backend's docs/decisions first (e.g. a null field
  that is null on purpose).
- A front-end interim (when the owner wants the feature before the backend fix) lives inside the
  operation body, with `// INTERIM until {ticket}: remove when …`, and is listed in the registry notes.
  Never a second write from a component; that duplicates data once the backend ships its fix.
- When the backend ships the fix: re-probe, remove the interim, close both tickets, update the registry.
- If several sessions or teams work in parallel, the gap goes to whoever owns the backend lane, not
  straight into another lane's code.
