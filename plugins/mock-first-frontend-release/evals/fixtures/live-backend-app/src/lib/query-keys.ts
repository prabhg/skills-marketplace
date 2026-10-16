import type { ProjectId, TaskId } from "../api/_shared/ids";
export const queryKeys = {
  account: { me: () => ["account", "me"] as const },
  projects: { all: () => ["projects"] as const, list: () => ["projects", "list"] as const, detail: (id: ProjectId) => ["projects", "detail", id] as const, stats: (id: ProjectId) => ["projects", "stats", id] as const },
  tasks: { all: () => ["tasks"] as const, list: (projectId: ProjectId) => ["tasks", "list", projectId] as const, detail: (id: TaskId) => ["tasks", "detail", id] as const },
};
export const CACHE_SCHEMA_VERSION = 3;
