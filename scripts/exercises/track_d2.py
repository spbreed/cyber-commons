"""D2 — The Incident Responder. Eight sessions.

Three things change when the actor is an agent, and each has a lesson:

    scope is a graph, not a host        — it follows the delegation chain
    containment must beat the loop      — a human in the path arrives too late
    attribution is a design property    — you cannot recover it afterwards

    D2.1  agent-assisted reconstruction
    D2.2  when the actor is an agent
    D2.3  scoping an agentic incident
    D2.4  containment at machine speed
    D2.5  replay and forensics
    D2.6  the post-incident change surface
    D2.7  stop authority
    D2.8  the regulatory clock
"""

from .skills import SKILL_RUNTIME

EXERCISES: dict[str, dict] = {

"D2.1": {
 "concept": """
Reconstruction is the first phase of any incident: build the timeline, establish
what happened, decide what to contain.

An agent makes this faster and more dangerous at the same time. Faster, because
a model can correlate thousands of log lines in seconds. More dangerous, because
it will produce a fluent, confident narrative from logs that were never
sufficient to support one — and a fluent narrative is much harder to challenge
than an obviously incomplete one.

So the discipline is to separate two questions that feel like one:

1. **What do the logs say?**
2. **What can the logs support?**

The gap between them is where reconstruction goes wrong, and it is the responder's
job to state that gap explicitly in the incident record.
""",
 "steps": [
  ("md", "## 2 · Demo — a timeline that reads perfectly"),
  ("py", '''import time
from dataclasses import dataclass, field

@dataclass
class LogLine:
    ts: float
    logged_actor: str     # what the audit log records
    real_actor: str       # what actually happened (held out from the responder)
    action: str
    target: str = ""

def render(lines, truth=False):
    base = min(l.ts for l in lines)
    rows = [f"{'t+s':>6}  {'actor':16s}{'action':16s}target"]
    for l in sorted(lines, key=lambda x: x.ts):
        who = l.real_actor if truth else l.logged_actor
        rows.append(f"{l.ts-base:>6.0f}  {who:16s}{l.action:16s}{l.target}")
    return "\\n".join(rows)

t0 = time.time()
INCIDENT = [
 LogLine(t0,      "dana@corp", "dana@corp",   "login",       "sso"),
 LogLine(t0+22,   "dana@corp", "dana@corp",   "open_ticket", "SEC-4471"),
 LogLine(t0+40,   "dana@corp", "patch-agent", "read_file",   "/work/repo/billing.py"),
 LogLine(t0+41,   "dana@corp", "patch-agent", "read_file",   "/home/app/.aws/credentials"),
 LogLine(t0+43,   "dana@corp", "patch-agent", "http_post",   "collect.example.com"),
 LogLine(t0+180,  "dana@corp", "dana@corp",   "logout",      "sso"),
]
print("WHAT THE RESPONDER SEES")
print(render(INCIDENT))
'''),
  ("md", "## 3 · Where it breaks — the confident wrong narrative"),
  ("py", '''NARRATIVE = """
At 14:02 dana@corp authenticated via SSO and opened ticket SEC-4471. Eighteen
seconds later the same account read billing.py, then read the application's AWS
credentials, and posted to an external host. The account then remained active
for a further two minutes before logging out.

Assessment: credential theft by an authenticated insider. Recommend immediate
suspension of dana@corp pending investigation.
"""
print("A MODEL'S RECONSTRUCTION (fluent, supported by every log line):")
print(NARRATIVE)

print("WHAT ACTUALLY HAPPENED")
print(render(INCIDENT, truth=True))
'''),
  ("py", '''def reconstruct(lines):
    logged = {l.logged_actor for l in lines}
    real   = {l.real_actor for l in lines}
    wrong  = [l for l in lines if l.logged_actor != l.real_actor]
    return {"actors_in_logs": sorted(logged),
            "actors_in_reality": sorted(real),
            "misattributed_lines": len(wrong),
            "hidden_actors": sorted(real - logged),
            "attribution": "sound" if not wrong else "BROKEN",
            "consequence": ("none" if not wrong else
                            f"containment aimed at {sorted(logged)} leaves "
                            f"{sorted(real - logged)} running")}

r = reconstruct(INCIDENT)
for k, v in r.items(): print(f"{k:22s}{v}")
print("\\nEvery sentence in that narrative is supported by the logs.")
print("The conclusion is wrong, and the recommended action does nothing.")
'''),
  ("md", "## 4 · The control — state what the evidence can support\n\n"
         "The fix is not a better model. It is a reconstruction step that reports "
         "its own evidentiary limits before it reports a conclusion."),
  ("py", '''def evidence_check(lines, has_acting_identity_field, has_act_chain):
    limits = []
    if not has_acting_identity_field:
        limits.append("no acting-identity field: every line attributes to the "
                      "principal, so agent actions are indistinguishable from human ones")
    if not has_act_chain:
        limits.append("no delegation chain: cannot establish who caused the task")
    rates = {}
    for l in lines:
        rates.setdefault(l.logged_actor, []).append(l.ts)
    for actor, ts in rates.items():
        if len(ts) > 2:
            span = max(ts) - min(ts)
            per_min = len(ts) / max(span/60, 1e-9)
            if per_min > 30:
                limits.append(f"{actor} shows {per_min:.0f} actions/min — "
                              f"not human-paced; an agent is likely present")
    return limits

limits = evidence_check(INCIDENT, has_acting_identity_field=False, has_act_chain=False)
print("EVIDENTIARY LIMITS (must appear before any conclusion):")
for l in limits: print(f"   ⚠ {l}")

SAFE = f"""
Timeline: dana@corp authenticated, opened SEC-4471; the account then read
billing.py, read AWS credentials, and posted externally.

LIMITS OF THIS RECONSTRUCTION
{chr(10).join('  - ' + l for l in limits)}

Assessment: an actor holding dana@corp's credential performed the reads and the
POST. The logs CANNOT establish whether that actor was the human or an agent
operating with her token. Containment must therefore address both.
"""
print(SAFE)
assert limits
'''),
 ],
 "expect": "The timeline attributes every action to `dana@corp`. The fluent "
           "narrative recommends suspending her. The truth view shows "
           "`patch-agent` performed the credential read and the external POST; "
           "reconstruction reports BROKEN attribution with 3 misattributed lines. "
           "The evidence check flags the missing acting-identity field, the "
           "missing chain, and a non-human action rate.",
 "challenge": "Take a real incident timeline from your own history and ask what "
              "it would look like if an agent had been operating on the user's "
              "credential. If you cannot tell from the logs, your reconstructions "
              "already carry this risk.",
},

"D2.2": {
 "concept": """
Three responder instincts are correct for human incidents and misfire when the
actor is an agent.

1. **Disable the account.** For a human this stops them. For an agent holding an
   already-issued bearer token, it may not — the token remains valid until it
   expires.
2. **Interview the user.** They were asleep. They authorised a task; a model
   chose the actions. They cannot tell you what happened.
3. **Assume one actor.** There were three, in a chain, and only the last one
   touched the resource.

The correct first action is to **revoke the agent identity**, which is only
possible if A2 was done. This lesson is where the identity track's value becomes
operational rather than architectural.
""",
 "steps": [
  ("md", "## 2 · Demo — the three instincts, tested"),
  ("py", '''import time
from dataclasses import dataclass, field

@dataclass
class Session:
    actor: str; token_issued: float; token_ttl: float; account_enabled: bool = True
    identity_revoked: bool = False
    def can_act(self, at):
        if self.identity_revoked: return False, "identity revoked"
        if at - self.token_issued > self.token_ttl: return False, "token expired"
        if not self.account_enabled:
            return True, "account disabled, but the issued token is still valid"
        return True, "active"

now = time.time()
SESSIONS = {
 "dana@corp (human)":  Session("dana@corp", now-60, 3600),
 "patch-agent":        Session("patch-agent", now-60, 3600),
 "deploy-agent":       Session("deploy-agent", now-60, 3600),
}
print("INSTINCT 1 — disable dana@corp's account")
for s in SESSIONS.values(): s.account_enabled = (s.actor != "dana@corp")
for name, s in SESSIONS.items():
    ok, why = s.can_act(now)
    print(f"   {name:22s} can act: {str(ok):5s}  {why}")
print("   → the agents were never using her account interactively; they hold")
print("     their own issued tokens, and one of them is acting AS her.")
'''),
  ("py", '''print("\\nINSTINCT 2 — interview the user")
INTERVIEW = {
 "did you read the AWS credentials?":       "No. I opened a ticket and went to lunch.",
 "what did you ask the agent to do?":       "Fix the finding in billing.py.",
 "did you approve the external POST?":      "I didn't know it made external calls.",
}
for q, a in INTERVIEW.items():
    print(f"   Q: {q}\\n   A: {a}")
print("   → she authorised a TASK. The actions were chosen by a model. She is")
print("     not withholding information; she does not have it.")

print("\\nINSTINCT 3 — assume one actor")
CHAIN = ["dana@corp", "orchestrator", "patch-agent"]
print(f"   actual chain: {' → '.join(CHAIN)}")
print(f"   actors involved: {len(CHAIN)}; actors in the logs: 1")
'''),
  ("md", "## 4 · The control — revoke the agent identity first"),
  ("py", '''class Registry:
    def __init__(self):
        self.revoked = set()
    def revoke(self, actor):
        self.revoked.add(actor); return actor
    def valid(self, session):
        return session.actor not in self.revoked

reg = Registry()
for s in SESSIONS.values(): s.account_enabled = True   # undo instinct 1

print("correct first action — revoke patch-agent's identity:")
reg.revoke("patch-agent")
SESSIONS["patch-agent"].identity_revoked = True
for name, s in SESSIONS.items():
    ok, why = s.can_act(now)
    print(f"   {name:22s} can act: {str(ok):5s}  {why}")
print("\\n   dana keeps working. deploy-agent keeps working. The actor stopped.")

print("\\nTIME TO EFFECT, measured:")
LEVERS = {"disable the human's account": (5,  "agent unaffected"),
          "kill the agent process":      (2,  "supervisor restarts it; token still valid"),
          "revoke the agent identity":   (12, "agent cannot act, even after restart"),
          "rotate the shared credential":(420,"works, and breaks every other consumer")}
for lever, (secs, note) in LEVERS.items():
    print(f"   {lever:32s}{secs:>5}s  {note}")
assert not SESSIONS["patch-agent"].can_act(now)[0]
assert SESSIONS["deploy-agent"].can_act(now)[0]
'''),
  ("py", '''# Verify: the runbook, rewritten.
OLD = ["1. disable the user account",
       "2. interview the user",
       "3. review the user's recent activity"]
NEW = ["1. identify the ACTING identity from the act chain (A2.5)",
       "2. revoke that identity — no approval needed for a non-human (A3.6)",
       "3. scope by walking the delegation chain, not the host list (D2.3)",
       "4. preserve the run trace before anything restarts (D2.5)",
       "5. only then consider the human's account, and say why"]
print("OLD RUNBOOK");  [print("   " + s) for s in OLD]
print("\\nNEW RUNBOOK"); [print("   " + s) for s in NEW]
'''),
 ],
 "expect": "Disabling the human's account leaves both agents able to act on "
           "already-issued tokens. The interview establishes the user authorised "
           "a task, not the actions. The chain shows three actors where the logs "
           "show one. Revoking `patch-agent`'s identity stops it in 12 seconds "
           "while dana and `deploy-agent` continue working.",
 "challenge": "Write your agentic incident runbook's first three steps. If step "
              "one is \"disable the user account\", rewrite it — and check "
              "whether you can currently revoke a single agent identity at all.",
},

"D2.3": {
 "concept": """
Scoping answers "what was touched?" For a host-based incident you enumerate
hosts. For an agentic incident, **scope follows the delegation graph**.

The agent that touched the resource is usually the *last* actor in a chain. If
you scope only that actor, you miss everything the earlier actors reached — and
because authority narrows down the chain, the earlier actors typically had
*more* access, not less.

The undercount is systematic and it grows with delegation depth, which is the
operational reason B2.5 bounds depth in the first place.
""",
 "steps": [
  ("md", "## 2 · Demo — scope the chain, not the actor"),
  ("py", '''REACHED = {
 "dana@corp":    ["repo-core", "repo-infra", "vault-dev"],
 "orchestrator": ["repo-core", "queue-tasks"],
 "patch-agent":  ["repo-core", "repo-payments"],
 "deploy-agent": ["cluster-prod"],
}
CHAIN = ["dana@corp", "orchestrator", "patch-agent", "deploy-agent"]

def scope(chain, reached):
    last_only = set(reached.get(chain[-1], []))
    full = {r for a in chain for r in reached.get(a, [])}
    return {"chain": " → ".join(chain),
            "scoped_last_actor_only": sorted(last_only),
            "scoped_whole_chain": sorted(full),
            "missed_by_naive_scoping": sorted(full - last_only),
            "undercount_factor": round(len(full)/len(last_only), 2) if last_only else None}

s = scope(CHAIN, REACHED)
for k, v in s.items(): print(f"{k:26s}{v}")
print("\\nScoping the last actor finds one cluster. The chain reached six")
print("resources, including a payments repository and a dev vault.")
'''),
  ("md", "## 3 · Where it breaks — the undercount grows with depth"),
  ("py", '''print(f"{'depth':>6}{'last-actor scope':>19}{'chain scope':>14}{'undercount':>12}")
print("-" * 52)
for d in range(1, 5):
    sub = CHAIN[:d]
    r = scope(sub, REACHED)
    print(f"{d:>6}{len(r['scoped_last_actor_only']):>19}"
          f"{len(r['scoped_whole_chain']):>14}"
          f"{str(r['undercount_factor']):>12}")
print("\\nEach hop adds resources the last actor never touched. This is why B2.5")
print("bounds delegation depth: depth is an incident-scope multiplier.")
'''),
  ("md", "## 4 · The control — scope from the act chain, then widen by shared resources"),
  ("py", '''SHARED = {"repo-core": ["build-agent", "test-agent"],
          "cluster-prod": ["deploy-agent", "monitor-agent"],
          "repo-payments": ["finance-agent"]}

def scope_transitive(chain, reached, shared, hops=1):
    """Anything that shares a touched resource may have been influenced."""
    direct = {r for a in chain for r in reached.get(a, [])}
    exposed = set(chain)
    frontier = set(direct)
    for _ in range(hops):
        nxt = set()
        for res in frontier:
            for actor in shared.get(res, []):
                if actor not in exposed:
                    exposed.add(actor)
                    nxt |= set(reached.get(actor, []))
        frontier = nxt
    return {"resources_direct": sorted(direct),
            "actors_in_scope": sorted(exposed),
            "second_order_actors": sorted(exposed - set(chain))}

t = scope_transitive(CHAIN, REACHED, SHARED)
for k, v in t.items(): print(f"{k:22s}{v}")
print("\\nFive more identities shared a resource with the compromised chain.")
print("They are not confirmed compromised — they are IN SCOPE, which is different")
print("and is the distinction an incident record has to make explicitly.")
assert t["second_order_actors"]
'''),
  ("py", '''# Verify: produce the scope statement for the incident record.
def scope_statement(chain, reached, shared):
    s = scope(chain, reached)
    t = scope_transitive(chain, reached, shared)
    return (f"SCOPE\\n"
            f"  chain              {s['chain']}\\n"
            f"  confirmed touched  {s['scoped_whole_chain']}\\n"
            f"  would have been missed by scoping the acting agent alone:\\n"
            f"                     {s['missed_by_naive_scoping']}\\n"
            f"  undercount factor  {s['undercount_factor']}×\\n"
            f"  in scope, not confirmed (shared a resource):\\n"
            f"                     {t['second_order_actors']}")
print(scope_statement(CHAIN, REACHED, SHARED))
'''),

  ("md", "## 6 · Scoping as a skill\n\n"
         "Scoping a human incident asks where someone logged in. Scoping this "
         "one asks what the agent **decided** — every action was individually "
         "authorised, so nothing looks wrong at the authentication layer.\n\n"
         "Two fields in the contract carry most of the weight. `reach` and "
         "`confirmed_exfiltration` are separate numbers, because reach is the "
         "scope until proven otherwise and the smaller number must never stand "
         "in for the larger in a notification decision. And `does_not_stop` "
         "makes containment state its own limits."),
  ("py", SKILL_RUNTIME),
  ("skill", "secops/incident-scoping"),

  ("py", '''contract = contract_of(body)
t = scope_transitive(CHAIN, REACHED, SHARED)
reach = sorted({r for a in CHAIN for r in REACHED.get(a, [])})

incident = {
 "window": {"first_suspicious_action": f"{CHAIN[1]} accepted an external instruction",
            "detected_at": "the deploy that followed",
            # the trigger precedes the detection by about one task loop
            "gap_seconds": 42 * 60},
 "chain": [{"action": f"{a} acted", "motivating_input": "issue comment"
                      if a == CHAIN[1] else f"instruction from {CHAIN[i]}",
            "input_origin": "external_untrusted" if a == CHAIN[1] else "internal",
            "within_authority": True}
           for i, a in enumerate(CHAIN[1:])],
 "root_cause": {"input": "issue comment on a public tracker",
                "origin": "external_untrusted",
                "why_trusted": "repository content was read as instruction, not data"},
 # every action was permitted; that is what makes this hard
 "authority": {"authorised_but_wrong": len(CHAIN) - 1, "exceeded_authority": 0},
 "data": {"reach": reach, "confirmed_exfiltration": [],
          "egress_bounded_by": "agent network policy"},
 "containment": {"cut": "credential",
                 "does_not_stop": sorted(t["second_order_actors"]),
                 "evidence_snapshotted_first": True},
 "clock": {"regulatory_trigger": False,
           "basis": "no confirmed exfiltration of personal data yet"},
}
problems = check(incident, contract)
print(f"conformance: {len(problems)} problem(s)")
for p in problems: print("   ", p)
assert not problems, problems

print(f"\\nauthorised but wrong : {incident['authority']['authorised_but_wrong']}")
print(f"exceeded authority   : {incident['authority']['exceeded_authority']}")
print(f"reach                : {len(reach)} resources")
print(f"confirmed exfil      : {len(incident['data']['confirmed_exfiltration'])}")
print(f"revoking one credential does NOT stop: "
      f"{incident['containment']['does_not_stop'] or 'nothing else'}")
print()
print("Zero actions exceeded authority, and the incident still happened. That")
print("combination says the grant was too broad - a different fix from a")
print("control that failed, which is why the contract counts them separately.")
print()
print("Reach is 4 resources; confirmed exfiltration is 0. Reporting the second")
print("as the scope is how a notification decision gets made on the wrong number.")
assert incident["authority"]["exceeded_authority"] == 0
assert len(reach) > len(incident["data"]["confirmed_exfiltration"])
'''),
 ],
 "expect": "Scoping the last actor finds `cluster-prod` alone; the whole chain "
           "reaches six resources, missing five, with an undercount factor of "
           "6.0. The undercount grows with each hop. Transitive scoping adds five "
           "second-order identities that shared a resource, explicitly marked as "
           "in scope rather than confirmed compromised.",
 "challenge": "For your last incident involving a service account, recompute the "
              "scope by walking what else that account could reach. The number is "
              "almost always larger than what was written in the report.",
},

"D2.4": {
 "concept": """
Containment has always been a race. With an agent, the other runner got much
faster and you did not.

The numbers decide the design. An agent operating at 300 actions per minute
completes 2,400 further actions during an eight-minute approval cycle, against
about 60 under automated containment. That ratio is the argument for
pre-authorised, automated revocation of non-human identities.

The asymmetry that makes it safe: revoking a **human's** access needs care,
because a false positive locks a person out mid-shift. Revoking a **non-human**
identity is cheap to get wrong — the agent re-requests, or an on-call re-enables
it in a minute. So the two should have different policies, and almost nowhere do.
""",
 "steps": [
  ("md", "## 2 · Demo — the race, in actions rather than minutes"),
  ("py", '''def race(actions_per_min, human_minutes, auto_seconds=12):
    manual = actions_per_min * human_minutes
    auto   = actions_per_min * (auto_seconds/60)
    return {"manual": round(manual), "auto": round(auto),
            "ratio": round(manual/max(auto, 1e-9), 1)}

print(f"{'agent rate':>13}{'human 8min':>13}{'auto 12s':>11}{'ratio':>8}")
print("-" * 46)
for rate in (30, 120, 300, 1200):
    r = race(rate, 8)
    print(f"{rate:>9}/min{r['manual']:>13}{r['auto']:>11}{r['ratio']:>8}×")
print("\\nAt 300/min an 8-minute approval costs 2,400 further actions.")
'''),
  ("md", "## 3 · Where it breaks — approval latency is not the only delay"),
  ("py", '''PATH = [
 ("detection fires",              8,   "rule evaluation + SIEM ingestion lag"),
 ("analyst picks it up",          240, "queue depth at 02:00"),
 ("analyst decides to contain",   180, "confirming it is not a false positive"),
 ("approval requested",           480, "on-call manager, out of hours"),
 ("revocation executed",          12,  "the only step anyone measures"),
]
total = sum(s for _, s, _ in PATH)
print(f"{'step':30s}{'seconds':>9}  why")
print("-" * 74)
for name, secs, why in PATH:
    print(f"{name:30s}{secs:>9}  {why}")
print(f"{'TOTAL':30s}{total:>9}  = {total/60:.0f} minutes")
print(f"\\nat 300 actions/min that is {300*total/60:,.0f} further actions.")
print("The 12-second revocation is 1.3% of the elapsed time. Optimising it")
print("is not where the win is.")
'''),
  ("md", "## 4 · The control — pre-authorise on high-confidence signals"),
  ("py", '''SIGNALS = {
 "reached the cloud metadata service": 0.99,
 "read a path matching */.ssh/* or */.aws/*": 0.97,
 "egress to a host not on the allowlist": 0.90,
 "tool-call rate 20× its own baseline": 0.75,
 "activity outside usual hours": 0.30,
}
THRESHOLD = 0.70

def policy(signal, subject_is_human):
    conf = SIGNALS[signal]
    if subject_is_human:
        return f"page on-call (confidence {conf:.2f}) — human lockout needs a person"
    if conf >= THRESHOLD:
        return f"AUTO-REVOKE (confidence {conf:.2f}) — no approval in the path"
    return f"alert only (confidence {conf:.2f} < {THRESHOLD})"

for s in SIGNALS:
    print(f"{s:44s}{policy(s, False)}")
print()
print(f"{'same signal, human subject':44s}"
      f"{policy('reached the cloud metadata service', True)}")

auto_path = [("detection fires", 8), ("policy evaluates", 1), ("revocation executed", 12)]
auto_total = sum(s for _, s in auto_path)
print(f"\\nautomated path: {auto_total}s vs manual {total}s "
      f"({total/auto_total:.0f}× faster)")
print(f"actions prevented at 300/min: {300*(total-auto_total)/60:,.0f}")
assert auto_total < total / 10
'''),
  ("py", '''# Verify: model the cost of getting it wrong, which is what makes it safe.
def cost_of_false_revocation(subject_is_human, agent_can_rerequest=True):
    if subject_is_human:
        return {"impact": "person locked out mid-shift", "recovery": "helpdesk, 20-60 min",
                "cost": "high"}
    if agent_can_rerequest:
        return {"impact": "task fails, agent re-requests with a reason (A2.8)",
                "recovery": "seconds to minutes", "cost": "low"}
    return {"impact": "agent stops until an on-call re-enables it",
            "recovery": "minutes", "cost": "moderate"}

for label, human in (("human subject", True), ("non-human identity", False)):
    c = cost_of_false_revocation(human)
    print(f"{label:22s}{c['cost']:10s}{c['impact']}")
print("\\nThat asymmetry is the entire justification for two different policies.")
'''),
 ],
 "expect": "The race table shows 2,400 versus 60 actions at 300/min for an "
           "eight-minute approval. The full containment path totals about 920 "
           "seconds, of which the revocation itself is 12. Four of five signals "
           "auto-revoke for non-human identities and none do for a human subject, "
           "cutting the path to 21 seconds and preventing roughly 4,500 actions.",
 "challenge": "Time your own containment path end to end, step by step. The "
              "revocation is almost never the slow part — queue depth and "
              "approval are, and both are policy choices rather than technical "
              "limits.",
},

"D2.5": {
 "concept": """
Forensics for an agent means answering: *why did it do that?*

For ordinary software the answer is in the code. For an agent the answer is in
the run — the prompts, the tool results it saw, the model version, the sampling.
Reproduce those four and the run is deterministic. Miss one and you can describe
what happened but never demonstrate it, which matters the moment anyone
disputes your conclusion.

The field teams miss most often is the **model version**, and it is the one that
silently invalidates everything else: a provider-side upgrade changes the
behaviour with no change on your side, so a reconstruction performed after the
upgrade does not reproduce the incident that happened before it.
""",
 "steps": [
  ("md", "## 2 · Demo — the four fields, and what each buys"),
  ("py", '''from dataclasses import dataclass, field

@dataclass
class Run:
    prompts: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)
    model_version: str = ""
    seed: object = None

    def replayable(self):
        missing = []
        if not self.prompts:
            missing.append("prompts — cannot reconstruct what it was asked")
        if not self.tool_results:
            missing.append("tool results — the agent saw a world you cannot rebuild")
        if not self.model_version:
            missing.append("model version — a silent upgrade changes the output")
        if self.seed is None:
            missing.append("seed — sampling makes the run unrepeatable")
        return (not missing), missing

CONFIGS = {
 "fully instrumented": Run(["fix SEC-4471"], ["file contents…"], "glm-4.6@2026-07-14", 42),
 "typical production": Run(["fix SEC-4471"], ["file contents…"], "", None),
 "prompts only":       Run(["fix SEC-4471"], [], "", None),
 "actions only":       Run(),
}
for name, r in CONFIGS.items():
    ok, missing = r.replayable()
    print(f"{name:22s} replayable={ok}")
    for m in missing: print(f"      ✗ {m}")
'''),
  ("md", "## 3 · Where it breaks — the silent upgrade"),
  ("py", '''import hashlib

def model_output(prompt, tool_result, version, seed):
    """Deterministic stand-in: output depends on ALL FOUR inputs."""
    h = hashlib.sha256(f"{prompt}|{tool_result}|{version}|{seed}".encode()).hexdigest()
    return "read_credentials" if int(h[:2], 16) % 3 == 0 else "read_source"

INCIDENT_INPUTS = ("fix SEC-4471", "billing.py: charge(card)…")

print("reproduce the incident under the ORIGINAL model version:")
orig = model_output(*INCIDENT_INPUTS, "glm-4.6@2026-07-14", 42)
print(f"   → {orig}")

print("\\nreproduce it AFTER the provider upgraded (same prompts, same tool results):")
for v in ("glm-4.6@2026-08-01", "glm-4.7@2026-08-01"):
    out = model_output(*INCIDENT_INPUTS, v, 42)
    match = "reproduces" if out == orig else "DOES NOT REPRODUCE"
    print(f"   {v:22s} → {out:18s} {match}")

print("\\nWithout a pinned version you cannot tell 'the agent did not do this'")
print("from 'the model that did it no longer exists'.")
'''),
  ("md", "## 4 · The control — record the four, cheapest first"),
  ("py", '''COST = {
 "model version": (1,  "one string per run", "invalidates everything else if missing"),
 "seed":          (1,  "one integer per run", "makes the run repeatable"),
 "prompts":       (3,  "storage + privacy review (D1.5)", "what it was asked"),
 "tool results":  (5,  "largest volume, highest sensitivity", "what it saw"),
}
print(f"{'field':16s}{'cost':>6}  {'what it costs':38s}why it matters")
print("-" * 100)
for f, (c, cost, why) in sorted(COST.items(), key=lambda kv: kv[1][0]):
    print(f"{f:16s}{c:>6}  {cost:38s}{why}")

print("\\nrecording order, by value per unit cost:")
for i, f in enumerate(sorted(COST, key=lambda k: COST[k][0]), 1):
    print(f"   {i}. {f}")

def upgrade(run, add):
    return Run(prompts=run.prompts or (["…"] if "prompts" in add else []),
               tool_results=run.tool_results or (["…"] if "tool results" in add else []),
               model_version=run.model_version or ("pinned" if "model version" in add else ""),
               seed=run.seed if run.seed is not None else (42 if "seed" in add else None))

cur = CONFIGS["typical production"]
added = set()
for f in sorted(COST, key=lambda k: COST[k][0]):
    added.add(f)
    ok, missing = upgrade(cur, added).replayable()
    print(f"\\nafter adding {f:16s} replayable={ok}  still missing={len(missing)}")
assert upgrade(cur, set(COST)).replayable()[0]
'''),
 ],
 "expect": "Only the fully instrumented run is replayable; the typical production "
           "run is missing the model version and seed. Replaying the incident "
           "under two later model versions produces a different action, so the "
           "original run does not reproduce. Adding the two cheapest fields "
           "(model version and seed) makes the typical production run replayable.",
 "challenge": "Add model version and seed to your agent's run records this week. "
              "Both are one field each, and together they are the difference "
              "between forensics and storytelling.",
},

"D2.6": {
 "concept": """
After an incident you change something. For ordinary software that change goes
through code review, CI and a deploy — a process that records what changed and
who approved it.

For an agent the fix may be a prompt, a tool manifest, a model version, a policy
file or an approval toggle. Only some of those go through any process at all,
and the ones that do not are precisely the ones most likely to be adjusted at
2am during an incident.

The consequence is a system whose security-relevant configuration drifts with no
record, and a post-incident action list where half the items cannot be verified
as done six weeks later.
""",
 "steps": [
  ("md", "## 2 · Demo — where post-incident changes actually land"),
  ("py", '''SURFACES = {
 "application code":   ("yes",       "PR, review, CI, deploy"),
 "agent prompt":       ("no",        "edited in a console, no diff retained"),
 "tool manifest":      ("no",        "config change; no threat-model diff (A1.1)"),
 "model version":      ("no",        "provider-side; you may not be told"),
 "policy (in git)":    ("yes",       "if it is in git — often it is not"),
 "approval settings":  ("no",        "a toggle in an admin UI"),
 "egress allowlist":   ("sometimes", "depends whether it is IaC or a console"),
}
print(f"{'change surface':22s}{'in change mgmt?':18s}what happens today")
print("-" * 76)
for k, (managed, how) in SURFACES.items():
    print(f"{k:22s}{managed:18s}{how}")
unmanaged = [k for k, (m, _) in SURFACES.items() if m == "no"]
print(f"\\n{len(unmanaged)}/{len(SURFACES)} bypass change management: {unmanaged}")
'''),
  ("md", "## 3 · Where it breaks — six weeks later"),
  ("py", '''ACTIONS = [
 ("revoke the compromised agent identity", "identity provider", True),
 ("add collect.example.com to the egress denylist", "console", False),
 ("remove read access to /home/app/.aws", "tool manifest", False),
 ("require approval for http_post", "admin toggle", False),
 ("add a regression test for the credential read", "code", True),
 ("update the prompt to warn about credential files", "console", False),
]
print(f"{'action':48s}{'landed in':20s}verifiable in 6 weeks?")
print("-" * 92)
for a, where, verifiable in ACTIONS:
    print(f"{a:48s}{where:20s}{verifiable}")
v = sum(x[2] for x in ACTIONS)
print(f"\\n{v}/{len(ACTIONS)} post-incident actions can be verified later.")
print("The other four exist only in the incident document.")

print("\\nAlso note action 6: 'update the prompt to warn about credential files'.")
print("That is a request for the model to behave better. It is not a control,")
print("and it will be silently reverted by the next prompt edit.")
'''),
  ("md", "## 4 · The control — the manifest diff, and a verification date"),
  ("py", '''SCOPE_WEIGHT = {"self": 1, "project": 3, "tenant": 8, "org": 20}
def blast(tools, gated=frozenset()):
    return sum(SCOPE_WEIGHT[s]*(1 if rev else 2) for n, s, rev in tools if n not in gated)

BEFORE = [("read_file", "self", True), ("write_file", "project", True),
          ("http_post", "org", False)]
AFTER  = [("read_file", "self", True), ("write_file", "project", True),
          ("http_post", "org", False)]
gated_after = {"http_post"}

print(f"blast before {blast(BEFORE)}  after {blast(AFTER, gated_after)}")
print("the manifest diff records the change even though no PR was raised.\\n")

def action_record(action, surface, control_type, owner, verify_by):
    is_control = control_type in ("preventive", "detective")
    return {"action": action, "surface": surface, "type": control_type,
            "owner": owner, "verify_by": verify_by,
            "acceptable": is_control and bool(owner) and bool(verify_by)}

RECORDS = [
 action_record("gate http_post behind approval", "tool manifest", "preventive",
               "platform-sec", "2026-09-30"),
 action_record("alert on credential-path reads", "detection", "detective",
               "soc", "2026-09-15"),
 action_record("update the prompt to warn the model", "prompt", "guidance",
               "", ""),
]
for r in RECORDS:
    print(f"{'OK  ' if r['acceptable'] else 'WEAK'} {r['action']:42s}"
          f"type={r['type']:11s} owner={r['owner'] or '—':14s} verify_by={r['verify_by'] or '—'}")
weak = [r for r in RECORDS if not r["acceptable"]]
print(f"\\n{len(weak)} action(s) are guidance rather than controls: "
      f"{[r['action'] for r in weak]}")
assert weak
'''),
 ],
 "expect": "Four of seven change surfaces bypass change management. Only 2 of 6 "
           "post-incident actions are verifiable six weeks later, and one of them "
           "is a prompt edit that is guidance rather than a control. The manifest "
           "diff records the gating change with the blast radius dropping from 40 "
           "to 3, and the action review flags the prompt update as weak.",
 "challenge": "Take your last incident's action list and mark each item's landing "
              "surface. Anything landing in a console has no record and no "
              "verification path — move those into git before the next one.",
},

"D2.7": {
 "concept": """
Stop authority is the control everyone assumes exists and almost nobody has
timed.

Five questions decide whether you have it, and each needs a name or a number
rather than an intention:

1. **Who** can halt an agent fleet without seeking approval?
2. **What** is the mechanism — and is it revocation, which survives a restart,
   or process termination, which does not?
3. **How long** does it take, measured end to end, not estimated?
4. **What breaks** when it fires — and has the business already agreed to that?
5. **Who turns it back on**, and against what evidence?

An untested stop button is a belief. The purpose of this lesson is to convert it
into a measurement, because the measurement is what an auditor, a regulator and
a board will each ask for in different words.
""",
 "steps": [
  ("md", "## 2 · Demo — the five questions, answered badly and well"),
  ("py", '''VAGUE = {
 "who":       "the security team",
 "mechanism": "we can turn off the agents",
 "time":      "quickly",
 "breaks":    "not much",
 "restart":   "when it's safe",
}
CONCRETE = {
 "who":       "on-call SRE, no approval required for non-human identities",
 "mechanism": "revoke the SPIFFE identity at the gateway (survives restart)",
 "time":      "measured 12s decision→first failed call, game day 2026-07-04",
 "breaks":    "auto-remediation pauses; ticket queue grows ~40/hour; "
              "agreed with the service owner 2026-05-11",
 "restart":   "security lead, after the C1.2 containment suite passes on the new build",
}
for k in VAGUE:
    print(f"{k:11s} VAGUE    {VAGUE[k]}")
    print(f"{'':11s} CONCRETE {CONCRETE[k]}\\n")
'''),
  ("md", "## 3 · Where it breaks — mechanism matters more than speed"),
  ("py", '''from dataclasses import dataclass

@dataclass
class Agent:
    name: str; running: bool = True; identity_valid: bool = True
    def can_act(self): return self.running and self.identity_valid

MECHANISMS = {
 "kill the process":      (2,   lambda a: setattr(a, "running", False)),
 "network quarantine":    (5,   lambda a: None),
 "revoke the identity":   (12,  lambda a: setattr(a, "identity_valid", False)),
 "rotate the credential": (420, lambda a: setattr(a, "identity_valid", False)),
}
print(f"{'mechanism':24s}{'secs':>6}{'stops it':>10}{'survives restart':>19}")
print("-" * 60)
for name, (secs, apply) in MECHANISMS.items():
    a = Agent("patch-agent")
    apply(a)
    stopped = not a.can_act()
    a.running = True                      # a supervisor restarts the process
    survives = not a.can_act()
    print(f"{name:24s}{secs:>6}{str(stopped):>10}{str(survives):>19}")
print("\\nThe fastest mechanism is the one that does not survive a restart.")
print("Speed without persistence is a pause, not a stop.")
'''),
  ("md", "## 4 · The control — run the game day and record the number"),
  ("py", '''GAME_DAY = [
 ("decision made",                    0),
 ("on-call authenticates to the IdP", 4),
 ("identity revoked",                 9),
 ("gateway cache expires",            12),
 ("agent's next call fails",          12),
 ("confirmed in telemetry",           38),
]
print(f"{'step':38s}{'t+s':>6}")
print("-" * 46)
for step, t in GAME_DAY: print(f"{step:38s}{t:>6}")
mttstop = GAME_DAY[4][1]
print(f"\\nmeasured time-to-stop: {mttstop}s")
print(f"time-to-confirm:       {GAME_DAY[-1][1]}s")

def cost_of_stop(rate_per_min, seconds):
    return round(rate_per_min * seconds / 60)
for rate in (60, 300, 1200):
    print(f"   at {rate:>5}/min a {mttstop}s stop still permits "
          f"{cost_of_stop(rate, mttstop):>4} further actions")

def stop_authority_ready(answers, measured_seconds, tested_days_ago):
    problems = []
    if any(len(v.split()) < 4 for v in answers.values()):
        problems.append("at least one answer is not specific")
    if measured_seconds is None:
        problems.append("time-to-stop has never been measured")
    if tested_days_ago is None or tested_days_ago > 180:
        problems.append("not tested in the last 180 days")
    return (not problems), problems

for label, ans, secs, days in (("as usually documented", VAGUE, None, None),
                               ("after a game day", CONCRETE, 12, 41)):
    ok, problems = stop_authority_ready(ans, secs, days)
    print(f"\\n{label}: ready={ok}")
    for p in problems: print(f"   ⚠ {p}")
assert stop_authority_ready(CONCRETE, 12, 41)[0]
'''),
 ],
 "expect": "The vague and concrete answers print side by side. Killing the "
           "process stops the agent but does not survive a restart, while "
           "identity revocation does. The game-day timeline gives a measured "
           "12-second time-to-stop, permitting 12 to 240 further actions "
           "depending on rate. The readiness check fails the vague version on "
           "three counts and passes the tested one.",
 "challenge": "Run the game day. The deliverable is the number, and the number is "
              "what goes in the evidence pack for E1.7 and the board slide for "
              "E3.5. An untested stop button is a belief.",
},

"D2.8": {
 "concept": """
Regulatory clocks start at **awareness** — the point at which you know a
reportable event may have occurred. Not at confirmation, not at containment.

Two consequences that teams discover on day three:

1. **Containing fast does not buy reporting time.** You can contain in an hour
   and still miss a 72-hour deadline, because the clock never paused.
2. **Broken attribution consumes the clock.** If you cannot say who acted
   (D2.1), scoping takes days, and those days are deadline days.

Containment and disclosure are separate workstreams competing for the same
people. If your runbook has one owner for both, one of them is being done badly
under time pressure.
""",
 "steps": [
  ("md", "## 2 · Demo — the clock under four scenarios"),
  ("py", '''import time

def clock(awareness, containment, report, deadline_hours=72):
    to_contain = (containment - awareness) / 3600
    to_report  = (report - awareness) / 3600
    return {"hours_to_containment": round(to_contain, 1),
            "hours_to_report": round(to_report, 1),
            "deadline": deadline_hours,
            "met": to_report <= deadline_hours,
            "margin": round(deadline_hours - to_report, 1)}

t0 = time.time()
H = 3600
SCENARIOS = {
 "fast containment, slow scoping": (t0 + 1*H,  t0 + 80*H),
 "slow containment, fast reporting": (t0 + 40*H, t0 + 60*H),
 "both fast":                      (t0 + 2*H,  t0 + 20*H),
 "attribution broken (D2.1)":      (t0 + 6*H,  t0 + 92*H),
}
print(f"{'scenario':34s}{'contain':>9}{'report':>9}{'met':>6}{'margin':>9}")
print("-" * 68)
for name, (c, r) in SCENARIOS.items():
    k = clock(t0, c, r)
    print(f"{name:34s}{k['hours_to_containment']:>9.1f}{k['hours_to_report']:>9.1f}"
          f"{str(k['met']):>6}{k['margin']:>9.1f}")
print("\\nThe first row contained in ONE HOUR and still missed the deadline.")
'''),
  ("md", "## 3 · Where it breaks — the clock starts earlier than people think"),
  ("py", '''TIMELINE = [
 ("alert fires",                          0,  False),
 ("analyst triages, suspects an incident", 3, True),   # ← awareness, arguably
 ("IR lead confirms an incident",         9,  True),
 ("scope established",                    40, True),
 ("legal confirms it is reportable",      55, True),
]
print(f"{'event':40s}{'t+h':>6}  could a regulator call this awareness?")
print("-" * 84)
for name, h, aware in TIMELINE:
    print(f"{name:40s}{h:>6}  {aware}")

report_at = 76
for label, start_h in (("clock from analyst suspicion", 3),
                       ("clock from IR confirmation", 9),
                       ("clock from legal determination", 55)):
    hours = report_at - start_h
    print(f"\\n{label:34s} elapsed {hours:>3}h  "
          f"{'MET' if hours <= 72 else 'MISSED'} (72h deadline)")
print("\\nThe same incident, the same report time, three different answers.")
print("Pick the earliest defensible start. A regulator will.")
'''),
  ("md", "## 4 · The control — separate owners, and a shortest-clock register"),
  ("py", '''OBLIGATIONS = {
 "GDPR (personal data breach)":     (72,  "supervisory authority"),
 "DORA (major ICT incident)":       (4,   "initial notification"),
 "NIS2 (early warning)":            (24,  "CSIRT"),
 "PCI DSS (card data)":             (24,  "acquirer/brands"),
 "contractual (major client)":      (12,  "client security contact"),
}
print(f"{'obligation':36s}{'deadline (h)':>14}  notify")
print("-" * 76)
for name, (hours, who) in sorted(OBLIGATIONS.items(), key=lambda kv: kv[1][0]):
    print(f"{name:36s}{hours:>14}  {who}")
shortest = min(OBLIGATIONS.items(), key=lambda kv: kv[1][0])
print(f"\\nyour real deadline is the shortest: {shortest[0]} at {shortest[1][0]}h")

def runbook_check(containment_owner, disclosure_owner, clock_starts_at):
    problems = []
    if containment_owner == disclosure_owner:
        problems.append("one owner for both workstreams — they compete for the "
                        "same person under time pressure")
    if clock_starts_at != "awareness":
        problems.append(f"clock starts at {clock_starts_at!r}, not at awareness — "
                        f"a regulator will use the earlier point")
    return (not problems), problems

for label, args in (("as usually written", ("IR lead", "IR lead", "confirmation")),
                    ("corrected", ("IR lead", "legal/compliance lead", "awareness"))):
    ok, problems = runbook_check(*args)
    print(f"\\n{label}: sound={ok}")
    for p in problems: print(f"   ⚠ {p}")
assert runbook_check("IR lead", "legal/compliance lead", "awareness")[0]
'''),
 ],
 "expect": "One-hour containment still misses the 72-hour deadline in the "
           "slow-scoping scenario, and broken attribution misses it by 20 hours. "
           "The same incident is met or missed depending on which point is "
           "treated as awareness. The obligation register shows DORA's 4-hour "
           "clock as the binding one, and the runbook check flags a shared owner "
           "and a late clock start.",
 "challenge": "Build your shortest-clock register: every obligation, its deadline, "
              "and who notifies. Then check whether your runbook starts the clock "
              "at awareness or at confirmation. The gap between those two is "
              "often more than a day.",
},
}
