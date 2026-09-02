#!/usr/bin/env bash
# Validate the CyberTravels bookings spec with openapi-spec-validator, then run
# the security audit the validator does not do.
#
#   ./run.sh
#
# Needs: python3 and outbound HTTPS to PyPI.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
mkdir -p "$WORK"

[ -d "$WORK/venv" ] || python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" install --quiet --upgrade pip
"$WORK/venv/bin/pip" install --quiet openapi-spec-validator

"$WORK/venv/bin/python" "$HERE/audit.py" "$HERE/bookings-openapi.yaml"
