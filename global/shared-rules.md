# Global instructions (all projects, all machines)

## Environment & destructive-operation safety

These rules apply to **every** project and override convenience. Treat them as paramount.

- **Multiple environments exist per project** — typically dev and prod, often staging, and
  sometimes PR/preview builds. Their resource identifiers (DynamoDB table suffixes, Amplify/app
  IDs, S3 buckets, Lambda names, git branches) **differ per project and per environment and are
  NOT guessable**. Never assume which resource is which (e.g. do not hardcode a branch infix
  like `-ma-`/`-de-` or a fixed prod suffix).
- **Establish the dev/prod mapping EARLY — as one of your first steps when you begin working
  with any cloud CLI (`aws`, `gcloud`, `az`, or similar) in a project**, before you run
  anything that could mutate state. To identify it, in order:
  1. **Recall project memory** from prior interactions — the env-identification scheme may
     already be recorded (check memory / `MEMORY.md` for this project).
  2. **Look for explicit identifiers** in resource names — most projects share a common env
     token across resources, e.g. `-dev`, `-dev-`, `dev-`, `-prod`, `staging`, an account ID,
     or a profile/branch name.
  3. **If still ambiguous, ask the human** how prod vs dev resources are distinguished for this
     project (e.g. "which DynamoDB table suffix / account / profile is dev vs prod?").
  Once determined, **remember it** — save the project's env-identification scheme to memory so
  future sessions don't have to re-derive it (and re-verify it still holds, since infra changes).
- **Before ANY mutating or destructive operation on a cloud resource, re-confirm which
  environment it belongs to** using the mapping above. If you cannot positively confirm it is
  the intended (dev) target, STOP and ask.
- **Never alter or delete data on prod or staging unless the user explicitly asks** for that
  specific operation.
- **Never delete data on S3 — in ANY environment, including dev — without explicit,
  per-operation approval.**
- **Never run a destructive or irreversible command without first stating its full scope and
  blast radius and getting approval** (what tables/buckets/rows/branches it touches).
- **dev is the only manual target. Prod (and staging) deploy via CI/CD only** — never push to
  main/prod branches or trigger prod deploys (e.g. `ampx pipeline-deploy`, `amplify start-job`)
  directly.

## Communication with human

When reporting information to me, be extremely concise, and sacrifice grammar for the sake of concision.

## Design principles

- **Leave room for possible futures; model nothing for them.** When a feature "might" come later, do not add
  fields, tables, API operations, policy objects, placeholders, "not built" seams or open decisions for it.
  Move or build only what is needed today; record at most one sentence of rationale. Situations change, and
  unused structure is cost.
