#!/bin/sh
# Full pipeline: flows.json + filled page -> single self-contained HTML.
# usage: build.sh flows.json page.html OUT.html [WORK_DIR]
# WORK_DIR defaults to a fresh temp dir (never inside a repo). Needs python3, Chrome, network (jsdelivr, Google Fonts).
set -e
S="$(cd "$(dirname "$0")" && pwd)"
FLOWS="$1"; PAGE="$2"; OUT="$3"; WORK="${4:-$(mktemp -d -t archdoc-build)}"
[ -n "$OUT" ] || { echo "usage: build.sh flows.json page.html OUT.html [WORK_DIR]"; exit 2; }
echo "work dir: $WORK"
python3 "$S/flowgen.py" "$FLOWS" "$WORK"
python3 "$S/render.py" "$WORK"
python3 "$S/postprocess.py" "$FLOWS" "$WORK"
python3 "$S/assemble.py" "$PAGE" "$FLOWS" "$WORK" "$OUT"
