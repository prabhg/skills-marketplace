#!/usr/bin/env python3
"""Screenshot one section or flow of the page at desktop width, isolated, for visual review.

usage: shot.py OUT.html ELEMENT_ID PNG [--width 1440] [--height 1800] [--chrome PATH]

Writes a sibling copy OUT.html.verify.html with a small script that hides everything except the
section/flow with ELEMENT_ID (the real page is untouched), then takes a headless Chrome screenshot.
Read the PNG and LOOK at it: clipped labels, overlaps, unreadable sizes, blank boxes.
Note: the in-app browser pane cannot inspect file:// pages; to check the console or DOM there,
serve the folder with `python3 -m http.server --bind 127.0.0.1 <port>` and open http://127.0.0.1:<port>/...
"""
import argparse, os, shutil, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import find_chrome

JS = '''<script>(function(){var id=location.hash.slice(1);if(!id)return;document.documentElement.style.scrollBehavior='auto';
var t=document.getElementById(id);if(!t)return;['header.hero','nav.toc'].forEach(function(q){var e=document.querySelector(q);if(e)e.style.display='none';});
document.querySelectorAll('main > section').forEach(function(s){if(!s.contains(t))s.style.display='none';});
if(t.classList.contains('flow')){document.querySelectorAll('article.flow, .flow-index, #flows .sec-head, .legend-block').forEach(function(a){if(a!==t)a.style.display='none';});}
window.scrollTo(0,0);})();</script>'''

ap = argparse.ArgumentParser()
ap.add_argument('page'); ap.add_argument('id'); ap.add_argument('png')
ap.add_argument('--width', type=int, default=1440); ap.add_argument('--height', type=int, default=1800)
ap.add_argument('--chrome')
a = ap.parse_args()
v = os.path.abspath(a.page) + '.verify.html'
open(v, 'w').write(open(a.page).read().replace('</body>', JS + '</body>'))
png = os.path.abspath(a.png)
if os.path.exists(png):
    os.remove(png)
prof = tempfile.mkdtemp(prefix='archdoc-shot-')
p = subprocess.Popen([find_chrome(a.chrome), '--headless=new', '--disable-gpu', '--no-first-run', '--hide-scrollbars',
                      f'--user-data-dir={prof}', '--virtual-time-budget=6000', f'--window-size={a.width},{a.height}',
                      f'--screenshot={png}', f'file://{v}#{a.id}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(120):  # Chrome may not exit after screenshotting
    if os.path.exists(png) and os.path.getsize(png) > 0:
        time.sleep(1)
        break
    time.sleep(0.5)
p.kill()
shutil.rmtree(prof, ignore_errors=True)
print(png if os.path.exists(png) else 'screenshot failed')
