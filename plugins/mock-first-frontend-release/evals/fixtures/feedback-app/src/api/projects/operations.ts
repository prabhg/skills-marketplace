import { mockLatency, maybeInjectError } from "../_shared/simulate";
import type { MemberId, ProjectId } from "../_shared/ids";
import type { Project, ProjectStats } from "./types";
import * as store from "./mock/storage";

// MOCK — getProjects: projects where the caller is a member, newest first, max 50.
export async function getProjects(): Promise<Project[]> { await mockLatency(); maybeInjectError("getProjects"); return store.listForMe(); }

// MOCK — createProject: caller becomes owner and first member. name 1..60 → validation{name}.
export async function createProject(input: { name: string }): Promise<Project> { await mockLatency(); maybeInjectError("createProject"); return store.create(input.name); }

// MOCK — addMember: owner only (forbidden otherwise); member must exist (not_found).
export async function addMember(projectId: ProjectId, memberId: MemberId): Promise<Project> { await mockLatency(); maybeInjectError("addMember"); return store.addMember(projectId, memberId); }

// MOCK — updateProject: generic patch (owner only).
export async function updateProject(projectId: ProjectId, patch: Partial<Project>): Promise<Project> { await mockLatency(); return store.patch(projectId, patch); }

// MOCK — getProjectStats: counts by status. (no screen uses this yet)
export async function getProjectStats(projectId: ProjectId): Promise<ProjectStats> { await mockLatency(); return store.stats(projectId); }
