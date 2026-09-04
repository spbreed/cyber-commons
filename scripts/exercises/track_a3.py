"""A3 — Controls: runtime, and the gateway.

Chapter 2 answered "who is calling" and "where did this text come from". This
chapter assumes both have already been defeated and asks what still holds.

Every control here binds below the model, where a persuaded agent cannot argue
with it. The chapter ends at the gateway, because that is what happens to all
of these controls once you run more than a handful of agents.

    A3.1  default-deny on the tool call   T2, T3, T6
    A3.2  sandboxed execution             T11, T2
    A3.3  egress control                  T2, T6, LLM02
    A3.4  budgets and stop conditions     T4, T10
    A3.5  validating what comes back      T5, T12, T7
    A3.6  approval that survives volume   T10, T15
    A3.7  the gateway                     all of the above, once
"""

MITIGATES = """
> **What this control closes.**
>
"""

from . import diagrams as D
from .skills import runtime_step

RUNTIME_STEP = runtime_step()

EXERCISES: dict[str, dict] = {

"A3.1": {
 "concept": """
**Mitigates: T2 Tool Misuse · T3 Privilege Compromise · T6 Intent Breaking.**

The tool call is the moment text becomes consequence. It is also the last point
where a decision can be made on **facts** — this identity, this tool, these
arguments, this resource — rather than on intent, which nobody can read.

**Start from the identity, and be very specific about it.** Not "the Workflow
Agent"; the SPIFFE ID A2.3 issued —
`spiffe://cybertravels.com/ns/prod/sa/workflow-agent` — and against it, an
entitlement written at full resolution: which tools, on which resources, with
which verbs. Everything else in this lesson is a consequence of writing the
entitlement down at that resolution. A policy phrased one notch vaguer cannot
express the distinction the attack turns on, and the vagueness is invisible
until it is exploited.

Default-deny then means the absence of a rule is a refusal. That sounds like a
detail and it is the entire control, because it changes what a mistake costs.
Under allow-by-default, a permission somebody forgot to restrict is available to
an attacker. Under deny-by-default, a permission somebody forgot to grant is a
broken feature — which someone reports on Monday morning, loudly, and which
harms nobody.

The policy takes four inputs and all four matter:

- **identity** — the attested workload identity, from A2.3
- **tool** — which capability
- **arguments** — the actual values, not the schema
- **resource** — which specific thing

Dropping the fourth is the most common weakening. `run_query` permitted for the
Workflow Agent is not the same as `run_query` permitted *on the bookings table*,
and A1.5 was the difference between those two sentences. The verb is the second
most common: `charge_card` entitled for payments is not `refund` entitled for
payments, and R1 is the entire distance between them.

This does not stop the agent being persuaded. It stops persuasion mattering,
which is a better place to stand.
""",
 "steps": [
  ("md", MITIGATES + "> Stands on the edge every topology shares: "
         "`agent_runtime -> tools`. Persuasion still happens; it just stops "
         "reaching anything.\n\n## 2 · The entitlement, at full resolution"),
("md", "## 3 · The same five calls, evaluated both ways"),

  ("md", "## 4 · Proving the baseline is default-deny, as a skill\\n\\n"
         "Writing the entitlement is one job; showing that CyberTravels' running "
         "role *is* the entitlement is another, and it is the one an auditor "
         "asks for. The procedure reads every inline and attached policy for the "
         "baseline, then measures granted-but-unused permissions against what "
         "the audit trail observed — which only means anything if the trail is "
         "intact, so incomplete coverage is a finding rather than a clean pass. "
         "This is the file in this repository:"),
  RUNTIME_STEP,
  ("skill", "attestation/iam-least-privilege-verifier"),
],
 "expect": "The skill loads and reports its shape. Two of its failure modes are "
           "the ones this lesson is about: counting managed-policy *names* "
           "instead of effective actions, and reading a low excess count as a "
           "pass while a wildcard sits in the policy — a wildcard is not a large "
           "number of permissions, it is an unbounded one.",
 "challenge": "Take one tool policy you have and check whether it names the "
              "resource *and* the verb. If it grants `run_query` rather than "
              "`SELECT on these tables`, it cannot express the difference that "
              "A1.5 and R1 both turn on.",
},

"A3.2": {
 "concept": """
**Mitigates: T11 Malicious Code Execution · T2 Tool Misuse.**

For an agent that runs code, the sandbox **is** the security boundary. Not the
prompt, not the code review, not the model's training. The question is never
"is there a sandbox" but "what does this one actually contain".

A1.8's lesson was that reach is a property of the environment, not of intent —
the benign task touched a private key because `open()` sees what the process
sees. So the control is to change what the process sees.

Four dimensions, and the fourth is the one teams get wrong:

**Filesystem.** A bounded working directory. Not the home directory, which holds
`.ssh`, `.aws` and `.config`.

**Process and syscall.** No spawning, no ptrace, resource ceilings so a runaway
loop is contained rather than fatal.

**Network.** No egress by default. Not "restricted" — none, and then an
explicit allow per destination the workload genuinely needs.

**Credentials.** The one people miss: **a sandbox with production credentials
mounted in it is not a sandbox.** Isolation of the filesystem is irrelevant if
the environment holds a token that reaches production over a network the
sandbox does permit. The strongest boundary in the world does not help when the
keys are inside it.

### Say it in the manifest, or you have not said it

"No egress by default" is a claim about a cluster, and a claim about a cluster
is worth what its manifest says. In Kubernetes that is two objects and they are
both required, because a `NetworkPolicy` is an **additive allow-list**: pods
that no policy selects are unrestricted, and policies never deny — they only
add permitted traffic to a pod that some policy has already made restricted.

So the pattern is: one policy that selects every pod in the namespace and
permits nothing, then one narrow policy per destination the agent needs. Delete
the first and the second stops being a restriction at all, silently, with every
pod still running and every test still green.

The same two-object shape appears in every cloud. On AWS a security group with
no egress rules plus one rule per endpoint, and an IAM policy whose `Condition`
binds the role to the workload identity rather than to a subnet. On GCP a
hierarchical firewall policy with a low-priority `deny` on `0.0.0.0/0` and
higher-priority `allow` rules. Different nouns, identical structure: deny
everything by construction, then name what is permitted, one destination at a
time.
""",
 "steps": [
  ("md", MITIGATES + "> Changes what the executing process can **reach**, which "
         "is the only variable A1.8 turned on. A sandbox holding production "
         "credentials contains nothing that matters.\n\n"
         "## 2 · The four dimensions, and the configuration that ships"),
("md", """## 3 · The network dimension, as a manifest

Two objects, both required. The first makes every pod in the namespace
restricted and permits nothing; the second adds back exactly one destination.

```yaml
# 1. Default-deny. Selects EVERY pod in the namespace, permits no egress and
#    no ingress. Without this object the policy below is not a restriction —
#    it is an allowance on a pod that was already unrestricted.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: prod-agents
spec:
  podSelector: {}                 # every pod
  policyTypes: [Ingress, Egress]  # both, or egress stays wide open
---
# 2. One destination, for one agent, selected by the same service account that
#    carries its SPIFFE ID. DNS is separate and explicit: without port 53 the
#    agent cannot resolve anything, which is a correct default and a confusing
#    first afternoon.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: workflow-agent-egress
  namespace: prod-agents
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: workflow-agent   # sa/workflow-agent
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels: {kubernetes.io/metadata.name: prod-data}
          podSelector:
            matchLabels: {app: bookings-db}
      ports:
        - {protocol: TCP, port: 5432}
    - to:
        - namespaceSelector:
            matchLabels: {kubernetes.io/metadata.name: kube-system}
          podSelector:
            matchLabels: {k8s-app: kube-dns}
      ports:
        - {protocol: UDP, port: 53}
```

Note what is **not** in the allow-list, and what that costs an attacker:
`169.254.169.254` — the cloud metadata service, which hands out the node's
credentials to anything that can reach it — is unreachable because nothing
named it, not because anybody thought of it. That is the property a deny-list
can never have.

The pod itself carries the other three dimensions:

```yaml
spec:
  serviceAccountName: workflow-agent
  automountServiceAccountToken: false   # no ambient cluster credential
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    seccompProfile: {type: RuntimeDefault}
  containers:
    - name: agent
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities: {drop: [ALL]}
      resources:
        limits: {cpu: "1", memory: 1Gi}
      volumeMounts:
        - {name: work, mountPath: /sandbox/work}   # the only writable path
  volumes:
    - name: work
      emptyDir: {sizeLimit: 512Mi}
```

The same shape on **AWS** — a security group whose egress rules are the whole
allow-list, and a role whose trust policy binds to the workload rather than to
the subnet:

```hcl
resource "aws_security_group" "workflow_agent" {
  name   = "workflow-agent"
  vpc_id = var.vpc_id
  # No `egress` block at all: an AWS security group with no egress rules
  # permits nothing outbound. The default SG that ships with a VPC allows
  # 0.0.0.0/0 — never attach that one.
}

resource "aws_vpc_security_group_egress_rule" "bookings_db" {
  security_group_id            = aws_security_group.workflow_agent.id
  referenced_security_group_id = aws_security_group.bookings_db.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}
```

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": "arn:aws:s3:::cybertravels-itineraries/*",
    "Condition": {
      "StringEquals": {
        "aws:PrincipalTag/spiffe-id":
          "spiffe://cybertravels.com/ns/prod/sa/workflow-agent"
      },
      "Bool": {"aws:SecureTransport": "true"}
    }
  }]
}
```

And on **GCP**, where the deny is explicit and priority-ordered rather than
implicit:

```yaml
# gcloud compute network-firewall-policies rules create ...
- priority: 65000            # lowest priority: the floor
  direction: EGRESS
  action: deny
  match: {destIpRanges: ["0.0.0.0/0"]}
- priority: 1000             # higher priority wins
  direction: EGRESS
  action: allow
  targetSecureTags: ["tagValues/workflow-agent"]
  match:
    destIpRanges: ["10.20.0.0/24"]
    layer4Configs: [{ipProtocol: tcp, ports: ["5432"]}]
```

Three products, one structure: deny everything by construction, then name what
is permitted, one destination at a time."""),
  ("md", "## 4 · Evaluate the manifest, including the way it is usually broken"),
],
 "expect": "The same code is executed against three environments: unsandboxed it "
           "reaches a private key, two credentials and the whole network; "
           "sandboxed with production credentials mounted it still reaches both "
           "credentials and the production database; only the third contains it. "
           "Then the two NetworkPolicy objects are evaluated — 2 of 5 connections "
           "permitted, with cloud metadata and the exfiltration target both "
           "refused for not being named. Deleting `default-deny-all` leaves "
           "workflow-agent unchanged and silently opens every other pod in the "
           "namespace.",
 "challenge": "Run `kubectl get networkpolicy -A` and look for a policy with an "
              "empty `podSelector` and `policyTypes: [Ingress, Egress]`. If "
              "there isn't one in the namespace your agents run in, every "
              "narrow policy you have written is an allowance rather than a "
              "restriction, and every pod nobody wrote a policy for has the "
              "internet.",
},

"A3.3": {
 "concept": """
**Mitigates: T2 Tool Misuse · T6 Intent Breaking · LLM02 Sensitive Information Disclosure.**

Egress is the highest-leverage control in the architecture, for a structural
reason: **every exfiltration path ends at the network boundary**, no matter how
the agent was persuaded to take it.

Injection, tool misuse, a compromised MCP server, model-authored code, a
poisoned peer message — all of them converge on the same final step. Data leaves.
A control at that step does not need to understand what happened upstream, which
is exactly what makes it robust: it is the one place where you do not have to
predict the attack.

Two rules that decide whether it works:

**Allow-list, never deny-list.** You cannot enumerate the internet. A deny-list
blocks the destinations you thought of.

**Specific destinations.** `*.googleapis.com` or `*.s3.amazonaws.com` is not an
egress policy — anyone can create a bucket in those namespaces, and A1.3's
attacker will. The allow-list holds the destinations this workload actually
needs, and there are usually fewer than five.

And one placement rule: enforce it **where the agent cannot rewrite it** — the
network layer, the sidecar, the gateway. An egress check inside the agent's own
process is a suggestion to the component being attacked.

The cost is honest: an agent that needs the open internet cannot have this
control, and that is a design decision to make deliberately rather than by
default.
""",
 "steps": [
  ("md", MITIGATES + "> The one control that does not need to know how the "
         "attack worked, because every exfiltration path ends here.\\n\\n"
         "## 2 · The control"),

  ("md", "## 2 · Probing the sandbox, as a skill\\n\\n"
         "An allow-list in a config file is a claim. CyberTravels' Coding Agent "
         "runs model-authored code, so the claim worth making is *this runtime "
         "has no egress*, and that one is settled by probing, in an environment "
         "you own. The procedure names the residual paths — DNS first, because "
         "it is the one that has actually been used — and requires you to record "
         "what you did **not** test, because a probe list is a statement about "
         "coverage. This is the file in this repository:"),
  RUNTIME_STEP,
  ("skill", "attestation/sandbox-egress-verifier"),
],
 "expect": "The skill loads and reports its shape. Its ceiling is PARTIAL and "
           "not negotiable: a configuration that looks right is not a PASS, and "
           "probing general HTTP while leaving DNS alone tests the path nobody "
           "uses. The untested list is part of the output, not an omission from "
           "it.",
 "challenge": "Write the allow-list for one agent by listing the hosts it "
              "genuinely calls. If it is under five, you can ship this control "
              "this week; if it is unbounded, that is the finding.",
},

"A3.4": {
 "concept": """
**Mitigates: T4 Resource Overload · T10 Overwhelming Human-in-the-Loop.**

A budget is what makes "autonomous" a bounded word.

A1.13's loop had no exit condition, so it ran until something outside it
intervened. A ceiling turns that into a defined worst case — and a worst case is
the thing you can actually put in a design document, an incident plan or a risk
register.

Four ceilings, because they bound different failures:

**Tokens or cost.** The visible one. Bounds the bill.

**Wall-clock time.** Bounds a workflow step that never returns.

**Actions.** Bounds *consequence*, and it is the one that matters for security.
Twenty tool calls is a very different blast radius from two thousand, whatever
either costs.

**Downstream calls per target.** Bounds harm to other people. A1.13's damage was
not the token spend, it was the capacity taken from everybody else.

Two design rules:

**Terminate, do not degrade.** A loop that hits a ceiling and keeps going with a
smaller model or a shorter context has not been bounded, it has been redirected.

**Make the ceiling visible in the output.** `stopped_by: action_budget` is a
signal to a human that this run is incomplete. Silent truncation is how a
partial result becomes a reported success, which is A1.16 arriving through a
different door.
""",
 "steps": [
  ("md", MITIGATES + "> Turns an unbounded loop into a defined worst case, and "
         "bounds the harm to **other people's** capacity, not just your "
         "bill.\\n\\n## 2 · The control"),
],
 "expect": "The impossible task from A1.13 now stops after six steps, halted by "
           "the per-target ceiling — before the token or action budgets are "
           "anywhere near exhausted — and the result carries `complete: False` "
           "rather than reporting what it managed.",
 "challenge": "Check whether your agent's budget bounds calls per downstream "
              "target. If it only bounds tokens, your cost is protected and the "
              "service your agent hammers is not.",
},

"A3.5": {
 "concept": """
**Mitigates: T5 Cascading Hallucination · T12 Communication Poisoning · T7 Misaligned Behaviour.**

Everything that comes back into the context is an input: tool results, peer
messages, retrieved documents, a sub-agent's summary. A1.10 and A1.12 both
happened because those inputs were trusted in proportion to how internal they
looked rather than to how checked they were.

Two different checks, and conflating them is the mistake:

**Schema validation** asks *is this the right shape*. Cheap, mechanical, catches
malformed input and injection through a field that was supposed to be an
integer. It is necessary and it proves nothing about truth — a perfectly-formed
JSON object can assert anything.

**Verification** asks *is this claim true, according to something that is true
independently of the agent*. A test that passes. A query whose result you can
re-run. A file that exists. A signature that checks.

The rule that follows: **a claim may not propagate past the hop that produced
it without a verification result attached.** Not "was it plausible" — was it
checked, by what, and what did that return.

That single field is what stops A1.12's cascade, because confidence can no
longer rise as evidence disappears: the evidence field travels with the claim,
and an empty one is visible at every hop.

It is also the answer to A1.16, which is why "ask the model whether it
succeeded" is not a verifier — it is the same component grading its own work.
""",
 "steps": [
  ("md", MITIGATES + "> Stops a claim propagating without evidence attached. "
         "Schema validity is not truth: a well-formed object can assert "
         "anything.\\n\\n## 2 · The control"),
],
 "expect": "Four messages are checked twice. A schema-perfect, high-confidence "
           "claim is refuted by the oracle; a claim with no oracle stops with "
           "`unverifiable` rather than silently becoming true; a malformed "
           "message is caught by the schema; and only the verified claim "
           "propagates.",
 "challenge": "Find one place a sub-agent's output becomes another agent's "
              "input and ask what oracle checks it. If the answer is the "
              "model's own confidence, that is the component grading its own work.",
},

"A3.6": {
 "concept": """
**Mitigates: T10 Overwhelming Human-in-the-Loop · T15 Human Manipulation.**

A1.15 showed approval collapsing under volume while still reporting 100%
coverage. The fix is not a better reviewer or a nicer queue. It is **sending
fewer things**.

Route by **reversibility**, because that is what a human is actually useful for:

- **Reversible, bounded** — no approval. Policy from A3.1 decides, and the
  action can be undone if it was wrong.
- **Reversible, expensive to undo** — no approval, but recorded prominently and
  sampled after the fact.
- **Irreversible or externally visible** — approval, every time. Sending mail,
  paying, publishing, deleting without a backup, rotating a credential.

The test for whether your gate will hold is arithmetic, not intent: **how many
requests per day reach a human?** If the answer is more than a person can
consider properly, the control is already a click, and the number tells you so
before the incident does.

The T15 half is one line of implementation and easy to skip: **mark
machine-generated content as machine-generated** wherever a human reads it. A
recommendation that arrives with institutional formatting recruits authority it
has not earned. Labelling it does not stop anyone acting on it — it restores the
scepticism they would apply to a colleague.
""",
 "steps": [
  ("md", MITIGATES + "> Sends **fewer** things to humans, so the ones that "
         "arrive are read. The test is arithmetic: how many per day reach a "
         "person.\\n\\n## 2 · The control"),

  ("md", "## 2 · Deciding what needs a human, as a skill\\n\\n"
         "Routing by reversibility only works if somebody has computed what each "
         "CyberTravels agent can actually reach and damage in one run. That is a "
         "blast-radius review, and its output is an autonomy level rather than "
         "an opinion: enumerate the reachable actions with attacker-chosen "
         "arguments, not the happy path, and include time-to-stop, because how "
         "fast you can halt a run is part of how much it can cost. This is the "
         "file in this repository:"),
  RUNTIME_STEP,
  ("skill", "architecture/blast-radius-review"),
],
 "expect": "The skill loads and reports its shape. The failure mode to carry "
           "into your own estate is the last one: raising an agent's autonomy "
           "because it has been reliable. Reliability is a measurement of the "
           "happy path; blast radius is a measurement of the worst one, and only "
           "the second bounds what an approval gate is for.",
 "challenge": "Count how many approvals your agents generate daily and compare "
              "it with 25. If you are above it, decide which actions are "
              "reversible enough to be handled by policy instead — that list is "
              "usually most of them.",
},

"A3.7": {
 "concept": """
**Mitigates: every threat in this chapter, at one enforcement point.**

Everything in Chapters 2 and 3 works. The problem is where it lives.

At one agent, the controls sit in the agent, and that is fine. At fifty, it
stops being fine for reasons that have nothing to do with security engineering:

- Each team implements provenance, budgets and egress slightly differently.
- Nobody can answer "is this control on, everywhere" without reading fifty
  repositories.
- A new agent starts at zero and re-earns every control by hand.
- Fixing a control means fifty pull requests and a migration.

The **gateway** is the same controls, moved to a point every call must pass
through. It holds identity (A2.1–A2.3), policy (A3.1), egress (A3.3), budgets
(A3.4) and audit (A2.7). An agent that implements none of them still gets all of
them, because the enforcement is no longer the agent's responsibility.

It also solves a problem nothing else does: **downstream systems that cannot
consume a delegated identity.** A legacy database or a vendor API that only
understands a static credential forces that credential back into agent code —
undoing A2.3 completely. The gateway holds it instead, authorises the *user*
before the call, and presents the static credential onward. The agent never sees
it.

The honest cost: the gateway is now a single point of failure and a very
attractive target. It has to be operated accordingly.
""",
 "steps": [
  ("md", MITIGATES + "> Not a new control. The same controls, at a point every "
         "call passes through — and the only answer to a downstream that cannot "
         "consume delegated identity.\\n\\n## 2 · The control"),

  ("md", "## 2 · Proving every call goes through it, as a skill\\n\\n"
         "A gateway is only a choke point if nothing routes around it, and "
         "\"nothing routes around it\" is not a fact you can read off a route "
         "table. The procedure tests reachability from inside the deployment, "
         "covers the paths people forget — tool-initiated calls, background "
         "jobs, retries — and records each guardrail's **action**, because a "
         "filter set to observe is a filter that is switched on and stopping "
         "nothing. This is the file in this repository:"),
  RUNTIME_STEP,
  ("skill", "attestation/llm-gateway-guardrail-verifier"),
],
 "expect": "The skill loads and reports its shape. Its confidence is HIGH only "
           "where egress is enforced below the application — the gateway is a "
           "choke point because the network makes it one, not because the SDK "
           "was configured to point at it, and an application-level base URL is "
           "a default, not a control.",
 "challenge": "Count your agents. If it is more than five, work out how you "
              "would currently answer 'is egress control on for all of them' — "
              "and how long that would take.",
},
}
