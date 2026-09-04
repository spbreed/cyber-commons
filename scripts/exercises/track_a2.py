"""A2 — Controls: identity and ingress.

Chapter 1 named the risks. This chapter closes the two that everything else
depends on: knowing who is calling, and knowing what came in from outside.

Each lesson states the threats it mitigates, describes the control, and carries
exactly one block of code implementing it.

    A2.1  agent identity            T9, T3, T1
    A2.2  bootstrapping             T9
    A2.3  delegation that narrows   T3, T8, T14
    A2.4  just-in-time authority    T3, T2
    A2.5  the NHI lifecycle         T9, T13, T3
    A2.6  ingress provenance        T6, T1, T12
    A2.7  attribution               T8, T13
"""

from . import diagrams as D
from .skills import runtime_step

RUNTIME_STEP = runtime_step()

from .skills import skill_steps

MITIGATES = """
> **What this control closes.**
>
"""

EXERCISES: dict[str, dict] = {

"A2.1": {
 "concept": """
**Mitigates: T9 Identity Spoofing · T3 Privilege Compromise · T1 Memory Poisoning.**

Three identities are in play whenever an agent acts, and A1.6 and A1.7 were both
caused by collapsing them into one.

**The user.** The human who asked. Carries the business authority and is the
answer to "on whose behalf".

**The workload.** The process that runs — a container, a function, a pod. It has
its own identity, derived from the platform, not from a secret someone pasted.

**The agent instance.** This particular run, of this particular agent, for this
particular task. It is what you revoke when one agent misbehaves.

The control is to keep all three, and to use them for different things:

- **Authorize on the workload.** What may this agent ever do? That is its
  ceiling, and it does not change per request.
- **Attribute to the user.** Who caused this? That is what the audit trail needs
  and what A1.14 could not answer.
- **Scope memory and state to the instance or the user**, never to the workload
  alone — which is the write that made A1.4 spread across sessions.

The failure mode to watch for is a system that authenticates the agent and then
forgets the human, because it produces logs that are complete and useless.
""",
 "steps": [
  ("md", MITIGATES + "> Answers **who is calling**, so every later control has "
         "a subject. Without it, default-deny has nothing to deny and the audit "
         "trail has nobody to name.\\n\\n"
         "## 2 · The control"),

  ("md", "## 2 · Separating the three, as a skill\\n\\n"
         "Keeping the three identities apart is a review you will run against "
         "every agent CyberTravels ships, not a decision you make once. So it "
         "is written down as a procedure: which principal authorises, which one "
         "is attributed, which one scopes memory — and the two narrowing rules "
         "a delegated token has to satisfy before any of it means anything. "
         "This is the file in this repository, embedded verbatim:"),
  ("skill", "identity/agent-identity-review"),
  ("skill_script", "identity/agent-identity-review/scripts/agent_identity_review.py"),
],
 "expect": "The skill loads and reports its own shape: a routing description an "
           "agent reads to decide whether this review applies, the tools it is "
           "allowed to use, and a procedure long enough to separate user, "
           "workload and agent instance and to check both narrowing rules — "
           "scope is a subset of what was presented, and within the actor's own "
           "ceiling.",
 "challenge": "For one agent, write down its three identities. If the workload "
              "and the user are the same value, you have inherited credentials; "
              "if the instance does not exist, you cannot revoke one run.",
},

"A2.2": {
 "concept": """
**Mitigates: T9 Identity Spoofing & Impersonation.**

A2.1 says the workload needs its own identity. This lesson is about how it gets
one, because there is a circularity: to receive a credential securely the
workload must already prove who it is.

The wrong answer is a **pre-shared secret** — a key in the image, a token in an
environment variable, a file mounted at deploy time. All of them are copyable,
and a copyable secret makes possession the proof of identity. Anyone who reads
the image is the agent.

The control is **attestation**. The platform that started the workload already
knows things nobody else can forge: which image ran, in which namespace, under
which service account, on which node. It signs a statement to that effect, and
an identity service exchanges that statement for a short-lived credential bound
to that workload.

Three properties matter:

- **Non-copyable.** The attestation describes a running process. Copying the
  document to another machine produces a claim the platform will not sign.
- **Short-lived.** The credential expires in minutes, so theft has a deadline.
- **Bound.** It is issued *to* that workload identity, so presenting it from
  elsewhere fails.

This is what SPIFFE/SPIRE and every cloud workload-identity system do. The
lesson models the exchange, not the product.
""",
 "steps": [
  ("md", MITIGATES + "> Makes **possession stop being proof**. Without it, "
         "A1.7 is unavoidable: a copyable secret means every holder is the "
         "agent.\\n\\n## 2 · The control"),
  *skill_steps('identity/workload-attestation-check',
               "## 2 · The check, as a skill\n\nWhether CyberTravels' agents hold a credential or a secret is settled by four probes, not by reading the deployment manifest. The skill runs them: an unattested process, a genuine image nobody registered, a credential presented from another node, and one presented after its TTL."),
],
 "expect": "An unattested process receives no credential, a genuine but "
           "unregistered image receives none either, and a credential issued to "
           "a real workload is refused when presented from another node or after "
           "its five-minute expiry.",
 "challenge": "Find where one of your agents gets its first credential. If the "
              "answer is an environment variable or a mounted file, list "
              "everyone who can read it — that is the set of people who are "
              "currently that agent.",
},

"A2.3": {
 "concept": """
**Mitigates: T3 Privilege Compromise · T8 Repudiation · T14 Human Attacks.**

The agent has its own identity now. This lesson is about carrying the user's
authority alongside it — without losing it, amplifying it, or handing it to
whoever picks the token out of a log.

Three layers do that, and each one answers a question the layer above it
cannot. Skipping any of them leaves a specific, named hole.

**Layer 1 — mTLS with an X.509 SVID. *Is this the workload it claims to be?***
The agent pod presents a client certificate whose URI SAN is a SPIFFE ID:
`spiffe://cybertravels.com/ns/prod/sa/agent-alpha`. The platform issues it on
attestation (A2.2), it lives minutes rather than months, and it rotates without
anybody being told. Nothing downstream trusts a name in a header again.

**Layer 2 — OAuth on-behalf-of, RFC 8693 token exchange. *On whose authority?***
The agent presents two tokens: the user's (`subject_token`) and its own SVID
(`actor_token`). The authorization server returns one access token whose `sub`
is still the user and whose **`act` claim** names the agent. Delegation is
written down rather than inferred, and it nests — `act.act` records the hop
before — so `alice → orchestrator → agent-alpha` survives into the audit log.

**Layer 3 — RFC 8705 certificate-bound tokens. *Is the presenter the one it was
issued to?*** The issued token carries a `cnf` claim holding `x5t#S256`: the
SHA-256 thumbprint of the client certificate that asked for it. The downstream
service recomputes the thumbprint of the certificate on *its own* TLS
connection and compares. A bearer token is a password; a bound token is useless
to anyone holding it without the private key that earned it.

On top of the three layers, delegation still has to **narrow**, and it has to
satisfy two rules rather than one:

**Subset of presented.** The issued token carries no more scope than the
incoming one. Stops the agent inventing authority.

**Within the actor's ceiling.** The issued token carries no more than the
receiving agent may ever hold. Stops a privileged user handing an agent
authority the agent must never have.

Neither is sufficient alone, and they fail in opposite directions. Subset-only
lets an admin's request give a low-trust agent `payments:refund` — legitimately,
and it looks correct in every log. Ceiling-only lets an agent exceed the person
who asked, which is A1.6. **The issued scope is the intersection.**

> **On the standards.** RFC 8693 (token exchange) and RFC 8705 (mTLS client
> authentication and certificate-bound access tokens) are published and widely
> implemented — none of this is future work. The IETF OAuth working group
> additionally has a live draft for AI agents acting on a user's behalf, which
> adds agent-specific metadata to the same exchange. It is a draft, not an RFC,
> and nothing in this lesson depends on it: all three layers are buildable on
> RFC 8693 and RFC 8705 as they stand today.
""",
 "steps": [
  ("md", "## 2 · The three layers, and what each one refuses"),
  ("html", D.flow(
    [D.column("agent pod", [
       D.card("&#129302;", "AI agent", "holds an X.509 SVID issued on "
              "attestation, plus the user's token from the request",
              colour=D.DEFEND, note="spiffe://.../sa/agent-alpha"),
     ]),
     D.column("layer 1 · mTLS", [
       D.card("&#128274;", "client certificate", "URI SAN carries the SPIFFE "
              "ID. Minutes long, rotated automatically", colour=D.GOOD,
              note="REFUSES A NAME IN A HEADER"),
     ]),
     D.column("layer 2 · RFC 8693", [
       D.card("&#127915;&#65039;", "authorization server", "subject_token is "
              "the user, actor_token is the SVID. One token comes back: sub is "
              "still the user, act names the agent", colour=D.SECURE,
              note="REFUSES WIDENING"),
     ]),
     D.column("layer 3 · RFC 8705", [
       D.card("&#128273;", "cnf / x5t#S256", "the thumbprint of the certificate "
              "that asked for the token, stamped into the token itself",
              colour=D.SECURE, note="REFUSES A STOLEN TOKEN"),
     ]),
     D.column("downstream", [
       D.card("&#128179;", "payments API", "re-derives the thumbprint from its "
              "own TLS connection and compares it before reading a single scope",
              colour=D.BAD, note="R1"),
     ])],
    caption="Each layer answers a question the one before it cannot: is this "
            "the workload, on whose authority, and is the presenter the one the "
            "token was issued to. The code below builds all three, then steals "
            "the token.")),
  ("md", MITIGATES + "> Both narrowing rules, at every hop, plus a binding that "
         "makes the token worthless off the connection that earned it."
         "\n\n## 3 · Layers 1 and 2 — the exchange, and the token it issues"),
("md", "## 4 · Layer 3 — steal the token and try to use it"),
("md", """## 5 · The same three layers, against real Keycloak

Everything above is the protocol, modelled in the standard library so this
notebook runs with the internet switched off. That proves RFC 8693 and RFC 8705
work. It does not prove the product you are about to deploy implements them,
which is a different question and has a different answer.

[`labs/tools/keycloak-obo/`](https://github.com/spbreed/cyber-commons/tree/main/labs/tools/keycloak-obo)
downloads Keycloak 26.0.7, starts it with mTLS, configures this realm and runs
the same three checks. Three of them behaved as the specifications describe:

```
the agent asks for its own token over plain HTTP, with no certificate:
  {"error":"invalid_request",
   "error_description":"Client Certification missing for MTLS HoK Token Binding"}

its x5t#S256 thumbprint (computed with openssl):
  BuTPvYMaI3z-suLCcWsnFHDCv_6VQdDrYwLlf70Sjfg
the cnf claim on the token Keycloak issued:
  {"x5t#S256": "BuTPvYMaI3z-suLCcWsnFHDCv_6VQdDrYwLlf70Sjfg"}

the same token, presented to a resource server that compares:
  legitimate agent  HTTP 200
  the thief         HTTP 403  cnf mismatch - token was not issued to this client
  no client cert    HTTP 403  no client certificate presented
```

The thief's certificate is signed by the same CA and is therefore trusted.
Trust is not what separates them.

**And two did not.** These are the ones worth carrying out of this lesson:

**Keycloak's standard token exchange emits no `act` claim** — with or without
an `actor_token`. It returns 200 either way and produces the same token. `azp`
does name the agent, so the information is not lost, but `azp` is one value and
`act` nests: a three-hop chain has nowhere to go. The delegation chain
reconstructed in the next cell is something you write a protocol mapper for.

**The exchange drops the certificate binding.** The direct token carries `cnf`.
The exchanged token — requested over the same mTLS connection, with the same
certificate — does not. So the token the agent actually carries downstream, the
one issued for acting on alice's behalf, is a bearer token again, and the theft
the binding was bought to prevent is back.

Neither is a reason not to build this. Both are reasons to check your own
deployment rather than assume the control is on because the feature exists."""),
  ("md", "## 5 · What the audit trail can now answer\n\nEvery hop is on the "
         "token, so the chain reconstructs from the token alone rather than by "
         "correlating four services' logs on timestamp. This is the thing A1.14 "
         "could not do."),

  ("md", "## 6 · Verifying the chain, as a skill\n\nThe two findings above are "
         "what you get from *checking* a deployment rather than reading its "
         "design document, and CyberTravels has four agents and a payments API "
         "to check. The procedure walks every hop — user, agent, MCP server, "
         "tool, downstream — looks for token passthrough, and refuses to accept "
         "a matching `sub` as proof of delegation, because impersonation "
         "produces one too. This is the file in this repository:"),
  ("skill", "attestation/identity-chain-verifier"),
  ("skill_script", "attestation/identity-chain-verifier/scripts/identity_chain_verifier.py"),
],
 "expect": "The verifier skill loads and reports its shape: the description an "
           "agent routes on, the tools it may use, and a procedure that walks "
           "every hop of the chain rather than checking the token it was handed. "
           "Read its failure modes against the Keycloak findings above — a "
           "matching `sub` is not delegation, and a chain with no audience check "
           "cannot see passthrough at all.",
 "challenge": "Find your token exchange and check three things: does it set an "
              "`act` claim, does it check the actor's ceiling as well as the "
              "subset rule, and does anything downstream look at `cnf`? Most "
              "implementations do the subset rule only — it is the one the "
              "specification example shows.",
},

"A2.4": {
 "concept": """
**Mitigates: T3 Privilege Compromise · T2 Tool Misuse.**

A2.3 narrows authority at the moment of delegation. This lesson removes it when
the task is over.

Standing authority is the reason an injection is always worth attempting: the
credential is there, permanently, waiting. Every successful A1.3 lands on a live
grant. Just-in-time authority changes the arithmetic — the attacker has to
arrive during a window that exists only while a specific task is running, and
that is bound to a specific resource.

Three properties, and the third is the one usually skipped:

**Short-lived.** Minutes, not months. Theft has a deadline.

**Purpose-bound.** Scoped to *this* resource, not to the resource class. Not
`reports:write` but `reports:write` on report 8812.

**Revoked on completion.** The grant ends when the task ends, not when the timer
does. A task that finishes in ten seconds should not leave a fifteen-minute
credential lying around, which is the difference between a TTL and an actual
lifecycle.

The operational cost is real and worth stating plainly: something must issue
these, and if that path breaks, work stops. That is the trade — a system that
fails closed under a control outage, in exchange for a system that has no
standing authority to steal.
""",
 "steps": [
  ("md", MITIGATES + "> Removes the **standing** grant an injection needs. The "
         "attacker must now arrive inside a window bound to one task and one "
         "resource.\\n\\n## 2 · The control"),

  ("md", "## 2 · Finding the standing grants, as a skill\\n\\n"
         "Just-in-time authority is only worth building where standing "
         "authority exists today, and at CyberTravels that list is not the one "
         "in the design document — it is in the authorisation graph and in the "
         "OAuth scopes the credential provider stored when someone first "
         "connected the payments API. The procedure diffs what each identity "
         "*holds* against what its declared tools actually *need*, and flags "
         "every permanent grant. This is the file in this repository:"),
  ("skill", "attestation/entitlement-overprivilege-analyzer"),
  ("skill_script", "attestation/entitlement-overprivilege-analyzer/scripts/entitlement_overprivilege_analyzer.py"),
],
 "expect": "The skill loads and reports its shape. Note what its procedure "
           "insists on: the denominator is the capability set the tools require, "
           "not another set of grants — comparing grants against grants is how a "
           "review concludes that an over-privileged agent is normal — and a "
           "narrow-looking scope still counts as standing privilege if it never "
           "expires.",
 "challenge": "Take one standing grant an agent holds and work out what would "
              "break if it expired in two minutes. That list is the real cost of "
              "just-in-time, and it is usually shorter than expected.",
},

"A2.5": {
 "concept": """
**Mitigates: T9 Identity Spoofing · T13 Rogue Agents · T3 Privilege Compromise.**

Human identities have a lifecycle: someone joins, moves team, leaves, and an HR
event drives the change. Non-human identities have none of that. They are
created by whoever needed one, owned by nobody in particular, and removed never.

They also outnumber humans, often by a large multiple.

A1.11's rogue agent was admitted because the orchestrator had no notion of an
approved agent. The control is a registry, and a registry is only useful if it
carries three fields:

**A named owner.** A person, not a team alias. An identity with no owner cannot
be renewed, questioned or revoked, because nobody is accountable for answering.

**An expiry.** Not for the credential — for the *registration*. It forces a
recurring decision about whether this agent should still exist, which is the
only mechanism that removes the ones nobody uses.

**An admission binding.** The registry entry names the workload identity from
A2.2. Admission then checks the presented identity against the registry rather
than checking a name the caller supplied.

That last point is what makes it a control rather than a spreadsheet. A registry
consulted by name is documentation; a registry consulted by attested identity is
an authorization decision.

### The registry has to be driven by something, and that something is SCIM

A registry nobody updates decays into the spreadsheet it replaced. Humans do
not have this problem, because their lifecycle is already automated by a
protocol: **SCIM** — System for Cross-domain Identity Management, RFC 7643 for
the schema and RFC 7644 for the protocol. The HR system creates a user, the
identity provider `POST`s it to `/Users`, a leaver event `PATCH`es
`{"active": false}`, and every downstream application finds out without anybody
filing a ticket.

Point the same protocol at agents and three things become true at once:

**The joiner-mover-leaver machinery you already run is the machinery that
governs agents.** No parallel process, no second system of record. Deploying an
agent means creating a SCIM resource; retiring it means one `PATCH`.

**The owner is a reference, not a string.** `owner.$ref` points at the SCIM
`User` — so when Sam leaves, Sam's own leaver event is enough to answer "which
agents just lost their owner", automatically, on the day it happens rather than
at the next audit.

**Orphans become a query.** `GET /Agents?filter=active eq true and owner pr
false` is a one-line answer to a question that is otherwise a quarter of
someone's life.

> **What is and is not standard here.** SCIM's protocol — the endpoints, the
> filter syntax, `PATCH` with `active: false`, the `meta` block — is RFC 7644
> and your IdP already speaks it. A resource type for *agents* is not in RFC
> 7643; you declare it as a schema extension under your own URN, exactly as the
> enterprise extension does for `manager`. The protocol is standard, the schema
> is yours, and that split is the whole reason this is cheap to adopt.
""",
 "steps": [
  ("md", MITIGATES + "> Turns 'which agents are allowed here' from a "
         "convention into a check, and turns 'is this one still wanted' from "
         "an audit question into a leaver event. Closes A1.11 at the door.\n\n"
         "## 2 · Provisioning an agent the same way you provision a person"),
  ("html", D.flow(
    [D.column("system of record", [
       D.card("&#127970;", "HR / IdP", "the one place a joiner, mover or leaver "
              "is recorded", colour=D.GOOD),
     ]),
     D.column("scim protocol", [
       D.card("&#128100;", "POST /Users", "a person joins", colour=D.SECURE),
       D.card("&#129302;", "POST /Agents", "an agent is deployed — same "
              "protocol, your own schema URN", colour=D.DEFEND),
       D.card("&#9940;", "PATCH active:false", "a leaver, or a retirement. One "
              "call, and every consumer finds out", colour=D.SECURE,
              note="NOT DELETE — THE RECORD SURVIVES"),
     ]),
     D.column("agent registry", [
       D.card("&#128220;", "the registry", "owner is a $ref to a User, not a "
              "string. Expiry is on the registration, not the credential",
              colour=D.DEFEND),
     ]),
     D.column("admission", [
       D.card("&#128737;&#65039;", "the orchestrator", "checks the attested "
              "SPIFFE ID against the registry, and resolves the owner ref "
              "before it admits anything", colour=D.BAD, note="R2"),
     ])],
    caption="The point of using SCIM rather than a table is the middle column: "
            "the leaver event that already exists is the one that retires the "
            "agent, and the owner reference is what makes it cascade."),
  ),
("md", "## 3 · Admission, and the two entries that fail it"),
("md", "## 4 · Sam leaves. One SCIM `PATCH`, and what it does not reach\n\n"
         "This is the part a registry without a protocol behind it gets wrong. "
         "Sam's leaver event fires correctly — his own account is deactivated "
         "the same afternoon. The agent he deployed keeps running."),
  *skill_steps('identity/nhi-lifecycle-audit',
               "## 2 · The check, as a skill\n\n`cybertravels-svc` was created for a proof of concept in March and is still authenticating. The skill provisions agents as SCIM resources with an owner *reference*, then runs Sam's leaver event and re-runs admission — because a reference can be followed and a name in a text field cannot."),
],
 "expect": "An agent is provisioned as a SCIM resource whose owner is a `$ref` "
           "to a `User`. Four agents present identities and one is admitted — "
           "unregistered, orphaned and lapsed are all refused. Sam's leaver "
           "event is a single `PATCH {active: false}` on `/Users`, and because "
           "admission resolves the owner reference, his agent is refused on the "
           "next call. The orphan query returns one result.",
 "challenge": "Count your non-human identities and how many have a named human "
              "owner that resolves to a live account. The difference is the set "
              "nobody can revoke during an incident, because nobody can be asked "
              "whether it is still needed. Then check whether your IdP's SCIM "
              "connector can carry a custom resource type — most can, and it is "
              "usually a configuration rather than a project.",
},

"A2.6": {
 "concept": """
**Mitigates: T6 Intent Breaking, direct and indirect · T1 Memory Poisoning · T12 Communication Poisoning.**

This is the control for the largest risk in Chapter 1.

A1.3 worked because the context window is one flat string. Everything —
operator instruction, user question, retrieved document, tool result, peer
message — arrives as tokens with no marker for where it came from. The
distinction the operator believed in is destroyed by the concatenation.

The control is to **stop flattening**: attach an origin to every span *before*
assembly, carry it everywhere the span goes, and make one rule out of it.

> **Only spans from a trusted origin may select a tool.**

Three properties do the work:

**Tag at every ingress point.** Not just retrieval — tool results, MCP tool
descriptions, memory reads, and inter-agent messages are all ingress. A path you
did not tag is a path with no control on it.

**Carry the tag into memory.** This is what stops A1.4. A summary written from a
trust-0 document is itself trust-0, and if the tag is dropped on write the
poison becomes a fact.

**Let untrusted content still be useful.** The document is read, summarised,
quoted and reasoned about. What it may not do is choose an action. Refusing to
*read* untrusted content would refuse the entire use case.

Note what this does not do: it does not detect malicious text. It never looks at
the content at all, which is exactly why rephrasing does not defeat it.
""",
 "steps": [
  ("md", MITIGATES + "> The largest control in the chapter. It never inspects "
         "content, so rewriting the payload does not help — the check is on "
         "**origin**, which the attacker cannot change.\\n\\n## 2 · The control"),

  ("md", "## 2 · Checking the ingress paths, as a skill\\n\\n"
         "Tagging origin is the control; knowing which of CyberTravels' paths "
         "actually reaches the model without one is the audit. The procedure "
         "inventories every untrusted ingestion path — hotel descriptions, "
         "booking notes, uploaded vouchers, web fetches, and the one everybody "
         "forgets, **tool results** — and checks each for a screening step and "
         "for whether provenance survives into context. Note its confidence "
         "ceiling: PARTIAL, and not negotiable, because no detector is a "
         "boundary. This is the file in this repository:"),
  ("skill", "attestation/input-injection-screening-verifier"),
  ("skill_script", "attestation/input-injection-screening-verifier/scripts/input_injection_screening_verifier.py"),
],
 "expect": "The skill loads and reports its shape. Its ceiling is the lesson: a "
           "screening step is evidence of effort, not of protection, so the "
           "verdict is capped at PARTIAL however good the detector's benchmark "
           "looks — and the combination it flags, private data reachable plus "
           "untrusted content plus egress, is the one that turns a summary into "
           "an exfiltration.",
 "challenge": "List every place text enters your agent's context and check which "
              "of them attaches an origin. The untagged ones are the paths where "
              "this control does not exist, whatever the design document says.",
},

"A2.7": {
 "concept": """
**Mitigates: T8 Repudiation & Untraceability · T13 Rogue Agents.**

A1.14 showed a log that was complete for debugging and empty for investigation.
This is the record that is not.

Four fields, each answering a question the tool-call log could not:

**The human principal** — who caused this. From A2.1.

**The agent identity and instance** — what performed it, and which run. From
A2.2, so it is attested rather than claimed.

**The delegation chain** — how authority got from the human to this action. From
A2.3, which is also what makes A1.17's laundering path visible.

**The motivating input, with its origin** — what made the agent decide. From
A2.6. This is the field that establishes root cause, and the one most often
missing, because logging tool calls feels like logging decisions.

Then the structural property, which is not a field: **the store must be outside
the agent's reach.** An agent with broad credentials can usually touch the
logging stack, and a record the actor can edit is not evidence. Append-only,
different credential, ideally different trust domain.

The test is not whether the log looks thorough. It is whether you can answer
"which user caused this, and what made it happen" without asking anyone.
""",
 "steps": [
  ("md", MITIGATES + "> Makes the incident answerable. Also the control an "
         "auditor asks for first, because a system that cannot attribute an "
         "action cannot be defended even on a quiet day.\\n\\n## 2 · The control"),
  *skill_steps('identity/attribution-ledger-check',
               '## 2 · The check, as a skill\n\nThe four questions an auditor asks about that $5,000 refund have to be answerable from one entry. The skill puts them to a single ledger record, and then tries to amend the record as the agent — because a complete log its subject can edit records what the agent wanted you to see.'),
],
 "expect": "One ledger entry answers all four investigation questions — the "
           "human principal, the attested workload and run, the delegation "
           "chain, and the motivating input with its origin — and the agent's "
           "attempt to amend the record is refused.",
 "challenge": "Take the last significant action one of your agents performed and "
              "try to fill in these four fields from what you actually logged. "
              "The missing one is almost always the motivating input.",
},
}
