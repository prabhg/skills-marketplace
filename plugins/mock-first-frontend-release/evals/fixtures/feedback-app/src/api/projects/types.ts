import type { MemberId, ProjectId } from "../_shared/ids";
export interface Project { id: ProjectId; name: string; ownerId: MemberId; memberIds: MemberId[]; isSetupComplete: boolean; archived: boolean }
export interface ProjectStats { projectId: ProjectId; open: number; done: number; overdue: number }
