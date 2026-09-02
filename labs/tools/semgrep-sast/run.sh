#!/usr/bin/env bash
# Semgrep against a real pull request from the CyberTravels Coding Agent.
#
# B1.5 argues that deterministic SAST and LLM-driven SAST find different things
# and that you want both. This script establishes the first half of that claim
# empirically: it installs Semgrep, runs it against booking.py at two ruleset
# widths, and prints what each width found and what it did not.
#
#   ./run.sh
#
# Needs: python3 and outbound HTTPS to PyPI and the Semgrep registry.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
mkdir -p "$WORK"

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }

say "1 · install"
[ -d "$WORK/venv" ] || python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" install --quiet --upgrade pip
"$WORK/venv/bin/pip" install --quiet semgrep
"$WORK/venv/bin/semgrep" --version

report() {
  python3 - "$1" "$2" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
rs = sorted(d["results"], key=lambda r: r["start"]["line"])
print(f"  {sys.argv[2]}: {len(rs)} finding(s)")
for r in rs:
    print(f"    line {r['start']['line']:>3}  {r['extra']['severity']:<8}"
          f"{r['check_id'].split('.')[-1]}")
PY
}

say "2 · the default Python pack"
"$WORK/venv/bin/semgrep" --config=p/python --config=p/secrets \
  --json --quiet "$HERE/booking.py" > "$WORK/narrow.json" 2>/dev/null
report "$WORK/narrow.json" "p/python + p/secrets"

say "3 · seven packs — everything a team would plausibly turn on"
"$WORK/venv/bin/semgrep" \
  --config=p/default --config=p/python --config=p/security-audit \
  --config=p/sql-injection --config=p/command-injection \
  --config=p/secrets --config=p/owasp-top-ten \
  --json --quiet "$HERE/booking.py" > "$WORK/wide.json" 2>/dev/null
report "$WORK/wide.json" "seven packs"

say "4 · what neither width found"
python3 - "$WORK/wide.json" "$HERE/booking.py" <<'PY'
import json, sys
found = {r["start"]["line"] for r in json.load(open(sys.argv[1]))["results"]}
src = open(sys.argv[2]).read().splitlines()

# Two defects that are in the file and are not in any ruleset's output. The
# first is lexical and a rule could in principle catch it; the second is not
# expressible as a pattern at all, which is the entire argument for the second
# generation of the auditor.
KNOWN = [
    (22, "a live-looking API key assigned to a module-level constant"),
    (7,  "find_booking takes a reference from the caller and performs no "
         "authorisation check of any kind — the Workflow Agent calls it with "
         "payments scope attached"),
]
for line, what in KNOWN:
    mark = "MISSED" if line not in found else "found"
    print(f"  line {line:>3}  {mark:<7}{what}")
    print(f"           {src[line-1].strip()[:70]}")
PY

say "done"
