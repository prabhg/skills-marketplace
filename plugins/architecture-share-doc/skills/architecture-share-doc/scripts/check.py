#!/usr/bin/env python3
"""Check a finished share page.

usage: check.py OUT.html flows.json [--source DESIGN.md] [--forbid term ...] [--prefixes user,chat,...]

Reports:
- diagrams: sequence SVGs authored (flows.json) vs present in the page; map/figure SVG count;
  mermaid error SVGs; leftover <!--SEQ:--> markers or {{PLACEHOLDER}} tokens.
- forbidden terms (case-insensitive; e.g. names from a previous project's doc), with context.
- names used in flow labels: camelCase operations (optionally only those starting with --prefixes),
  UPPER_SNAKE events/codes and PascalCase models. With --source, lists the ones NOT found verbatim
  in the design doc -> each must be fixed or justified.
- event producers: for 'event' steps whose label starts with an UPPER_SNAKE name, prints sender -> event
  pairs so they can be compared with the source's event catalogue.
Exit code 1 on any hard failure (missing diagrams, errors, placeholders, forbidden terms, unknown names).
"""
import argparse, json, re, sys

ap = argparse.ArgumentParser()
ap.add_argument('page')
ap.add_argument('flows')
ap.add_argument('--source')
ap.add_argument('--forbid', nargs='*', default=[])
ap.add_argument('--prefixes', default='')
a = ap.parse_args()

html = open(a.page).read()
data = json.load(open(a.flows))
fail = False

authored = len(data['flows'])
present = len(re.findall(r'aria-roledescription="sequence"', html))
other = len(re.findall(r'<svg[^>]*role="img"', html))
print(f'sequence diagrams: authored {authored}, in page {present}; other figures (role=img): {other}')
fail |= authored != present
for pat, what in ((r'aria-roledescription="error"|Syntax error in text', 'mermaid error'),
                  (r'<!--SEQ:', 'unreplaced SEQ marker'), (r'\{\{[^{}\n]{1,300}\}\}', 'template placeholder')):
    n = len(re.findall(pat, html))
    if n:
        print(f'FAIL {what}: {n}')
        fail = True

for term in a.forbid:
    hits = [html[max(0, m.start() - 40):m.end() + 30].replace('\n', ' ') for m in re.finditer(re.escape(term), html, re.I)]
    hits = [h for h in hits if 'EventListener' not in h]
    if hits:
        fail = True
        print(f'FAIL forbidden "{term}": {len(hits)}')
        for h in hits[:5]:
            print('   ...', h)

labels, producers = [], []


def walk(steps):
    for s in steps:
        if s[0] in ('call', 'reply', 'event', 'frame', 'push', 'self'):
            labels.append(s[3])
            m = re.match(r'([A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+)', s[3])
            if s[0] == 'event' and m:
                producers.append((s[1], m.group(1)))
        elif s[0] == 'note':
            labels.append(s[2])
        elif s[0] in ('loop', 'opt', 'critical'):
            walk(s[2])
        elif s[0] in ('alt', 'par'):
            for _, inner in s[1]:
                walk(inner)


for f in data['flows']:
    walk(f['steps'])
prefixes = [p for p in a.prefixes.split(',') if p]
op_re = (r'\b(?:' + '|'.join(prefixes) + r')[A-Z][A-Za-z0-9]+\b') if prefixes else r'\b[a-z]+(?:[A-Z][a-z0-9]+){2,}\b'
names = {
    'operations': set(re.findall(op_re, ' '.join(labels))),
    'events/codes': set(re.findall(r'\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b', ' '.join(labels))),
    'models': set(re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z0-9]+)+\b', ' '.join(labels))),
}
src = open(a.source).read() if a.source else None
for k, v in names.items():
    line = f'{k}: {len(v)}'
    if src is not None:
        miss = sorted(x for x in v if x not in src)
        line += f', not in source: {miss}'
        fail |= bool(miss)
    else:
        line += ': ' + ', '.join(sorted(v))
    print(line)
print('event senders (check against the source catalogue; the bus is always fine):')
for snd, ev in sorted(set(producers)):
    print(f'   {snd:8s} {ev}')
print('RESULT:', 'FAIL' if fail else 'OK')
sys.exit(1 if fail else 0)
