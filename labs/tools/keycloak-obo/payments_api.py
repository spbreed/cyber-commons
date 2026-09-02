"""A minimal RFC 8705 relying party: the CyberTravels payments API.

It terminates mTLS, introspects the presented bearer token against Keycloak,
and refuses the request unless cnf.x5t#S256 equals the SHA-256 thumbprint of
the certificate on THIS connection. That comparison is the resource server's
job — the authorization server issues the binding and can never enforce it.
"""
import base64, hashlib, json, ssl, sys, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PKI = sys.argv[1]
INTROSPECT = ("https://localhost:8443/realms/cybertravels/protocol/"
              "openid-connect/token/introspect")


def b64u(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def introspect(token):
    ctx = ssl.create_default_context(cafile=f"{PKI}/ca.pem")
    ctx.load_cert_chain(f"{PKI}/agent.pem", f"{PKI}/agent.key")
    body = urllib.parse.urlencode({
        "token": token, "client_id": "workflow-agent",
        "client_secret": "agent-secret"}).encode()
    req = urllib.request.Request(INTROSPECT, data=body)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        return json.load(r)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _reply(self, code, payload):
        raw = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return self._reply(401, {"error": "no bearer token"})
        token = auth[7:]

        claims = introspect(token)
        if not claims.get("active"):
            return self._reply(401, {"error": "token is not active"})

        # RFC 8705 section 3: compare the token's cnf against the certificate
        # on THIS TLS connection. Everything above this line is what a bearer
        # deployment already does.
        peer_der = self.connection.getpeercert(binary_form=True)
        if peer_der is None:
            return self._reply(403, {"error": "no client certificate presented",
                                     "cnf": claims.get("cnf")})
        presented = b64u(hashlib.sha256(peer_der).digest())
        bound_to = (claims.get("cnf") or {}).get("x5t#S256")
        if bound_to is None:
            return self._reply(403, {"error": "token is not certificate-bound"})
        if presented != bound_to:
            return self._reply(403, {"error": "cnf mismatch - token was not "
                                              "issued to this client",
                                     "token_bound_to": bound_to,
                                     "connection_using": presented})
        return self._reply(200, {"ok": True, "client": claims.get("client_id"),
                                 "bound_to": bound_to})


ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(f"{PKI}/server.pem", f"{PKI}/server.key")
ctx.load_verify_locations(f"{PKI}/ca.pem")
ctx.verify_mode = ssl.CERT_OPTIONAL          # so "no cert" is a 403, not a reset

srv = ThreadingHTTPServer(("127.0.0.1", 9443), Handler)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
print("payments API listening on https://127.0.0.1:9443", flush=True)
srv.serve_forever()
