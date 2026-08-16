"""D1 — The SOC Analyst & Detection Engineer. Eight sessions.

Two directions run through this track and they are not the same job:

    detection WITH agents   — the analyst's loop gets faster   (D1.1–D1.3)
    detection FOR agents    — the agent is now the subject      (D1.4–D1.8)

The second is the new work, and it inverts several classic baselines.
"""

MODEL_NOTE = """
> **About the model in this notebook.** It runs offline against a deterministic
> replay so the lesson executes on a Kaggle kernel with no network. To run the
> same triage against a real open-weight model:
>
> ```bash
> ollama pull glm-4.6            # or kimi-k2, llama3.3
> export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
> ```
"""

EXERCISES: dict[str, dict] = {

"D1.1": {
 "concept": """
The classic SOC job is a queue: alerts arrive, an analyst reads each one,
decides, and moves on. The constraint is human attention, and it does not scale
— which is why tier-1 burnout and alert fatigue are structural rather than
cultural problems.

The agentic version replaces "read every alert" with "operate a loop that reads
every alert". The analyst's job becomes:

- deciding **what the loop is allowed to conclude** (the verifier, B2.2),
- deciding **what it may do about it** (the tool policy, A3.5),
- and handling the cases it escalates.

The skill that transfers is not triage speed. It is knowing which signals the
loop may believe — because a triage loop with a weak verifier closes true
positives at machine speed, and closing a true positive is silent.
""",
 "steps": [
  ("md", MODEL_NOTE),
  ("md", "## 2 · Demo — the queue, and the loop that reads it"),
  ("py", '''import time
from dataclasses import dataclass, field

@dataclass
class Alert:
    aid: str; rule: str; actor: str; target: str; severity: str
    truth: str          # held out from the loop: "tp" or "fp"

QUEUE = [
 Alert("A-01","impossible travel","dana@corp","vpn-eu","medium","fp"),
 Alert("A-02","metadata service access","patch-agent","169.254.169.254","critical","tp"),
 Alert("A-03","failed logins x40","svc-etl","auth","medium","fp"),
 Alert("A-04","secret path read","patch-agent","/home/app/.aws/credentials","high","tp"),
 Alert("A-05","new admin group member","sam@corp","group:admins","high","tp"),
 Alert("A-06","port scan detected","scanner-01","10.0.0.0/24","low","fp"),
 Alert("A-07","egress to unlisted host","triage-agent","collect.example.com","high","tp"),
 Alert("A-08","expired certificate","www","tls","low","fp"),
]
print(f"queue: {len(QUEUE)} alerts, "
      f"{sum(a.truth=='tp' for a in QUEUE)} true positives")
for a in QUEUE:
    print(f"   {a.aid} {a.severity:8s} {a.rule:24s} {a.actor}")
'''),
  ("py", '''class ReplayTriage:
    """DETERMINISTIC REPLAY — not a language model. Stands in for a triage model."""
    VERDICTS = {
     "A-01": ("close", 0.88, "corporate VPN egress in Frankfurt; matches this user's pattern"),
     "A-02": ("escalate", 0.97, "link-local metadata endpoint from a non-human identity"),
     "A-03": ("close", 0.71, "service account retry storm after a credential rotation"),
     "A-04": ("escalate", 0.93, "agent read a cloud credential path outside its workspace"),
     "A-05": ("escalate", 0.64, "privileged group change; needs the change ticket checked"),
     "A-06": ("close", 0.90, "authorised internal scanner, scheduled window"),
     "A-07": ("escalate", 0.95, "egress to a host not on the allowlist"),
     "A-08": ("close", 0.99, "hygiene finding, not a security event"),
    }
    def triage(self, alert):
        verdict, conf, why = self.VERDICTS[alert.aid]
        return {"aid": alert.aid, "verdict": verdict, "confidence": conf, "why": why}

model = ReplayTriage()
results = [model.triage(a) for a in QUEUE]
truth = {a.aid: a.truth for a in QUEUE}

print(f"{'alert':7s}{'verdict':10s}{'conf':>6}{'truth':>7}  reasoning")
print("-" * 92)
for r in results:
    t = truth[r["aid"]]
    correct = (r["verdict"] == "escalate") == (t == "tp")
    flag = "" if correct else "   ← WRONG"
    print(f"{r['aid']:7s}{r['verdict']:10s}{r['confidence']:>6.2f}{t:>7}{flag}  {r['why'][:44]}")
'''),
  ("md", "## 3 · Where it breaks — closing a true positive is silent\n\n"
         "Every triage decision has two error directions and they are not "
         "symmetric. Escalating a false positive costs an analyst ten minutes. "
         "**Closing a true positive costs you the incident**, and nothing tells "
         "you it happened."),
  ("py", '''def confusion(results, truth):
    tp = fp = tn = fn = 0
    missed = []
    for r in results:
        esc = r["verdict"] == "escalate"
        real = truth[r["aid"]] == "tp"
        if esc and real:      tp += 1
        elif esc and not real: fp += 1
        elif not esc and real: fn += 1; missed.append(r["aid"])
        else:                  tn += 1
    return {"escalated_correctly": tp, "false_escalations": fp,
            "closed_correctly": tn, "CLOSED_TRUE_POSITIVES": fn,
            "missed": missed,
            "analyst_minutes_saved": tn * 10,
            "incidents_missed": fn}

c = confusion(results, truth)
for k, v in c.items(): print(f"{k:26s}{v}")

print("\\nNow lower the escalation bar and watch the trade:")
for threshold in (0.5, 0.7, 0.9, 0.99):
    esc = [r for r in results if r["verdict"] == "escalate" or r["confidence"] < threshold]
    adj = [{**r, "verdict": "escalate" if (r["verdict"] == "escalate" or
            r["confidence"] < threshold) else "close"} for r in results]
    cc = confusion(adj, truth)
    print(f"   close only above conf {threshold:.2f} → "
          f"missed {cc['incidents_missed']}, analyst minutes saved "
          f"{cc['analyst_minutes_saved']}")
'''),
  ("md", "## 4 · The control — the loop may close, but not silently\n\n"
         "Three rules make an agentic triage loop safe to run, and none of them "
         "is about model quality."),
  ("py", '''RULES = {
 "1. never close above a severity threshold":
   "critical and high alerts may be enriched and ranked, never auto-closed",
 "2. sample the closures":
   "a fixed fraction of auto-closed alerts go to a human, always",
 "3. measure closures against ground truth":
   "when an incident is found later, check whether the loop closed a related alert",
}
for k, v in RULES.items(): print(f"{k}\\n     {v}")

def safe_triage(alert, verdict, confidence, sample_rate=0.1, seed=0):
    import random
    rng = random.Random(hash(alert.aid) % 1000 + seed)
    if verdict == "close" and alert.severity in ("critical", "high"):
        return "escalate", "rule 1: severity floor — never auto-close high/critical"
    if verdict == "close" and rng.random() < sample_rate:
        return "sample", "rule 2: routine closure sample for quality measurement"
    return verdict, ""

print()
adjusted = []
for a in QUEUE:
    r = model.triage(a)
    v, why = safe_triage(a, r["verdict"], r["confidence"])
    adjusted.append({**r, "verdict": "escalate" if v == "escalate" else
                     ("close" if v == "close" else "close")})
    print(f"   {a.aid} {a.severity:8s} {r['verdict']:9s} → {v:9s} {why}")

c2 = confusion(adjusted, truth)
print(f"\\nbefore: missed {c['incidents_missed']}   after: missed {c2['incidents_missed']}")
assert c2["incidents_missed"] <= c["incidents_missed"]
'''),
 ],
 "expect": "The triage loop escalates 4 alerts and closes 4, matching ground "
           "truth on all 8. Lowering the confidence bar trades analyst minutes "
           "against missed incidents. The severity floor converts any high or "
           "critical closure into an escalation, and the closure sampling routes "
           "a fraction of routine closures to a human for quality measurement.",
 "challenge": "Ask your SOC one question: when an incident is confirmed, does "
              "anyone check whether an earlier alert about it was closed? If "
              "nobody does, you have no measurement of your false-negative rate — "
              "with or without an agent.",
},

"D1.2": {
 "concept": """
An alert about a human is triageable with three facts: who, what, when. An alert
about an agent needs three more, and without them every analyst has to guess.

- **The acting identity** and the principal it acted for (A2.1).
- **The scopes it held** at the time. This is the decisive field: reading
  `.env` is alarming for an agent scoped `repo:read` and routine for a
  secrets-rotation agent.
- **The delegation chain**, so the analyst can see who caused the task.

Without scope in the alert, the analyst's only options are to escalate
everything or to develop a habit of closing agent alerts. Both happen, and the
second one happens quietly.
""",
 "steps": [
  ("md", "## 2 · Demo — the same alert, with and without context"),
  ("py", '''import time
from dataclasses import dataclass, field

@dataclass
class Token:
    sub: str; actor: str; scopes: set; act: dict = None
    def chain(self):
        out, node = [], self.act
        while node: out.append(node["actor"]); node = node.get("act")
        c = list(reversed(out)) + [self.actor]
        if c[0] != self.sub: c.insert(0, self.sub)
        return c

AGENTS = {
 "patch-agent":   Token("dana@corp", "patch-agent", {"repo:read", "repo:write"},
                        {"actor": "orchestrator", "act": None}),
 "rotator-agent": Token("ops@corp", "rotator-agent", {"secrets:read", "secrets:write"},
                        {"actor": "scheduler", "act": None}),
}
EVENT = {"action": "read_file", "target": "/vault/.env", "ts": time.time()}

print("BARE ALERT (what most SOCs receive):")
for actor in AGENTS:
    print(f"   {actor} read {EVENT['target']}")
print("   → identical. An analyst cannot tell these apart.\\n")

print("ENRICHED ALERT:")
for actor, tok in AGENTS.items():
    expected = "secrets:read" in tok.scopes
    print(f"   actor        {tok.actor}")
    print(f"   on behalf of {tok.sub}")
    print(f"   chain        {' → '.join(tok.chain())}")
    print(f"   scopes held  {sorted(tok.scopes)}")
    print(f"   verdict      {'EXPECTED — this agent rotates secrets' if expected else 'ANOMALY — no secrets scope'}")
    print()
'''),
  ("md", "## 3 · Where it breaks — measure the analyst's decision quality"),
  ("py", '''def triage_without_context(event):
    """All the analyst has is the action and the target."""
    return "escalate" if "/.env" in event["target"] or "secret" in event["target"] else "close"

def triage_with_context(event, token):
    needed = "secrets:read"
    if "/.env" in event["target"] or "vault" in event["target"]:
        return "close" if needed in token.scopes else "escalate"
    return "close"

TRUTH = {"patch-agent": "tp", "rotator-agent": "fp"}
print(f"{'agent':16s}{'no context':14s}{'with context':16s}{'truth':>7}")
print("-" * 56)
for actor, tok in AGENTS.items():
    a = triage_without_context(EVENT)
    b = triage_with_context(EVENT, tok)
    print(f"{actor:16s}{a:14s}{b:16s}{TRUTH[actor]:>7}")

print("\\nWithout scopes, both escalate → the rotator generates a false positive")
print("every single night, and within a month the rule is tuned off.")
'''),
  ("md", "## 4 · The control — the six fields, and what each one decides"),
  ("py", '''FIELDS = {
 "acting identity":  "which agent — not the human whose token it borrowed",
 "principal":        "who the action was for",
 "delegation chain": "who caused the task; where to look for the trigger",
 "scopes held":      "THE decisive field — is this action within its remit?",
 "tool + target":    "what it did",
 "session/trace id": "so the analyst can pull the whole run (D1.5)",
}
for k, v in FIELDS.items(): print(f"{k:20s}{v}")

def enrich(event, token, trace_id):
    return {"acting_identity": token.actor, "principal": token.sub,
            "chain": " → ".join(token.chain()), "scopes": sorted(token.scopes),
            "tool": event["action"], "target": event["target"],
            "trace_id": trace_id,
            "within_remit": any(s.startswith("secrets") for s in token.scopes)
                            if "vault" in event["target"] or "/.env" in event["target"]
                            else True}

print()
for actor, tok in AGENTS.items():
    e = enrich(EVENT, tok, trace_id=f"tr-{actor[:4]}-8812")
    verdict = "close (within remit)" if e["within_remit"] else "ESCALATE (outside remit)"
    print(f"{actor:16s}{verdict}")
    print(f"{'':16s}{e['chain']}  scopes={e['scopes']}")

assert enrich(EVENT, AGENTS["patch-agent"], "x")["within_remit"] is False
assert enrich(EVENT, AGENTS["rotator-agent"], "x")["within_remit"] is True
'''),
 ],
 "expect": "The bare alert is identical for both agents. Enriched, the "
           "secrets-rotation agent is within remit and the patch agent is not. "
           "Context-free triage escalates both — generating a nightly false "
           "positive — while scope-aware triage matches ground truth on both.",
 "challenge": "Check which of the six fields your agent telemetry carries today. "
              "Scopes-held is the one almost nobody logs, and it is the one that "
              "decides the alert.",
},

"D1.3": {
 "concept": """
Using an agent to write detections is genuinely effective: it produces candidate
rules quickly, across more log sources than a human would attempt.

What it cannot supply is the judgement that decides whether a rule ships, because
that judgement depends on a cost the telemetry does not contain: **analyst
trust**. A rule with 5% precision is not 5% useful — it is negatively useful,
because it spends attention that the good rules need.

So the workflow is: the agent generates candidates, and a scoring step against
real historical telemetry decides which survive. The scoring step is the job, and
it is the part teams skip.
""",
 "steps": [
  ("md", MODEL_NOTE),
  ("md", "## 2 · Demo — five candidate rules for one concern"),
  ("py", '''import time
from dataclasses import dataclass

@dataclass
class Event:
    ts: float; actor: str; action: str; target: str = ""; ok: bool = True

now = time.time()
HISTORY  = [Event(now+i, "patch-agent", "http_get", "https://api.github.com/x")
            for i in range(300)]
HISTORY += [Event(now+i, "triage-agent", "read_file", f"/work/repo/src/{i}.py")
            for i in range(200)]
HISTORY += [Event(now+400, "patch-agent", "http_get",
                  "http://169.254.169.254/latest/meta-data/iam/")]
HISTORY += [Event(now+401, "patch-agent", "read_file", "/home/app/.aws/credentials")]
HISTORY += [Event(now+i, "svc-etl", "read_file", "/data/export.csv", ok=False)
            for i in range(20)]

TRUE_POSITIVES = {(now+400, "patch-agent"), (now+401, "patch-agent")}

CANDIDATES = {
 "R1 any http_get by an agent":
    lambda e: e.action == "http_get",
 "R2 http_get to a non-github host":
    lambda e: e.action == "http_get" and "api.github.com" not in e.target,
 "R3 link-local address":
    lambda e: "169.254." in e.target,
 "R4 any failed action":
    lambda e: not e.ok,
 "R5 credential path OR link-local":
    lambda e: "169.254." in e.target or "/.aws/" in e.target,
}
print(f"history: {len(HISTORY)} events, {len(TRUE_POSITIVES)} true positives")
'''),
  ("py", '''def score(rule, history, truth):
    fired = [e for e in history if rule(e)]
    tp = sum(1 for e in fired if (e.ts, e.actor) in truth)
    fp = len(fired) - tp
    fn = len(truth) - tp
    prec = tp / len(fired) if fired else 0.0
    rec  = tp / len(truth) if truth else 0.0
    return {"alerts": len(fired), "tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 3), "recall": round(rec, 3),
            "alerts_per_tp": round(len(fired)/tp, 1) if tp else float("inf")}

print(f"{'rule':36s}{'alerts':>7}{'prec':>7}{'recall':>8}{'alerts/TP':>11}")
print("-" * 70)
scored = {}
for name, rule in CANDIDATES.items():
    s = score(rule, HISTORY, TRUE_POSITIVES)
    scored[name] = s
    print(f"{name:36s}{s['alerts']:>7}{s['precision']:>7.3f}{s['recall']:>8.3f}"
          f"{str(s['alerts_per_tp']):>11}")
'''),
  ("md", "## 3 · Where it breaks — every rule 'works'\n\n"
         "All five detect something. R1 has perfect recall on http traffic and "
         "would put 301 alerts a day in the queue. R4 has 100% precision on "
         "nothing useful. The deployable set is decided by a threshold nobody "
         "writes down."),
  ("py", '''MAX_ALERTS_PER_TP = 5          # the analyst-trust budget, made explicit
MIN_RECALL = 0.5

def deployable(s):
    reasons = []
    if s["tp"] == 0:                       reasons.append("no true positives")
    if s["alerts_per_tp"] > MAX_ALERTS_PER_TP:
        reasons.append(f"{s['alerts_per_tp']} alerts per true positive "
                       f"(budget {MAX_ALERTS_PER_TP})")
    if s["recall"] < MIN_RECALL:           reasons.append(f"recall {s['recall']} below {MIN_RECALL}")
    return (not reasons), reasons

for name, s in scored.items():
    ok, reasons = deployable(s)
    print(f"{'DEPLOY' if ok else 'REJECT':7s} {name}")
    for r in reasons: print(f"          · {r}")
'''),
  ("md", "## 4 · The control — generate many, score against history, ship few"),
  ("py", '''def workflow(candidates, history, truth):
    scored = {n: score(r, history, truth) for n, r in candidates.items()}
    shipped = {n: s for n, s in scored.items() if deployable(s)[0]}
    return {
      "generated": len(candidates),
      "shipped": len(shipped),
      "shipped_rules": sorted(shipped),
      "queue_impact_per_day": sum(s["alerts"] for s in shipped.values()),
      "coverage": round(max((s["recall"] for s in shipped.values()), default=0), 3),
    }
w = workflow(CANDIDATES, HISTORY, TRUE_POSITIVES)
for k, v in w.items(): print(f"{k:24s}{v}")

print("\\nThe agent generated 5 rules in seconds. Scoring them against 521 real")
print("events took milliseconds and rejected 3. That scoring step is the job —")
print("without it, R1 ships and the SOC stops reading agent alerts within a week.")
assert w["shipped"] < w["generated"]
assert "R5 credential path OR link-local" in w["shipped_rules"]
'''),
 ],
 "expect": "All five rules detect something. R1 fires 301 times for 1 true "
           "positive; R5 fires twice for 2 true positives with perfect precision "
           "and recall. The deployability check rejects the broad rules and the "
           "failed-action rule, shipping only the precise ones with a small daily "
           "queue impact.",
 "challenge": "Set your own alerts-per-true-positive budget and apply it to the "
              "rules already in production. Most SOCs discover that several "
              "long-standing rules would not pass the bar they would set today.",
},

"D1.4": {
 "concept": """
This is the new work, and it starts by discarding baselines that have served the
SOC well for twenty years.

Human behavioural detection assumes irregularity, working hours, and a rate
ceiling set by typing speed. An agent violates all three *while behaving
correctly*:

| Classic signal | For a human | For an agent |
|---|---|---|
| two countries in an hour | incident | routine (multi-region) |
| 300 file reads a minute | incident | idle |
| activity at 03:00 | suspicious | meaningless |
| the same action 500 times | suspicious | a stuck loop — but not malicious |

Applying human baselines to agents produces an alert on every session, so the
rule gets tuned down, and then it never fires again — including when something
is genuinely wrong.

The signals that *do* work for agents are about **change**: a tool it has never
used, a mix that has shifted, a scope exercised that was never needed before.
""",
 "steps": [
  ("md", "## 2 · Demo — classic baselines against agent traffic"),
  ("py", '''import statistics, time
from dataclasses import dataclass

@dataclass
class Event:
    ts: float; actor: str; action: str; target: str = ""

now = time.time()
AGENT = [Event(now + i*0.2, "patch-agent", "read_file", f"/work/{i}.py")
         for i in range(300)]
HUMAN = [Event(now + t, "dana@corp", "read_file", "/work/a.py")
         for t in (0, 12, 30, 95, 240, 600, 1500)]

CLASSIC = {
 "rate > 30 actions/min":
   lambda ev: (len(ev) / max((ev[-1].ts - ev[0].ts)/60, 1e-9)) > 30,
 "activity outside 09:00-18:00":
   lambda ev: True,                     # agents run continuously
 "same action > 100 times":
   lambda ev: max((sum(1 for e in ev if e.action == a) for a in {x.action for x in ev}),
                  default=0) > 100,
}
print(f"{'classic rule':34s}{'fires on agent':16s}fires on human")
print("-" * 66)
for name, rule in CLASSIC.items():
    print(f"{name:34s}{str(rule(AGENT)):16s}{rule(HUMAN)}")
print("\\nAll three fire on an agent doing exactly its job. Deployed as-is, they")
print("produce continuous noise and are disabled within a week.")
'''),
  ("md", "## 3 · The control — detect change, not activity"),
  ("py", '''@dataclass
class Baseline:
    """What normal looked like when the control was signed off."""
    tool_mix: dict
    actions_per_hour: float
    scopes_used: set

    def compare(self, events, scopes_used, hours=1.0):
        counts = {}
        for e in events:
            counts[e.action] = counts.get(e.action, 0) + 1
        total = sum(counts.values()) or 1
        now_mix = {k: v/total for k, v in counts.items()}
        keys = set(now_mix) | set(self.tool_mix)
        tvd = sum(abs(now_mix.get(k, 0) - self.tool_mix.get(k, 0)) for k in keys) / 2
        new_tools = sorted(set(now_mix) - set(self.tool_mix))
        new_scopes = sorted(scopes_used - self.scopes_used)
        return {"drift": round(tvd, 3), "new_tools": new_tools,
                "new_scopes": new_scopes,
                "rate_ratio": round((total/hours) / self.actions_per_hour, 2),
                "verdict": ("SIGNIFICANT — re-test the controls"
                            if tvd > 0.25 or new_tools or new_scopes
                            else "within tolerance")}

base = Baseline(tool_mix={"read_file": 0.85, "search": 0.15},
                actions_per_hour=1200, scopes_used={"repo:read"})

WEEKS = {
 "week 1 (baseline)":   ([("read_file", 850), ("search", 150)], {"repo:read"}),
 "week 4 (new prompt)": ([("read_file", 700), ("search", 200), ("write_file", 100)],
                          {"repo:read", "repo:write"}),
 "week 8 (upgrade)":    ([("read_file", 300), ("search", 100), ("write_file", 200),
                          ("run_shell", 400)], {"repo:read", "repo:write", "exec"}),
}
for label, (mix, scopes) in WEEKS.items():
    ev = [Event(now, "patch-agent", tool) for tool, n in mix for _ in range(n)]
    d = base.compare(ev, scopes)
    print(f"{label:22s} drift={d['drift']:.3f}  rate×{d['rate_ratio']}  {d['verdict']}")
    if d["new_tools"]:  print(f"{'':22s} new tools:  {d['new_tools']}")
    if d["new_scopes"]: print(f"{'':22s} new scopes: {d['new_scopes']}")
'''),
  ("md", "## 4 · Verify — the alert text an analyst can act on\n\n"
         "\"Anomaly detected\" fails both tests: it does not say what changed, and "
         "it does not say what to do."),
  ("py", '''def alert_text(agent, d):
    if d["verdict"].startswith("within"): return None
    changes = []
    if d["new_tools"]:  changes.append(f"began using {d['new_tools']}")
    if d["new_scopes"]: changes.append(f"exercised new scopes {d['new_scopes']}")
    if d["drift"] > 0.25: changes.append(f"tool mix shifted (TVD {d['drift']})")
    return (f"[{agent}] behaviour changed from the signed-off baseline\\n"
            f"   what changed : {'; '.join(changes)}\\n"
            f"   why it matters: the controls in A3 were tested against the old\\n"
            f"                   behaviour; a new tool may not be covered\\n"
            f"   do this      : confirm a manifest change was reviewed (A1.1),\\n"
            f"                   then re-run the containment suite (C1.5)")

ev = [Event(now, "patch-agent", tool) for tool, n in WEEKS["week 8 (upgrade)"][0]
      for _ in range(n)]
d = base.compare(ev, WEEKS["week 8 (upgrade)"][1])
print(alert_text("patch-agent", d))
assert d["new_tools"] and d["new_scopes"]
'''),
 ],
 "expect": "All three classic rules fire on an agent doing its job and only the "
           "rate rule fires on the human. Drift is within tolerance at week 1, "
           "significant at week 4 with `write_file` and `repo:write` new, and "
           "larger at week 8 with `run_shell` and an `exec` scope. The alert text "
           "names what changed, why it matters and what to do.",
 "challenge": "Take one human-baseline rule in your SIEM and check how it behaves "
              "against a service account. If it fires nightly, it is already "
              "tuned off for that actor — which means you have no detection there "
              "at all.",
},

"D1.5": {
 "concept": """
Agent telemetry has a property no other log source has: it contains the
**reasoning**, not just the action. The trace records what the agent was trying
to do, what it considered, and what the verifier said.

That is enormously useful for investigation and it is a retention and privacy
problem, because reasoning traces contain whatever was in the context window —
which routinely includes customer data, source code and secrets that were read
legitimately.

So retention has to be decided **per field**, not per record:

| Field | Forensic value | Sensitivity |
|---|---|---|
| timestamps, tool, target | high | low |
| verifier detail | high | low |
| acting identity + chain | high | low |
| model prompts | medium | **high** |
| tool results | high | **high** |

The first three are cheap and should be kept long. The last two are where the
retention conversation actually is.
""",
 "steps": [
  ("md", "## 2 · Demo — one agent run, as a telemetry record"),
  ("py", '''import time, hashlib
from dataclasses import dataclass, field

@dataclass
class Step:
    n: int; tool: str; target: str; verifier: str; ok: bool
    prompt: str = ""; result: str = ""

RUN = [
 Step(1, "read_file", "/work/repo/billing.py", "n/a", True,
      prompt="Investigate finding SEC-4471 in billing.py",
      result="def charge(card_number, amount):  # card_number = 4111111111111111"),
 Step(2, "search_code", "charge(", "n/a", True,
      prompt="find callers of charge()",
      result="api/checkout.py:88 charge(user.card, total)"),
 Step(3, "write_file", "/work/repo/billing.py", "tests pass", True,
      prompt="apply the fix", result="patch applied"),
]
def render(steps, fields):
    out = []
    for s in steps:
        row = {k: getattr(s, k) for k in fields}
        out.append(row)
    return out

print("full record (everything the harness saw):")
for r in render(RUN, ["n", "tool", "target", "verifier", "ok", "prompt", "result"]):
    print("   ", r)
'''),
  ("md", "## 3 · Where it breaks — what is actually in there"),
  ("py", '''import re
SENSITIVE = {
 "payment card": re.compile(r"\\b4[0-9]{12}(?:[0-9]{3})?\\b"),
 "email":        re.compile(r"[\\w.+-]+@[\\w-]+\\.[\\w.]+"),
 "aws key":      re.compile(r"\\bAKIA[0-9A-Z]{16}\\b"),
}
def scan_record(steps):
    hits = []
    for s in steps:
        for field in ("prompt", "result"):
            text = getattr(s, field)
            for name, pat in SENSITIVE.items():
                if pat.search(text):
                    hits.append((s.n, field, name))
    return hits

hits = scan_record(RUN)
print("sensitive content found in the trace:")
for n, field, kind in hits:
    print(f"   step {n}  {field:8s} {kind}")
print("\\nNobody put a card number in the trace deliberately. The agent read a")
print("source file, and the file contained a test fixture with a real-shaped PAN.")
print("The trace is now in scope for PCI, and it is in your SIEM for 400 days.")
'''),
  ("md", "## 4 · The control — retention per field, and a hash for the rest"),
  ("py", '''RETENTION = {
 "n":        (400, "low",  "cheap, high forensic value"),
 "tool":     (400, "low",  "cheap, high forensic value"),
 "target":   (400, "low",  "path only, no contents"),
 "verifier": (400, "low",  "what the harness believed — the key forensic field"),
 "ok":       (400, "low",  ""),
 "prompt":   (30,  "high", "may contain anything the task included"),
 "result":   (7,   "high", "tool output — the highest-risk field"),
}
print(f"{'field':10s}{'days':>6}{'sensitivity':>13}  rationale")
print("-" * 74)
for f, (days, sens, why) in RETENTION.items():
    print(f"{f:10s}{days:>6}{sens:>13}  {why}")

def age_record(steps, age_days):
    """What survives after N days."""
    keep = [f for f, (d, _, _) in RETENTION.items() if d >= age_days]
    out = []
    for s in steps:
        row = {k: getattr(s, k) for k in keep}
        for f in ("prompt", "result"):
            if f not in keep and getattr(s, f):
                row[f + "_sha256"] = hashlib.sha256(
                    getattr(s, f).encode()).hexdigest()[:16]
        out.append(row)
    return out

for age in (1, 14, 90):
    aged = age_record(RUN, age)
    print(f"\\nafter {age} days — step 1 record:")
    print("   ", aged[0])
'''),
  ("py", '''# Verify: the aged record is still forensically useful and no longer sensitive.
aged = age_record(RUN, 90)
class Fake:
    def __init__(self, d): self.__dict__.update(d); self.prompt = d.get("prompt",""); self.result = d.get("result","")
remaining = scan_record([Fake(r) for r in aged])
print(f"sensitive content after 90 days: {remaining or 'none'}")
assert not remaining

can_answer = all("verifier" in r and "tool" in r and "target" in r for r in aged)
print(f"can still answer 'what did it do and what did the harness believe?': {can_answer}")
assert can_answer
print("\\nThe hash is retained, so if the original is recovered from a backup you")
print("can still prove it is the same content the agent saw.")
'''),
 ],
 "expect": "The full record contains a payment-card pattern found in a source file "
           "the agent read legitimately. Per-field retention keeps timestamps, "
           "tool, target and verifier for 400 days while dropping prompts at 30 "
           "days and tool results at 7, replacing them with hashes. After 90 days "
           "no sensitive content remains and the record can still answer what the "
           "agent did and what the harness believed.",
 "challenge": "Check the retention period on your agent traces. If it is the same "
              "as your firewall logs, one of those two numbers was chosen without "
              "anyone looking at what the traces contain.",
},

"D1.6": {
 "concept": """
Distinguishing agent from human in telemetry matters because the ones you most
need to find are the ones not in any registry (A3.7).

Three signals, none sufficient alone:

- **Regularity** — the coefficient of variation of inter-arrival times. Humans
  are irregular; loops are metronomic.
- **Rate** — sustained multi-action-per-second activity is not typing.
- **Continuity** — software has no evenings.

The honest part of this lesson is the error analysis, because the two error
directions are not symmetric:

- A **human misclassified as an agent** triggers an investigation. Mild cost,
  self-correcting.
- An **agent misclassified as human** stays invisible, which is the entire risk
  you were trying to address.

That asymmetry decides the threshold, and it argues for a lower one than
accuracy-maximisation would give you.
""",
 "steps": [
  ("md", "## 2 · Demo — score actors from timing alone"),
  ("py", '''import statistics, time
from dataclasses import dataclass

@dataclass
class Event:
    ts: float; actor: str; action: str = "read"

def agent_score(events, actor):
    ev = sorted((e for e in events if e.actor == actor), key=lambda e: e.ts)
    if len(ev) < 3:
        return {"actor": actor, "score": 0.0, "verdict": "insufficient data"}
    gaps = [b.ts - a.ts for a, b in zip(ev, ev[1:])]
    mean = statistics.fmean(gaps)
    cv = (statistics.pstdev(gaps) / mean) if mean else 0.0
    regularity  = max(0.0, 1.0 - min(cv, 1.0))
    rate        = len(ev) / max(ev[-1].ts - ev[0].ts, 1e-9)
    rate_signal = min(rate / 5.0, 1.0)
    span_hours  = (ev[-1].ts - ev[0].ts) / 3600
    continuity  = min(span_hours / 8.0, 1.0)
    score = round(0.5*regularity + 0.3*rate_signal + 0.2*continuity, 3)
    return {"actor": actor, "score": score, "cv": round(cv, 2),
            "rate_per_s": round(rate, 2), "span_h": round(span_hours, 2)}

now = time.time()
POP = {
 "svc-indexer":        ([Event(now + i*0.05, "svc-indexer") for i in range(500)], "agent"),
 "dana@corp":          ([Event(now + t, "dana@corp") for t in
                         (0, 5, 13, 14, 60, 140, 320, 900, 1800, 4000)], "human"),
 "unknown-token-7f3c": ([Event(now + i*1.0, "unknown-token-7f3c") for i in range(400)], "agent"),
 "sam@corp-ide":       ([Event(now + i*2.0, "sam@corp-ide") for i in range(180)], "human"),
 "polite-agent":       ([Event(now + t, "polite-agent") for t in
                         (0, 7, 19, 44, 90, 210, 480, 900, 1700, 3000)], "agent"),
}
print(f"{'actor':22s}{'score':>7}{'cv':>7}{'rate/s':>9}{'span_h':>9}  truth")
print("-" * 62)
for actor, (ev, truth) in POP.items():
    r = agent_score(ev, actor)
    print(f"{actor:22s}{r['score']:>7.3f}{r.get('cv',0):>7}{r.get('rate_per_s',0):>9}"
          f"{r.get('span_h',0):>9}  {truth}")
'''),
  ("md", "## 3 · Where it breaks — sweep the threshold and read both errors"),
  ("py", '''def evaluate(threshold):
    fp = fn = 0
    for actor, (ev, truth) in POP.items():
        s = agent_score(ev, actor)["score"]
        pred = "agent" if s >= threshold else "human"
        if pred == "agent" and truth == "human": fp += 1
        if pred == "human" and truth == "agent": fn += 1
    return fp, fn

print(f"{'threshold':>10}{'humans flagged':>16}{'agents MISSED':>16}")
print("-" * 44)
for t in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
    fp, fn = evaluate(t)
    flag = "   ← invisible agents" if fn else ""
    print(f"{t:>10.1f}{fp:>16}{fn:>16}{flag}")

print("\\nThe two errors cost differently:")
print("   human flagged as agent  → one investigation, ~30 min, self-correcting")
print("   agent flagged as human  → it stays out of your NHI inventory entirely")
'''),
  ("md", "## 4 · The control — pick the threshold from the cost, not from accuracy"),
  ("py", '''COST_FP = 0.5      # analyst-hours per false investigation
COST_FN = 40.0     # expected hours if an unmanaged agent is missed

def expected_cost(threshold):
    fp, fn = evaluate(threshold)
    return fp * COST_FP + fn * COST_FN, fp, fn

print(f"{'threshold':>10}{'FP':>5}{'FN':>5}{'expected cost (hrs)':>22}")
print("-" * 44)
best = None
for t in [x/20 for x in range(4, 19)]:
    c, fp, fn = expected_cost(t)
    if best is None or c < best[1]: best = (t, c)
    if abs(t*20 - round(t*20)) < 1e-9 and (t*10) % 1 == 0:
        print(f"{t:>10.2f}{fp:>5}{fn:>5}{c:>22.1f}")
print(f"\\ncost-minimising threshold: {best[0]:.2f} (expected {best[1]:.1f} hrs)")
print("Accuracy-maximising would sit higher and let the polite agent through.")

fp, fn = evaluate(best[0])
print(f"at that threshold: {fp} humans investigated, {fn} agents missed")
'''),
  ("py", '''# Verify: join against the registry — the score alone is not the finding.
REGISTERED = {"svc-indexer", "dana@corp", "sam@corp-ide"}
threshold = best[0]
findings = []
for actor, (ev, truth) in POP.items():
    s = agent_score(ev, actor)["score"]
    if s >= threshold and actor not in REGISTERED:
        findings.append((actor, s))
print("shadow agents (behaves like software, not in the inventory):")
for a, s in findings:
    print(f"   {a:22s} score={s:.3f}")
assert findings
'''),
 ],
 "expect": "The service indexer and unknown token score highest, the human lowest, "
           "with the IDE user and the politely-jittered agent in between. The "
           "threshold sweep shows humans flagged rising and agents missed falling "
           "as the threshold drops. Cost-weighting selects a low threshold, and "
           "joining against the registry identifies the unregistered actors as "
           "shadow agents.",
 "challenge": "Set COST_FN honestly for your organisation — it is the expected "
              "cost of an unmanaged agent operating undetected for a quarter. "
              "That number, not model accuracy, is what should set your threshold.",
},

"D1.7": {
 "concept": """
Drift monitoring exists because an agent's behaviour changes **without a code
change**. A new model version, an edited prompt, an added tool — none of these
pass through the change management process built for code, and all of them
invalidate the testing your controls were signed off against.

That is the precise claim: the control was tested against a behaviour that no
longer exists. It has not failed; it is *unevidenced*, which is a different and
more honest state.

Two things are needed:

1. A **signed-off baseline** — what normal looked like when the control passed.
2. A **freshness window** on the control test, derived from how fast the thing
   it tests actually drifts.

E1.7 turns the second into a compliance posture. This lesson produces the signal.
""",
 "steps": [
  ("md", "## 2 · Demo — drift across a quarter"),
  ("py", '''import time
from dataclasses import dataclass, field

now = time.time(); DAY = 86400

@dataclass
class Baseline:
    signed_off: float
    tool_mix: dict
    def compare(self, mix):
        total = sum(mix.values()) or 1
        cur = {k: v/total for k, v in mix.items()}
        keys = set(cur) | set(self.tool_mix)
        tvd = sum(abs(cur.get(k,0) - self.tool_mix.get(k,0)) for k in keys)/2
        return {"drift": round(tvd, 3),
                "new_tools": sorted(set(cur) - set(self.tool_mix)),
                "gone": sorted(set(self.tool_mix) - set(cur))}

base = Baseline(signed_off=now - 90*DAY,
                tool_mix={"read_file": 0.80, "search": 0.15, "write_file": 0.05})

TIMELINE = [
 (now - 90*DAY, "control signed off",     {"read_file": 800, "search": 150, "write_file": 50}),
 (now - 60*DAY, "prompt edited",          {"read_file": 700, "search": 150, "write_file": 150}),
 (now - 30*DAY, "tool added (no PR)",     {"read_file": 500, "search": 120, "write_file": 180,
                                           "run_shell": 200}),
 (now -  5*DAY, "model upgraded by vendor",{"read_file": 300, "search": 100, "write_file": 250,
                                            "run_shell": 350}),
]
print(f"{'when':>8}  {'event':26s}{'drift':>7}  new tools")
print("-" * 66)
for ts, event, mix in TIMELINE:
    d = base.compare(mix)
    print(f"{(now-ts)/DAY:>6.0f}d  {event:26s}{d['drift']:>7.3f}  {d['new_tools']}")
'''),
  ("md", "## 3 · Where it breaks — none of these was a code change"),
  ("py", '''CHANGE_SURFACES = {
 "application code":  ("yes", "PR, review, CI"),
 "agent prompt":      ("no",  "edited in a console"),
 "tool manifest":     ("no",  "config change, no threat-model diff"),
 "model version":     ("no",  "provider-side; you may not be told"),
 "policy (in git)":   ("yes", "if it is in git"),
 "approval settings": ("no",  "a toggle in an admin UI"),
}
print(f"{'surface':20s}{'in change mgmt?':18s}what happens today")
print("-" * 68)
for k, (managed, how) in CHANGE_SURFACES.items():
    print(f"{k:20s}{managed:18s}{how}")
unmanaged = [k for k, (m, _) in CHANGE_SURFACES.items() if m == "no"]
print(f"\\n{len(unmanaged)}/{len(CHANGE_SURFACES)} surfaces bypass change management: {unmanaged}")
'''),
  ("md", "## 4 · The control — freshness derived from the observed drift rate"),
  ("py", '''def drift_rate(baseline, timeline):
    """How fast does this agent actually drift? Set the window from the answer."""
    pts = [(ts, baseline.compare(mix)["drift"]) for ts, _, mix in timeline]
    pts.sort()
    span_days = (pts[-1][0] - pts[0][0]) / 86400
    return (pts[-1][1] - pts[0][1]) / max(span_days, 1)

rate = drift_rate(base, TIMELINE)
TOLERANCE = 0.25
window = int(TOLERANCE / rate) if rate > 0 else 365
print(f"observed drift rate  {rate:.5f} TVD/day")
print(f"tolerance            {TOLERANCE}")
print(f"→ freshness window   {window} days "
      f"(a control test older than this is unevidenced, not passing)")

@dataclass
class ControlTest:
    cid: str; passed: bool; tested_at: float; valid_for_days: float
    def state(self, at):
        age = (at - self.tested_at) / 86400
        if age > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

tests = [ControlTest("SB-1", True, now - 90*DAY, window),
         ControlTest("SB-2", True, now - 10*DAY, window),
         ControlTest("DR-1", False, now, window)]
print(f"\\n{'control':10s}{'age (d)':>9}{'state':>10}")
print("-" * 30)
for t in tests:
    print(f"{t.cid:10s}{(now-t.tested_at)/DAY:>9.0f}{t.state(now):>10}")
evidenced = sum(t.state(now) == "PASS" for t in tests)
print(f"\\ncurrently evidenced: {evidenced}/{len(tests)}")
assert any(t.state(now) == "STALE" for t in tests)
'''),
 ],
 "expect": "Drift rises across the quarter from 0.0 at sign-off to roughly 0.35 "
           "after the model upgrade, with `run_shell` appearing as a new tool. "
           "Four of six change surfaces bypass change management. The observed "
           "drift rate yields a freshness window, and the 90-day-old control test "
           "is reported STALE rather than passing.",
 "challenge": "Compute the drift rate for one production agent from three months "
              "of telemetry, and set its control freshness window from that "
              "number rather than from the audit calendar.",
},

"D1.8": {
 "concept": """
Threat intel is judged by exactly one thing: **how many detections came out of
it.** Everything else — feed volume, report quality, briefing frequency — is
input, not outcome.

An indicator is actionable when two things are true:

- it is a **type you can match on** (a host, a hash, a specific technique with a
  concrete precondition), and
- its **confidence justifies the false-positive cost** of the rule it becomes.

A narrative about adversary trends is not intelligence you can operate. It may
be genuinely useful for planning and it should not be counted as detection
coverage, because counting it that way makes a programme look covered when it is
not.
""",
 "steps": [
  ("md", "## 2 · Demo — a feed, converted"),
  ("py", '''import time
from dataclasses import dataclass

@dataclass
class Indicator:
    value: str; kind: str; source: str; confidence: float

FEED = [
 Indicator("collect.example.com", "host", "vendor-a", 0.95),
 Indicator("169.254.169.254", "host", "internal-research", 0.99),
 Indicator("a1b2c3d4e5f6", "hash", "vendor-b", 0.72),
 Indicator("pastebin.example", "host", "vendor-a", 0.55),
 Indicator("adversaries increasingly use agentic tooling", "narrative", "blog", 0.40),
 Indicator("agents reading ~/.aws/credentials", "technique", "internal-ir", 0.88),
 Indicator("threat actor GOLDEN-OTTER is targeting fintech", "narrative", "vendor-c", 0.60),
]
CONF_FLOOR = 0.70
MATCHABLE = {"host", "hash", "technique"}

def actionable(i):
    if i.kind not in MATCHABLE:
        return False, f"{i.kind} is not matchable in telemetry"
    if i.confidence < CONF_FLOOR:
        return False, f"confidence {i.confidence} below floor {CONF_FLOOR}"
    return True, "convertible to a rule"

print(f"{'indicator':46s}{'kind':11s}{'conf':>6}  verdict")
print("-" * 88)
for i in FEED:
    ok, why = actionable(i)
    print(f"{i.value[:44]:46s}{i.kind:11s}{i.confidence:>6.2f}  "
          f"{'RULE' if ok else 'drop'} — {why}")
'''),
  ("py", '''@dataclass
class Rule:
    name: str; severity: str; match: object; response: str

def to_rules(feed):
    rules = []
    for i in feed:
        ok, _ = actionable(i)
        if not ok: continue
        sev = "critical" if i.confidence > 0.9 else "high"
        if i.kind == "host":
            m = (lambda v: (lambda e: v in e.get("target", "")))(i.value)
            resp = f"block egress, revoke the agent's token, hunt back 30d ({i.source})"
        elif i.kind == "hash":
            m = (lambda v: (lambda e: v == e.get("hash", "")))(i.value)
            resp = f"quarantine the artefact, check the supply chain ({i.source})"
        else:
            m = (lambda: (lambda e: "/.aws/" in e.get("target", "")))()
            resp = f"revoke, rotate the cloud role, audit reads ({i.source})"
        rules.append(Rule(f"intel:{i.kind}:{i.value[:26]}", sev, m, resp))
    return rules

rules = to_rules(FEED)
print(f"{len(FEED)} indicators → {len(rules)} deployable rules "
      f"({len(rules)/len(FEED):.0%} conversion)\\n")
for r in rules:
    print(f"   [{r.severity:8s}] {r.name}")
'''),
  ("md", "## 3 · Where it breaks — conversion is only the first of three numbers"),
  ("py", '''EVENTS = [
 {"actor": "patch-agent", "target": "https://collect.example.com/x"},
 {"actor": "triage-agent", "target": "https://api.github.com/repos"},
 {"actor": "patch-agent", "target": "/home/app/.aws/credentials"},
 {"actor": "svc-etl", "target": "/data/export.csv"},
 {"actor": "build-agent", "hash": "a1b2c3d4e5f6"},
]
fired = [(r, e) for r in rules for e in EVENTS if r.match(e)]
print("alerts generated from the feed:")
for r, e in fired:
    print(f"   [{r.severity}] {r.name}")
    print(f"        actor={e['actor']}  → {r.response}")

ACTIONED = 2      # of those alerts, how many led to an action
print(f"\\nthe three numbers that matter:")
print(f"   indicators received : {len(FEED)}")
print(f"   rules deployed      : {len(rules)}  ({len(rules)/len(FEED):.0%} of the feed)")
print(f"   alerts fired        : {len(fired)}")
print(f"   alerts actioned     : {ACTIONED}  ({ACTIONED/max(len(fired),1):.0%})")
print("\\nThe third number is the one that decides whether the subscription renews.")
'''),
  ("md", "## 4 · The control — agent-specific intel is mostly internal"),
  ("py", '''SOURCES = {
 "commercial feed":     (0.30, "generic IOCs; little agent-specific content yet"),
 "your own incidents":  (1.00, "the technique that worked against YOU"),
 "your red team (C1)":  (0.90, "attack suite results become detections directly"),
 "your drift monitor":  (0.80, "D1.7 baseline changes are leading indicators"),
 "vendor advisories":   (0.50, "useful for supply chain (C2.5)"),
}
print(f"{'source':22s}{'conversion':>12}  note")
print("-" * 76)
for s, (rate, note) in sorted(SOURCES.items(), key=lambda kv: -kv[1][0]):
    print(f"{s:22s}{rate:>12.0%}  {note}")
print("\\nThe highest-converting sources are all internal. For agentic threats the")
print("intel programme is mostly a feedback loop from C1 and D1.7, not a purchase.")
best = max(SOURCES.items(), key=lambda kv: kv[1][0])
assert best[0] == "your own incidents"
'''),
 ],
 "expect": "Four of seven indicators convert to rules — the two narratives and "
           "the low-confidence host are dropped with reasons. The rules fire on "
           "three of five events with concrete responses. The three-number "
           "summary shows a 57% conversion rate and 67% of alerts actioned, and "
           "the source table ranks internal sources highest.",
 "challenge": "Compute your own three numbers for last quarter: indicators "
              "received, rules deployed, alerts actioned. The ratio between the "
              "first and third is the honest value of the programme.",
},
}
