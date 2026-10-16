import type { AccountId, MemberId } from "../_shared/ids";
export interface Me { accountId: AccountId; memberId: MemberId; displayName: string; email: string; plan: "free" | "team"; onboardingDone: boolean }
export interface MemberCard { memberId: MemberId; displayName: string; avatarUrl: string | null }
