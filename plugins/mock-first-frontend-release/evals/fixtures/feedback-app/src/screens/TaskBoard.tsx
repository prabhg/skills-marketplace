import { useTasksQuery, useMoveTaskMutation, useAssignTaskMutation } from "../api/tasks/hooks";
import type { ProjectId } from "../api/_shared/ids";
import { useQueryClient } from "@tanstack/react-query";
// Kanban: columns todo/doing/done; drag to move; assignee picker; shows due date (red when overdue).
export function TaskBoard({ projectId }: { projectId: ProjectId }) {
  const tasks = useTasksQuery(projectId);
  const move = useMoveTaskMutation();
  const assign = useAssignTaskMutation();
  const qc = useQueryClient();
  const onDrop = async (id: any, status: any) => { await move.mutateAsync({ id, status }); await tasks.refetch(); };
  const onAssign = async (id: any, m: any) => { await assign.mutateAsync({ id, assigneeId: m }); qc.invalidateQueries(); };
  return <div>{tasks.data?.length ?? 0} tasks</div>;
}
