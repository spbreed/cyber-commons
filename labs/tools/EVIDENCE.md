# What these tools actually did

Recorded 2 September 2026, on Linux with Python 3.11 and OpenJDK 21.0.10.
Every line below is output from `run.sh` in the directory named. Re-running
them reproduces the shape; certificate thumbprints differ because the CA is
minted fresh on each run.

The notebooks in `labs/notebooks/` model these protocols in the standard
library so they run on a Kaggle kernel with the internet switched off. These
scripts are the other half of the claim: the same protocols, against the actual
products, with the results — including the ones that contradict what the
protocol says should happen.

---

## `keycloak-obo/` — Keycloak 26.0.7

Five things were checked. Three behaved as the specifications describe and two
did not, and the two are the reason this directory exists.

**A certificate-bound client cannot get a token without a certificate.** Once
`tls.client.certificate.bound.access.tokens` is `true`, a plain-HTTP token
request from that client is refused outright:

```
the agent asks for its own token over plain HTTP, with no certificate:
  {"error":"invalid_request","error_description":"Client Certification missing for MTLS HoK Token Binding"}
```

**RFC 8705 binding works, exactly.** Requested over mTLS with the agent's
certificate, the access token carries a `cnf` claim whose `x5t#S256` equals the
SHA-256 thumbprint of that certificate, computed independently with `openssl`:

```
agent SVID: URI:spiffe://cybertravels.com/ns/prod/sa/workflow-agent
its x5t#S256 thumbprint: BuTPvYMaI3z-suLCcWsnFHDCv_6VQdDrYwLlf70Sjfg
  cnf: {"x5t#S256": "BuTPvYMaI3z-suLCcWsnFHDCv_6VQdDrYwLlf70Sjfg"}
```

**The comparison is the resource server's job, and nothing does it for you.**
Keycloak issues the binding and publishes it through introspection; it cannot
enforce it, because it is not in the path of the request to the payments API.
`payments_api.py` is 80 lines of standard library that introspects the token
and then compares `cnf.x5t#S256` against the certificate on its own TLS
connection. The same token, presented three ways:

```
  legitimate agent  {"ok": true, "client": "workflow-agent", "bound_to": "BuTPvYMaI3z-..."}  [HTTP 200]
  the thief         {"error": "cnf mismatch - token was not issued to this client",
                     "token_bound_to": "BuTPvYMaI3z-...",
                     "connection_using": "YCOt32KGs6Hv-..."}                                 [HTTP 403]
  no client cert    {"error": "no client certificate presented"}                             [HTTP 403]
```

The thief's certificate is signed by the same CA and is therefore trusted.
Trust is not what separates them; the binding is.

### The two findings

**Keycloak's standard token exchange emits no `act` claim.** RFC 8693 §4.1
defines `act` as the claim that names the actor, and §2.1 distinguishes
delegation — where an `actor_token` is presented and the result identifies both
parties — from impersonation, where it does not. Keycloak 26.0.7 accepts
`actor_token`, returns 200, and produces the same token either way:

```
subject_token only (RFC 8693 calls this impersonation):
  preferred_username  "alice"
  azp                 "workflow-agent"
  act                 "(absent)"

with actor_token as well (RFC 8693 calls this delegation, and says the
result SHOULD carry an act claim naming the actor):
  preferred_username  "alice"
  azp                 "workflow-agent"
  act                 "(absent)"
```

`azp` does name the agent, so the information is not lost — but `azp` is one
value, and `act` nests. A three-hop chain has nowhere to go. If you want the
delegation chain A2.3 reconstructs, you are writing a protocol mapper.

**The exchange drops the certificate binding.** The direct
`client_credentials` token carries `cnf`. The exchanged token, requested over
the same mTLS connection with the same certificate, does not:

```
  cnf                 "(absent)"
```

So the token the agent actually carries downstream — the one issued for acting
on alice's behalf — is a bearer token again, and the theft the binding was
bought to prevent is back. This is the one to check in your own deployment
before assuming the control is on.

### Notes for anyone reproducing it

- The subject token and the exchange must be issued by the **same** issuer
  URL. Getting the first over `:8080` and exchanging at `:8443` returns
  `{"error":"invalid_request","error_description":"Invalid token"}` with no
  hint that the issuer is the problem.
- The subject token must name the agent client in its audience, or the
  exchange returns `Client is not within the token audience`. That is an
  audience protocol mapper on the *calling* client.
- A user created through `kcadm` picks up the realm's default required actions
  even when none were asked for. The password grant then fails with `Account is
  not fully set up`, which does not say which action is pending.

---

## `semgrep-sast/` — Semgrep 1.176.0

Run against `booking.py`, which stands in for a pull request from the
CyberTravels Coding Agent. Two ruleset widths:

```
  p/python + p/secrets: 1 finding(s)
    line  17  ERROR   subprocess-shell-true

  seven packs: 4 finding(s)
    line   9  ERROR   sqlalchemy-execute-raw-query
    line  14  WARNING eval-detected
    line  17  ERROR   subprocess-shell-true
    line  20  ERROR   disabled-cert-validation
```

The default Python pack finds one of four. Adding `p/default`,
`p/security-audit`, `p/sql-injection`, `p/command-injection` and
`p/owasp-top-ten` finds the other three, including the SQL injection. Nothing
about the file changed; the coverage was a configuration decision, and on the
narrow setting three real defects were invisible.

Two things neither width found:

```
  line  22  MISSED a live-looking API key assigned to a module-level constant
           API_KEY = "sk-live-4f9a2b1c8e7d6a5b3c2d1e0f9a8b7c6d"
  line   7  MISSED find_booking takes a reference from the caller and performs
           no authorisation check of any kind
```

The first is lexical and a rule could catch it — `p/secrets` was enabled and
did not, because the string does not match a known provider's format. The
second is not expressible as a pattern at all: the defect is the *absence* of a
call, in a function whose caller holds payments scope. That is the boundary
B1.3's second generation exists to cross, and it is why the argument there is
"both", not "the newer one".

---

## `openapi-audit/` — openapi-spec-validator

`bookings-openapi.yaml` is a valid OpenAPI 3.1 document. It is also wrong in
two ways that no validator will ever report, because neither is a schema
violation:

```
openapi-spec-validator: the document is valid OpenAPI 3.1

operation           method and path                         scopes enforced
getBooking          GET /bookings/{ref}                     bookings:read
createBooking       POST /bookings                          bookings:write
refundBooking       POST /bookings/{ref}/refund             bookings:read       INHERITED from the document default, not declared
exportCustomers     GET /internal/customers/export          (none)              AUTHENTICATION EXPLICITLY DISABLED
```

`refundBooking` declares no `security` block, so it silently inherits the
document default of `bookings:read`. A token that can look at a booking can
refund it. That is R1 written in YAML — and since the Workflow Agent's tool
surface is generated from this file, the agent inherits it exactly.

`exportCustomers` has `security: []`, which is not "unspecified" but
"authentication explicitly disabled" — the one value a reviewer skims past
because it looks like an empty default.

---

## `litellm-gateway/` — LiteLLM 1.99.0

Started with a two-model config, a master key and `mock_response`, so routing
and policy are exercised without spending anything on a model call.

```
  master key, model on the list     {"choices":[{"message":{"content":"Two nights in Lisbon, ..."}}]}
  master key, model NOT on it       {"error":{"message":"Invalid model name passed in model=gpt-4o ...","code":"400"}}
```

The model allow-list holds with nothing but a config file. A request for a
model the file does not name is refused whoever asked, which is the control
A3.7 wants.

Key checking is a different story:

```
  a guessed key                     {"error":{"message":"No connected db.","code":"400"}}  [HTTP 400]
  no key at all                     {"error":{"message":"Internal server error"}}          [HTTP 500]
```

LiteLLM's virtual keys — per-agent keys with their own model list, budget and
rate limit — live in Postgres. With no `DATABASE_URL`, every key that is not
the master key returns `No connected db` rather than a refusal, and a request
with no key at all returns a 500. `/health/liveliness` returns 200 throughout
and the startup log says nothing about it.

Which is the general shape: a gateway is a control **surface**, not a control.
It enforces what you configured and fails open on what you did not, while its
own health check reports healthy.

---

## Kaggle — 121/121 reproduced, after six traps

**The result first.** Every one of the 121 notebooks was pushed to Kaggle, run
on Kaggle's machines, and its stdout compared line for line against a fresh
local run:

```
121/121 kernels printed exactly what the local run printed
```

That is the strong form of the claim this repository makes. Not "it completed"
— a kernel that prints nothing completes — but *the same notebook produced the
same output on two independent machines*, which is only possible because the
notebooks are deterministic and carry every line they run. The remote logs are
committed under `labs/notebooks/_kaggle_output/` so the comparison can be
repeated by anyone.

## Getting there — six failures, none of which said what was wrong

Not a tool lab, but the same shape of finding and worth recording next to them.
`scripts/kaggle_push.py` pushes every notebook to Kaggle so "it runs on a
Kaggle kernel" is checked rather than assumed. Getting 121 notebooks up hit
three failures that all present as the same misleading HTTP 409:

```
ERROR HTTP 409 {"code":409,"message":"The requested title \u0022Cyber Commons A1.4\u0022 ...
```

**The username was wrong, and nothing said so.** A kernel is addressed as
`<username>/<slug>`. `KAGGLE_USERNAME` had been set from the GitHub
organisation rather than the Kaggle account, so every push named a namespace
belonging to somebody else — and Kaggle reports that as a *title* conflict, not
as an authentication or authorisation error. Auth succeeds, the account name is
never mentioned, and the message points at the one thing that is not the
problem.

**There is no whoami endpoint.** The only reliable way to learn which account a
token belongs to is to push a kernel with an empty slug and read the owner out
of the returned `ref`. The script now does that once and caches the answer next
to the credentials.

**The probe collides with itself, twice over.** A probe with a fixed title
409s on the second run against the kernel the first run left behind. And
because `credentials()` was called per request while pushes run four at a
time, four concurrent probes raced for the same title and three came back
409 — reproducing the exact error the resolution was added to prevent. The
title is now unique per run, the resolution is memoised, and a failed probe
exits loudly rather than falling back to the claimed username, which is what
made the first version of this fix look like it had not worked.

**The verifier was verifying nothing.** It selected kernels with
`v == "complete"`, but the push ledger stores the kernel *URL* after a plain
`--all` push and the string `"complete"` only after `--all --wait`. So it
matched nothing, exited before checking a single kernel, and phrased its own
empty selection as a fact about Kaggle: "no kernels reported 'complete'".

**A throttle was recorded as a verdict.** `/kernels/status` returns HTTP 429
well before 121 sequential calls finish. The pre-check caught every exception
as `unknown` and skipped anything not `"complete"`, so 62 kernels were dropped
and the smaller denominator was reported as though it were the real one. Status
reads now retry with backoff — 12 retries were needed in the successful run —
and *complete*, *still running* and *unreadable* are kept distinct, with
unreadable counted as neither pass nor fail.

**The test harness caused a mismatch and blamed the notebooks.** The first
clean pass reported 54/59 identical, with the five "failures" being exactly the
five model lessons. A Kaggle kernel has no model credentials, so a lesson takes
its offline replay path there — but the local comparison run inherited the
operator's environment, and with `ANTHROPIC_API_KEY` exported it took the
frontier path instead. The difference was real and was entirely about the
shell. `local_output()` is now hermetic, which also means the claim no longer
depends on who runs it.

The general lesson is the one the Keycloak section makes too: **the error a
service returns is about the request it could not satisfy, not about the
mistake you made.** Six failures in a row, each a confident statement about
something other than the cause — a wrong account reported as a title
collision, a stale probe kernel, a concurrency race, an empty selection
reported as an empty world, a throttle reported as incompletion, and a harness
bug reported as a notebook difference.

---

## What was not run

**No model API call has completed against a billed endpoint.** Three keys were
tried across two providers, and every one was blocked before inference:

- **Anthropic, identity-linked key.** The Messages API refuses every call with
  `anthropic-workspace-id is required when authenticating with an
  identity-linked API key`. The workspace id cannot be discovered from the key
  itself — `/v1/organizations/workspaces` needs an admin key and returns
  `permission_error`. The adapter now sends the header when
  `ANTHROPIC_WORKSPACE_ID` is set, confirmed by watching the error change from
  "is required" to "must be a valid workspace ID".
- **Anthropic, default-workspace key.** Correctly scoped — the workspace error
  is gone. `GET /v1/models`, which costs nothing, authenticates and returns 11
  models including the adapter's default `claude-haiku-4-5-20251001`. Every
  inference call, down to `max_tokens: 1`, returns
  `Your credit balance is too low to access the Anthropic API`. So the key,
  the scoping, the model id and the adapter are all correct, and the only
  missing input is a funded balance.
- **OpenAI** — authenticates fine and returns `credit_balance_exhausted`: the
  account has no credits.

Both accounts are simply out of credit. The gateway lab therefore still uses
`mock_response` and the model lessons still fall back to their recorded replay
— the designed behaviour, labelled as a replay everywhere it appears, and the
reason the offline path is the default rather than a fallback bolted on.

Nothing further is needed in code. `scripts/live_model_test.py` runs the seven
model lessons against the real API the moment either account has a balance:

    export ANTHROPIC_API_KEY=...
    export ANTHROPIC_WORKSPACE_ID=...   # only for an identity-linked key
    python3 scripts/live_model_test.py --backend frontier --save

That this ran end to end against `claude-haiku-4-5-20251001` and stopped at a
billing check rather than at a bug is itself worth recording: the failure is
outside the code.

That attempt was not wasted: holding real keys is what found the hole in
`scripts/check_secrets.py`. Its `sk-` rule was anchored on alphanumerics, which
matches the classic OpenAI key and silently misses both `sk-ant-api03-…` and
`sk-proj-…`, because those carry hyphens in the body. The scanner had been
reporting "no credentials" while being unable to detect the two key formats
actually issued today. It now has a self-test that runs on every invocation.

**No Docker.** There is no daemon in this environment, so Keycloak runs from
its distribution zip rather than a container. That is why `run.sh` needs Java.
