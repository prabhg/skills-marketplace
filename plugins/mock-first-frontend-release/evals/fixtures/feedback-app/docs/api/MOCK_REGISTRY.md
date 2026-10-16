# Mock registry

Last reconciled: (3 rounds ago) against no backend yet

| Domain | Operation | Kind | Status | Consumers | Id fields (kind) | Notes |
|---|---|---|---|---|---|---|
| account | getMe | Q | MOCK | app shell | accountId (AccountId), memberId (MemberId) | |
| account | completeOnboarding | M | MOCK | Onboarding | | |
| account | devSetPlan | M | DEV-ONLY | dev menu | | stands in for billing |
| projects | getProjects | Q | MOCK | ProjectList | id, ownerId, memberIds | |
| projects | createProject | M | MOCK | ProjectSetup | | |
| projects | addMember | M | MOCK | ProjectSetup | memberId | |
| tasks | getTasks | Q | MOCK | TaskBoard | assigneeId, watcherIds | 40 seeded rows |
| tasks | createTask | M | MOCK | NewTaskSheet | | |
| tasks | moveTask | M | MOCK | TaskBoard | | |
