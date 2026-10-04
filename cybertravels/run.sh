#!/usr/bin/env bash
# Run CyberTravels locally. 127.0.0.1 only, and that is not an accident:
# this application is deliberately vulnerable. See LABELS.md.
set -euo pipefail
cd "$(dirname "$0")/.."

# This file ships from A0.1 and `main.py` does not arrive until A1.1, so a
# reader who materialised an early checkpoint and ran the obvious command used
# to get a uvicorn import error about a module they had never heard of. Say
# which lesson builds it instead.
if [ ! -f cybertravels/main.py ]; then
  echo "cybertravels/main.py does not exist at this checkpoint yet." >&2
  echo "The web app is built in lesson A1.1. To get a tree that serves:" >&2
  echo "  python3 scripts/checkpoint.py --at A1.1 --out work/cybertravels" >&2
  echo "Everything before A1.1 is libraries you can import and test." >&2
  exit 1
fi

python3 -m pip install -q -r cybertravels/requirements.txt
exec python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000 "$@"
