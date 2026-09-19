# CyberTravels — the system the whole commons is taught on

A small, **runnable** agentic application: a corporate travel platform with four
agents, two MCP resource servers, agent-to-agent messaging, scoped memory,
per-action on-behalf-of delegation, a human gate on high-risk actions, and an
append-only audit log.

> **This application is deliberately vulnerable.** [`LABELS.md`](LABELS.md) is
> the hand-written key: eight real defects, including a SQL injection and a
> path traversal that now **execute** rather than merely parse. It binds to
> `127.0.0.1` and it must never be exposed to a network, tunnelled, or
> deployed. It is a teaching corpus you attack on your own machine.

## Run it

```bash
pip install -r cybertravels/requirements.txt
python3 -m uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
# open http://127.0.0.1:8000
```

**With no API key it still runs.** A deterministic planner drives the same
identity → token exchange → MCP → audit path, so the whole control story is
demonstrable offline. Every span it emits is labelled `planner`; it is never
presented as a model's answer. Set `ANTHROPIC_API_KEY` for the real reasoning
loop.

The controls, without a server or a model at all:

```bash
python3 -m cybertravels.tests.smoke_test    # 8 assertions, all about refusals
```

## The architecture

```
  browser  ──►  BFF / orchestrator  ──►  model loop (or planner)
  console        main.py                  runtime.py │ picks a tool
  sign in        authn, SSE, HITL                     ▼
  approve                                    policy → budget → human gate
                                                      ▼
                                          RFC 8693 token exchange
                                          user token + agent NHI token
                                          ──► sub=human, act=agent,
                                              aud=one server, scope=one,
                                              expires in 120s
                                                      │
                                    ┌─────────────────┴──────────────────┐
                                    ▼                                    ▼
                          internal MCP server                  vendor MCP server
                          aud mcp:internal                     aud mcp:vendor
                          bookings, payments                   notices, policy
                          verifies before acting               verifies before acting
                                    │                                    │
                                    └──────────► SQLite + append-only audit
```

| layer | file | what to read it for |
|---|---|---|
| policy, as data | `config.py` | roles → delegatable scopes, tool → (audience, scope, high-risk), budgets |
| identity | `identity.py` | minting, RFC 8693 exchange, and **enforcement at the resource server** |
| orchestrator | `main.py` | authn, SSE trace, the approval endpoint |
| the loop | `runtime.py` | where every control is either applied or bypassed |
| MCP servers | `mcp/internal_server.py`, `mcp/vendor_server.py` | a boundary that refuses its own caller |
| agent-to-agent | `a2a/protocol.py` | signed envelopes, the human carried through, a hop ceiling |
| memory | `memory.py` | origin recorded with content, scoped per person, with delete and export |
| observability | `observability.py` | the run as spans, with tokens summarised and refusals recorded |
| storage | `db.py` | SQLite, seeded, append-only audit |
| workload identity | `registry.py` | identities as records with an approver, attestation, rotation and revocation |
| provenance | `provenance.py` | where a piece of text came from, marked at the boundary and carried |
| the decision point | `policy.py` | one decision per call, with a reason, obligations and the exemption register |
| containment | `sandbox.py` | what an execution may reach, and what the live process actually has |
| egress | `egress.py` | the destination allow-list **and** what is being sent to it |
| the return path | `returns.py` | schema, then an independent verifier — conformance is not correctness |
| the choke point | `gateway.py` | the controls above, behind one entry point, with a coverage number |
| the developer's agent | `devagent.py` | containment for the IDE agent that wrote all of the above |
| the AppSec pipeline | `appsec/` | **not part of the product** — the eleven stages Function B builds to review it, shipping in the same repository and scanned by its own rules |
| the defects | `tools/`, `agents/` | the corpus the AppSec lessons scan |

Those files arrive one lesson at a time. `python3 scripts/checkpoint.py --at <id>`
writes the tree as it stood at the end of any lesson, so a reader joining at A3.5
gets everything up to it and nothing after.

## Four things it does that most demos do not

**The resource server verifies.** Most systems log the actor claim and act
anyway, which makes the delegation chain a description rather than a control.
Here `verify_delegated` runs at the top of every MCP tool and refuses on
signature, audience, scope, actor registration or expiry.

**Least privilege is keyed to the human.** Dana is a traveller. However the
model is prompted, argued with or injected, the exchange will not mint her a
`payments:refund` token — so the resource server is never even asked. Sign in
as Dana and try `refund booking 2` to watch that happen.

**Refusals are recorded and returned.** A denial is an audit row, a span, and a
result the model receives and can explain. A trace that shows only successful
calls hides the events worth alerting on.

**Untrusted text is labelled where it enters.** Vendor documents arrive with
`origin` and `trusted: false` attached, and the runtime marks them before the
model sees them. `mcp/vendor_server.py` carries a notice with an instruction
aimed at automated agents — that is the fixture A1.2 and C1.3 use, and it is
in the corpus rather than injected by a test.

## It is meant to be defective

The defects are labelled in [`LABELS.md`](LABELS.md), written by reading the
tree before any scanner ran. A key written after the scan is a description of
the scan. `scripts/check_labels.py` holds the key to the tree in CI, so a
rename can never leave a skill scoring recall against a function that no longer
exists.

Five of the eight defects are a missing ownership check, and no pattern reaches
any of them — which is the whole argument of
[B2.3](https://cybercommons.ai/lessons/B2.3.html). The four labelled
*non*-defects are in the key on purpose: a corpus where everything is broken
cannot measure precision.

## What is simplified, and what is not

Simplified, and each one is somebody's lesson rather than a thing to pretend is
done: HS256 with a shared secret instead of RS256 + JWKS; a demo login with no
password instead of OIDC; the delegated token passed as a tool argument instead
of on the transport; SQLite and keyword search instead of Postgres and vector
retrieval; attestation modelled as matching observed selectors instead of real
SVIDs signed by SPIRE; containment and egress **decided in-process** rather
than enforced by an isolate and a network boundary the agent cannot reach —
which is the weaker placement, is said so in `sandbox.py` and `egress.py`, and
is the reason A3.7 exists.

Not simplified, because they are the point: per-action down-scoped delegation,
an actor claim carried end to end, audience and scope **enforced at the
resource server**, a human gate on high-risk actions, least privilege keyed to
the human's role, bounded loops, and an append-only audit trail that records
what was refused as well as what was done.

`HTTP` in `_stubs.py` is still inert on purpose. `sync_vendor` disables TLS
verification, and a teaching repository that actually made that request would
be reaching the internet with verification off from somebody else's laptop.
