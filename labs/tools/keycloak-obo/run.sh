#!/usr/bin/env bash
# Keycloak, on-behalf-of, and RFC 8705 certificate-bound tokens — for real.
#
# The notebooks model these protocols in the standard library so they run
# anywhere with the internet switched off. This script does the opposite: it
# downloads Keycloak, starts it, configures a realm, and runs the exchanges
# against it, so the claims in A2.3 are checked against a product rather than
# against a model of one.
#
#   ./run.sh          download, start, configure, and run every check
#
# Needs: Java 21+, openssl, curl, ~1GB of disk and outbound HTTPS to GitHub.
# Everything lands in ./work/, which is gitignored. Nothing here is a secret:
# the passwords are "admin" and the certificates are minted on the spot and
# thrown away.
set -euo pipefail

KC_VERSION=26.0.7
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
PKI="$WORK/pki"
KC="$WORK/keycloak-$KC_VERSION"
mkdir -p "$WORK" "$PKI"

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
nc() { curl -s --noproxy '*' "$@"; }

# --------------------------------------------------------------------------
say "1 · Keycloak $KC_VERSION"
if [ ! -d "$KC" ]; then
  curl -sSL -o "$WORK/keycloak.zip" \
    "https://github.com/keycloak/keycloak/releases/download/$KC_VERSION/keycloak-$KC_VERSION.zip"
  unzip -q -d "$WORK" "$WORK/keycloak.zip"
fi
echo "unpacked to $KC"

# --------------------------------------------------------------------------
say "2 · a certificate authority, a server certificate, and two SVIDs"
if [ ! -f "$PKI/agent.pem" ]; then
  cd "$PKI"
  openssl req -x509 -newkey rsa:2048 -nodes -keyout ca.key -out ca.pem -days 30 \
    -subj "/CN=CyberTravels Demo CA" 2>/dev/null

  openssl req -newkey rsa:2048 -nodes -keyout server.key -out server.csr \
    -subj "/CN=localhost" 2>/dev/null
  printf 'subjectAltName=DNS:localhost,IP:127.0.0.1\n' > server.ext
  openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
    -out server.pem -days 30 -extfile server.ext 2>/dev/null

  # The two client certificates. Both are signed by the same CA and both are
  # therefore trusted by the server — which is the point. Trust is not what
  # distinguishes them; the cnf binding is.
  for who in workflow-agent:agent scraper:thief; do
    cn="${who%%:*}"; f="${who##*:}"
    openssl req -newkey rsa:2048 -nodes -keyout "$f.key" -out "$f.csr" \
      -subj "/CN=$cn" 2>/dev/null
    printf 'subjectAltName=URI:spiffe://cybertravels.com/ns/prod/sa/%s\n' "$cn" > "$f.ext"
    openssl x509 -req -in "$f.csr" -CA ca.pem -CAkey ca.key -CAcreateserial \
      -out "$f.pem" -days 30 -extfile "$f.ext" 2>/dev/null
  done
  cd - >/dev/null
fi
echo -n "agent SVID: "
openssl x509 -in "$PKI/agent.pem" -noout -ext subjectAltName | tail -1 | tr -d ' '
echo -n "its x5t#S256 thumbprint: "
openssl x509 -in "$PKI/agent.pem" -outform DER | openssl dgst -sha256 -binary \
  | base64 | tr '+/' '-_' | tr -d '='

# --------------------------------------------------------------------------
say "3 · start Keycloak with mTLS"
if ! nc -o /dev/null -w '' https://localhost:8443/realms/master --insecure 2>/dev/null; then
  ( cd "$KC" && JAVA_TOOL_OPTIONS="" \
      KC_BOOTSTRAP_ADMIN_USERNAME=admin KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
      ./bin/kc.sh start-dev --http-port=8080 --https-port=8443 \
        --https-certificate-file="$PKI/server.pem" \
        --https-certificate-key-file="$PKI/server.key" \
        --https-client-auth=request --truststore-paths="$PKI/ca.pem" \
        --features=token-exchange > "$WORK/keycloak.log" 2>&1 & )
fi
for _ in $(seq 1 40); do
  [ "$(nc -k -o /dev/null -w '%{http_code}' https://localhost:8443/realms/master)" = "200" ] \
    && break || sleep 5
done
echo "up on https://localhost:8443 (log: $WORK/keycloak.log)"

# --------------------------------------------------------------------------
say "4 · configure the realm"
unset JAVA_TOOL_OPTIONS; export JAVA_TOOL_OPTIONS=""
KCADM="$KC/bin/kcadm.sh"
$KCADM config credentials --server http://localhost:8080 --realm master \
  --user admin --password admin >/dev/null 2>&1

if ! $KCADM get realms/cybertravels >/dev/null 2>&1; then
  $KCADM create realms -s realm=cybertravels -s enabled=true >/dev/null

  WEB=$($KCADM create clients -r cybertravels -i \
    -s clientId=cybertravels-web -s enabled=true -s publicClient=false \
    -s secret=web-secret -s directAccessGrantsEnabled=true -s 'redirectUris=["*"]')
  AGENT=$($KCADM create clients -r cybertravels -i \
    -s clientId=workflow-agent -s enabled=true -s publicClient=false \
    -s secret=agent-secret -s serviceAccountsEnabled=true -s standardFlowEnabled=false)

  # The subject token must name the agent in its audience, or the exchange is
  # refused with "Client is not within the token audience".
  $KCADM create "clients/$WEB/protocol-mappers/models" -r cybertravels \
    -s name=agent-audience -s protocol=openid-connect \
    -s protocolMapper=oidc-audience-mapper \
    -s 'config."included.client.audience"=workflow-agent' \
    -s 'config."access.token.claim"=true' >/dev/null

  # RFC 8705: bind this client's access tokens to its TLS certificate.
  $KCADM get "clients/$AGENT" -r cybertravels > "$WORK/client.json"
  python3 - "$WORK/client.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p))
d.setdefault("attributes", {})["tls.client.certificate.bound.access.tokens"] = "true"
json.dump(d, open(p, "w"))
PY
  $KCADM update "clients/$AGENT" -r cybertravels -f "$WORK/client.json" >/dev/null

  U=$($KCADM create users -r cybertravels -i -s username=alice -s enabled=true \
    -s email=alice@cybertravels.com -s emailVerified=true \
    -s firstName=Alice -s lastName=Traveller)
  $KCADM set-password -r cybertravels --username alice --new-password travel123
  # Has to be a separate update: a user created with requiredActions unset
  # still gets the realm's defaults, and the password grant then refuses with
  # "Account is not fully set up" rather than saying which action is pending.
  $KCADM update "users/$U" -r cybertravels -s 'requiredActions=[]' >/dev/null
fi
AGENT_ID=$($KCADM get clients -r cybertravels -q clientId=workflow-agent --fields id \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["id"])')
echo "realm cybertravels: alice, cybertravels-web, workflow-agent ($AGENT_ID)"

TOKEN=http://localhost:8080/realms/cybertravels/protocol/openid-connect/token
STOKEN=https://localhost:8443/realms/cybertravels/protocol/openid-connect/token

claims() { python3 -c '
import sys, json, base64
d = json.load(sys.stdin)
if "access_token" not in d:
    print("  refused:", json.dumps(d)); raise SystemExit
p = d["access_token"].split(".")[1]
c = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
for k in ("preferred_username", "azp", "act", "cnf"):
    print(f"  {k:20s}{json.dumps(c.get(k, '"'"'(absent)'"'"'))}")
'; }

# --------------------------------------------------------------------------
say "5 · RFC 8693 token exchange — the agent acts for alice"
# Over the HTTPS listener, so the issuer on this token matches the issuer the
# exchange below is performed against. Cross them and Keycloak says only
# "Invalid token", which is a long afternoon.
SUBJ=$(nc --cacert "$PKI/ca.pem" -d grant_type=password -d client_id=cybertravels-web \
  -d client_secret=web-secret -d username=alice -d password=travel123 "$STOKEN" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# Worth seeing before anything else: once a client is certificate-bound,
# Keycloak refuses to issue it a token over a connection with no client
# certificate at all. The binding is not advisory.
echo "the agent asks for its own token over plain HTTP, with no certificate:"
nc -d grant_type=client_credentials -d client_id=workflow-agent \
  -d client_secret=agent-secret "$TOKEN" | sed 's/^/  /'
echo

MT=(--cacert "$PKI/ca.pem" --cert "$PKI/agent.pem" --key "$PKI/agent.key")
ACTOR=$(nc "${MT[@]}" -d grant_type=client_credentials -d client_id=workflow-agent \
  -d client_secret=agent-secret "$STOKEN" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo "subject_token only (RFC 8693 calls this impersonation):"
nc "${MT[@]}" -d grant_type=urn:ietf:params:oauth:grant-type:token-exchange \
  -d client_id=workflow-agent -d client_secret=agent-secret \
  -d subject_token="$SUBJ" \
  -d subject_token_type=urn:ietf:params:oauth:token-type:access_token \
  -d requested_token_type=urn:ietf:params:oauth:token-type:access_token \
  "$STOKEN" | claims

echo
echo "with actor_token as well (RFC 8693 calls this delegation, and says the"
echo "result SHOULD carry an act claim naming the actor):"
nc "${MT[@]}" -d grant_type=urn:ietf:params:oauth:grant-type:token-exchange \
  -d client_id=workflow-agent -d client_secret=agent-secret \
  -d subject_token="$SUBJ" \
  -d subject_token_type=urn:ietf:params:oauth:token-type:access_token \
  -d actor_token="$ACTOR" \
  -d actor_token_type=urn:ietf:params:oauth:token-type:access_token \
  -d requested_token_type=urn:ietf:params:oauth:token-type:access_token \
  "$STOKEN" | claims

# --------------------------------------------------------------------------
say "6 · RFC 8705 — a token bound to the certificate that asked for it"
nc "${MT[@]}" -d grant_type=client_credentials -d client_id=workflow-agent \
  -d client_secret=agent-secret "$STOKEN" > "$WORK/bound.json"
python3 -c '
import sys, json, base64
d = json.load(open(sys.argv[1]))
p = d["access_token"].split(".")[1]
c = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
print("  cnf:", json.dumps(c.get("cnf", "(absent)")))
open(sys.argv[2], "w").write(d["access_token"])
' "$WORK/bound.json" "$WORK/bound_token.txt"

# --------------------------------------------------------------------------
say "7 · the resource server does the comparison, or nothing does"
python3 "$HERE/payments_api.py" "$PKI" > "$WORK/api.log" 2>&1 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT
sleep 2

TOK=$(cat "$WORK/bound_token.txt")
for who in "legitimate agent:agent" "the thief:thief" "no client cert:"; do
  label="${who%%:*}"; f="${who##*:}"
  args=()
  [ -n "$f" ] && args=(--cert "$PKI/$f.pem" --key "$PKI/$f.key")
  printf '  %-18s' "$label"
  nc --cacert "$PKI/ca.pem" "${args[@]}" -H "Authorization: Bearer $TOK" \
    -w ' [HTTP %{http_code}]\n' https://127.0.0.1:9443/bookings/BK-4471
done

say "done — see EVIDENCE.md for the run this was recorded from"
