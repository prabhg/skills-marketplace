import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "../../lib/query-keys";
import * as ops from "./operations";
export const useProjectsQuery = () => useQuery({ queryKey: queryKeys.projects.list(), queryFn: ops.getProjects });
export const useProjectStatsQuery = (id: Parameters<typeof ops.getProjectStats>[0]) => useQuery({ queryKey: queryKeys.projects.stats(id), queryFn: () => ops.getProjectStats(id) });
export const useCreateProjectMutation = () => { const qc = useQueryClient(); return useMutation({ mutationFn: ops.createProject, onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.projects.all() }) }); };
export const useAddMemberMutation = () => useMutation({ mutationFn: (v: { projectId: Parameters<typeof ops.addMember>[0]; memberId: Parameters<typeof ops.addMember>[1] }) => ops.addMember(v.projectId, v.memberId) });
export const useUpdateProjectMutation = () => useMutation({ mutationFn: (v: { id: Parameters<typeof ops.updateProject>[0]; patch: Parameters<typeof ops.updateProject>[1] }) => ops.updateProject(v.id, v.patch) });
