#!/usr/bin/env python3
"""Inject pre-rendered sequence SVGs into the page.

usage: assemble.py PAGE_IN.html flows.json WORK_DIR OUT.html

PAGE_IN.html is your filled-in copy of assets/template.html. Wherever it contains
<!--SEQ:f-some-id-->, the processed SVG WORK_DIR/svg/seq-f-some-id.svg is inserted with:
- aria-label "Sequence diagram: <letter> · <title>" (from flows.json)
- inline max-width = natural width (small diagrams are never upscaled) and
  min-width = min(w, max(1000, 0.8·w)) (wide diagrams scroll inside .seq instead of shrinking text).
Fails if a marker has no SVG or a flow has no marker.
"""
import json, os, re, sys
from html import escape


def main():
    page_in, flows_json, work, out = sys.argv[1:5]
    page = open(page_in).read()
    flows = {f['id']: f for f in json.load(open(flows_json))['flows']}
    used, errs = set(), []

    def sub(m):
        fid = m.group(1)
        p = os.path.join(work, 'svg', f'seq-{fid}.svg')
        if not os.path.exists(p):
            errs.append(f'no SVG for marker {fid}')
            return m.group(0)
        used.add(fid)
        svg = open(p).read()
        w = float(re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+)', svg).group(1))
        mn = int(min(w, max(1000, round(w * 0.8))))
        svg = re.sub(r'style="max-width: [\d.]+px;"', f'style="max-width:{w:.0f}px;min-width:{mn}px"', svg, count=1)
        f = flows.get(fid, {})
        label = escape(f"Sequence diagram: {f.get('letter', '')} · {f.get('title', fid)}")
        return svg.replace('<svg ', f'<svg aria-label="{label}" ', 1)

    page = re.sub(r'<!--SEQ:([A-Za-z0-9_-]+)-->', sub, page)
    for fid in flows:
        if fid not in used:
            errs.append(f'flow {fid} has no <!--SEQ:{fid}--> marker in the page')
    open(out, 'w').write(page)
    print(f'wrote {out} ({os.path.getsize(out):,} bytes), {len(used)} diagrams inserted')
    for e in errs:
        print('ERROR', e)
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
