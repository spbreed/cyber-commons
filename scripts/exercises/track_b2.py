"""B2 — Trusting the harness that tests CyberTravels. Four sessions.

Chapter 4 built the pipeline. This chapter is about whether its output is worth
acting on, which is a different question and the one nobody asks.

    B2.0  the eight parts    what a harness actually is, and the one people
                             cannot name
    B2.1  evaluation         on a corpus with known answers, because a
                             hallucinated finding looks exactly like a real one
    B2.2  reliability + cost pass^k, variance, and dollars per confirmed finding
    D1.11  deception          canaries and honeypots in the agent's own
                             environment — the detection with no false positives

Budgets and stop conditions are A3.4. The loop, tools, routing, delegation
depth and replay are properties of the harness B2.0 names; they are exercised
throughout chapter 4 rather than taught as separate lessons here.
"""

MODEL_NOTE = """
> **About the model in this notebook.** It runs offline against a deterministic
> replay, so the lesson executes on a Kaggle kernel with no network. The replay
> is not a language model and is labelled as such. To run the identical harness
> against a real open-weight model:
>
> ```bash
> ollama pull glm-4.6            # or kimi-k2, llama3.3
> export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
> ```
"""

EXERCISES: dict[str, dict] = {

"B2.1": {
 "concept": """
This is the flagship lesson of the track: how to tell whether a security harness
is any good.

Four stages, in order, each answering a different question:

1. **Ingest** — did the output parse and match the schema?
2. **Path matching** — is the finding about the file we asked about?
3. **Expert proxy** — is it right? Scored {0, 0.5, 1}.
4. **Dual judges** — is the reasoning sound? Two judges, aggregated by **MIN**.

And the distinction the whole lesson exists for:

> **Conformance** is schema validity. With structured output it is ~100% by
> construction. It is a build-health signal.
>
> **Accuracy** is correctness. It is the number that means something.

Quoting conformance as quality — "our harness scores 100%" — is the single most
common way a security evaluation misleads its own sponsors.

There is also one implementation detail that silently randomises everyone's
results, and it is a single line: **file matching must use parent directory plus
filename, never the bare basename.** Public corpora reuse `1.py` and `3.c` across
every CWE directory.
""",
 "steps": [
  ("model", {
   "title": "The harness under evaluation, actually answering",
   "task": ("Review this function and report any security vulnerability as "
            "JSON: {\"cwe\": ..., \"file\": ..., \"line\": ..., "
            "\"rationale\": ...}. Report nothing else.\n\n"
            "# src/data/reports.py\n"
            "def load_booking(ref, owner):\n"
            "    return DB.execute(\"SELECT * FROM bookings WHERE ref=\" + ref +\n"
            "                      \" AND owner='\" + owner + \"'\")"),
   "replay": ('{"cwe": "CWE-89", "file": "src/data/reports.py", "line": 2, '
              '"rationale": "ref and owner are concatenated into the SQL string, '
              'so a traveller-supplied booking reference can terminate the '
              'literal and append arbitrary SQL"}'),
   "system": ("You are a security code reviewer. Reply with one JSON object and "
              "nothing else."),
   "check": ('("reports CWE-89", "89" in answer)')}),
  ("md", "## 3 · The four stages that decide whether that answer counts\n\n"
         "The cell above is the harness producing one finding. Everything below "
         "is the machinery that decides whether it was right — and the point of "
         "the lesson is that stage 1 says yes to plenty of answers that stages "
         "2 to 4 then reject."),
  ("md", "## 2 · Stage 1 — ingest, where conformance is decided"),
  ("py", '''import json
from dataclasses import dataclass, field

@dataclass
class Answer:
    qid: str; cwe: str = ""; file: str = ""; line: int = 0; rationale: str = ""
    REQUIRED = ("qid", "cwe", "file", "rationale")

    @classmethod
    def parse(cls, raw):
        try:
            d = json.loads(raw)
        except json.JSONDecodeError as e:
            return None, f"non-conforming: not JSON ({e.msg})"
        missing = [k for k in cls.REQUIRED if not d.get(k)]
        if missing:
            return None, f"non-conforming: missing {missing}"
        return cls(str(d["qid"]), str(d["cwe"]).upper(), str(d["file"]),
                   int(d.get("line", 0)), str(d["rationale"])), "conforming"

@dataclass
class Truth:
    qid: str; cwe: str; file: str; line: int = 0

TRUTHS = {
 "q1": Truth("q1", "CWE-89",  "CWE-89/1.py"),
 "q2": Truth("q2", "CWE-78",  "CWE-78/1.py"),
 "q3": Truth("q3", "CWE-22",  "CWE-22/3.c"),
 "q4": Truth("q4", "CWE-798", "CWE-798/2.py"),
}
ANSWERS = {
 "q1": '{"qid":"q1","cwe":"CWE-89","file":"CWE-89/1.py","line":2,'
       '"rationale":"user input is concatenated into the query string"}',
 "q2": '{"qid":"q2","cwe":"CWE-89","file":"CWE-78/1.py","line":3,'
       '"rationale":"untrusted input reaches a shell"}',
 "q3": '{"qid":"q3","cwe":"CWE-22","file":"CWE-89/1.py","line":1,'
       '"rationale":"path built from user input"}',
 "q4": 'I think this file contains a hardcoded credential.',
}
for qid, raw in ANSWERS.items():
    _, note = Answer.parse(raw)
    print(f"{qid}: {note}")
'''),
  ("md", "## 3 · Stage 2 — the one line that decides whether this is a benchmark\n\n"
         "Public corpora reuse filenames across directories. Match on the "
         "basename and you score an answer about CWE-79 against the ground truth "
         "for CWE-89 — and your accuracy becomes a random variable."),
  ("py", '''def path_key(path):
    """Parent directory + filename. NEVER the bare basename."""
    parts = [p for p in path.replace("\\\\", "/").split("/") if p not in ("", ".")]
    return "/".join(parts[-2:]) if len(parts) > 1 else (parts[-1] if parts else "")

def basename(path):
    return path.replace("\\\\", "/").split("/")[-1]

pairs = [("CWE-89/1.py", "CWE-79/1.py"), ("a/CWE-22/3.c", "b/CWE-78/3.c")]
print(f"{'pair':34s}{'basename match':17s}path_key match")
print("-" * 66)
for a, b in pairs:
    print(f"{a + '  vs  ' + b:34s}{str(basename(a)==basename(b)):17s}"
          f"{path_key(a)==path_key(b)}")
print("\\nq3 answered about CWE-89/1.py when the truth is CWE-22/3.c.")
print(f"   basename says match: {basename('CWE-89/1.py') == basename('CWE-22/3.c')}")
print(f"   path_key says match: {path_key('CWE-89/1.py') == path_key('CWE-22/3.c')}")
'''),
  ("md", "## 4 · Stages 3 and 4 — expert proxy and two judges\n\n"
         "Half credit is not politeness. \"Right file, wrong vulnerability class\" "
         "is a genuinely different failure from \"wrong file entirely\", and "
         "averaging them away hides which one your harness is making.\n\n"
         "Two judges aggregated by **MIN**, not mean — judges exist to catch each "
         "other, and averaging lets the lenient one carry the strict one's failures."),
  ("py", '''def path_match(a, t): return path_key(a.file) == path_key(t.file)
def cwe_match(a, t):  return a.cwe == t.cwe.upper()

def expert_proxy(a, t):
    if not path_match(a, t): return 0.0
    return 1.0 if cwe_match(a, t) else 0.5

MECHANISM = ("concatenat", "unsanitis", "unsanitiz", "untrusted", "user input",
             "interpolat", "taint", "unvalidated")
def judge_strict(a, t):
    if expert_proxy(a, t) < 1.0: return 0.0
    return 1.0 if any(w in a.rationale.lower() for w in MECHANISM) else 0.5
def judge_lenient(a, t):
    return 1.0 if cwe_match(a, t) else 0.0

@dataclass
class Report:
    total: int = 0; conforming: int = 0
    expert_sum: float = 0.0; judge_sum: float = 0.0
    failures: list = field(default_factory=list)
    @property
    def conformance(self): return self.conforming / self.total if self.total else 0
    @property
    def expert_accuracy(self): return self.expert_sum / self.total if self.total else 0
    @property
    def judge_accuracy(self): return self.judge_sum / self.total if self.total else 0
    def render(self):
        return (f"  questions            {self.total}\\n"
                f"  conformance          {self.conformance:.4f}   "
                f"← schema validity. Structural. NOT quality.\\n"
                f"  expert accuracy      {self.expert_accuracy:.4f}   ← correctness\\n"
                f"  judge accuracy (MIN) {self.judge_accuracy:.4f}\\n"
                f"  failures             {len(self.failures)}")

def evaluate(answers, truths):
    rep = Report(total=len(truths))
    for qid, t in truths.items():
        a, note = Answer.parse(answers.get(qid, ""))
        if a is None:
            rep.failures.append((qid, "1-ingest", note)); continue
        rep.conforming += 1
        e = expert_proxy(a, t)
        j = min(judge_strict(a, t), judge_lenient(a, t))
        rep.expert_sum += e; rep.judge_sum += j
        if e < 1.0:
            why = ("wrong file" if not path_match(a, t)
                   else f"right file, wrong class (said {a.cwe}, truth {t.cwe})")
            rep.failures.append((qid, "3-expert", why))
    return rep

rep = evaluate(ANSWERS, TRUTHS)
print(rep.render())
print("\\nfailures:")
for qid, stage, why in rep.failures:
    print(f"   {qid}  [{stage}]  {why}")
'''),
  ("md", "## 5 · The control — never report one number\n\n"
         "Here is what happens when the harness is upgraded to emit structured "
         "output. Conformance goes to 1.0. Nothing about its capability changed."),
  ("py", '''STRUCTURED = dict(ANSWERS)
STRUCTURED["q4"] = ('{"qid":"q4","cwe":"CWE-798","file":"CWE-798/2.py","line":1,'
                    '"rationale":"a credential is hardcoded"}')
rep2 = evaluate(STRUCTURED, TRUTHS)
print("after adding structured output:")
print(rep2.render())
print(f"\\nconformance  {rep.conformance:.2f} → {rep2.conformance:.2f}   "
      f"(+{rep2.conformance-rep.conformance:.2f})")
print(f"expert acc   {rep.expert_accuracy:.2f} → {rep2.expert_accuracy:.2f}   "
      f"(+{rep2.expert_accuracy-rep.expert_accuracy:.2f})")
print("\\nA press release could truthfully say 'conformance improved to 100%'.")
print("The harness still gets half the questions wrong.")

def gameable(answers):
    parsed = [Answer.parse(r)[0] for r in answers.values()]
    ok = [p for p in parsed if p]
    cwes = [p.cwe for p in ok]
    maj = max(set(cwes), key=cwes.count) if cwes else ""
    return {"conformance": round(len(ok)/len(answers), 3),
            "majority_class": maj,
            "accuracy_by_always_guessing_majority":
                round(cwes.count(maj)/len(cwes), 3) if cwes else 0}
print("\\nwithout any capability at all:", gameable(STRUCTURED))
assert rep2.conformance == 1.0 and rep2.expert_accuracy < 0.7
'''),
 ],
 "expect": "q1–q3 conform and q4 does not, giving conformance 0.75 against expert "
           "accuracy 0.375 — q1 scores 1.0, q2 scores 0.5 (right file, wrong "
           "class), q3 and q4 score 0. The basename comparison wrongly matches "
           "`CWE-89/1.py` with `CWE-79/1.py` where `path_key` does not. Adding "
           "structured output raises conformance to 1.00 while expert accuracy "
           "moves to 0.625, and the gameability check shows high conformance "
           "with no capability.",
 "challenge": "Take an eval number your organisation has quoted — internally or "
              "externally — and determine which of the two it was. Then check the "
              "file matcher in whatever produced it. Both checks take an hour and "
              "one of them usually changes the number.",
},

"B2.0": {
 "concept": """
**The model is not the system.**

A model is a text generator. Give it tokens, get tokens back. It has no memory
between calls, no ability to act, and no notion of whether it succeeded. Left
alone it cannot read a file, run a scanner or open a pull request.

> **A harness is everything wrapped around a model that turns generating text
> into getting work done.** It decides what the model sees, what it is allowed
> to do, whether what it did worked, when to stop, and what is written down
> afterwards. The whole pipeline in chapter 4 is one.

That is the definition, and it is worth being pedantic about, because "agent",
"scaffold", "framework" and "harness" get used interchangeably and the
substitution hides the question that matters: *which of these eight parts do
you actually have?*

| Component | What it does |
|---|---|
| **The loop** | Decides what happens next — plan, act, observe, decide again — and when to stop |
| **Tools** | The only way the model touches the world |
| **Context management** | What the model sees at each step, assembled from a world much larger than the window |
| **The verifier** | The independent check on whether a step actually succeeded |
| **State & memory** | What survives between steps and between runs |
| **Budgets & stop conditions** | Token, time, cost and action ceilings that bound autonomy |
| **Orchestrator** | Sub-agent spawning, parallelism, delegation depth |
| **Telemetry** | The record that makes a run auditable, replayable and debuggable |

Why this chapter exists: two teams given the **identical model** routinely
differ by an order of magnitude in output quality, purely on harness design.
Most of the capability you attribute to a model is the scaffold around it.

And the security consequence is direct. A harness is itself an autonomous actor
holding credentials and tools — so every harness you build is a system that must
be governed, contained and audited like any other.
""",
 "steps": [
  ("md", "## 2 · Build the smallest harness that is still a harness\\n\\n"
         "Eight components, none optional. The model here is a deterministic "
         "stand-in — labelled as one — so the scaffold is what you can see."),
  ("py", '''from dataclasses import dataclass, field

def stand_in_model(prompt):
    """NOT a language model. A deterministic stub, so the harness is visible.

    It reads the transcript so far to decide what is left to do - which is all
    any agent loop does, minus the part that is hard."""
    if "write_patch" not in prompt:
        return {"tool": "write_patch", "args": {"file": "auth.py"}}
    if "run_tests" not in prompt:
        return {"tool": "run_tests", "args": {}}
    return {"tool": "done", "args": {"claim": "fixed it"}}

WORLD = {"tests_pass": False, "patched": False}

def run_tests(**_):
    # the patch this stub writes does not actually fix the bug
    return {"passed": WORLD["tests_pass"], "failing": [] if WORLD["tests_pass"] else ["test_login"]}
def write_patch(file, **_):
    WORLD["patched"] = True
    return {"wrote": file}
def done(claim, **_):
    return {"claim": claim}

TOOLS = {"run_tests": run_tests, "write_patch": write_patch, "done": done}

@dataclass
class Budget:
    steps: int = 6
    used: int = 0
    def spend(self):
        self.used += 1
        return self.used <= self.steps

def harness(task, verifier=None, budget=None, telemetry=None):
    """loop + tools + context + verifier + state + budget + telemetry."""
    budget = budget or Budget()
    telemetry = telemetry if telemetry is not None else []
    context = [f"TASK: {task}"]                       # context management
    state = {"steps": 0}                              # state
    while budget.spend():                             # budgets / stop conditions
        step = stand_in_model("\\n".join(context))     # the model
        tool, args = step["tool"], step["args"]
        result = TOOLS[tool](**args)                  # tools
        state["steps"] += 1
        telemetry.append({"step": state["steps"], "tool": tool, "result": result})
        context.append(f"{tool} -> {result}")
        if tool == "done":
            ok = verifier() if verifier else True     # the verifier
            return {"claimed": True, "verified": ok, "steps": state["steps"],
                    "telemetry": telemetry}
    return {"claimed": False, "verified": False, "steps": state["steps"],
            "telemetry": telemetry}

print("components wired:", ["loop","tools","context","verifier","state",
                            "budget","orchestrator","telemetry"])
'''),

  ("md", "## 3 · Run it once with no verifier"),
  ("py", '''WORLD.update(tests_pass=False, patched=False)
r = harness("fix the failing test_login", verifier=None)
print(f"agent claimed success : {r['claimed']}")
print(f"independently checked : {r['verified']}")
print(f"steps                 : {r['steps']}")
for t in r["telemetry"]:
    print(f"   {t['step']}. {t['tool']:12s}{t['result']}")
print()
print("It reported success. The tests still fail. Nothing in that transcript")
print("is a lie - the agent did write a patch, and then it said it was done.")
assert r["claimed"] and not WORLD["tests_pass"]
'''),

  ("md", "## 4 · Where it breaks — the component people leave out\\n\\n"
         "Add the verifier and change nothing else."),
  ("py", '''def real_verifier():
    """Ground truth, not self-assessment: run the tests and read the result."""
    return run_tests()["passed"]

WORLD.update(tests_pass=False, patched=False)
r2 = harness("fix the failing test_login", verifier=real_verifier)
print(f"claimed {r2['claimed']}  verified {r2['verified']}")

WORLD.update(tests_pass=True)          # now the fix actually works
r3 = harness("fix the failing test_login", verifier=real_verifier)
print(f"claimed {r3['claimed']}  verified {r3['verified']}")
print()
print("Same model. Same loop. Same tools. The only difference between a harness")
print("that reports the truth and one that reports its own optimism is one")
print("component - and it is the cheapest one in the table.")
assert not r2["verified"] and r3["verified"]
'''),

  ("md", "## 5 · The budget is a security control, not a cost control"),
  ("py", '''def looping_model(prompt):
    return {"tool": "run_tests", "args": {}}          # never finishes

import builtins
_orig = stand_in_model
try:
    globals()["stand_in_model"] = looping_model
    WORLD.update(tests_pass=False)
    r4 = harness("fix it", verifier=real_verifier, budget=Budget(steps=4))
finally:
    globals()["stand_in_model"] = _orig

print(f"ran {r4['steps']} steps, then stopped: claimed={r4['claimed']}")
print()
print("Without the ceiling this runs until something else stops it - a bill, a")
print("rate limit, or an on-call engineer. The budget is what makes 'autonomous'")
print("a bounded word.")
assert r4["steps"] == 4 and not r4["claimed"]
'''),

  ("md", "## 6 · Verify — the harness is itself an actor\\n\\n"
         "It holds credentials and calls tools. Score it the way you would "
         "score any other non-human identity."),
  ("py", '''HARNESS_ACTOR = {
 "identity": "ci-sast-harness",
 "tools": sorted(TOOLS),
 "writes": ["write_patch"],
 "credentials": ["repo:write"],
 "runs_unattended": True,
 "telemetry": True,
}
irreversible = [t for t in HARNESS_ACTOR["writes"]]
print(f"{'property':22s}value")
for k, v in HARNESS_ACTOR.items():
    print(f"{k:22s}{v}")
print()
print(f"tools that change state : {irreversible}")
print(f"unattended              : {HARNESS_ACTOR['runs_unattended']}")
print(f"auditable               : {HARNESS_ACTOR['telemetry']}")
print()
print("Every question you would ask of an agent applies to the thing you just")
print("built to review agents. A harness with repo:write running unattended is")
print("a non-human identity, and it belongs in the inventory in A2 and E1.2.")
assert HARNESS_ACTOR["telemetry"], "an unauditable harness cannot be governed"
'''),
 ],
 "expect": "The minimal harness runs and reports success while the tests still "
           "fail. Adding one component — a verifier that reads ground truth "
           "rather than the agent's own claim — flips `verified` to False on the "
           "same run and to True only when the fix genuinely works. A four-step "
           "budget stops a looping model. The harness then scores itself as a "
           "non-human identity holding repo:write and running unattended.",
 "challenge": "Take a harness you already run and name its eight components. The "
              "one people cannot name is almost always the verifier, and the "
              "answer 'the model tells us' means there isn't one.",
},

"B2.2": {
 "concept": """
A single run tells you almost nothing about a stochastic system, and almost
every published harness result is a single run.

Two metrics, and the gap between them is the whole lesson:

**pass@k** — succeeded *at least once* in k attempts. This is the right metric
when you can cheaply check which attempt was correct and keep it. A code
generator whose output you compile and test is a pass@k system: five tries and
one good answer is a good day.

**pass^k** — succeeded *every time*, k out of k. This is the right metric when
the run is autonomous and nobody is checking, which describes every security
harness that files tickets, gates a merge or closes an alert.

A harness at 80% per-run reliability has a pass@5 of 99.97% and a pass^5 of
33%. Both numbers are true. Quoting the first one for a system that runs
unattended is where most harness claims quietly go wrong.

The other half is **run-to-run variance.** If the same input produces eleven
findings one day and four the next, the average is not a description of
anything, and any change you make afterwards is being measured against noise.

Reliability is one of three numbers that decide whether a harness is worth
running, and most teams measure only the first:

- **Accuracy**, usually against whatever the tool happened to find, which is
  circular. A **seeded corpus** of deliberately planted defects turns recall
  into a fraction with a real denominator.
- **Money**, per unit of value. Total spend is on the invoice; *cost per
  confirmed finding* is what changes when someone switches model tier.
- **Human time**, which is almost never measured and decides whether the tool
  survives. Four hundred findings a week at nine minutes each has not removed
  work. It has moved the work, renamed it triage, and made it somebody else's.
""",
 "steps": [
  ("md", "## 2 · The two metrics, from the same runs"),
  ("py", '''import random

def run_once(reliability, rng):
    return rng.random() < reliability

def measure(reliability, k=5, trials=2000, seed=3):
    rng = random.Random(seed)                  # seeded: identical every run
    at_least_one = every_time = 0
    for _ in range(trials):
        outcomes = [run_once(reliability, rng) for _ in range(k)]
        at_least_one += any(outcomes)
        every_time   += all(outcomes)
    return at_least_one / trials, every_time / trials

print(f"{'per-run':>9}{'pass@5':>10}{'pass^5':>10}  what it means unattended")
for r in (0.95, 0.90, 0.80, 0.60, 0.50):
    at_k, pow_k = measure(r)
    note = ("dependable" if pow_k > .8 else
            "coin flip" if pow_k > .3 else "fails most nights")
    print(f"{r:>8.0%}{at_k:>10.1%}{pow_k:>10.1%}  {note}")
print()
print("At 80% per-run the same harness is 99.9% reliable if a human picks the")
print("good answer, and 33% reliable if nobody is looking.")
'''),

  ("md", "## 3 · Where it breaks — the demo that was a lucky run"),
  ("py", '''def one_demo(reliability, seed):
    return run_once(reliability, random.Random(seed))

demos = [one_demo(0.6, s) for s in range(12)]
print("twelve single-run demos of the same 60% harness:")
print("   " + " ".join("PASS" if d else "fail" for d in demos))
print(f"   -> {demos.count(True)} passed")
print()
print("Publish any of the passes. Every one is an honest single run. None of")
print("them is a measurement, and the reader has no way to tell which they got.")
assert demos.count(True) and demos.count(False)
'''),

  ("md", "## 4 · Variance, and why it precedes every other question"),
  ("py", '''def findings_per_run(base, noise, rng):
    return max(0, int(rng.gauss(base, noise)))

def variance_profile(base, noise, runs=30, seed=11):
    rng = random.Random(seed)
    xs = [findings_per_run(base, noise, rng) for _ in range(runs)]
    mean = sum(xs) / len(xs)
    sd = (sum((x - mean) ** 2 for x in xs) / len(xs)) ** 0.5
    return xs, mean, sd

for noise in (0.5, 3.0):
    xs, mean, sd = variance_profile(8, noise)
    print(f"noise sd={noise}:  mean {mean:.1f}  sd {sd:.2f}  "
          f"range {min(xs)}-{max(xs)}")
    print(f"   runs: {xs[:12]} ...")

_, m_stable, sd_stable = variance_profile(8, 0.5)
_, m_noisy,  sd_noisy   = variance_profile(8, 3.0)
improvement = 1.5
print()
print(f"suppose a change adds {improvement} findings on average.")
print(f"   against sd {sd_stable:.2f}: visible after a handful of runs")
print(f"   against sd {sd_noisy:.2f}: indistinguishable from a quiet Tuesday")
print()
print("Until variance is characterised, every A/B comparison you run is")
print("measuring the dice.")
assert sd_noisy > sd_stable
'''),

  ("md", "## 5 · The control — separate harness failure from model failure\\n\\n"
         "Before changing either one, find out which is moving."),
  ("py", '''def attribute(runs_same_model_same_harness, runs_same_model_new_harness):
    """If output changes when only the harness changed, it was the harness."""
    a = sum(runs_same_model_same_harness) / len(runs_same_model_same_harness)
    b = sum(runs_same_model_new_harness) / len(runs_same_model_new_harness)
    return a, b, ("harness" if abs(b - a) > 0.15 else "not the harness")

rng = random.Random(5)
baseline = [run_once(0.6, rng) for _ in range(200)]
better_harness = [run_once(0.85, rng) for _ in range(200)]   # same model, better verifier
a, b, verdict = attribute(baseline, better_harness)
print(f"same model, original harness : {a:.0%}")
print(f"same model, better verifier  : {b:.0%}")
print(f"attribution                  : {verdict}")
print()
print("Twenty-five points of reliability, no model change. Teams routinely")
print("spend that budget on a bigger backbone instead, because the harness")
print("was never measured separately.")
assert verdict == "harness"
'''),

  ("md", "## 6 · Verify — the scorecard line that has to be published"),
  ("py", '''k = 5
rel = 0.85
at_k, pow_k = measure(rel, k=k)
xs, mean, sd = variance_profile(8, 0.9)
card = {
  "per_run_reliability": rel,
  "k": k,
  "pass_at_k": round(at_k, 4),
  "pass_pow_k": round(pow_k, 4),
  "runs_measured": 2000,
  "findings_mean": round(mean, 2),
  "findings_sd": round(sd, 2),
  "seed": 3,
  "unattended": True,
  "headline_metric": "pass^k",       # because unattended is True
}
for kk, vv in card.items():
    print(f"   {kk:22s}{vv}")
print()
print("The headline metric is chosen by how the harness runs, not by which")
print("number is larger. An unattended harness that reports pass@k is")
print("reporting the reliability of a system it is not.")
assert card["headline_metric"] == "pass^k" and card["pass_pow_k"] < card["pass_at_k"]
'''),

  ("md", "## 6 · The other two numbers — money, and somebody's afternoon\\n\\n"
         "Reliability says whether the harness can be left alone. Cost per "
         "confirmed finding and analyst minutes per accepted finding say whether "
         "leaving it alone is worth doing. Both need a corpus whose defects you "
         "planted, so recall has a real denominator."),
  ("py", '''SEEDED_CORPUS = {
 f"unit_{i:02d}": (i % 4 == 0, ["CWE-22", "CWE-78", "CWE-89", "CWE-79"][i % 4])
 for i in range(40)
}
planted = sorted(u for u, (is_bug, _) in SEEDED_CORPUS.items() if is_bug)
print(f"units in corpus : {len(SEEDED_CORPUS)}")
print(f"planted defects : {len(planted)}   <- the denominator is now a fact")

def harness_run(corpus, sensitivity, seed=2):
    """Higher sensitivity finds more real defects, and more false ones."""
    rng = random.Random(seed)
    out = []
    for unit, (is_bug, cwe) in sorted(corpus.items()):
        if is_bug and rng.random() < sensitivity:
            out.append((unit, cwe, True))
        elif not is_bug and rng.random() < sensitivity * 0.35:
            out.append((unit, cwe, False))
    return out

def scorecard(found, corpus, tokens_per_unit=1800, usd_per_1k=0.002,
              analyst_minutes=9):
    tp = [f for f in found if f[2]]
    planted_n = sum(1 for _, (b, _) in corpus.items() if b)
    spend = len(corpus) * tokens_per_unit / 1000 * usd_per_1k
    return {"recall": len(tp) / planted_n,
            "precision": len(tp) / len(found) if found else 0.0,
            "usd_per_finding": spend / len(tp) if tp else None,
            "analyst_minutes": len(found) * analyst_minutes,
            "minutes_per_accepted": len(found) * analyst_minutes / len(tp) if tp else None}

MANUAL_MINUTES = 40 * 4          # a human reading the same forty units
print(f"\\n{'sens':>6}{'recall':>9}{'prec':>7}{'$/find':>9}{'min/accepted':>14}"
      f"{'review load':>13}")
for s in (0.4, 0.7, 0.95):
    c = scorecard(harness_run(SEEDED_CORPUS, s), SEEDED_CORPUS)
    verdict = "saves time" if c["analyst_minutes"] < MANUAL_MINUTES else "COSTS MORE"
    print(f"{s:>6.2f}{c['recall']:>9.0%}{c['precision']:>7.0%}"
          f"{c['usd_per_finding']:>9.3f}{c['minutes_per_accepted']:>14.1f}"
          f"{verdict:>13}")

best_recall = scorecard(harness_run(SEEDED_CORPUS, 0.95), SEEDED_CORPUS)
print()
print(f"At the highest sensitivity recall is {best_recall['recall']:.0%} and the review")
print(f"queue is {best_recall['analyst_minutes']} minutes against {MANUAL_MINUTES} for reading the code by")
print("hand. The accuracy metric improved and the thing got worse - which stays")
print("invisible unless review load is a first-class number beside it.")
assert best_recall["analyst_minutes"] > MANUAL_MINUTES
'''),
 ],
 "expect": "pass@5 and pass^5 are computed from the same 2000 trials and "
           "diverge sharply: at 80% per-run reliability the harness is 99.9% "
           "reliable with a human picking the good answer and 33% reliable "
           "unattended. Twelve single-run demos of a 60% harness return a mix of "
           "passes and failures, and a change worth 1.5 findings is shown to be "
           "invisible against a standard deviation of 3. On the same seeded "
           "corpus of 40 units with 10 planted defects, raising sensitivity from "
           "0.70 to 0.95 lifts recall from 60% to 90% and pushes the review queue "
           "from 'saves time' to 180 analyst minutes against 160 for reading the "
           "code by hand.",
 "challenge": "Run your harness on one fixed task five times and count how many "
              "times it fully succeeded. That integer, out of five, is the number "
              "to put in front of anyone deciding whether to let it run "
              "unattended. Then divide last month's spend by the findings anyone "
              "actually accepted, and compare that to an hour of the reviewer's "
              "time.",
},

}
