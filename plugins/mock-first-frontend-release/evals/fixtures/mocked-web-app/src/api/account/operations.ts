import { mockLatency, maybeInjectError } from "../_shared/simulate";
import type { Me } from "./types";
import { readMe, writeMe } from "./mock/storage";

// MOCK — backend spec for getMe: returns the caller's own record (identity from token).
export async function getMe(): Promise<Me> { await mockLatency(); maybeInjectError("getMe"); return readMe(); }

// MOCK — backend spec for completeOnboarding:
//  1. validate displayName 2..40 chars → validation{displayName}
//  2. write Account.displayName, create MemberProfile(displayName) if missing
//  3. set Account.onboardingDone = true
//  4. return fresh Me
export async function completeOnboarding(input: { displayName: string }): Promise<Me> {
  await mockLatency(); maybeInjectError("completeOnboarding");
  return writeMe({ displayName: input.displayName.trim(), onboardingDone: true });
}

// DEV-ONLY: stands in for the billing provider. Internal builds only.
export async function devSetPlan(plan: "free" | "team"): Promise<Me> { await mockLatency(); return writeMe({ plan }); }
