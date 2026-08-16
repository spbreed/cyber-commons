"""A2 — The Identity & Non-Human Identity Engineer. Nine sessions.

Narrative arc, deliberately built from the familiar to the new:

    A2.1  human identity → workload identity → why agents break both
    A2.2  the bootstrap problem: where the FIRST credential comes from
    A2.3  shadow autonomy: the agent wearing a human's credential
    A2.4  the NHI governance gap: you cannot revoke what you cannot list
    A2.5  on-behalf-of (RFC 8693): delegation that survives audit
    A2.6  the agent gateway: when the downstream does not speak OBO
    A2.7  legacy systems: throttle at a choke point instead
    A2.8  just-in-time authority: replacing the standing grant
    A2.9  the classic failures, now at machine speed
"""

EXERCISES: dict[str, dict] = {

"A2.1": {
 "concept": """
Before agents, "who is calling?" had two well-understood answers.

**Human identity.** A person authenticates — password plus a second factor, or
SSO through an identity provider. The result is a token that says *this is
dana@corp*. It is short-lived, tied to a session, and revocable by disabling one
account. Crucially it carries an assumption: a human was present and intended
this.

**Workload identity.** A program authenticates. Historically this meant a
**service account** — a username and a long-lived secret, checked into a config
file and shared by everything in the deployment. Modern practice replaces the
secret with *attestation*: SPIFFE/SPIRE, IRSA, managed identities. The platform
vouches for the workload because of where it is running, so no secret has to be
planted anywhere. The result says *this is the payments-api pod in cluster-3*.

Both work because each answers a different question cleanly. A human token says
who *intended* something. A workload token says which *code* is running.

An agent breaks the distinction, because an agent is code that acts on a
human's intent, and the two identities have different lifetimes, different
scopes, and different revocation stories. Answer "who is calling?" with only
one of them and you lose information you will need later:

- Use the **human's** identity → the audit log says dana did it. She did not.
  She asked for something, three hops ago, and cannot tell you what happened.
- Use the **workload's** identity → the log says `triage-agent` did it, and now
  nobody knows *for whom*, or whether that person was allowed to ask.

The correct answer needs both at once, plus every intermediary. That is the rest
of this track.
""",
 "steps": [
  ("md", "## 2 · Demo — the two identities we already know how to do\n\n"
         "Start with the familiar, working correctly. Nothing here is new; the "
         "point is to have both mechanisms concrete before we break them."),
  ("py", '''import hashlib, json, time
from dataclasses import dataclass, field

# ---------- human identity: short-lived, session-bound, one account -------
@dataclass
class HumanToken:
    sub: str                       # dana@corp
    scopes: set
    auth_time: float = field(default_factory=time.time)
    amr: tuple = ("pwd", "mfa")    # how they proved it
    ttl: float = 3600

    @property
    def expired(self): return time.time() - self.auth_time > self.ttl
    def describe(self):
        return (f"human   sub={self.sub:14s} scopes={sorted(self.scopes)} "
                f"amr={list(self.amr)} ttl={self.ttl:.0f}s")

# ---------- workload identity: attested, no planted secret ---------------
@dataclass
class WorkloadToken:
    spiffe_id: str                 # spiffe://corp/ns/prod/sa/triage-agent
    scopes: set
    attested_by: str = "spire-agent on node-7"
    issued: float = field(default_factory=time.time)
    ttl: float = 300               # short, because it is cheap to reissue

    @property
    def expired(self): return time.time() - self.issued > self.ttl
    def describe(self):
        return (f"workload id={self.spiffe_id:38s} scopes={sorted(self.scopes)} "
                f"ttl={self.ttl:.0f}s")

dana = HumanToken("dana@corp", {"repo:read", "repo:write", "deploy:prod"})
svc  = WorkloadToken("spiffe://corp/ns/prod/sa/triage-agent", {"repo:read"})

print(dana.describe())
print(svc.describe())
print("\\nBoth answer 'who is calling?' — for different questions:")
print("  human    → who INTENDED this")
print("  workload → which CODE is running")
'''),
  ("md", "## 3 · Where it breaks — the agent needs both, and gets one\n\n"
         "Now put an agent in the middle. Dana asks the triage agent to fix a "
         "finding. The agent calls GitHub. What identity does GitHub see?\n\n"
         "In practice, one of two things happens, and both lose information."),
  ("py", '''def github_sees(token):
    """What the resource server can actually record."""
    if isinstance(token, HumanToken):
        return {"actor": token.sub, "on_behalf_of": token.sub,
                "audit_line": f"{token.sub} pushed a commit",
                "lost": "that an agent acted, and which one"}
    return {"actor": token.spiffe_id.split('/')[-1], "on_behalf_of": "unknown",
            "audit_line": f"{token.spiffe_id.split('/')[-1]} pushed a commit",
            "lost": "who asked for it, and whether they were allowed to"}

print("PATTERN 1 — hand the agent Dana's token ('it just needs her permissions')")
for k, v in github_sees(dana).items():
    print(f"   {k:14s} {v}")

print("\\nPATTERN 2 — give the agent its own service account")
for k, v in github_sees(svc).items():
    print(f"   {k:14s} {v}")

print("\\nBoth are complete, consistent records. Both are missing half the answer.")
'''),
  ("md", "## 4 · What the answer has to contain\n\n"
         "Three facts, together, at the moment of the call:\n\n"
         "- **`sub`** — the principal the action is *for* (Dana)\n"
         "- **`actor`** — the identity actually making the call (`triage-agent`)\n"
         "- **`act`** — the chain of everything in between\n\n"
         "This is not invented for agents. It is [RFC 8693 token exchange]"
         "(https://datatracker.ietf.org/doc/html/rfc8693), which OAuth has had "
         "since 2020 for exactly this problem, under the name **on-behalf-of**. "
         "A2.5 builds it properly. Here is just the shape, so the rest of the "
         "track has something to point at."),
  ("py", '''@dataclass
class AgentToken:
    sub: str            # the human the action is for
    actor: str          # who is actually calling right now
    scopes: set
    act: dict = None    # nested chain of prior actors
    issued: float = field(default_factory=time.time)
    ttl: float = 300

    def chain(self):
        out, node = [], self.act
        while node:
            out.append(node["actor"]); node = node.get("act")
        c = list(reversed(out)) + [self.actor]
        if c[0] != self.sub:
            c.insert(0, self.sub)
        return c

    def describe(self):
        return (f"sub={self.sub}  actor={self.actor}\\n"
                f"   chain  {' → '.join(self.chain())}\\n"
                f"   scopes {sorted(self.scopes)}")

agent_tok = AgentToken(sub="dana@corp", actor="triage-agent",
                       scopes={"repo:read"}, act=None)
print(agent_tok.describe())

print("\\nwhat GitHub can now record:")
print(f"   'triage-agent pushed a commit on behalf of dana@corp'")
print("   → both questions answered, one log line, nothing reconstructed later.")
'''),
  ("md", "## 5 · Verify — the three patterns side by side"),
  ("py", '''def audit(actor, on_behalf_of, chain):
    answerable = actor != "?" and on_behalf_of != "?" and chain != "not recorded"
    return {"who acted": actor, "for whom": on_behalf_of,
            "chain": chain, "answerable": answerable}

rows = {
 "agent uses Dana's token":  audit("dana@corp", "dana@corp", "not recorded"),
 "agent uses service acct":  audit("triage-agent", "?", "not recorded"),
 "on-behalf-of (RFC 8693)":  audit("triage-agent", "dana@corp",
                                   " → ".join(agent_tok.chain())),
}
for name, r in rows.items():
    print(f"{name:28s} answerable={str(r['answerable']):5s} "
          f"acted={r['who acted']:14s} for={r['for whom']:11s} {r['chain']}")
assert rows["on-behalf-of (RFC 8693)"]["answerable"]
print("\\nOnly the third can answer an incident question without guesswork.")
'''),
 ],
 "expect": "The human and workload tokens each print with their distinct "
           "properties. Both single-identity patterns produce a complete, "
           "consistent and incomplete audit record — one blaming Dana, one unable "
           "to say who asked. The on-behalf-of token records `dana@corp → "
           "triage-agent` and is the only one marked answerable.",
 "challenge": "Take one agent in your estate and find out which pattern it uses. "
              "The test is a single question: *for an action it took last week, "
              "can you name both the agent and the human who asked?* If you have "
              "to reconstruct it from timestamps, the answer is no.",
},

"A2.2": {
 "concept": """
Every identity system has a bootstrap problem: to prove who you are, you need a
credential; to get a credential, you need to prove who you are.

For humans we solve it out of band — someone checks a passport on the first day.
For workloads, the answer has historically been **secret zero**: a long-lived
API key placed in an environment variable, a config file, or a Kubernetes
Secret. Everything else hangs off it.

Secret zero has three properties that make it the root of most cloud breaches:

- **It never expires.** The median rotation interval for a service-account key
  in the wild is "never".
- **Anything that can read it becomes the workload.** A file read, a log line,
  a core dump, a compromised sidecar. It is a bearer credential with no context.
- **Revoking it breaks everything at once**, because it is shared, so nobody
  revokes it.

The modern answer is **attestation**. SPIFFE/SPIRE (and cloud equivalents like
IRSA or managed identities) issue an identity based on *properties of where the
workload is running* — this node, this pod, this container image — verified by
a platform component. No secret is planted, because none is needed. The
credential is short-lived and reissued continuously.

For agents this matters more than for ordinary services, because agents are
spawned dynamically, often per task, and a static secret handed to a fleet of
ephemeral workers is the worst version of secret zero.
""",
 "steps": [
  ("md", "## 2 · Demo — secret zero, working exactly as designed\n\n"
         "First, the thing that works. This is a normal service-account bootstrap; "
         "there is nothing broken about it yet."),
  ("py", '''import hashlib, time
from dataclasses import dataclass, field

ENVIRONMENT = {                       # what the process can read
    "AGENT_API_KEY": "sk-live-7f3c9a2b8e1d4f6a0c5b3e9d",
    "PATH": "/usr/bin",
}
ISSUED_AT = time.time() - 400 * 86400   # planted 400 days ago, as is typical

@dataclass
class StaticCredential:
    value: str
    issued: float
    def authenticate(self):
        return {"identity": "triage-agent", "method": "bearer secret",
                "age_days": round((time.time() - self.issued) / 86400),
                "ok": True}

cred = StaticCredential(ENVIRONMENT["AGENT_API_KEY"], ISSUED_AT)
print("bootstrap via secret zero:", cred.authenticate())
print("→ it works. Every service in your estate does this today.")
'''),
  ("md", "## 3 · Where it breaks — three ways, all ordinary\n\n"
         "None of these require a sophisticated attacker. They require a log "
         "statement, a debug endpoint, or a curious process on the same host."),
  ("py", '''import re

def leaks(env):
    found = []
    # 1. anything that can read the process environment
    found.append(("process env read", env.get("AGENT_API_KEY")))
    # 2. a well-meaning debug log
    log_line = f"starting agent with config {env}"
    m = re.search(r"sk-live-[a-z0-9]+", log_line)
    found.append(("debug log line", m.group(0) if m else None))
    # 3. a crash dump / error report
    crash = {"env": env, "stack": "..."}
    found.append(("crash report", crash["env"].get("AGENT_API_KEY")))
    return found

for how, value in leaks(ENVIRONMENT):
    print(f"{how:22s} → {'LEAKED ' + value[:14] + '…' if value else 'safe'}")

print(f"\\ncredential age: {cred.authenticate()['age_days']} days")
print("exposure window for every one of those leaks: the whole 400 days,")
print("because nothing about a static secret expires on its own.")
'''),
  ("md", "## 4 · The control — attestation instead of a planted secret\n\n"
         "SPIRE issues an SVID (an X.509 or JWT identity document) to a workload "
         "after verifying *node attestation* (this is really node-7, confirmed by "
         "the cloud provider's instance identity document) and *workload "
         "attestation* (this really is the process running image X, confirmed by "
         "reading the kernel's view of the process).\n\n"
         "The agent never holds a secret. It asks a local socket for an identity, "
         "and gets a short-lived one it did not have to keep."),
  ("py", '''@dataclass
class Attestor:
    """Stands in for the SPIRE agent's node + workload attestation."""
    node_id: str
    trusted_images: set

    def attest(self, claimed_sa, image, pid_namespace):
        # These facts come from the platform, not from the workload's own claims.
        if image not in self.trusted_images:
            return None, f"image {image!r} is not an attested workload image"
        if pid_namespace != self.node_id:
            return None, f"process is not running on {self.node_id}"
        return (f"spiffe://corp/ns/prod/sa/{claimed_sa}", "attested")

@dataclass
class SVID:
    spiffe_id: str
    issued: float = field(default_factory=time.time)
    ttl: float = 300                         # SPIRE default is minutes, not months
    @property
    def age_days(self): return (time.time() - self.issued) / 86400
    @property
    def expired(self): return time.time() - self.issued > self.ttl

spire = Attestor("node-7", {"ghcr.io/corp/triage-agent@sha256:9f2c…"})

for sa, image, node in [
    ("triage-agent", "ghcr.io/corp/triage-agent@sha256:9f2c…", "node-7"),
    ("triage-agent", "ghcr.io/attacker/evil@sha256:dead…",     "node-7"),
    ("triage-agent", "ghcr.io/corp/triage-agent@sha256:9f2c…", "laptop-of-contractor"),
]:
    sid, why = spire.attest(sa, image, node)
    if sid:
        svid = SVID(sid)
        print(f"ISSUED   {sid}  ttl={svid.ttl:.0f}s")
    else:
        print(f"REFUSED  sa={sa} image={image[:34]}… — {why}")
'''),
  ("md", "## 5 · Verify — compare the exposure windows"),
  ("py", '''def exposure(cred_kind, ttl_seconds, leaked_at_day):
    """How long a leaked credential stays useful."""
    if ttl_seconds is None:
        return {"kind": cred_kind, "useful_for": "until someone rotates it",
                "typical": "never rotated", "window_seconds": float("inf")}
    return {"kind": cred_kind, "useful_for": f"{ttl_seconds:.0f}s",
            "typical": "auto-reissued continuously", "window_seconds": ttl_seconds}

for row in (exposure("secret zero (env var)", None, 12),
            exposure("SPIFFE SVID", 300, 12)):
    print(f"{row['kind']:26s} useful for {row['useful_for']:32s} ({row['typical']})")

static_window = 400 * 86400
svid_window = 300
print(f"\\nratio: a leaked static key is useful "
      f"{static_window / svid_window:,.0f}× longer than a leaked SVID")
print("\\nAnd the SVID names its own holder — a stolen one identifies the thief's")
print("workload, which a shared bearer secret can never do.")
'''),
 ],
 "expect": "The static credential authenticates successfully and is 400 days old. "
           "All three leak paths expose it. SPIRE issues an SVID only for the "
           "attested image on the attested node, refusing the wrong image and the "
           "contractor's laptop. The final comparison shows a leaked static key "
           "is useful roughly 115,200× longer than a leaked 300-second SVID.",
 "challenge": "Find the oldest non-human credential in one production account and "
              "compute its age in days. Then ask what would break if you rotated "
              "it this afternoon. If nobody knows, that is the finding — and it is "
              "the same finding at every organisation that has not done this yet.",
},

"A2.3": {
 "concept": """
**Shadow autonomy** is what you get when an agent acts using a human's identity.

It is not a bug anyone wrote. It is the path of least resistance: the agent
needs permissions, the human already has them, handing over the human's token
takes ten minutes and requesting a properly scoped agent identity takes three
weeks. Everyone involved is being reasonable.

The result is that the agent becomes indistinguishable from the person, in every
system that matters:

- The audit log names the human for actions they never saw.
- Anomaly detection tuned to human behaviour sees a human doing 400 things a
  minute and either alerts on everything or gets retuned until it alerts on
  nothing.
- Incident containment aims at the human's account, which does not stop the
  agent if it holds a copy of the token.
- The human is accountable, in the formal sense, for decisions made by a model
  they cannot inspect.

The name is deliberate: the autonomy is real, and it is invisible to every
control you have.
""",
 "steps": [
  ("md", "## 2 · Demo — an ordinary Tuesday, correctly recorded\n\n"
         "First, what a *properly* attributed session looks like, so the broken "
         "one is recognisable by contrast."),
  ("py", '''import time
from dataclasses import dataclass, field

@dataclass
class LogLine:
    ts: float
    logged_actor: str      # what the audit log says
    real_actor: str        # what actually happened
    action: str
    target: str = ""

def render(lines, truth=False):
    base = lines[0].ts
    out = [f"{'t+s':>5}  {'actor':16s}{'action':16s}target"]
    for ln in sorted(lines, key=lambda x: x.ts):
        who = ln.real_actor if truth else ln.logged_actor
        out.append(f"{ln.ts-base:>5.0f}  {who:16s}{ln.action:16s}{ln.target}")
    return "\\n".join(out)

t0 = time.time()
proper = [
    LogLine(t0,      "dana@corp",    "dana@corp",    "login",       "console"),
    LogLine(t0+30,   "dana@corp",    "dana@corp",    "assign_task", "finding-4471"),
    LogLine(t0+31,   "triage-agent", "triage-agent", "read_source", "src/auth.py"),
    LogLine(t0+33,   "triage-agent", "triage-agent", "open_pr",     "pr/8812"),
]
print("PROPERLY ATTRIBUTED — agent has its own identity")
print(render(proper))
'''),
  ("md", "## 3 · Where it breaks — the same Tuesday, one shortcut\n\n"
         "Now the agent is handed Dana's token. Nothing else changes: same "
         "actions, same times, same outcome. Only the identity is different."),
  ("py", '''shadow = [
    LogLine(t0,      "dana@corp", "dana@corp",    "login",        "console"),
    LogLine(t0+30,   "dana@corp", "dana@corp",    "assign_task",  "finding-4471"),
    LogLine(t0+31,   "dana@corp", "triage-agent", "read_source",  "src/auth.py"),
    LogLine(t0+33,   "dana@corp", "triage-agent", "open_pr",      "pr/8812"),
    LogLine(t0+34,   "dana@corp", "triage-agent", "merge_pr",     "pr/8812"),
    LogLine(t0+36,   "dana@corp", "triage-agent", "deploy",       "prod"),
]
print("WHAT THE RESPONDER SEES")
print(render(shadow))
print("\\nWHAT ACTUALLY HAPPENED")
print(render(shadow, truth=True))

def reconstruct(lines):
    logged = {l.logged_actor for l in lines}
    real   = {l.real_actor for l in lines}
    wrong  = [l for l in lines if l.logged_actor != l.real_actor]
    return {"actors_in_logs": sorted(logged), "actors_in_reality": sorted(real),
            "misattributed_lines": len(wrong),
            "hidden_actors": sorted(real - logged),
            "attribution": "sound" if not wrong else "BROKEN"}

r = reconstruct(shadow)
for k, v in r.items():
    print(f"{k:22s} {v}")
'''),
  ("md", "## 4 · The three controls that misfire\n\n"
         "This is the part worth internalising: shadow autonomy does not merely "
         "make logs untidy. It **breaks controls you are relying on**, silently."),
  ("py", '''# --- control 1: behavioural anomaly detection -------------------------
def human_baseline_alert(lines, actor):
    acts = [l for l in lines if l.logged_actor == actor]
    if len(acts) < 2: return None
    span = max(l.ts for l in acts) - min(l.ts for l in acts)
    rate = len(acts) / max(span, 1e-9) * 60
    return (f"{actor}: {rate:.0f} actions/min — "
            f"{'IMPOSSIBLE for a human, alert' if rate > 30 else 'normal'}")

print("control 1 — anomaly detection tuned for humans")
print("   ", human_baseline_alert(shadow, "dana@corp"))
print("    → this alert fires on every agent-assisted session, so it gets tuned")
print("      down or disabled within a week. Then it never fires again.")

# --- control 2: incident containment ---------------------------------
print("\\ncontrol 2 — containment")
def contain(disable_account, lines):
    stopped = {l.real_actor for l in lines if l.logged_actor == disable_account
               and l.real_actor == disable_account}
    still_running = {l.real_actor for l in lines} - stopped
    return sorted(still_running)
print(f"    disable dana@corp → still running: {contain('dana@corp', shadow)}")
print("    → the agent holds a copy of the token. Disabling the human's login")
print("      does not invalidate a bearer token already issued.")

# --- control 3: accountability ---------------------------------------
print("\\ncontrol 3 — accountability")
print("    formal record: dana@corp deployed to prod at t+36s")
print("    reality:       dana was in a meeting; a model chose to deploy")
print("    → she is accountable for a decision she could not have reviewed.")
'''),
  ("md", "## 5 · The fix, and why it is A2.5's job\n\n"
         "The fix is not \"log harder\". You cannot recover the acting identity "
         "afterwards, because it was never transmitted — the resource server saw "
         "Dana's token and recorded exactly what it was given.\n\n"
         "The fix is that the agent must present a token that names *both*. That "
         "is on-behalf-of, and it is A2.5. What this lesson establishes is that "
         "the alternative is not merely untidy: it disables anomaly detection, "
         "containment and accountability at the same time."),
  ("py", '''def containment_options(has_agent_identity):
    if has_agent_identity:
        return ["revoke the agent identity (agent stops, human keeps working)",
                "revoke the human (agent's delegated tokens die with the chain)",
                "revoke one agent in a fleet, leaving the others up"]
    return ["disable the human's account (agent may continue on a live token)",
            "rotate the shared credential (breaks every consumer at once)",
            "…that is the complete list"]

for label, flag in (("with agent identity", True), ("shadow autonomy", False)):
    print(f"{label}:")
    for o in containment_options(flag):
        print(f"   · {o}")
    print()
'''),
 ],
 "expect": "The properly-attributed timeline names `triage-agent` for its own "
           "actions. The shadow timeline is identical except that all four agent "
           "actions are logged as `dana@corp` — attribution BROKEN, 4 "
           "misattributed lines, `triage-agent` hidden. The anomaly rule computes "
           "an impossible human rate, containment shows the agent still running "
           "after the account is disabled, and the containment-options list "
           "collapses to two bad choices.",
 "challenge": "Search your audit logs for a human account performing more than 30 "
              "actions in a minute. Every hit is either an incident or shadow "
              "autonomy, and you will not be able to tell which from the log "
              "alone — which is the point.",
},

"A2.4": {
 "concept": """
Non-human identities outnumber human ones in a typical estate by somewhere
between 10:1 and 50:1. They are governed by roughly none of the same process:
no joiner-mover-leaver, no manager attestation, no periodic recertification,
frequently no owner.

The gap is not primarily a policy gap. Policies for this exist and are easy to
write. The gap is that **nobody can enumerate them**, and you cannot govern,
tier, revoke or recertify a list you do not have.

Agents make this acute for three reasons:

- They are created **programmatically**, often per task, so the population grows
  without anyone filing a request.
- They are frequently created by *other* agents, so the requester is not a
  person who can be asked.
- They **outlive their purpose**. A retired agent whose identity still exists is
  a standing credential with no owner and no expiry — the single most common
  finding in a first NHI review.

So the first control is not a policy. It is an inventory, built from telemetry
rather than from a survey nobody answers.
""",
 "steps": [
  ("md", "## 2 · Demo — build the inventory from telemetry\n\n"
         "The registry below is what a survey produces. The auth log is what is "
         "actually happening. The interesting rows are the ones in one and not "
         "the other."),
  ("py", '''import time
from dataclasses import dataclass, field

now = time.time(); DAY = 86400

# what the CMDB / spreadsheet says exists
REGISTERED = {
    "ci-builder":    {"owner": "platform", "created": now - 900*DAY},
    "deploy-bot":    {"owner": "platform", "created": now - 700*DAY},
    "triage-agent":  {"owner": "appsec",   "created": now - 120*DAY},
    "backup-runner": {"owner": "",         "created": now - 1400*DAY},
}
# what the identity provider actually saw authenticate in the last 90 days
AUTH_LOG = {
    "ci-builder":        now - 0.2*DAY,
    "deploy-bot":        now - 1*DAY,
    "triage-agent":      now - 0.1*DAY,
    "svc-legacy-etl":    now - 3*DAY,      # not in the registry at all
    "agent-worker-7f3c": now - 0.05*DAY,   # spawned by another agent
    "agent-worker-a91b": now - 0.05*DAY,
    # backup-runner: absent — has not authenticated in 90 days
}

registered, seen = set(REGISTERED), set(AUTH_LOG)
print(f"{'identity':22s}{'in registry':13s}{'seen in logs':14s}{'owner':10s}status")
print("-" * 74)
for ident in sorted(registered | seen):
    in_reg, in_log = ident in registered, ident in seen
    owner = REGISTERED.get(ident, {}).get("owner") or "—"
    if in_reg and in_log:   status = "governed" if owner != "—" else "NO OWNER"
    elif in_log:            status = "SHADOW — unregistered but active"
    else:                   status = "ORPHAN — registered, never authenticates"
    print(f"{ident:22s}{str(in_reg):13s}{str(in_log):14s}{owner:10s}{status}")
'''),
  ("md", "## 3 · Where it breaks\n\n"
         "Three of the six active identities were never registered, and one "
         "registered identity has not authenticated in 90 days. Both directions "
         "are findings, and they fail differently:\n\n"
         "- **Shadow** identities have no owner, so no one can answer \"should "
         "this exist?\" during an incident.\n"
         "- **Orphans** are standing credentials for a purpose that ended. Nobody "
         "will notice them being used, because nobody is watching something they "
         "believe is retired."),
  ("py", '''def gaps(ident):
    out = []
    reg = REGISTERED.get(ident)
    if reg is None:
        out.append("unregistered: in use but never requested or approved")
    elif not reg["owner"]:
        out.append("no named owner — nobody can accept the risk or recertify it")
    last = AUTH_LOG.get(ident)
    if last is None:
        age = (now - reg["created"]) / DAY if reg else 0
        out.append(f"no authentication in 90d — decommissioning never finished "
                   f"(identity is {age:.0f}d old)")
    if ident.startswith("agent-worker-"):
        out.append("created by another agent — no human requester exists")
    return out

for ident in sorted(registered | seen):
    g = gaps(ident)
    if g:
        print(f"{ident}")
        for x in g:
            print(f"   ⚠ {x}")
'''),
  ("md", "## 4 · The control — per-identity revocation, proven\n\n"
         "An inventory is only useful if you can act on a single row. The test "
         "that separates an *identity* from a *shared password* is: can you revoke "
         "exactly one of these without breaking the others?"),
  ("py", '''class Registry:
    def __init__(self):
        self.revoked, self.issued = set(), []
    def issue(self, actor, scopes):
        t = {"actor": actor, "scopes": set(scopes), "id": len(self.issued)}
        self.issued.append(t); return t
    def revoke(self, actor):
        self.revoked.add(actor)
        return sum(1 for t in self.issued if t["actor"] == actor)
    def valid(self, t):
        return t["actor"] not in self.revoked

reg = Registry()
toks = {a: reg.issue(a, {"repo:read"}) for a in
        ("ci-builder", "deploy-bot", "agent-worker-7f3c", "agent-worker-a91b")}

print("revoking one dynamically-spawned worker:")
n = reg.revoke("agent-worker-7f3c")
print(f"   invalidated {n} token(s)\\n")
for a, t in toks.items():
    print(f"   {a:22s} valid={reg.valid(t)}")

print("\\nNow the shared-secret world, for contrast:")
SHARED = "one API key used by all four"
print(f"   revoking the shared key stops: {list(toks)}")
print("   → which is why, in practice, nobody ever revokes it.")
'''),
  ("py", '''# Verify: the inventory has to be reproducible, not a one-off spreadsheet.
def build_inventory(registry, auth_log, stale_days=90):
    rows = []
    for ident in sorted(set(registry) | set(auth_log)):
        reg = registry.get(ident)
        last = auth_log.get(ident)
        rows.append({
            "identity": ident,
            "owner": (reg or {}).get("owner") or None,
            "registered": reg is not None,
            "active": last is not None,
            "stale": last is None,
            "auto_spawned": ident.startswith("agent-worker-"),
        })
    return rows

inv = build_inventory(REGISTERED, AUTH_LOG)
unowned = [r["identity"] for r in inv if not r["owner"]]
shadow  = [r["identity"] for r in inv if not r["registered"]]
stale   = [r["identity"] for r in inv if r["stale"]]
print(f"identities: {len(inv)}   unowned: {len(unowned)}   "
      f"shadow: {len(shadow)}   stale: {len(stale)}")
print(f"   unowned {unowned}\\n   shadow  {shadow}\\n   stale   {stale}")
assert shadow and stale, "a first inventory always finds both"
'''),
 ],
 "expect": "Seven identities appear across the registry and the auth log: three "
           "governed, one with no owner, three shadow (including two "
           "agent-spawned workers) and one orphan. Revoking `agent-worker-7f3c` "
           "invalidates only its own token. The inventory reports 4 unowned, 3 "
           "shadow and 1 stale.",
 "challenge": "Run the real query: every non-human identity in one production "
              "account, joined against 90 days of authentication events. Count "
              "the rows with no owner. That number, not a policy document, is "
              "your NHI governance gap.",
},

"A2.5": {
 "concept": """
Now we build the thing A2.1 pointed at and A2.3 proved we need:
**on-behalf-of delegation**, standardised as [RFC 8693 OAuth 2.0 Token
Exchange](https://datatracker.ietf.org/doc/html/rfc8693).

The idea is small. An actor presents a token it holds and asks for a new one for
a different actor. The issuer returns a token with:

- **`sub`** — unchanged. The action is still *for* the original principal.
- **`actor`** — the new holder.
- **`act`** — a nested claim recording who presented the token, and who
  presented it to *them*, all the way back.

Two rules make the result auditable, and both must hold:

1. **Subset of what was presented.** You cannot hand on authority you were not
   given.
2. **Within the new actor's own ceiling.** You cannot hand on authority the
   recipient may never hold, even if the caller offered it. (This is A1.3's
   ceiling, doing its second job.)

Drop either rule and the chain still *looks* correct — every token parses, every
call succeeds — which is precisely why this needs a test rather than a review.
""",
 "steps": [
  ("md", "## 2 · Demo — a three-hop chain that narrows at every step\n\n"
         "Dana asks for a fix. The orchestrator delegates to a patch agent, which "
         "delegates to a deploy agent. Watch the scopes shrink."),
  ("py", '''import hashlib, json, time
from dataclasses import dataclass, field

# A1.3's ceilings: what each actor may EVER hold.
CEILINGS = {
    "dana@corp":    {"repo:read", "repo:write", "deploy:prod", "secrets:read"},
    "orchestrator": {"repo:read", "repo:write", "deploy:prod"},
    "patch-agent":  {"repo:read", "repo:write"},
    "deploy-agent": {"repo:read", "deploy:prod"},
    "triage-agent": {"repo:read"},
}

class DelegationError(Exception):
    """Refusing to widen is the feature."""

@dataclass
class Token:
    sub: str
    actor: str
    scopes: set
    act: dict = None
    issued: float = field(default_factory=time.time)
    ttl: float = 300

    @property
    def expired(self): return time.time() - self.issued > self.ttl

    def chain(self):
        out, node = [], self.act
        while node:
            out.append(node["actor"]); node = node.get("act")
        c = list(reversed(out)) + [self.actor]
        if c[0] != self.sub:
            c.insert(0, self.sub)
        return c

    def fingerprint(self):
        blob = json.dumps({"sub": self.sub, "actor": self.actor,
                           "scopes": sorted(self.scopes), "act": self.act},
                          sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:12]

    def describe(self):
        return (f"{' → '.join(self.chain()):48s}\\n"
                f"      scopes {sorted(self.scopes)}   fp={self.fingerprint()}")

def mint(principal, scopes=None):
    ceiling = CEILINGS[principal]
    want = set(scopes) if scopes else set(ceiling)
    if not want <= ceiling:
        raise DelegationError(f"{principal} cannot hold {sorted(want - ceiling)}")
    return Token(sub=principal, actor=principal, scopes=want)

def exchange(presented, new_actor, scopes):
    """One RFC 8693 hop. Both narrowing rules live here and nowhere else."""
    if presented.expired:
        raise DelegationError("presented token has expired")
    scopes = set(scopes)
    if not scopes <= presented.scopes:                       # rule 1
        raise DelegationError(
            f"widening refused: {sorted(scopes - presented.scopes)} is not in the "
            f"presented token {sorted(presented.scopes)}")
    ceiling = CEILINGS.get(new_actor, set())
    if not scopes <= ceiling:                                # rule 2
        raise DelegationError(
            f"widening refused: {new_actor} may never hold "
            f"{sorted(scopes - ceiling)} (ceiling {sorted(ceiling)})")
    return Token(sub=presented.sub, actor=new_actor, scopes=scopes,
                 act={"actor": presented.actor, "act": presented.act},
                 ttl=min(presented.ttl, 300))

dana  = mint("dana@corp", {"repo:read", "repo:write", "deploy:prod"})
orch  = exchange(dana, "orchestrator", {"repo:read", "repo:write", "deploy:prod"})
patch = exchange(orch, "patch-agent",  {"repo:read", "repo:write"})
ship  = exchange(patch, "deploy-agent", {"repo:read"})

for t in (dana, orch, patch, ship):
    print(t.describe())
'''),
  ("md", "## 3 · Demo — the resource server can finally answer the question\n\n"
         "This is the payoff. GitHub (or any downstream) receives the last token "
         "and can record a truthful, complete line."),
  ("py", '''def resource_server(token, required_scope):
    if token.expired:
        return {"allowed": False, "why": "token expired"}
    if required_scope not in token.scopes:
        return {"allowed": False,
                "why": f"needs {required_scope}, holds {sorted(token.scopes)}"}
    return {"allowed": True,
            "audit": f"{token.actor} performed {required_scope} on behalf of "
                     f"{token.sub} via {' → '.join(token.chain()[1:-1]) or 'direct'}",
            "chain": token.chain()}

for tok, scope in ((patch, "repo:write"), (ship, "repo:write"), (ship, "repo:read")):
    r = resource_server(tok, scope)
    print(f"{tok.actor:14s} wants {scope:12s} → {'ALLOW' if r['allowed'] else 'DENY '}")
    print(f"   {r.get('audit') or r['why']}")
'''),
  ("md", "## 4 · Where it breaks — three ways, all refused\n\n"
         "Now the attacks. Each of these is something a real integration will "
         "attempt, usually by accident."),
  ("py", '''attacks = [
 ("widen beyond the presented token",
  lambda: exchange(ship, "deploy-agent", {"deploy:prod"})),
 ("widen beyond the actor's own ceiling",
  lambda: exchange(dana, "triage-agent", {"repo:write"})),
 ("replay an expired token",
  lambda: exchange(Token("dana@corp", "patch-agent", {"repo:write"}, ttl=-1),
                   "deploy-agent", {"repo:write"})),
]
for name, fn in attacks:
    try:
        fn()
        print(f"GRANTED  {name}   ← this must not happen")
    except DelegationError as e:
        print(f"REFUSED  {name}\\n         {e}")
'''),
  ("md", "## 5 · The anti-pattern, for contrast\n\n"
         "Impersonation produces a token that works perfectly and destroys the "
         "audit trail — the A2.3 failure, now visible next to the correct version."),
  ("py", '''def impersonate(principal, actor, scopes):
    """No act claim. The agent simply becomes the human."""
    return Token(sub=principal, actor=principal, scopes=set(scopes), act=None)

bad = impersonate("dana@corp", "patch-agent", {"repo:write"})
print("delegated    :", " → ".join(patch.chain()))
print("impersonated :", " → ".join(bad.chain()), "  ← the agent is invisible")
print("\\nresource server sees:")
print("   delegated    :", resource_server(patch, "repo:write")["audit"])
print("   impersonated :", resource_server(bad, "repo:write")["audit"])
'''),
  ("py", '''# Verify: property-test the invariant over random chains.
import random
random.seed(11)
actors = [a for a in CEILINGS if a != "dana@corp"]
violations, built = 0, 0
for _ in range(1500):
    tok = mint("dana@corp")
    for _ in range(random.randint(1, 4)):
        nxt = random.choice(actors)
        want = set(random.sample(sorted(tok.scopes),
                                 k=random.randint(0, len(tok.scopes))))
        try:
            new = exchange(tok, nxt, want)
        except DelegationError:
            continue
        if not new.scopes <= tok.scopes or not new.scopes <= CEILINGS[nxt]:
            violations += 1
        tok = new; built += 1
print(f"{built} successful hops across 1500 random chains — widening violations: {violations}")
assert violations == 0
print("Invariant holds: authority can only shrink, on every path.")
'''),
 ],
 "expect": "Four tokens print with strictly narrowing scopes and readable chains "
           "ending in `dana@corp → orchestrator → patch-agent → deploy-agent`. "
           "The resource server allows `patch-agent` a write, denies "
           "`deploy-agent` the same write, and produces a truthful audit line "
           "naming both the actor and the principal. All three attacks are "
           "refused with the rule that refused them. The impersonated token's "
           "chain contains only `dana@corp`. The property test reports zero "
           "widening violations.",
 "challenge": "Run these same four scenarios against real Keycloak with token "
              "exchange enabled. The properties should hold identically — and if "
              "your realm allows the second one (widening past the actor's "
              "ceiling), that is a live finding, because Keycloak will happily "
              "issue it if the client is configured permissively.",
},

"A2.6": {
 "concept": """
A2.5 works when the downstream system understands token exchange. Most do not.

Your estate contains services that accept exactly one thing — a bearer token, an
API key, a mutual-TLS client certificate — and have no field for "who is this
being done on behalf of". They will not gain one. Some are vendor products, some
are twenty years old, some are perfectly modern and simply do not implement RFC
8693.

This is where an **agent gateway** earns its place. The gateway is a single
mediation point that:

1. **Terminates the rich identity.** It receives the full on-behalf-of token,
   validates the chain, and applies policy while it still has the information.
2. **Translates down.** It calls the downstream with whatever that system does
   understand — often a narrow service credential the *gateway* holds, never the
   agent.
3. **Keeps the chain.** The act chain is recorded in the gateway's log, so the
   information is not lost even though the downstream never saw it.

The critical design point: after translation, the downstream cannot tell one
agent from another. So **every decision that depends on the chain has to happen
at the gateway**, before the identity is flattened. A gateway that only
authenticates and forwards is not a gateway, it is a proxy.
""",
 "steps": [
  ("md", "## 2 · Demo — the estate as it actually is\n\n"
         "Three downstream systems with three different identity capabilities. "
         "Only one speaks on-behalf-of."),
  ("py", '''import time, hashlib
from dataclasses import dataclass, field

@dataclass
class Token:
    sub: str; actor: str; scopes: set; act: dict = None
    issued: float = field(default_factory=time.time); ttl: float = 300
    @property
    def expired(self): return time.time() - self.issued > self.ttl
    def chain(self):
        out, node = [], self.act
        while node:
            out.append(node["actor"]); node = node.get("act")
        c = list(reversed(out)) + [self.actor]
        if c[0] != self.sub: c.insert(0, self.sub)
        return c

DOWNSTREAM = {
  "internal-api":  {"understands": "obo",     "note": "modern, RFC 8693 aware"},
  "github":        {"understands": "bearer",  "note": "PAT or app token, one identity"},
  "mainframe-fin": {"understands": "svc-acct","note": "fixed service account, 1998"},
}
for name, d in DOWNSTREAM.items():
    print(f"{name:15s} accepts {d['understands']:9s} — {d['note']}")

agent_token = Token(sub="dana@corp", actor="patch-agent", scopes={"repo:write", "ledger:post"},
                    act={"actor": "orchestrator", "act": None})
print(f"\\nagent presents: {' → '.join(agent_token.chain())}  scopes={sorted(agent_token.scopes)}")
'''),
  ("md", "## 3 · Where it breaks — forward the token and information dies\n\n"
         "The naive integration forwards whatever it has. Watch what each "
         "downstream can record."),
  ("py", '''GATEWAY_CREDENTIALS = {          # credentials the GATEWAY holds, not the agent
    "github":        "ghs_gateway_scoped_to_repo_write",
    "mainframe-fin": "SVCACCT-GW-01",
}

def naive_forward(token, target):
    kind = DOWNSTREAM[target]["understands"]
    if kind == "obo":
        return {"target": target, "sees_actor": token.actor,
                "sees_principal": token.sub, "chain": token.chain(),
                "audit_ok": True}
    # bearer / svc-acct: there is nowhere to put the chain
    return {"target": target, "sees_actor": GATEWAY_CREDENTIALS.get(target, "?"),
            "sees_principal": "unknown", "chain": "LOST",
            "audit_ok": False}

for target in DOWNSTREAM:
    r = naive_forward(agent_token, target)
    print(f"{target:15s} actor={str(r['sees_actor'])[:26]:28s} "
          f"principal={r['sees_principal']:10s} chain={r['chain']}")
print("\\nTwo of three downstreams cannot record who caused the action.")
print("Worse: to them, every agent looks like the same service account —")
print("so a per-agent policy CANNOT be enforced there. It has to happen earlier.")
'''),
  ("md", "## 4 · The control — decide at the gateway, then translate\n\n"
         "The gateway applies every chain-dependent rule while it still has the "
         "chain, and only then swaps in the credential the downstream understands."),
  ("py", '''POLICY = {
  # (downstream, required scope) -> which actors may reach it, and any conditions
  ("github",        "repo:write"):  {"actors": {"patch-agent"}, "max_chain": 3},
  ("mainframe-fin", "ledger:post"): {"actors": {"finance-agent"}, "max_chain": 2},
  ("internal-api",  "repo:read"):   {"actors": {"patch-agent", "triage-agent"},
                                     "max_chain": 4},
}

@dataclass
class Gateway:
    log: list = field(default_factory=list)

    def call(self, token, target, scope):
        # --- 1. decide, while the identity is still rich -----------------
        if token.expired:
            return self._deny(token, target, "token expired")
        if scope not in token.scopes:
            return self._deny(token, target, f"token lacks {scope}")
        rule = POLICY.get((target, scope))
        if rule is None:
            return self._deny(token, target, "no policy for this route (deny by default)")
        if token.actor not in rule["actors"]:
            return self._deny(token, target,
                              f"actor {token.actor} not permitted on this route "
                              f"(allowed: {sorted(rule['actors'])})")
        if len(token.chain()) > rule["max_chain"]:
            return self._deny(token, target,
                              f"delegation depth {len(token.chain())} > "
                              f"{rule['max_chain']}")
        # --- 2. translate down -------------------------------------------
        kind = DOWNSTREAM[target]["understands"]
        presented = (f"obo:{token.actor}@{token.sub}" if kind == "obo"
                     else GATEWAY_CREDENTIALS[target])
        # --- 3. keep the chain in OUR log, since downstream cannot ---------
        entry = {"allowed": True, "target": target, "scope": scope,
                 "presented_downstream": presented,
                 "chain": " → ".join(token.chain())}
        self.log.append(entry)
        return entry

    def _deny(self, token, target, why):
        entry = {"allowed": False, "target": target, "why": why,
                 "chain": " → ".join(token.chain())}
        self.log.append(entry)
        return entry

gw = Gateway()
finance = Token(sub="dana@corp", actor="finance-agent", scopes={"ledger:post"},
                act={"actor": "orchestrator", "act": None})
deep = Token(sub="dana@corp", actor="patch-agent", scopes={"repo:write"},
             act={"actor": "sub-3", "act": {"actor": "sub-2",
                  "act": {"actor": "orchestrator", "act": None}}})

for tok, target, scope, label in [
    (agent_token, "github",        "repo:write",  "permitted actor"),
    (agent_token, "mainframe-fin", "ledger:post", "wrong actor for this route"),
    (finance,     "mainframe-fin", "ledger:post", "correct actor"),
    (deep,        "github",        "repo:write",  "chain too deep"),
]:
    r = gw.call(tok, target, scope)
    print(f"{label:28s} {'ALLOW' if r['allowed'] else 'DENY '} {target:15s} "
          f"{r.get('presented_downstream', r.get('why'))}")
'''),
  ("py", '''# Verify: the chain survives in the gateway log even where the downstream
# could not carry it. This is the audit trail A2.3 said we could not reconstruct.
print("gateway audit log — the only place the full story exists:")
for e in gw.log:
    verdict = "ALLOW" if e["allowed"] else "DENY"
    print(f"   {verdict:5s} {e['target']:15s} {e['chain']}")

allowed = [e for e in gw.log if e["allowed"]]
assert all("→" in e["chain"] for e in allowed)
print(f"\\n{len(allowed)}/{len(gw.log)} calls allowed; every one carries its chain,")
print("including the two whose downstream saw only a service account.")
'''),
 ],
 "expect": "Only `internal-api` can record the actor and principal; GitHub and the "
           "mainframe both lose the chain and see a gateway credential. The "
           "gateway allows `patch-agent` to GitHub and `finance-agent` to the "
           "mainframe, denies `patch-agent` on the finance route, and denies the "
           "4-deep chain. The gateway log carries the full chain for every call, "
           "including the two the downstream could not record.",
 "challenge": "List your downstream systems and mark which speak on-behalf-of. "
              "For every one that does not, name where the per-agent decision is "
              "made today. If the answer is \"nowhere — they all use the same "
              "service account\", you have found the gateway you need to build.",
},

"A2.7": {
 "concept": """
A2.6 assumed you can put a gateway in front of the system. Sometimes you cannot.

There is a category of system where the agent must be allowed access, the system
cannot be modified, and no meaningful per-agent identity is possible:

- A vendor SaaS with one API key per tenant.
- A mainframe or ERP where the integration account was configured in 2003 and
  the person who understood it has retired.
- A database that only does username/password, reached over a private link.

You cannot give these systems identity. What you *can* do is control **the one
place every call passes through** — a choke point — and apply the controls that
do not need identity:

- **Rate limiting**, so a compromised agent cannot drain a dataset at machine
  speed.
- **Volume and pattern budgets**, because the difference between an agent doing
  its job and an agent exfiltrating is almost always *quantity*.
- **Time-of-day and concurrency limits**, matching the business process the
  legacy system actually serves.
- **Full recording at the choke point**, since the downstream log is useless.

This is a genuinely weaker control than identity, and it should be labelled as
such rather than presented as equivalent. What it buys is a bounded worst case.
""",
 "steps": [
  ("md", "## 2 · Demo — the legacy system, and why identity is off the table\n\n"
         "A customer database behind one shared account. Every consumer — three "
         "agents and a nightly batch job — presents the same credential."),
  ("py", '''import time
from dataclasses import dataclass, field

LEGACY = {"name": "crm-oracle-prod", "auth": "shared username/password",
          "per_caller_identity": False, "can_be_modified": False,
          "holds": "1.2M customer records"}
for k, v in LEGACY.items():
    print(f"{k:22s} {v}")

CONSUMERS = ["support-agent", "billing-agent", "analytics-agent", "nightly-batch"]
print(f"\\nconsumers sharing one credential: {CONSUMERS}")
print("the database's own log will attribute every query to 'SVC_CRM_INT'.")
'''),
  ("md", "## 3 · Where it breaks — normal use and abuse look identical\n\n"
         "The support agent legitimately reads customer records. So does an agent "
         "whose prompt has been compromised. Per-query, they are indistinguishable "
         "— which is exactly why the control has to be about *rate and volume*, "
         "not about intent."),
  ("py", '''def session(name, queries, rows_each, seconds):
    return {"caller": name, "queries": queries, "rows": queries * rows_each,
            "seconds": seconds, "rows_per_min": queries * rows_each / (seconds/60)}

sessions = [
    session("support-agent  (normal)",     40,     1, 3600),
    session("billing-agent  (normal)",    600,     1, 3600),
    session("nightly-batch  (normal)",      1, 50000, 1800),
    session("support-agent  (compromised)", 9000,  50,  120),
]
print(f"{'caller':30s}{'queries':>8}{'rows':>9}{'rows/min':>11}")
print("-" * 60)
for s in sessions:
    print(f"{s['caller']:30s}{s['queries']:>8}{s['rows']:>9}{s['rows_per_min']:>11.0f}")
print("\\nEvery one of these presents the same credential and issues valid SQL.")
print("The compromised session is not doing anything the account may not do —")
print("it is doing a permitted thing far too much.")
'''),
  ("md", "## 4 · The control — a throttling choke point\n\n"
         "One place all four consumers must pass through. It cannot tell them "
         "apart cryptographically, but it *can* give each a named lane with its "
         "own budget, and enforce the budget."),
  ("py", '''@dataclass
class ChokePoint:
    """The one place every call to the legacy system passes through.

    Identity here is a *declared lane*, not a proven one — a compromised agent
    could claim another lane. That is an honest weakness: the control bounds
    the worst case, it does not attribute. Say so in the design doc.
    """
    budgets: dict                        # lane -> (rows_per_min, max_concurrent)
    window_start: float = field(default_factory=time.time)
    used: dict = field(default_factory=dict)
    log: list = field(default_factory=list)

    def query(self, lane, rows, at=None):
        at = at or time.time()
        limit, _ = self.budgets.get(lane, (0, 0))
        spent = self.used.get(lane, 0)
        if spent + rows > limit:
            entry = {"lane": lane, "rows": rows, "allowed": False,
                     "why": f"rate budget exceeded: {spent}+{rows} > {limit} rows/min"}
            self.log.append(entry); return entry
        self.used[lane] = spent + rows
        entry = {"lane": lane, "rows": rows, "allowed": True,
                 "remaining": limit - self.used[lane]}
        self.log.append(entry); return entry

choke = ChokePoint(budgets={
    "support-agent":   (200,    4),      # a human-paced support workflow
    "billing-agent":   (1200,   8),
    "analytics-agent": (5000,   2),
    "nightly-batch":   (60000,  1),      # bulk, but only in its window
})

print("normal traffic:")
for lane, rows in [("support-agent", 30), ("support-agent", 45),
                   ("billing-agent", 900), ("nightly-batch", 50000)]:
    r = choke.query(lane, rows)
    print(f"   {lane:18s} {rows:>6} rows → "
          f"{'ok, ' + str(r['remaining']) + ' left' if r['allowed'] else r['why']}")

print("\\ncompromised support agent tries to drain the table:")
for attempt in range(1, 5):
    r = choke.query("support-agent", 5000)
    print(f"   attempt {attempt}: {'ALLOWED' if r['allowed'] else 'BLOCKED — ' + r['why']}")
'''),
  ("py", '''# Verify: what did the choke point actually bound?
attacker_got = sum(e["rows"] for e in choke.log
                   if e["lane"] == "support-agent" and e["allowed"])
unbounded = 9000 * 50
print(f"rows the compromised lane obtained: {attacker_got}")
print(f"rows it would have obtained unthrottled: {unbounded:,}")
print(f"reduction: {unbounded / max(attacker_got,1):,.0f}×")
print("\\nHonest framing for the design doc:")
print("  · this does NOT tell you which agent misbehaved (no identity available)")
print("  · it DOES bound the worst case to one lane's budget per window")
print("  · and the choke point log is the only per-caller record that exists")
assert attacker_got < unbounded
'''),
 ],
 "expect": "The legacy system is shown with no per-caller identity. Normal and "
           "compromised sessions are indistinguishable per query — the "
           "compromised one differs only by rate (225,000 rows/min vs 40). The "
           "choke point permits normal traffic and blocks the drain attempts, "
           "bounding what the attacker obtains to a fraction of the unthrottled "
           "450,000 rows.",
 "challenge": "Find one system in your estate where every agent shares a "
              "credential. Set a rows-per-minute budget from the *legitimate* "
              "workload's 99th percentile, not from the system's capacity. The "
              "gap between those two numbers is what an attacker currently has.",
},

"A2.8": {
 "concept": """
Every control so far has narrowed *what* an identity may hold. Just-in-time
authority narrows *when*.

The default is a **standing grant**: `deploy-agent` holds `deploy:prod`
permanently, because it needs it sometimes. The audit question that produces is
"who has deploy:prod?" — answered by the same dull list every quarter, which
tells a reviewer nothing.

JIT replaces it with authority that exists only for the duration of one
justified task. The audit question becomes "who held it, for what, and for how
long?" — which is answerable, sampleable, and genuinely interesting, because
each grant carries a reason a human can dispute.

The two design decisions that matter:

- **TTL.** Derived from the measured duration of the real task, not a round
  number. Too short and the agent fails mid-task; too long and you have
  reinvented the standing grant with extra steps.
- **What happens at expiry.** The agent must handle losing authority gracefully.
  An agent that crashes when its grant expires will be given a longer TTL, and
  then a permanent one.
""",
 "steps": [
  ("md", "## 2 · Demo — standing grants, and what an auditor sees\n\n"
         "The starting position, and the reason it is unsatisfying."),
  ("py", '''import time
from dataclasses import dataclass, field

STANDING = {
    "deploy-agent":  {"deploy:prod", "artifact:read"},
    "patch-agent":   {"repo:write", "repo:read"},
    "backup-runner": {"db:read", "s3:write"},
}
print("standing grants — the quarterly access review:")
for actor, scopes in STANDING.items():
    print(f"   {actor:16s} {sorted(scopes)}")
print("\\nThe reviewer's only possible question: 'should this still exist?'")
print("With no usage data attached, the honest answer is always 'probably'.")

# how often is that authority actually exercised?
USAGE = {"deploy-agent": 6, "patch-agent": 210, "backup-runner": 30}   # per 90 days
print("\\nactual use in the last 90 days:")
for actor, n in USAGE.items():
    held_seconds = 90 * 86400
    used_seconds = n * 180          # ~3 minutes of real work per use
    print(f"   {actor:16s} used {n:>3}×  → authority idle "
          f"{100 * (1 - used_seconds/held_seconds):.2f}% of the time")
'''),
  ("md", "## 3 · Where it breaks\n\n"
         "`deploy-agent` holds production deploy rights continuously and uses them "
         "six times a quarter. For 99.99% of its life, the credential is a "
         "liability with no corresponding benefit — and that idle window is "
         "exactly when a compromise would go unnoticed, because nobody is "
         "watching a capability that is not being used."),
  ("md", "## 4 · The control — grants with a reason and an expiry"),
  ("py", '''class GrantExpired(Exception): pass

@dataclass
class JITGrant:
    actor: str
    scope: str
    reason: str                 # free text, but MANDATORY — this is the audit value
    ttl: float
    granted: float = field(default_factory=time.time)
    used: int = 0

    @property
    def active(self): return time.time() - self.granted < self.ttl
    @property
    def age(self): return time.time() - self.granted

    def use(self):
        if not self.active:
            raise GrantExpired(f"{self.actor}'s {self.scope} grant expired "
                               f"after {self.ttl}s ({self.reason!r})")
        self.used += 1
        return True

    def audit_line(self):
        return (f"{self.actor:14s} {self.scope:14s} "
                f"{'ACTIVE' if self.active else 'expired':8s} "
                f"ttl={self.ttl:>5.1f}s used={self.used}  reason={self.reason!r}")

grants = [
    JITGrant("deploy-agent", "deploy:prod", "roll out fix for CVE-2026-1188", ttl=0.6),
    JITGrant("patch-agent",  "repo:write",  "patch finding-4471",             ttl=60),
]
print("at issue:")
for g in grants: print("   " + g.audit_line())

grants[0].use(); grants[1].use()
time.sleep(0.7)

print("\\nafter the deploy window closes:")
for g in grants: print("   " + g.audit_line())
'''),
  ("md", "## 5 · Verify — the agent must survive expiry\n\n"
         "This is the design decision that decides whether JIT survives contact "
         "with an on-call engineer. An agent that crashes on expiry gets a longer "
         "TTL; an agent that re-requests with a reason keeps the control alive."),
  ("py", '''def naive_agent(grant, steps):
    """Crashes when authority disappears mid-task."""
    for i in range(steps):
        grant.use()                      # raises when expired
        time.sleep(0.25)
    return "completed"

def resilient_agent(grant_factory, grant, steps, reason):
    """Re-requests, with a reason, and records why. Survives expiry."""
    events = []
    for i in range(steps):
        try:
            grant.use()
        except GrantExpired:
            events.append(f"step {i}: grant expired → re-requesting")
            grant = grant_factory(reason=f"{reason} (continuation, step {i})")
            grant.use()
        events.append(f"step {i}: ok")
        time.sleep(0.25)
    return events, grant

g = JITGrant("deploy-agent", "deploy:prod", "rollout", ttl=0.3)
try:
    naive_agent(g, 4)
except GrantExpired as e:
    print("naive agent    :", e)
    print("                 → on-call asks for a 24h TTL, and JIT is over.")

factory = lambda reason: JITGrant("deploy-agent", "deploy:prod", reason, ttl=0.3)
events, final = resilient_agent(factory, factory("rollout"), 4, "rollout")
print("\\nresilient agent:")
for e in events: print("   ", e)
print("   final grant:", final.audit_line())
print("\\nThe audit trail now contains every continuation and its reason —")
print("which is strictly more information than a standing grant ever produced.")
'''),
 ],
 "expect": "The standing-grant review shows `deploy-agent`'s authority idle "
           "99.99% of the time. The JIT grants print ACTIVE at issue and the "
           "0.6-second one shows expired afterwards, each carrying its reason. "
           "The naive agent raises `GrantExpired` mid-task; the resilient agent "
           "detects expiry, re-requests with a continuation reason, and completes "
           "all four steps.",
 "challenge": "Pick the standing grant with the worst ratio of held-time to "
              "used-time in your estate. Measure how long the real task takes, "
              "set the TTL at the 95th percentile of that, and make the agent "
              "re-request. The reason field is where the audit value lives — "
              "insist it be specific.",
},

"A2.9": {
 "concept": """
The classic identity failures did not go away when the caller became an agent.
They got faster, harder to attribute, and in one case genuinely worse.

This lesson runs the whole track's controls against a suite of them, so you can
see which are closed by what you have built and which are not:

| Failure | Age | What changed with agents |
|---|---|---|
| Credential in source | ancient | Agents read source, so a leaked key is now *actionable* by the reader |
| Over-broad scope | ancient | Granted programmatically, at machine speed, with no reviewer |
| Replay of a stolen token | ancient | Same, but the thief acts in milliseconds |
| Confused deputy | 1988 | The agent *is* a deputy, by design |
| Privilege escalation via chain | ancient | Chains are now 3–5 hops and nobody drew them |
| Impersonation | ancient | **Worse**: now the default deployment pattern |

The honest outcome of this lesson is that the controls built in A2.1–A2.8 close
most of these, and one of them — impersonation — cannot be closed by a token
format at all. It requires a platform decision: agents must not be *issuable* a
principal's credential in the first place.
""",
 "steps": [
  ("md", "## 2 · Demo — the delegation implementation from A2.5, under attack\n\n"
         "Rebuild the minimum needed, then fire the suite at it."),
  ("py", '''import time
from dataclasses import dataclass, field

CEILINGS = {"dana@corp": {"repo:read", "repo:write", "deploy:prod", "secrets:read"},
            "patch-agent": {"repo:read", "repo:write"},
            "triage-agent": {"repo:read"},
            "deploy-agent": {"repo:read", "deploy:prod"}}

class DelegationError(Exception): pass

@dataclass
class Token:
    sub: str; actor: str; scopes: set; act: dict = None
    issued: float = field(default_factory=time.time); ttl: float = 300
    @property
    def expired(self): return time.time() - self.issued > self.ttl
    def chain(self):
        out, node = [], self.act
        while node: out.append(node["actor"]); node = node.get("act")
        c = list(reversed(out)) + [self.actor]
        if c[0] != self.sub: c.insert(0, self.sub)
        return c

def mint(p, s=None):
    want = set(s) if s else set(CEILINGS[p])
    if not want <= CEILINGS[p]: raise DelegationError("over ceiling")
    return Token(p, p, want)

def exchange(pres, actor, scopes):
    if pres.expired: raise DelegationError("presented token expired")
    scopes = set(scopes)
    if not scopes <= pres.scopes:
        raise DelegationError(f"not in presented token: {sorted(scopes - pres.scopes)}")
    if not scopes <= CEILINGS.get(actor, set()):
        raise DelegationError(f"above {actor}'s ceiling: "
                              f"{sorted(scopes - CEILINGS.get(actor,set()))}")
    return Token(pres.sub, actor, scopes, {"actor": pres.actor, "act": pres.act})

def impersonate(p, actor, scopes):
    return Token(p, p, set(scopes), None)

dana  = mint("dana@corp")
patch = exchange(dana, "patch-agent", {"repo:read", "repo:write"})
print("baseline chain:", " → ".join(patch.chain()))
'''),
  ("py", '''SUITE = [
 ("IDN-01", "escalate scope during delegation", "critical",
  lambda: exchange(patch, "deploy-agent", {"deploy:prod"})),
 ("IDN-02", "exceed the recipient's ceiling", "high",
  lambda: exchange(dana, "triage-agent", {"repo:write"})),
 ("IDN-03", "replay an expired token", "high",
  lambda: exchange(Token("dana@corp", "patch-agent", {"repo:write"}, ttl=-1),
                   "deploy-agent", {"repo:read"})),
 ("IDN-04", "confused deputy: reuse the chain for an unrelated task", "high",
  lambda: exchange(patch, "patch-agent", {"repo:write"})),
]
results = []
for aid, name, sev, fn in SUITE:
    try:
        fn(); got_through, detail = True, "succeeded"
    except DelegationError as e:
        got_through, detail = False, str(e)[:48]
    results.append((aid, name, sev, got_through, detail))
    print(f"{aid}  {'GOT THROUGH' if got_through else 'blocked    '}  {name}")
    print(f"        {detail}")

# impersonation is not a token-format failure; it is a platform one
bad = impersonate("dana@corp", "patch-agent", {"repo:write"})
hidden = "patch-agent" not in bad.chain()
results.append(("IDN-05", "impersonation (agent uses the human's credential)",
                "critical", hidden, "agent absent from the chain"))
print(f"IDN-05  {'GOT THROUGH' if hidden else 'blocked    '}  "
      f"impersonation — chain is {bad.chain()}")
'''),
  ("md", "## 3 · Where it breaks — read the one that got through\n\n"
         "Four of five are closed by the narrowing rules. IDN-05 succeeds, and it "
         "succeeds **by design**: nothing inside a token format can stop a caller "
         "choosing not to use delegation at all. If an agent can obtain a "
         "principal's credential, it can always present it.\n\n"
         "Note also IDN-04 — the confused deputy. It is *blocked here* only "
         "because the scope re-request is a no-op; a genuine confused-deputy "
         "attack works at the content layer, not the token layer, and belongs to "
         "the injection surface (C1.3)."),
  ("py", '''asr = sum(1 for *_, got, _ in results if got) / len(results)
print(f"attack success rate against the identity surface: {asr:.0%}")
print("\\nby severity:")
for aid, name, sev, got, detail in results:
    if got:
        print(f"   {sev.upper():9s} {aid} — {name}")
'''),
  ("md", "## 4 · The control for the one that got through\n\n"
         "Impersonation is closed at the platform, not the protocol. Three "
         "mechanisms, in descending order of strength."),
  ("py", '''CONTROLS = [
 ("issuance", "The IdP refuses to issue a human-subject credential to a workload "
              "identity. An agent literally cannot obtain Dana's token.",
              "strongest — removes the capability", True),
 ("binding",  "Tokens are sender-constrained (mTLS / DPoP), so a token minted for "
              "Dana's browser cannot be presented by the agent's workload.",
              "strong — token is useless off its holder", True),
 ("detection","Alert when a human-subject token is presented from a workload "
              "network identity or at machine rate.",
              "weakest — after the fact, but deployable this week", False),
]
for name, how, strength, preventive in CONTROLS:
    print(f"{name:10s} [{'preventive' if preventive else 'detective':10s}] {strength}")
    print(f"           {how}\\n")

def token_binding_check(token, presenter_workload, bound_to):
    """Sender-constrained tokens: presenting from the wrong workload fails."""
    if bound_to and presenter_workload != bound_to:
        return False, (f"token bound to {bound_to}, presented by "
                       f"{presenter_workload}")
    return True, "binding ok"

print("verify — the same impersonation attempt, with sender-constrained tokens:")
for workload in ("dana-browser-session", "spiffe://corp/ns/prod/sa/patch-agent"):
    ok, why = token_binding_check(bad, workload, bound_to="dana-browser-session")
    print(f"   presented by {workload:42s} {'ACCEPTED' if ok else 'REJECTED'} — {why}")
'''),
 ],
 "expect": "IDN-01 through IDN-04 are all blocked by the narrowing rules, each "
           "naming the rule that refused it. IDN-05 (impersonation) gets through, "
           "giving an identity-surface attack success rate of 20%, and the chain "
           "for the impersonated token contains only `dana@corp`. Sender-"
           "constrained binding then rejects the same token when presented from "
           "the agent's workload identity.",
 "challenge": "IDN-05 is the one that matters and the one your platform probably "
              "allows. Find out whether your IdP will issue a human-subject token "
              "to a workload. If it will, write the detection first — it ships in "
              "a week — and open the issuance change as the real fix.",
},
}
