"""Function C as a hands-on lab: the AppSec pipeline, one stage per lesson.

Same contract as `lab_a.py`: real Python against the CyberTravels tree as it
stood at the end of the lesson, no step asks a model anything, and every
`expect` was produced by running the code (`build_lab.py --check` reruns it).
Each lab drives the pipeline stage its lesson adds under `cybertravels/appsec/`,
the way `cybertravels/tests/smoke_test.py` does. The exploits run against a
disposable replica the code builds itself; nothing reaches the network or a
shell.
"""

_TREE = ('import pathlib\nfrom cybertravels import config\n'
         'TREE = str(pathlib.Path(config.__file__).parent)\n')

LAB = {

"C2.0": {
 "goal": "See the pipeline's stages, and what each one is allowed to claim.",
 "actors": ["Code", "Before deploy", "After deploy", "Report"],
 "steps": [
  {"title": "The stages, before and after deploy",
   "arrow": ("Code", "Before deploy", "stages"),
   "say": ["The pipeline is a list of stages. Some run before a deploy, some after.",
           "Count them."],
   "code": 'from cybertravels import appsec\nprint(len(appsec.stages("before")), "before deploy,", len(appsec.stages("after")), "after")\n',
   "expect": "5 before deploy, 6 after\n"},
  {"title": "What a stage may say",
   "arrow": ("After deploy", "Report", "claims"),
   "say": ["Each stage may only claim what it can show.",
           "Stage 10 cannot say something was exploited. Stage 12 can."],
   "code": 'for n in (10, 12):\n    print(n, "->", appsec.claim_for(n))\n',
   "expect": "10 -> an external caller can, or cannot, reach this sink\n12 -> this was exploited, here is the request and the response\n"},
 ]},

"C2.1": {
 "goal": "Try to let a security harness check its own work, and see it refuse.",
 "actors": ["Producer", "Harness", "Verifier", "Budget"],
 "steps": [
  {"title": "One function as producer and checker",
   "arrow": ("Producer", "Harness", "same callable"),
   "say": ["The same function finds problems and then confirms them.",
           "The harness refuses. Nothing should grade its own work."],
   "code": 'from cybertravels.appsec import findings as fnd\ndef both(_=None):\n    return []\ntry:\n    fnd.run(both, both)\nexcept fnd.HarnessError as e:\n    print("refused:", e)\n',
   "expect": "refused: the producer and the verifier are the same callable — a harness that grades its own work reports a clean run either way\n"},
  {"title": "A checker that cannot say I don't know",
   "arrow": ("Verifier", "Harness", "probably"),
   "say": ["A checker must be able to answer undetermined.",
           "One that only says probably is refused."],
   "code": 'f = fnd.Finding("x.py", 1, "u", "CWE-1", basis="test", stage=7)\ntry:\n    fnd.run(lambda: [f], lambda _: "probably")\nexcept fnd.HarnessError as e:\n    print("refused:", e)\n',
   "expect": "refused: a verifier returned 'probably'; it must be able to say 'undetermined', because one that cannot abstain guesses\n"},
 ]},

"C2.2": {
 "goal": "Build a threat model from the code itself, then see it notice when the code changes.",
 "actors": ["Code", "Threat model", "Analyst", "Drift"],
 "steps": [
  {"title": "Read the threat model out of the code",
   "arrow": ("Code", "Threat model", "build"),
   "say": ["Assets and entry points come from the tree, not from memory.",
           "Some assets are left unclassified. A person has to judge those."],
   "code": _TREE + 'from cybertravels.appsec import threatmodel\nm = threatmodel.build(TREE)\nprint(len(m["assets"]), "assets,", len(m["entry_points"]), "entry points")\nprint("left for a person:", [a["asset"] for a in m["assets"] if a["why_an_attacker_cares"].startswith("UNCLASSIFIED")])\n',
   "expect": "7 assets, 13 entry points\nleft for a person: ['policies']\n"},
  {"title": "Is the model out of date?",
   "arrow": ("Threat model", "Drift", "compare"),
   "say": ["Take an old model that is missing two entry points.",
           "The check lists exactly what changed."],
   "code": 'stale = dict(m, entry_points=m["entry_points"][:-2])\nd = threatmodel.drift(stale, TREE)\nprint("stale:", d["stale"], "| new entry points:", len(d["entry_points_added"]))\n',
   "expect": "stale: True | new entry points: 2\n"},
 ]},

"C2.3": {
 "goal": "Scan the code with fixed rules, and see what rules can and cannot find.",
 "actors": ["Code", "Rules", "Findings", "Analyst"],
 "steps": [
  {"title": "Run the rule-based scan",
   "arrow": ("Code", "Rules", "scan"),
   "say": ["Fixed rules find patterns: SQL built from strings, eval, shell commands.",
           "Each finding names the file, the function and the weakness."],
   "code": _TREE + 'from cybertravels.appsec import sast\nfor f in sorted(sast.scan(TREE), key=lambda f: f.unit):\n    print(f"{f.cwe:8} {f.unit}")\n',
   "expect": "CWE-78   _open_branch\nCWE-22   download_invoice\nCWE-95   render_template\nCWE-89   search_bookings\nCWE-295  sync_vendor\n"},
  {"title": "What no rule can find",
   "arrow": ("Rules", "Analyst", "not reachable"),
   "say": ["A missing owner check is the absence of a line. There is nothing to match.",
           "The scan says so, and lists those functions for a model or a person."],
   "code": 'print(sorted({u for _f, u, _c in sast.unreachable_by_pattern()}))\n',
   "expect": "['cancel_booking', 'download_invoice', 'get_booking', 'issue_refund', 'search_bookings']\n"},
 ]},

"C2.4": {
 "goal": "Merge three reports of one bug into one, and throw out a report about code that does not exist.",
 "actors": ["Scanners", "Dedup", "Code", "Queue"],
 "steps": [
  {"title": "Three tools, one bug",
   "arrow": ("Scanners", "Dedup", "merge"),
   "say": ["A rule, a model and a taint check all report the same SQL injection.",
           "It becomes one finding that remembers all three."],
   "code": 'from cybertravels.appsec import findings as fnd\nsame = [fnd.Finding("tools/bookings_api.py", 41, "search_bookings", "CWE-89", basis=b, stage=7)\n        for b in ("rule:sql-concat", "model:read", "dep:taint")]\nmerged = fnd.dedup(same)\nprint(len(merged), "finding, found by", fnd.bases(merged[0]), "tools")\n',
   "expect": "1 finding, found by 3 tools\n"},
  {"title": "A finding about a function nobody wrote",
   "arrow": ("Code", "Queue", "refuted"),
   "say": ["A model reports a bug in delete_booking. There is no such function.",
           "It is refuted before anyone wastes time on it."],
   "code": 'real = fnd.Finding("tools/bookings_api.py", 17, "get_booking", "CWE-639", basis="model:read", stage=7)\nghost = fnd.Finding("tools/bookings_api.py", 60, "delete_booking", "CWE-639", basis="model:read", stage=7)\nkept, rejected = fnd.cross_reference([real, ghost], {"tools/bookings_api.py": {"get_booking", "get_my_booking"}})\nprint("kept:", [f.unit for f in kept], "| refuted:", [f.unit for f in rejected])\n',
   "expect": "kept: ['get_booking'] | refuted: ['delete_booking']\n"},
 ]},

"C2.5": {
 "goal": "Mark which findings an outsider can actually reach, without deleting any.",
 "actors": ["Findings", "Call graph", "Entry points", "Report"],
 "steps": [
  {"title": "Build the call graph",
   "arrow": ("Entry points", "Call graph", "reachable"),
   "say": ["Follow calls from every entry point.",
           "A function on that path can be reached from outside."],
   "code": _TREE + 'from cybertravels.appsec import sast, reach\ng = reach.build(TREE)\nlive = g.reachable()\nprint("download_invoice reachable:", "download_invoice" in live)\n',
   "expect": "download_invoice reachable: True\n"},
  {"title": "Mark, do not delete",
   "arrow": ("Findings", "Report", "rank"),
   "say": ["Two findings sit in code nothing calls.",
           "They are marked unreachable, and every finding is still there."],
   "code": 'found = sast.scan(TREE)\nr = reach.report(found, g)\nprint(r["findings"], "findings kept | unreachable:", sorted(r["unreachable_units"]))\n',
   "expect": "5 findings kept | unreachable: ['render_template', 'sync_vendor']\n"},
 ]},

"C2.6": {
 "goal": "Build a throwaway copy to test in, and see it refuse to be a shared environment.",
 "actors": ["Tester", "Replica", "Staging", "Disk"],
 "steps": [
  {"title": "Refuse a shared environment",
   "arrow": ("Tester", "Staging", "refused"),
   "say": ["Testing exploits in staging hurts other people.",
           "The replica refuses any name that is not disposable."],
   "code": 'from cybertravels.appsec import replica as rep\nfor name in ("cybertravels-staging", "prod-eu"):\n    try:\n        rep.for_target(name)\n    except rep.NotDisposable:\n        print(name, "-> refused")\n',
   "expect": "cybertravels-staging -> refused\nprod-eu -> refused\n"},
  {"title": "Use it, then it is gone",
   "arrow": ("Replica", "Disk", "close"),
   "say": ["A local replica is created for the run.",
           "When the run ends, it is deleted."],
   "code": 'r = rep.for_target("local-replica")\nprint("exists:", r.path.exists())\nr.close()\nprint("after close:", r.path.exists())\n',
   "expect": "exists: True\nafter close: False\n"},
 ]},

"C2.7": {
 "goal": "Compare what the code imports with what the project says it needs.",
 "actors": ["Manifest", "Code", "Checker", "Report"],
 "steps": [
  {"title": "Imports against the manifest",
   "arrow": ("Code", "Checker", "imports"),
   "say": ["Every import should be in requirements.txt, unless it is standard library.",
           "A local folder called mcp shadows the real mcp package. That is reported too."],
   "code": _TREE + 'import sys\nfrom cybertravels.appsec import supplychain\nr = supplychain.reconcile(f"{TREE}/requirements.txt", TREE, stdlib=sys.stdlib_module_names)\nprint("imported, not declared:", r["undeclared_but_imported"])\nprint("shadowed:", r["shadowed"])\n',
   "expect": "imported, not declared: []\nshadowed: ['mcp']\n"},
  {"title": "Package name is not import name",
   "arrow": ("Manifest", "Report", "pyjwt = jwt"),
   "say": ["You install PyJWT but import jwt.",
           "The check knows the mapping, so it does not report a false gap."],
   "code": 'print(supplychain.DISTRIBUTION_TO_IMPORT["pyjwt"])\nprint("jwt" in supplychain.declared(f"{TREE}/requirements.txt"))\n',
   "expect": "jwt\nTrue\n"},
 ]},

"C2.8": {
 "goal": "Run three exploits against a throwaway replica and see which really work.",
 "actors": ["Tester", "Replica", "Database", "Report"],
 "steps": [
  {"title": "Fire the exploits",
   "arrow": ("Tester", "Replica", "exploit"),
   "say": ["SQL injection, reading someone else's booking, and escaping a folder.",
           "Each runs against the replica's own copy of the data."],
   "code": 'from cybertravels import config, db\nfrom cybertravels.appsec import replica as rep\nwas = config.DB_PATH\nwith rep.for_target("local-replica") as r:\n    live = rep.isolated_db(r)\n    sqli = rep.exploit_sql_injection(live)\n    idor = rep.exploit_idor(live)\n    trav = rep.exploit_path_traversal(live, r)\nconfig.DB_PATH = was\ndb.reset()\nprint("SQL injection rows:", sqli["rows_honest"], "->", sqli["rows_injected"])\nprint("IDOR read a booking owned by", idor["owner"], "as", idor["caller"])\nprint("path traversal escaped:", trav["escaped"])\n',
   "expect": "SQL injection rows: 1 -> 4\nIDOR read a booking owned by priya as dana\npath traversal escaped: True\n"},
  {"title": "An exploit that did not fire proves nothing",
   "arrow": ("Replica", "Report", "undetermined"),
   "say": ["If an exploit does not work, that does not mean the code is safe.",
           "It is reported as undetermined, not refuted."],
   "code": 'print(rep.verdict_from(None))\n',
   "expect": "undetermined\n"},
 ]},

"C2.9": {
 "goal": "Chain three medium findings into one critical one, and refuse a chain with an unproven link.",
 "actors": ["Findings", "Chain", "Score", "Report"],
 "steps": [
  {"title": "Three mediums make a critical",
   "arrow": ("Findings", "Chain", "link"),
   "say": ["A vendor filename reaches a file reader, in a process that can reach a shell.",
           "Each step is medium. Together they are critical."],
   "code": 'from cybertravels.appsec import findings as fnd\ndef link(unit, file, cwe):\n    f = fnd.Finding(file, 1, unit, cwe, basis="dast", stage=12)\n    f.verdict, f.severity = "confirmed", "medium"\n    return f\nlinks = [link("handle", "agents/file_agent.py", "CWE-20"),\n         link("download_invoice", "tools/payments_api.py", "CWE-22"),\n         link("_open_branch", "agents/coding_agent.py", "CWE-78")]\nbuilt = fnd.chains(links, [("vendor file to a shell", [(f.file, f.unit) for f in links], "")])\nprint(len(built), "chain, scored", built[0].score())\n',
   "expect": "1 chain, scored critical\n"},
  {"title": "One unproven link breaks the chain",
   "arrow": ("Chain", "Report", "refused"),
   "say": ["If one link is only a guess, there is no chain. It is a story.",
           "Nothing is built."],
   "code": 'a = fnd.Finding("x.py", 1, "a", "CWE-1", basis="dast", stage=12)\nb = fnd.Finding("x.py", 2, "b", "CWE-2", basis="model", stage=7)\na.verdict = "confirmed"\nprint(len(fnd.chains([a, b], [("story", [("x.py", "a"), ("x.py", "b")], "")])), "chains built")\n',
   "expect": "0 chains built\n"},
 ]},

"C2.10": {
 "goal": "Give an agent pentester a scope, and see the boundary hold whatever it tries.",
 "actors": ["Pentest agent", "Scope", "In scope", "Out of scope"],
 "steps": [
  {"title": "One host in scope, two not",
   "arrow": ("Pentest agent", "Scope", "check"),
   "say": ["The scope is enforced in code, not written into a prompt.",
           "A vendor host and the excluded payments system are refused."],
   "code": 'from cybertravels.appsec import pentest\nscope = pentest.Scope(["*.cybertravels.local"], exclude=["payments.cybertravels.local"])\nfor url in ("https://api.cybertravels.local/v1/bookings", "https://api.northwind-rail.example/x",\n            "https://payments.cybertravels.local/x"):\n    try:\n        scope.check(url)\n        print("allowed ", url)\n    except pentest.OutOfScope:\n        print("refused ", url)\n',
   "expect": "allowed  https://api.cybertravels.local/v1/bookings\nrefused  https://api.northwind-rail.example/x\nrefused  https://payments.cybertravels.local/x\n"},
  {"title": "The record of the engagement",
   "arrow": ("Scope", "Out of scope", "report"),
   "say": ["Every refusal is counted.",
           "That record is part of the engagement report."],
   "code": 'r = scope.report()\nprint(r["in_scope_calls"], "in scope,", len(r["refused"]), "refused")\n',
   "expect": "1 in scope, 2 refused\n"},
 ]},

"C2.11": {
 "goal": "With the source in hand, check whether an outsider can reach each weak spot.",
 "actors": ["Source", "Call graph", "Finding", "Report"],
 "steps": [
  {"title": "A sink nobody can reach",
   "arrow": ("Call graph", "Report", "unreachable"),
   "say": ["The eval in render_template is real, but nothing calls it.",
           "It is reported as unreachable, not dropped."],
   "code": _TREE + 'from cybertravels.appsec import sast, reach, pentest\ng = reach.build(TREE)\nfound = {f.unit: f for f in sast.scan(TREE)}\nprint(pentest.candidate(found["render_template"], g, "def x(): pass")["report_as"])\n',
   "expect": "unreachable — reported, not dropped\n"},
  {"title": "A sink an outsider can reach",
   "arrow": ("Source", "Finding", "entry points"),
   "say": ["The SQL injection is reachable.",
           "It comes with the entry points that lead to it."],
   "code": 'live = pentest.candidate(found["search_bookings"], g, "def x(): pass")\nprint("reachable:", live["reachable"], "| from:", live["entry_points"])\n',
   "expect": "reachable: True | from: ['handle', 'search_bookings']\n"},
 ]},

"C2.12": {
 "goal": "Report what you saw separately from what you guessed, from outside the system.",
 "actors": ["Tester", "Observation", "Inference", "Report"],
 "steps": [
  {"title": "A guess cannot be rated",
   "arrow": ("Inference", "Report", "no severity"),
   "say": ["You saw a 403. You guessed the database from response times.",
           "The observation can be rated. The guess cannot."],
   "code": 'from cybertravels.appsec import pentest\nseen = pentest.Claim("the booking API returns 403 for other owners", "observed", ["HTTP 403 on GET /bookings/2"])\nseen.rate("low")\nguess = pentest.Claim("the backend is Postgres", "inferred", ["response timing"])\ntry:\n    guess.rate("high")\nexcept ValueError as e:\n    print("refused:", e)\n',
   "expect": "refused: cannot rate an inference: 'the backend is Postgres' was reasoned from ['response timing'], not seen. Go and observe it, or report it as an inference with no severity\n"},
  {"title": "How much of the report is guessing",
   "arrow": ("Observation", "Report", "ratio"),
   "say": ["The report counts both kinds.",
           "Half of this one is inference, and it says so."],
   "code": 'r = pentest.report_claims([seen, guess])\nprint(r["observed"], "observed,", r["inferred"], "inferred, ratio", r["inference_ratio"])\n',
   "expect": "1 observed, 1 inferred, ratio 0.5\n"},
 ]},

"C2.13": {
 "goal": "Test with one login per role, and list the checks nobody has done yet.",
 "actors": ["Roles", "Matrix", "Tester", "Report"],
 "steps": [
  {"title": "Fill in two cells",
   "arrow": ("Tester", "Matrix", "tested"),
   "say": ["Two roles, two kinds of record, read and write: eight cells.",
           "You tested two. The other six are only assumed."],
   "code": 'from cybertravels.appsec import pentest\nm = pentest.Matrix(["traveller", "finance"], ["own_booking", "other_booking"], ["read", "write"])\nm.mark("traveller", "own_booking", "read", "tested")\nm.mark("traveller", "other_booking", "read", "tested")\nprint(m.coverage())\n',
   "expect": "{'tested': 2, 'assumed': 6, 'unreachable': 0, 'total': 8, 'tested_fraction': 0.25}\n"},
  {"title": "Which untested cell matters most",
   "arrow": ("Matrix", "Report", "worst first"),
   "say": ["Rank the untested cells by how much damage they could do.",
           "Writing someone else's booking comes first."],
   "code": 'worst = m.assumed_by_blast_radius(lambda r, o, v: (o == "other_booking") * 2 + (v == "write"))\nprint(worst[0])\n',
   "expect": "('traveller', 'other_booking', 'write')\n"},
 ]},

"C2.14": {
 "goal": "Try to start an attacking agent without its safety controls.",
 "actors": ["Operator", "Preflight", "SOC", "Agent"],
 "steps": [
  {"title": "Everything in place",
   "arrow": ("Operator", "Preflight", "check"),
   "say": ["The checklist must be complete before an attacking agent runs.",
           "With everything ticked, it may start."],
   "code": 'from cybertravels.appsec import pentest\nready = {k: True for k in pentest.REQUIRED}\nprint(sorted(pentest.REQUIRED))\nprint("may start:", pentest.may_start(ready))\n',
   "expect": "['authorisation_in_writing', 'findings_store_offline', 'kill_switch', 'rate_limited', 'replica_not_production', 'scope_enforced_at_boundary', 'soc_notified']\nmay start: True\n"},
  {"title": "One control missing",
   "arrow": ("Preflight", "Agent", "blocked"),
   "say": ["Untick the kill switch.",
           "It refuses to start, and says which control is missing."],
   "code": 'short = dict(ready, kill_switch=False)\nprint(pentest.preflight(short))\ntry:\n    pentest.may_start(short)\nexcept pentest.OutOfScope:\n    print("refused to start")\n',
   "expect": "{'kill_switch': 'one command, tested before the engagement, not written during it'}\nrefused to start\n"},
 ]},

"C2.15": {
 "goal": "Rate two findings by their evidence, and report the pipeline's real numbers.",
 "actors": ["Finding", "Evidence", "Severity", "Report"],
 "steps": [
  {"title": "Same rule, different severity",
   "arrow": ("Evidence", "Severity", "calibrate"),
   "say": ["A refund bug proven in the replica, on the money path: critical.",
           "An eval nothing can reach: info."],
   "code": 'from cybertravels.appsec import findings as fnd\nlive = fnd.Finding("tools/payments_api.py", 8, "issue_refund", "CWE-639", basis="dast", stage=12)\nlive.verdict = "confirmed"\ndead = fnd.Finding("agents/file_agent.py", 11, "render_template", "CWE-95", basis="rule:eval-call", stage=7)\nfor f, reach in ((live, True), (dead, False)):\n    sev, why = fnd.calibrate(f, reachable=reach)\n    print(f"{f.unit:16} {sev}")\n',
   "expect": "issue_refund     critical\nrender_template  info\n"},
  {"title": "Findings are not confirmations",
   "arrow": ("Finding", "Report", "economics"),
   "say": ["Four findings: two confirmed, one refuted, one unknown.",
           "A report that says four, alone, hides that."],
   "code": 'pool = []\nfor v in ("confirmed", "confirmed", "refuted", "undetermined"):\n    f = fnd.Finding("tools/bookings_api.py", 41, "search_bookings", "CWE-89", basis="rule:sql-concat", stage=7)\n    f.verdict = v\n    pool.append(f)\ne = fnd.economics(pool, {"stage7": 0.4, "stage10": 1.2})\nprint({k: e[k] for k in ("findings", "confirmed", "refuted", "undetermined")})\n',
   "expect": "{'findings': 4, 'confirmed': 2, 'refuted': 1, 'undetermined': 1}\n"},
 ]},

"C2.16": {
 "goal": "Accept a fix only with a test that fails without it.",
 "actors": ["Patch", "Exploit", "Test", "Merge"],
 "steps": [
  {"title": "A real fix, a real test",
   "arrow": ("Patch", "Test", "proven"),
   "say": ["Fix the IDOR in get_booking. The test proves Dana can no longer read booking 2.",
           "A quiet scanner is not counted as evidence."],
   "code": 'from cybertravels import config, db\nfrom cybertravels.appsec import replica as rep, remediate\nfrom cybertravels.tools import bookings_api\nfrom cybertravels.identity import Session\noriginal, was = bookings_api.get_booking, config.DB_PATH\ndana = Session("dana", "traveller")\ndef exploit():\n    for i in range(1, 8):\n        try:\n            row = bookings_api.get_booking(dana, i)\n        except PermissionError:\n            continue\n        if row and row["owner_id"] != "dana":\n            return True\n    return False\ndef regression():\n    try:\n        bookings_api.get_booking(dana, 2)\n    except PermissionError:\n        return\n    raise AssertionError("dana read booking 2")\nwith rep.for_target("local-replica") as r:\n    rep.isolated_db(r)\n    patch = remediate.fix_get_booking()\n    out = remediate.accept(patch, bookings_api, exploit=exploit, regression=regression)\n    print("accepted. not evidence:", out["not_evidence"])\n',
   "expect": "accepted. not evidence: ['the scanner went quiet']\n"},
  {"title": "A test that passes either way",
   "arrow": ("Exploit", "Merge", "rejected"),
   "say": ["Now a test that passes whether or not the fix is there.",
           "The patch is rejected. That test proves nothing."],
   "code": 'bookings_api.get_booking = original\nwith rep.for_target("local-replica") as r:\n    rep.isolated_db(r)\n    try:\n        remediate.accept(remediate.fix_get_booking(), bookings_api, exploit=exploit, regression=lambda: None)\n    except remediate.PatchRejected as e:\n        print("rejected:", "UNPATCHED" in str(e))\nbookings_api.get_booking = original\nconfig.DB_PATH = was\ndb.reset()\n',
   "expect": "rejected: True\n"},
 ]},

"C2.17": {
 "goal": "Give a model only the code that matters for one finding, and see how much smaller it is.",
 "actors": ["Finding", "Slice", "Model", "File"],
 "steps": [
  {"title": "The slice keeps the safe twin",
   "arrow": ("Finding", "Slice", "context"),
   "say": ["The bug is the difference between get_booking and get_my_booking.",
           "So the slice includes both, and leaves the rest out."],
   "code": _TREE + 'from cybertravels.appsec import findings as fnd, sast\nf = fnd.Finding("tools/bookings_api.py", 17, "get_booking", "CWE-639", basis="model:read", stage=7)\ntext = sast.slice_for(TREE, f)\nprint("has get_booking:", "def get_booking" in text, "| has twin:", "def get_my_booking" in text,\n      "| has unrelated code:", "def search_bookings" in text)\n',
   "expect": "has get_booking: True | has twin: True | has unrelated code: False\n"},
  {"title": "How much smaller",
   "arrow": ("Slice", "Model", "ratio"),
   "say": ["Less unrelated code means fewer false alarms.",
           "The slice is under half the file."],
   "code": 'print("slice is", round(sast.slice_ratio(TREE, f) * 100), "% of the file")\n',
   "expect": "slice is 25 % of the file\n"},
 ]},

"C2.18": {
 "goal": "Attest the controls on one deployment, and see the attestation refuse to overclaim.",
 "actors": ["Pipeline", "Control", "Attestation", "Auditor"],
 "steps": [
  {"title": "A pass needs evidence",
   "arrow": ("Pipeline", "Control", "PASS?"),
   "say": ["Claiming a control passes, with nowhere to check, is refused.",
           "Some controls can never be PASS from a pipeline. They are capped."],
   "code": 'from cybertravels.appsec import attest\ntry:\n    attest.Control("default-deny-tools", "PASS", "")\nexcept ValueError as e:\n    print("refused:", e)\nprint("capped at partial:", sorted(attest.CAPPED_AT_PARTIAL))\n',
   "expect": "refused: default-deny-tools: PASS with no evidence URI is an assertion. The whole point of the predicate is that somebody else can go and look\ncapped at partial: ['injection-screening', 'sandbox-egress']\n"},
  {"title": "The image moved, the verdicts did not",
   "arrow": ("Attestation", "Auditor", "drift"),
   "say": ["The agent's image changed between two attestations.",
           "The verdicts stayed the same. That is the finding."],
   "code": 'controls = [attest.Control("delegated-authorisation", "PASS", "s3://evidence/a2"),\n            attest.Control("injection-screening", "PARTIAL", "s3://evidence/a1")]\nfirst = attest.statement("ct-prod-eu-1", [attest.subject("workflow-agent", "image-v1")], controls)\nsecond = attest.statement("ct-prod-eu-1", [attest.subject("workflow-agent", "image-v2")], controls, previous=first)\nprint(second["predicate"]["drift"])\n',
   "expect": "{'verdicts_changed': {}, 'controls_added': [], 'controls_gone': [], 'subjects_changed': ['workflow-agent'], 'unreviewed_pass': []}\n"},
 ]},

"C2.19": {
 "goal": "Run the pipeline's stages end to end on CyberTravels and read the numbers a production pipeline reports.",
 "actors": ["Code", "Scan", "Reachability", "Report"],
 "steps": [
  {"title": "Scan, then mark reachability",
   "arrow": ("Code", "Reachability", "stages 7 and 10"),
   "say": ["The same stages a production pipeline runs, on this code.",
           "Count what each stage leaves."],
   "code": _TREE + 'from cybertravels.appsec import sast, reach\nfound = sast.scan(TREE)\nr = reach.report(found, reach.build(TREE))\nprint(len(found), "findings,", len(found) - len(r["unreachable_units"]), "reachable")\n',
   "expect": "5 findings, 3 reachable\n"},
  {"title": "What a reviewer gets first",
   "arrow": ("Reachability", "Report", "queue"),
   "say": ["Reachable findings go to the top of the queue.",
           "Unreachable ones stay, lower down."],
   "code": 'dead = set(r["unreachable_units"])\nfor f in sorted(found, key=lambda f: (f.unit in dead, f.unit)):\n    print("unreachable" if f.unit in dead else "reachable  ", f.cwe, f.unit)\n',
   "expect": "reachable   CWE-78 _open_branch\nreachable   CWE-22 download_invoice\nreachable   CWE-89 search_bookings\nunreachable CWE-95 render_template\nunreachable CWE-295 sync_vendor\n"},
 ]},
}
