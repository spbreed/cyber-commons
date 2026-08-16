"""Function A — Architecture & Platform. A1 architect, A2 identity, A3 platform."""

EXERCISES: dict[str, dict] = {

# ------------------------------------------------------- A1 Security Architect
"A1.1": {
 "intro": "A threat model goes stale the moment the tool manifest changes — and "
          "adding a tool is not a code change, so nothing in your change process "
          "notices. The useful artefact is therefore not the model. It is the *diff*.",
 "steps": [
  ("py", '''from cybercommons import planes
W = planes.Tool

v1 = planes.Manifest("review-agent", [
    W("read_file"), W("search_code"),
    W("post_comment", writes=True, scope="project"),
], approval_required=set(), rung="L2.5")

v2 = planes.Manifest("review-agent", [
    W("read_file"), W("search_code"),
    W("post_comment", writes=True, scope="project"),
    W("merge_pr", writes=True, scope="project", reversible=False),   # added Tuesday
], approval_required=set(), rung="L2.5")

d = planes.diff_manifests(v1, v2)
print("added:  ", d["added"])
print("blast:  ", d["blast_before"], "→", d["blast_after"], f"(delta {d['delta']:+d})")
for p in d["new_problems"]:
    print("new problem:", p)
'''),
  ("md", "One line in a config file doubled the blast radius and introduced an "
         "irreversible action with no gate. No pull request touched the agent's "
         "code. This is why the review has to run against the manifest, "
         "continuously, and not against a document written at design time."),
 ],
 "expect": "`merge_pr` appears in `added`, the blast radius roughly doubles, and "
           "a new problem is reported: an irreversible ungated tool below L3.",
 "challenge": "Wire `diff_manifests` into a check that runs whenever the manifest "
              "file changes and fails when `delta > 0` without a matching entry "
              "in `approval_required`. That is a living threat model in ~10 lines.",
},

"A1.2": {
 "intro": "The control plane is the only place a design decision can actually "
          "bind. Here it is as three composable policies — the same shape you get "
          "from OPA, Kyverno and a service mesh, minus the YAML.",
 "steps": [
  ("py", '''from cybercommons import sandbox

box = sandbox.Sandbox(
    egress=sandbox.EgressPolicy(allow_hosts={"api.github.com"},
                                allow_suffixes={".internal.example"}),
    paths=sandbox.PathGuard(workspace="/work"),
    tools=sandbox.ToolPolicy(allow={"read_file", "search_code", "http_get"},
                             require_approval={"write_file", "post_comment"},
                             deny={"delete_repo", "rotate_secrets"}))

for tool, target, approved in [
    ("read_file",  "/work/src/app.py", False),
    ("read_file",  "/work/../../root/.ssh/id_rsa", False),
    ("http_get",   "https://api.github.com/repos/x/y", False),
    ("http_get",   "http://169.254.169.254/latest/meta-data/", False),
    ("write_file", "/work/out.txt", False),
    ("write_file", "/work/out.txt", True),
    ("delete_repo", "", True),
]:
    print(box.call(tool, target, approved))

print("\\n", box.summary())
'''),
  ("md", "Every line is a decision with a reason attached. A control plane whose "
         "denials you cannot explain is a control plane you cannot tune — and an "
         "untunable control gets switched off the first time it blocks something "
         "legitimate."),
 ],
 "expect": "Reads inside the workspace and calls to the allowlisted host succeed. "
           "The traversal, the metadata address, the ungated write and the denied "
           "tool are all refused — the denied write succeeds only once approval is "
           "presented. Note that `delete_repo` is refused *even with approval*.",
 "challenge": "Add a fourth lever: a rate limit. What is the right unit — calls "
              "per minute, or state-changing calls per minute? Only one of them "
              "bounds damage.",
},

"A1.3": {
 "intro": "Most authorization models can express a bad grant. The question for an "
          "architect is whether yours can be *made* not to.",
 "steps": [
  ("py", '''from cybercommons import identity

print("ceilings — what each actor may hold at most, whoever asks:")
for actor, scopes in identity.GRANTS.items():
    print(f"  {actor:16s} {sorted(scopes)}")

alice = identity.mint("alice")
print("\\nalice holds:", sorted(alice.scopes))

# the grant a ticket would ask for, and the system refuses to express
for actor, want in [("reviewer-agent", {"repo:write"}),
                    ("reviewer-agent", {"secrets:read"}),
                    ("patch-agent",    {"repo:write"})]:
    try:
        t = identity.exchange(alice, actor, want)
        print(f"  GRANTED  {actor} ← {sorted(want)}")
    except identity.DelegationError as e:
        print(f"  REFUSED  {actor} ← {sorted(want)}: {e}")
'''),
  ("md", "The refusal does not depend on anyone reviewing the request. The "
         "ceiling makes the bad grant *unrepresentable*, which is the only kind "
         "of control that survives a busy quarter."),
 ],
 "expect": "`patch-agent` receives `repo:write`. Both requests for "
           "`reviewer-agent` are refused, and the error names the ceiling that "
           "refused them — not a policy document, the token exchange itself.",
 "challenge": "Add a `break-glass` actor with every scope. Now decide what makes "
              "it safe: a ceiling cannot, so the control has to be time and "
              "audit. Model it with `identity.JITGrant`.",
},

"A1.4": {
 "intro": "\"Reduce blast radius\" is advice. A number is a design metric — it "
          "moves when you change the design, and you can put it in a review.",
 "steps": [
  ("py", '''from cybercommons import planes
W = planes.Tool

designs = {
 "one agent, all tools": planes.Manifest("mono", [
     W("read_file"),
     W("write_file",  writes=True, scope="project"),
     W("deploy_prod", writes=True, scope="org", reversible=False),
     W("rotate_secrets", writes=True, scope="org", reversible=False)], rung="L2.5"),
 "split by scope": planes.Manifest("reader+writer", [
     W("read_file"), W("write_file", writes=True, scope="project")], rung="L2.5"),
 "split + gate the org-wide tools": planes.Manifest("gated", [
     W("read_file"),
     W("write_file",  writes=True, scope="project"),
     W("deploy_prod", writes=True, scope="org", reversible=False),
     W("rotate_secrets", writes=True, scope="org", reversible=False)],
     approval_required={"deploy_prod", "rotate_secrets"}, rung="L2.5"),
}
for name, m in designs.items():
    b = m.blast_radius()
    print(f"{name:34s} blast={b['total']:4d}  {b['per_tool']}")
'''),
  ("md", "Splitting the agent and gating the wide tools reach a similar number by "
         "different means — and they fail differently. Splitting survives a "
         "compromised agent; gating survives a compromised *tool list* but not a "
         "compromised approver. Architecture is choosing which failure you prefer."),
 ],
 "expect": "The monolithic design scores far highest (two irreversible org-wide "
           "tools at double weight). Splitting drops it by an order of magnitude; "
           "gating drops the same two tools to zero.",
 "challenge": "Compute the blast radius of your largest production agent. If the "
              "number is over 40, name which single tool contributes most and "
              "what it would cost to gate it.",
},

"A1.5": {
 "intro": "Multi-agent topologies fail in the seams. Delegation depth is the "
          "variable nobody bounds, and each hop is a place authority can widen.",
 "steps": [
  ("py", '''from cybercommons import identity

reg = identity.Registry()
root = reg.record(identity.mint("alice"))

# a three-hop chain, each hop narrowing
hop1 = reg.record(identity.exchange(root, "reviewer-agent", {"repo:read"}))
hop2 = reg.record(identity.exchange(root, "patch-agent",    {"repo:read", "repo:write"}))
hop3 = reg.record(identity.exchange(hop2, "deploy-agent",   {"repo:read"}))

for t in (root, hop1, hop2, hop3):
    print(t.describe())

print("\\ndepth of the deepest chain:", max(len(t.chain()) for t in reg.issued))
'''),
  ("md", "Now the seam: what happens to the topology when one node is revoked?"),
  ("py", '''affected = reg.revoke("patch-agent")
print(f"revoking patch-agent invalidates {affected} token(s)\\n")
for t in (hop1, hop2, hop3):
    ok, why = reg.valid(t)
    print(f"  {' → '.join(t.chain()):48s} valid={str(ok):5s} {why}")
'''),
  ("md", "`deploy-agent` was never revoked, but it derived its authority through "
         "`patch-agent`, so it dies too — correctly. A topology where revoking a "
         "middle node leaves its descendants running is a topology with no "
         "containment story."),
 ],
 "expect": "Three tokens carry increasingly narrow scopes and a readable "
           "`alice → … → agent` chain. Revoking `patch-agent` invalidates both it "
           "and the `deploy-agent` token derived from it, while `reviewer-agent` "
           "keeps working.",
 "challenge": "Add a fourth hop and a policy that refuses any exchange producing "
              "a chain longer than three actors. Where should that check live — "
              "at the issuer, or at the resource server?",
},

"A1.6": {
 "intro": "Build-vs-buy for agent infrastructure turns on one question: which "
          "controls can you *evidence* afterwards? A bought platform that cannot "
          "produce an act chain has made your audit problem permanent.",
 "steps": [
  ("py", '''from cybercommons import grc

CANDIDATES = {
 "vendor platform":   {"AC-1": True,  "AC-2": False, "SB-1": True,  "EV-1": False, "ST-1": False},
 "CNCF stack (SPIRE + OPA + gateway)": {"AC-1": True, "AC-2": True, "SB-1": True,
                                        "EV-1": True,  "ST-1": True},
 "roll your own":     {"AC-1": True,  "AC-2": True,  "SB-1": False, "EV-1": True,  "ST-1": False},
}
required = ["AC-1", "AC-2", "SB-1", "EV-1", "ST-1"]
catalogue = {c.cid: c for c in grc.CATALOGUE}

for name, support in CANDIDATES.items():
    missing = [c for c in required if not support.get(c)]
    print(f"{name}")
    print(f"  covers {len(required) - len(missing)}/{len(required)}")
    for c in missing:
        print(f"  ✗ {c}  {catalogue[c].text}")
    print()
'''),
  ("md", "The decisive gaps are AC-2 (act chains) and ST-1 (a stop mechanism you "
         "own). Both are cheap to specify up front and effectively impossible to "
         "retrofit into someone else's control plane."),
 ],
 "expect": "The CNCF stack covers all five. The vendor platform misses delegation "
           "chains, per-agent logging and an independent stop mechanism; rolling "
           "your own misses egress control and stop authority.",
 "challenge": "Add the two controls your current platform cannot evidence to the "
              "list, and price them as 'ask the vendor' versus 'build alongside'. "
              "The second number is usually smaller than people expect.",
},

"A1.7": {
 "intro": "Routing between models is a security decision, not a cost decision — "
          "because the cheap model is usually the one holding the tools.",
 "steps": [
  ("py", '''from cybercommons import planes

ROUTES = {
 # (model, what it is allowed to trigger)
 "small local (Llama 3.3 8B)": planes.Manifest("router:small",
     [planes.Tool("read_file"), planes.Tool("search_code")], rung="L1"),
 "mid open-weight (GLM-4.6)": planes.Manifest("router:mid",
     [planes.Tool("read_file"),
      planes.Tool("write_file", writes=True, scope="project")],
     approval_required={"write_file"}, rung="L2"),
 "large (Kimi K2) for planning only": planes.Manifest("router:large",
     [planes.Tool("read_file")], rung="L1"),
}
for name, m in ROUTES.items():
    print(f"{name:36s} blast={m.blast_radius()['total']:3d}  "
          f"issues={m.rung_check() or 'none'}")

print("\\nThe routing rule that matters:")
print("  capability decides which model *plans*;")
print("  blast radius decides which model is allowed to *act*.")
'''),
  ("md", "The common anti-pattern inverts this: the expensive model plans, and "
         "the cheap fast model is given the tools so the loop stays responsive. "
         "That puts the weakest reasoning next to the highest authority."),
 ],
 "expect": "All three routes report a blast radius of 0 or near it and no rung "
           "problems, because the tools are attached to the gated route rather "
           "than the fastest one.",
 "challenge": "Model the anti-pattern: give `router:small` the ungated "
              "`write_file` and `deploy_prod`. Compare the blast radius, then "
              "argue the cost saving against it.",
},

# --------------------------------------------- A2 Identity & Non-Human Identity
"A2.1": {
 "intro": "\"Who is calling?\" has a different answer for agents than for people, "
          "and most systems can only represent the human one.",
 "steps": [
  ("py", '''from cybercommons import identity

alice = identity.mint("alice", {"repo:read", "repo:write"})
agent = identity.exchange(alice, "patch-agent", {"repo:write"})

print("token the resource server receives:")
print("  sub   ", agent.sub,   "  ← who the action is *for*")
print("  actor ", agent.actor, "  ← who is actually calling")
print("  act   ", agent.act,   "  ← the chain that got here")
print("  chain ", " → ".join(agent.chain()))
print("  fp    ", agent.fingerprint())
'''),
  ("md", "Three distinct identities are in play — the principal, the acting "
         "agent, and every intermediary. A system that logs only `sub` cannot "
         "answer the question in the title."),
  ("py", '''bad = identity.impersonate("alice", "patch-agent", {"repo:write"})
print("with impersonation instead of delegation:")
print("  chain ", " → ".join(bad.chain()))
print("  the agent has vanished. Every log line will say alice did it.")
'''),
 ],
 "expect": "The delegated token shows `alice → patch-agent` with a nested `act` "
           "claim. The impersonated token shows only `alice`, with `act = None`.",
 "challenge": "Check one system you operate: does its audit log have a field for "
              "the acting identity that is separate from the principal? If not, "
              "every agent action in it is already misattributed.",
},

"A2.2": {
 "intro": "The bootstrap problem: an agent needs an identity before it can prove "
          "anything, and whatever you use to hand it that first credential is "
          "your real trust root.",
 "steps": [
  ("py", '''from cybercommons import identity, sandbox

# The anti-pattern: a long-lived secret in the environment. Anything that can
# read the process environment is now the agent.
print("bootstrap A — static secret in env")
print("  lifetime: until someone rotates it (median: never)")
print("  theft:    any file read, any log line, any core dump")
guard = sandbox.PathGuard(workspace="/work")
print("  ", guard.check("/work/.env"))

print("\\nbootstrap B — short-lived, attested, narrowed at issue")
t = identity.mint("alice", {"repo:read", "repo:write"})
agent = identity.exchange(t, "patch-agent", {"repo:write"})
print(f"  ttl {agent.ttl:.0f}s, scopes {sorted(agent.scopes)}, chain {agent.chain()}")
print("  theft window is the ttl, and the stolen token names its own thief")
'''),
  ("md", "SPIFFE/SPIRE solves this properly by attesting the *workload* — the "
         "node and process identity become the evidence, so no secret has to be "
         "planted anywhere. The modelled version above captures the property that "
         "matters: the credential is short-lived and already narrowed when it "
         "arrives."),
 ],
 "expect": "The `.env` read is denied by the path guard, and the delegated token "
           "prints a 300-second TTL with a single narrowed scope and a readable "
           "chain.",
 "challenge": "For one agent you run, measure the actual lifetime of its "
              "bootstrap credential. If the answer is 'since we deployed it', "
              "that is a standing grant, not a bootstrap.",
},

"A2.3": {
 "intro": "**Shadow Autonomy** is the default failure, and it is not a bug in "
          "anyone's code. It is what happens when an agent is handed a service "
          "account and told to get on with it.",
 "steps": [
  ("py", '''from cybercommons import identity, ir
import time

good = identity.exchange(identity.mint("alice"), "patch-agent", {"repo:write"})
bad  = identity.impersonate("alice", "patch-agent", {"repo:write"})

print("delegation :", " → ".join(good.chain()))
print("impersonation:", " → ".join(bad.chain()))
'''),
  ("md", "Now play it forward into the incident, where the difference stops being "
         "academic."),
  ("py", '''t0 = time.time()
tl = ir.Timeline()
tl.add(t0,      "alice", "alice",       "login",      "console")
tl.add(t0 + 12, "alice", "patch-agent", "write_file", "/etc/app.conf")
tl.add(t0 + 13, "alice", "patch-agent", "merge_pr",   "repo/main")
tl.add(t0 + 14, "alice", "patch-agent", "deploy",     "prod")

print("what the responder sees:")
print(tl.render())
print("\\nwhat actually happened:")
print(tl.render(truth=True))

r = ir.reconstruct(tl)
print("\\nattribution:", r["attribution"])
print("consequence:", r["consequence"])
'''),
 ],
 "expect": "Both timelines look identical except for the actor column. "
           "`reconstruct` reports BROKEN attribution, names `patch-agent` as a "
           "hidden actor, and states that containment aimed at alice leaves the "
           "agent running.",
 "challenge": "Disabling alice's account is the obvious containment step and it "
              "does nothing here. Write down what the *correct* containment step "
              "is, and whether your platform can perform it today.",
},

"A2.4": {
 "intro": "Non-human identities outnumber humans by an order of magnitude and are "
          "governed by roughly none of the same process. The gap is not policy — "
          "it is that nobody can enumerate them.",
 "steps": [
  ("py", '''from cybercommons import identity

reg = identity.Registry()
root = reg.record(identity.mint("alice"))
for actor, scopes in [("reviewer-agent", {"repo:read"}),
                      ("patch-agent",    {"repo:read", "repo:write"}),
                      ("deploy-agent",   {"repo:read"})]:
    reg.record(identity.exchange(root, actor, scopes))

print(f"{'identity':18s}{'tokens':>7}  scopes")
for row in reg.inventory():
    print(f"{row['actor']:18s}{row['tokens']:>7}  {row['scopes']}")
'''),
  ("md", "Now the governance question that separates an identity from a password: "
         "can you revoke exactly one of these?"),
  ("py", '''n = reg.revoke("patch-agent")
print(f"revoked patch-agent → {n} token(s) invalidated")
for row in reg.inventory():
    print(f"  {row['actor']:18s} revoked={row['revoked']}")
print("\\nThe others keep working. If your only lever were rotating a shared")
print("secret, revoking one agent would take down all four.")
'''),
 ],
 "expect": "Four identities are listed with their scopes. Revoking `patch-agent` "
           "marks only that row revoked; the other three remain usable.",
 "challenge": "Count the non-human identities in one production account. Then "
              "count how many have a named owner and an expiry. The ratio is "
              "your NHI governance gap.",
},

"A2.5": {
 "intro": "This is the flagship identity lab. A three-hop delegation chain that "
          "survives audit — and the four ways it usually doesn't.",
 "steps": [
  ("md", "**1 — the chain.** Each hop narrows, and each hop is recorded."),
  ("py", '''from cybercommons import identity

alice = identity.mint("alice")
rev   = identity.exchange(alice, "reviewer-agent", {"repo:read"})
patch = identity.exchange(alice, "patch-agent",    {"repo:read", "repo:write"})
dep   = identity.exchange(patch, "deploy-agent",   {"repo:read"})

for t in (alice, rev, patch, dep):
    print(t.describe())
'''),
  ("md", "**2 — widening is refused, twice over.** Once against the token that "
         "was presented, once against the actor's own ceiling."),
  ("py", '''for presented, actor, want, why in [
    (patch, "deploy-agent",   {"deploy:prod"},  "not in the presented token"),
    (alice, "reviewer-agent", {"secrets:read"}, "above the actor's ceiling"),
]:
    try:
        identity.exchange(presented, actor, want)
        print(f"GRANTED — this should not happen ({why})")
    except identity.DelegationError as e:
        print(f"refused ({why}):\\n    {e}")
'''),
  ("md", "**3 — the anti-pattern.** Impersonation produces a token that works "
         "perfectly and destroys the audit trail."),
  ("py", '''bad = identity.impersonate("alice", "patch-agent", {"repo:write"})
print("delegated    :", " → ".join(patch.chain()))
print("impersonated :", " → ".join(bad.chain()), "  ← the agent is invisible")
'''),
  ("md", "**4 — revocation is per-actor.** One identity dies; the rest live."),
  ("py", '''reg = identity.Registry()
for t in (alice, rev, patch, dep):
    reg.record(t)
print(f"revoking reviewer-agent → {reg.revoke('reviewer-agent')} token(s) hit\\n")
for t in (rev, patch, dep):
    ok, why = reg.valid(t)
    print(f"  {' → '.join(t.chain()):46s} valid={str(ok):5s} {why}")
'''),
 ],
 "expect": "Four tokens print with strictly narrowing scopes and readable chains "
           "(`alice → patch-agent → deploy-agent`). Both widening attempts raise "
           "`DelegationError` naming which rule refused. The impersonated token's "
           "chain contains only `alice`. Revoking `reviewer-agent` invalidates "
           "one token and leaves the patch and deploy chains valid.",
 "challenge": "Run the same four scenarios against real Keycloak with RFC 8693 "
              "token exchange (`labs/a2-delegation` has the compose file). The "
              "properties should hold identically — if they don't, your realm "
              "configuration is the finding.",
},

"A2.6": {
 "intro": "An agent gateway is where identity, policy and egress meet. It is the "
          "one component that can enforce all three at once, which is exactly why "
          "it is worth building deliberately rather than accreting.",
 "steps": [
  ("py", '''from cybercommons import identity, sandbox

box = sandbox.default_sandbox()

def gateway(token, tool, target=""):
    """Every call: authenticate, authorise by scope, then contain."""
    if token.expired:
        return "DENY  expired token"
    need = {"read_file": "repo:read", "write_file": "repo:write",
            "http_get": "repo:read"}.get(tool)
    if need and need not in token.scopes:
        return f"DENY  scope {need} not in {sorted(token.scopes)}"
    d = box.call(tool, target, approved=(tool in box.tools.require_approval))
    return f"{'ALLOW' if d.allowed else 'DENY '} {d.reason}"

alice = identity.mint("alice")
rev   = identity.exchange(alice, "reviewer-agent", {"repo:read"})
patch = identity.exchange(alice, "patch-agent", {"repo:read", "repo:write"})

for tok, tool, target in [(rev, "read_file", "/work/a.py"),
                          (rev, "write_file", "/work/a.py"),
                          (patch, "write_file", "/work/a.py"),
                          (patch, "http_get", "http://169.254.169.254/"),
                          (patch, "read_file", "/work/../../root/.ssh/id_rsa")]:
    print(f"{tok.actor:16s} {tool:11s} → {gateway(tok, tool, target)}")
'''),
  ("md", "Note the last two: `patch-agent` holds every scope it needs and is "
         "still refused, because scope is not containment. A gateway that checks "
         "only authorisation is half a gateway."),
 ],
 "expect": "`reviewer-agent` is refused `write_file` on scope. `patch-agent` "
           "passes the scope check for the same call and succeeds, then is "
           "refused the metadata address and the traversal on containment grounds.",
 "challenge": "The open-source path here is `agentgateway` plus OPA for policy. "
              "Which of the three checks above would you put in the gateway, and "
              "which in the tool itself? Defend the split.",
},

"A2.7": {
 "intro": "Most systems you must integrate with have no concept of an agent. They "
          "have users, and they will happily believe your agent is one.",
 "steps": [
  ("py", '''from cybercommons import identity

agent = identity.exchange(identity.mint("alice"), "patch-agent", {"repo:write"})

def legacy_system(token):
    """A system that understands only `sub`. Most of them."""
    return {"authenticated_as": token.sub, "audit_line": f"{token.sub} performed write"}

def agent_aware(token):
    return {"authenticated_as": token.sub, "acting": token.actor,
            "chain": token.chain(),
            "audit_line": f"{token.actor} performed write on behalf of {token.sub}"}

print("legacy      :", legacy_system(agent))
print()
print("agent-aware :", agent_aware(agent))
'''),
  ("md", "The token carries the truth; the legacy system throws it away. That is "
         "the integration problem in one line — and the mitigation is not to fix "
         "the legacy system but to keep the chain at the gateway, which *is* "
         "agent-aware, and reconcile logs against it afterwards."),
 ],
 "expect": "Both calls authenticate as `alice`. Only the agent-aware handler "
           "records `patch-agent` as the actor and produces a truthful audit line.",
 "challenge": "Write the reconciliation query: given gateway logs with act chains "
              "and legacy logs with only `sub`, how would you attribute a legacy "
              "log line to the right agent? What has to be true for that join to "
              "work?",
},

"A2.8": {
 "intro": "Just-in-time authority replaces the standing grant. The audit question "
          "changes from \"who has deploy:prod?\" — always the same dull list — to "
          "\"who held it, for what, for how long?\", which is answerable.",
 "steps": [
  ("py", '''from cybercommons import identity
import time

grants = [
    identity.JITGrant("patch-agent",  "repo:write",  "fix CVE-2024-0001", seconds=60),
    identity.JITGrant("deploy-agent", "deploy:prod", "roll out the fix",  seconds=0.5),
]
print("at issue:")
for g in grants:
    print("  " + g.audit_line())

time.sleep(0.6)
print("\\nafter 0.6s:")
for g in grants:
    print("  " + g.audit_line())
'''),
  ("md", "Compare the two audit stories. A standing grant produces a list of "
         "identities. This produces a list of *justified episodes* — with a "
         "reason field an auditor can sample and a duration they can question."),
 ],
 "expect": "Both grants are ACTIVE at issue. After the sleep the deploy grant has "
           "expired while the longer one is still active, and each line carries "
           "its reason.",
 "challenge": "What is the right TTL for `deploy:prod`? Argue it from the "
              "measured duration of a real deploy, not from a round number — and "
              "note what happens to the agent when the grant expires mid-task.",
},

"A2.9": {
 "intro": "The classic identity failures did not go away when the caller became "
          "an agent. They got faster, and they got harder to attribute.",
 "steps": [
  ("py", '''from cybercommons import identity, redteam

alice = identity.mint("alice")
patch = identity.exchange(alice, "patch-agent", {"repo:read", "repo:write"})
reg = identity.Registry()
reg.record(alice); reg.record(patch)

def target(a):
    """Fire the identity-surface attacks at the delegation implementation."""
    if a.surface != redteam.IDENTITY:
        return False, "n/a"
    if a.aid == "IDN-01":                       # widen scope during delegation
        try:
            identity.exchange(patch, "deploy-agent", {"deploy:prod"})
            return True, "scope widened"
        except identity.DelegationError as e:
            return False, str(e)[:40]
    if a.aid == "IDN-02":                       # replay an expired token
        old = identity.Token("alice", "patch-agent", {"repo:write"}, ttl=-1)
        return reg.valid(old)[0], reg.valid(old)[1]
    if a.aid == "IDN-03":                       # drop the act claim
        bad = identity.impersonate("alice", "patch-agent", {"repo:write"})
        hidden = "patch-agent" not in bad.chain()
        return hidden, "agent absent from the chain" if hidden else "chain intact"
    if a.aid == "IDN-04":                       # exceed the actor ceiling
        try:
            identity.exchange(alice, "reviewer-agent", {"repo:write"})
            return True, "ceiling ignored"
        except identity.DelegationError as e:
            return False, str(e)[:40]
    return False, "n/a"

c = redteam.run_campaign(target, "delegation implementation",
                         [a for a in redteam.SUITE if a.surface == redteam.IDENTITY])
print(c.table())
'''),
  ("md", "Three of the four are blocked by the exchange rules. IDN-03 succeeds — "
         "and it succeeds *by design*, because nothing in a token format can stop "
         "a caller choosing not to use delegation. That control lives in the "
         "platform: agents must not be issuable a principal's credential at all."),
 ],
 "expect": "IDN-01, IDN-02 and IDN-04 are blocked with reasons. IDN-03 "
           "(impersonation) gets through, giving an identity-surface ASR of 0.25.",
 "challenge": "IDN-03 is the one that matters. Write the platform control that "
              "would stop it, then work out how you would *detect* it in a system "
              "where you cannot deploy that control yet.",
},

# ------------------------------------------- A3 Platform & Cloud Security
"A3.1": {
 "intro": "For an agent, the sandbox is the perimeter — because intent is not a "
          "control you own, and the prompt can be fully compromised while every "
          "containment property still holds.",
 "steps": [
  ("py", '''from cybercommons import sandbox

box = sandbox.default_sandbox()
attempts = [
    ("read_file",  "/work/src/app.py"),
    ("read_file",  "/work/../../root/.ssh/id_rsa"),
    ("read_file",  "/work/.env"),
    ("http_get",   "https://api.github.com/repos/x/y"),
    ("http_get",   "http://169.254.169.254/latest/meta-data/iam/"),
    ("http_get",   "https://exfil.example.com/collect"),
    ("run_shell",  ""),
    ("delete_repo", ""),
]
for tool, target in attempts:
    print(box.call(tool, target))
print("\\n", box.summary())
'''),
  ("md", "Assume the prompt is entirely under attacker control. Every one of "
         "these was *requested*; six were refused anyway. That is what it means "
         "for containment to be the perimeter."),
 ],
 "expect": "Two calls succeed (the workspace read and the allowlisted host). Six "
           "are denied, and `summary()` lists the distinct reasons.",
 "challenge": "Which single denial in that list would you most regret losing? "
              "Now check whether your production agent actually has it.",
},

"A3.2": {
 "intro": "Egress control is the difference between a compromised agent and a "
          "data breach. The destination that matters is always the one nobody "
          "thought to list.",
 "steps": [
  ("py", '''from cybercommons import sandbox

strict = sandbox.EgressPolicy(allow_hosts={"api.github.com"},
                              allow_suffixes={".internal.example"})
loose  = sandbox.EgressPolicy(allow_hosts=set(), allow_suffixes={".com"})

urls = ["https://api.github.com/repos/x/y",
        "https://build.internal.example/artifacts",
        "http://169.254.169.254/latest/meta-data/",
        "http://127.0.0.1:8080/admin",
        "https://exfil.example.com/collect",
        "https://pastebin.com/api/post"]

for name, pol in (("deny-by-default allowlist", strict), ("suffix allowlist", loose)):
    print(name)
    for u in urls:
        print("   ", pol.check(u))
    print()
'''),
  ("md", "The suffix allowlist looks reasonable in a config review and permits "
         "exfiltration to any `.com` host on the internet. Allowlists have to "
         "name hosts; suffixes are for domains you control."),
 ],
 "expect": "The strict policy allows two destinations and blocks four, naming the "
           "metadata service explicitly. The loose policy blocks the private "
           "addresses but permits both exfiltration destinations.",
 "challenge": "Add the DNS problem: an allowlisted hostname that resolves to "
              "169.254.169.254. Which layer has to catch that, and why can't the "
              "URL check?",
},

"A3.3": {
 "intro": "Path guards fail in one specific way, over and over: the check runs "
          "before normalisation, and `workspace/../../secret` starts with "
          "`workspace/`.",
 "steps": [
  ("py", '''from cybercommons import sandbox

g = sandbox.PathGuard(workspace="/work")
paths = ["/work/src/main.py",
         "/work/./src/../src/main.py",
         "/work/../../root/.ssh/id_rsa",
         "/work/.env",
         "/work/deploy.pem",
         "/etc/shadow",
         "/work/sub/../.aws/credentials"]
for p in paths:
    print(g.check(p))
'''),
  ("md", "Now the buggy version, to see the failure rather than read about it."),
  ("py", '''def naive_check(path, workspace="/work"):
    return path.startswith(workspace)          # the bug

for p in paths:
    real = g.check(p).allowed
    naive = naive_check(p)
    flag = "  ← NAIVE CHECK IS WRONG" if naive != real else ""
    print(f"{p:38s} guard={str(real):5s} naive={str(naive):5s}{flag}")
'''),
 ],
 "expect": "The guard allows the two legitimate workspace paths and denies the "
           "rest, naming the resolved path or the deny rule. The naive check "
           "wrongly allows the traversal to `/root/.ssh/id_rsa` and the "
           "`.aws/credentials` read.",
 "challenge": "Symlinks are the next layer: a link inside the workspace pointing "
              "out of it defeats pure string normalisation. What has to change — "
              "and which real containment technology gives it to you for free?",
},

"A3.4": {
 "intro": "MCP is a transport and a discovery mechanism. It is not a security "
          "boundary, and treating it as one is how tool servers end up with "
          "ambient authority.",
 "steps": [
  ("py", '''from cybercommons import injection, sandbox

# An MCP-style server exposes tools. The protocol says nothing about *who*
# may call them or what the content it returns is allowed to trigger.
SERVER_TOOLS = ["read_issue", "post_comment", "merge_pr"]

# A document fetched through one MCP tool contains an instruction for the agent.
poisoned = SERVER_TOOLS and injection.CORPUS[2].text
print("content returned by read_issue:\\n ", poisoned, "\\n")

naive  = injection.Deputy("agent", {"merge_pr"}, trust_data_as_instructions=True)
strict = injection.Deputy("agent", {"merge_pr"}, trust_data_as_instructions=False)

for name, d in (("MCP alone", naive), ("MCP + provenance", strict)):
    r = d.handle(poisoned, "merge_pr", source="mcp-tool-result")
    print(f"{name:20s} merge_pr executed={r['executed']}  blocked_by={r['blocked_by']}")
'''),
  ("md", "The protocol carried the payload faithfully. Whether it becomes an "
         "action depends entirely on a control that MCP does not specify — so "
         "you have to supply it."),
  ("py", '''box = sandbox.ToolPolicy(allow={"read_issue"},
                         require_approval={"post_comment"},
                         deny={"merge_pr"})
for t in SERVER_TOOLS:
    print(box.check(t))
'''),
 ],
 "expect": "With MCP alone the poisoned issue body triggers `merge_pr`. With "
           "provenance enforced it is blocked because the instruction came from a "
           "tool result rather than the principal. The tool policy independently "
           "denies `merge_pr` regardless.",
 "challenge": "List the MCP servers your developers have connected. For each, "
              "name what would happen if the content it returns were attacker-"
              "controlled. That list is your actual injection surface.",
},

"A3.5": {
 "intro": "Tool permission models are where L2 and L2.5 stop being vocabulary and "
          "start being configuration.",
 "steps": [
  ("py", '''from cybercommons import sandbox

MODELS = {
 "allow-all (no model at all)":
    sandbox.ToolPolicy(allow={"read_file", "write_file", "run_shell",
                              "delete_repo", "rotate_secrets"}),
 "L2 — approve every writer":
    sandbox.ToolPolicy(allow={"read_file"},
                       require_approval={"write_file", "run_shell",
                                         "delete_repo", "rotate_secrets"}),
 "L2.5 — bounded set, some tools never":
    sandbox.ToolPolicy(allow={"read_file", "write_file"},
                       require_approval={"run_shell"},
                       deny={"delete_repo", "rotate_secrets"}),
}
calls = ["read_file", "write_file", "run_shell", "delete_repo", "unknown_tool"]
for name, pol in MODELS.items():
    print(name)
    for c in calls:
        print("   ", pol.check(c))
    print()
'''),
  ("md", "Look at `unknown_tool` in each. Deny-by-default is the property that "
         "makes the model hold when someone adds a tool and forgets to update the "
         "policy — which is the normal case, not the exception."),
 ],
 "expect": "The allow-all policy permits everything named and still denies "
           "`unknown_tool`. L2 gates every writer. L2.5 allows the bounded set, "
           "gates the shell and refuses the two destructive tools outright.",
 "challenge": "Where does 'approve' actually happen for your agents — a human in "
              "a chat window, or a policy engine? Measure the median approval "
              "latency. If it is under two seconds, nobody is reading them.",
},

"A3.6": {
 "intro": "When containment fails, the runtime levers are what you have left. "
          "They are worth rehearsing before you need them.",
 "steps": [
  ("py", '''from cybercommons import ir, soc
import time

# the lever question: how much damage happens while containment waits?
for approval_minutes in (0.5, 5, 30):
    r = ir.containment_race(agent_actions_per_min=120,
                            human_approval_minutes=approval_minutes)
    print(f"human approval {approval_minutes:>4} min → "
          f"{r['actions_during_manual_approval']:>7.0f} actions "
          f"vs {r['actions_during_auto_containment']:>5.0f} automated "
          f"({r['ratio']}× more)")
print("\\n", ir.containment_race(120, 5)["conclusion"])
'''),
  ("md", "Now the detection side: the levers only fire if something notices."),
  ("py", '''events = [soc.Event(time.time(), "patch-agent", "http_get",
                    "http://169.254.169.254/latest/meta-data/iam/")]
for a in soc.run_rules(events, soc.default_rules()):
    print(f"[{a.severity}] {a.rule}\\n    → {a.response}")
'''),
 ],
 "expect": "A five-minute human approval permits ~600 agent actions against ~10 "
           "for automated containment — a 60× difference. The metadata rule fires "
           "at critical severity with a concrete response.",
 "challenge": "Rank your available levers by measured time-to-effect: revoke "
              "identity, kill process, network quarantine, rotate credentials. "
              "The fastest one should be the one you have automated.",
},

"A3.7": {
 "intro": "The unmanaged agent problem: the agents you know about are not the "
          "ones that will hurt you. Discovery has to run against behaviour, "
          "because registration is voluntary and voluntary means partial.",
 "steps": [
  ("py", '''from cybercommons import soc, grc
import time

now = time.time()
# telemetry from three actors — no registry, just behaviour
events  = [soc.Event(now + i * 0.08, "svc-ci-runner", "read_file") for i in range(80)]
events += [soc.Event(now + t, "dana", "read_file")
           for t in (0, 6, 9, 45, 91, 140, 260, 420)]
events += [soc.Event(now + i * 0.5, "unknown-token-7f3", "http_get") for i in range(40)]

for actor in ("svc-ci-runner", "dana", "unknown-token-7f3"):
    r = soc.agent_score(events, actor)
    print(f"{actor:20s} score={r['score']:.3f}  {r['verdict']:8s} {r['signals']}")
'''),
  ("md", "Two of these behave like software. Only one is in anybody's inventory. "
         "That third row is what \"shadow AI\" looks like in telemetry before it "
         "has a name."),
  ("py", '''found = grc.AIAsset("unknown-token-7f3", "agent", owner="", autonomy="L2.5",
                    data=("customer",), shadow=True)
print(grc.risk_tier(found))
for g in found.gaps():
    print("  ⚠", g)
'''),
 ],
 "expect": "`svc-ci-runner` and `unknown-token-7f3` score as agents; `dana` scores "
           "as human. The discovered agent tiers high or critical and reports "
           "gaps for missing ownership and registration.",
 "challenge": "Run `agent_score` over a day of real authentication logs. Every "
              "actor scoring above 0.6 that is not in your NHI inventory is a "
              "finding — and the first run always produces some.",
},

"A3.8": {
 "intro": "Environment separation for agents is not the same problem as for CI. "
          "An agent carries its context across boundaries, so the separation has "
          "to bind to the identity, not to the network.",
 "steps": [
  ("py", '''from cybercommons import identity, sandbox

ENVS = {
 "dev":     sandbox.Sandbox(
     egress=sandbox.EgressPolicy(allow_suffixes={".dev.internal"}),
     paths=sandbox.PathGuard(workspace="/work/dev"),
     tools=sandbox.ToolPolicy(allow={"read_file", "write_file", "run_shell"})),
 "prod":    sandbox.Sandbox(
     egress=sandbox.EgressPolicy(allow_hosts={"api.github.com"}),
     paths=sandbox.PathGuard(workspace="/work/prod"),
     tools=sandbox.ToolPolicy(allow={"read_file"},
                              require_approval={"write_file"},
                              deny={"run_shell"})),
}
for env, box in ENVS.items():
    print(env)
    for tool, target in [("read_file", f"/work/{env}/app.py"),
                         ("read_file", "/work/prod/secrets.yaml"),
                         ("run_shell", ""),
                         ("write_file", f"/work/{env}/out.txt")]:
        print("   ", box.call(tool, target))
    print()
'''),
  ("md", "The dev sandbox cannot reach `/work/prod` — not because of a network "
         "rule, but because its workspace is a different path and the guard "
         "normalises before checking. Separation that lives in the identity's "
         "policy travels with the agent; separation that lives in a VPC does not."),
 ],
 "expect": "Each environment permits reads inside its own workspace only. The dev "
           "box is denied the prod secrets path; the prod box denies `run_shell` "
           "outright and gates writes.",
 "challenge": "An agent debugging a prod incident needs prod read access from a "
              "dev context. Design that as a JIT grant rather than a second "
              "credential — `identity.JITGrant` is the shape.",
},
}
