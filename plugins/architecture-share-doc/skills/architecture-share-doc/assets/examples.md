# Worked examples

All names below are invented. In a real doc every operation and event name comes verbatim from the source design.

## 1. A simple flow (one user action, 6 participants, no phases)

flows.json entry:
```json
{"id": "f-share", "letter": "B", "title": "Share a note",
 "parts": ["MB", "APP", "NS", "BUS", "NO", "PEER"],
 "steps": [
  ["call",  "MB",  "APP", "Share with a collaborator"],
  ["call",  "APP", "NS",  "notesShareNote(noteId, profileId, idempotencyKey)"],
  ["self",  "NS",  "NS",  "Idempotency put, can note.share, TransactWrite Share row"],
  ["reply", "NS",  "APP", "Share"],
  ["event", "NS",  "BUS", "NOTE_SHARED via outbox"],
  ["event", "BUS", "NO",  "NOTE_SHARED"],
  ["alt", [["collaborator online", [["frame", "NO", "PEER", "Frame note.shared on /user/u/activity"]]],
           ["offline",             [["push",  "NO", "PEER", "Content-free push note.shared"]]]]],
  ["note", "over NS,BUS", "Pushes never carry note text"]
 ]}
```
Why it reads well:
- Person on the far left, then the client, then services in call order, providers/bus to the right, the other person on the far right.
- The app talks to the service directly; the API gateway is not a participant (it adds width and no information).
- Each label starts with the real name (`notesShareNote`, `NOTE_SHARED`, `note.shared`) and adds only the essential argument or effect.
- Kinds drive the styling: `call` solid, `reply` dashed, `event` teal dashed, `frame`/`push` red dotted.
- The note sits over two service participants, never over a person.

Generated mermaid (what `flowgen.py` emits):
```
sequenceDiagram
  autonumber
  actor MB as Member
  participant APP as Notes app
  participant NS as notes-<br/>service
  ...
  APP->>NS: notesShareNote<br/>(noteId, profileId,<br/>idempotencyKey)
  NS-)BUS: NOTE_SHARED via outbox
  alt collaborator online
    NO--)PEER: Frame note.shared on<br/>/user/u/activity
  else offline
    NO--)PEER: Content-free push<br/>note.shared
  end
  Note over NS,BUS: Pushes never carry note<br/>text
```

## 2. A long action split into phases (D1, D2)

An approval flow touched 8 participants (staff, ops script, safety, user, bus, permission, notification, app) and rendered 1,700px wide at unreadable scale. Splitting by *who acts* fixed it:

- **D1 · Submit the application** — member, app, user-service, bus, permission-service, safety-service (6). Ends at the event that opens the review case.
- **D2 · A moderator approves** — moderator, safety-service, user-service, bus, permission-service, notification-service, app (7). Starts from the moderator; the ops script is folded into the moderator's label instead of being its own participant.

Rules of thumb: split at an asynchronous hand-off (an event, a webhook, a scheduled job, a human decision); give both phases the same letter with 1/2; repeat the participant that links them; each phase must make sense without the other; keep each under ~16 steps and ≤ 7 participants. `flowgen.py` warns above 7; `postprocess.py` flags width over 1360px.

## 3. System map layout approach

- Decide the bands top to bottom by distance from the user: people and devices → API edge → services → async backbone → data and delivery → outside services. 4 to 6 bands.
- Put boxes on a fixed grid (4 × 265px at x = 40, 325, 610, 895, or 3 × 360px). Generate the grid in a small script if there are many services, so coordinates cannot drift.
- Colour each service box with the same fill/stroke as its participant group in flows.json.
- Draw only edges between adjacent bands; anything that bypasses layers (direct uploads, CDN reads, pushes, webhooks) goes on a *rail* outside the bands with a rotated label.
- One horizontal "bus line" under the API edge with short drops into the services band replaces a fan of crossing arrows.
- Pick one end-to-end journey (e.g. one message) and place numbered dots on the top-right corner of each box it visits; narrate them in the figcaption.
- Keep band labels short: vertical edges at x≈172 cross long band labels. Place edge labels right of their edge, or `text-anchor="end"` left of it, never across another edge or rail label.
- Then screenshot it and look; most map bugs are label collisions you only see rendered.
