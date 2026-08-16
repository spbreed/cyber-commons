"""A1 — The Security Architect. Seven sessions.

Narrative arc. A1.1 is the first lesson of the whole curriculum, so it starts
from nothing: what an agent actually is, and the vocabulary (three planes,
autonomy ladder) that the other 98 lessons reuse. From there:

    A1.1  the planes            what changes when software acts
    A1.2  the control plane     where a design decision can bind
    A1.3  authorization         making a bad grant unrepresentable
    A1.4  blast radius          turning "reduce risk" into a number
    A1.5  topology              what multi-agent does to that number
    A1.6  build vs buy          which controls you can still evidence
    A1.7  model routing         why the cheap model must not hold the tools
"""

from .skills import SKILL_RUNTIME

EXERCISES: dict[str, dict] = {

"A1.1": {
 "concept": """
Start with something that is not an agent.

A **model** takes text and returns text. Ask GPT-4 or Llama 3.3 to delete your
production database and it will produce a convincing paragraph about deleting
your production database. Nothing happens. The output is a string.

A model becomes an **agent** when something reads that string and *acts on it* —
a program that sees `{"tool": "run_sql", "args": {...}}` and actually connects
to the database. That program is the agent. The model is a component inside it.

This gives us three layers, and the whole curriculum uses these names:

| Plane | What lives here | Can it change the world? |
|---|---|---|
| **Decision** | the model. Proposals, plans, text. | No. Never. |
| **Control** | policy, scopes, approval gates, the gateway. | It decides what passes. |
| **Action** | the tools. SQL, HTTP, the filesystem, the cloud API. | Yes. Only here. |

The consequence is the point of this lesson. When something goes wrong, "the
model did it" cannot be the root cause — the model only ever wrote on the
decision plane. Something on the **control plane** let a proposal through. That
is where your architecture review has to look.

Traditional architecture review assumed the system's behaviour was fixed at
design time: you read the code, you drew the trust boundaries, you signed the
document. An agent's behaviour is determined by a *tool manifest* that changes
when someone edits a config file. So we need a review that runs against the
manifest, continuously — which means the manifest has to be something a program
can read.
""",
 "steps": [
  ("md", "## 2 · Demo — classify a real tool manifest\n\n"
         "Here is the manifest of a plausible internal agent: a bot that triages "
         "security findings. Every entry is a capability someone actually grants "
         "in real deployments. The question the code answers is which plane each "
         "one sits on — and note that the answer comes from what a tool *can do*, "
         "never from what it is called."),
  ("py", '''from dataclasses import dataclass, field

# How far a single call can reach. These weights are the crude, useful kind:
# the absolute number means nothing, the *ratio* between designs means a lot.
SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20, "internet": 50}

@dataclass(frozen=True)
class Tool:
    name: str
    writes: bool = False        # can it change state anywhere?
    reversible: bool = True     # can the change be undone cheaply?
    scope: str = "self"         # self | project | tenant | org | internet

    @property
    def plane(self) -> str:
        # A tool that cannot write is a read tool no matter what it is called.
        return "action" if self.writes else "decision"

# A security finding-triage agent, as actually deployed in a lot of places.
manifest = [
    Tool("search_findings"),
    Tool("read_source"),
    Tool("post_jira_comment", writes=True, scope="project"),
    Tool("close_finding",     writes=True, scope="project"),
    Tool("open_pr",           writes=True, scope="project"),
    Tool("merge_pr",          writes=True, scope="project", reversible=False),
    Tool("rotate_credential", writes=True, scope="org", reversible=False),
]

print(f"{'tool':22s}{'plane':10s}{'scope':10s}reversible")
print("-" * 56)
for t in manifest:
    print(f"{t.name:22s}{t.plane:10s}{t.scope:10s}{t.reversible}")

reads  = [t.name for t in manifest if not t.writes]
writes = [t.name for t in manifest if t.writes]
print(f"\\ndecision plane ({len(reads)}): {reads}")
print(f"action plane   ({len(writes)}): {writes}")
print("\\nThe model can propose all seven. Only the five on the action plane")
print("can change anything, and only if the control plane lets them through.")
'''),
  ("md", "## 3 · Where it breaks\n\n"
         "Look at that manifest again. There is **no control plane in it at all** "
         "— nothing between the model's proposal and the tool call. Whatever the "
         "model emits, happens.\n\n"
         "That is not a hypothetical configuration. It is the default: you give a "
         "framework a list of tools, and it calls them. The trust boundary that "
         "used to exist between \"a human decided\" and \"the system executed\" is "
         "gone, and nothing in the code review shows it missing, because *no code "
         "was written to remove it*.\n\n"
         "So the first architecture question for an agent is not \"is the code "
         "safe?\" It is: **what is the worst single call this manifest permits, and "
         "who reviewed that?**"),
  ("py", '''def blast_radius(tools, gated=frozenset()):
    """What one unreviewed action can cost. Gated calls score zero — they are
    reviewed by definition."""
    per, total = {}, 0
    for t in tools:
        if not t.writes:
            continue
        score = SCOPE_WEIGHT[t.scope]
        if not t.reversible:
            score *= 2          # you cannot review an action after undoing it
        if t.name in gated:
            score = 0
        per[t.name] = score
        total += score
    return total, dict(sorted(per.items(), key=lambda kv: -kv[1]))

total, per = blast_radius(manifest)
print("ungoverned manifest — blast radius:", total)
for name, score in per.items():
    print(f"   {name:22s}{score:4d}")
print("\\nThe worst single call is rotate_credential: org-wide and irreversible.")
print("An agent that can close a finding can also rotate the credential that")
print("finding was about. Nobody decided that; it fell out of the tool list.")
'''),
  ("md", "## 4 · The control\n\n"
         "The fix is not to remove tools — the agent needs them to be useful. It "
         "is to put a **control plane** in the path, and the cheapest one that "
         "works is an approval gate on the calls that are wide or irreversible.\n\n"
         "This is the first appearance of the **autonomy ladder**, which the rest "
         "of the curriculum uses constantly:\n\n"
         "| Rung | What it means |\n|---|---|\n"
         "| **L1** | Model proposes, a human performs every action. |\n"
         "| **L2** | Model calls tools, a human approves each call. |\n"
         "| **L2.5** | Pre-approved tool set, bounded scope, humans review after the fact. |\n"
         "| **L3** | Model acts and self-verifies; humans see aggregates. |\n\n"
         "The rung is **not** about how clever the model is. It is about what the "
         "model's output is allowed to trigger without a human in the path. A "
         "small local model at L3 is more dangerous than a frontier model at L1."),
  ("py", '''LADDER = {"L1": 0, "L2": 1, "L2.5": 3, "L3": 5}

def review(tools, gated, claimed_rung):
    """The architecture review, as a function. This is the deliverable."""
    problems = []
    writers = [t for t in tools if t.writes]
    ungated = [t.name for t in writers if t.name not in gated]
    if claimed_rung == "L1" and writers:
        problems.append(f"claims L1 but holds {len(writers)} state-changing tools")
    if claimed_rung == "L2" and ungated:
        problems.append(f"claims L2 (approve every call) but ungated: {ungated}")
    if claimed_rung == "L2.5":
        wide = [t.name for t in writers
                if SCOPE_WEIGHT[t.scope] >= SCOPE_WEIGHT["org"] and t.name not in gated]
        if wide:
            problems.append(f"claims L2.5 (bounded) but reaches org-wide ungated: {wide}")
    irrev = [t.name for t in writers if not t.reversible and t.name not in gated]
    if irrev and claimed_rung != "L3":
        problems.append(f"irreversible and ungated (no after-the-fact review possible): {irrev}")
    return problems

for label, gated, rung in [
    ("as deployed",                set(),                                      "L2.5"),
    ("gate the irreversible ones", {"merge_pr", "rotate_credential"},          "L2.5"),
    ("gate every writer",          {t.name for t in manifest if t.writes},     "L2"),
]:
    total, _ = blast_radius(manifest, gated)
    problems = review(manifest, gated, rung)
    print(f"{label:30s} rung={rung:5s} blast={total:3d}  "
          f"{'CLEAN' if not problems else 'FINDINGS'}")
    for p in problems:
        print(f"{'':32s}⚠ {p}")
'''),
  ("md", "## 5 · Verify — the review that runs itself\n\n"
         "A threat model written in a document is stale the moment someone adds a "
         "tool, and adding a tool is a config change that no code review sees. So "
         "the artefact that actually protects you is not the model — it is the "
         "**diff**, run automatically whenever the manifest changes."),
  ("py", '''def diff(before, after, gated=frozenset()):
    b, a = {t.name for t in before}, {t.name for t in after}
    tb, _ = blast_radius(before, gated)
    ta, _ = blast_radius(after, gated)
    return {"added": sorted(a - b), "removed": sorted(b - a),
            "blast": f"{tb} → {ta}", "delta": ta - tb,
            "new_findings": [p for p in review(after, gated, "L2.5")
                             if p not in review(before, gated, "L2.5")]}

gated = {"merge_pr", "rotate_credential"}
v1 = [t for t in manifest if t.name != "rotate_credential"]
v2 = manifest                               # someone adds credential rotation

print("someone edits the manifest on a Tuesday:")
for k, v in diff(v1, v2, gated={"merge_pr"}).items():
    print(f"   {k:14s} {v}")
print("\\nNo pull request touched the agent's code. The blast radius doubled.")
print("This diff, wired into CI, IS the living architecture review.")
'''),
 ],
 "expect": "The manifest splits into 2 decision-plane and 5 action-plane tools. "
           "Ungoverned it scores a blast radius of 55, with `rotate_credential` "
           "(40) dominating. Gating the two irreversible tools cuts it to 9 and "
           "clears every finding. The manifest diff shows `rotate_credential` "
           "being added, the blast radius going 15 → 55, and a new finding for an "
           "irreversible ungated tool.",
 "challenge": "Write out the manifest of one agent that is running in your "
              "organisation right now — every tool, honestly, including the ones "
              "added after launch. Run `review()` against the rung your team "
              "claims. The usual result is that the claimed rung is one or two "
              "above what the controls support.",
},

"A1.2": {
 "concept": """
A1.1 established that the control plane is where a design decision can actually
bind. This lesson builds it.

A control plane for an agent has exactly three levers, and they map onto
questions an attacker asks:

| Lever | The attacker's question | Real-world equivalent |
|---|---|---|
| **Tool policy** | what can I invoke? | OPA / Kyverno admission policy |
| **Egress policy** | who can I talk to? | Cilium network policy, a proxy allowlist |
| **Path policy** | what can I read or write? | container mounts, seccomp, AppArmor |

Each one must be **deny-by-default**. That is not paranoia — it is the only
setting that survives someone adding a capability and forgetting to update the
policy, which is the normal case, not the exception.

And every decision must return a **reason**. A control you cannot explain is a
control you cannot tune, and an untunable control gets switched off the first
time it blocks something legitimate. That is how security controls actually die
— not overridden, just quietly disabled by a tired engineer at 6pm.
""",
 "steps": [
  ("md", "## 2 · Demo — the three levers, deny-by-default\n\n"
         "This is a working control plane in about sixty lines. In production the "
         "same three decisions come from OPA, Cilium and your container runtime; "
         "the logic is what matters here."),
  ("py", '''import fnmatch, re
from dataclasses import dataclass, field
from urllib.parse import urlparse

@dataclass
class Decision:
    allowed: bool
    reason: str
    subject: str = ""
    def __str__(self):
        return f"{'ALLOW' if self.allowed else 'DENY ':5s} {self.subject:42s} {self.reason}"

PRIVATE = [re.compile(p) for p in (
    r"^127\\.", r"^10\\.", r"^192\\.168\\.", r"^169\\.254\\.",
    r"^172\\.(1[6-9]|2\\d|3[01])\\.", r"^localhost$")]

@dataclass
class EgressPolicy:
    allow_hosts: set = field(default_factory=set)
    def check(self, url):
        host = (urlparse(url).hostname or "").lower()
        if not host:
            return Decision(False, "unparseable destination", url)
        if any(p.match(host) for p in PRIVATE):
            extra = " — cloud metadata service" if host.startswith("169.254") else ""
            return Decision(False, f"private/link-local address blocked{extra}", url)
        if host in self.allow_hosts:
            return Decision(True, "host on the allowlist", url)
        return Decision(False, "not on the egress allowlist (deny by default)", url)

@dataclass
class PathGuard:
    workspace: str = "/work"
    deny_globs: tuple = ("*/.ssh/*", "*/.aws/*", "*.pem", "*/.env", "*/etc/shadow")
    @staticmethod
    def normalise(path):
        parts = []
        for seg in path.split("/"):
            if seg in ("", "."):      continue
            if seg == "..":
                if parts: parts.pop()
                continue
            parts.append(seg)
        return "/" + "/".join(parts)
    def check(self, path):
        real = self.normalise(path)          # normalise BEFORE checking — see A3.3
        for g in self.deny_globs:
            if fnmatch.fnmatch(real, g):
                return Decision(False, f"matches deny rule {g}", path)
        ws = self.normalise(self.workspace)
        if real == ws or real.startswith(ws + "/"):
            return Decision(True, f"inside workspace ({real})", path)
        return Decision(False, f"outside workspace; resolves to {real}", path)

@dataclass
class ToolPolicy:
    allow: set = field(default_factory=set)
    require_approval: set = field(default_factory=set)
    deny: set = field(default_factory=set)
    def check(self, tool, approved=False):
        if tool in self.deny:
            return Decision(False, "tool explicitly denied", tool)
        if tool in self.require_approval and not approved:
            return Decision(False, "requires human approval, none presented", tool)
        if tool in self.allow or tool in self.require_approval:
            return Decision(True, "approved call" if approved else "on the allowlist", tool)
        return Decision(False, "not on the tool allowlist (deny by default)", tool)

print("three policies, defined. Nothing is permitted that was not named.")
'''),
  ("md", "## 3 · Demo — run a real agent session through it\n\n"
         "These are the calls a code-review agent actually makes during one task, "
         "plus the three an attacker would make if the prompt were compromised. "
         "The control plane cannot tell the difference — and does not need to."),
  ("py", '''@dataclass
class ControlPlane:
    egress: EgressPolicy
    paths: PathGuard
    tools: ToolPolicy
    log: list = field(default_factory=list)

    def call(self, tool, target="", approved=False):
        d = self.tools.check(tool, approved)
        if d.allowed:
            if target.startswith(("http://", "https://")):
                d = self.egress.check(target)
            elif target.startswith("/"):
                d = self.paths.check(target)
        self.log.append(d)
        return d

cp = ControlPlane(
    egress=EgressPolicy(allow_hosts={"api.github.com"}),
    paths=PathGuard(workspace="/work/repo"),
    tools=ToolPolicy(allow={"read_file", "search_code", "http_get"},
                     require_approval={"post_comment", "open_pr"},
                     deny={"merge_pr", "rotate_credential"}))

session = [
    # --- what the agent legitimately does ---
    ("read_file",   "/work/repo/src/auth.py",              False),
    ("search_code", "",                                     False),
    ("http_get",    "https://api.github.com/repos/x/y/pulls", False),
    ("post_comment", "",                                    False),   # ungated attempt
    ("post_comment", "",                                    True),    # with approval
    # --- what a compromised prompt would try ---
    ("read_file",   "/work/repo/../../root/.aws/credentials", False),
    ("http_get",    "http://169.254.169.254/latest/meta-data/iam/", False),
    ("http_get",    "https://exfil.example.com/collect",   False),
    ("rotate_credential", "",                               True),
]
for tool, target, approved in session:
    print(cp.call(tool, target, approved))

denied = [d for d in cp.log if not d.allowed]
print(f"\\n{len(cp.log)} calls · {len(cp.log)-len(denied)} allowed · {len(denied)} denied")
'''),
  ("md", "## 4 · Where it breaks\n\n"
         "Notice the last line: `rotate_credential` was refused **even though "
         "approval was presented**. That is deliberate, and it is the design "
         "decision this lesson exists to make.\n\n"
         "An approval gate is only as good as the approver. Approve-every-call "
         "(L2) sounds strong until you measure the median approval latency — when "
         "it drops under two seconds, nobody is reading them, and the gate has "
         "become a click-through. For actions that are org-wide and irreversible, "
         "the right control is not a gate but a **denial**: that tool does not "
         "belong to this agent at all, and a different, narrower agent owns it.\n\n"
         "This is why `deny` exists as a separate lever from `require_approval`."),
  ("py", '''# Model the approval gate honestly: an approver under load.
def gate_effectiveness(calls_per_hour, seconds_per_real_review=45):
    seconds_available = 3600
    reviewable = seconds_available / seconds_per_real_review
    return {"calls": calls_per_hour, "can_truly_review": int(reviewable),
            "rubber_stamped": max(0, calls_per_hour - int(reviewable)),
            "fraction_real": round(min(reviewable / calls_per_hour, 1.0), 3)}

for rate in (10, 80, 400):
    r = gate_effectiveness(rate)
    print(f"{r['calls']:>4} approvals/hour → {r['fraction_real']:.0%} genuinely "
          f"reviewed, {r['rubber_stamped']:>3} rubber-stamped")
print("\\nAt 400/hour the gate is theatre. Deny the irreversible tools instead,")
print("and give them to a separate agent with its own, much narrower manifest.")
'''),
 ],
 "expect": "The legitimate calls succeed; `post_comment` is refused until "
           "approval is presented. The traversal, the metadata address and the "
           "exfiltration host are all denied with distinct reasons, and "
           "`rotate_credential` is denied despite approval. The gate model shows "
           "review quality collapsing to 20% at 400 approvals per hour.",
 "challenge": "Take the three levers and decide where each belongs in your stack: "
              "in the agent process, in a sidecar, or in the network. Only one of "
              "those placements still works when the agent process itself is the "
              "compromised component.",
},

"A1.3": {
 "concept": """
There are three ways to stop a bad permission grant, and they are not equally
good.

1. **Review it.** A human reads the request and says no. Works until Friday
   afternoon, or until the requester is persuasive, or until the reviewer is on
   holiday.
2. **Detect it.** You find the bad grant afterwards, in an access review. Better
   than nothing; the window between grant and detection is your exposure.
3. **Make it unrepresentable.** The system cannot express the grant at all. The
   request fails at the point of issue, with no human in the loop.

Only the third one scales, and the mechanism is a **ceiling**: a declared upper
bound on what each identity may *ever* hold, enforced by the thing that issues
credentials rather than by the thing that reviews them.

This matters more for agents than for people because agents get their
permissions programmatically, at machine speed, often from other agents. A
review step in that path is not a control; it is a bottleneck that will be
removed.
""",
 "steps": [
  ("md", "## 2 · Demo — ceilings, and what they refuse\n\n"
         "Real scopes from a real deployment: a CI/CD estate with a human "
         "engineer and three service identities."),
  ("py", '''# The ceiling: what each identity may hold AT MOST, whoever asks, forever.
CEILINGS = {
    "dana@corp":       {"repo:read", "repo:write", "deploy:staging", "deploy:prod",
                        "secrets:read"},
    "ci-builder":      {"repo:read", "artifact:write"},
    "deploy-bot":      {"artifact:read", "deploy:staging"},
    "triage-agent":    {"repo:read", "finding:comment"},
}

class GrantRefused(Exception):
    """Refusing is the feature, not an error path."""

def grant(identity, scopes):
    ceiling = CEILINGS.get(identity, set())
    excess = set(scopes) - ceiling
    if excess:
        raise GrantRefused(
            f"{identity} may never hold {sorted(excess)} "
            f"(ceiling: {sorted(ceiling)})")
    return set(scopes)

requests = [
    ("ci-builder",   {"repo:read", "artifact:write"},  "the normal build grant"),
    ("deploy-bot",   {"deploy:staging"},               "staging deploy"),
    ("deploy-bot",   {"deploy:prod"},                  "'just for the hotfix'"),
    ("triage-agent", {"repo:write"},                   "'so it can fix what it finds'"),
    ("ci-builder",   {"secrets:read"},                 "'the build needs a token'"),
]
for identity, scopes, why in requests:
    try:
        grant(identity, scopes)
        print(f"GRANTED  {identity:14s} {sorted(scopes)}   — {why}")
    except GrantRefused as e:
        print(f"REFUSED  {identity:14s} {sorted(scopes)}   — {why}")
        print(f"         {e}")
'''),
  ("md", "## 3 · Where it breaks\n\n"
         "Three of those five requests are ones a real engineer would file with a "
         "straight face, and a reviewer would probably approve at least two. "
         "\"Just for the hotfix\" is how `deploy-bot` ends up with permanent "
         "production rights.\n\n"
         "But a ceiling has a hole in it, and it is worth seeing rather than being "
         "told about: **the ceiling constrains a single identity, not a chain of "
         "them.** If `triage-agent` cannot hold `repo:write`, but it can ask "
         "`ci-builder` to act for it, the ceiling has been walked around without "
         "ever being violated."),
  ("py", '''# Each individual grant is legal. The composition is not.
def call_chain(chain):
    print(" → ".join(chain))
    held = set()
    for identity in chain:
        held |= CEILINGS.get(identity, set())
    return held

reachable = call_chain(["triage-agent", "ci-builder", "deploy-bot"])
print("scopes reachable through the chain:", sorted(reachable))
print("triage-agent's own ceiling:        ", sorted(CEILINGS["triage-agent"]))
print("\\nNo ceiling was broken. The agent still reached artifact:write and")
print("deploy:staging, because it can ask something else to do the work.")
'''),
  ("md", "## 4 · The control\n\n"
         "The fix has two halves and you need both:\n\n"
         "**Narrowing on delegation.** When one identity acts for another, the "
         "resulting authority must be the *intersection* of what was presented "
         "and what the new actor may hold — never the union. This is the "
         "mechanism A2.5 builds properly as RFC 8693 token exchange.\n\n"
         "**Recording the chain.** The resource server must be able to see that "
         "the call arrived through `triage-agent`, so a policy can refuse it even "
         "when the immediate caller is allowed."),
  ("py", '''def delegate(presented_scopes, presenting, new_actor):
    """Intersection, not union. This one line is the whole control."""
    ceiling = CEILINGS.get(new_actor, set())
    return set(presented_scopes) & ceiling

start = grant("triage-agent", {"repo:read", "finding:comment"})
print("triage-agent holds:      ", sorted(start))
hop1 = delegate(start, "triage-agent", "ci-builder")
print("→ delegated to ci-builder:", sorted(hop1) or "∅ — nothing survives")
hop2 = delegate(hop1, "ci-builder", "deploy-bot")
print("→ delegated to deploy-bot:", sorted(hop2) or "∅ — nothing survives")

print("\\nAuthority can only shrink along a chain. The walk-around is closed,")
print("and no reviewer had to notice anything.")
'''),
  ("py", '''# Verify: property-test it. Delegation must NEVER widen, for any input.
import itertools, random
random.seed(7)
ids = list(CEILINGS)
violations = 0
for _ in range(2000):
    a, b = random.sample(ids, 2)
    held = set(random.sample(sorted(CEILINGS[a]), k=random.randint(0, len(CEILINGS[a]))))
    out = delegate(held, a, b)
    if not out <= held or not out <= CEILINGS[b]:
        violations += 1
print(f"2000 random delegations, widening violations: {violations}")
assert violations == 0
print("Property holds: result ⊆ presented AND result ⊆ new actor's ceiling.")
'''),
 ],
 "expect": "Two grants succeed; three are refused with the ceiling that refused "
           "them. The chain demo shows `triage-agent` reaching `artifact:write` "
           "and `deploy:staging` without breaking any ceiling. Intersection-based "
           "delegation reduces the chain to the empty set, and the 2000-case "
           "property test reports zero widening violations.",
 "challenge": "Find one identity in your estate whose ceiling is effectively "
              "\"everything\" — a break-glass role, a CI admin token. A ceiling "
              "cannot constrain it, so its controls have to be time and audit "
              "instead. A2.8 builds that.",
},

"A1.4": {
 "concept": """
"Reduce the blast radius" is advice. Advice does not survive a roadmap
discussion, because it cannot be traded off against a delivery date.

A **number** survives. It moves when you change the design, you can put it in a
review, and — most usefully — it can go into CI and fail a build.

The metric used throughout this curriculum is deliberately crude:

    blast radius = Σ over state-changing tools of
                     scope_weight × (2 if irreversible) × (0 if gated)

The absolute value means nothing. The **ratio between two designs** means a
great deal, and that is all a design metric has to do. Anyone who demands a
calibrated number before measuring anything ends up measuring nothing.
""",
 "steps": [
  ("md", "## 2 · Demo — four ways to build the same capability\n\n"
         "The requirement: an agent that can triage security findings, fix simple "
         "ones, and deploy the fix. Four architectures, all of which deliver it."),
  ("py", '''from dataclasses import dataclass

SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20, "internet": 50}

@dataclass(frozen=True)
class Tool:
    name: str; writes: bool = False; reversible: bool = True; scope: str = "self"

def blast(tools, gated=frozenset()):
    total = 0
    for t in tools:
        if not t.writes or t.name in gated:
            continue
        total += SCOPE_WEIGHT[t.scope] * (1 if t.reversible else 2)
    return total

READ   = [Tool("read_findings"), Tool("read_source")]
FIX    = [Tool("write_file", writes=True, scope="project"),
          Tool("open_pr",    writes=True, scope="project")]
SHIP   = [Tool("merge_pr", writes=True, scope="project", reversible=False),
          Tool("deploy",   writes=True, scope="org",     reversible=False)]

designs = {
    "A · one agent, everything":        (READ + FIX + SHIP, set()),
    "B · one agent, gate the shipping": (READ + FIX + SHIP, {"merge_pr", "deploy"}),
    "C · two agents (fixer / shipper)": (READ + FIX,        set()),
    "D · two agents + gated shipper":   (READ + FIX,        set()),
}
for name, (tools, gated) in designs.items():
    print(f"{name:36s} blast = {blast(tools, gated):3d}")

print("\\nDesign D's shipper agent, measured separately:")
print(f"{'    shipper (gated)':36s} blast = {blast(SHIP, {'merge_pr','deploy'}):3d}")
print(f"{'    shipper (ungated)':36s} blast = {blast(SHIP):3d}   ← the honest number")
'''),
  ("md", "## 3 · Where it breaks — the number can lie\n\n"
         "Design C looks best: blast 6. But it achieved that by *moving* the "
         "dangerous tools to another agent, not by removing them. If you measure "
         "each agent separately and report the lowest, you have optimised the "
         "metric rather than the risk. This is Goodhart's law arriving on "
         "schedule.\n\n"
         "The metric is only honest when it is computed **over the whole system**, "
         "including every agent that can be reached from the first one."),
  ("py", '''def system_blast(agents):
    """Sum across every agent in the system, not the one you are reviewing."""
    return sum(blast(tools, gated) for tools, gated in agents.values())

split_honest = {
    "fixer":   (READ + FIX, set()),
    "shipper": (SHIP,       set()),          # someone still runs this
}
split_gated = {
    "fixer":   (READ + FIX, set()),
    "shipper": (SHIP,       {"merge_pr", "deploy"}),
}
mono = {"one-agent": (READ + FIX + SHIP, set())}

for name, agents in (("monolith", mono), ("split, shipper ungated", split_honest),
                     ("split, shipper gated", split_gated)):
    print(f"{name:26s} system blast = {system_blast(agents):3d}")
print("\\nSplitting alone bought nothing. Splitting AND gating bought everything.")
print("Reporting only the fixer's number would have hidden that.")
'''),
  ("md", "## 4 · The control — put it in CI\n\n"
         "A metric nobody computes is a metric nobody has. The version that works "
         "is a budget, enforced by the build."),
  ("py", '''BUDGETS = {"L1": 0, "L2": 0, "L2.5": 20, "L3": 60}

def check_budget(system, rung):
    total = system_blast(system)
    budget = BUDGETS[rung]
    ok = total <= budget
    return ok, (f"system blast {total} {'≤' if ok else '>'} budget {budget} "
                f"for rung {rung}")

for name, system, rung in [
    ("split + gated shipper", split_gated,  "L2.5"),
    ("split, ungated shipper", split_honest, "L2.5"),
    ("monolith",              mono,         "L2.5"),
]:
    ok, msg = check_budget(system, rung)
    print(f"{'PASS' if ok else 'FAIL'}  {name:26s} {msg}")

ok, _ = check_budget(split_gated, "L2.5")
assert ok, "the intended design must pass its own budget"
print("\\nWired into CI, adding a tool now fails the build unless someone either")
print("gates it or raises the budget deliberately — which is a decision with a name on it.")
'''),

  ("md", "## 6 · The review, written down as a skill\n\n"
         "A number computed once is a fact about today. The skill below is the "
         "same computation as a procedure someone else can run, and its "
         "contract requires `blast_radius.inputs` beside the score.\n\n"
         "That requirement is the point: a metric nobody can decompose is a "
         "metric nobody can challenge, and an unchallengeable metric quietly "
         "stops being used."),
  ("py", SKILL_RUNTIME),
  ("skill", "architecture/blast-radius-review"),

  ("py", '''contract = contract_of(body)
TOOLS = READ + FIX + SHIP

def irreversibility(t):
    if not t.writes:      return 0                      # read-only
    if t.reversible:      return 1 if t.scope in ("self", "project") else 2
    return 3                                            # irreversible

# An agent that runs unattended overnight has a much longer path to a human
# than one that prompts. This term is usually the cheapest of the three to fix.
TIME_TO_STOP = 8 * 60 * 60

review = {
 "resources": [{"tool": t.name, "reachable": [t.scope],
                "unbounded": t.scope in ("org", "internet")} for t in TOOLS],
 "actions": [{"action": t.name, "irreversibility": irreversibility(t),
              "why": ("read-only" if not t.writes else
                      f"writes at {t.scope} scope, "
                      f"{'reversible' if t.reversible else 'irreversible'}")}
             for t in TOOLS],
 "time_to_human_stop_seconds": TIME_TO_STOP,
 "blast_radius": {"score": blast(TOOLS),
                  "inputs": {"resources": len(TOOLS),
                             "max_irreversibility": max(irreversibility(t) for t in TOOLS),
                             "seconds": TIME_TO_STOP}},
 "autonomy": {"current": "L3", "supported": "L2.5", "mismatch": True},
 "reductions": [{"change": f"gate {t.name} behind approval",
                 "new_score": blast(TOOLS, gated=frozenset({t.name})),
                 "friction": "low"}
                for t in TOOLS if irreversibility(t) == 3],
}
problems = check(review, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\\nblast radius {review['blast_radius']['score']} from "
      f"{review['blast_radius']['inputs']['resources']} tools, worst action grade "
      f"{review['blast_radius']['inputs']['max_irreversibility']}")
print(f"autonomy claimed {review['autonomy']['current']}, "
      f"supported {review['autonomy']['supported']} -> mismatch "
      f"{review['autonomy']['mismatch']}")
print("\\ncheapest reductions:")
for r in sorted(review["reductions"], key=lambda r: (r["new_score"], r["change"])):
    print(f"   {r['change']:38s} {review['blast_radius']['score']} -> {r['new_score']}")
print()
print("The mismatch is the finding. Grade-3 actions are why approval gates")
print("exist, and an agent running unattended with one is at L3 by deployment")
print("and L2.5 by design - misclassified, not brave.")
assert review["autonomy"]["mismatch"]
assert any(a["irreversibility"] == 3 for a in review["actions"])
'''),
 ],
 "expect": "Design A scores 92, B scores 6, C scores 6. Measured across the whole "
           "system, the ungated split still scores 92 while the gated split "
           "scores 6 — showing that splitting alone bought nothing. The budget "
           "check passes only the gated design.",
 "challenge": "Compute the system blast radius for your largest agent deployment, "
              "counting every agent it can invoke. Then pick a budget and see how "
              "many of your current designs would fail it. Set the budget at "
              "today's number and ratchet down; a budget nothing passes is "
              "ignored by lunchtime.",
},

"A1.5": {
 "concept": """
Multi-agent systems are sold on capability: a planner, a coder, a reviewer, each
good at one thing. What they actually introduce is **delegation depth**, and
depth is the variable nobody bounds.

Two properties change when one agent can call another:

**Authority composes.** A1.3 showed the walk-around: each grant legal, the
composition not. With three or four hops, no single reviewer sees the whole
path.

**Failure propagates.** If the orchestrator is compromised, every sub-agent is a
capability it now holds. The blast radius of the system is not the largest
agent's — it is the *sum over everything reachable*.

The topology decision is therefore a security decision, and the three common
shapes have genuinely different properties. This lesson measures them rather
than asserting a preference.
""",
 "steps": [
  ("md", "## 2 · Demo — three topologies, same capability\n\n"
         "**Star**: one orchestrator calls specialised workers.\n"
         "**Chain**: each agent hands to the next.\n"
         "**Mesh**: any agent may call any other.\n\n"
         "All three deliver \"triage → fix → review → ship\"."),
  ("py", '''SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}
AGENTS = {   # agent -> (scope of its most dangerous tool, reversible?)
    "orchestrator": ("self",    True),
    "triager":      ("project", True),
    "fixer":        ("project", True),
    "reviewer":     ("project", True),
    "shipper":      ("org",     False),
}
def agent_blast(a):
    scope, rev = AGENTS[a]
    return SCOPE_WEIGHT[scope] * (1 if rev else 2)

TOPOLOGIES = {
    "star":  {"orchestrator": ["triager", "fixer", "reviewer", "shipper"],
              "triager": [], "fixer": [], "reviewer": [], "shipper": []},
    "chain": {"orchestrator": ["triager"], "triager": ["fixer"],
              "fixer": ["reviewer"], "reviewer": ["shipper"], "shipper": []},
    "mesh":  {a: [b for b in AGENTS if b != a] for a in AGENTS},
}

def reachable(topo, start):
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        for m in topo.get(n, []):
            if m not in seen:
                seen.add(m); stack.append(m)
    return seen

def depth(topo, start, _seen=None):
    _seen = _seen or set()
    if start in _seen: return 0
    _seen = _seen | {start}
    kids = [depth(topo, k, _seen) for k in topo.get(start, []) if k not in _seen]
    return 1 + max(kids, default=0)

print(f"{'topology':10s}{'depth':>7}{'reachable from orchestrator':>32}{'blast':>8}")
print("-" * 60)
for name, topo in TOPOLOGIES.items():
    r = reachable(topo, "orchestrator")
    b = sum(agent_blast(a) for a in r)
    print(f"{name:10s}{depth(topo,'orchestrator'):>7}{len(r):>10} agents{'':<16}{b:>8}")
'''),
  ("md", "## 3 · Where it breaks\n\n"
         "All three reach the same four agents and the same blast radius of 55, so "
         "on that metric alone they are identical. The difference shows up under "
         "**compromise**: which agent, if taken over, gives the attacker what?"),
  ("py", '''print(f"{'topology':10s}{'compromised':14s}{'reaches':>9}{'blast':>7}   worst case")
print("-" * 64)
for name, topo in TOPOLOGIES.items():
    worst, worst_b = None, -1
    for a in AGENTS:
        r = reachable(topo, a)
        b = sum(agent_blast(x) for x in r) + agent_blast(a)
        if b > worst_b:
            worst, worst_b = a, b
    for a in ("fixer", worst):
        r = reachable(topo, a)
        b = sum(agent_blast(x) for x in r) + agent_blast(a)
        tag = "  ← worst" if a == worst else ""
        print(f"{name:10s}{a:14s}{len(r):>9}{b:>7}{tag}")
    print()
print("In the mesh, compromising the LOWEST-privilege agent reaches everything.")
print("In the star, only the orchestrator does. That is the whole argument.")
'''),
  ("md", "## 4 · The control — bound the depth, and make it refuse\n\n"
         "Two controls, both cheap:\n\n"
         "1. **A depth limit**, enforced at the token issuer rather than the "
         "orchestrator — because when the orchestrator is the compromised "
         "component, a check inside it is worth nothing.\n"
         "2. **No cycles.** A mesh where A can call B can call A has unbounded "
         "depth by construction."),
  ("py", '''MAX_DEPTH = 3

class DepthExceeded(Exception): pass

def call(chain, callee, topo):
    if callee not in topo.get(chain[-1], []):
        raise PermissionError(f"{chain[-1]} may not call {callee} in this topology")
    if callee in chain:
        raise DepthExceeded(f"cycle: {' → '.join(chain)} → {callee}")
    if len(chain) + 1 > MAX_DEPTH:
        raise DepthExceeded(f"depth {len(chain)+1} > limit {MAX_DEPTH}: "
                            f"{' → '.join(chain)} → {callee}")
    return chain + [callee]

for topo_name, path in [("star",  ["orchestrator", "shipper"]),
                        ("chain", ["orchestrator", "triager", "fixer", "reviewer"]),
                        ("mesh",  ["orchestrator", "fixer", "orchestrator"])]:
    topo = TOPOLOGIES[topo_name]
    chain = [path[0]]
    try:
        for nxt in path[1:]:
            chain = call(chain, nxt, topo)
        print(f"{topo_name:6s} OK      {' → '.join(chain)}")
    except (DepthExceeded, PermissionError) as e:
        print(f"{topo_name:6s} REFUSED {e}")
'''),
 ],
 "expect": "All three topologies reach 4 agents and a blast radius of 55. Under "
           "compromise they diverge sharply: in the mesh, taking over `fixer` "
           "reaches everything, while in the star only the orchestrator does. The "
           "depth limit permits the star's 2-hop call, refuses the chain at depth "
           "4, and refuses the mesh cycle.",
 "challenge": "Draw your actual agent topology, including the calls that were "
              "added for convenience rather than design. If any two agents can "
              "call each other, you have a mesh — and the lowest-privilege agent "
              "in it is your real attack surface.",
},

"A1.6": {
 "concept": """
The build-vs-buy conversation for agent infrastructure usually runs on features:
which platform supports more models, more connectors, more dashboards.

That is the wrong axis. Features can be added later. The question that cannot be
retrofitted is: **which controls can you still evidence in eighteen months, when
an auditor or a regulator asks?**

Two capabilities decide it, and both are effectively impossible to bolt on
afterwards because they have to be present at the moment an action happens:

- **Delegation chains.** Can you show, for one action, who caused it and through
  which intermediaries? If the platform authenticates every agent as a service
  account, that information was never recorded and cannot be reconstructed.
- **An independent stop mechanism.** Can you halt the fleet without the vendor's
  cooperation, and have you timed it?

Everything else — routing, observability, prompt management — is genuinely
easier to buy.
""",
 "steps": [
  ("md", "## 2 · Demo — score the options on evidenceability\n\n"
         "Three realistic options. The CNCF column is the open-source stack this "
         "curriculum uses throughout: SPIFFE/SPIRE for workload identity, OPA for "
         "policy, an agent gateway for mediation, OpenTelemetry for traces."),
  ("py", '''CONTROLS = {
 "AC-1": "agent identities distinct from human, separately revocable",
 "AC-2": "delegated authority narrows at every hop, recorded in an act chain",
 "SB-1": "egress deny-by-default with an allowlist",
 "SB-2": "privileged tools require approval below L3",
 "EV-1": "every action logged with the ACTING identity, not the principal",
 "EV-2": "harness accuracy evaluated against a held-out key per release",
 "ST-1": "a tested stop mechanism you own, timed",
}
RETROFITTABLE = {"AC-1": False, "AC-2": False, "SB-1": True, "SB-2": True,
                 "EV-1": False, "EV-2": True, "ST-1": False}

OPTIONS = {
 "vendor agent platform":
    {"AC-1": True, "AC-2": False, "SB-1": True,  "SB-2": True,
     "EV-1": False, "EV-2": True, "ST-1": False},
 "CNCF stack (SPIRE+OPA+gateway+OTel)":
    {"AC-1": True, "AC-2": True,  "SB-1": True,  "SB-2": True,
     "EV-1": True,  "EV-2": True, "ST-1": True},
 "roll your own from scratch":
    {"AC-1": True, "AC-2": True,  "SB-1": False, "SB-2": True,
     "EV-1": True,  "EV-2": False, "ST-1": False},
}
for name, support in OPTIONS.items():
    missing = [c for c in CONTROLS if not support[c]]
    hard = [c for c in missing if not RETROFITTABLE[c]]
    print(f"{name}")
    print(f"   covers {len(CONTROLS)-len(missing)}/{len(CONTROLS)}   "
          f"unfixable-later gaps: {hard or 'none'}")
    for c in missing:
        flag = "✗✗" if not RETROFITTABLE[c] else "✗ "
        print(f"   {flag} {c}  {CONTROLS[c]}")
    print()
'''),
  ("md", "## 3 · Where it breaks\n\n"
         "The vendor platform scores 5/7, which reads fine in a comparison table. "
         "But both of its gaps are marked `✗✗` — not retrofittable. In eighteen "
         "months you will be asked to produce an act chain for one action and you "
         "will not be able to, because the data was never captured.\n\n"
         "Let's make that concrete rather than rhetorical."),
  ("py", '''def audit_record(platform, action, principal, agent, chain):
    """What the platform can actually produce when asked about one action."""
    if platform["EV-1"] and platform["AC-2"]:
        return {"action": action, "acting_identity": agent,
                "on_behalf_of": principal, "chain": chain, "answerable": True}
    if platform["EV-1"]:
        return {"action": action, "acting_identity": agent,
                "on_behalf_of": "?", "chain": "not recorded", "answerable": False}
    return {"action": action, "acting_identity": principal,   # the human takes the blame
            "on_behalf_of": principal, "chain": "not recorded", "answerable": False}

for name, support in OPTIONS.items():
    r = audit_record(support, "merge_pr #4471", "dana@corp", "fixer-agent",
                     ["dana@corp", "orchestrator", "fixer-agent"])
    print(f"{name}")
    print(f"   {r}")
    if not r["answerable"]:
        print(f"   → cannot answer 'who caused this?'. "
              f"{'Logs name the human who never saw it.' if r['acting_identity']=='dana@corp' else ''}")
    print()
'''),
  ("md", "## 4 · The control — buy, but specify the two hard things\n\n"
         "This is not an argument for building everything. It is an argument for "
         "making two requirements non-negotiable in procurement, where they are "
         "cheap, instead of discovering them in an audit, where they are not."),
  ("py", '''PROCUREMENT_QUESTIONS = [
 ("Can you produce, for a single action, the full chain of identities that "
  "caused it — not just the last one?", "AC-2 + EV-1"),
 ("Can we halt every agent without your assistance, and what is the measured "
  "time from decision to the agent's next call failing?", "ST-1"),
 ("Is the agent's identity distinct from the human's, and separately "
  "revocable?", "AC-1"),
 ("Can we export the policy and the traces in a form we still own if we "
  "leave?", "exit strategy — see E2.4 (DORA)"),
]
for q, maps_to in PROCUREMENT_QUESTIONS:
    print(f"Q: {q}\\n   → {maps_to}\\n")

decision = {n: sum(s.values()) for n, s in OPTIONS.items()}
best = max(decision, key=decision.get)
print("scored:", decision)
print("recommended spine:", best)
assert best.startswith("CNCF")
'''),
 ],
 "expect": "The vendor platform covers 5/7 with two unfixable-later gaps (AC-2, "
           "ST-1, EV-1); the CNCF stack covers 7/7; rolling your own covers 5/7 "
           "with two hard gaps. The audit demo shows the vendor platform "
           "attributing the merge to the human who never saw it.",
 "challenge": "Send the four procurement questions to whichever platform you are "
              "currently evaluating. The answer to question 2 — a measured number, "
              "not 'yes we support that' — tells you most of what you need.",
},

"A1.7": {
 "concept": """
Routing between models is presented as a cost decision: use the big model where
it matters, the small one everywhere else. Real deployments do exactly that, and
the saving is genuine.

The security content is in *which stage gets which model*, because the stages
have very different relationships to authority:

- **Plan** — reads context, produces a strategy. Touches nothing.
- **Act** — chooses and invokes tools. This is where authority lives.
- **Verify** — decides whether the result is acceptable. This is where *trust*
  lives.

The common optimisation puts the large model on planning (it looks impressive in
demos) and a small fast model on acting, so the loop stays responsive. That
places the weakest reasoning next to the highest authority.

The second common optimisation puts the cheapest model on verification, because
verification "is just a check". That is worse: a weak verifier does not fail
loudly, it *approves*. B2.2 is an entire lesson on why.
""",
 "steps": [
  ("md", "## 2 · Demo — the routing table as a security artefact\n\n"
         "Open-weight models, since this curriculum assumes no frontier account: "
         "Kimi K2 and GLM for heavy reasoning, Llama 3.3 in its smaller sizes for "
         "the fast paths. The table below is the deliverable — it says which model "
         "may trigger what."),
  ("py", '''SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}

ROUTES = {
 #  stage      model                  tools it may invoke               gated
 "plan":   ("Kimi K2 (large, open)",  [],                                set()),
 "act":    ("GLM-4.6 (mid, open)",    [("write_file", "project", True),
                                       ("open_pr",    "project", True)], {"open_pr"}),
 "verify": ("GLM-4.6 (mid, open)",    [],                                set()),
 "summarise": ("Llama 3.3 8B (small)", [],                               set()),
}
def stage_blast(tools, gated):
    return sum(SCOPE_WEIGHT[s] * (1 if rev else 2)
               for n, s, rev in tools if n not in gated)

print(f"{'stage':11s}{'model':26s}{'tools':>6}{'blast':>7}")
print("-" * 52)
for stage, (model, tools, gated) in ROUTES.items():
    print(f"{stage:11s}{model:26s}{len(tools):>6}{stage_blast(tools, gated):>7}")
print("\\nOnly one stage holds tools at all, and its one risky tool is gated.")
'''),
  ("md", "## 3 · Where it breaks — the two cheap optimisations\n\n"
         "Both of these get proposed in every performance review of an agent "
         "system, and both are reasonable-sounding."),
  ("py", '''def evaluate(routes, label):
    total = sum(stage_blast(t, g) for _, t, g in routes.values())
    actor = [(s, m) for s, (m, t, g) in routes.items() if t]
    verifier = routes["verify"][0]
    print(f"{label}")
    print(f"   system blast {total:3d}   tools held by: {actor}")
    print(f"   verifier model: {verifier}")
    return total

good = evaluate(ROUTES, "as designed")

# optimisation 1: move tools to the fast small model so the loop feels snappy
opt1 = dict(ROUTES)
opt1["act"] = ("Llama 3.3 8B (small)",
               [("write_file", "project", True), ("open_pr", "project", True),
                ("deploy", "org", False)], set())
bad1 = evaluate(opt1, "\\n'speed up the act stage' — small model, ungated, +deploy")

# optimisation 2: verify with the cheapest thing available
opt2 = dict(ROUTES)
opt2["verify"] = ("Llama 3.2 1B (tiny)", [], set())
evaluate(opt2, "\\n'verification is just a check' — tiny model verifies")
print("   blast unchanged — and that is exactly why this one is dangerous:")
print("   the metric does not move, but every result is now trusted on the")
print("   word of the weakest model in the system. See B2.2.")
'''),
  ("md", "## 4 · The control — two routing rules\n\n"
         "State them as rules a policy engine can enforce, not as guidance:\n\n"
         "1. **Capability decides who plans. Blast radius decides who acts.** A "
         "model may only hold tools whose combined blast radius is within the "
         "budget for its tier.\n"
         "2. **The verifier is never below the actor.** If the model that acts is "
         "stronger than the model that checks it, the check is decorative."),
  ("py", '''TIER = {"Llama 3.2 1B (tiny)": 0, "Llama 3.3 8B (small)": 1,
        "GLM-4.6 (mid, open)": 2, "Kimi K2 (large, open)": 3}
TIER_BUDGET = {0: 0, 1: 3, 2: 20, 3: 60}

def routing_review(routes):
    problems = []
    for stage, (model, tools, gated) in routes.items():
        b = stage_blast(tools, gated)
        tier = TIER[model]
        if b > TIER_BUDGET[tier]:
            problems.append(f"{stage}: {model} (tier {tier}) holds blast {b} > "
                            f"budget {TIER_BUDGET[tier]}")
    actor_tier = max((TIER[m] for _, (m, t, g) in routes.items() if t), default=0)
    verifier_tier = TIER[routes["verify"][0]]
    if verifier_tier < actor_tier:
        problems.append(f"verifier tier {verifier_tier} < actor tier {actor_tier} "
                        f"— the check is weaker than the thing it checks")
    return problems

for label, r in (("as designed", ROUTES), ("fast-actor", opt1), ("cheap-verifier", opt2)):
    p = routing_review(r)
    print(f"{label:16s} {'PASS' if not p else 'FAIL'}")
    for x in p:
        print(f"                 ⚠ {x}")
assert not routing_review(ROUTES)
'''),
 ],
 "expect": "The designed routing holds tools in one stage only, with a system "
           "blast of 3, and passes both rules. The fast-actor variant jumps to 43 "
           "and fails the tier budget. The cheap-verifier variant leaves the blast "
           "radius unchanged and fails the second rule — the point being that the "
           "metric alone would not have caught it.",
 "challenge": "Write your own routing table with the tier budgets your risk "
              "appetite implies, then check it against a real deployment. The "
              "verifier rule catches the most systems, and it is the one that "
              "never shows up in a cost review.",
},
}
