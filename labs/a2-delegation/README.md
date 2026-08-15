# Lab A2.5 — delegation that survives audit

**Chapter:** [Track A2 — Identity & NHI Engineer](../../curriculum/track-a2.md) ·
also backs A2.3 (Shadow Autonomy), A2.4 (revocation), B2.6 (sub-agent depth),
C1.4 (attacking the chain)

The question every agentic incident starts with is *"who is calling?"* — and the
honest answer in most orgs today is *"we can't tell."* This lab makes the answer
live **in the token**.

## Run it — no infrastructure required

```bash
python3 delegate.py chain        # build a 3-hop chain, print the nested act claims
python3 delegate.py verify       # prove every hop is strictly attenuating
python3 delegate.py escalate     # try to widen scope mid-chain — must be refused
python3 delegate.py impersonate  # the anti-pattern, and why audit dies
python3 delegate.py revoke reviewer-agent   # kill one actor, not the chain
```

Python stdlib only. The chapter's full lab runs the same mechanics against real
**Keycloak** (RFC 8693 token exchange) — see the command block in
[track-a2.md](../../curriculum/track-a2.md); this file is that lesson with the
infrastructure removed so it is reachable on any laptop.

## What you should see

```
hop 0 — alice's own token
  scope=['deploy:prod', 'repo:read', 'repo:write']
  chain: user:alice
hop 1 — reviewer-agent acting for alice
  scope=['repo:read', 'repo:write']
  chain: user:alice → reviewer-agent
hop 2 — patch-agent acting for reviewer-agent acting for alice
  scope=['repo:read']
  chain: user:alice → reviewer-agent → patch-agent
```

and in the final token itself:

```json
{"sub": "user:alice",
 "scope": ["repo:read"],
 "act": {"sub": "patch-agent", "act": {"sub": "reviewer-agent"}}}
```

**That nested `act` claim is the audit trail** ([E2.8](../../curriculum/track-e2.md)).
It names who acted, under whose authority, at what scope — without ever
pretending the agent *was* alice.

## The four things this proves

| Command | Shows |
|---|---|
| `verify` | Scope shrinks strictly at every hop; `deploy:prod` is unreachable by `patch-agent` — **attenuation, not impersonation** |
| `escalate` | Widening is refused **by the token**, not by an application check an injected instruction could argue past |
| `impersonate` | Hand the agent alice's token unchanged and nothing looks broken — the audit log just says "alice deployed to prod". That's **Shadow Autonomy** (A2.3), and it survives in production for years precisely because it isn't an error |
| `revoke` | One actor dies, the other keeps working — the A2.4 deliverable ("revoke one misbehaving agent without breaking forty others") |

## Two rules do all the work

`exchange()` enforces both, and either one alone is insufficient:

1. **Subset of the presented token** — you cannot hand on more than you were given.
2. **Within the actor's own ceiling** — a compromised upstream token still cannot
   push an actor past what it was ever granted.

That second rule is *attenuation by construction*
([A1.3](../../curriculum/track-a1.md)): the over-privileged grant isn't blocked
by a policy, it cannot be written down.

## Things worth breaking

- Delete the ceiling check in `exchange()` and re-run `escalate` — it now
  succeeds. That deleted line is the control.
- Give `patch-agent` a wider entry in `GRANTS` and re-run `verify`. Attenuation
  fails, and the failure is visible in the token rather than in a log you'd have
  to go looking for.
- Chain to depth 5 and ask where you would cap it — that's
  [B2.6](../../curriculum/track-b2.md), delegation-depth budgets.

> **Not production crypto.** HMAC with a hard-coded lab key, and no JWKS, `aud`,
> `nonce` or replay window. The point is the *claim structure*; real deployments
> use the Keycloak path in the chapter.
