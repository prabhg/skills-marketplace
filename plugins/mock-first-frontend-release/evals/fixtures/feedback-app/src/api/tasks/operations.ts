import { mockLatency, maybeInjectError } from "../_shared/simulate";
import type { MemberId, ProjectId, TaskId } from "../_shared/ids";
import type { Task, TaskStatus } from "./types";
import * as store from "./mock/storage";

// MOCK — getTasks: tasks of a project the caller belongs to (forbidden otherwise); ordered by createdAt desc; page 50 + cursor.
export async function getTasks(projectId: ProjectId): Promise<Task[]> { await mockLatency(); maybeInjectError("getTasks"); return store.list(projectId); }

// MOCK — createTask:
//  1. title 1..120 → validation{title}; caller is project member → forbidden
//  2. write Task(status=todo), add creator to watcherIds
//  3. notify assignee (if any) — event TASK_ASSIGNED
export async function createTask(input: { projectId: ProjectId; title: string; assigneeId?: MemberId; dueOn?: string }): Promise<Task> { await mockLatency(); maybeInjectError("createTask"); return store.create(input); }

// MOCK — moveTask: change status; moving to done stamps completedAt; event TASK_STATUS_CHANGED to watchers.
export async function moveTask(id: TaskId, status: TaskStatus): Promise<Task> { await mockLatency(); maybeInjectError("moveTask"); return store.move(id, status); }

// MOCK — assignTask: assignee must be a project member (validation{assigneeId}); event TASK_ASSIGNED.
export async function assignTask(id: TaskId, assigneeId: MemberId | null): Promise<Task> { await mockLatency(); return store.assign(id, assigneeId); }
