import { useState } from "react";
import { useAddMemberMutation, useCreateProjectMutation, useUpdateProjectMutation } from "../api/projects/hooks";
import type { MemberId } from "../api/_shared/ids";

// "New project" wizard: name + invite teammates, then done.
export function ProjectSetup({ invitees }: { invitees: MemberId[] }) {
  const [name, setName] = useState("");
  const create = useCreateProjectMutation();
  const addMember = useAddMemberMutation();
  const update = useUpdateProjectMutation();
  async function onFinish() {
    const project = await create.mutateAsync({ name });
    for (const memberId of invitees) await addMember.mutateAsync({ projectId: project.id, memberId });
    await update.mutateAsync({ id: project.id, patch: { isSetupComplete: invitees.length > 0 } });
  }
  return <form onSubmit={(e) => { e.preventDefault(); void onFinish(); }}><input value={name} onChange={(e) => setName(e.target.value)} /><button>Create</button></form>;
}
