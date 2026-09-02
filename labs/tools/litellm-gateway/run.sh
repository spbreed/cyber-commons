#!/usr/bin/env bash
# LiteLLM as the CyberTravels AI gateway.
#
# A3.7 argues that once you run more than a couple of agents, the controls
# collapse into one choke point. This script stands one up and tests what it
# does and does not enforce — including the failure mode that matters, which is
# a gateway deployed without the database its key checks depend on.
#
#   ./run.sh
#
# Needs: python3 and outbound HTTPS to PyPI. No model API key: the config uses
# LiteLLM's mock_response so the routing and policy behaviour is exercised
# without spending anything. Set ANTHROPIC_API_KEY and delete the mock_response
# lines to point it at a real model.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
mkdir -p "$WORK"
G=http://localhost:4000

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
nc() { curl -s --noproxy '*' "$@"; }

say "1 · install"
[ -d "$WORK/venv" ] || python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" install --quiet --upgrade pip
"$WORK/venv/bin/pip" install --quiet "litellm[proxy]"
"$WORK/venv/bin/litellm" --version 2>&1 | tail -1

say "2 · start the gateway"
if [ "$(nc -o /dev/null -w '%{http_code}' $G/health/liveliness || true)" != "200" ]; then
  ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-not-used-mock-response}" \
    "$WORK/venv/bin/litellm" --config "$HERE/gateway.yaml" --port 4000 \
    > "$WORK/litellm.log" 2>&1 &
  trap 'kill %1 2>/dev/null || true' EXIT
fi
for _ in $(seq 1 30); do
  [ "$(nc -o /dev/null -w '%{http_code}' $G/health/liveliness)" = "200" ] && break
  sleep 2
done
echo "listening on $G"

ask() {   # $1 label, $2 auth header (or ""), $3 model
  printf '  %-34s' "$1"
  if [ -n "$2" ]; then
    nc $G/v1/chat/completions -H 'content-type: application/json' \
      -H "Authorization: Bearer $2" \
      -d "{\"model\":\"$3\",\"messages\":[{\"role\":\"user\",\"content\":\"3 days in Lisbon?\"}]}" \
      -w ' [HTTP %{http_code}]\n' | head -c 260
  else
    nc $G/v1/chat/completions -H 'content-type: application/json' \
      -d "{\"model\":\"$3\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}" \
      -w ' [HTTP %{http_code}]\n' | head -c 260
  fi
}

say "3 · what the gateway enforces"
ask "master key, model on the list"   sk-cybertravels-master advisor-model
ask "master key, model NOT on it"     sk-cybertravels-master gpt-4o

say "4 · what it does not, without its database"
ask "a guessed key"                   sk-guessed             advisor-model
ask "no key at all"                   ""                     advisor-model

cat <<'NOTE'

  The model allow-list holds with nothing but a config file: a request for a
  model the file does not name is refused with a 400, whoever asked.

  Key checking is different. LiteLLM's virtual keys — per-agent keys with their
  own model list, budget and rate limit — live in Postgres, and with no
  DATABASE_URL configured every key that is not the master key returns
  "No connected db" rather than a refusal, and a request with no key at all
  returns a 500. Nothing in the startup log calls that out.

  Which is the general shape of the thing: a gateway is a control surface, not
  a control. It enforces what you configured, and it fails open on the parts
  you did not, in ways its own health check reports as healthy.
NOTE
