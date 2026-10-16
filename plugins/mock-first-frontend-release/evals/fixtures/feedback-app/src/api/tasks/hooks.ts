import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "../../lib/query-keys";
import * as ops from "./operations";
import type { ProjectId } from "../_shared/ids";
export const useTasksQuery = (projectId: ProjectId) => useQuery({ queryKey: queryKeys.tasks.list(projectId), queryFn: () => ops.getTasks(projectId) });
export const useCreateTaskMutation = () => { const qc = useQueryClient(); return useMutation({ mutationFn: ops.createTask, onSuccess: (t) => qc.invalidateQueries({ queryKey: queryKeys.tasks.list(t.projectId) }) }); };
export const useMoveTaskMutation = () => { const qc = useQueryClient(); return useMutation({ mutationFn: (v: { id: Parameters<typeof ops.moveTask>[0]; status: Parameters<typeof ops.moveTask>[1] }) => ops.moveTask(v.id, v.status), onSuccess: (t) => qc.setQueryData(queryKeys.tasks.detail(t.id), t) }); };
export const useAssignTaskMutation = () => useMutation({ mutationFn: (v: { id: Parameters<typeof ops.assignTask>[0]; assigneeId: Parameters<typeof ops.assignTask>[1] }) => ops.assignTask(v.id, v.assigneeId) });
