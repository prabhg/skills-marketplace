export type ApiErrorKind = "network" | "timeout" | "unauthenticated" | "forbidden" | "validation" | "conflict" | "not_found" | "server";
export class ApiError extends Error {
  constructor(public kind: ApiErrorKind, public detail?: { field?: string }) { super(kind); }
}
