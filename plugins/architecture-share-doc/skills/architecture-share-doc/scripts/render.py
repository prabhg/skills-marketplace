#!/usr/bin/env python3
"""Pre-render mermaid diagrams to static SVG with headless Chrome.

usage: render.py WORK_DIR [--chrome PATH] [--port 8765] [--timeout 180]
expects WORK_DIR/diagrams.json (from flowgen.py); writes WORK_DIR/raw/<id>.svg and WORK_DIR/raw/_done.json

How it works: a throwaway local HTTP server serves render.html + diagrams.json from WORK_DIR.
The page loads mermaid 11 from cdn.jsdelivr.net, waits for the IBM Plex fonts (mermaid measures text
in the browser, so the font must be loaded first), renders each diagram and POSTs the SVG back.
Headless Chrome never exits on its own, so it is killed once '/done' arrives.
Needs: python3, Google Chrome (or Chromium/Brave), network access to jsdelivr and Google Fonts.
"""
import argparse, http.server, json, os, shutil, subprocess, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
CHROMES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    'google-chrome', 'chromium', 'chromium-browser',
]


def find_chrome(explicit):
    for c in ([explicit] if explicit else []) + CHROMES:
        if c and (os.path.exists(c) or shutil.which(c)):
            return shutil.which(c) or c
    sys.exit('No Chrome/Chromium found; pass --chrome PATH')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('work')
    ap.add_argument('--chrome')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--timeout', type=int, default=180)
    a = ap.parse_args()
    work = os.path.abspath(a.work)
    raw = os.path.join(work, 'raw')
    os.makedirs(raw, exist_ok=True)
    for f in os.listdir(raw):
        os.remove(os.path.join(raw, f))
    shutil.copy(os.path.join(HERE, 'render.html'), os.path.join(work, 'render.html'))

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(s, *x, **k):
            super().__init__(*x, directory=work, **k)

        def log_message(s, *x):
            pass

        def do_POST(s):
            body = s.rfile.read(int(s.headers.get('Content-Length', 0))).decode('utf-8')
            name = '_done.json' if s.path == '/done' else s.path[len('/save/'):]
            with open(os.path.join(raw, os.path.basename(name)), 'w') as fh:
                fh.write(body)
            s.send_response(200)
            s.end_headers()
            s.wfile.write(b'ok')

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', a.port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    profile = tempfile.mkdtemp(prefix='archdoc-chrome-')
    chrome = subprocess.Popen([find_chrome(a.chrome), '--headless=new', '--disable-gpu', '--no-first-run',
                               f'--user-data-dir={profile}', '--window-size=1400,1000',
                               f'http://127.0.0.1:{a.port}/render.html'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    done = os.path.join(raw, '_done.json')
    t0 = time.time()
    try:
        while not os.path.exists(done) and time.time() - t0 < a.timeout:
            time.sleep(0.5)
    finally:
        chrome.kill()
        srv.shutdown()
        shutil.rmtree(profile, ignore_errors=True)
    if not os.path.exists(done):
        sys.exit('render timed out (no network to jsdelivr? fonts blocked?)')
    log = json.load(open(done))
    bad = [d for d in log if not d.get('ok')]
    print(f'rendered {len(log) - len(bad)}/{len(log)}')
    for d in bad:
        print('FAILED', d)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
