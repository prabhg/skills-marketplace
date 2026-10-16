export const mockLatency = (min = 150, max = 600) => new Promise((r) => setTimeout(r, min + Math.random() * (max - min)));
const forced = new Map<string, import("./errors").ApiErrorKind>();
export function maybeInjectError(op: string) { const k = forced.get(op); if (k) throw new (require("./errors").ApiError)(k); }
export const devErrors = forced;
