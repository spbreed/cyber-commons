#!/usr/bin/env bash
# Run CyberTravels locally. 127.0.0.1 only, and that is not an accident:
# this application is deliberately vulnerable. See LABELS.md.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r cybertravels/requirements.txt
exec python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000 "$@"
