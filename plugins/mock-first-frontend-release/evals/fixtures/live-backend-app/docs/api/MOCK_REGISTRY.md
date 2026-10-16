# Mock registry

Last reconciled: 2026-08-20 against no backend yet. Design settled 2026-08-25 (round 3).

| Domain | Operation | Kind | Status | Consumers | Id fields (kind) | Notes |
|---|---|---|---|---|---|---|
| account | getMe | Q | WIRED | app shell | accountId (AccountId), memberId (MemberId) | |
| account | completeOnboarding | M | WIRED | Onboarding | | |
| account | devSetPlan | M | DEV-ONLY | dev menu | | stands in for billing |
| projects | getProjects | Q | MOCK | ProjectList | id, ownerId (MemberId), memberIds | |
| projects | createProject | M | MOCK | ProjectSetup | | |
| projects | addMember | M | MOCK | ProjectSetup | memberId | |
| projects | getProjectStats | Q | MOCK | (none) | | |
| tasks | getTasks | Q | WIRED | TaskBoard | assigneeId (MemberId), watcherIds | |
| tasks | createTask | M | MOCK | NewTaskSheet | assigneeId (MemberId) | |
| tasks | moveTask | M | MOCK | TaskBoard | | |
| tasks | assignTask | M | MOCK | TaskBoard | assigneeId (MemberId) | |
