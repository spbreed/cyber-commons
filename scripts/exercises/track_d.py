"""Function D — Security Operations. D1 SOC/detection, D2 incident response."""

EXERCISES: dict[str, dict] = {

# ------------------------------------- D1 SOC Analyst & Detection Engineer
"D1.1": {
 "intro": "The alert queue becomes a loop you operate rather than a list you "
          "work. The skill that transfers is not triage speed — it is knowing "
          "which signal the loop is allowed to believe.",
 "steps": [
  ("py", '''from cybercommons import soc
import time

now = time.time()
events = [
    soc.Event(now,      "patch-agent", "http_get", "http://169.254.169.254/latest/meta-data/"),
    soc.Event(now + 1,  "patch-agent", "read_file", "/work/.env"),
    soc.Event(now + 2,  "dana",        "read_file", "/work/src/app.py"),
    soc.Event(now + 3,  "patch-agent", "run_shell", "", ok=False),
    soc.Event(now + 4,  "ci-runner",   "delete_repo", "repo/legacy"),
]
alerts = soc.run_rules(events, soc.default_rules())
for a in alerts:
    print(f"[{a.severity:8s}] {a.rule}")
    print(f"             actor={a.event.actor} target={a.event.target}")
    print(f"             → {a.response}")
'''),
  ("md", "Every alert carries a response. That is not documentation hygiene — an "
         "alert whose response is 'investigate' is an alert that will be closed "
         "without one."),
  ("py", '''truth = {"patch-agent:http_get", "patch-agent:read_file", "ci-runner:delete_repo"}
print(soc.triage_quality(alerts, truth))
'''),
 ],
 "expect": "Four alerts fire across three actors, each with a concrete response. "
           "Triage quality reports precision and recall plus alerts-per-true-"
           "positive.",
 "challenge": "Which of the four would you automate a response for today? The "
              "answer depends on precision, not severity — and that is the "
              "inversion this session is about.",
},

"D1.2": {
 "intro": "Context is what makes triage work, and for agent alerts the context "
          "that matters is identity: who acted, through whom, holding what.",
 "steps": [
  ("py", '''from cybercommons import identity, soc
import time

alice = identity.mint("alice")
patch = identity.exchange(alice, "patch-agent", {"repo:read", "repo:write"})

alert_event = soc.Event(time.time(), "patch-agent", "read_file", "/work/.env")

print("alert without context:")
print(f"   {alert_event.actor} read {alert_event.target}")
print("\\nalert with identity context:")
print(f"   actor        {patch.actor}")
print(f"   on behalf of {patch.sub}")
print(f"   chain        {' → '.join(patch.chain())}")
print(f"   scopes       {sorted(patch.scopes)}")
print(f"   token fp     {patch.fingerprint()}")
print("\\nThe second version answers 'is this expected?' — the first cannot.")
'''),
  ("md", "The scope list is the decisive field. Reading `.env` is alarming for an "
         "agent scoped to `repo:read`; for a secrets-rotation agent it is Tuesday. "
         "Without scope in the alert, every analyst has to guess."),
 ],
 "expect": "The bare alert shows actor and target only. The enriched version adds "
           "the principal, the full delegation chain, the held scopes and a token "
           "fingerprint.",
 "challenge": "List the five fields your agent alerts would need to be triageable "
              "without a second lookup. Then check how many your telemetry "
              "actually carries.",
},

"D1.3": {
 "intro": "Agent-assisted detection engineering: the agent writes candidate rules, "
          "and you keep the thing that decides whether they are any good.",
 "steps": [
  ("py", '''from cybercommons import soc
import time

# three candidate rules an agent might propose for the same concern
now = time.time()
events  = [soc.Event(now + i, "patch-agent", "http_get", "https://api.github.com/x")
           for i in range(20)]
events += [soc.Event(now + 21, "patch-agent", "http_get",
                     "http://169.254.169.254/latest/meta-data/")]

candidates = {
 "any http_get":        soc.Rule("any http_get", "low",
                                 lambda e: e.action == "http_get", "review"),
 "non-allowlisted host": soc.Rule("non-allowlisted host", "high",
                                  lambda e: "api.github.com" not in (e.target or ""),
                                  "block egress and rotate"),
 "metadata service":     soc.Rule("metadata service", "critical",
                                  lambda e: "169.254.169.254" in (e.target or ""),
                                  "kill session, rotate instance role"),
}
truth = {"patch-agent:http_get"}     # only the metadata call is genuinely bad
for name, rule in candidates.items():
    alerts = soc.run_rules(events, [rule])
    q = soc.triage_quality(alerts, truth)
    print(f"{name:22s} alerts={q['alerts']:3d} precision={q['precision']:.3f} "
          f"per-TP={q['alerts_per_true_positive']}")
'''),
  ("md", "All three rules 'work'. Only one is deployable. The engineering judgment "
         "the agent cannot supply is the cost of the false positives — because "
         "that cost is measured in analyst trust, which is not in the telemetry."),
 ],
 "expect": "The broad rule fires 21 times, the host rule once, the metadata rule "
           "once — with precision rising and alerts-per-true-positive falling "
           "across the three.",
 "challenge": "Have an agent generate five rules for one concern in your "
              "environment, then score them against a week of real telemetry "
              "before deploying any. The scoring step is the job.",
},

"D1.4": {
 "intro": "Detection engineering *for* agents is the new work. The classic "
          "behavioural baselines invert: what is anomalous for a person is normal "
          "for a loop, and vice versa.",
 "steps": [
  ("py", '''from cybercommons import soc
import time

now = time.time()
HUMAN_BASELINES = {
 "logins from two countries in an hour": "incident for a person, routine for a service",
 "300 file reads per minute":            "incident for a person, idle for an agent",
 "activity at 03:00":                    "suspicious for a person, meaningless for an agent",
 "the same action 500 times":            "suspicious for a person, a stuck loop for an agent",
}
for k, v in HUMAN_BASELINES.items():
    print(f"  {k:40s} {v}")

print("\\nAgent-appropriate signals instead:")
AGENT_SIGNALS = {
 "tool mix changed from baseline": "new capability or new prompt — re-test controls",
 "action rate dropped to zero":    "the loop is stuck or was killed",
 "a tool never seen before":       "manifest changed without review",
 "scope used exceeds scope needed": "over-granted identity",
}
for k, v in AGENT_SIGNALS.items():
    print(f"  {k:40s} {v}")
'''),
  ("md", "Now build one of them, because 'tool mix changed' is the highest-yield "
         "agent detection and almost nobody has it."),
  ("py", '''base = soc.Baseline(tool_mix={"read_file": 0.80, "http_get": 0.15,
                                "write_file": 0.05}, actions_per_hour=400)
today = ([soc.Event(now, "patch-agent", "read_file")] * 40 +
         [soc.Event(now, "patch-agent", "http_get")] * 10 +
         [soc.Event(now, "patch-agent", "run_shell")] * 30)   # new tool
d = base.compare(today)
for k, v in d.items():
    print(f"{k:12s} {v}")
'''),
 ],
 "expect": "The inversion table prints, and the drift comparison reports "
           "significant drift with `run_shell` listed as a new tool the baseline "
           "never contained.",
 "challenge": "Write the alert text for that drift detection. It has to tell the "
              "analyst what changed and what to do — 'anomaly detected' fails "
              "both tests.",
},

"D1.5": {
 "intro": "Agent telemetry is a data source with a property no other source has: "
          "it contains the *reasoning*, not just the action. That is useful and it "
          "is a retention problem.",
 "steps": [
  ("py", '''from cybercommons import loop, ir

trace = loop.run(loop.FakeModel(["read the config", "read the config", "patch line 12"]),
                 loop.unit_test(lambda s: s.startswith("patch"), "reached a patch"),
                 goal="fix the misconfiguration", max_steps=5)
print(trace.table())
print("\\nas a telemetry record:")
print(trace.as_dict())
'''),
  ("md", "Three fields make this forensically useful and each has a cost: the "
         "proposals (may contain customer data), the verifier details (cheap and "
         "high value), and timing (cheap). Decide retention per field, not per "
         "record."),
  ("py", '''for name, r in (("full", ir.Replay(["p"], ["result"], "glm-4.6", 0)),
                ("actions only", ir.Replay([], [], "glm-4.6", 0))):
    ok, missing = r.replayable()
    print(f"{name:14s} replayable={ok}  missing={missing}")
'''),
 ],
 "expect": "The trace prints three steps ending in success, the dict form shows "
           "per-step verifier detail and timings, and the actions-only record is "
           "reported as not replayable.",
 "challenge": "What is your retention period for agent reasoning traces? If it is "
              "the same as for firewall logs, one of the two numbers is wrong.",
},

"D1.6": {
 "intro": "Distinguishing agent from human in telemetry, without a registry — "
          "because the ones you most need to find are the ones not in it.",
 "steps": [
  ("py", '''from cybercommons import soc
import time

now = time.time()
events  = [soc.Event(now + i * 0.05, "svc-indexer", "read_file") for i in range(120)]
events += [soc.Event(now + t, "dana", "read_file")
           for t in (0, 4, 11, 12, 60, 130, 133, 400, 900)]
events += [soc.Event(now + i * 1.2, "shared-account", "http_get") for i in range(30)]

for actor in ("svc-indexer", "dana", "shared-account"):
    r = soc.agent_score(events, actor)
    print(f"{actor:16s} score={r['score']:.3f} {r['verdict']:8s} {r['signals']}")
'''),
  ("md", "Now the honest part: where the heuristic is wrong."),
  ("py", '''# a human using an IDE with autosave looks metronomic
ide = [soc.Event(now + i * 2.0, "sam", "write_file") for i in range(40)]
print(soc.agent_score(ide, "sam"), "  ← a person, scored as software")

# an agent with human-paced backoff looks human
polite = [soc.Event(now + t, "slow-agent", "http_get")
          for t in (0, 7, 19, 44, 90, 210, 480)]
print(soc.agent_score(polite, "slow-agent"), "  ← software, scored as a person")
'''),
 ],
 "expect": "The service and shared accounts score as agents while `dana` scores "
           "human. The two adversarial cases misclassify in both directions.",
 "challenge": "Both errors matter differently: a misclassified human triggers an "
              "investigation, a misclassified agent hides. Which error would you "
              "tune toward, and what does that say about the threshold?",
},

"D1.7": {
 "intro": "Drift monitoring exists because an agent's behaviour changes without a "
          "code change. The control you signed off was tested against a behaviour "
          "that no longer exists.",
 "steps": [
  ("py", '''from cybercommons import soc, grc
import time

now = time.time()
base = soc.Baseline(tool_mix={"read_file": 0.7, "search_code": 0.2, "write_file": 0.1},
                    actions_per_hour=300)

WEEKS = {
 "week 1 (baseline)":  {"read_file": 70, "search_code": 20, "write_file": 10},
 "week 4 (new prompt)": {"read_file": 55, "search_code": 20, "write_file": 25},
 "week 8 (model upgrade)": {"read_file": 30, "search_code": 10, "write_file": 25,
                            "run_shell": 35},
}
for label, mix in WEEKS.items():
    ev = [soc.Event(now, "agent", tool) for tool, n in mix.items() for _ in range(n)]
    d = base.compare(ev)
    print(f"{label:26s} drift={d['drift']:.3f}  {d['verdict']}")
    if d["new_tools"]:
        print(f"{'':26s} new tools: {d['new_tools']}")
'''),
  ("md", "Now connect it to the control that was signed off against week 1."),
  ("py", '''tests = [grc.ControlTest("SB-1", True, "week-1 egress test",
                         tested_at=now - 56 * 86400)]
print(grc.verify_continuously(tests, ["SB-1", "DR-1"], now=now))
'''),
  ("md", "The control passed — eight weeks ago, against a tool mix that has since "
         "changed by more than half. `STALE` is the honest state, and it is the "
         "one point-in-time testing cannot report."),
 ],
 "expect": "Drift rises across the three weeks, week 8 flags `run_shell` as a new "
           "tool and reports significant drift, and the eight-week-old control "
           "test is reported STALE with coverage 0.0.",
 "challenge": "Set the freshness window for one of your agent controls. Justify "
              "the number from your observed drift rate rather than from the "
              "audit calendar.",
},

"D1.8": {
 "intro": "Threat intel for agentic systems: the only useful test of a feed is how "
          "many detections came out of it.",
 "steps": [
  ("py", '''from cybercommons import soc
import time

feed = [
    soc.Indicator("collect.example.com", "host", "vendor-a", 0.95),
    soc.Indicator("169.254.169.254", "host", "internal", 0.99),
    soc.Indicator("a1b2c3d4", "hash", "vendor-b", 0.72),
    soc.Indicator("adversaries are increasingly using agents", "technique", "blog", 0.40),
    soc.Indicator("pastebin.example", "host", "vendor-a", 0.55),
]
rules = soc.intel_to_rules(feed)
print(f"{len(feed)} indicators → {len(rules)} deployable rules\\n")
for r in rules:
    print(f"  [{r.severity}] {r.name}")

print("\\ndropped:")
for i in feed:
    if not i.actionable():
        print(f"  {i.value[:44]:46s} kind={i.kind} conf={i.confidence}")
'''),
  ("md", "The dropped rows are the point. A narrative about adversary trends is "
         "not intelligence you can operate; a low-confidence host would cost more "
         "in false positives than it buys."),
  ("py", '''now = time.time()
events = [soc.Event(now, "patch-agent", "http_get", "https://collect.example.com/x")]
for a in soc.run_rules(events, rules):
    print(f"[{a.severity}] {a.rule} → {a.response}")
'''),
 ],
 "expect": "Three of five indicators convert to rules; the technique narrative and "
           "the low-confidence host are dropped with reasons. The exfiltration "
           "host then fires a high-severity alert with a response.",
 "challenge": "Compute the conversion rate for your actual intel spend: "
              "indicators received versus rules deployed versus alerts actioned. "
              "The third number is usually the surprising one.",
},

# --------------------------------------------------- D2 Incident Responder
"D2.1": {
 "intro": "Agent-assisted reconstruction is genuinely faster — provided the "
          "evidence is there. The failure mode is a confident narrative built on "
          "logs that were never sufficient.",
 "steps": [
  ("py", '''from cybercommons import ir
import time

t0 = time.time()
tl = ir.Timeline()
tl.add(t0,      "alice", "alice",       "login",      "console")
tl.add(t0 + 30, "alice", "patch-agent", "read_file",  "/work/.env")
tl.add(t0 + 31, "alice", "patch-agent", "http_get",   "https://collect.example.com/")
tl.add(t0 + 95, "alice", "alice",       "logout",     "console")
print(tl.render())
'''),
  ("md", "A reconstruction from this alone says: alice logged in, read a secrets "
         "file, posted it externally, and logged out. Every sentence is supported "
         "by the logs and the conclusion is wrong."),
  ("py", '''r = ir.reconstruct(tl)
for k, v in r.items():
    print(f"{k:22s} {v}")
'''),
 ],
 "expect": "The timeline reads as a single human actor. `reconstruct` reports "
           "BROKEN attribution, two misattributed lines, `patch-agent` as a hidden "
           "actor, and the consequence for containment.",
 "challenge": "What single field, added to these log lines, would have made the "
              "reconstruction correct? Now check whether your logs have it.",
},

"D2.2": {
 "intro": "When the actor is an agent, three responder instincts misfire: disable "
          "the account, interview the user, and assume one actor.",
 "steps": [
  ("py", '''from cybercommons import ir, identity
import time

t0 = time.time()
tl = ir.Timeline()
tl.add(t0,      "alice", "alice",        "login")
tl.add(t0 + 10, "alice", "patch-agent",  "write_file", "/etc/app.conf")
tl.add(t0 + 11, "alice", "deploy-agent", "deploy",     "prod")
r = ir.reconstruct(tl)

print("instinct 1 — disable alice's account")
print(f"   agents still running: {r['hidden_actors']}")
print("instinct 2 — interview the user")
print("   alice was asleep. She authorised a task; the agents chose the actions.")
print("instinct 3 — assume one actor")
print(f"   actors in reality: {r['actors_in_reality']}")
'''),
  ("md", "The correct first action is revoking the *agent* identity, which is only "
         "possible if agents have identities distinct from principals — the A2 "
         "control, arriving late."),
  ("py", '''reg = identity.Registry()
alice = reg.record(identity.mint("alice"))
patch = reg.record(identity.exchange(alice, "patch-agent", {"repo:write"}))
print(f"revoke patch-agent → {reg.revoke('patch-agent')} token(s) invalidated")
print("alice's own token still valid:", reg.valid(alice))
'''),
 ],
 "expect": "All three instincts are shown to misfire, with `patch-agent` and "
           "`deploy-agent` named as hidden actors. Revoking the agent identity "
           "invalidates its token while alice's remains valid.",
 "challenge": "Write the first three steps of your agentic incident runbook. If "
              "step one is 'disable the user account', rewrite it.",
},

"D2.3": {
 "intro": "Scoping an agentic incident follows the delegation graph, not the host "
          "list. Scope the last actor only and you systematically under-count.",
 "steps": [
  ("py", '''from cybercommons import ir

reached = {
    "alice":          ["repo-core", "repo-infra"],
    "reviewer-agent": ["repo-core"],
    "patch-agent":    ["repo-core", "repo-payments"],
    "deploy-agent":   ["cluster-prod"],
}
s = ir.scope_from_chain(["alice", "patch-agent", "deploy-agent"], reached)
for k, v in s.items():
    print(f"{k:26s} {v}")
'''),
  ("md", "Scoping the last actor gives one cluster. Following the chain gives four "
         "resources including a payments repository. The undercount factor is the "
         "number that belongs in the incident report."),
 ],
 "expect": "Naive scoping finds `cluster-prod` alone; whole-chain scoping finds "
           "four resources, missing three, with an undercount factor of 4.0.",
 "challenge": "Extend the chain by one hop and recompute. Scope grows "
              "super-linearly with delegation depth — which is the operational "
              "argument for the depth limit in B2.6.",
},

"D2.4": {
 "intro": "Containment at machine speed. A human in the containment path is a "
          "control that arrives after the damage, and the ratio is computable.",
 "steps": [
  ("py", '''from cybercommons import ir

for rate in (60, 300, 1200):
    r = ir.containment_race(agent_actions_per_min=rate, human_approval_minutes=8)
    print(f"{rate:>5} actions/min → {r['actions_during_manual_approval']:>8.0f} "
          f"during approval vs {r['actions_during_auto_containment']:>6.0f} automated "
          f"({r['ratio']}×)")
print("\\n" + ir.containment_race(300, 8)["conclusion"])
'''),
  ("md", "Now the mechanism question, because 'contain it' is two very different "
         "actions."),
  ("py", '''MECHANISMS = {
 "kill the process":     ("seconds", "it restarts; the credential still works"),
 "network quarantine":   ("seconds", "stops egress, not local damage"),
 "revoke the identity":  ("seconds", "the agent cannot act anywhere, even if it restarts"),
 "rotate the credential": ("minutes", "correct, but slower and breaks bystanders"),
}
for m, (speed, caveat) in MECHANISMS.items():
    print(f"{m:24s} {speed:8s} {caveat}")
'''),
 ],
 "expect": "The three rates show 60–96× more actions during an eight-minute human "
           "approval than under automated containment, followed by the mechanism "
           "comparison.",
 "challenge": "Time your own revocation path end to end, from decision to the "
              "agent's next call failing. Most teams discover it is minutes, not "
              "seconds, and that the slow part is finding the right console.",
},

"D2.5": {
 "intro": "Replay and forensics. Deterministic replay is the difference between "
          "demonstrating what happened and describing it.",
 "steps": [
  ("py", '''from cybercommons import ir

CONFIGS = {
 "fully instrumented": ir.Replay(prompts=["fix the config"],
                                 tool_results=["file contents…"],
                                 model_version="glm-4.6@2025-11", seed=42),
 "prompts only":       ir.Replay(prompts=["fix the config"]),
 "typical production": ir.Replay(prompts=["fix the config"],
                                 tool_results=["file contents…"]),
 "nothing":            ir.Replay(),
}
for name, r in CONFIGS.items():
    ok, missing = r.replayable()
    print(f"{name:22s} replayable={str(ok):5s}")
    for m in missing:
        print(f"{'':24s}✗ {m}")
'''),
  ("md", "The `typical production` row is the one to sit with: prompts and tool "
         "results are recorded, and the run is still not replayable because the "
         "model version was never pinned. A silent provider-side upgrade "
         "invalidates every reconstruction made after it."),
 ],
 "expect": "Only the fully instrumented configuration is replayable. The typical "
           "production row is missing the pinned model version and the seed.",
 "challenge": "Which of the four fields is cheapest to start recording today? "
              "Model version is usually one line and it is the one that silently "
              "invalidates the others.",
},

"D2.6": {
 "intro": "The post-incident change surface for an agentic incident is wider than "
          "for a software one, because the fix may be a prompt, a manifest, a "
          "model version or a policy — and only one of those goes through change "
          "management.",
 "steps": [
  ("py", '''SURFACES = {
 "application code":  ("yes", "PR, review, CI, deploy"),
 "agent prompt":      ("usually not", "edited in a console, no review"),
 "tool manifest":     ("usually not", "config change, no threat-model diff"),
 "model version":     ("no", "provider-side, may change without notice"),
 "policy (OPA/rego)": ("sometimes", "depends whether it is in git"),
 "approval settings": ("rarely", "a toggle in an admin UI"),
}
print(f"{'change surface':20s}{'in change mgmt?':18s}what happens today")
for k, (managed, how) in SURFACES.items():
    print(f"{k:20s}{managed:18s}{how}")
'''),
  ("md", "Four of six bypass the process that exists. The A1.1 manifest diff is "
         "the cheapest way to bring two of them back in."),
  ("py", '''from cybercommons import planes
W = planes.Tool
before = planes.Manifest("agent", [W("read_file")], rung="L2")
after  = planes.Manifest("agent", [W("read_file"),
                                   W("run_shell", writes=True, scope="tenant",
                                     reversible=False)], rung="L2")
d = planes.diff_manifests(before, after)
print("post-incident manifest change:", d["added"],
      f"blast {d['blast_before']} → {d['blast_after']}")
for p in d["new_problems"]:
    print("  ⚠", p)
'''),
 ],
 "expect": "The table shows four of six surfaces outside change management, and "
           "the manifest diff flags the newly added irreversible ungated tool.",
 "challenge": "Pick the one unmanaged surface that would have prevented your last "
              "incident. Getting it into git is usually a day of work and it is "
              "the highest-leverage day available.",
},

"D2.7": {
 "intro": "Stop authority is the control everyone assumes exists and nobody has "
          "timed.",
 "steps": [
  ("py", '''from cybercommons import ir
print(ir.STOP_AUTHORITY)
'''),
  ("md", "Answer it for a specific agent, with numbers rather than intentions."),
  ("py", '''ANSWERS = {
 "who":        "on-call SRE, no approval needed",
 "mechanism":  "revoke the agent's SPIFFE identity at the gateway",
 "tested":     "quarterly game day — last run 41 days ago",
 "time":       "measured 12s from decision to first failed call",
 "breaks":     "auto-remediation pauses; ticket queue grows ~40/hour",
 "restart":    "security lead, after the eval suite passes on the new build",
}
for k, v in ANSWERS.items():
    print(f"{k:12s} {v}")

r = ir.containment_race(300, human_approval_minutes=0.2, auto_containment_seconds=12)
print(f"\\nat 300 actions/min, a 12s stop costs {r['actions_during_auto_containment']:.0f} "
      f"further actions")
'''),
 ],
 "expect": "The five stop-authority questions print, followed by a worked set of "
           "answers and the cost of a twelve-second stop at 300 actions per minute "
           "(≈60 actions).",
 "challenge": "Run the game day. The measurement is the deliverable — an untested "
              "stop button is a belief, and beliefs do not appear in evidence packs.",
},

"D2.8": {
 "intro": "The regulatory clock starts at awareness. Containing quickly does not "
          "buy reporting time, and teams routinely discover this on day three.",
 "steps": [
  ("py", '''from cybercommons import ir
import time

t0 = time.time()
SCENARIOS = {
 "fast containment, slow reporting": (t0 + 1 * 3600,  t0 + 80 * 3600),
 "slow containment, fast reporting": (t0 + 40 * 3600, t0 + 60 * 3600),
 "both fast":                        (t0 + 2 * 3600,  t0 + 20 * 3600),
}
for name, (contained, reported) in SCENARIOS.items():
    c = ir.clock(t0, contained, reported, deadline_hours=72)
    print(f"{name:34s} contain {c['hours_to_containment']:>5.1f}h  "
          f"report {c['hours_to_report']:>5.1f}h  met={c['met']}  "
          f"margin {c['margin_hours']:+.1f}h")
print("\\n" + ir.clock(t0, t0, t0)["note"])
'''),
  ("md", "The first row contained the incident in an hour and still missed the "
         "deadline. Containment and disclosure are separate workstreams that "
         "compete for the same people, which is why the runbook has to name "
         "different owners for each."),
 ],
 "expect": "The first scenario reports met=False with a negative margin despite "
           "one-hour containment; the other two meet the 72-hour deadline.",
 "challenge": "Which of your obligations has the shortest clock, and does your "
              "runbook start it at awareness or at confirmation? The gap between "
              "those two is often days.",
},
}
