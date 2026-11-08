"""Function F as a hands-on lab: governance as numbers you can compute.

Same contract as `lab_a.py`. Each lab drives the module its lesson adds under
`cybertravels/governance/`, the way `cybertravels/tests/smoke_test.py` does.
F2.6 adds no code of its own; its lab uses the regulatory clock from E5.6,
which is already in the tree.
"""

LAB = {

"F1.0": {
 "goal": "Check that every property you claim for the AI has an owner and evidence.",
 "actors": ["Claim", "Owner", "Evidence", "Gap"],
 "steps": [
  {"title": "Who owns each property",
   "arrow": ("Claim", "Owner", "owners"),
   "say": ["Each property has an owning function, A to F, and a piece of evidence.",
           "Read the table."],
   "code": 'from cybertravels import governance as gov\nfor r in gov.owners():\n    print(f"{r[\'property\']:12} {r[\'function\']:24} {r[\'evidence\'][:40]}")\n',
   "expect": "secure       A                        cybertravels/policy.py, gateway.py, sand\ncorrect      B                        cybertravels/appsec/ — the pipeline that\nrobust       C                        cybertravels/redteam/campaign.py — a rat\nobservable   D                        cybertravels/soc/sensors.py — coverage p\naccountable  E                        cybertravels/governance/ — this package,\nprivate      E                        soc/sensors.py FIELD_RETENTION, per fiel\n"},
  {"title": "Properties nobody owns",
   "arrow": ("Owner", "Gap", "unowned"),
   "say": ["Claim the AI is fair and explainable.",
           "Nobody owns either. Those claims have nothing behind them."],
   "code": 'print(gov.unowned(["secure", "fair", "explainable"]))\n',
   "expect": "['explainable', 'fair']\n"},
 ]},

"F1.1": {
 "goal": "Turn a framework control into a number a computer can check.",
 "actors": ["Control", "Indicator", "Code", "Result"],
 "steps": [
  {"title": "A control as a number",
   "arrow": ("Control", "Indicator", "compute"),
   "say": ["Unclassified tools denied: measured by code, target 100%.",
           "It passes. Change the measured value to 0.5 and run it again."],
   "code": 'from cybertravels.governance import register as reg\nk = reg.KCI("B3.1", "unclassified tools denied", lambda: 1.0, 1.0, ">=", 7, "cybertravels/policy.py")\nprint(k.evaluate())\n',
   "expect": "{'control': 'B3.1', 'name': 'unclassified tools denied', 'value': 1.0, 'threshold': 1.0, 'direction': '>=', 'passes': True, 'source': 'cybertravels/policy.py', 'cadence_days': 7}\n"},
  {"title": "A sentence is not an indicator",
   "arrow": ("Code", "Result", "refused"),
   "say": ["Measured by asking an engineer.",
           "That cannot be computed, so it is refused."],
   "code": 'try:\n    reg.KCI("Y", "ask an engineer", "go and look", 1, ">=", 365, "s")\nexcept ValueError as e:\n    print("refused:", e)\n',
   "expect": "refused: Y: the measurement has to be computable. One that needs an engineer to go and look is taken once, at audit time, by somebody who knows what answer is wanted\n"},
 ]},

"F1.2": {
 "goal": "Build the list of AI agents from the system itself, and find the ones nobody registered.",
 "actors": ["Registry", "Inventory", "Running agents", "Shadow"],
 "steps": [
  {"title": "The inventory, from the registry",
   "arrow": ("Registry", "Inventory", "derive"),
   "say": ["Not a survey. The list comes from the registry, with who approved each.",
           "Every agent has an approver."],
   "code": 'from cybertravels.governance import register as reg\nfor r in reg.inventory():\n    print(r["spiffe_id"].rsplit("/", 1)[-1], "| approved by", r["approved_by"])\n',
   "expect": "coding | approved by alex\nfile-system | approved by alex\nrag-advisor | approved by alex\nworkflow | approved by alex\n"},
  {"title": "What is running that nobody listed",
   "arrow": ("Running agents", "Shadow", "compare"),
   "say": ["One agent is running with no record. Three are registered and not running.",
           "Both need someone to look."],
   "code": 'from cybertravels import config\ns = reg.shadow([config.AGENT_IDS["workflow"], "spiffe://cybertravels.local/agent/ghost"])\nprint("shadow agents:", s["shadow_count"], "| registered, not running:", len(s["registered_but_absent"]))\n',
   "expect": "shadow agents: 1 | registered, not running: 3\n"},
 ]},

"F1.3": {
 "goal": "Rate an AI use by what it can do, and see it disagree with rating by model name.",
 "actors": ["Use case", "Capability", "Model name", "Tier"],
 "steps": [
  {"title": "The workflow agent",
   "arrow": ("Capability", "Tier", "critical"),
   "say": ["It moves money, unattended, on customer data: critical.",
           "Rating by model name would say something else."],
   "code": 'from cybertravels.governance import register as reg\nt = reg.tier_the_workflow_agent()\nprint("by capability:", t["tier"], "| disagrees with model-name tiering:", t["disagrees"])\n',
   "expect": "by capability: critical | disagrees with model-name tiering: True\n"},
  {"title": "Your turn: rate a use",
   "arrow": ("Use case", "Model name", "tier"),
   "say": ["A tool that only suggests, on public data, with no effect outside.",
           "Change the three words and see the tier move."],
   "code": 'print(reg.tier("suggests", "public", "none"))\n',
   "expect": "{'tier': 'low', 'score': 0, 'inputs': {'autonomy': 'suggests', 'data_reach': 'public', 'external_effect': 'none'}, 'tier_by_model_name_would_say': 'medium', 'disagrees': True, 'why': 'the model is the least deployment-specific fact about a deployment; these three are properties of what was built'}\n"},
 ]},

"F1.4": {
 "goal": "Map your controls out to a regulation's clauses, and find the clauses nothing covers.",
 "actors": ["Controls", "Mapping", "Clauses", "Gap"],
 "steps": [
  {"title": "Two controls, three clauses",
   "arrow": ("Controls", "Clauses", "map"),
   "say": ["Map from your controls outward to the clauses.",
           "One clause has nothing behind it."],
   "code": 'from cybertravels.governance import register as reg\nm = reg.map_outward({"B3.1": ["Art. 15"], "B2.8": ["Art. 12"]}, ["Art. 12", "Art. 14", "Art. 15"])\nprint("uncovered:", m["clauses_uncovered"], "| coverage:", m["coverage"])\n',
   "expect": "uncovered: ['Art. 14'] | coverage: 0.667\n"},
  {"title": "Most agent risks need no new control",
   "arrow": ("Mapping", "Gap", "existing?"),
   "say": ["Agent access review is your existing access review.",
           "Marking where a prompt came from is genuinely new."],
   "code": 'for need in ("agent access review", "prompt provenance marking"):\n    r = reg.needs_a_new_control(need)\n    print(f"{need:26}", "NEW" if r["new"] else "existing: " + r["existing_control"])\n',
   "expect": "agent access review        existing: access review\nprompt provenance marking  NEW\n"},
 ]},

"F1.5": {
 "goal": "Decide whether an evaluation result can count as audit evidence.",
 "actors": ["Vendor", "Eval result", "Auditor", "Verdict"],
 "steps": [
  {"title": "A best-of-8 demo",
   "arrow": ("Vendor", "Eval result", "best of 8"),
   "say": ["The vendor ran it eight times and reported the best.",
           "That is not evidence of how the control behaves."],
   "code": 'from cybertravels.governance import evidence as ev\nr = ev.evidences({"best_of_k": 8, "accuracy": 0.91, "interval": (0.87, 0.94), "held_out": True})\nprint("usable:", r["usable_as_control_evidence"], "|", r["does_not_evidence"][0])\n',
   "expect": "usable: False | best-of-8 shows the system can produce this answer, not that it does. A control needs the rate\n"},
  {"title": "Conformance against accuracy",
   "arrow": ("Eval result", "Verdict", "which?"),
   "say": ["99.8% conformance only means the output had the right shape.",
           "82% accuracy on held-out data, with an interval, is evidence."],
   "code": 'for res in ({"conformance": 0.998, "interval": (0.9, 1.0), "held_out": True},\n            {"accuracy": 0.82, "interval": (0.78, 0.86), "held_out": True}):\n    print(res.get("accuracy", res.get("conformance")), "->", ev.evidences(res)["usable_as_control_evidence"])\n',
   "expect": "0.998 -> False\n0.82 -> True\n"},
 ]},

"F1.6": {
 "goal": "Sort guardrails into enforced, watched and just written down.",
 "actors": ["Guardrail", "Enforcement", "Measurement", "Status"],
 "steps": [
  {"title": "Three guardrails",
   "arrow": ("Guardrail", "Status", "classify"),
   "say": ["One is enforced by code. One is checked weekly. One is only a sentence.",
           "Only the first is in place."],
   "code": 'from cybertravels.governance import evidence as ev\nfor rule, kw in [("the agent may not act outside its authority", {"enforced_by": "policy.decide"}),\n                 ("the agent must not mislead", {"measured_by": "a weekly sample"}),\n                 ("the agent must be fair", {})]:\n    print(f"{rule:44}", ev.classify_guardrail(rule, enforced_by=kw.get("enforced_by"), measured_by=kw.get("measured_by"))["status"])\n',
   "expect": "the agent may not act outside its authority  in place\nthe agent must not mislead                   watched\nthe agent must be fair                       aspirational\n"},
 ]},

"F1.7": {
 "goal": "Collect control evidence automatically, and leave the verdict to a named person.",
 "actors": ["Control", "Collector", "Person", "Record"],
 "steps": [
  {"title": "Collected, not judged",
   "arrow": ("Collector", "Record", "evidence"),
   "say": ["The numbers are gathered by code.",
           "The verdict is left empty, for Priya."],
   "code": 'from cybertravels.governance import evidence as ev\nout = ev.collect("B3.1", lambda: {"denied": 12}, judged_by="priya")\nprint("collected:", out["artefact"], "| judgement:", out["judgement"], "| by:", out["judged_by"])\n',
   "expect": "collected: {'denied': 12} | judgement: None | by: priya\n"},
  {"title": "Nobody to judge it",
   "arrow": ("Person", "Control", "missing"),
   "say": ["With no named person, collection is refused.",
           "Automation gathers. People decide."],
   "code": 'try:\n    ev.collect("B3.1", lambda: {}, judged_by=None)\nexcept ValueError as e:\n    print("refused:", e)\n',
   "expect": "refused: B3.1: collection can be automated and judgement cannot. An adequacy verdict with no named human is a model grading a control on behalf of the people accountable for it\n"},
 ]},

"F1.8": {
 "goal": "Assess an AI vendor, and see the gap in who they pass your data to.",
 "actors": ["Vendor", "Sub-processors", "Assessment", "Decision"],
 "steps": [
  {"title": "A vendor with gaps",
   "arrow": ("Vendor", "Assessment", "assess"),
   "say": ["AI features on by default, training on your data, and no list of sub-processors.",
           "Not acceptable."],
   "code": 'from cybertravels.governance import evidence as ev\nbad = ev.assess_third_party({"name": "VendorCo", "ai_features_default_on": True, "trains_on_customer_data": True})\nprint("acceptable:", bad["acceptable"])\nfor g in bad["gaps"]:\n    print(" -", g)\n',
   "expect": "acceptable: False\n - AI features on by default — no purchase event triggered a review, so nothing was reviewed\n - no sub-processor list — the chain behind this vendor is where the data actually goes\n - trains on customer data; F2.5's deletion question has no good answer once it is in weights\n - no notification on model change — E1.2's first drift surface, on somebody else's schedule\n"},
  {"title": "A vendor that tells you",
   "arrow": ("Sub-processors", "Decision", "ok"),
   "say": ["This one lists its sub-processors and tells you when they change.",
           "Acceptable."],
   "code": 'print(ev.assess_third_party({"name": "Good", "sub_processors": ["a"], "change_notification": True})["acceptable"])\n',
   "expect": "True\n"},
 ]},

"F1.9": {
 "goal": "Find the changes to an agent that usually skip change management.",
 "actors": ["Change", "Agent", "Process", "Gap"],
 "steps": [
  {"title": "Re-indexing the search",
   "arrow": ("Change", "Agent", "behaviour"),
   "say": ["Rebuilding the search index changes what the agent does.",
           "It is usually filed as maintenance."],
   "code": 'from cybertravels.governance import evidence as ev\nprint(ev.is_a_change("retrieval_index"))\n',
   "expect": "{'surface': 'retrieval_index', 'changes_behaviour': True, 'usually_filed_as_maintenance': True, 'needs_change_record': True, 'why': 'the test is whether it alters what the system does, not whether it touched code'}\n"},
  {"title": "Every change that slips through",
   "arrow": ("Process", "Gap", "lifecycle"),
   "say": ["These three change behaviour and have no change record.",
           "Add them to your change process."],
   "code": 'print(sorted(ev.lifecycle_gaps()))\n',
   "expect": "['mcp_tool_descriptions', 'memory', 'retrieval_index']\n"},
 ]},

"F1.10": {
 "goal": "Map who owns each part of AI governance, and find what is shared or owned by nobody.",
 "actors": ["Teams", "Parts", "Seam", "Gap"],
 "steps": [
  {"title": "Owned, shared, unowned",
   "arrow": ("Teams", "Parts", "map"),
   "say": ["Each part of the work is owned, shared or unowned.",
           "Proof that a control works is owned by nobody."],
   "code": 'from cybertravels.governance import seams\nm = seams.seam_map()\nprint("unowned:", m["unowned"])\nprint("shared:", m["shared"])\n',
   "expect": "unowned: ['evidence that a control works', 'who may raise the autonomy of a deployment']\nshared: ['agent entitlements review', 'retention of agent telemetry', \"the system prompt's legal wording\"]\n"},
  {"title": "Why shared is risky",
   "arrow": ("Seam", "Gap", "risk"),
   "say": ["When two teams share something, each may think the other has it.",
           "Read the risk."],
   "code": 'row = next(r for r in m["parts"] if r["state"] == "shared")\nprint(row["risk"])\n',
   "expect": "each may believe the other has it\n"},
 ]},

"F1.11": {
 "goal": "Check whether model validation still covers a model that can act.",
 "actors": ["Model", "Validation", "Agent", "Retier"],
 "steps": [
  {"title": "Classic validation, for an acting model",
   "arrow": ("Validation", "Agent", "enough?"),
   "say": ["The classic checks are all done.",
           "But they say nothing about what the model is allowed to do."],
   "code": 'from cybertravels.governance import seams\nc = seams.validation_scope({"validated": ["conceptual soundness", "output accuracy", "input data quality",\n                                         "use within limitations", "ongoing monitoring"]})\nprint("valid for an acting model:", c["valid_for_an_acting_model"])\nprint("missing:", c["agentic_missing"])\n',
   "expect": "valid for an acting model: False\nmissing: ['action reversibility', 'adversarial reachability', 'authority', 'blast radius', 'containment']\n"},
  {"title": "It gained a new power",
   "arrow": ("Model", "Retier", "delta"),
   "say": ["It could read bookings. Now it can also issue refunds.",
           "That alone means it must be rated again."],
   "code": 'print(seams.capability_delta(["read bookings"], ["read bookings", "issue refunds"]))\n',
   "expect": "{'gained': ['issue refunds'], 'retier': True, 'why': 'more capability is a governance event even when the release note calls it an improvement'}\n"},
 ]},

"F1.12": {
 "goal": "Count which handoffs between teams actually produced something.",
 "actors": ["Team A", "Handoff", "Team B", "Artefact"],
 "steps": [
  {"title": "Two handoffs delivered",
   "arrow": ("Handoff", "Artefact", "delivered"),
   "say": ["The curriculum names handoffs between teams.",
           "Here, two produced an artefact. Count the rest."],
   "code": 'from cybertravels.governance import seams\nd = seams.delivered({"a retention parameter per telemetry field — E1.3",\n                     "an eval case, a control and a detection — D1.11"})\nprint(d["delivered"], "delivered of", len(seams.HANDOFFS), "| rate", d["rate"])\n',
   "expect": "2 delivered of 6 | rate 0.333\n"},
 ]},

"F1.13": {
 "goal": "Measure CyberTravels' controls from the code, then break one and watch the number drop.",
 "actors": ["Code", "Register", "Engineer", "Coverage"],
 "steps": [
  {"title": "Measure the tree",
   "arrow": ("Code", "Register", "measure"),
   "say": ["Every control in the register is checked against the code.",
           "Known gaps are listed, each with a mitigation."],
   "code": 'from cybertravels.governance import evidence as ev\nm = ev.measure()\nprint(m["controls"], "controls, coverage", m["coverage"], "|", len(m["known_gaps"]), "known gaps")\n',
   "expect": "8 controls, coverage 1.0 | 4 known gaps\n"},
  {"title": "Break the sandbox",
   "arrow": ("Engineer", "Coverage", "drops"),
   "say": ["Give the coding agent a cloud key in its sandbox.",
           "The control fails, and coverage drops."],
   "code": 'from cybertravels import sandbox\nsandbox.CODING_AGENT.env_keys.add("AWS_SECRET_ACCESS_KEY")\nbroken = ev.measure()\nsandbox.CODING_AGENT.env_keys.discard("AWS_SECRET_ACCESS_KEY")\nprint("failing:", broken["failing"], "| coverage:", round(broken["coverage"], 2))\n',
   "expect": "failing: ['B3.2'] | coverage: 0.88\n"},
 ]},

"F2.1": {
 "goal": "Map one set of controls to several regulations at once.",
 "actors": ["Controls", "Obligations", "Regimes", "Gap"],
 "steps": [
  {"title": "Six controls, many obligations",
   "arrow": ("Controls", "Obligations", "map"),
   "say": ["Some controls answer more than one regulation.",
           "Some obligations are still not met."],
   "code": 'from cybertravels.governance import regulatory as regu\nm = regu.map_obligations(["B2.8", "B2.7", "E1.3", "B3.6", "E4.2", "E5.6"])\nprint(m["satisfied"], "satisfied | unmet:", len(m["unmet"]), "| controls answering more than one:", m["controls_reused"]["answering_more_than_one"])\n',
   "expect": "5 satisfied | unmet: 5 | controls answering more than one: 2\n"},
 ]},

"F2.2": {
 "goal": "Find out whether you are a provider or a deployer, and test a requirement against evidence.",
 "actors": ["Company", "Role", "Requirement", "Evidence"],
 "steps": [
  {"title": "Fine-tuning changes your role",
   "arrow": ("Company", "Role", "which"),
   "say": ["Use a model as it is: deployer. Fine-tune or rebrand it: provider.",
           "Providers carry more duties."],
   "code": 'from cybertravels.governance import regulatory as regu\nfor facts in ({}, {"fine_tuned": True}, {"renamed_or_rebranded": True}):\n    print(facts or "used as is", "->", regu.role(facts)["role"])\n',
   "expect": "used as is -> deployer\n{'fine_tuned': True} -> provider\n{'renamed_or_rebranded': True} -> provider\n"},
  {"title": "Show me",
   "arrow": ("Requirement", "Evidence", "show me"),
   "say": ["A requirement with no artefact fails show me.",
           "One backed by the audit hash chain passes."],
   "code": 'print(regu.requirement_to_control("be transparent", evidence_artefact=None)["passes_show_me"])\nprint(regu.requirement_to_control("keep records", evidence_artefact="db.audit hash chain")["passes_show_me"])\n',
   "expect": "False\nTrue\n"},
 ]},

"F2.3": {
 "goal": "Pick the framework that covers most of your controls as your backbone.",
 "actors": ["Frameworks", "Controls", "Spine", "Gap"],
 "steps": [
  {"title": "Choose the spine",
   "arrow": ("Frameworks", "Spine", "most coverage"),
   "say": ["Three frameworks, four controls.",
           "The one covering most of yours is the spine. List what it misses."],
   "code": 'from cybertravels.governance import regulatory as regu\ns = regu.choose_spine({"ISO 42001": ["B2.8", "B3.1", "E1.3"], "NIST AI RMF": ["B3.1"], "SOC 2": ["B2.8", "E2.2"]},\n                      ["B2.8", "B3.1", "E1.3", "D1.0"])\nprint("spine:", s["spine"], "| not covered:", s["not_covered_by_the_spine"])\n',
   "expect": "spine: ISO 42001 | not covered: ['D1.0']\n"},
 ]},

"F2.4": {
 "goal": "See which sector rules already apply to AI, without a new AI law.",
 "actors": ["Sector", "Rules", "AI system", "Overlay"],
 "steps": [
  {"title": "Financial services",
   "arrow": ("Sector", "Overlay", "already?"),
   "say": ["Banks already have model risk rules. An AI system is a model.",
           "Much of the work is already required."],
   "code": 'from cybertravels.governance import regulatory as regu\nfs = regu.overlays("financial services")\nfor o in fs["overlays"]:\n    print("-", o["regime"])\n',
   "expect": "- SR 11-7 / model risk\n- DORA\n"},
 ]},

"F2.5": {
 "goal": "Check where a traveller's data can and cannot be erased, and scan the audit log for it.",
 "actors": ["Traveller", "Erasure", "Audit log", "Scanner"],
 "steps": [
  {"title": "Where erasure reaches",
   "arrow": ("Traveller", "Erasure", "forget me"),
   "say": ["Some stores can delete a person. Some cannot.",
           "Fine-tuned model weights are the hardest."],
   "code": 'from cybertravels.governance import regulatory as regu\nr = regu.erasure_reach()\nprint("coverage:", r["coverage"], "| cannot erase:", r["not_erasable"])\n',
   "expect": "coverage: 0.714 | cannot erase: [\"model provider's logs\", 'model weights (if fine-tuned)']\n"},
  {"title": "Personal data in the audit log",
   "arrow": ("Audit log", "Scanner", "scan"),
   "say": ["An email address slipped into an audit row.",
           "The scanner finds it."],
   "code": 'print(regu.scan_text("contact dana@example.com re CT-4417"))\nprint("clean:", regu.audit_trace([{"detail": "refund for dana@example.com", "chain": "dana => spiffe://x"}])["clean"])\n',
   "expect": "['a booking reference', 'email address']\nclean: False\n"},
 ]},

"F2.6": {
 "goal": "Work out which incident reporting deadlines apply, and when they start.",
 "actors": ["Incident", "Facts", "Clock", "Deadline"],
 "steps": [
  {"title": "A financial firm, significant, with personal data",
   "arrow": ("Facts", "Clock", "which apply"),
   "say": ["This uses the regulatory clock from E5.6.",
           "Every deadline starts when you become aware."],
   "code": 'import time\nfrom cybertravels.soc import recover as rec\nc = rec.clock_check(time.time(), personal_data=True, significant=True, financial_entity=True, listed=False)\nfor r in c["running"]:\n    print(f"{r[\'regime\']:22} {r[\'hours\']} hours")\n',
   "expect": "DORA major ICT         4 hours\nNIS2 early warning     24 hours\nGDPR Art. 33           72 hours\n"},
 ]},

"F2.7": {
 "goal": "Score your documentation against what a supervisor asks for.",
 "actors": ["Documentation", "Sections", "Supervisor", "Score"],
 "steps": [
  {"title": "Two sections out of many",
   "arrow": ("Documentation", "Score", "score"),
   "say": ["Intended purpose and authority are written. The run record is not.",
           "The score is low, and the missing parts are named."],
   "code": 'from cybertravels.governance import regulatory as regu\ns = regu.score_documentation(["intended purpose", "authority"])\nprint("score:", s["score"], "| missing:", s["missing"])\n',
   "expect": "score: 0.333 | missing: {'bounds': 'budgets, scopes, the human gate and where each is enforced', 'run record': 'what happened on a specific date, reconstructable', 'decisions': 'who approved the autonomy level, and when', 'known limitations': \"including the ones in F1.13's known_gaps\"}\n"},
 ]},

"F2.8": {
 "goal": "Answer a regulator's question about one autonomous action, from the record.",
 "actors": ["Regulator", "Audit log", "Trace", "Answer"],
 "steps": [
  {"title": "A complete record",
   "arrow": ("Audit log", "Answer", "auditable"),
   "say": ["Who, which agent, which tool, why, and every step.",
           "The question can be answered."],
   "code": 'from cybertravels.governance import regulatory as regu\nrows = [{"chain": "priya => spiffe://ct/agent/workflow", "tool": "issue_refund", "motive_origin": "vendor-document"}]\nspans = [{"kind": k} for k in ("start", "plan", "token_issued", "tool_result", "done")]\nprint(regu.auditability(rows, spans, lambda: (True, None))["answerable"])\n',
   "expect": "True\n"},
  {"title": "A broken chain",
   "arrow": ("Regulator", "Trace", "blocked"),
   "say": ["Now the log's hash chain breaks at row 3.",
           "The answer cannot be trusted."],
   "code": 'b = regu.auditability(rows, spans, lambda: (False, 3))\nprint(b["answerable"], b["blockers"])\n',
   "expect": "False ['the audit chain breaks at row 3']\n"},
 ]},

"F2.9": {
 "goal": "Prepare for a regulator meeting: accuracy and conformance apart, gaps first.",
 "actors": ["Evidence", "Briefing", "Regulator", "Openings"],
 "steps": [
  {"title": "Prepare the briefing",
   "arrow": ("Evidence", "Briefing", "prepare"),
   "say": ["Accuracy and conformance are reported separately. Gaps are named first.",
           "Then three ways to open the conversation."],
   "code": 'from cybertravels.governance import evidence as ev, regulatory as regu\np = regu.prepare(ev.measure(), {"accuracy": 0.82, "conformance": 0.998, "interval": (0.78, 0.86), "held_out": True})\nprint("accuracy", p["accuracy"], "| conformance", p["conformance"], "| gaps first:", p["gaps_named_up_front"])\nfor o in p["openings"]:\n    print("-", o)\n',
   "expect": "accuracy 0.82 | conformance 0.998 | gaps first: ['containment and egress are decided in-process', 'the kill switch is not on the direct API path', 'no audit column carries the attestation digest', 'sandbox-egress and injection-screening cannot be proven here']\n- show me a specific action and tell me who authorised it\n- what does this system do that you cannot explain\n- what would have to go wrong for you to stop it\n"},
 ]},

"F3.1": {
 "goal": "Turn an engineering risk into a sentence for the board.",
 "actors": ["Engineer", "Translation", "Board", "Number"],
 "steps": [
  {"title": "From scope to money",
   "arrow": ("Engineer", "Translation", "translate"),
   "say": ["12 refunds a run, 5,000 each, not reversible, caught in 5 minutes.",
           "Change the numbers and read both sentences."],
   "code": 'from cybertravels.governance import programme as prog\nt = prog.translate(scope="payments:refund", max_calls=12, amount_per_call=5000, reversible=False, detected_in=5)\nprint("engineering:", t["engineering_sentence"])\nprint("board:      ", t["board_sentence"])\n',
   "expect": "engineering: the agent holds payments:refund with a ceiling of 12 calls per run\nboard:       one compromised run can move up to 60,000 before any human is involved; it is not recoverable and we would know within 5 minutes\n"},
 ]},

"F3.2": {
 "goal": "Approve autonomy by level, based on what could go wrong, not by tool.",
 "actors": ["Team", "Request", "Rung", "Approval"],
 "steps": [
  {"title": "Asking for too much",
   "arrow": ("Team", "Request", "rung 4"),
   "say": ["The team asks for level 4. Not reversible, attended, low volume supports level 3.",
           "Approve at 3."],
   "code": 'from cybertravels.governance import programme as prog\nr = prog.request({"requested_rung": 4, "reversible": False, "unattended": False, "volume": "low"})\nprint("asked 4, supported", r["supported_by_blast_radius"], "-> approve at", r["approve_at"])\n',
   "expect": "asked 4, supported 3 -> approve at 3\n"},
  {"title": "The levels",
   "arrow": ("Rung", "Approval", "ladder"),
   "say": ["Each level, from suggest to fully unattended.",
           "The top one is not granted."],
   "code": 'for n, what, approval in prog.RUNGS:\n    print(n, "|", what, "|", approval)\n',
   "expect": "0 | suggests to a person | no approval needed\n1 | acts on reversible things, logged | team lead, one page\n2 | acts on reversible things at volume | the autonomy board, with a measured containment time\n3 | acts on irreversible things with a human gate | the autonomy board, plus E4.2's real decision point\n4 | acts on irreversible things unattended | not granted in this system; B3.6 says the gate stops working before this\n"},
 ]},

"F3.3": {
 "goal": "Choose the first workflow to win, not the most visible one.",
 "actors": ["Options", "Score", "Order", "Programme"],
 "steps": [
  {"title": "Demo or refund triage",
   "arrow": ("Options", "Order", "sequence"),
   "say": ["A board demo is visible and hard, and reuses nothing.",
           "Refund triage is easy and builds controls later work reuses. It goes first."],
   "code": 'from cybertravels.governance import programme as prog\ns = prog.sequence([{"name": "board demo", "visibility": 5, "difficulty": 5, "control_reuse": 0},\n                   {"name": "refund triage", "visibility": 1, "difficulty": 1, "control_reuse": 4}])\nprint(s["order"])\n',
   "expect": "['refund triage', 'board demo']\n"},
 ]},

"F3.4": {
 "goal": "Find the functions in your organisation that nobody owns.",
 "actors": ["Org chart", "Functions", "Owners", "Gap"],
 "steps": [
  {"title": "Two functions with no home",
   "arrow": ("Functions", "Gap", "homeless"),
   "say": ["Harness engineering and red teaming have no owner.",
           "Read what happens to them."],
   "code": 'from cybertravels.governance import programme as prog\no = prog.ownership()\nprint(o["homeless"])\nprint(o["why"])\n',
   "expect": "['harness engineering', 'red team / research']\nneither of these fails loudly; they quietly do not happen, and the first evidence is an incident nobody had the tooling to investigate\n"},
 ]},

"F3.5": {
 "goal": "Replace a busy-work metric with one that measures exposure.",
 "actors": ["Metric", "Activity", "Exposure", "Leader"],
 "steps": [
  {"title": "Agents reviewed",
   "arrow": ("Metric", "Exposure", "replace"),
   "say": ["Counting reviews shows effort, not safety.",
           "Each activity metric has an exposure metric to use instead."],
   "code": 'from cybertravels.governance import programme as prog\nfor m in prog.INSTEAD_OF:\n    print(f"{m:26} ->", prog.replace(m)["exposure_metric"])\n',
   "expect": "agents reviewed            -> agents running at a rung above what their blast radius supports\nfindings closed            -> findings that became an eval case, a control and a detection — D1.11's durability\nalerts triaged             -> the floor miss rate — what the closing rule missed\ncontrols implemented       -> control coverage measured against the tree, with the gaps named — F1.13\npolicies published         -> obligations satisfied by controls that exist\ntraining completed         -> time to stop, measured from a real attempt\n"},
 ]},

"F3.6": {
 "goal": "Say yes with conditions that can be tested, have a date, and have a consequence.",
 "actors": ["Request", "Condition", "Owner", "Approval"],
 "steps": [
  {"title": "A weak condition and a strong one",
   "arrow": ("Condition", "Approval", "real?"),
   "say": ["Improve logging has no test, no date, no consequence. It is a wish.",
           "Sensor coverage above 0.9 by a date, or the level drops, is a condition."],
   "code": 'from cybertravels.governance import programme as prog\nweak = prog.condition("improve logging", testable_by=None, due=None, owner="alex", consequence=None)\nstrong = prog.condition("sensor coverage above 0.9", testable_by="soc.sensors.matrix()", due="2026-12-01",\n                        owner="alex", consequence="the rung drops to 1")\nprint("weak real:", weak["real"], "missing", weak["missing"])\nprint("strong real:", strong["real"])\nprint("approval enforceable with both:", prog.approve_with([weak, strong])["enforceable"])\n',
   "expect": "weak real: False missing ['testable_by', 'due', 'consequence']\nstrong real: True\napproval enforceable with both: False\n"},
 ]},

"F3.7": {
 "goal": "Order the build so each step has somewhere to land.",
 "actors": ["Team", "Order", "Red team", "Result"],
 "steps": [
  {"title": "Controls first, red team last",
   "arrow": ("Team", "Order", "build"),
   "say": ["Start with inventory and tiering. The red team comes last.",
           "Its findings then have controls to land in."],
   "code": 'from cybertravels.governance import programme as prog\nprint(prog.build_order()["order"])\n',
   "expect": "['inventory and tiering', 'control baseline and KCIs', 'detection and telemetry', 'harness engineering', 'red team']\n"},
  {"title": "Demos first",
   "arrow": ("Red team", "Result", "nowhere to land"),
   "say": ["Put the red team first and see what that produces.",
           "Findings with nowhere to go."],
   "code": 'print(prog.build_order(demos_first=True)["produces"])\n',
   "expect": "a sequence of striking findings with nowhere to land, and a control baseline nobody built\n"},
 ]},

"F3.8": {
 "goal": "Report resilience as four numbers the curriculum has taught you to produce.",
 "actors": ["SOC", "Numbers", "Leader", "Next time"],
 "steps": [
  {"title": "The four numbers",
   "arrow": ("SOC", "Numbers", "readiness"),
   "say": ["Time to detect, time to stop, containment coverage, and whether you can rebuild what happened.",
           "With all four, you can say how resilient you are."],
   "code": 'from cybertravels.governance import programme as prog\nr = prog.readiness({"time_to_detect": 5, "time_to_stop": 14, "containment_coverage": 0.4, "reconstructable": True})\nprint("resilient:", r["resilient"])\nprint("with one number:", prog.readiness({"time_to_detect": 5})["unanswered"])\n',
   "expect": "resilient: True\nwith one number: {'time_to_stop': 'E4.4, from a real attempt', 'containment_coverage': 'D1.9 — which act-paths the stop is on', 'reconstructable': 'D1.10 — can the run be defended afterwards'}\n"},
  {"title": "What lasts",
   "arrow": ("Leader", "Next time", "durable"),
   "say": ["Three of ten findings were turned into lasting controls.",
           "The other seven will happen again."],
   "code": 'print(prog.durable(3, 10))\n',
   "expect": "{'durability': 0.3, 'repeated_next_time': 7, 'why': 'the rest will be rediscovered by the next engagement at full price, and reported as a new finding'}\n"},
 ]},
}
