import type { Me } from "../types";
const KEY = "mock:me";
export function readMe(): Me { return JSON.parse(localStorage.getItem(KEY) ?? "null") ?? seedMe(); }
export function writeMe(patch: Partial<Me>): Me { const me = { ...readMe(), ...patch }; localStorage.setItem(KEY, JSON.stringify(me)); return me; }
function seedMe(): Me { const me = { accountId: "acc_self", memberId: "mem_self", displayName: "", email: "me@example.com", plan: "free", onboardingDone: false } as Me; localStorage.setItem(KEY, JSON.stringify(me)); return me; }
