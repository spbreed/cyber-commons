"""Function E — GRC & CISO Office. E1 risk/control, E2 regulatory, E3 BISO/CISO."""

EXERCISES: dict[str, dict] = {

# ---------------------------------------------------- E1 GRC Practitioner
"E1.1": {
 "intro": "Point-in-time control testing fails for AI because the thing you tested "
          "is not the thing running next week — and none of the changes that break "
          "it are code changes.",
 "steps": [
  ("py", '''from cybercommons import grc
import time

now = time.time()
tests = [
    grc.ControlTest("AC-1", True, "delegation trace captured", tested_at=now - 3 * 86400),
    grc.ControlTest("SB-1", True, "egress denial log",         tested_at=now - 40 * 86400),
    grc.ControlTest("EV-1", True, "audit sample",              tested_at=now - 200 * 86400),
    grc.ControlTest("DR-1", False, "no drift alerting deployed"),
]
required = ["AC-1", "AC-2", "SB-1", "EV-1", "DR-1", "ST-1"]
v = grc.verify_continuously(tests, required, now=now)

print(f"{'control':10s}{'state':14s}age (days)")
for r in v["rows"]:
    print(f"{r['control']:10s}{r['state']:14s}{r['age_days']}")
print(f"\\ncurrently evidenced {v['currently_evidenced']}/{v['required']} "
      f"= {v['coverage']:.0%}")
print(v["note"])
'''),
  ("md", "A point-in-time report would count AC-1, SB-1 and EV-1 as passes and "
         "claim 50%. The honest number is 17%, because two of those tests are "
         "older than their freshness window and two controls have no evidence at "
         "all."),
 ],
 "expect": "AC-1 is PASS, SB-1 and EV-1 are STALE, DR-1 is FAIL, AC-2 and ST-1 "
           "have NO EVIDENCE — coverage 0.167.",
 "challenge": "Set a freshness window per control from how fast the thing it "
              "tests actually changes. Egress policy drifts slowly; a tool "
              "manifest drifts weekly.",
},

"E1.2": {
 "intro": "You cannot govern what you cannot list, and the honest finding of every "
          "first AI inventory is that most of it was already in production.",
 "steps": [
  ("py", '''from cybercommons import grc

inventory = [
    grc.AIAsset("support-summariser", "copilot", owner="support-eng",
                autonomy="L1", data=("customer",)),
    grc.AIAsset("pr-review-agent", "agent", owner="platform-sec",
                autonomy="L2", data=("public",)),
    grc.AIAsset("remediation-agent", "agent", owner="",
                autonomy="L3", data=("customer", "regulated"), external=True),
    grc.AIAsset("marketing-copy-bot", "embedded-feature", owner="",
                autonomy="L1", data=("public",), shadow=True),
    grc.AIAsset("unknown-token-7f3", "agent", owner="",
                autonomy="L2.5", data=("customer",), shadow=True),
]
print(f"{'asset':24s}{'kind':18s}{'autonomy':10s}{'owner':16s}gaps")
for a in inventory:
    print(f"{a.name:24s}{a.kind:18s}{a.autonomy:10s}{a.owner or '—':16s}{len(a.gaps())}")

print("\\ngaps in detail:")
for a in inventory:
    for g in a.gaps():
        print(f"  {a.name:24s} {g}")
'''),
  ("md", "Three of five have no owner. Two were discovered rather than registered. "
         "That distribution is typical, and it is why the inventory is the first "
         "control rather than a documentation exercise."),
 ],
 "expect": "Five assets list with their autonomy and owner; three report gaps, "
           "including two shadow assets and one L3 system with no accountable "
           "owner.",
 "challenge": "Build the same table for your organisation from three sources: the "
              "model registry, expense reports, and egress logs to model provider "
              "domains. The third source finds the ones the first two miss.",
},

"E1.3": {
 "intro": "Risk-tier by what the system can *do*, not by which model it uses. "
          "Tiering on model capability tracks vendor marketing rather than exposure.",
 "steps": [
  ("py", '''from cybercommons import grc

assets = [
    grc.AIAsset("frontier-model chatbot (read-only, public data)", "copilot",
                owner="x", autonomy="L1", data=("public",)),
    grc.AIAsset("small local model with deploy rights", "agent",
                owner="x", autonomy="L3", data=("customer", "regulated"), external=True),
    grc.AIAsset("mid model, gated writes, internal only", "agent",
                owner="x", autonomy="L2", data=("employee",)),
]
for a in assets:
    t = grc.risk_tier(a)
    print(f"{t['tier']:9s} score {t['score']:2d}  {a.name}")
    for w in t["because"]:
        print(f"{'':20s}{w}")
    print()
'''),
  ("md", "The frontier model tiers low; the small local model tiers critical. If "
         "your tiering questionnaire asks 'which model?' before it asks 'what can "
         "it change?', it will produce the opposite answer."),
 ],
 "expect": "The public read-only chatbot tiers low, the small model with deploy "
           "rights and regulated data tiers critical, and the gated internal agent "
           "lands in between — each with its scoring shown.",
 "challenge": "Re-tier your top ten AI use cases with authority and data as the "
              "only inputs. Note which ones move, and be ready to explain the "
              "movement to whoever wrote the original questionnaire.",
},

"E1.4": {
 "intro": "Control mapping runs one way: control → framework. Starting from the "
          "framework produces a checklist that is complete and defends nothing.",
 "steps": [
  ("py", '''from cybercommons import grc

asset = grc.AIAsset("remediation-agent", "agent", owner="platform-sec",
                    autonomy="L3", data=("customer", "regulated"), external=True)
m = grc.map_controls(asset)
print(f"{asset.name} — tier {m['tier']}\\n")
catalogue = {c.cid: c for c in grc.CATALOGUE}
for cid in m["controls"]:
    c = catalogue[cid]
    print(f"  {cid}  [{c.kind:10s}] {c.text}")
print("\\nframeworks satisfied as a by-product:")
for f in m["frameworks_satisfied"]:
    print(f"  · {f}")
'''),
  ("md", "The framework list is an output, not an input. Every entry is there "
         "because a control you decided to operate happens to satisfy it — which "
         "is the only mapping that survives a supervisor asking 'show me'."),
 ],
 "expect": "The critical-tier asset requires all eight catalogue controls, and the "
           "framework list derives from them — NIST AI RMF, ISO 42001, EU AI Act "
           "and others.",
 "challenge": "Try it the other way: start from a framework clause and derive "
              "controls. Notice how quickly you produce controls nobody operates "
              "and that evidence nothing.",
},

"E1.5": {
 "intro": "Evaluation output as audit evidence — the bridge between B2.10 and the "
          "evidence pack. It only works if you present the right number.",
 "steps": [
  ("py", '''from cybercommons import evalkit, grc
import time

truths = {f"q{i}": evalkit.Truth(f"q{i}",
              ["CWE-89", "CWE-78", "CWE-22", "CWE-798"][i % 4],
              f"{['CWE-89','CWE-78','CWE-22','CWE-798'][i % 4]}/{i}.py")
          for i in range(1, 13)}
answers = {q: '{"qid":"%s","cwe":"%s","file":"%s","rationale":"untrusted input reaches the sink"}'
                % (q, t.cwe if int(q[1:]) % 3 else "CWE-89", t.file)
           for q, t in truths.items()}
rep = evalkit.evaluate(answers, truths)
print(rep.render())
'''),
  ("md", "Now the part that decides whether this is evidence or a marketing slide."),
  ("py", '''now = time.time()
test = grc.ControlTest("EV-2", passed=rep.expert_accuracy >= 0.80,
                       evidence=f"expert accuracy {rep.expert_accuracy:.4f} over "
                                f"{rep.total} held-out questions",
                       tested_at=now, valid_for_days=30)
print(f"EV-2 → {test.state(now)}  ({test.evidence})")
print("\\nWhat makes this auditable:")
for line in ["the key was held out — the harness never saw it",
             "the number reported is accuracy, not conformance",
             "the sample size is stated",
             "it expires in 30 days, so it cannot silently age into a claim"]:
    print("  ·", line)
'''),
 ],
 "expect": "The report prints conformance 1.0 alongside a materially lower expert "
           "accuracy, and the control test records the accuracy figure with a "
           "30-day validity window.",
 "challenge": "Take an eval number your organisation has quoted externally. Was it "
              "conformance, pass-rate on a public set, or accuracy against a "
              "held-out key? Only the third is evidence.",
},

"E1.6": {
 "intro": "Operating guardrails constrain how the system runs; outcome guardrails "
          "constrain what results are acceptable. A programme of only the first "
          "passes audit and misses harm.",
 "steps": [
  ("py", '''from cybercommons import grc

RULES = [
    ("All agent egress goes through the gateway", False),
    ("No agent action causes unrecoverable customer data loss", True),
    ("Privileged tools require approval below L3", False),
    ("Automated remediation does not increase customer-facing incidents", True),
    ("Every agent action is logged with the acting identity", False),
    ("Model outputs do not produce disparate outcomes across customer segments", True),
]
for rule, outcome in RULES:
    r = grc.guardrail_kind(rule, outcome)
    print(f"{r['kind']:10s} enforceable_today={str(r['enforceable_today']):5s}  {rule}")
    print(f"{'':10s} risk: {r['risk']}\\n")
'''),
  ("md", "The operating rules are all enforceable today and all narrow. The "
         "outcome rules matter more and each needs a measurement you may not have. "
         "The failure is shipping only the first column and reporting it as "
         "coverage."),
 ],
 "expect": "Three operating guardrails are marked enforceable today; three outcome "
           "guardrails are not, each flagged as needing an agreed measurement.",
 "challenge": "Pick one outcome guardrail and define its measurement precisely "
              "enough that someone could dispute the result. If you cannot, it is "
              "an aspiration, and it should be labelled as one.",
},

"E1.7": {
 "intro": "Continuous control verification. The number that matters is not how "
          "much passed once — it is how much is *currently evidenced*.",
 "steps": [
  ("py", '''from cybercommons import grc
import time

now = time.time()
required = [c.cid for c in grc.CATALOGUE]
tests = [
    grc.ControlTest("AC-1", True,  "act chain in gateway logs",  tested_at=now - 2 * 86400),
    grc.ControlTest("AC-2", True,  "delegation refusal test",    tested_at=now - 9 * 86400),
    grc.ControlTest("SB-1", True,  "egress denial evidence",     tested_at=now - 31 * 86400),
    grc.ControlTest("SB-2", True,  "approval gate screenshot",   tested_at=now - 120 * 86400),
    grc.ControlTest("EV-1", True,  "audit sample, 50 actions",   tested_at=now - 5 * 86400),
    grc.ControlTest("EV-2", True,  "expert accuracy 0.91",       tested_at=now - 12 * 86400),
    grc.ControlTest("DR-1", False, "drift alerting not deployed", tested_at=now),
]
v = grc.verify_continuously(tests, required, now=now)
for r in v["rows"]:
    print(f"{r['control']:8s}{r['state']:14s}{r['age_days']}")
print(f"\\ncoverage {v['coverage']:.1%} — {v['currently_evidenced']}/{v['required']}")
'''),
  ("md", "Two controls quietly aged out of their window. One was never deployed. "
         "One has no evidence at all. A point-in-time report shows 6/8 passing; "
         "the continuous view shows 4/8, and the difference is entirely made of "
         "things nobody did wrong — time simply passed."),
 ],
 "expect": "AC-1, AC-2, EV-1 and EV-2 are PASS; SB-1 and SB-2 are STALE; DR-1 is "
           "FAIL; ST-1 has NO EVIDENCE — coverage 50%.",
 "challenge": "Automate one of these tests so it re-runs weekly and writes its own "
              "`ControlTest`. That single change converts an annual assertion into "
              "a live control.",
},

"E1.8": {
 "intro": "Third-party and model supply-chain risk. Two of the artefacts have no "
          "mature provenance story yet, and saying so is part of the assessment.",
 "steps": [
  ("py", '''from cybercommons import research
P = research.Package

for p in [P("langchain-community", "0.2.1", signed=False, downloads=400_000, age_days=200),
          P("mcp-jira-connector",  "0.0.3", signed=False, downloads=90,      age_days=6),
          P("cryptography",        "42.0.5", signed=True,  downloads=900_000, age_days=300)]:
    r = research.provenance(p)
    print(f"{r['package']:30s}{r['verdict']}")
    for f in r["flags"]:
        print(f"      · {f}")
'''),
  ("md", "Now the two artefacts your existing process does not cover."),
  ("py", '''GAPS = {
 "model weights":   ("Sigstore/in-toto attestation is possible and rare",
                     "no download-count equivalent; 'popular checkpoint' is not provenance"),
 "prompt/tool packs": ("no signing convention at all",
                     "runs inside the agent with the agent's authority"),
 "the model API itself": ("version can change server-side without notice",
                     "your pinned dependency list does not include it"),
}
for artefact, (state, why) in GAPS.items():
    print(f"{artefact}\\n   state: {state}\\n   why it matters: {why}\\n")
'''),
 ],
 "expect": "The mature package is allowed, the new unsigned MCP connector is "
           "blocked or flagged for review, and the three gap areas print with an "
           "honest statement of what does not yet exist.",
 "challenge": "Add one question to your third-party assessment: 'can the model "
              "version change without notifying us?' The answer is usually yes, "
              "and it changes the risk rating.",
},

"E1.9": {
 "intro": "Model and agent lifecycle governance. The lifecycle events that matter "
          "are the ones with no ticket.",
 "steps": [
  ("py", '''from cybercommons import planes, grc, soc
import time

EVENTS = {
 "new agent deployed":        ("ticketed", "caught by existing process"),
 "tool added to manifest":    ("no ticket", "changes blast radius silently"),
 "prompt edited in console":  ("no ticket", "changes behaviour, not code"),
 "provider upgrades model":   ("no ticket", "you may not even be told"),
 "scope widened in IAM":      ("sometimes", "depends on your IAM review"),
 "agent decommissioned":      ("rarely",   "identity often outlives the agent"),
}
for e, (state, why) in EVENTS.items():
    print(f"{e:28s}{state:12s}{why}")
'''),
  ("md", "Two of these are detectable with things already built in this "
         "curriculum: the manifest diff (A1.1) and drift monitoring (D1.7)."),
  ("py", '''W = planes.Tool
d = planes.diff_manifests(
    planes.Manifest("a", [W("read_file")], rung="L2"),
    planes.Manifest("a", [W("read_file"),
                          W("deploy_prod", writes=True, scope="org",
                            reversible=False)], rung="L2"))
print("manifest change detected:", d["added"], f"blast +{d['delta']}")

now = time.time()
base = soc.Baseline({"read_file": 1.0}, actions_per_hour=100)
print("behaviour change detected:",
      base.compare([soc.Event(now, "a", "deploy")] * 10)["verdict"])
'''),
  ("md", "The decommissioning row is the one people miss: a retired agent whose "
         "identity still exists is a standing credential with no owner."),
 ],
 "expect": "The lifecycle table shows four of six events untracked. The manifest "
           "diff detects the added tool with its blast-radius delta, and the "
           "baseline comparison reports significant drift.",
 "challenge": "Query your identity provider for non-human identities with no "
              "authentication in 90 days. Each one is a decommissioning that never "
              "finished.",
},

# --------------------------------------- E2 Regulatory & Compliance Lead
"E2.1": {
 "intro": "The regulatory map for AI has three layers, and confusing them is how "
          "programmes end up over-invested in one and blind to another.",
 "steps": [
  ("py", '''LAYERS = {
 "horizontal AI regulation": (
    ["EU AI Act", "national AI acts in progress"],
    "applies because it is AI, regardless of sector"),
 "sector overlays": (
    ["DORA (financial)", "HIPAA (health)", "PCI DSS (payments)", "NIS2 (critical infra)"],
    "applies because of what you do — and usually predates AI entirely"),
 "cross-cutting": (
    ["GDPR / privacy law", "sectoral incident-reporting rules", "consumer protection"],
    "applies to the data and the outcome, not the technology"),
}
for layer, (examples, why) in LAYERS.items():
    print(f"{layer}\\n   {', '.join(examples)}\\n   {why}\\n")
print("The common mistake: treating layer 1 as the whole map. For most")
print("organisations layers 2 and 3 bite first, because they already apply.")
'''),
  ("md", "Now locate one system on the map — which is the only form of this "
         "exercise that produces a decision."),
  ("py", '''from cybercommons import grc
asset = grc.AIAsset("claims-triage-agent", "agent", owner="ops",
                    autonomy="L2.5", data=("customer", "regulated"), external=False)
m = grc.map_controls(asset)
print(f"{asset.name} — tier {m['tier']}")
print("frameworks reached by the controls it needs:")
for f in m["frameworks_satisfied"]:
    print("  ·", f)
'''),
 ],
 "expect": "The three layers print with examples and applicability, and the "
           "claims-triage agent tiers high or critical with its framework list "
           "derived from required controls.",
 "challenge": "For your highest-tier AI system, list every obligation from all "
              "three layers. The sector overlay usually has the shortest deadline "
              "and the least AI-specific guidance.",
},

"E2.2": {
 "intro": "Horizontal AI regulation is mostly about *documented process and human "
          "oversight*, which maps onto controls you can already build.",
 "steps": [
  ("py", '''from cybercommons import grc

catalogue = {c.cid: c for c in grc.CATALOGUE}
AI_ACT_THEMES = {
 "risk management system":   ["AC-1", "SB-2"],
 "record-keeping (Art.12)":  ["EV-1"],
 "human oversight (Art.14)": ["SB-2", "ST-1"],
 "accuracy & robustness":    ["EV-2", "DR-1"],
}
for theme, cids in AI_ACT_THEMES.items():
    print(theme)
    for cid in cids:
        c = catalogue[cid]
        print(f"   {cid}  {c.text}")
        print(f"        evidence: a passing, in-window ControlTest")
    print()
'''),
  ("md", "Every theme resolves to a control that produces machine-generated "
         "evidence. That is the practical answer to 'how do we comply' — not a "
         "policy document, a control whose output is the artefact."),
  ("py", '''import time
now = time.time()
tests = [grc.ControlTest(c, True, "automated", tested_at=now - 3 * 86400)
         for c in ("AC-1", "SB-2", "EV-1")]
print(grc.verify_continuously(tests, ["AC-1", "SB-2", "EV-1", "EV-2", "DR-1", "ST-1"],
                              now=now))
'''),
 ],
 "expect": "Four themes map onto named controls, and the coverage check reports "
           "three evidenced out of six required (50%).",
 "challenge": "Human oversight (Art.14) is the clause most often satisfied with a "
              "sentence. Write what would actually demonstrate it for an L2.5 "
              "agent — SB-2 and ST-1 together are a start.",
},

"E2.3": {
 "intro": "Voluntary frameworks make a better spine than regulation, because they "
          "are written as controls rather than as obligations and they change more "
          "slowly than the law.",
 "steps": [
  ("py", '''from cybercommons import grc

by_framework = {}
for c in grc.CATALOGUE:
    for f in c.frameworks:
        by_framework.setdefault(f.split(":")[0], []).append(c.cid)

for fw, cids in sorted(by_framework.items()):
    print(f"{fw:18s} {sorted(set(cids))}")
'''),
  ("md", "Build the control set once against the framework with the best coverage, "
         "then map outward. Building separately per regulation produces duplicated "
         "controls that evidence the same thing twice and drift apart."),
  ("py", '''spine = "NIST AI RMF"
covered = sorted(set(by_framework.get(spine, [])))
allc = [c.cid for c in grc.CATALOGUE]
print(f"spine: {spine} covers {len(covered)}/{len(allc)} controls")
print("not covered by the spine:", sorted(set(allc) - set(covered)))
print("\\nThose remaining controls need a second source — usually ISO 42001")
print("for management-system requirements and the sector overlay for the rest.")
'''),
 ],
 "expect": "Controls group under NIST AI RMF, ISO 42001, ISO 27001, EU AI Act and "
           "DORA, and the spine analysis names which controls the chosen spine "
           "does not reach.",
 "challenge": "Pick your spine and justify it in one sentence to an auditor. "
              "'It has the best coverage of the controls we actually operate' is a "
              "much stronger answer than 'it is the one our regulator mentioned'.",
},

"E2.4": {
 "intro": "Sector overlays usually bite first, because they already applied before "
          "anyone deployed an agent — and their operational-resilience clauses "
          "cover autonomous action without ever naming it.",
 "steps": [
  ("py", '''OVERLAYS = {
 "DORA (financial)": [
    ("ICT third-party risk", "your model provider is an ICT third party"),
    ("incident reporting",   "clocks measured in hours, not days"),
    ("exit strategy",        "can you stop using this model provider?"),
    ("resilience testing",   "your stop mechanism is in scope")],
 "HIPAA (health)": [
    ("minimum necessary",    "the agent's context window is a disclosure"),
    ("audit controls",       "the acting identity must be recorded")],
 "PCI DSS (payments)": [
    ("scope containment",    "an agent with CDE access expands scope"),
    ("access control",       "non-human identities need the same rigour")],
}
for fw, clauses in OVERLAYS.items():
    print(fw)
    for clause, why in clauses:
        print(f"   {clause:24s} {why}")
    print()
'''),
  ("md", "Note the DORA exit-strategy clause and the PCI scope clause. Both are "
         "pre-existing obligations that an agent deployment can breach without "
         "anyone filing an AI-related change."),
  ("py", '''from cybercommons import ir
import time
t0 = time.time()
print("DORA-style short clock:")
print(ir.clock(t0, t0 + 2 * 3600, t0 + 20 * 3600, deadline_hours=24))
'''),
 ],
 "expect": "Three overlays print with their agent-relevant clauses, and the "
           "24-hour clock example reports met=True with a four-hour margin.",
 "challenge": "Find the clause in your sector overlay that already covers "
              "autonomous action without naming AI. Citing it is more persuasive "
              "internally than any new AI policy.",
},

"E2.5": {
 "intro": "Privacy and data protection for agents turns on one under-discussed "
          "fact: the context window is a disclosure, and the trace is a record.",
 "steps": [
  ("py", '''from cybercommons import loop, research

trace = loop.run(loop.FakeModel(["read customer record 4471",
                                 "summarise: J. Okonkwo, acct 4471, balance …"]),
                 loop.unit_test(lambda s: s.startswith("summarise"), "produced a summary"),
                 max_steps=3)
print(trace.table())
print("\\nThis trace now contains personal data. Three obligations attach:")
for o in ["lawful basis for the processing that put it there",
          "retention limit on the trace itself, not just the source system",
          "the right to erasure reaches into traces, backups and eval sets"]:
    print("  ·", o)
'''),
  ("md", "The erasure obligation is the one that surprises teams: a customer "
         "record deleted from the database can survive in an agent trace, an eval "
         "corpus and a fine-tuning set."),
  ("py", '''corpus = [f"record {i}" for i in range(500)]
erase = {"record 4471"} & set(corpus)
print(research.poison_rate(corpus, {"record 471"}))
print("\\nTo honour erasure you must be able to LOCATE the record. Content")
print("hashes make that possible:", research.content_hash("record 471"))
'''),
 ],
 "expect": "The trace prints containing simulated personal data, the three "
           "obligations list, and the corpus check shows how a single record is "
           "located by hash.",
 "challenge": "Can you delete one customer's data from your agent traces today? "
              "Time-box the investigation to an hour — the answer usually arrives "
              "in ten minutes and it is usually no.",
},

"E2.6": {
 "intro": "Incident and disclosure obligations, applied to an incident whose actor "
          "was an agent. The clock and the attribution interact badly.",
 "steps": [
  ("py", '''from cybercommons import ir
import time

t0 = time.time()
tl = ir.Timeline()
tl.add(t0,      "alice", "alice",       "login")
tl.add(t0 + 40, "alice", "patch-agent", "read_file", "/work/customer_export.csv")
tl.add(t0 + 41, "alice", "patch-agent", "http_get",  "https://collect.example.com/")
r = ir.reconstruct(tl)
print("attribution:", r["attribution"])
print("hidden actors:", r["hidden_actors"])
'''),
  ("md", "Awareness starts when you know a reportable event *may* have occurred — "
         "not when you have finished attributing it. Broken attribution therefore "
         "consumes the clock rather than pausing it."),
  ("py", '''SCENARIOS = {
 "attribution sound, report at 20h":   (t0 + 4 * 3600,  t0 + 20 * 3600),
 "attribution broken, 3 days to scope": (t0 + 70 * 3600, t0 + 76 * 3600),
}
for name, (contained, reported) in SCENARIOS.items():
    c = ir.clock(t0, contained, reported, deadline_hours=72)
    print(f"{name:38s} report {c['hours_to_report']:>5.1f}h met={c['met']} "
          f"margin {c['margin_hours']:+.1f}h")
'''),
 ],
 "expect": "Attribution is reported BROKEN with `patch-agent` hidden. The sound "
           "scenario meets the 72-hour deadline with a wide margin; the broken one "
           "misses it.",
 "challenge": "Draft the disclosure sentence you would send when you know an agent "
              "acted but cannot yet say which one. Write it now, not during the "
              "incident.",
},

"E2.7": {
 "intro": "Documentation that survives supervision is documentation that points at "
          "machine-generated evidence rather than restating intent.",
 "steps": [
  ("py", '''WEAK = """
Our AI systems are subject to appropriate oversight and controls.
Access is granted on a least-privilege basis and reviewed periodically.
Agents are monitored for anomalous behaviour.
"""
STRONG = """
Agent identities are distinct from human identities (AC-1). Evidence: gateway
logs containing an `act` chain for every action; sampled monthly, last test
2026-08-13, valid 30d.

Delegated authority narrows at every hop (AC-2). Evidence: the exchange refuses
widening; regression suite case IDN-01/IDN-04, run on every release.

Autonomy above L2 requires approval for privileged tools (SB-2). Evidence:
tool policy in git; denial log for the last 90 days attached.
"""
print("WEAK\\n", WEAK)
print("STRONG\\n", STRONG)
print("The difference is not length. Every STRONG sentence names a control,")
print("an artefact, and a date — three things a supervisor can request.")
'''),
  ("py", '''from cybercommons import grc
import time
now = time.time()
tests = [grc.ControlTest("AC-1", True, "gateway act-chain sample", tested_at=now - 3 * 86400),
         grc.ControlTest("AC-2", True, "IDN-01/IDN-04 regression", tested_at=now - 1 * 86400),
         grc.ControlTest("SB-2", True, "90-day denial log",        tested_at=now - 8 * 86400)]
v = grc.verify_continuously(tests, ["AC-1", "AC-2", "SB-2"], now=now)
print(f"\\nevidence currently valid: {v['coverage']:.0%}")
for r in v["rows"]:
    print(f"  {r['control']} {r['state']} (age {r['age_days']}d)")
'''),
 ],
 "expect": "The weak and strong versions print, and all three cited controls "
           "verify as PASS within their windows — 100% coverage.",
 "challenge": "Rewrite one paragraph of your AI policy in the STRONG shape. If a "
              "sentence cannot name an artefact, it is intent and should be "
              "labelled as such rather than deleted.",
},

"E2.8": {
 "intro": "Auditability of autonomous action reduces to one question: can you "
          "produce, for any single action, who caused it and what they were "
          "allowed to do?",
 "steps": [
  ("py", '''from cybercommons import identity, ir

alice = identity.mint("alice")
patch = identity.exchange(alice, "patch-agent", {"repo:read", "repo:write"})

print("auditable record of one action:")
print(f"   action        write_file /etc/app.conf")
print(f"   acting id     {patch.actor}")
print(f"   on behalf of  {patch.sub}")
print(f"   chain         {' → '.join(patch.chain())}")
print(f"   scopes held   {sorted(patch.scopes)}")
print(f"   token fp      {patch.fingerprint()}")
'''),
  ("md", "Now the same action under impersonation — the record an auditor would "
         "actually receive from most deployments today."),
  ("py", '''bad = identity.impersonate("alice", "patch-agent", {"repo:write"})
print(f"   acting id     {bad.actor}   ← the human")
print(f"   chain         {' → '.join(bad.chain())}")
print("   the agent does not appear. The record is complete, consistent, and false.")

ok, missing = ir.Replay(["prompt"], ["tool result"], "glm-4.6@2025-11", 42).replayable()
print(f"\\nreplayable: {ok}  (auditability = attribution + replay, not one of them)")
'''),
 ],
 "expect": "The delegated record names the acting identity, the principal, the "
           "chain, the scopes and a fingerprint. The impersonated record shows "
           "only alice, and the replay check passes for a fully instrumented run.",
 "challenge": "Pick one production agent action from last week and try to produce "
              "this record. Whatever field you cannot fill is your auditability "
              "gap, stated precisely.",
},

"E2.9": {
 "intro": "Regulator and auditor conversations go well when you bring the number "
          "that is weakest and explain it, and badly when you bring the number that "
          "is strongest and let them find the other one.",
 "steps": [
  ("py", '''from cybercommons import evalkit, grc
import time

truths = {f"q{i}": evalkit.Truth(f"q{i}", "CWE-89" if i % 2 else "CWE-78",
                                 f"{'CWE-89' if i % 2 else 'CWE-78'}/{i}.py")
          for i in range(1, 11)}
answers = {q: '{"qid":"%s","cwe":"CWE-89","file":"%s","rationale":"concatenated input"}'
                % (q, t.file) for q, t in truths.items()}
rep = evalkit.evaluate(answers, truths)
print(rep.render())
'''),
  ("md", "Two numbers, one story. Bringing conformance alone is how a supervisor "
         "concludes you do not understand your own evaluation."),
  ("py", '''now = time.time()
tests = [grc.ControlTest("AC-1", True, "act chains", tested_at=now - 4 * 86400),
         grc.ControlTest("SB-1", True, "egress log", tested_at=now - 45 * 86400)]
v = grc.verify_continuously(tests, ["AC-1", "AC-2", "SB-1", "EV-2"], now=now)

print("\\nWhat to say:")
print(f"  · conformance {rep.conformance:.0%} — structural, and not a quality claim")
print(f"  · expert accuracy {rep.expert_accuracy:.0%} against a held-out key")
print(f"  · control coverage {v['coverage']:.0%} currently evidenced; "
      f"SB-1 is stale at 45 days and is being re-tested")
print("  · here is the control we have not deployed, and the date we will")
'''),
 ],
 "expect": "Conformance is 1.0 while expert accuracy is around 0.5, and the "
           "coverage check reports 25% with SB-1 stale — the exact combination "
           "you would disclose.",
 "challenge": "Rehearse the sentence naming your weakest control out loud. If it "
              "is uncomfortable, that discomfort is the reason to say it first "
              "rather than be asked.",
},

# ------------------------------ E3 BISO, Risk Communicator & CISO Office
"E3.1": {
 "intro": "Translating agentic risk upward means dropping every mechanism and "
          "keeping exposure, likelihood and the decision being requested.",
 "steps": [
  ("py", '''from cybercommons import grc, planes, redteam, sandbox
W = planes.Tool

agent = planes.Manifest("remediation-agent", [
    W("read_file"),
    W("write_file",  writes=True, scope="project"),
    W("deploy_prod", writes=True, scope="org", reversible=False)], rung="L2.5")
blast = agent.blast_radius()["total"]

def target(a):
    box = sandbox.default_sandbox()
    if a.surface != redteam.CONTAINMENT:
        return True, "no control on this surface"
    tool = ("http_get" if a.payload.startswith("http")
            else "read_file" if a.payload.startswith("/") else a.payload)
    d = box.call(tool, a.payload if tool != a.payload else "")
    return d.allowed, d.reason
asr = redteam.run_campaign(target, "prod").asr()

print(grc.board_translation(tier="critical", blast_radius=blast,
                            asr=asr, coverage=0.5))
'''),
  ("md", "No tool names, no CWEs, no autonomy jargon. Three facts and a decision. "
         "Note the last line: the alternative to funding is *accepting in "
         "writing*, which is a real option and makes the ask credible."),
 ],
 "expect": "A four-line board statement giving the exposure as a blast-radius "
           "number, likelihood from the measured attack success rate, assurance as "
           "control coverage, and an explicit decision request.",
 "challenge": "Write the same four lines for your highest-tier system. If you "
              "cannot fill the likelihood line with a measurement, that is the "
              "first thing to fund.",
},

"E3.2": {
 "intro": "Govern autonomy, not tools. A tool-approval process scales linearly "
          "with a list that grows weekly; an autonomy-tier policy does not.",
 "steps": [
  ("py", '''from cybercommons import planes

print(planes.describe_ladder())
print("\\nPolicy expressed per rung rather than per tool:\\n")
POLICY = {
 "L1":   "self-service. Register it. No further review.",
 "L2":   "register + named owner. Approval gate on every writer, enforced by policy.",
 "L2.5": "risk tier + blast-radius budget + drift monitoring + tested stop.",
 "L3":   "all of L2.5, plus held-out evaluation per release and board-level sign-off.",
}
for rung, rule in POLICY.items():
    print(f"  {rung:5s} {rule}")
'''),
  ("md", "Now test a request against it — which takes seconds and needs no tool "
         "committee."),
  ("py", '''W = planes.Tool
request = planes.Manifest("new-triage-agent", [
    W("read_file"),
    W("post_comment", writes=True, scope="project"),
    W("close_ticket", writes=True, scope="project")], rung="L2")
print("requested rung:", request.rung)
problems = request.rung_check()
print("decision:", "approve at L2" if not problems else "refuse or re-tier —")
for p in problems:
    print("   ", p)
print(f"blast radius {request.blast_radius()['total']} "
      f"(budget for L2.5 in this example: 20)")
'''),
 ],
 "expect": "The ladder and per-rung policy print, and the request is refused at L2 "
           "because both writers are ungated — with its blast radius shown against "
           "a budget.",
 "challenge": "Write your own per-rung policy in four lines. If L1 needs approval, "
              "nobody will register anything and your inventory dies.",
},

"E3.3": {
 "intro": "Sequencing decides whether the programme compounds or thrashes. There "
          "is a right order and it is not the exciting one.",
 "steps": [
  ("py", '''from cybercommons import grc
print(grc.SEQUENCING)
'''),
  ("md", "Test the claim in the last line by trying the popular order."),
  ("py", '''import time
now = time.time()
# the popular order: evaluate first, because it demos well
tests = [grc.ControlTest("EV-2", True, "expert accuracy 0.94", tested_at=now)]
v = grc.verify_continuously(tests, ["AC-1", "AC-2", "SB-1", "EV-1", "EV-2", "ST-1"],
                            now=now)
print(f"eval-first coverage: {v['coverage']:.0%}")
print("you can measure the agent precisely and cannot switch it off:")
for r in v["rows"]:
    if r["state"] == "NO EVIDENCE":
        print(f"   missing {r['control']}")
'''),
 ],
 "expect": "The sequencing guidance prints, and the eval-first ordering reports "
           "~17% coverage with identity, containment, evidence and stop authority "
           "all missing.",
 "challenge": "Locate your programme on the six steps. Most are somewhere between "
              "2 and 3 while reporting on 5, which is exactly the gap this "
              "sequence is designed to prevent.",
},

"E3.4": {
 "intro": "Org design and ownership. The failures happen in the seams, so the "
          "question is which seams you have chosen to have.",
 "steps": [
  ("py", '''SEAMS = {
 ("AppSec", "Platform"):  "who owns the agent's sandbox? Usually neither, in practice.",
 ("Identity", "SecOps"):  "who revokes a non-human identity at 3am?",
 ("GRC", "Engineering"):  "who decides an autonomy rung — the tier or the roadmap?",
 ("SOC", "Data"):         "who retains agent traces, and for how long?",
 ("CISO office", "Legal"): "who starts the regulatory clock?",
}
for (a, b), q in SEAMS.items():
    print(f"{a:12s} ↔ {b:12s} {q}")
print("\\nEvery unanswered row becomes an incident finding later, phrased as")
print("'unclear ownership' — which is a decision nobody made, not a surprise.")
'''),
  ("py", '''from cybercommons import grc
assets = [
    grc.AIAsset("remediation-agent", "agent", owner="", autonomy="L3",
                data=("customer",), external=True),
    grc.AIAsset("pr-review-agent", "agent", owner="platform-sec", autonomy="L2"),
]
for a in assets:
    print(f"{a.name:22s} tier {grc.risk_tier(a)['tier']:9s} gaps {a.gaps() or 'none'}")
'''),
 ],
 "expect": "Five ownership seams print as questions, and the unowned L3 asset "
           "reports gaps while the owned L2 one does not.",
 "challenge": "Put a name against each of the five seams. Any seam where two "
              "people both say 'them' is the one that will fail first.",
},

"E3.5": {
 "intro": "The metrics that matter at CISO level are few, and none of them is a "
          "count of alerts.",
 "steps": [
  ("py", '''from cybercommons import grc, planes, redteam, sandbox
W = planes.Tool

# 1. exposure — how much unreviewed action exists
fleet = [planes.Manifest("a1", [W("read_file"), W("write_file", writes=True,
                                                  scope="project")], rung="L2.5"),
         planes.Manifest("a2", [W("deploy_prod", writes=True, scope="org",
                                  reversible=False)], rung="L2.5")]
exposure = sum(m.blast_radius()["total"] for m in fleet)

# 2. likelihood — measured, not asserted
def t(a):
    box = sandbox.default_sandbox()
    if a.surface != redteam.CONTAINMENT:
        return False, "n/a"
    tool = ("http_get" if a.payload.startswith("http")
            else "read_file" if a.payload.startswith("/") else a.payload)
    d = box.call(tool, a.payload if tool != a.payload else "")
    return d.allowed, d.reason
asr = redteam.run_campaign(t, "fleet").asr(redteam.CONTAINMENT)

# 3. assurance — how much is currently evidenced
import time
now = time.time()
tests = [grc.ControlTest(c, True, "auto", tested_at=now - 5 * 86400)
         for c in ("AC-1", "AC-2", "SB-1", "EV-1")]
cov = grc.verify_continuously(tests, [c.cid for c in grc.CATALOGUE], now=now)["coverage"]

print(f"exposure   fleet blast radius        {exposure}")
print(f"likelihood red-team ASR (containment) {asr:.0%}")
print(f"assurance  controls evidenced        {cov:.0%}")
print(f"coverage   agents in inventory       (report honestly — usually < 100%)")
print(f"speed      measured time-to-stop     seconds, from a game day")
'''),
  ("md", "Five numbers. Each moves when someone does work, and each degrades on "
         "its own if nobody does — which is the property that makes a metric worth "
         "reporting monthly."),
 ],
 "expect": "Exposure prints as a summed blast radius, containment ASR as 0%, and "
           "control coverage as 50%.",
 "challenge": "Which of the five can you produce today without a project? Start "
              "reporting that one monthly and let the missing ones become "
              "conspicuous.",
},

"E3.6": {
 "intro": "Saying no is cheap and rarely correct. Saying yes with conditions is "
          "the actual job, and the conditions have to be testable.",
 "steps": [
  ("py", '''from cybercommons import planes, grc
W = planes.Tool

ask = planes.Manifest("customer-refund-agent", [
    W("read_file"),
    W("issue_refund", writes=True, scope="tenant", reversible=False)], rung="L2.5")
asset = grc.AIAsset("customer-refund-agent", "agent", owner="payments-eng",
                    autonomy="L2.5", data=("customer", "regulated"))

print("request:", ask.agent, "at", ask.rung)
print("tier:", grc.risk_tier(asset)["tier"],
      " blast:", ask.blast_radius()["total"])
for p in ask.rung_check():
    print("  ⚠", p)

print("\\nyes, with conditions:")
CONDITIONS = [
 ("refund cap per action, enforced in the tool", "bounds the irreversible step"),
 ("approval gate above the cap",                 "SB-2, testable in the policy file"),
 ("act chain on every refund",                   "AC-1/EV-1, testable in the logs"),
 ("tested stop, measured in seconds",            "ST-1, testable at a game day"),
 ("re-tier if the tool list changes",            "A1.1 manifest diff in CI"),
]
for cond, why in CONDITIONS:
    print(f"   · {cond:44s} {why}")
'''),
  ("md", "Now show the condition working, because a condition you cannot "
         "demonstrate is a condition nobody will meet."),
  ("py", '''gated = planes.Manifest("customer-refund-agent", ask.tools,
                        approval_required={"issue_refund"}, rung="L2.5")
print("blast radius with the gate:", gated.blast_radius()["total"],
      "  issues:", gated.rung_check() or "none")
'''),
 ],
 "expect": "The request tiers critical with a flagged irreversible ungated tool. "
           "Five testable conditions print, and applying the approval gate drops "
           "the blast radius to 0 with no remaining issues.",
 "challenge": "Take a request you refused in the last year and write the five "
              "conditions that would have made it a yes. Send them to the team "
              "that asked.",
},

"E3.7": {
 "intro": "Building the capability is mostly a sequencing and hiring question, and "
          "the honest version accounts for what you can evidence rather than what "
          "you can present.",
 "steps": [
  ("py", '''from cybercommons import grc
import time

now = time.time()
QUARTERS = {
 "Q1 — inventory + identity": ["AC-1", "AC-2"],
 "Q2 — containment":          ["AC-1", "AC-2", "SB-1", "SB-2"],
 "Q3 — evidence + eval":      ["AC-1", "AC-2", "SB-1", "SB-2", "EV-1", "EV-2"],
 "Q4 — continuous + stop":    [c.cid for c in grc.CATALOGUE],
}
required = [c.cid for c in grc.CATALOGUE]
for q, done in QUARTERS.items():
    tests = [grc.ControlTest(c, True, "automated", tested_at=now - 5 * 86400)
             for c in done]
    v = grc.verify_continuously(tests, required, now=now)
    print(f"{q:30s} coverage {v['coverage']:>5.0%}")
'''),
  ("md", "The curve is deliberately unglamorous in Q1 and Q2. Programmes that "
         "invert it — eval and dashboards first — report high numbers early and "
         "then spend a year discovering they cannot switch anything off."),
  ("py", '''ROLES = {
 "harness engineer": "owns the loop, the verifier, the eval — B2",
 "identity engineer": "owns agent identity and delegation — A2",
 "detection engineer": "owns agent telemetry and drift — D1",
 "GRC practitioner": "owns tiering, evidence, continuous verification — E1",
}
print()
for r, what in ROLES.items():
    print(f"  {r:20s} {what}")
print("\\nThe first hire is usually the harness engineer. The first hire that")
print("unblocks everyone else is the identity engineer.")
'''),
 ],
 "expect": "Coverage climbs 25% → 50% → 75% → 100% across the four quarters, "
           "followed by the four roles and their track ownership.",
 "challenge": "Map your existing team onto those four roles. Most organisations "
              "have three of them under other names and are missing the identity "
              "one entirely.",
},

"E3.8": {
 "intro": "Resilience over perfection. You will not prevent every agentic failure; "
          "the programme is judged on how quickly you notice, stop and recover.",
 "steps": [
  ("py", '''from cybercommons import ir, soc, grc
import time

now = time.time()
# notice
base = soc.Baseline({"read_file": 0.9, "http_get": 0.1}, actions_per_hour=300)
drift = base.compare([soc.Event(now, "a", "run_shell")] * 20 +
                     [soc.Event(now, "a", "read_file")] * 5)
print("notice:", drift["verdict"], "| new tools:", drift["new_tools"])

# stop
race = ir.containment_race(300, human_approval_minutes=8, auto_containment_seconds=12)
print(f"stop:   automated {race['actions_during_auto_containment']:.0f} further actions "
      f"vs {race['actions_during_manual_approval']:.0f} manual")

# recover
ok, missing = ir.Replay(["p"], ["r"], "glm-4.6@2025-11", 42).replayable()
print("recover: replayable =", ok, "| missing:", missing or "nothing")
'''),
  ("md", "Three capabilities, each independently testable, none of them "
         "prevention. A programme with all three survives a failure it did not "
         "predict — which is the only kind that actually happens."),
  ("py", '''print(grc.SEQUENCING)
print("\\nPerfection would mean step 3 (containment) never fails.")
print("Resilience means steps 4-6 work when it does.")
'''),
 ],
 "expect": "Drift is detected with `run_shell` as a new tool, automated "
           "containment permits ~60 further actions against ~2400 for manual "
           "approval, and the instrumented run is replayable.",
 "challenge": "Run a game day that assumes containment failed. Measure notice, "
              "stop and recover as three separate numbers. The weakest one is next "
              "quarter's plan.",
},
}
