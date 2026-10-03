#!/usr/bin/env python3
"""Post-process rendered SVGs: per-diagram id fix, per-service colours, event/frame arrow styling, checks.

usage: postprocess.py flows.json WORK_DIR
reads WORK_DIR/raw/<id>.svg + WORK_DIR/kinds.json, writes WORK_DIR/svg/<id>.svg, prints width + problems.
Exit code 1 if any diagram has a problem.

Fixes applied (each one was a real failure):
- mermaid emits id="drop-shadow" in every SVG; with many diagrams on one page the first definition wins,
  and if that SVG is hidden every actor box goes blank. Renamed to <svg-id>-drop-shadow.
- participant boxes get an inline fill/stroke from the participant's group, so the same service has the
  same colour in every diagram (inline style beats mermaid's #id-scoped CSS).
- 'event' arrows -> teal dashed, 'frame'/'push' arrows -> accent dotted, each with its own arrowhead.
Checks: mermaid error SVG; rendered message lines == authored messages; label lines ending in a
letter + '-' (mermaid hyphen-split an identifier); viewBox width over 1360 (renders below 0.8 scale).
"""
import json, os, re, sys

TEAL, FRAME = '#0c7a69', '#c42f28'


def process(svg, kinds, sid, participants, groups):
    errs = []
    if 'aria-roledescription="error"' in svg or 'Syntax error' in svg:
        errs.append('mermaid error SVG')
    svg = svg.replace('id="drop-shadow"', f'id="{sid}-drop-shadow"').replace('url(#drop-shadow)', f'url(#{sid}-drop-shadow)')

    def rect_sub(m):
        tag = m.group(0)
        name = re.search(r'name="([^"]+)"', tag).group(1)
        fill, stroke = groups[participants[name]['group']]
        return tag[:-1] + f' style="fill:{fill};stroke:{stroke};stroke-width:1.3">'
    svg = re.sub(r'<rect[^>]*class="actor actor-top"[^>]*>', rect_sub, svg)

    lines = list(re.finditer(r'<(line|path)[^>]*class="messageLine[01]"[^>]*>', svg))
    if len(lines) != len(kinds):
        errs.append(f'messages rendered {len(lines)} != authored {len(kinds)}')
    out, last = [], 0
    for m, k in zip(lines, kinds):
        tag = m.group(0)
        if k == 'event':
            tag = re.sub(r'marker-end="url\([^)]+\)"', f'marker-end="url(#{sid}-evt-head)"', tag)
            tag = re.sub(r'style="[^"]*"', f'style="fill:none;stroke:{TEAL};stroke-width:2;stroke-dasharray:7,4"', tag)
        elif k in ('frame', 'push'):
            tag = re.sub(r'marker-end="url\([^)]+\)"', f'marker-end="url(#{sid}-frm-head)"', tag)
            tag = re.sub(r'style="[^"]*"', f'style="fill:none;stroke:{FRAME};stroke-width:2;stroke-dasharray:2,4;stroke-linecap:round"', tag)
        out += [svg[last:m.start()], tag]
        last = m.end()
    out.append(svg[last:])
    svg = ''.join(out)
    marks = ''.join(
        f'<marker id="{sid}-{n}-head" refX="7.9" refY="5" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" orient="auto">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" style="fill:{c};stroke:{c}"></path></marker>' for n, c in (('evt', TEAL), ('frm', FRAME)))
    if '<defs>' in svg:
        svg = svg.replace('<defs>', '<defs>' + marks, 1)
    else:
        svg = re.sub(r'(<svg[^>]*>)', r'\1<defs>' + marks + '</defs>', svg, count=1)
    for t in re.findall(r'class="messageText"[^>]*>([^<]*)</text>', svg):
        if re.search(r'[A-Za-z]-$', t.strip()):
            errs.append('hyphen-split label: ' + t)
    w = float(re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+)', svg).group(1))
    if w > 1360:
        errs.append(f'wide ({w:.0f}px): shorten labels or split into phases')
    return svg, errs, w


def main():
    data = json.load(open(sys.argv[1]))
    work = sys.argv[2]
    kinds = json.load(open(os.path.join(work, 'kinds.json')))
    os.makedirs(os.path.join(work, 'svg'), exist_ok=True)
    problems = 0
    for sid, k in kinds.items():
        p = os.path.join(work, 'raw', sid + '.svg')
        if not os.path.exists(p):
            print(f'{sid:30s} MISSING')
            problems += 1
            continue
        svg, errs, w = process(open(p).read(), k, sid, data['participants'], data['groups'])
        open(os.path.join(work, 'svg', sid + '.svg'), 'w').write(svg)
        hard = [e for e in errs if not e.startswith('wide')]
        problems += bool(hard)
        print(f'{sid:30s} w={w:6.0f} msgs={len(k):2d} {"; ".join(errs)}')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
