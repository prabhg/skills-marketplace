import type { MemberId, ProjectId, TaskId } from "../_shared/ids";
export type TaskStatus = "todo" | "doing" | "done";
export interface Task { id: TaskId; projectId: ProjectId; title: string; status: TaskStatus; assigneeId: MemberId | null; dueOn: string | null; watcherIds: MemberId[]; createdAt: string }
