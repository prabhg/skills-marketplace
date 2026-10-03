---
name: architecture-share-doc
description: Build a team-shareable, single-file HTML architecture review document from a design doc or spec, with a layered system map, one pre-rendered sequence diagram per user action, services and what each owns, the event bus, APIs by domain, features, plans/tiers, access rules, environments, security, rollout and decisions. Use whenever the user asks for an "architecture share doc", an "architecture review doc for the team", a "shareable architecture HTML", a "system map plus user flow diagrams", wants to "document the architecture like the Rebel/Flewed share doc", or wants an existing share doc updated to a new revision of its design doc, even if they only say "make the architecture page" or "diagram every user flow for the team".
---

# Architecture share doc

Produce one self-contained HTML page a team can read to review an architecture: a system map, a flow diagram for every user action, and compact reference sections, all faithful to a canonical design source. The diagrams are the core of the deliverable; the prose around them is short.

## When to use

- The user wants a shareable/reviewable architecture page for a project with a design doc, spec, or deployed system to describe.
- The user wants an existing share page updated after the design doc changed (new revision, new repo, redrawn flow).
- The user names the Rebel or Flewed share doc as the format to copy.

**Do not use** for:
- Writing the architecture itself (designing services, choosing tech). This skill documents a design; it never invents one.
- A single diagram or a quick explanation in chat; draw that directly.
- Docs that belong in a repo as Markdown (ADRs, READMEs).

## Bundled files

| Path | Use |
|---|---|
| `references/format-spec.md` | The format: section order and content rules, tokens, map and flow conventions, tone, checklist. Read it fully before writing. |
| `assets/template.html` | Page skeleton with all CSS/JS chrome and one example of every component, `{{PLACEHOLDERS}}` everywhere. Copy it; never edit it in place. |
| `assets/examples.md` | Two annotated flows (simple; split into phases) and the system-map layout approach. |
| `scripts/flowgen.py` | flows.json → mermaid sources; label wrapping; warns over 7 participants. |
| `scripts/render.py` + `render.html` | Pre-render mermaid to static SVG with headless Chrome. |
| `scripts/postprocess.py` | Per-diagram id fix, service colours, event/frame arrow styling, render checks. |
| `scripts/assemble.py` | Puts SVGs into the page at `<!--SEQ:f-id-->` markers. |
| `scripts/check.py` | Diagram counts, leftover placeholders, forbidden terms, names not found in the source, event senders. |
| `scripts/shot.py` | Isolated desktop screenshot of one section or flow, for looking at it. |
| `scripts/build.sh` | flowgen → render → postprocess → assemble in one go. |

Dependencies: `python3` (stdlib only), Google Chrome/Chromium/Brave, network access to `cdn.jsdelivr.net` (mermaid 11, build time only) and Google Fonts. Nothing is installed. Work files go to a temp or scratch dir, never into the user's repo.

## Step 1 — Gather inputs

You need:
1. **The canonical design source** (doc/spec, ideally versioned) and its revision and date. It is the single source of truth for every name.
2. **User journeys / requirements** (what people actually do in the product), to pick the flows and the features/tiers.
3. **Output path** for the HTML.
4. **Reference doc** if the user wants a specific existing page matched.

If the source is missing, ask for it; don't reconstruct an architecture from code or memory. If the output path is missing, propose one next to the other docs and confirm. Ask which environments map to prod vs dev only if the source doesn't say.

## Step 2 — Study the sources and plan

- Read the format spec, then the whole design source. Note the revision/date and the tags it uses for unverified or pending facts.
- Make the inventory: services/repos (with what each owns and must not own), events (producer → consumers), API operations by service, permission rules, environments, tiers, decisions, open items.
- List the user actions that become flows. One flow per thing a person does (sign in, pay, upload, send, block, delete account …), plus important system journeys (webhook lapse, scheduled shred, ops alerts). Give them letters in journey order.
- Choose a fixed alias and colour group per service; the same colour is used in the map boxes, flow participants, card squares and chips. The template and `postprocess.py` use `groups` in flows.json for this.
- Decide which optional sections apply (APIs, access, rollout, decisions); see format-spec §2.

## Step 3 — Author the flows as data

Write `flows.json` (shape in `scripts/flowgen.py` docstring, examples in `assets/examples.md`):
- Step kinds: `call` (operation, invoke, webhook), `reply`, `event` (bus), `frame`/`push` (to a device), `self`, plus `note`, `loop`, `opt`, `alt`.
- Every label starts with the real operation/event/frame name from the source. Where the source names no operation for a step, describe the step and say so in the paragraph; never make a name up.
- At most 7 participants. Split longer actions into phases (A1/A2) at an async hand-off. Leave the API gateway out; the app calls services directly.
- Event arrows start at the event's documented producer (or the bus).

## Step 4 — Build

```sh
S=~/.claude/skills/architecture-share-doc/scripts
WORK=$(mktemp -d -t archdoc)                    # never inside a repo
cp ~/.claude/skills/architecture-share-doc/assets/template.html "$WORK/page.html"   # then fill it in
sh $S/build.sh flows.json "$WORK/page.html" OUT.html "$WORK"
# or step by step:
python3 $S/flowgen.py flows.json "$WORK" && python3 $S/render.py "$WORK" \
 && python3 $S/postprocess.py flows.json "$WORK" && python3 $S/assemble.py "$WORK/page.html" flows.json "$WORK" OUT.html
```

Fill the page: hand-lay the system map on the template's grid (format-spec §4, examples §3), write each section from the inventory, and put one `<article class="panel flow">` with a `<!--SEQ:f-id-->` marker per flow. Keep prose terse. Mark unverified or pending things as the source does. Label placeholder values (mock prices, sample hosts) as placeholders. Hero stats must be counted by script from the source, not estimated.

`postprocess.py` prints each diagram's width. Over ~1360px it will render too small: shorten labels (per-flow `"ww": 17`), cut participants, or split the flow, and rebuild.

## Step 5 — Verify by looking

1. `python3 $S/check.py OUT.html flows.json --source DESIGN.md --prefixes <service op prefixes> --forbid <terms from any previous project/reference>`. Fix every name it reports missing from the source; compare the event-sender list with the source's event catalogue.
2. Screenshot the system map and **every changed or new flow** (at least 6 on a first build) with `python3 $S/shot.py OUT.html <id> shot.png`, then read the PNGs. Look for clipped or overlapping labels, text crossing lines, blank boxes, unreadably small diagrams.
3. Check the console and a narrow viewport. The in-app browser pane can't inspect `file://`; serve the folder with `python3 -m http.server --bind 127.0.0.1 PORT` and open `http://127.0.0.1:PORT/…`. At 390px wide nothing but `.scroll-x`/`.seq` content may scroll sideways. Stop the server afterwards.
4. Count: diagrams authored = diagrams rendered (check.py prints both, plus the map and other figures).

## Hard rules

- One self-contained HTML file; the only network load at view time is Google Fonts. Diagrams are static SVG; no mermaid runtime in the page.
- Never invent architecture. Every service, operation, event, frame and model name comes verbatim from the source. Keep its "unverified"/"pending" markings.
- One flow per user action; every arrow labelled; sync calls, responses, bus events and realtime frames/pushes styled differently, with a legend.
- Same colour per service across map, flows, cards and chips.
- State the source revision and date in the kicker and footer. Placeholder values are labelled as placeholders.
- No leftover content from a template, reference or earlier project: grep case-insensitively for its product names, domains and domain terms (also in CSS class names and comments).
- Don't modify the reference doc or any repo; write only the output file and scratch files.

## Pitfalls already hit (and what fixes them)

| Symptom | Cause | Fix (where) |
|---|---|---|
| All participant boxes blank | mermaid's `id="drop-shadow"` repeated in every SVG; the first one is hidden or missing | per-diagram id prefix (`postprocess.py`) |
| `createLongOperationNa-` / `me` | mermaid `wrap: true` hyphen-splits tokens | `wrap: false` + manual wrap on spaces/`(` (`render.html`, `flowgen.py`) |
| Diagram text tiny | viewBox too wide (8+ participants, long labels) | ≤7 participants, `ww`, phases; inline min-width 0.8·w (`assemble.py`) |
| Labels clipped or misplaced | fonts not loaded when mermaid measured | `document.fonts.load` before render (`render.html`) |
| Note text spills out of its box | note font smaller than message font; note over an `actor` | `noteFontSize` 16, wrap 26, never over a person (`flowgen.py`) |
| Map labels collide | long band labels, edge labels across rails | short band labels, end-anchored edge labels, look at the shot |
| Page scrolls sideways on tablets | long UPPER_SNAKE names in card `dd` | `overflow-wrap:anywhere` (in template CSS) |
| Headless Chrome hangs | it doesn't exit after a screenshot | scripts kill it after the file appears |
| Browser pane shows a static snapshot | file:// pages can't be inspected there | serve over 127.0.0.1 |

## Step 6 — Report

Tell the user: output path and size; sections produced vs the format (and any omitted, with the reason); diagram count by type; what the checks found and what you fixed after looking at screenshots; assumptions and anything the source doesn't name. When updating a page to a new design revision, follow format-spec §9 (diff the source, update every place a changed component appears, recount, re-check).
