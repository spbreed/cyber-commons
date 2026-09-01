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

EXERCISES: dict[str, dict] = {

"A3.1": {
 "concept": """
**Mitigates: T2 Tool Misuse · T3 Privilege Compromise · T6 Intent Breaking.**

The tool call is the moment text becomes consequence. It is also the last point
where a decision can be made on **facts** — this identity, this tool, these
arguments, this resource — rather than on intent, which nobody can read.

Default-deny means the absence of a rule is a refusal. That sounds like a
detail and it is the entire control, because it changes what a mistake costs.
Under allow-by-default, a permission somebody forgot to restrict is available to
an attacker. Under deny-by-default, a permission somebody forgot to grant is a
broken feature — which someone reports on Monday morning, loudly, and which
harms nobody.

The policy takes four inputs and all four matter:

- **identity** — the workload, from A2.1
- **tool** — which capability
- **arguments** — the actual values, not the schema
- **resource** — which specific thing

Dropping the fourth is the most common weakening. `run_query` permitted for the
reports agent is not the same as `run_query` permitted *on the reports table*,
and A1.5 was the difference between those two sentences.

This does not stop the agent being persuaded. It stops persuasion mattering,
which is a better place to stand.
""",
 "steps": [
  ("md", MITIGATES + "> Stands on the edge every topology shares: "
         "`agent_runtime -> tools`. Persuasion still happens; it just stops "
         "reaching anything.\\n\\n## 2 · The control"),
  ("py", '''POLICY = [
 # (identity,        tool,        resource-prefix,   allowed-args)
 ("reports-agent", "run_query",  "table:reports",   {"SELECT"}),
 ("reports-agent", "send_email", "domain:corp.example", {"*"}),
 ("billing-agent", "run_query",  "table:invoices",  {"SELECT", "UPDATE"}),
]

def decide(identity, tool, resource, verb, default_deny=True):
    """Four inputs. No matching rule means refuse."""
    for ident, t, res_prefix, verbs in POLICY:
        if ident == identity and t == tool and resource.startswith(res_prefix):
            if "*" in verbs or verb in verbs:
                return True, f"rule {ident}/{t}/{res_prefix}"
            return False, f"verb {verb} not permitted on {res_prefix}"
    return (False, "no rule matches - default deny") if default_deny else (True, "allowed by default")

CALLS = [
 ("reports-agent", "run_query",  "table:reports",  "SELECT"),   # intended
 ("reports-agent", "run_query",  "table:secrets",  "SELECT"),   # A1.5, resource
 ("reports-agent", "run_query",  "table:reports",  "DELETE"),   # A1.5, verb
 ("reports-agent", "send_email", "domain:evil.example", "*"),   # A1.3, exfil
 ("reports-agent", "drop_table", "table:reports",  "*"),        # tool never granted
]

for mode in (False, True):
    label = "DEFAULT-DENY" if mode else "allow-by-default"
    allowed = 0
    print(f"{label}:")
    for identity, tool, resource, verb in CALLS:
        ok, why = decide(identity, tool, resource, verb, default_deny=mode)
        allowed += ok
        print(f"   {tool:11s}{resource:22s}{verb:7s}{'ALLOW' if ok else 'deny ':6s}{why}")
    print(f"   -> {allowed}/{len(CALLS)} permitted\\n")

print("The only call that should succeed is the first. Under allow-by-default")
print("four do, and each one is a real risk from Chapter 1 walking through.")
print()
print("Note the third row: same identity, same tool, same resource, refused on")
print("the verb. Authorization attached to the tool instead of the call cannot")
print("express that distinction at all.")
assert sum(decide(*c, default_deny=True)[0] for c in CALLS) == 1
'''),
 ],
 "expect": "Five tool calls are evaluated twice. Under allow-by-default four "
           "succeed, each one a Chapter 1 risk walking through. Under "
           "default-deny only the intended call survives — including a refusal "
           "on the verb for an otherwise-permitted identity, tool and resource.",
 "challenge": "Take one tool policy you have and check whether it names the "
              "resource. If it grants `run_query` rather than `run_query on "
              "these tables`, it cannot express the difference that A1.5 turned on.",
},

"A3.2": {
 "concept": """
**Mitigates: T11 Unexpected Code Execution · T2 Tool Misuse.**

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

**Network.** No egress by default. Combined with A3.3 this is what makes an
exfiltration primitive useless.

**Credentials.** The one people miss: **a sandbox with production credentials
mounted in it is not a sandbox.** Isolation of the filesystem is irrelevant if
the environment holds a token that reaches production over a network the
sandbox does permit. The strongest boundary in the world does not help when the
keys are inside it.
""",
 "steps": [
  ("md", MITIGATES + "> Changes what the executing process can **reach**, which "
         "is the only variable A1.8 turned on. A sandbox holding production "
         "credentials contains nothing that matters.\\n\\n## 2 · The control"),
  ("py", '''HOST = {"fs": ["/home/agent/work/data.csv", "/home/agent/.ssh/id_ed25519",
                "/etc/passwd"],
        "env": {"AWS_ACCESS_KEY_ID": "AKIA-EXAMPLE-NOT-REAL",
                "DATABASE_URL": "postgres://prod-db/main"},
        "net": ["prod-db:5432", "169.254.169.254:80", "0.0.0.0/0"]}

def sandbox(workdir="/sandbox/work", allow_net=(), keep_env=()):
    return {"fs": [p for p in HOST["fs"] if p.startswith(workdir)] + [f"{workdir}/data.csv"],
            "env": {k: v for k, v in HOST["env"].items() if k in keep_env},
            "net": list(allow_net)}

def reach(env, code):
    out = []
    if "open("    in code: out += [f"file:{p}" for p in sorted(env["fs"])]
    if "environ"  in code: out += [f"env:{k}"  for k in sorted(env["env"])]
    if "connect"  in code: out += [f"net:{h}"  for h in sorted(env["net"])]
    return out

CODE = "import os; d=os.environ; open('/home/agent/.ssh/id_ed25519'); connect('x')"

configs = {
 "no sandbox":                    HOST,
 "sandbox, prod creds mounted":   sandbox(allow_net=["prod-db:5432"],
                                          keep_env=("AWS_ACCESS_KEY_ID", "DATABASE_URL")),
 "sandbox, no ambient creds":     sandbox(),
}
for label, env in configs.items():
    r = reach(env, CODE)
    print(f"{label:32s}reached {len(r)}")
    for item in r:
        print(f"      {item}")
    print()

print("The middle configuration is the one that ships. The filesystem is")
print("isolated, the syscalls are filtered, and the environment holds a")
print("credential that reaches production over a network hop the sandbox allows.")
print()
print("Isolation of the wrong dimension is not a weaker control. It is the")
print("appearance of one.")
assert reach(configs["sandbox, no ambient creds"], CODE) and \\
       not any("env:" in r for r in reach(configs["sandbox, no ambient creds"], CODE))
'''),
 ],
 "expect": "The same code is executed against three environments. Unsandboxed it "
           "reaches a private key, two credentials and the whole network. "
           "Sandboxed but with production credentials mounted it still reaches "
           "both credentials and the production database. Only the third — no "
           "ambient credentials — contains it.",
 "challenge": "Print the environment of one sandbox you run code in. Every "
              "credential in it is reachable by anything that executes there, "
              "and the isolation you paid for does not apply to any of them.",
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
  ("py", '''ALLOW = {"api.corp.example", "reports-db.corp.example"}
DENY_SUFFIXES = {".evil.example"}          # the deny-list, for comparison

def by_denylist(host):
    return not any(host.endswith(s) for s in DENY_SUFFIXES)

def by_allowlist(host):
    return host in ALLOW                    # exact, not suffix

DESTINATIONS = [
 ("api.corp.example",              "the one it actually needs"),
 ("archive.evil.example",          "A1.3's exfiltration target"),
 ("attacker-bucket.s3.amazonaws.com", "a bucket anyone can create"),
 ("169.254.169.254",               "cloud metadata - every credential"),
 ("pastebin.example",              "not on anyone's deny-list"),
]

print(f"{'destination':38s}{'deny-list':12s}{'allow-list':12s}note")
for host, note in DESTINATIONS:
    d, a = by_denylist(host), by_allowlist(host)
    print(f"{host:38s}{'allow' if d else 'block':12s}{'allow' if a else 'block':12s}{note}")

leaked = [h for h, _ in DESTINATIONS if by_denylist(h) and h not in ALLOW]
print(f"\\ndeny-list lets through : {len(leaked)}  {leaked}")
print(f"allow-list lets through : {sorted(h for h, _ in DESTINATIONS if by_allowlist(h))}")
print()
print("The deny-list blocked exactly the destination somebody had already")
print("thought of. It cannot be completed, because the internet cannot be")
print("enumerated.")
print()
print("Placement matters as much: this check belongs in the network path, not")
print("in the agent. A check inside the process being attacked is advice.")
assert len(leaked) == 3 and len([h for h, _ in DESTINATIONS if by_allowlist(h)]) == 1
'''),
 ],
 "expect": "Five destinations are evaluated both ways. The deny-list permits "
           "three exfiltration paths — a public-cloud bucket namespace anyone can "
           "register in, the cloud metadata address, and a host nobody listed — "
           "while the exact allow-list permits only the one destination the "
           "workload needs.",
 "challenge": "Write the allow-list for one agent by listing the hosts it "
              "genuinely calls. If it is under five, you can ship this control "
              "this week; if it is unbounded, that is the finding.",
},

"A3.4": {
 "concept": """
**Mitigates: T4 Resource Overload · T10 Overwhelming Human-in-the-Loop.**

A budget is what makes "autonomous" a bounded word.

A1.12's loop had no exit condition, so it ran until something outside it
intervened. A ceiling turns that into a defined worst case — and a worst case is
the thing you can actually put in a design document, an incident plan or a risk
register.

Four ceilings, because they bound different failures:

**Tokens or cost.** The visible one. Bounds the bill.

**Wall-clock time.** Bounds a workflow step that never returns.

**Actions.** Bounds *consequence*, and it is the one that matters for security.
Twenty tool calls is a very different blast radius from two thousand, whatever
either costs.

**Downstream calls per target.** Bounds harm to other people. A1.12's damage was
not the token spend, it was the capacity taken from everybody else.

Two design rules:

**Terminate, do not degrade.** A loop that hits a ceiling and keeps going with a
smaller model or a shorter context has not been bounded, it has been redirected.

**Make the ceiling visible in the output.** `stopped_by: action_budget` is a
signal to a human that this run is incomplete. Silent truncation is how a
partial result becomes a reported success, which is A1.15 arriving through a
different door.
""",
 "steps": [
  ("md", MITIGATES + "> Turns an unbounded loop into a defined worst case, and "
         "bounds the harm to **other people's** capacity, not just your "
         "bill.\\n\\n## 2 · The control"),
  ("py", '''class Budget:
    def __init__(self, tokens=50_000, seconds=60, actions=20, per_target=5):
        self.limits = {"tokens": tokens, "seconds": seconds,
                       "actions": actions, "per_target": per_target}
        self.used = {"tokens": 0, "seconds": 0, "actions": 0}
        self.targets = {}
    def spend(self, tokens=0, seconds=0, action=None, target=None):
        self.used["tokens"] += tokens
        self.used["seconds"] += seconds
        if action: self.used["actions"] += 1
        if target:
            self.targets[target] = self.targets.get(target, 0) + 1
            if self.targets[target] > self.limits["per_target"]:
                return False, f"per_target ({target})"
        for k in ("tokens", "seconds", "actions"):
            if self.used[k] > self.limits[k]:
                return False, k
        return True, None

def loop(budget):
    """A task that cannot succeed - A1.12's exact scenario, now bounded."""
    steps = 0
    while True:
        steps += 1
        ok, hit = budget.spend(tokens=1800, seconds=0.4, action="query",
                               target="reports-db")
        if not ok:
            return {"steps": steps, "stopped_by": hit, "complete": False}

b = Budget()
r = loop(b)
print(f"steps taken : {r['steps']}")
print(f"stopped by  : {r['stopped_by']}")
print(f"complete    : {r['complete']}   <- visible in the output, not silent")
print()
print(f"{'ceiling':14s}{'limit':>9}{'used':>9}")
for k in ("tokens", "seconds", "actions"):
    print(f"{k:14s}{b.limits[k]:>9}{round(b.used[k], 1):>9}")
print(f"{'per_target':14s}{b.limits['per_target']:>9}{b.targets['reports-db']:>9}")
print()
print("per_target fired first, at 6 calls - long before the token budget or the")
print("action budget. That is the ceiling that protects everyone else, and it is")
print("the one most budgets do not have.")
print()
print("`complete: False` is the other half. A run that stops silently and")
print("reports what it managed becomes A1.15 with extra steps.")
assert r["stopped_by"].startswith("per_target") and not r["complete"]
'''),
 ],
 "expect": "The impossible task from A1.12 now stops after six steps, halted by "
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
messages, retrieved documents, a sub-agent's summary. A1.9 and A1.11 both
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

That single field is what stops A1.11's cascade, because confidence can no
longer rise as evidence disappears: the evidence field travels with the claim,
and an empty one is visible at every hop.

It is also the answer to A1.15, which is why "ask the model whether it
succeeded" is not a verifier — it is the same component grading its own work.
""",
 "steps": [
  ("md", MITIGATES + "> Stops a claim propagating without evidence attached. "
         "Schema validity is not truth: a well-formed object can assert "
         "anything.\\n\\n## 2 · The control"),
  ("py", '''SCHEMA = {"claim": str, "confidence": float, "verified_by": (str, type(None))}

def schema_ok(msg):
    return all(k in msg and isinstance(msg[k], t) for k, t in SCHEMA.items())

GROUND_TRUTH = {"libfoo has no known CVEs": False,      # it has one
                "test_login passes": True}

def verify(claim):
    """Independent: reads ground truth, not the sender's opinion."""
    if claim not in GROUND_TRUTH:
        return None, "no oracle for this claim"
    return GROUND_TRUTH[claim], "checked against the advisory database"

def propagate(msg, hops=3):
    """A claim may not travel without a verification result attached."""
    if not schema_ok(msg):
        return {"stopped": "malformed"}
    result, how = verify(msg["claim"])
    if result is None:
        return {"stopped": "unverifiable", "claim": msg["claim"], "why": how}
    if result is False:
        return {"stopped": "refuted", "claim": msg["claim"], "by": how}
    return {"propagated": msg["claim"], "verified_by": how, "hops": hops}

MESSAGES = [
 {"claim": "libfoo has no known CVEs", "confidence": 0.9, "verified_by": None},
 {"claim": "test_login passes",        "confidence": 0.5, "verified_by": None},
 {"claim": "the refund was approved",  "confidence": 0.99, "verified_by": None},
 {"claim": "libfoo is fine",           "confidence": "high", "verified_by": None},
]
for m in MESSAGES:
    print(f"   schema_ok={str(schema_ok(m)):5s} -> {propagate(m)}")

print()
print("The first message is schema-perfect and confident and false. Schema")
print("validation passed it; the oracle refuted it.")
print()
print("The third is unverifiable - no oracle exists. That is a legitimate")
print("outcome and it must not silently become 'true'. It stops here with a")
print("reason, which is what A1.11's cascade never had.")
assert propagate(MESSAGES[0])["stopped"] == "refuted"
assert propagate(MESSAGES[2])["stopped"] == "unverifiable"
assert "propagated" in propagate(MESSAGES[1])
'''),
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

A1.14 showed approval collapsing under volume while still reporting 100%
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
  ("py", '''ACTIONS = {
 "read_report":      {"reversible": True,  "external": False},
 "write_draft":      {"reversible": True,  "external": False},
 "update_ticket":    {"reversible": True,  "external": False},
 "delete_row":       {"reversible": False, "external": False},
 "send_email":       {"reversible": False, "external": True},
 "issue_refund":     {"reversible": False, "external": True},
 "rotate_credential":{"reversible": False, "external": False},
}
DAILY_VOLUME = {"read_report": 400, "write_draft": 120, "update_ticket": 260,
                "delete_row": 6, "send_email": 3, "issue_refund": 2,
                "rotate_credential": 1}

def route(action):
    a = ACTIONS[action]
    if not a["reversible"] or a["external"]:
        return "human approval"
    return "policy only"

CAREFUL_CAPACITY = 25
print(f"{'action':20s}{'reversible':12s}{'external':10s}{'routing':16s}per day")
to_human = 0
for name in sorted(ACTIONS):
    a, r = ACTIONS[name], route(name)
    if r == "human approval": to_human += DAILY_VOLUME[name]
    print(f"{name:20s}{str(a['reversible']):12s}{str(a['external']):10s}"
          f"{r:16s}{DAILY_VOLUME[name]}")

total = sum(DAILY_VOLUME.values())
print(f"\\nactions per day            : {total}")
print(f"reaching a human           : {to_human}")
print(f"a reviewer considers ~{CAREFUL_CAPACITY}/day properly")
print(f"gate holds?                : {to_human <= CAREFUL_CAPACITY}")
print()
print(f"Approving everything would send {total} a day to someone who can read")
print(f"{CAREFUL_CAPACITY}. Routing by reversibility sends {to_human}, and every one gets read.")

# the T15 half
FINDING = "libfoo has no known vulnerabilities"
print(f"\\nunlabelled : {FINDING}")
print(f"labelled   : [machine-generated, unverified] {FINDING}")
print("\\nThe label does not stop anyone acting on it. It restores the scepticism")
print("they would give a colleague saying the same sentence.")
assert to_human <= CAREFUL_CAPACITY
'''),
 ],
 "expect": "Routing by reversibility sends 12 actions a day to a human instead "
           "of 792, which is inside what one reviewer can consider properly — so "
           "the gate holds rather than degrading into a click — and "
           "machine-generated output is labelled where a person reads it.",
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
  ("py", '''LEGACY_DB_CREDENTIAL = "static-service-password"     # never leaves the gateway

REGISTRY = {"spiffe://corp/reports-agent": {"owner": "sam@corp", "expires": 9000}}
POLICY = {("reports-agent", "run_query", "table:reports"): {"SELECT"}}
EGRESS_ALLOW = {"reports-db.corp.example"}

AUDIT = []

def gateway(call):
    """One choke point: identity, registry, policy, egress, budget, audit."""
    checks = []
    def check(name, ok, why=""):
        checks.append((name, ok, why)); return ok

    if not check("identity", call["identity"] in REGISTRY, "attested and registered"):
        return {"allowed": False, "checks": checks}
    verbs = POLICY.get((call["agent"], call["tool"], call["resource"]), set())
    if not check("policy", call["verb"] in verbs, f"permitted verbs {sorted(verbs) or 'none'}"):
        return {"allowed": False, "checks": checks}
    if not check("egress", call["destination"] in EGRESS_ALLOW, "destination allow-list"):
        return {"allowed": False, "checks": checks}
    if not check("budget", call["calls_so_far"] < 5, "per-target ceiling"):
        return {"allowed": False, "checks": checks}

    # the agent never held this; the gateway attaches it on the way out
    AUDIT.append({"principal": call["principal"], "agent": call["agent"],
                  "tool": call["tool"], "resource": call["resource"]})
    return {"allowed": True, "checks": checks, "credential_attached": LEGACY_DB_CREDENTIAL[:6] + "..."}

BASE = {"identity": "spiffe://corp/reports-agent", "agent": "reports-agent",
        "principal": "dana@corp", "tool": "run_query", "resource": "table:reports",
        "verb": "SELECT", "destination": "reports-db.corp.example", "calls_so_far": 0}

CASES = {
 "the intended call":          BASE,
 "unregistered agent":         dict(BASE, identity="spiffe://corp/rogue-agent"),
 "verb not permitted":         dict(BASE, verb="DELETE"),
 "exfiltration destination":   dict(BASE, destination="archive.evil.example"),
 "over the per-target ceiling":dict(BASE, calls_so_far=9),
}
for label, call in CASES.items():
    r = gateway(call)
    failed = [n for n, ok, _ in r["checks"] if not ok]
    print(f"   {label:28s}{'ALLOWED' if r['allowed'] else 'denied at ' + failed[0]}")

print(f"\\naudit entries written: {len(AUDIT)}")
print(f"credential held by the agent: never - attached at the gateway")
print()
print("The agent implements none of this. Add a new agent tomorrow and it")
print("inherits every control by being on the other side of one hop.")
print()
print("And the legacy database, which cannot consume a delegated token, is")
print("reached with a static credential the agent has never seen - authorised")
print("against dana before the call was made.")
assert len(AUDIT) == 1 and gateway(CASES["unregistered agent"])["allowed"] is False
'''),
 ],
 "expect": "Five calls hit one gateway. The intended call is allowed and audited "
           "with the human principal attached; the unregistered agent, the "
           "unpermitted verb, the exfiltration destination and the "
           "over-budget call are each denied at the first check that catches "
           "them — and the legacy credential is attached at the gateway, never "
           "held by the agent.",
 "challenge": "Count your agents. If it is more than five, work out how you "
              "would currently answer 'is egress control on for all of them' — "
              "and how long that would take.",
},
}
