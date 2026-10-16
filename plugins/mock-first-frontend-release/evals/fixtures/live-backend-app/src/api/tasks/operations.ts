import { mockLatency, maybeInjectError } from "../_shared/simulate";
import { transport } from "../../lib/transport";
import type { MemberId, ProjectId, TaskId } from "../_shared/ids";
import type { Task, TaskStatus } from "./types";
import * as store from "./mock/storage";

// LIVE (first page only)
export async function getTasks(projectId: ProjectId): Promise<Task[]> {
  const data = await transport.request<{ projectTasks: { items: any[] } }>(`query($p:ID!){ projectTasks(projectId:$p){ items { id projectId title status assigneeAccountId dueOn createdAt } } }`, { p: projectId });
  return data.projectTasks.items.map((t) => ({ ...t, status: t.status.toLowerCase(), assigneeId: t.assigneeAccountId, watcherIds: [] }));
}

// MOCK — createTask (see mock body spec in history)
export async function createTask(input: { projectId: ProjectId; title: string; assigneeId?: MemberId; dueOn?: string }): Promise<Task> { await mockLatency(); maybeInjectError("createTask"); return store.create(input); }
// MOCK — moveTask
export async function moveTask(id: TaskId, status: TaskStatus): Promise<Task> { await mockLatency(); return store.move(id, status); }
// MOCK — assignTask
export async function assignTask(id: TaskId, assigneeId: MemberId | null): Promise<Task> { await mockLatency(); return store.assign(id, assigneeId); }
