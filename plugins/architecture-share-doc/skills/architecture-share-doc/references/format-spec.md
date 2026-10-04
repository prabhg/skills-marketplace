# Architecture Share page: format spec

The single-page "architecture share" HTML a team uses to review a platform's architecture. Product-agnostic. `assets/template.html` implements everything below; the scripts in `scripts/` implement §5. If a user hands you an existing share page saved from claude.ai, the outer file is only a frame shell: the authored page is the inner `*_files/saved_resource.html`, starting at `<title>`.

Contents: 1 Page shape · 2 Section inventory · 3 Tokens and components · 4 System map · 5 Flow diagrams · 6 Service cards · 7 Tone · 8 Build checklist · 9 Keeping a page in sync

## 1. Page shape

- One self-contained HTML file. Inline `<style>` and a tiny inline `<script>`. The only external load is Google Fonts (IBM Plex Sans 400/500/600/700 and IBM Plex Mono 400/500).
- **Light only.** `color-scheme: light` on `:root` and `html`; no dark-mode media query. Explicit `body` background.
- No diagram runtime at view time. Every diagram is **static inline SVG**: the system map and small figures are hand-laid SVG; the per-flow diagrams are **Mermaid `sequenceDiagram`s pre-rendered at build time** (mermaid 11, `look: neo`) and pasted in as SVG. No mermaid script in the shipped page.
- Width: `.wrap { max-width: 1180px; padding-inline: 16px }`. Wide figures sit in `.scroll-x` with an SVG `min-width` (map 1120px, sequence 1000px, small figures 760px), so phones scroll the figure horizontally instead of the page.
- Anchors: TOC and flow-index links are bare `#id` fragments.
- Print: no special print stylesheet. The sticky TOC and the filter buttons are the only interactive chrome.

## 2. Section inventory (in order)

| # | Section id | Title pattern | Content |
|---|---|---|---|
| hero | `header.hero` | `h1`: "How X works, from A to B" | Kicker (small inline SVG glyph + "Product · doc kind <source revision> · design as of / as deployed <date>"), one-paragraph lede naming what the product is, then the cloud and runtime, service count, API, client, realtime path, event bus and identity; which branch is prod; "design only, nothing built" when true. Then a `.stats` row of 6 to 9 **countable** facts (`<b>N</b> label`), each counted by script from the source |
| nav | `nav.toc` | — | Sticky, blurred, horizontally scrollable pill links `<span class="n">01</span>Label`. Keep labels to one word so all fit at 1440px |
| 01 | `#map` | System map | One large layered SVG (§4) + a legend row + a figcaption narrating the numbered dots as one object's journey |
| 02 | `#flows` | User flows, step by step | Lede (one diagram per user action; arrow labels are real names; capitals are events). `.flow-index` of letter-coded links, a "How to read" legend with the arrow styles and the per-service colour key, then one `article.panel.flow` per action (§5) |
| 03 | `#services` | Services and what each one owns | `.grid` of cards, one per deployable repo (§6), then `.support` with an `h4` "Supporting repositories" (libs, tests, web apps, planned repos with a `planned` tag), then a one-line repo-count note |
| 04 | `#events` | The event bus: who announces what, and who listens | `table.tbl` Event / Produced by / Consumed by / What it does, `tr.group` rows by domain; an `outbox` tag where delivery is guaranteed; optional group rows for realtime channels and things not on the bus |
| 05 | `#apis` | APIs and their domains | **Optional**, include when the source lists the API surface: `table.tbl` grouped by owning service, columns Operations (codes joined by ` · `) / Ref / Access (tag: JWT, API key, dev only, admin, public) / Notes |
| 06 | `#features` | Features, and where each one stands | Filter buttons (All + one per status) above `.feat-grid` panels: area `h4`, features with `<small>` detail and a status `.tag`. For a design not yet built, use launch / gated / later instead of live / partial / planned, never "live" |
| 07 | `#plans` | Plans, and how <metered unit or entitlement> works | Tier table (capability rows × tier columns, incl. a lapsed/free column), label placeholder prices as placeholders; one small hand-laid SVG of the metering or entitlement lifecycle (boxes + labelled arrows + an amber dashed alternate path); optional comparison table of implementation options; `.two` panel "Rules worth knowing" |
| 08 | `#access` | Who can do what | **Optional**, include when the source has a permission model: gate/predicate table plus an action matrix (Action / Allowed when / Denial) grouped by domain |
| 09 | `#stack` | Technology | `.stack-grid` panels per layer; name left, version or role right in mono. Versions exactly as the source pins them, with verdict-gated pins said as such |
| 10 | `#envs` | Environments, domains and delivery | Lede: accounts, regions, branch model. Table What × one column per env (hosts, identity instance, payment mode, bus, removal policy). Then an `ol.pipeline` of 5 to 7 delivery stages |
| 11 | `#security` | Security and operations | Optional `.posture` panel (compliance target or explicit non-target), then `.two` grid of panels: Access, Content and data, Edge, Operations, plus topic panels when the source has them (e.g. on-device storage, checkout) |
| 12 | `#rollout` | Rollout | **Optional**, for designs not yet built: `ol.pipeline.ms` of milestones (`<b>M0 · name</b><span>scope</span>`) + a note on post-launch milestones and the launch bar |
| 13 | `#open` | Decisions and open items (or just Open items) | `.open` panel grids: "Decided" (ID · decision + one sentence; include "evaluated, not chosen" items with the one-line reason) and "Still open" (item + what it waits on: decision, benchmark, counsel) |
| footer | `footer.wrap` | — | Sources with revision and date; "design only" if true; unverified facts are marked the same way |

Renumber `sec-num`s and TOC numbers when you drop an optional section. Add sections only by reusing these components.

Every section starts with:
```html
<section id="x" class="wrap">
  <div class="sec-head"><span class="sec-num">NN</span><h2>Title</h2><p class="sec-lede">One or two sentences.</p></div>
  ...
</section>
```

## 3. Visual tokens and components

`:root` tokens (light):
`--bg #f3f4f6`, `--panel #fff`, `--panel-2 #eceef2`, `--ink #14161a`, `--muted #4a5161`, `--text-2 #2c323d`, `--line #d4d8df`, `--line-strong #aeb5c1`, `--accent #c42f28` (+ `--accent-soft #fbe8e6`), `--teal #0c7a69` (+ `#e0f2ee`), `--amber #945700` (+ `#fbefd9`), `--violet #5646c0` (+ `#ebe9fb`), `--band-a #f7f8fa`, `--band-b #eff1f4`, `--radius 10px`.

Semantics: accent red = numbering, people, public path, step dots; teal = async (events, queues, workflows) and "live/ok"; amber = partial, warnings, alternate paths; violet = libraries, outside providers, AI; grey dashed = planned.

Type: IBM Plex Sans 15px/1.55 body; `h1` clamp(28px, 4.2vw, 44px); `h2` clamp(22px, 2.8vw, 30px); `h3` 18px; `h4` 12px uppercase tracked muted. Mono (IBM Plex Mono) for code, section numbers, service names, flow letters. `text-wrap: balance` on headings.

Components:
- `.panel` white card with 1px `--line` border and 10px radius.
- `.tag` 10.5px uppercase pill: `.live` teal, `.partial` amber, `.planned` grey, `.lib` violet.
- `.chip` 12.5px rounded pill under each flow: `.svc` teal-soft (internal services), `.ext` violet-soft (outside providers), `.warn` amber-soft (pending items), plain grey (events, libraries).
- `table` 13.5px, uppercase sticky `th` on `--panel-2`, `tr.group td` uppercase muted band, `.tbl { min-width: 760px }` inside `.panel.scroll-x`.
- `.kv` definition grid (84px label column) inside service cards.
- `.pipeline` flex list with CSS counters showing `01`, `02` in accent mono.
- Mobile (`max-width: 560px`): body 14.5px, tighter hero and flow padding, `.kv` label column 70px. Long unbreakable names (UPPER_SNAKE events, bucket names) in card `dd`s overflow the page on tablets: add `.card { min-width: 0 } .kv dd { min-width: 0; overflow-wrap: anywhere }`.

JS: only the feature filter. Buttons carry `data-filter` and `aria-pressed`; `li[data-s]` items hide when not matching; a group with no visible items hides.

## 4. System map conventions (hand-laid SVG)

- `viewBox` about `0 0 1200 H`, `class="map"`, `role="img"` with a full-sentence `aria-label` describing the whole architecture.
- **Horizontal bands**, alternating `band-a`/`band-b` rects (x=30, w=1140, rx=12), each with an uppercase `band-label` at top-left: e.g. PEOPLE · PUBLIC EDGE · SERVICES · ASYNC BACKBONE · DATA · OUTSIDE SERVICES.
- **Boxes** are `<g class="box [kind]"><rect rx=9/>` with a 16px semibold title (`.t`), 13.5px description lines (`.d`) and optional mono hostname lines (`.h`). Kinds: `people` (accent), default (white), `async` (teal), `ai` (violet), `vendor`, `planned` (dashed, muted text). Grid: 4 columns × 265px with 20px gutters (x = 40, 325, 610, 895), or 3 × 360px for wide rows.
- **Edges**: `.edge` solid ink = request/response; `.edge.async` teal dashed `7 4` = event/queue/workflow; `.edge.public` accent = public delivery; `.edge.rail` dotted grey = direct path that bypasses layers (drawn around the outside, with a rotated label). Each class has its own arrowhead marker. Edge labels `.elabel` 13px, `.async` labels teal.
- **Numbered dots** (`g.step`: accent circle r=12 + white bold number) sit on box corners and are narrated in the figcaption as one object's journey.
- Legend row under the SVG: swatches for each edge class and the dot.

## 5. Flow diagram conventions (Mermaid sequence, pre-rendered)

Per flow:
```html
<article class="panel flow" id="f-key">
  <div class="flow-head"><h3>A · Verb phrase</h3><span class="fnum">service · service · provider</span></div>
  <p>2 to 3 sentences: the design point of this flow (what makes it safe/correct), not a restatement of the arrows.</p>
  <div class="seq"><svg id="seq-f-key" ...static mermaid SVG...></svg></div>
  <div class="chips">services (svc) · providers (ext) · pending (warn) · events and libs (plain)</div>
</article>
```
Diagram rules:
- One diagram per user action; letter-coded A, B, C… matching the flow index. 6 to 19 numbered steps (`autonumber`). Split longer flows into phases (A1, A2).
- Leftmost participant is the person (`actor`), then the client app, then services in call order, then outside providers / infrastructure on the right.
- Arrow labels are the real operation, invoke or event names, followed by the essential arguments or effect in plain words. Responses dashed (`-->>`). Events carry their CAPITALISED name.
- `rect`/`loop`/`alt`/`par` blocks for retries, schedules and alternatives; notes (`Note over`) sparingly for invariants or pending items.
- Mermaid config: `theme: base`, `look: neo`, fontFamily IBM Plex Sans, font size 16. Theme variables: actorBkg `#eef2f7`, actorBorder `#8e9aad`, actorLineColor `#b3bccb`, signalColor `#2c323d`, text `#14161a`, noteBkg `#fff4d6`, noteBorder `#d9a93a`, labelBoxBkg `#e6ebf2`, sequence number fill `#2c323d` with white digits.
- **Use `sequence.wrap: false` and break labels yourself.** With `wrap: true` mermaid hyphen-splits long identifiers (`createLiveTranscriptionSe-` / `ssion`). Wrap labels at about 22 characters on spaces only, and allow a break before `(` in `opName(args)`; never split inside a token. Participant names `x-service` render as `x-<br/>service`. Settings that worked: `mirrorActors: false, width: 112, height: 58, actorMargin: 18, messageMargin: 28`.
- **Size budget:** at most 7 participants per diagram (drop the API gateway participant; draw app → service directly, as the reference does). Keep the viewBox width ≤ ~1360 so the diagram renders at scale ≥ 0.8. Give each SVG inline `max-width: <natural>px; min-width: min(w, max(1000, 0.8·w))px` so small diagrams are not upscaled and wide ones scroll inside `.seq` rather than shrinking text. A wider flows container (`#flows.wrap { max-width: 1400px }`) lets most diagrams render at natural size on a 1440px screen.
- **Notes:** never `Note over` a person (`actor`) participant (mermaid mis-sizes the box). Set `noteFontSize` equal to `messageFontSize` (16) and wrap note text at ~26 characters; with a smaller note font or longer lines the text spills past the note box.
- SVG gets `id="seq-<flow-id>"`, `width=100%`, `aria-label="Sequence diagram: <title>"`.
- **Prefix shared SVG ids per diagram.** Mermaid emits `id="drop-shadow"` in every SVG and references it with `filter="url(#drop-shadow)"`; with many diagrams the first definition wins, and if that SVG is ever hidden every actor box disappears. Rewrite to `<svg-id>-drop-shadow`.
- **Label halo:** `#flows .seq svg text.messageText, … text.loopText, … text.labelText { paint-order: stroke; stroke: #fff; stroke-width: 5px; stroke-linejoin: round }` so lifelines never cut through self-message labels.
- Build pipeline that worked: author each flow as data (`(kind, from, to, label)`, plus `note`/`loop`/`opt`/`alt` blocks) → generate mermaid text → a local page loads mermaid 11 from the CDN, **awaits `document.fonts.load()` for the body font before any `mermaid.render`** (mermaid measures text in the browser), renders each diagram and POSTs the SVG to a tiny local HTTP server → post-process in a script → inline into the page. Headless Chrome drives the render page; it does not exit on its own, so kill it once the server has received a `done` POST.
- Build checks: no mermaid error SVGs; rendered message lines == authored messages per diagram (lines appear in document order); no `messageText` line ending in a letter + `-`; every operation, event and frame name in the labels exists verbatim in the source design; every event arrow starts at that event's documented producer or at the bus.

Optional extensions that keep the look (used successfully): colour each participant box by owning service with an inline `style` on `rect.actor` keyed by its `name` attribute (one fixed alias per service in every diagram, same palette as the map boxes and the service chips, with a colour key above the flows); style bus events teal dashed (`-)` arrows) and realtime frames or pushes accent dotted (`--)` arrows) with their own arrowhead markers, both in the legend.

## 6. Service card conventions

```html
<article class="panel card">
  <div class="top"><span class="name">repo-name</span><span class="tag live">badge</span></div>
  <p class="role">One sentence: what it owns end to end.</p>
  <dl class="kv"><dt>Tables</dt><dd>…</dd><dt>Lambdas</dt><dd>…</dd><dt>Emits</dt><dd>…</dd><dt>Consumes</dt><dd>…</dd><dt>Outside</dt><dd>…</dd></dl>
</article>
```
The badge is a count or status (e.g. query/mutation counts, "platform", "web app"). Keep `dd` to one or two lines; list names, not prose.

## 7. Tone

Terse, plain English, present tense, no marketing. Lede ≤ 2 sentences. Flow paragraph ≤ 3 sentences and explains *why* (safety, idempotency, privacy), with pending items stated plainly. Numbers are concrete. Status words: live / partial / planned (or the project's equivalent). Names in `<code>` or mono.

## 8. Build checklist

1. Section order and `sec-num`s match §2; TOC links are bare anchors.
2. Hero stats are countable from sources (script the counts).
3. Every deployable repo has a card; supporting repos in `.support`.
4. Every flow: id, letter, index entry, paragraph, static SVG, chips. Diagrams authored = diagrams rendered; no error SVGs.
5. Every arrow label exists verbatim in the source design (script a name check over operations, events, frames).
6. Colours: same service = same colour in map, flows and chips.
7. Screenshot the map and several flows at desktop width; fix clipping, overlaps, hyphen-split identifiers.
8. Console clean; only Google Fonts loads from the network.
9. Grep for leftover names and terms from any template or reference source (case-insensitive).
10. Narrow viewport: no horizontal page scroll; figures scroll inside `.scroll-x`.

## 9. Keeping a published page in sync with a revised design

- Keep the generator inputs (flow data, section content, map layout) in a build directory, so a revision means editing data and re-running render, post-process and page build, never hand-editing the HTML.
- On a new design revision: diff the source doc between the two revisions (`git diff <old> <new> -- <doc>`) and read the revision log; then update the revision/date in the kicker, decisions lede and footer; recount the hero stats with the same scripts (operations, events, models, repos); and re-run the name check and the event-producer check against the new doc.
- New components (a new repo, a new public endpoint) go in every place they appear: service or supporting card, system map box and edges, environments table, technology grid, rollout, decisions. Option comparisons (for example checkout options) use a small `table.tbl` with a status `.tag` in the last column.
- A new service usually needs a new row in the map's services grid. Keep everything below the services band inside one `<g transform="translate(0,dy)">` (or generate coordinates from a row count) so adding a row is one offset, then fix only what crosses bands: band heights, rails, the numbered dots and the viewBox height. Pick the new service's colour so it is distinguishable from its grid neighbours, and add it to the flows legend key.
- When ownership moves between services (a responsibility split out into a new service), re-check every flow where the old owner appears, not only the obvious ones: renamed operations and events also show up in push/notification, lapse, moderation, erasure and deep-link flows.
- Decisions recorded outside the doc (for example relayed by the owner) can be shown as decided; say where they came from in the report.
