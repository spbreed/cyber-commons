"""E2 — The Regulatory & Compliance Lead. Nine sessions.

    E2.1  the regulatory map — three layers, and which one bites first
    E2.2  horizontal AI regulation as controls, not clauses
    E2.3  voluntary frameworks as the spine
    E2.4  sector overlays, which already applied
    E2.5  privacy: the context window is a disclosure
    E2.6  incident and disclosure obligations
    E2.7  documentation that survives supervision
    E2.8  auditability of autonomous action
    E2.9  regulator and auditor conversations
"""

EXERCISES: dict[str, dict] = {

"E2.1": {
 "concept": """
The regulatory picture for an AI system has three layers, and confusing them is
how programmes end up heavily invested in one while blind to another.

1. **Horizontal AI regulation** — applies *because it is AI*, regardless of what
   you do. The EU AI Act is the archetype.
2. **Sector overlays** — apply *because of what you do*, and mostly predate AI
   entirely: DORA for financial services, HIPAA for health, PCI DSS for card
   data, NIS2 for critical infrastructure.
3. **Cross-cutting law** — applies to the *data and the outcome*: GDPR and
   privacy law, consumer protection, sectoral incident reporting.

The common mistake is treating layer 1 as the whole map. For most organisations
layers 2 and 3 bite first and harder, because they already apply, they already
have supervisors, and their clocks are shorter.

The useful exercise is never "what does the AI Act say". It is: **locate one
system on all three layers and find the shortest clock.**
""",
 "steps": [
  ("md", "## 2 · Demo — the three layers, and what triggers each"),
  ("py", '''LAYERS = {
 "1 · horizontal AI regulation": {
   "examples": ["EU AI Act", "national AI acts in progress"],
   "triggered_by": "the system being AI, and its risk classification",
   "typical_lead_time": "months to years of transition periods"},
 "2 · sector overlays": {
   "examples": ["DORA (financial)", "HIPAA (health)", "PCI DSS (cards)", "NIS2 (CNI)"],
   "triggered_by": "what your organisation does — already in force",
   "typical_lead_time": "none: already applies"},
 "3 · cross-cutting": {
   "examples": ["GDPR / privacy law", "consumer protection", "incident reporting"],
   "triggered_by": "the data processed and the outcome produced",
   "typical_lead_time": "none: already applies"},
}
for name, l in LAYERS.items():
    print(f"{name}")
    print(f"   {', '.join(l['examples'])}")
    print(f"   triggered by : {l['triggered_by']}")
    print(f"   lead time    : {l['typical_lead_time']}\\n")
'''),
  ("md", "## 3 · Locate one system on all three layers"),
  ("py", '''from dataclasses import dataclass

@dataclass
class System:
    name: str; sector: str; data: tuple; autonomy: str
    affects_individuals: bool; is_ict_service: bool

CLAIMS = System("claims-triage-agent", sector="insurance",
                data=("customer", "health", "regulated"), autonomy="L2.5",
                affects_individuals=True, is_ict_service=True)

def applicable(sys_):
    out = []
    # layer 1
    if sys_.autonomy in ("L2", "L2.5", "L3") and sys_.affects_individuals:
        out.append(("EU AI Act", 1, "automated decision affecting individuals; "
                    "human oversight and record-keeping obligations"))
    # layer 2
    if sys_.sector in ("insurance", "banking", "financial"):
        out.append(("DORA", 2, "ICT third-party risk, incident reporting, "
                    "resilience testing, exit strategy"))
    if "health" in sys_.data:
        out.append(("HIPAA-equivalent", 2, "minimum necessary; audit controls"))
    # layer 3
    if sys_.affects_individuals and "customer" in sys_.data:
        out.append(("GDPR", 3, "lawful basis, erasure, automated decision-making"))
    return sorted(out, key=lambda r: r[1])

print(f"{CLAIMS.name} — autonomy {CLAIMS.autonomy}, data {list(CLAIMS.data)}\\n")
print(f"{'instrument':22s}{'layer':>6}  obligation")
print("-" * 92)
for name, layer, why in applicable(CLAIMS):
    print(f"{name:22s}{layer:>6}  {why}")
'''),
  ("md", "## 4 · The control — the shortest-clock register\n\n"
         "Your real deadline is not the one you have read about. It is the "
         "shortest one that applies."),
  ("py", '''CLOCKS = {
 "DORA (major ICT incident)":       (4,  "initial notification to the regulator"),
 "contractual (major client)":      (12, "client security contact"),
 "NIS2 (early warning)":            (24, "national CSIRT"),
 "GDPR (personal data breach)":     (72, "supervisory authority"),
 "EU AI Act (serious incident)":    (72, "market surveillance authority"),
}
applicable_names = {n for n, _, _ in applicable(CLAIMS)}
mine = {k: v for k, v in CLOCKS.items()
        if any(a.split()[0] in k for a in applicable_names) or "contractual" in k}

print(f"{'obligation':36s}{'deadline (h)':>14}  notify")
print("-" * 78)
for name, (hours, who) in sorted(mine.items(), key=lambda kv: kv[1][0]):
    print(f"{name:36s}{hours:>14}  {who}")
shortest = min(mine.items(), key=lambda kv: kv[1][0])
print(f"\\nBINDING DEADLINE: {shortest[0]} at {shortest[1][0]}h")
print("Every runbook, every escalation path and every out-of-hours rota is")
print("designed against that number, not against the 72-hour one people quote.")
assert shortest[1][0] <= 12
'''),
  ("py", '''# Verify: which layer actually drove the requirements?
from collections import Counter
layers = Counter(layer for _, layer, _ in applicable(CLAIMS))
print("obligations by layer:", dict(layers))
print()
for layer, label in ((1, "horizontal AI regulation"), (2, "sector overlay"),
                     (3, "cross-cutting")):
    n = layers.get(layer, 0)
    print(f"   layer {layer} ({label:26s}) {n} obligation(s)")
print("\\nLayers 2 and 3 produce more obligations than layer 1, and they were")
print("already in force before anyone deployed an agent. That is the finding.")
assert layers.get(2, 0) + layers.get(3, 0) > layers.get(1, 0)
'''),
 ],
 "expect": "The three layers print with what triggers each. The claims-triage "
           "agent attracts obligations from all three — EU AI Act, DORA, a "
           "HIPAA-equivalent and GDPR. The shortest-clock register identifies "
           "DORA's 4-hour initial notification as the binding deadline, and "
           "layers 2 and 3 together produce more obligations than the horizontal "
           "AI regulation.",
 "challenge": "Build the shortest-clock register for your highest-tier AI system. "
              "Most teams discover the binding deadline is a sector overlay or a "
              "customer contract, not the AI regulation they have been reading.",
},

"E2.2": {
 "concept": """
Horizontal AI regulation is, in practice, mostly about **documented process and
human oversight**. That is good news, because those map onto controls you can
build and evidence mechanically.

The trap is answering a clause with a policy document. "We maintain appropriate
human oversight" satisfies nobody who asks the follow-up question, and the
follow-up question is always the same: *show me*.

So the working method is to resolve each regulatory theme down to a control from
your own catalogue (E1.4), and let the control's evidence be the answer. Four
themes cover most of it:

- risk management system,
- record-keeping,
- human oversight,
- accuracy and robustness.

Each one resolves to controls you already built in tracks A, B and D.
""",
 "steps": [
  ("md", "## 2 · Demo — resolve each theme to a control with evidence"),
  ("py", '''CATALOGUE = {
 "AC-1": ("agent identities distinct from human and separately revocable",
          "gateway logs with an act chain; monthly sample"),
 "AC-2": ("delegated authority narrows at every hop",
          "regression suite IDN-01/IDN-04 on every release"),
 "SB-1": ("egress deny-by-default with an allowlist", "90-day denial log"),
 "SB-2": ("privileged tools require approval below L3", "tool policy in git + denial log"),
 "EV-1": ("every action logged with the acting identity", "audit sample of 50 actions"),
 "EV-2": ("accuracy evaluated against a held-out key per release",
          "expert accuracy report with sample size"),
 "DR-1": ("behavioural drift raises an alert", "drift alerts and dispositions"),
 "ST-1": ("a tested stop mechanism you own", "game-day record with measured time-to-stop"),
}
THEMES = {
 "risk management system":       ["AC-1", "SB-2", "DR-1"],
 "record-keeping (Art.12)":      ["EV-1", "AC-2"],
 "human oversight (Art.14)":     ["SB-2", "ST-1"],
 "accuracy and robustness":      ["EV-2", "DR-1"],
}
for theme, cids in THEMES.items():
    print(f"{theme}")
    for cid in cids:
        text, evidence = CATALOGUE[cid]
        print(f"   {cid}  {text}")
        print(f"         evidence: {evidence}")
    print()
'''),
  ("md", "## 3 · Where it breaks — the clause answered with prose"),
  ("py", '''WEAK = {
 "risk management system":   "We operate a risk management framework for AI systems.",
 "record-keeping (Art.12)":  "Appropriate logs are retained.",
 "human oversight (Art.14)": "Human oversight is maintained at all times.",
 "accuracy and robustness":  "Models are tested prior to deployment.",
}
def survives_followup(answer, controls):
    """The follow-up question is always 'show me'."""
    return bool(controls), ("names a control with an artefact" if controls
                            else "no artefact — the answer IS the evidence, which is the problem")

print(f"{'theme':28s}{'prose answer survives?':>24}")
print("-" * 56)
for theme in THEMES:
    ok_weak, _ = survives_followup(WEAK[theme], [])
    print(f"{theme:28s}{str(ok_weak):>24}")
print("\\nAll four fail the same way: there is nothing to produce when asked.")
'''),
  ("md", "## 4 · The control — produce the evidence, then check it is fresh"),
  ("py", '''import time
from dataclasses import dataclass
now = time.time(); DAY = 86400

@dataclass
class ControlTest:
    cid: str; passed: bool; tested_at: float; valid_for_days: float
    def state(self, at):
        if (at - self.tested_at)/DAY > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

TESTS = [ControlTest("AC-1", True,  now -  3*DAY, 30),
         ControlTest("AC-2", True,  now -  9*DAY, 30),
         ControlTest("SB-2", True,  now - 40*DAY, 30),
         ControlTest("EV-1", True,  now -  5*DAY, 60),
         ControlTest("EV-2", True,  now - 12*DAY, 30),
         ControlTest("DR-1", False, now,          30),
         ControlTest("ST-1", True,  now - 41*DAY, 180)]
by = {t.cid: t for t in TESTS}

print(f"{'theme':28s}{'controls':22s}{'evidenced now':>15}")
print("-" * 68)
for theme, cids in THEMES.items():
    states = [by[c].state(now) if c in by else "NO EVIDENCE" for c in cids]
    ok = all(s == "PASS" for s in states)
    blockers = ",".join(c for c, s in zip(cids, states) if s != "PASS")
    verdict = "yes" if ok else f"NO — {blockers}"
    print(f"{theme:28s}{str(cids):22s}{verdict:>15}")

fully = [t for t, cids in THEMES.items()
         if all((by[c].state(now) if c in by else "X") == "PASS" for c in cids)]
print(f"\\nthemes fully evidenced right now: {len(fully)}/{len(THEMES)}  {fully}")
print("\\nThat sentence is what you say to a supervisor. It is smaller than the")
print("prose version and it is defensible, which is the trade worth making.")
assert len(fully) < len(THEMES)
'''),
 ],
 "expect": "Four regulatory themes resolve to named controls, each with a concrete "
           "evidence artefact. All four prose answers fail the show-me test. "
           "Checking freshness, two themes are fully evidenced — human oversight "
           "fails on a stale SB-2 and risk management on a failing DR-1 — giving a "
           "smaller but defensible statement.",
 "challenge": "Take one clause your programme claims to satisfy and trace it to "
              "an artefact with a date. If the trail ends at a policy document, "
              "the clause is ticked and undefended.",
},

"E2.3": {
 "concept": """
Voluntary frameworks make a better spine than regulation, for two reasons that
have nothing to do with enthusiasm for standards.

**They are written as controls.** NIST AI RMF and ISO 42001 describe things you
*do*. Regulation describes outcomes you must achieve, which is harder to
operationalise and easier to satisfy on paper.

**They change more slowly than the law.** Building against a framework and
mapping outward to regulation means new regulation is a mapping exercise rather
than a programme.

The method: pick one spine with the best coverage of the controls you actually
operate, map outward, and be explicit about what the spine does **not** reach —
because every spine has gaps, and the gaps are where the sector overlay lives.
""",
 "steps": [
  ("md", "## 2 · Demo — which spine covers your control set best"),
  ("py", '''from collections import defaultdict

CONTROLS = {
 "AC-1": ("NIST AI RMF: GOVERN-1.2", "ISO 42001: 6.1", "EU AI Act: Art.14"),
 "AC-2": ("NIST AI RMF: MANAGE-2.2", "ISO 42001: 8.1"),
 "SB-1": ("NIST AI RMF: MANAGE-2.1", "ISO 27001: A.8.20"),
 "SB-2": ("EU AI Act: Art.14",),
 "EV-1": ("ISO 42001: 9.1", "EU AI Act: Art.12"),
 "EV-2": ("NIST AI RMF: MEASURE-2.3",),
 "DR-1": ("NIST AI RMF: MEASURE-2.4", "ISO 42001: 9.1"),
 "ST-1": ("EU AI Act: Art.14", "DORA: Art.11"),
}
by_fw = defaultdict(set)
for cid, fws in CONTROLS.items():
    for f in fws:
        by_fw[f.split(":")[0]].add(cid)

print(f"{'framework':18s}{'covers':>8}  controls")
print("-" * 62)
for fw, cids in sorted(by_fw.items(), key=lambda kv: -len(kv[1])):
    print(f"{fw:18s}{len(cids):>8}  {sorted(cids)}")

spine = max(by_fw, key=lambda f: len(by_fw[f]))
gaps = sorted(set(CONTROLS) - by_fw[spine])
print(f"\\nbest spine: {spine} covering {len(by_fw[spine])}/{len(CONTROLS)}")
print(f"not reached by the spine: {gaps}")
'''),
  ("md", "## 3 · Where it breaks — one framework per regulation"),
  ("py", '''def per_regulation(controls):
    """Build a separate control set for each instrument. The usual approach."""
    sets = defaultdict(set)
    for cid, fws in controls.items():
        for f in fws:
            sets[f.split(":")[0]].add(cid)
    return sets

sets = per_regulation(CONTROLS)
total_implementations = sum(len(v) for v in sets.values())
distinct_controls = len(CONTROLS)
print(f"distinct controls actually needed : {distinct_controls}")
print(f"control implementations if built per-framework : {total_implementations}")
print(f"duplication factor : {total_implementations/distinct_controls:.1f}×")

print("\\ncontrols claimed by more than one framework:")
for cid, fws in CONTROLS.items():
    if len(fws) > 1:
        print(f"   {cid}  {len(fws)} frameworks: {[f.split(':')[0] for f in fws]}")
print("\\nBuilt separately, these drift: the ISO version of AC-1 and the AI Act")
print("version diverge, evidence is produced twice, and neither is trusted.")
assert total_implementations > distinct_controls
'''),
  ("md", "## 4 · The control — one spine, mapped outward, gaps named"),
  ("py", '''def spine_plan(controls, spine):
    covered = {c for c, fws in controls.items() if any(f.startswith(spine) for f in fws)}
    gaps = sorted(set(controls) - covered)
    secondary = defaultdict(list)
    for g in gaps:
        for f in controls[g]:
            secondary[f.split(":")[0]].append(g)
    return {"spine": spine, "covered": sorted(covered), "gaps": gaps,
            "secondary_sources": {k: v for k, v in secondary.items()
                                  if not k.startswith(spine)}}

plan = spine_plan(CONTROLS, "NIST AI RMF")
print(f"spine              {plan['spine']}")
print(f"covered by spine   {len(plan['covered'])}/{len(CONTROLS)}  {plan['covered']}")
print(f"gaps               {plan['gaps']}")
print("secondary sources needed for the gaps:")
for fw, cids in plan["secondary_sources"].items():
    print(f"   {fw:20s} supplies {cids}")

print("\\nstatement for the assessor:")
print(f"   'We operate {len(CONTROLS)} AI controls, built against {plan['spine']}.")
print(f"    {len(plan['covered'])} map directly to it; {len(plan['gaps'])} come from")
print(f"    {list(plan['secondary_sources'])}. Each control produces one artefact,")
print("    which satisfies every clause it maps to.'")
assert plan["gaps"]
'''),
 ],
 "expect": "NIST AI RMF covers the most controls (4 of 8) and is selected as the "
           "spine, leaving SB-2, EV-1 and ST-1 as gaps supplied by ISO 42001, the "
           "EU AI Act and DORA. Building per-framework would produce 14 control "
           "implementations for 8 distinct controls — a 1.8× duplication factor "
           "with controls claimed by several frameworks drifting apart.",
 "challenge": "Pick your spine and justify it in one sentence to an assessor. "
              "\"It has the best coverage of the controls we actually operate\" is "
              "far stronger than \"it is the one our regulator mentioned\".",
},

"E2.4": {
 "concept": """
Sector overlays usually bite first, and the reason is structural: they already
applied before anyone deployed an agent, they already have a supervisor who
knows your organisation, and several of their clauses cover autonomous action
without ever using the word AI.

Four clause types that catch agents without naming them:

- **ICT third-party risk** (DORA) — your model provider is an ICT third party.
- **Exit strategy** (DORA) — can you stop using this provider? Most AI contracts
  have no answer.
- **Scope containment** (PCI DSS) — an agent with access to the cardholder data
  environment expands that environment.
- **Minimum necessary** (HIPAA) — the agent's context window is a disclosure.

Citing an existing clause is also far more effective internally than proposing a
new AI policy: it needs no new governance, and somebody already owns it.
""",
 "steps": [
  ("md", "## 2 · Demo — map agent facts onto pre-existing clauses"),
  ("py", '''OVERLAYS = {
 "DORA (financial)": [
   ("ICT third-party risk", "your model provider is an ICT third party",
    lambda s: s["uses_external_model"]),
   ("exit strategy", "can you stop using this provider and keep operating?",
    lambda s: s["uses_external_model"]),
   ("resilience testing", "your stop mechanism is in scope for testing",
    lambda s: s["autonomy"] in ("L2.5", "L3")),
   ("incident reporting", "clocks measured in hours",
    lambda s: True)],
 "HIPAA (health)": [
   ("minimum necessary", "the context window is a disclosure",
    lambda s: "health" in s["data"]),
   ("audit controls", "the ACTING identity must be recorded",
    lambda s: True)],
 "PCI DSS (cards)": [
   ("scope containment", "an agent with CDE access expands the CDE",
    lambda s: "cardholder" in s["data"]),
   ("access control", "non-human identities need the same rigour",
    lambda s: True)],
}
SYSTEM = {"name": "claims-triage-agent", "uses_external_model": True,
          "autonomy": "L2.5", "data": ("customer", "health")}

print(f"{SYSTEM['name']}: autonomy {SYSTEM['autonomy']}, data {list(SYSTEM['data'])}, "
      f"external model {SYSTEM['uses_external_model']}\\n")
hits = []
for fw, clauses in OVERLAYS.items():
    applicable = [(c, why) for c, why, test in clauses if test(SYSTEM)]
    if not applicable: continue
    print(f"{fw}")
    for c, why in applicable:
        hits.append((fw, c)); print(f"   {c:24s}{why}")
    print()
print(f"{len(hits)} pre-existing clauses apply. None of them mentions AI.")
'''),
  ("md", "## 3 · Where it breaks — the exit-strategy clause"),
  ("py", '''PROVIDERS = {
 "hosted frontier API": {"can_pin_version": False, "can_export_weights": False,
                         "equivalent_alternative": True, "switching_days": 45},
 "hosted open-weight API": {"can_pin_version": True, "can_export_weights": False,
                            "equivalent_alternative": True, "switching_days": 14},
 "self-hosted open weights": {"can_pin_version": True, "can_export_weights": True,
                              "equivalent_alternative": True, "switching_days": 2},
}
def exit_assessment(p):
    problems = []
    if not p["can_pin_version"]:
        problems.append("cannot pin a version — behaviour changes without notice")
    if not p["can_export_weights"]:
        problems.append("cannot retain the artefact — no continuity if withdrawn")
    if p["switching_days"] > 30:
        problems.append(f"{p['switching_days']}d to switch — outside most RTOs")
    return (not problems), problems

print(f"{'provider':28s}{'exit strategy':>15}")
print("-" * 48)
for name, p in PROVIDERS.items():
    ok, problems = exit_assessment(p)
    print(f"{name:28s}{'defensible' if ok else 'NOT DEFENSIBLE':>15}")
    for x in problems: print(f"      ⚠ {x}")
print("\\nDORA Art.11 asks this directly. It is the clause most AI procurement")
print("cannot answer, and it was written years before anyone deployed an agent.")
'''),
  ("md", "## 4 · The control — cite the existing clause, not a new policy"),
  ("py", '''def make_the_case(clause, framework, agent_fact, existing_owner):
    return (f"'{clause}' ({framework}) already applies to us and is owned by "
            f"{existing_owner}.\\n"
            f"   The agent fact that engages it: {agent_fact}\\n"
            f"   Ask: extend the existing control, not create an AI policy.")

CASES = [
 ("ICT third-party risk", "DORA", "the model provider is an ICT third party",
  "third-party risk management"),
 ("audit controls", "HIPAA", "the acting identity is not currently recorded",
  "the security team"),
 ("access control", "PCI DSS", "non-human identities have no recertification",
  "identity and access management"),
]
for c, fw, fact, owner in CASES:
    print(make_the_case(c, fw, fact, owner)); print()

print("Compare with the alternative ask:")
print("   'We need a new AI governance policy and a new committee.'")
print("   → new owner, new process, new budget line, six months.")
print("versus")
print("   'Extend third-party risk to cover model providers.'")
print("   → existing owner, existing process, next review cycle.")
assert len(CASES) == 3
'''),
 ],
 "expect": "Seven pre-existing clauses apply to the claims-triage agent across "
           "DORA, HIPAA and PCI DSS, none of which mentions AI. The exit-strategy "
           "assessment marks the hosted frontier API as not defensible on all "
           "three counts, the hosted open-weight API on one, and self-hosted "
           "weights as defensible. Three cases show how to route the requirement "
           "to an existing owner rather than a new policy.",
 "challenge": "Find the clause in your own sector overlay that already covers "
              "autonomous action without naming AI. Citing it is faster, cheaper "
              "and more persuasive than any new AI policy you could write.",
},

"E2.5": {
 "concept": """
Privacy for agents turns on one fact that surprises most teams: **the context
window is a disclosure, and the trace is a record.**

When an agent reads a customer record to do its job, that record enters the
model's context. If the trace is retained — and it usually is, for forensics
(D1.5) — then personal data now exists in a system that was never in the privacy
review, with a retention period nobody set, in a place the erasure process does
not reach.

Three obligations attach, and the third is the one that bites:

- **Lawful basis** for the processing that put it there.
- **Retention limit** on the trace itself, separately from the source system.
- **Erasure** — and this reaches into traces, eval corpora, fine-tuning sets and
  backups.

The capability that makes erasure possible is the same one C2.4 built for poison
removal: per-record hashes. Without them you cannot locate the record, so you
cannot delete it.
""",
 "steps": [
  ("md", "## 2 · Demo — personal data arriving in a trace nobody reviewed"),
  ("py", '''import re, hashlib
from dataclasses import dataclass, field

@dataclass
class Step:
    n: int; tool: str; target: str; result: str

RUN = [
 Step(1, "read_ticket", "SUP-4471",
      "Customer J. Okonkwo (dana.okonkwo@example.com, acct 8812) reports a "
      "double charge on card 4111111111111111."),
 Step(2, "search_orders", "acct=8812",
      "3 orders found for account 8812, total GBP 412.90"),
 Step(3, "post_reply", "SUP-4471", "Refund issued for the duplicate charge."),
]
DETECTORS = {
 "email": re.compile(r"[\\w.+-]+@[\\w-]+\\.[\\w.]+"),
 "payment card": re.compile(r"\\b4[0-9]{12}(?:[0-9]{3})?\\b"),
 "account number": re.compile(r"\\bacct \\d{4}\\b"),
 "name": re.compile(r"\\b[A-Z]\\. [A-Z][a-z]+\\b"),
}
found = []
for s in RUN:
    for kind, pat in DETECTORS.items():
        for m in pat.finditer(s.result):
            found.append((s.n, kind, m.group(0)))
print("personal data present in the agent trace:")
for n, kind, val in found:
    print(f"   step {n}  {kind:16s}{val}")
print(f"\\n{len(found)} items. Nobody put them there deliberately — the agent read")
print("a support ticket, which is exactly what it was asked to do.")
'''),
  ("md", "## 3 · Where it breaks — the erasure request"),
  ("py", '''SYSTEMS = {
 "primary CRM":        {"has_index": True,  "retention_days": 2555},
 "data warehouse":     {"has_index": True,  "retention_days": 1095},
 "agent traces":       {"has_index": False, "retention_days": 400},
 "eval corpus":        {"has_index": False, "retention_days": 9999},
 "fine-tuning set":    {"has_index": False, "retention_days": 9999},
 "backups":            {"has_index": True,  "retention_days": 90},
}
SUBJECT = "dana.okonkwo@example.com"

print(f"erasure request for {SUBJECT}\\n")
print(f"{'system':22s}{'can locate?':>13}{'retention (d)':>15}  outcome")
print("-" * 76)
unreachable = []
for name, s in SYSTEMS.items():
    if s["has_index"]:
        outcome = "erased"
    else:
        outcome = "CANNOT LOCATE — request cannot be completed"
        unreachable.append(name)
    print(f"{name:22s}{str(s['has_index']):>13}{s['retention_days']:>15}  {outcome}")
print(f"\\n{len(unreachable)} system(s) where the request fails: {unreachable}")
print("The response to the data subject says 'erased'. It is not true in three")
print("systems, two of which retain indefinitely.")
assert unreachable
'''),
  ("md", "## 4 · The control — index the trace, and set retention per field"),
  ("py", '''def content_hash(text): return hashlib.sha256(text.encode()).hexdigest()[:16]

def index_trace(run, detectors):
    """A subject index: which steps contain data about whom."""
    idx = {}
    for s in run:
        for kind, pat in detectors.items():
            for m in pat.finditer(s.result):
                subj = m.group(0)
                idx.setdefault(subj, []).append(
                    {"step": s.n, "kind": kind, "hash": content_hash(s.result)})
    return idx

IDX = index_trace(RUN, DETECTORS)
print("subject index built from the trace:")
for subj, entries in IDX.items():
    print(f"   {subj:36s}{len(entries)} occurrence(s) in steps "
          f"{sorted({e['step'] for e in entries})}")

def erase(run, idx, subject):
    steps = sorted({e["step"] for e in idx.get(subject, [])})
    out = []
    for s in run:
        if s.n in steps:
            out.append(Step(s.n, s.tool, s.target,
                            f"[erased on request; original sha256={content_hash(s.result)}]"))
        else:
            out.append(s)
    return out, steps

erased, touched = erase(RUN, IDX, SUBJECT)
print(f"\\nerasure for {SUBJECT}: steps {touched}")
for s in erased:
    print(f"   step {s.n}: {s.result[:66]}")

remaining = [(n, k, v) for s in erased for k, pat in DETECTORS.items()
             for m in pat.finditer(s.result) for n, v in [(s.n, m.group(0))]]
print(f"\\npersonal data remaining in the trace: {remaining or 'none'}")
assert not remaining
print("The hash is retained, so if the original surfaces in a backup you can")
print("still prove it is the same content — which is what makes the erasure auditable.")
'''),
  ("py", '''# Per-field retention: keep the forensically useful parts, drop the rest early.
RETENTION = {"n": 400, "tool": 400, "target": 400, "result": 7}
print(f"{'field':10s}{'days':>6}  rationale")
print("-" * 62)
for f, d in RETENTION.items():
    why = ("tool output — highest sensitivity, lowest retention" if f == "result"
           else "cheap, high forensic value, no personal data")
    print(f"{f:10s}{d:>6}  {why}")
print("\\nAt 7 days the result field is gone and the trace is still forensically")
print("useful: you know what the agent did, to what, and when.")
'''),
 ],
 "expect": "Five items of personal data appear in the agent trace — name, email, "
           "account number and payment card — none placed there deliberately. The "
           "erasure request fails in three systems that cannot locate the record, "
           "two of which retain indefinitely. Building a subject index locates the "
           "affected steps, erasure leaves no personal data while retaining the "
           "hash, and per-field retention drops the sensitive field at 7 days.",
 "challenge": "Time-box this to an hour: can you delete one customer's data from "
              "your agent traces today? The answer usually arrives in ten minutes "
              "and is usually no — and the eval corpus is the system people forget "
              "entirely.",
},

"E2.6": {
 "concept": """
Incident and disclosure obligations meet agentic incidents badly, for one
specific reason: **broken attribution consumes the clock.**

The clock starts at *awareness* — when you know a reportable event may have
occurred. It does not pause while you work out who did it. So if your logs
attribute an agent's actions to the human whose credential it borrowed (D2.1),
the days you spend establishing what actually happened are deadline days.

Two consequences worth internalising:

1. **Containing fast does not buy reporting time.** You can contain in an hour
   and still miss a 72-hour deadline.
2. **You will have to disclose before attribution is complete.** So the sentence
   you send when you know an agent acted but cannot yet say which one needs to
   be drafted *now*, not during the incident.
""",
 "steps": [
  ("md", "## 2 · Demo — the clock, and what attribution costs it"),
  ("py", '''import time
t0 = time.time(); H = 3600

def clock(awareness, containment, report, deadline_hours):
    to_contain = (containment - awareness)/H
    to_report  = (report - awareness)/H
    return {"contain_h": round(to_contain,1), "report_h": round(to_report,1),
            "deadline": deadline_hours, "met": to_report <= deadline_hours,
            "margin_h": round(deadline_hours - to_report, 1)}

SCENARIOS = {
 "attribution sound":            (t0 + 2*H,  t0 + 20*H),
 "attribution broken, 3d scope": (t0 + 6*H,  t0 + 92*H),
 "fast containment, slow scope": (t0 + 1*H,  t0 + 80*H),
}
print(f"{'scenario':32s}{'contain':>9}{'report':>9}{'met':>6}{'margin':>9}")
print("-" * 66)
for name, (c, r) in SCENARIOS.items():
    k = clock(t0, c, r, 72)
    print(f"{name:32s}{k['contain_h']:>9.1f}{k['report_h']:>9.1f}"
          f"{str(k['met']):>6}{k['margin_h']:>9.1f}")
print("\\nThe third row contained in ONE HOUR and missed by 8 hours.")
'''),
  ("py", '''# Where the time actually goes when attribution is broken.
PHASES = [
 ("alert fires → analyst picks it up",        3,  "queue depth"),
 ("confirm an incident",                      6,  "is this real?"),
 ("establish WHO acted",                     48,  "logs name the human; agents hidden"),
 ("scope what was touched",                  24,  "must walk the delegation chain (D2.3)"),
 ("legal determines reportability",            8,  "needs the scope"),
 ("draft and send",                            3,  ""),
]
elapsed = 0
print(f"{'phase':38s}{'hours':>7}{'cumulative':>12}  note")
print("-" * 82)
for name, h, note in PHASES:
    elapsed += h
    flag = "  ← DEADLINE PASSED" if elapsed > 72 else ""
    print(f"{name:38s}{h:>7}{elapsed:>12}{flag}  {note}")
print(f"\\ntotal {elapsed}h against a 72h deadline")
attribution_cost = PHASES[2][1]
print(f"the attribution phase alone is {attribution_cost}h — "
      f"{attribution_cost/72:.0%} of the entire deadline")
assert elapsed > 72
'''),
  ("md", "## 3 · The control — fix attribution, and pre-draft the hard sentence"),
  ("py", '''def with_act_chains(phases):
    """With an acting-identity field, 'who acted' is a query, not an investigation."""
    return [(n, (0.5 if n.startswith("establish WHO") else h), note)
            for n, h, note in phases]

fixed = with_act_chains(PHASES)
total_fixed = sum(h for _, h, _ in fixed)
print(f"with act chains recorded (A2.5 + EV-1): {total_fixed}h vs {elapsed}h")
print(f"deadline met: {total_fixed <= 72}")
assert total_fixed <= 72

PRE_DRAFTED = """
We are notifying you of an incident under [instrument], first identified at
[awareness timestamp].

An automated system operating within our environment performed actions that may
have affected [scope]. Our logging currently attributes these actions to the
authenticated principal on whose behalf the system was acting; we are working to
establish which specific automated component performed them.

Containment: [action] completed at [time].
We will provide an update within [period], including the completed attribution.
"""
print("\\nPRE-DRAFTED DISCLOSURE (write this now, not during the incident):")
print(PRE_DRAFTED)
print("It is honest, it starts the notification, and it does not claim an")
print("attribution you cannot yet support.")
'''),
  ("py", '''# Verify: the runbook needs two owners, not one.
def runbook_check(containment_owner, disclosure_owner, clock_starts_at,
                  has_predrafted):
    problems = []
    if containment_owner == disclosure_owner:
        problems.append("one owner for both workstreams — they compete under time pressure")
    if clock_starts_at != "awareness":
        problems.append(f"clock starts at {clock_starts_at!r}; a regulator will use awareness")
    if not has_predrafted:
        problems.append("no pre-drafted disclosure for incomplete attribution")
    return (not problems), problems

for label, args in (("as usually written", ("IR lead", "IR lead", "confirmation", False)),
                    ("corrected", ("IR lead", "legal/compliance lead", "awareness", True))):
    ok, problems = runbook_check(*args)
    print(f"{label:22s} sound={ok}")
    for p in problems: print(f"   ⚠ {p}")
assert runbook_check("IR lead", "legal/compliance lead", "awareness", True)[0]
'''),
 ],
 "expect": "One-hour containment still misses the 72-hour deadline when scoping is "
           "slow. The phase breakdown totals 92 hours, of which establishing who "
           "acted is 48 — two-thirds of the entire deadline. Recording act chains "
           "cuts the total to 44.5 hours and meets the deadline. The runbook check "
           "flags a shared owner, a late clock start and a missing pre-drafted "
           "disclosure.",
 "challenge": "Draft the disclosure sentence you would send when you know an "
              "agent acted but cannot say which one. Getting legal to agree that "
              "wording takes weeks in peacetime and is impossible at hour 60.",
},

"E2.7": {
 "concept": """
Documentation survives supervision when it points at machine-generated evidence
rather than restating intent.

The difference is not length or formality. It is whether each sentence names
three things:

- a **control** that operates,
- an **artefact** it produces,
- a **date** on which that artefact was last produced.

A sentence with all three can be checked. A sentence with none of them is a
statement of intent, and a supervisor's next question makes that visible
immediately.

Intent statements are not forbidden — some things genuinely are aspirations. The
failure is presenting them as controls. Label them, and the rest of the document
becomes more credible rather than less.
""",
 "steps": [
  ("md", "## 2 · Demo — the same policy paragraph, two ways"),
  ("py", '''import re, time
now = time.time(); DAY = 86400

WEAK = """
Our AI systems are subject to appropriate oversight and controls. Access is
granted on a least-privilege basis and reviewed periodically. Agents are
monitored for anomalous behaviour and we maintain comprehensive logging.
"""

STRONG = """
Agent identities are distinct from human identities (AC-1). Evidence: gateway
logs containing an act chain for every action; sampled monthly, last test
2026-08-13, valid 30d.

Delegated authority narrows at every hop (AC-2). Evidence: the token exchange
refuses widening; regression cases IDN-01/IDN-04 run on every release, last run
2026-08-15.

Autonomy above L2 requires approval for privileged tools (SB-2). Evidence: tool
policy in git; 90-day denial log attached, last reviewed 2026-07-06.
"""

CONTROL_RE = re.compile(r"\\b([A-Z]{2}-\\d)\\b")
DATE_RE    = re.compile(r"\\b20\\d{2}-\\d{2}-\\d{2}\\b")
ARTEFACT_RE = re.compile(r"\\b(log|logs|sample|report|test|cases|policy|record)\\b", re.I)

def score_paragraph(text):
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    rows = []
    for s in sentences:
        rows.append({"has_control": bool(CONTROL_RE.search(s)),
                     "has_artefact": bool(ARTEFACT_RE.search(s)),
                     "has_date": bool(DATE_RE.search(s)),
                     "text": s[:56]})
    checkable = [r for r in rows if r["has_control"] and r["has_artefact"]]
    return rows, len(checkable), len(rows)

for label, text in (("WEAK", WEAK), ("STRONG", STRONG)):
    rows, checkable, total = score_paragraph(text)
    print(f"=== {label} — {checkable}/{total} sentences checkable ===")
    for r in rows:
        marks = ("C" if r["has_control"] else "-") + \\
                ("A" if r["has_artefact"] else "-") + \\
                ("D" if r["has_date"] else "-")
        print(f"   [{marks}] {r['text']}")
    print()
print("C = names a control · A = names an artefact · D = carries a date")
'''),
  ("md", "## 3 · Where it breaks — the follow-up question"),
  ("py", '''FOLLOWUPS = [
 ("'appropriate oversight' — show me the last time it operated.", "WEAK"),
 ("'reviewed periodically' — what period, and when was the last one?", "WEAK"),
 ("'comprehensive logging' — produce one action's full record.", "WEAK"),
 ("'act chain for every action' — produce the August sample.", "STRONG"),
]
print(f"{'follow-up question':64s}{'answerable?':>12}")
print("-" * 78)
for q, source in FOLLOWUPS:
    print(f"{q:64s}{('yes' if source == 'STRONG' else 'NO'):>12}")
print("\\nThree of four cannot be answered from the document, and the person")
print("asking now doubts the fourth as well.")
'''),
  ("md", "## 4 · The control — verify the document against live control state"),
  ("py", '''from dataclasses import dataclass
@dataclass
class ControlTest:
    cid: str; passed: bool; tested_at: float; valid_for_days: float
    def state(self, at):
        if (at - self.tested_at)/DAY > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

TESTS = {t.cid: t for t in [
 ControlTest("AC-1", True, now -  3*DAY, 30),
 ControlTest("AC-2", True, now -  1*DAY, 30),
 ControlTest("SB-2", True, now - 40*DAY, 30)]}

cited = CONTROL_RE.findall(STRONG)
print(f"controls cited in the document: {sorted(set(cited))}\\n")
print(f"{'control':9s}{'state now':12s}{'document claim still true?':>28}")
print("-" * 52)
stale = []
for cid in sorted(set(cited)):
    st = TESTS[cid].state(now) if cid in TESTS else "NO EVIDENCE"
    ok = st == "PASS"
    if not ok: stale.append(cid)
    print(f"{cid:9s}{st:12s}{str(ok):>28}")
print(f"\\n{len(stale)} cited control(s) no longer evidenced: {stale}")
print("A document that cites controls can be CHECKED against live state.")
print("A document of intent cannot go stale, because it never said anything.")
assert stale
'''),
 ],
 "expect": "The weak paragraph has zero checkable sentences; the strong one has "
           "three, each naming a control, an artefact and a date. Three of four "
           "supervisor follow-ups are unanswerable from the weak version. "
           "Verifying the strong document against live control state finds SB-2 "
           "stale, so one of its claims is no longer true — which is only "
           "detectable because the document named a control.",
 "challenge": "Rewrite one paragraph of your AI policy in the strong shape. Any "
              "sentence that cannot name an artefact is intent — label it as "
              "such rather than deleting it, and the document gets more credible.",
},

"E2.8": {
 "concept": """
Auditability of autonomous action reduces to one question:

> For any single action, can you produce **who caused it** and **what they were
> allowed to do**?

Answering it needs two capabilities that must both be present at the moment the
action happens, because neither can be reconstructed afterwards:

- **Attribution** — the acting identity, the principal, and the chain between
  them (A2.5, EV-1).
- **Replay** — the prompts, the tool results, the pinned model version and the
  seed (D2.5).

Attribution without replay tells you who acted but not why. Replay without
attribution tells you what happened but not on whose authority. Regulators and
auditors ask both, usually in that order.
""",
 "steps": [
  ("md", "## 2 · Demo — the record, complete and incomplete"),
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

@dataclass
class Replay:
    prompts: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)
    model_version: str = ""
    seed: object = None
    def replayable(self):
        missing = [n for n, v in (("prompts", self.prompts),
                                  ("tool results", self.tool_results),
                                  ("model version", self.model_version),
                                  ("seed", self.seed is not None)) if not v]
        return (not missing), missing

def audit_record(action, token, replay):
    ok, missing = replay.replayable()
    return {"action": action,
            "acting_identity": token.actor,
            "on_behalf_of": token.sub,
            "chain": " → ".join(token.chain()),
            "scopes_held": sorted(token.scopes),
            "replayable": ok,
            "replay_gaps": missing,
            "answerable": token.actor != token.sub and ok}

GOOD_TOKEN = Token("dana@corp", "patch-agent", {"repo:read", "repo:write"},
                   {"actor": "orchestrator", "act": None})
GOOD_REPLAY = Replay(["fix SEC-4471"], ["file contents…"], "glm-4.6@2026-07-14", 42)

r = audit_record("merge_pr #8812", GOOD_TOKEN, GOOD_REPLAY)
for k, v in r.items(): print(f"{k:18s}{v}")
'''),
  ("md", "## 3 · Where it breaks — the two half-answers"),
  ("py", '''IMPERSONATED = Token("dana@corp", "dana@corp", {"repo:write"}, None)
NO_REPLAY    = Replay(["fix SEC-4471"], ["file contents…"], "", None)

CASES = {
 "complete":                     (GOOD_TOKEN,  GOOD_REPLAY),
 "attribution broken":           (IMPERSONATED, GOOD_REPLAY),
 "replay incomplete":            (GOOD_TOKEN,  NO_REPLAY),
 "neither":                      (IMPERSONATED, NO_REPLAY),
}
print(f"{'case':22s}{'who acted':14s}{'replayable':12s}{'answerable':>12}")
print("-" * 62)
for name, (tok, rep) in CASES.items():
    r = audit_record("merge_pr #8812", tok, rep)
    print(f"{name:22s}{r['acting_identity']:14s}{str(r['replayable']):12s}"
          f"{str(r['answerable']):>12}")

r = audit_record("merge_pr #8812", IMPERSONATED, GOOD_REPLAY)
print(f"\\nattribution-broken record: acting_identity={r['acting_identity']}")
print("The record is complete, internally consistent, and false. It says a human")
print("merged a pull request she never saw.")
assert not r["answerable"]
'''),
  ("md", "## 4 · The control — the auditability test, run as a drill"),
  ("py", '''def auditability_drill(records, sample_size=3):
    """Pick actions at random and try to produce the full record for each."""
    results = []
    for i, (action, tok, rep) in enumerate(records[:sample_size], 1):
        r = audit_record(action, tok, rep)
        gaps = []
        if r["acting_identity"] == r["on_behalf_of"]:
            gaps.append("acting identity not distinguishable from the principal")
        gaps += [f"replay missing {m}" for m in r["replay_gaps"]]
        results.append({"n": i, "action": action, "complete": not gaps, "gaps": gaps})
    passed = sum(r["complete"] for r in results)
    return results, passed, len(results)

SAMPLE = [
 ("merge_pr #8812", GOOD_TOKEN, GOOD_REPLAY),
 ("deploy prod",    IMPERSONATED, GOOD_REPLAY),
 ("rotate secret",  GOOD_TOKEN, NO_REPLAY),
]
rows, passed, total = auditability_drill(SAMPLE)
for r in rows:
    print(f"{r['n']}. {r['action']:18s}{'COMPLETE' if r['complete'] else 'INCOMPLETE'}")
    for g in r["gaps"]: print(f"      ⚠ {g}")
print(f"\\nauditability: {passed}/{total} sampled actions fully answerable "
      f"({passed/total:.0%})")
print("\\nRun this as a drill, quarterly, on randomly chosen production actions.")
print("The percentage is the number that goes in the evidence pack — and it is")
print("far more persuasive than a statement that logging is comprehensive.")
assert passed < total
'''),
 ],
 "expect": "The complete record names the acting identity, principal, chain and "
           "scopes and is replayable, so it is answerable. Impersonation produces "
           "a complete, consistent and false record attributing the merge to the "
           "human. Missing replay fields break the other half. The drill reports 1 "
           "of 3 sampled actions fully answerable.",
 "challenge": "Run the drill on three real production actions from last week. The "
              "field you cannot fill is your auditability gap, stated precisely — "
              "and a number like \"1 of 3\" is far more useful to a supervisor than "
              "a paragraph about comprehensive logging.",
},

"E2.9": {
 "concept": """
Conversations with regulators and auditors go well when you bring the number
that is weakest and explain it, and badly when you bring the strongest and let
them find the other one.

That is not a moral point, it is a practical one. A supervisor who discovers a
weakness you did not disclose now doubts everything else you said, and the rest
of the engagement is spent re-establishing credibility you had at the start.

Three things to bring, in this order:

1. **The distinction you understand.** Conformance versus accuracy (B2.11).
   Volunteering it demonstrates you know what your own numbers mean.
2. **Your current coverage, honestly stated**, including stale and unevidenced
   controls (E1.7).
3. **The control you have not deployed, and the date you will.**

The third one is the one people omit, and it is the one that most reliably
converts scepticism into a working relationship.
""",
 "steps": [
  ("md", "## 2 · Demo — produce the two numbers, then the coverage"),
  ("py", '''import json, time
from dataclasses import dataclass
now = time.time(); DAY = 86400

@dataclass
class Truth:
    qid: str; cwe: str; file: str

def path_key(p):
    parts = [x for x in p.replace("\\\\","/").split("/") if x not in ("",".")]
    return "/".join(parts[-2:]) if len(parts) > 1 else (parts[-1] if parts else "")

TRUTHS = {f"q{i}": Truth(f"q{i}", ["CWE-89","CWE-78"][i % 2],
                         f"{['CWE-89','CWE-78'][i % 2]}/{i}.py") for i in range(1, 21)}
ANSWERS = {q: json.dumps({"qid": q, "cwe": "CWE-89", "file": t.file,
                          "rationale": "untrusted input is concatenated"})
           for q, t in TRUTHS.items()}

def evaluate(answers, truths):
    conf = expert = 0
    for q, t in truths.items():
        try: d = json.loads(answers[q])
        except (json.JSONDecodeError, KeyError): continue
        conf += 1
        if path_key(d["file"]) != path_key(t.file): continue
        expert += 1.0 if d["cwe"].upper() == t.cwe else 0.5
    return {"n": len(truths), "conformance": round(conf/len(truths), 4),
            "expert_accuracy": round(expert/len(truths), 4)}

R = evaluate(ANSWERS, TRUTHS)
print(f"n                {R['n']}")
print(f"conformance      {R['conformance']:.4f}")
print(f"expert accuracy  {R['expert_accuracy']:.4f}")
'''),
  ("py", '''@dataclass
class ControlTest:
    cid: str; passed: bool; tested_at: float; valid_for_days: float
    def state(self, at):
        if (at - self.tested_at)/DAY > self.valid_for_days: return "STALE"
        return "PASS" if self.passed else "FAIL"

REQUIRED = ["AC-1","AC-2","SB-1","SB-2","EV-1","EV-2","DR-1","ST-1"]
TESTS = {t.cid: t for t in [
 ControlTest("AC-1", True,  now -  4*DAY, 30),
 ControlTest("AC-2", True,  now -  9*DAY, 30),
 ControlTest("SB-1", True,  now - 45*DAY, 30),
 ControlTest("EV-1", True,  now -  5*DAY, 60),
 ControlTest("EV-2", True,  now - 12*DAY, 30)]}

rows = [(c, TESTS[c].state(now) if c in TESTS else "NO EVIDENCE") for c in REQUIRED]
evidenced = sum(1 for _, s in rows if s == "PASS")
print(f"{'control':9s}{'state':14s}")
print("-" * 24)
for c, s in rows: print(f"{c:9s}{s:14s}")
print(f"\\ncoverage: {evidenced}/{len(REQUIRED)} = {evidenced/len(REQUIRED):.0%}")
'''),
  ("md", "## 3 · Where it breaks — leading with the strongest number"),
  ("py", '''OPENINGS = {
 "Our harness scores 100%.":
   ("conformance quoted as quality",
    "the follow-up 'against what key?' ends the credibility of the meeting"),
 "We have full coverage of our AI controls.":
   ("counts stale and untested as passing",
    "one date request exposes it"),
 "Conformance is 100%; expert accuracy is 50% against a held-out key of 20. "
 "Coverage is 63%, with SB-1 stale at 45 days and two controls not yet deployed.":
   ("both numbers, honestly",
    "nothing left for them to discover — the conversation moves to the plan"),
}
for text, (label, consequence) in OPENINGS.items():
    print(f"{label}")
    print(f'   "{text[:72]}{"…" if len(text) > 72 else ""}"')
    print(f"   → {consequence}\\n")
'''),
  ("md", "## 4 · The control — the disclosure script, generated from live state"),
  ("py", '''def disclosure(evalr, rows, required):
    evidenced = [c for c, s in rows if s == "PASS"]
    stale     = [c for c, s in rows if s == "STALE"]
    missing   = [c for c, s in rows if s == "NO EVIDENCE"]
    failing   = [c for c, s in rows if s == "FAIL"]
    plan = {"SB-1": "re-tested by 2026-08-31 (automation in progress)",
            "DR-1": "drift alerting deployed by 2026-10-15",
            "ST-1": "game day scheduled 2026-09-12"}
    lines = [
      f"1. Two numbers, and they measure different things.",
      f"   conformance {evalr['conformance']:.0%} — schema validity, structural, "
      f"not a quality claim.",
      f"   expert accuracy {evalr['expert_accuracy']:.0%} against a held-out key "
      f"of {evalr['n']} questions. That is the number that means something.",
      f"",
      f"2. Control coverage {len(evidenced)}/{len(required)} = "
      f"{len(evidenced)/len(required):.0%}, counting only controls that are "
      f"currently evidenced.",
      f"   stale: {stale or 'none'}   failing: {failing or 'none'}   "
      f"no evidence: {missing or 'none'}",
      f"",
      f"3. What we have not done, and when we will:",
    ]
    for c in stale + failing + missing:
        lines.append(f"   {c}: {plan.get(c, 'plan to be confirmed')}")
    return "\\n".join(lines)

print(disclosure(R, rows, REQUIRED))
print("\\nRehearse the second section out loud. If naming your weakest control is")
print("uncomfortable, that discomfort is the reason to say it first.")
assert R["expert_accuracy"] < R["conformance"]
'''),
 ],
 "expect": "Conformance is 1.0000 while expert accuracy is 0.5000 on a 20-question "
           "held-out key. Coverage is 5 of 8 with SB-1 stale and DR-1 and ST-1 "
           "unevidenced. The three openings show conformance-as-quality and "
           "inflated coverage failing on the first follow-up, and the generated "
           "disclosure script states both numbers, the stale and missing "
           "controls, and a date for each.",
 "challenge": "Generate this script from your own live control state rather than "
              "writing it. If it cannot be generated, your coverage number is "
              "being assembled by hand for each meeting — which is why it differs "
              "between meetings.",
},
}
