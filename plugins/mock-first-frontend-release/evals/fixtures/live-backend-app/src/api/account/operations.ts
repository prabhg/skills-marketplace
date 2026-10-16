import { mockLatency, maybeInjectError } from "../_shared/simulate";
import { transport } from "../../lib/transport";
import type { Me } from "./types";
import { readMe, writeMe } from "./mock/storage";

// LIVE
export async function getMe(): Promise<Me> {
  const data = await transport.request<{ me: any }>(`query { me { accountId memberId displayName email plan onboardingDone } }`);
  const me = { ...data.me, plan: data.me.plan.toLowerCase() } as Me;
  return withMockOnboarding(me);
}
// keeps onboarding state from the old mock so testers don't redo it
function withMockOnboarding(me: Me): Me { const local = readMe(); return { ...me, onboardingDone: local.onboardingDone, displayName: local.displayName || me.displayName }; }

// LIVE
export async function completeOnboarding(input: { displayName: string }): Promise<Me> {
  const data = await transport.request<{ completeOnboarding: any }>(`mutation($n:String!){ completeOnboarding(displayName:$n){ accountId memberId displayName email plan onboardingDone } }`, { n: input.displayName.trim() });
  return { ...data.completeOnboarding, plan: data.completeOnboarding.plan.toLowerCase() };
}

// DEV-ONLY (still mock)
export async function devSetPlan(plan: "free" | "team"): Promise<Me> { await mockLatency(); return writeMe({ plan }); }
