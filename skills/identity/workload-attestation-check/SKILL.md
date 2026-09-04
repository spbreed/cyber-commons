---
name: workload-attestation-check
description: >-
  Establish how a workload receives its first credential and whether possession
  of that credential is still proof of identity — testing an unattested process,
  an unregistered image, presentation from another node, and use after expiry.
  Use when reviewing bootstrap, SPIFFE/SPIRE, or any secret mounted at deploy
  time.
allowed-tools: Read, Grep, Glob
---

# Where the first credential comes from

There is a circularity at the start of every workload identity: to receive a
credential securely the workload must already prove who it is. A pre-shared
secret resolves it by making **possession** the proof, which means everyone who
can read the image is the agent. Attestation resolves it by having the platform
sign what only the platform knows.

## When to use this

Reviewing how any agent, job or pod authenticates for the first time. The
answer decides whether every later identity control rests on something or on a
copied file.

## Procedure

**1 — Find the first credential.** Trace back from a downstream call to where
the credential entered the process: an environment variable, a mounted file, a
secrets manager fetch, or an attestation exchange.

**2 — Ask who else can read it.** For a secret, that set is the set of people
who are currently the agent. Enumerate it — image layers, CI logs, anyone with
`exec` on the namespace, anyone who can read the manifest.

**3 — Test the unattested process.** A process that is not what the platform
started should receive nothing. If it receives a credential, the exchange is
authenticating a claim rather than a workload.

**4 — Test the unregistered-but-genuine image.** A real workload nobody
registered is the case people forget: attestation proves *what* is running, and
registration decides whether it should be. Both must refuse.

**5 — Test binding and lifetime.** Present a legitimately issued credential
from a different node, and again after its TTL. Both must fail. A credential
that travels is a secret with extra steps.

## Output contract

```json
{
  "source": "env|file|manager|attestation",
  "readable_by": ["str"],
  "probes": {"unattested": "issued|refused", "unregistered_image": "issued|refused",
             "wrong_node": "accepted|refused", "expired": "accepted|refused"},
  "properties": {"non_copyable": false, "short_lived": false, "bound": false},
  "ttl_seconds": 0
}
```

All three properties, or the credential is a secret: non-copyable because it
describes a running process, short-lived so theft has a deadline, bound so
presenting it elsewhere fails.

## Failure modes

- **Accepting a secrets manager as attestation.** It answers "who may fetch
  this", which is the same circularity one layer down.
- **Testing only the unattested case.** The unregistered genuine workload is
  the one that gets through.
- **Recording a long TTL as acceptable** because rotation exists. Rotation is
  not a deadline for a copy already taken.
