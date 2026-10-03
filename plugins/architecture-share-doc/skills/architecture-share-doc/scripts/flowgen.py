#!/usr/bin/env python3
"""Turn flow data (JSON) into mermaid sequenceDiagram sources.

usage: flowgen.py flows.json OUT_DIR
writes OUT_DIR/diagrams.json  [{id, code}]   (input for render.py)
       OUT_DIR/kinds.json     {svg_id: [kind per message]}  (input for postprocess.py)

Flow JSON shape (see SKILL.md):
{
  "groups": {"person": ["#fdeceb", "#c42f28"], "app": ["#ffffff", "#14161a"], ...},
  "participants": {"MB": {"name": "Member", "group": "person"}, "US": {"name": "user-service", "group": "user"}, ...},
  "flows": [{
     "id": "f-signin", "letter": "A", "title": "...", "parts": ["MB", "APP", "US"],
     "names": {"MB": "Requester"},          # optional per-flow display-name override
     "ww": 22,                               # optional label wrap width (chars)
     "steps": [
        ["call", "MB", "APP", "label"],      # kinds: call reply event frame push self
        ["note", "over APP,US", "text"],     # never over a person participant
        ["loop", "label", [steps]], ["opt", "label", [steps]],
        ["alt", [["branch label", [steps]], ["other branch", [steps]]]]
     ]}]
}
Person-group participants render as mermaid `actor`; everything else as `participant`.
"""
import json, os, re, sys

ARROW = {'call': '->>', 'reply': '-->>', 'event': '-)', 'frame': '--)', 'push': '--)', 'self': '->>'}
BAD = re.compile(r'[#{}<>]')  # these break mermaid message parsing


def wrap(text, width=22):
    """Wrap on spaces only; allow a break before '(' in long opName(args). Never splits a token."""
    text = text.replace(';', ',')  # ';' ends a mermaid statement
    if BAD.search(text):
        raise ValueError('label has a character mermaid cannot take (# { } < >): ' + text)
    pieces = []
    for w in text.split(' '):
        if '(' in w and not w.startswith('(') and len(w) > width:
            a, b = w.split('(', 1)
            pieces += [(a, False), ('(' + b, True)]
        else:
            pieces.append((w, False))
    lines, cur = [], ''
    for w, glue in pieces:
        if not cur:
            cur = w
            continue
        cand = cur + ('' if glue else ' ') + w
        if len(cand) <= width:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return '<br/>'.join(lines)


def participant_label(name):
    if name.endswith('-service'):
        return name[:-len('service')] + '<br/>service'
    return wrap(name, 13)


def gen(flow, registry):
    out = ['sequenceDiagram', '  autonumber']
    names = flow.get('names', {})
    for a in flow['parts']:
        p = registry[a]
        kw = 'actor' if p['group'] == 'person' else 'participant'
        out.append(f'  {kw} {a} as {participant_label(names.get(a, p["name"]))}')
    kinds = []
    ww = flow.get('ww', 22)
    persons = {a for a in flow['parts'] if registry[a]['group'] == 'person'}

    def emit(steps, ind='  '):
        for s in steps:
            t = s[0]
            if t in ARROW:
                _, frm, to, label = s[:4]
                if frm not in flow['parts'] or to not in flow['parts']:
                    raise ValueError(f"{flow['id']}: participant not in parts: {s}")
                out.append(f'{ind}{frm}{ARROW[t]}{to}: {wrap(label, ww)}')
                kinds.append(t)
            elif t == 'note':
                _, where, text = s
                if any(p in persons for p in re.split(r'[ ,]+', where)):
                    raise ValueError(f"{flow['id']}: note over a person participant mis-renders: {where}")
                out.append(f'{ind}Note {where}: {wrap(text, 26)}')
            elif t in ('loop', 'opt', 'critical'):
                out.append(f'{ind}{t} {wrap(s[1], 60)}')
                emit(s[2], ind + '  ')
                out.append(f'{ind}end')
            elif t in ('alt', 'par'):
                for i, (label, inner) in enumerate(s[1]):
                    kw = t if i == 0 else ('else' if t == 'alt' else 'and')
                    out.append(f'{ind}{kw} {wrap(label, 60)}')
                    emit(inner, ind + '  ')
                out.append(f'{ind}end')
            else:
                raise ValueError(f'unknown step kind: {s}')
    emit(flow['steps'])
    return '\n'.join(out), kinds


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    data = json.load(open(src))
    os.makedirs(outdir, exist_ok=True)
    ds, kinds = [], {}
    for f in data['flows']:
        if len(f['parts']) > 7:
            print(f"warning: {f['id']} has {len(f['parts'])} participants; over 7 usually renders too wide, split into phases", file=sys.stderr)
        code, k = gen(f, data['participants'])
        sid = 'seq-' + f['id']
        ds.append({'id': sid, 'code': code})
        kinds[sid] = k
    json.dump(ds, open(os.path.join(outdir, 'diagrams.json'), 'w'), indent=1)
    json.dump(kinds, open(os.path.join(outdir, 'kinds.json'), 'w'))
    print(f'{len(ds)} diagrams -> {outdir}/diagrams.json')


if __name__ == '__main__':
    main()
