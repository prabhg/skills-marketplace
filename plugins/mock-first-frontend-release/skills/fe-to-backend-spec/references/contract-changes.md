# Additive vs breaking contract changes

| Change | Class | Rule |
|---|---|---|
| New operation | additive | ship backend first; front end wires when ready |
| New optional output field | additive | backend first; mapper ignores until used |
| New optional input field | additive | backend must default it |
| New enum value in output | **breaking for old clients** | mapper must map unknown values to a safe fallback *before* the backend sends it |
| New required input field | breaking | add optional + default, migrate clients, then require |
| Rename / remove field | breaking | add new, dual-write, migrate clients, remove after old builds age out |
| Change id kind of a field | breaking | new field with the new kind; never reuse the name |
| Tighten validation | breaking | front-end forms first, then backend |
| Change auth rule | breaking | list affected screens; owner ruling |

Mobile clients stay installed for months: "old clients" means every build still in testers' or users'
hands, not just the last one. Breaking changes therefore need either a forced-update gate or the
add/migrate/remove sequence.

Front-end side of any change that alters a mapper's output shape: bump the persisted-cache schema
version in the same commit.

Who files what: the side that finds a gap writes a short contract ticket (operation, current, wanted,
class, blocking which feature) to the side that owns the contract. The finder never works around it in
its own code.
