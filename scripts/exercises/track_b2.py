"""B2 — The Security Automation / Harness Engineer. Ten sessions.

The track builds one artefact, in order, and each lesson modifies the previous:

    B2.1  the loop            plan → act → verify → stop
    B2.2  the verifier        the single highest-value hour in the track
    B2.3  tool design         the signature is the control
    A3.4  budgets             what works when everything else has failed
    B2.4  model routing       inside the loop this time
    B2.5  sub-agents          depth, and what it does to authority
    B2.6  failure taxonomy    so "it broke" routes to the right owner
    B2.7  self-improvement    why a held-out signal stops being optional
    B2.8  idempotency         it will do the same thing twice
    B2.11 evaluation          conformance vs accuracy, and the matching bug
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
A harness is four moves in a loop:

1. **Plan** — the model proposes what to do next.
2. **Act** — the harness executes that proposal against a tool.
3. **Verify** — something decides whether the result is acceptable.
4. **Stop** — either verification succeeded, or a budget ran out.

That is the whole architecture. Everything that makes a harness safe or unsafe
lives in moves 3 and 4, and this track spends most of its time there.

The reason to build it explicitly rather than adopt a framework is that
frameworks make moves 1 and 2 easy and leave 3 and 4 as your problem — usually
with a default that is "the model says it's done" and "loop forever". You need
to know exactly what yours does.

This lesson builds the loop, in about forty lines, and then changes exactly one
thing — the verifier — to show that the same model and the same proposals
produce opposite outcomes.
""",
 "steps": [
  ("md", MODEL_NOTE),
  ("md", "## 2 · Demo — the loop, with a task that has a right answer\n\n"
         "The task: fix a function that mis-computes a security-relevant value. "
         "The model produces three attempts, the last of which is correct."),
  ("py", '''import time
from dataclasses import dataclass, field

class ReplayModel:
    """DETERMINISTIC REPLAY — not a language model.
    Emits a fixed sequence so the loop's control flow is the thing under test."""
    def __init__(self, proposals, name="replay"):
        self.proposals, self.name, self.calls = list(proposals), name, 0
    def propose(self, _prompt):
        # after the script runs out it repeats — exactly what a stuck loop does
        p = self.proposals[min(self.calls, len(self.proposals) - 1)]
        self.calls += 1
        return p

@dataclass
class Step:
    n: int; proposal: str; ok: bool; detail: str; ms: float = 0.0

@dataclass
class Trace:
    steps: list = field(default_factory=list)
    stopped_by: str = ""
    succeeded: bool = False
    def table(self):
        rows = [f"{'step':>4}  {'ok':<6}{'proposal':<44}detail",
                f"{'-'*4}  {'-'*6}{'-'*44}{'-'*28}"]
        for s in self.steps:
            rows.append(f"{s.n:>4}  {str(s.ok):<6}{s.proposal[:44]:<44}{s.detail[:28]}")
        rows.append(f"\\nstopped by: {self.stopped_by}    succeeded: {self.succeeded}")
        return "\\n".join(rows)

def run(model, verifier, goal="", max_steps=5, max_seconds=10.0):
    tr, started = Trace(), time.monotonic()
    for n in range(1, max_steps + 1):
        t0 = time.monotonic()
        proposal = model.propose(f"{goal} (attempt {n})")      # PLAN
        ok, detail = verifier(proposal)                        # ACT + VERIFY
        tr.steps.append(Step(n, proposal, ok, detail, (time.monotonic()-t0)*1000))
        if ok:                                                 # STOP
            tr.stopped_by, tr.succeeded = "verifier satisfied", True
            return tr
        if time.monotonic() - started > max_seconds:
            tr.stopped_by = f"time budget ({max_seconds}s)"
            return tr
    tr.stopped_by = f"step budget ({max_steps} steps)"
    return tr

ATTEMPTS = [
 "def is_expired(cert): return cert.days_left < 0",     # off-by-one: 0 is expired
 "def is_expired(cert): return cert.days_left <= 0",    # correct
]
'''),
  ("py", '''# The verifier: execute the proposal against known-good cases.
CASES = [(-5, True), (0, True), (1, False), (30, False)]

class Cert:
    def __init__(self, d): self.days_left = d

def behavioural_verifier(src):
    ns = {}
    try:
        exec(compile(src, "<proposal>", "exec"), ns)
        fn = ns["is_expired"]
    except Exception as e:
        return False, f"did not compile: {type(e).__name__}"
    for days, expected in CASES:
        got = fn(Cert(days))
        if got != expected:
            return False, f"is_expired(days_left={days}) → {got}, want {expected}"
    return True, f"all {len(CASES)} cases pass"

tr = run(ReplayModel(ATTEMPTS), behavioural_verifier,
         goal="fix certificate expiry check", max_steps=5)
print(tr.table())
'''),
  ("md", "## 3 · Where it breaks — change only the verifier\n\n"
         "Same model. Same proposals. Same order. The only difference is what the "
         "loop believes when it decides it has succeeded."),
  ("py", '''def self_grading_verifier(src):
    """The model judges its own work. Ships in a lot of harnesses."""
    looks_done = bool(src.strip()) and src.strip().startswith("def ")
    return looks_done, "judge: looks like a valid fix, approving"

tr2 = run(ReplayModel(ATTEMPTS), self_grading_verifier,
          goal="fix certificate expiry check", max_steps=5)
print(tr2.table())

ns = {}; exec(compile(tr2.steps[-1].proposal, "<x>", "exec"), ns)
print(f"\\nthe accepted code says a cert with 0 days left is expired: "
      f"{ns['is_expired'](Cert(0))}")
print("It is not. A certificate expiring today is still valid today, and this")
print("harness just shipped that. The trace above is clean and reports success.")
'''),
  ("md", "## 4 · The control — the verifier is a security control\n\n"
         "State it plainly, because the rest of the track depends on it: **the "
         "verifier decides what the harness is allowed to believe.** A harness "
         "with a weak verifier does not fail loudly. It succeeds incorrectly, "
         "produces a clean trace, and the failure is discovered downstream."),
  ("py", '''def compare(model_factory, verifiers, **kw):
    out = {}
    for name, v in verifiers.items():
        tr = run(model_factory(), v, **kw)
        out[name] = {"succeeded": tr.succeeded, "steps": len(tr.steps),
                     "stopped_by": tr.stopped_by,
                     "accepted": tr.steps[-1].proposal if tr.succeeded else None}
    return out

def no_verifier(_src):
    return False, "no verifier configured"

results = compare(lambda: ReplayModel(ATTEMPTS),
                  {"behavioural (executes the code)": behavioural_verifier,
                   "self-grading (asks the model)":   self_grading_verifier,
                   "none":                            no_verifier},
                  goal="fix expiry check", max_steps=4)
print(f"{'verifier':34s}{'succeeded':11s}{'steps':7s}stopped by")
print("-" * 76)
for name, r in results.items():
    print(f"{name:34s}{str(r['succeeded']):11s}{r['steps']:<7}{r['stopped_by']}")

print("\\nwhat each one accepted:")
for name, r in results.items():
    print(f"   {name:34s}{r['accepted'] or '—'}")
assert results["behavioural (executes the code)"]["accepted"] == ATTEMPTS[1]
assert results["self-grading (asks the model)"]["accepted"] == ATTEMPTS[0]
'''),
 ],
 "expect": "The behavioural verifier rejects the off-by-one on attempt 1 and "
           "accepts the correct version on attempt 2. The self-grading verifier "
           "stops on attempt 1 and reports success, having accepted code that "
           "says a certificate with 0 days left is expired. The no-verifier run "
           "consumes the full step budget.",
 "challenge": "Take the harness you actually run and answer one question: what "
              "exactly does it check before it reports success? If the answer is "
              "\"the model said it was done\" or \"the command exited 0\", B2.2 is "
              "the next lesson and you need it.",
},

"B2.2": {
 "concept": """
This is the highest-value lesson in the track, because every other control
assumes the verifier is honest.

Verifiers form a hierarchy, ordered by **what it takes to fool them**:

| Verifier | Fooled by | Available when |
|---|---|---|
| **Behavioural test** | changing real behaviour | you can execute the thing |
| **Exact-match oracle** | nothing, but needs the answer up front | rarely |
| **Shape check** | any well-formed output | always |
| **LLM judge** | confident prose | always |

The trap is that the two available-everywhere options are the two weakest, and
they fail in the worst possible direction: they do not error, they **approve**.

There is also a subtler failure that is worth seeing rather than reading about:
a verifier that is *correct* but reads stale state. A test runner that imports
cached bytecode reports on code that is no longer on disk. A lying oracle is
worse than no oracle, because you stop looking.
""",
 "steps": [
  ("md", "## 2 · Demo — four verifiers, one broken input"),
  ("py", '''BROKEN  = "def parse_port(s): return int(s)"          # accepts 0, 99999, -1
CORRECT = ("def parse_port(s):\\n"
           "    p = int(s)\\n"
           "    if not (1 <= p <= 65535): raise ValueError('port out of range')\\n"
           "    return p")

def behavioural(src):
    ns = {}
    try:
        exec(compile(src, "<p>", "exec"), ns); fn = ns["parse_port"]
    except Exception as e:
        return False, f"compile failed: {e}"
    for bad in ("0", "70000", "-1"):
        try:
            fn(bad)
            return False, f"accepted out-of-range port {bad!r}"
        except ValueError:
            pass
    try:
        if fn("443") != 443:
            return False, "rejected a valid port"
    except Exception as e:
        return False, f"valid port raised {e}"
    return True, "rejects out-of-range, accepts valid"

def exact_match(expected):
    return lambda src: (src.strip() == expected.strip(),
                        "exact match" if src.strip() == expected.strip()
                        else "differs from the reference implementation")

def shape_check(src):
    ok = src.strip().startswith("def parse_port")
    return ok, "defines parse_port" if ok else "wrong shape"

def llm_judge(src):
    ok = bool(src.strip()) and not src.lower().startswith("i cannot")
    return ok, "judge: this looks like a correct implementation"

VERIFIERS = {"behavioural (executes it)": behavioural,
             "exact-match oracle":        exact_match(CORRECT),
             "shape check":               shape_check,
             "llm judge":                 llm_judge}

print(f"{'verifier':28s}{'on BROKEN':12s}{'on CORRECT':12s}detail (broken)")
print("-" * 84)
for name, v in VERIFIERS.items():
    b_ok, b_why = v(BROKEN)
    c_ok, _     = v(CORRECT)
    print(f"{name:28s}{str(b_ok):12s}{str(c_ok):12s}{b_why[:32]}")
'''),
  ("md", "## 3 · Where it breaks — the exact-match oracle is also wrong\n\n"
         "Look at the `on CORRECT` column. The behavioural verifier is the only "
         "one that gets *both* right. The exact-match oracle rejects a correct "
         "implementation that differs from its reference — which is why nobody "
         "uses it, and why teams fall back to the two weak options."),
  ("py", '''ALTERNATIVE = ("def parse_port(s):\\n"
               "    p = int(s)\\n"
               "    if p < 1 or p > 65535:\\n"
               "        raise ValueError('bad port')\\n"
               "    return p")
print("a correct implementation, written differently:")
for name, v in VERIFIERS.items():
    ok, why = v(ALTERNATIVE)
    print(f"   {name:28s}{str(ok):7s}{why[:44]}")
print("\\nThe oracle says no. Behavioural says yes. Only one of those is useful")
print("on code you did not write in advance.")
'''),
  ("md", "## 4 · The subtler failure — a correct verifier reading stale state\n\n"
         "This one is not about weak checks. The check is right; the *input* to "
         "it is stale. Python's bytecode cache reproduces it faithfully."),
  ("py", '''import os, sys, tempfile, subprocess, textwrap, shutil, pathlib

work = pathlib.Path(tempfile.mkdtemp())
(work / "mod.py").write_text("def check(x):\\n    return True   # broken: always passes\\n")
(work / "test_mod.py").write_text(textwrap.dedent("""
    from mod import check
    def test_rejects_bad():
        assert check(-1) is False
"""))

def run_check(workdir, clear_cache):
    if clear_cache:
        shutil.rmtree(workdir / "__pycache__", ignore_errors=True)
    env = {**os.environ, "PYTHONPATH": str(workdir)}
    if clear_cache:
        env["PYTHONDONTWRITEBYTECODE"] = "1"
    r = subprocess.run([sys.executable, "-c",
                        "import mod; print('PASS' if mod.check(-1) is False else 'FAIL')"],
                       cwd=workdir, env=env, capture_output=True, text=True)
    return r.stdout.strip()

print("1. verifier on the broken code:      ", run_check(work, clear_cache=True))
# the agent "fixes" it
(work / "mod.py").write_text("def check(x):\\n    return x >= 0\\n")
print("2. after a real fix, cache cleared:  ", run_check(work, clear_cache=True))
# now put the broken version back, but leave a stale cache in place
import py_compile
(work / "mod.py").write_text("def check(x):\\n    return True   # broken again\\n")
py_compile.compile(str(work / "mod.py"), doraise=True)
(work / "mod.py").write_text("def check(x):\\n    return x >= 0\\n")
os.utime(work / "mod.py", (0, 0))          # make the source look older than the cache
print("3. source fixed, STALE cache honoured:", run_check(work, clear_cache=False),
      " ← the verifier is reading code that is not on disk")
shutil.rmtree(work, ignore_errors=True)
'''),
  ("md", "## 5 · The control — rank verifiers and always clear derived state"),
  ("py", '''RANKING = [
 (1, "behavioural / property test", "must change observable behaviour",
     "execute the artefact against facts that must hold"),
 (2, "differential test",           "must match a trusted second implementation",
     "run old and new against the same inputs"),
 (3, "exact-match oracle",          "nothing — but needs the answer in advance",
     "only usable on a fixed corpus"),
 (4, "shape / schema check",        "any well-formed output",
     "use for conformance ONLY, never for quality — see B2.11"),
 (5, "llm judge",                   "confident prose",
     "acceptable only as a filter before a real check, never as the last word"),
]
print(f"{'rank':5s}{'verifier':30s}{'fooled by':44s}")
print("-" * 80)
for r, name, fooled, use in RANKING:
    print(f"{r:<5}{name:30s}{fooled:44s}")
    print(f"{'':35s}{use}")

CHECKLIST = [
 "does it EXECUTE the artefact, or only inspect it?",
 "would it fail if the artefact were subtly wrong?",
 "does it clear caches / derived state before reading?",
 "is its own correctness tested (does it fail on known-bad input)?",
]
print("\\nverifier review checklist:")
for c in CHECKLIST:
    print("   ·", c)

# the fourth item, applied to our own verifier
assert behavioural(BROKEN)[0] is False, "verifier must fail on known-bad"
assert behavioural(CORRECT)[0] is True, "verifier must pass on known-good"
assert behavioural(ALTERNATIVE)[0] is True, "verifier must accept alternatives"
print("\\nour behavioural verifier passes its own test: fails broken, accepts both correct forms.")
'''),
 ],
 "expect": "Only the behavioural verifier gets both the broken and correct inputs "
           "right; the shape check and judge accept the broken port parser, and "
           "the exact-match oracle rejects a correct alternative implementation. "
           "The stale-cache demo shows the verifier reporting PASS while reading "
           "bytecode for code no longer on disk. The verifier's own test confirms "
           "it fails on known-bad and accepts both correct forms.",
 "challenge": "Find one check in your pipeline that is a shape check wearing an "
              "oracle's name — \"the build passed\", \"the JSON validated\", \"no "
              "errors in the log\". Then ask the fourth checklist question about "
              "it: has anyone ever confirmed it fails on known-bad input?",
},

"B2.3": {
 "concept": """
Tool design is security design, and it is stronger than anything you can put in
a prompt — because a tool's **signature decides what the model is able to ask
for**.

Two tools with identical underlying capability:

```python
read_file(path: str)              # the model can request any path
read_file(doc_id: Literal[...])   # the model can request one of five documents
```

Both may be safe if a path guard sits underneath. The difference appears when
the guard has a bug: the first tool *presents* the vulnerable surface, the
second never expresses it.

Three rules follow, and they compose:

1. **Enumerate rather than accept free text** wherever the real requirement is a
   choice from a known set.
2. **Take the narrowest type that works.** An `int` bounded to a range beats a
   string that gets parsed.
3. **Return the least that satisfies the caller.** A tool returning the whole
   record when the agent needed one field has widened your data exposure by
   default.
""",
 "steps": [
  ("md", "## 2 · Demo — the same capability, three signatures"),
  ("py", '''import fnmatch
from typing import Literal

DOCS = {"runbook": "/srv/docs/runbook.md", "policy": "/srv/docs/policy.md",
        "oncall":  "/srv/docs/oncall.md"}
FILESYSTEM = {**{p: f"contents of {k}" for k, p in DOCS.items()},
              "/home/app/.aws/credentials": "AKIA…SECRET",
              "/etc/shadow": "root:$6$…"}

def normalise(p):
    parts = []
    for seg in p.split("/"):
        if seg in ("", "."): continue
        if seg == "..":
            if parts: parts.pop()
            continue
        parts.append(seg)
    return "/" + "/".join(parts)

def guard(path, workspace="/srv/docs"):
    real = normalise(path)
    if fnmatch.fnmatch(real, "*/.aws/*") or fnmatch.fnmatch(real, "*/etc/shadow"):
        return False
    return real.startswith(workspace + "/")

# --- signature A: free-form path -------------------------------------
def read_file_freeform(path: str):
    if not guard(path):
        return {"error": "denied by path guard"}
    return {"content": FILESYSTEM.get(normalise(path), "not found")}

# --- signature B: enumerated document id ------------------------------
def read_file_enumerated(doc_id: str):
    if doc_id not in DOCS:
        return {"error": f"unknown doc_id; valid: {sorted(DOCS)}"}
    return {"content": FILESYSTEM[DOCS[doc_id]]}

REQUESTS = ["runbook", "/srv/docs/runbook.md",
            "/srv/docs/../../home/app/.aws/credentials", "/etc/shadow"]
print(f"{'request':46s}{'free-form':28s}enumerated")
print("-" * 92)
for r in REQUESTS:
    a = read_file_freeform(r) if r.startswith("/") else {"error": "not a path"}
    b = read_file_enumerated(r)
    print(f"{r:46s}{str(a)[:26]:28s}{str(b)[:34]}")
'''),
  ("md", "## 3 · Where it breaks — introduce one bug in the guard\n\n"
         "Both signatures were safe above, because the guard worked. Now make the "
         "guard wrong in the ordinary way (A3.3's bug: prefix check before "
         "normalisation) and re-run. Only one signature is affected."),
  ("py", '''def guard_buggy(path, workspace="/srv/docs"):
    return path.startswith(workspace)          # the classic bug

def read_file_freeform_buggy(path: str):
    if not guard_buggy(path):
        return {"error": "denied"}
    return {"content": FILESYSTEM.get(normalise(path), "not found")}

attack = "/srv/docs/../../home/app/.aws/credentials"
print("with a buggy path guard:")
print(f"   free-form  : {read_file_freeform_buggy(attack)}")
print(f"   enumerated : {read_file_enumerated(attack)}")
print("\\nThe enumerated tool is unaffected by a filesystem bug it never touches.")
print("It cannot express the request, so the guard's correctness stops mattering.")
'''),
  ("md", "## 4 · Rule 3 — return the least that satisfies the caller\n\n"
         "The overlooked half of tool design. A tool that returns the whole record "
         "puts everything in the model's context, and everything in the context is "
         "everything that can be exfiltrated by a later injection."),
  ("py", '''USER_RECORD = {"id": 4471, "email": "dana@corp", "name": "Dana",
               "ssn": "123-45-6789", "salary": 145000,
               "mfa_secret": "JBSWY3DPEHPK3PXP", "role": "engineer"}

def get_user_wide(user_id):            return USER_RECORD
def get_user_narrow(user_id, fields):
    allowed = {"id", "name", "email", "role"}
    bad = set(fields) - allowed
    if bad:
        return {"error": f"fields not exposed by this tool: {sorted(bad)}"}
    return {k: USER_RECORD[k] for k in fields}

print("wide tool returns  :", sorted(get_user_wide(4471)))
print("narrow, legitimate :", get_user_narrow(4471, ["name", "role"]))
print("narrow, overreach  :", get_user_narrow(4471, ["name", "ssn", "mfa_secret"]))

leaked = set(get_user_wide(4471)) & {"ssn", "mfa_secret", "salary"}
print(f"\\nsensitive fields placed in the model's context by the wide tool: {sorted(leaked)}")
assert not (set(get_user_narrow(4471, ["name", "role"])) & leaked)
'''),
  ("py", '''# Verify: score a tool signature against the three rules.
def review_signature(name, accepts_free_text, bounded_types, returns_minimum):
    score = sum([not accepts_free_text, bounded_types, returns_minimum])
    problems = []
    if accepts_free_text:
        problems.append("accepts free text where an enumeration would do")
    if not bounded_types:
        problems.append("unbounded types — parse errors become the guard's problem")
    if not returns_minimum:
        problems.append("returns more than the caller needs")
    return {"tool": name, "score": f"{score}/3", "problems": problems}

TOOLS = [
 ("read_file(path: str)",                   True,  False, True),
 ("read_file(doc_id: Literal[...])",        False, True,  True),
 ("get_user(user_id: int)",                 False, True,  False),
 ("get_user(user_id: int, fields: list)",   False, True,  True),
 ("run_shell(cmd: str)",                    True,  False, False),
]
for name, free, bounded, minimal in TOOLS:
    r = review_signature(name, free, bounded, minimal)
    print(f"{r['score']}  {r['tool']}")
    for p in r["problems"]:
        print(f"        ⚠ {p}")
'''),
 ],
 "expect": "Both signatures behave safely while the guard is correct. With the "
           "buggy prefix-check guard the free-form tool returns the AWS "
           "credentials while the enumerated tool still reports an unknown "
           "doc_id. The wide user tool places `ssn`, `mfa_secret` and `salary` in "
           "the model's context; the narrow one refuses those fields. The "
           "signature review scores `run_shell(cmd: str)` at 0/3.",
 "challenge": "Take one free-form tool in your harness and work out what the "
              "model genuinely needs the freedom for. The honest requirement is "
              "almost always narrower than the current signature — and narrowing "
              "it removes a whole class of guard bugs from your risk register.",
},

"B2.4": {
 "concept": """
A1.7 routed models across *stages* at the architecture level. This lesson routes
them **inside the loop**, where the decision is made per iteration and the
temptation is stronger.

The cost pressure is real: a large open-weight model on every iteration of a
50-step loop is slow and expensive, and most iterations are trivial. So teams
route dynamically — small model by default, escalate to the large one when the
task looks hard.

Two rules keep that safe, and they are the same two from A1.7 applied per-call:

1. **A model may only invoke tools within its tier's blast-radius budget.**
2. **The verifier is never weaker than the actor.**

The failure mode specific to in-loop routing is subtler than either: **escalation
on failure**. If the loop retries with a bigger model whenever the small one
fails verification, an attacker who can cause failures can force every task onto
the most capable model — and, more importantly, the escalation path usually
carries more authority too.
""",
 "steps": [
  ("md", MODEL_NOTE),
  ("md", "## 2 · Demo — tiered routing that works"),
  ("py", '''TIERS = {
 "llama3.2:1b":  {"tier": 0, "ms": 40,   "solves": 0.2},
 "llama3.3:8b":  {"tier": 1, "ms": 220,  "solves": 0.55},
 "glm-4.6":      {"tier": 2, "ms": 900,  "solves": 0.85},
 "kimi-k2":      {"tier": 3, "ms": 2400, "solves": 0.93},
}
TIER_BUDGET = {0: 0, 1: 3, 2: 20, 3: 60}     # max blast radius a tier may hold
SCOPE = {"read_file": 0, "search": 0, "write_file": 3, "open_pr": 3,
         "merge_pr": 6, "deploy": 40}

def may_invoke(model, tool):
    return SCOPE[tool] <= TIER_BUDGET[TIERS[model]["tier"]]

print(f"{'model':14s}{'tier':>5}  tools it may invoke")
print("-" * 70)
for m in TIERS:
    allowed = [t for t in SCOPE if may_invoke(m, t)]
    print(f"{m:14s}{TIERS[m]['tier']:>5}  {allowed}")
'''),
  ("md", "## 3 · Where it breaks — escalation on failure\n\n"
         "The natural retry policy: if the small model fails, try a bigger one. "
         "Watch what an attacker who can force failures gets."),
  ("py", '''LADDER = ["llama3.2:1b", "llama3.3:8b", "glm-4.6", "kimi-k2"]

def loop_with_escalation(task_fails_always, max_steps=4, escalate_authority=True):
    """The common pattern: harder task → bigger model → and, usually, more tools."""
    trace = []
    for i in range(max_steps):
        model = LADDER[min(i, len(LADDER)-1)]
        tools = [t for t in SCOPE if may_invoke(model, t)] if escalate_authority \\
                else [t for t in SCOPE if may_invoke(LADDER[0], t)]
        trace.append({"step": i+1, "model": model, "tier": TIERS[model]["tier"],
                      "ms": TIERS[model]["ms"], "tools": tools})
        if not task_fails_always:
            break
    return trace

print("a task that keeps failing verification:")
tr = loop_with_escalation(task_fails_always=True)
for s in tr:
    print(f"   step {s['step']}  {s['model']:14s} tier {s['tier']}  "
          f"{s['ms']:>5}ms  may invoke {s['tools']}")
total_ms = sum(s["ms"] for s in tr)
print(f"\\ncost of one forced escalation: {total_ms}ms and the final step could "
      f"invoke {tr[-1]['tools']}")
print("An attacker who can make verification fail has just promoted the loop to")
print("the most capable model AND the widest tool set. Both, for free.")
'''),
  ("md", "## 4 · The control — escalate capability, never authority\n\n"
         "The fix separates two things that are usually coupled: how *smart* the "
         "model is, and what it is *allowed to do*. Escalating the first is fine. "
         "Escalating the second must require a fresh decision."),
  ("py", '''def loop_capability_only(task_fails_always, max_steps=4, task_budget=TIER_BUDGET[1]):
    """Authority is fixed by the TASK, not by which model happens to be running.

    The ladder starts at the lowest tier whose budget covers the task's
    authority. Routing a tool-holding step to a model below that would hand the
    weakest model in the system tools its tier is not trusted with — which is
    the same mistake as escalating authority, in the other direction.
    """
    ladder = [m for m in LADDER if TIER_BUDGET[TIERS[m]["tier"]] >= task_budget]
    trace = []
    for i in range(max_steps):
        model = ladder[min(i, len(ladder)-1)]
        tools = [t for t in SCOPE if SCOPE[t] <= task_budget]
        trace.append({"step": i+1, "model": model, "tools": tools})
        if not task_fails_always:
            break
    return trace

tr2 = loop_capability_only(task_fails_always=True)
print(f"   task authority budget: {TIER_BUDGET[1]}  → ladder starts at the lowest "
      f"tier that covers it")
for s in tr2:
    print(f"   step {s['step']}  {s['model']:14s} may invoke {s['tools']}")
print("\\nThe model gets smarter. The authority does not move.")

escalated = set(tr[-1]["tools"]) - set(tr2[-1]["tools"])
print(f"tools the attacker gained under the naive policy: {sorted(escalated)}")
assert escalated
'''),
  ("py", '''# Verify: both rules, checked over every step of both policies.
def review(trace, verifier_model):
    problems = []
    for s in trace:
        model = s["model"]
        for t in s["tools"]:
            if SCOPE[t] > TIER_BUDGET[TIERS[model]["tier"]]:
                problems.append(f"step {s['step']}: {model} may invoke {t} "
                                f"(blast {SCOPE[t]} > budget "
                                f"{TIER_BUDGET[TIERS[model]['tier']]})")
        if TIERS[verifier_model]["tier"] < TIERS[model]["tier"]:
            problems.append(f"step {s['step']}: verifier {verifier_model} is weaker "
                            f"than actor {model}")
    return problems

for label, trace, verifier in (("escalate authority too",   tr,  "llama3.3:8b"),
                               ("capability only, glm verifier", tr2, "glm-4.6"),
                               ("capability only, kimi verifier", tr2, "kimi-k2")):
    p = review(trace, verifier)
    print(f"{label:32s} {'PASS' if not p else f'{len(p)} FINDING(S)'}")
    for x in p[:4]:
        print(f"      ⚠ {x}")

print("\\nRead the middle row. Fixing the authority leak was not enough:")
print("once the ladder can reach kimi-k2, a glm-4.6 verifier is weaker than the")
print("actor on the final step, and rule 2 fires. Escalating capability forces")
print("the verifier's tier up with it — a second-order cost of dynamic routing")
print("that cost models never include.")

assert review(tr2, "glm-4.6"), "the weaker-verifier finding must be reported"
assert review(tr2, "kimi-k2") == [], "top-tier verifier should satisfy both rules"
top = max(TIERS[s["model"]]["tier"] for s in tr2)
print(f"\\nrule: verifier tier must be ≥ {top} (the highest tier the ladder reaches)")
'''),
 ],
 "expect": "The tier table shows only `kimi-k2` may invoke `deploy`. Under "
           "escalation-on-failure a forced failure walks the loop up to `kimi-k2` "
           "in 3,560ms and hands it `merge_pr` and `deploy`. The capability-only "
           "policy keeps the tool set fixed throughout. The review then shows a "
           "second-order effect: with a `glm-4.6` verifier the capability-only "
           "policy still fails rule 2 on the final step, because the ladder "
           "reached a stronger model than the verifier. Only a top-tier verifier "
           "passes both rules.",
 "challenge": "Check your own retry logic: when a step fails and you retry with a "
              "different model, does the tool set change? In most frameworks the "
              "answer is yes and nobody chose it.",
},

"B2.5": {
 "concept": """
Sub-agents buy specialisation. What they also buy — and what is never on the
roadmap — is **delegation depth**.

Two things grow with depth, and only one of them is obvious:

- **Authority composition** (A1.3, A2.5). Each hop is a place authority could
  widen if the narrowing rules are not enforced at *every* hop.
- **Attribution distance.** By hop four, the action is five identities away from
  the human who asked, and no single reviewer has seen the whole path.

The control is a depth limit, and the interesting question is **where to enforce
it**. Enforcing it in the orchestrator is the obvious choice and the wrong one:
when the orchestrator is the compromised component, its own check is worth
nothing. It has to live at the token issuer or the resource server.
""",
 "steps": [
  ("md", "## 2 · Demo — a depth-3 sub-agent chain that narrows correctly"),
  ("py", '''from dataclasses import dataclass, field

CEILINGS = {"dana@corp": {"repo:read","repo:write","deploy:prod"},
            "orchestrator": {"repo:read","repo:write","deploy:prod"},
            "planner":   {"repo:read"},
            "coder":     {"repo:read","repo:write"},
            "reviewer":  {"repo:read"},
            "shipper":   {"repo:read","deploy:prod"}}

class DelegationError(Exception): pass

@dataclass
class Token:
    sub: str; actor: str; scopes: set; act: dict = None
    def chain(self):
        out, node = [], self.act
        while node: out.append(node["actor"]); node = node.get("act")
        c = list(reversed(out)) + [self.actor]
        if c[0] != self.sub: c.insert(0, self.sub)
        return c
    @property
    def depth(self): return len(self.chain())

def exchange(pres, actor, scopes):
    scopes = set(scopes)
    if not scopes <= pres.scopes:
        raise DelegationError(f"widening: {sorted(scopes - pres.scopes)}")
    if not scopes <= CEILINGS.get(actor, set()):
        raise DelegationError(f"above {actor}'s ceiling")
    return Token(pres.sub, actor, scopes, {"actor": pres.actor, "act": pres.act})

root  = Token("dana@corp", "dana@corp", set(CEILINGS["dana@corp"]))
orch  = exchange(root, "orchestrator", {"repo:read","repo:write","deploy:prod"})
coder = exchange(orch, "coder", {"repo:read","repo:write"})
rev   = exchange(coder, "reviewer", {"repo:read"})

for t in (root, orch, coder, rev):
    print(f"depth {t.depth}  {' → '.join(t.chain()):52s} {sorted(t.scopes)}")
'''),
  ("md", "## 3 · Where it breaks — the check in the wrong place\n\n"
         "The orchestrator enforces `MAX_DEPTH`. Now assume the orchestrator is "
         "the compromised component, which is the realistic case: it is the one "
         "processing untrusted task descriptions."),
  ("py", '''MAX_DEPTH = 3

def orchestrator_enforced(chain_token, new_actor, scopes, honest=True):
    """The limit lives inside the orchestrator's own code."""
    if honest and chain_token.depth + 1 > MAX_DEPTH:
        raise DelegationError(f"depth {chain_token.depth+1} > {MAX_DEPTH}")
    return exchange(chain_token, new_actor, scopes)

print("honest orchestrator:")
try:
    t = orchestrator_enforced(rev, "shipper", {"repo:read"}, honest=True)
    print("   granted:", t.chain())
except DelegationError as e:
    print("   refused:", e)

print("\\ncompromised orchestrator (simply does not run its own check):")
t = orchestrator_enforced(rev, "shipper", {"repo:read"}, honest=False)
print(f"   granted: depth {t.depth}  {' → '.join(t.chain())}")
print("   The limit was a line of code inside the component we no longer trust.")
'''),
  ("md", "## 4 · The control — enforce at the issuer and the resource server\n\n"
         "Both of these are outside the orchestrator's control, so a compromised "
         "orchestrator cannot skip them."),
  ("py", '''def issuer_exchange(pres, actor, scopes, max_depth=MAX_DEPTH):
    """The token issuer counts the act chain it is being asked to extend."""
    if pres.depth + 1 > max_depth:
        raise DelegationError(f"issuer refuses: depth {pres.depth+1} > {max_depth}")
    return exchange(pres, actor, scopes)

def resource_server(token, scope, max_depth=MAX_DEPTH):
    """Independent second check, at the point the action actually happens."""
    if token.depth > max_depth:
        return False, f"resource server refuses: depth {token.depth} > {max_depth}"
    if scope not in token.scopes:
        return False, f"missing scope {scope}"
    return True, f"allowed for {' → '.join(token.chain())}"

print("issuer enforcement:")
try:
    issuer_exchange(rev, "shipper", {"repo:read"})
except DelegationError as e:
    print("   ", e)

print("\\nresource server enforcement (even if a deep token somehow exists):")
deep = Token("dana@corp", "shipper", {"repo:read"},
             {"actor":"reviewer","act":{"actor":"coder",
              "act":{"actor":"orchestrator","act":None}}})
print(f"   depth {deep.depth}: {resource_server(deep, 'repo:read')}")
print(f"   depth {rev.depth}: {resource_server(rev, 'repo:read')}")
'''),
  ("py", '''# Verify: no chain the compromised orchestrator can build is ever honoured.
import random
random.seed(9)
actors = ["planner","coder","reviewer","shipper"]
honoured_too_deep = 0
for _ in range(3000):
    tok = Token("dana@corp","dana@corp", set(CEILINGS["dana@corp"]))
    for _ in range(random.randint(1,6)):
        a = random.choice(actors)
        want = set(random.sample(sorted(tok.scopes),
                                 k=random.randint(0,len(tok.scopes))))
        try:
            tok = exchange(tok, a, want)      # compromised: no depth check
        except DelegationError:
            break
    ok, _ = resource_server(tok, "repo:read")
    if ok and tok.depth > MAX_DEPTH:
        honoured_too_deep += 1
print(f"3000 chains built without any orchestrator-side limit — "
      f"over-deep chains honoured by the resource server: {honoured_too_deep}")
assert honoured_too_deep == 0
print("The limit holds because it is enforced where the orchestrator cannot reach.")
'''),
 ],
 "expect": "The three-hop chain narrows correctly to `dana@corp → orchestrator → "
           "coder → reviewer`. An honest orchestrator refuses the fourth hop; a "
           "compromised one grants it. The issuer refuses the same exchange, and "
           "the resource server refuses a depth-4 token while allowing depth 3. "
           "Over 3,000 randomly-built chains, zero over-deep chains are honoured.",
 "challenge": "Draw your own agent call graph and count the longest path. Then "
              "find where the depth limit is enforced. If the answer is \"in the "
              "orchestrator\", move it — the component that builds the chain "
              "cannot be the one that bounds it.",
},

"B2.6": {
 "concept": """
"The agent messed up" is not a defect report. It routes to nobody, and every
incident feels novel.

A failure taxonomy fixes that by making the class determine the **owner** and
the **fix**. Seven classes cover almost everything an agentic system does wrong:

| Class | What happened | Who fixes it |
|---|---|---|
| capability | the model could not do it | better model or better context |
| **verification** | it did it wrong and we believed it | harness engineer (B2.2) |
| authority | it did something it should not be able to do | identity (A2) |
| containment | the action reached further than intended | platform (A3) |
| injection | it was told to by untrusted content | provenance (C1.2) |
| budget | it never stopped | harness engineer (A3.4) |
| idempotency | it did the right thing twice | harness engineer (B2.8) |

The most important distinction in the table is between **capability** and
**verification**, because they look identical from the outside and have
completely different fixes. A capability failure means the model produced
something wrong. A verification failure means *your harness shipped it*. The
second is your defect, not the model's.
""",
 "steps": [
  ("md", "## 2 · Demo — classify eight real incidents"),
  ("py", '''INCIDENTS = [
 ("agent's patch did not compile; the loop retried and fixed it", None),
 ("agent's patch passed CI and introduced a SQL injection", None),
 ("agent deleted a production table it should never have had access to", None),
 ("agent posted the contents of .env to a public issue", None),
 ("agent approved a PR because a code comment told it to", None),
 ("agent looped for 6 hours re-running the same failing test", None),
 ("agent opened the same pull request 14 times", None),
 ("agent could not solve the task and correctly reported failure", None),
]
TAXONOMY = {
 "capability":   ("the model could not do it",              "better model / better context"),
 "verification": ("it did it wrong and we believed it",     "harness engineer — B2.2"),
 "authority":    ("it did what it should not be able to do","identity — A2"),
 "containment":  ("the action reached further than intended","platform — A3"),
 "injection":    ("untrusted content drove it",             "provenance — C1.2"),
 "budget":       ("it never stopped",                       "harness engineer — A3.4"),
 "idempotency":  ("it did the right thing twice",           "harness engineer — B2.8"),
}
LABELS = ["capability", "verification", "authority", "containment",
          "injection", "budget", "idempotency", "capability"]

for (text, _), label in zip(INCIDENTS, LABELS):
    what, owner = TAXONOMY[label]
    print(f"{label:13s} {text}")
    print(f"{'':13s} → {owner}")
'''),
  ("md", "## 3 · Where it breaks — the two that get confused\n\n"
         "Incidents 1 and 2 both start \"the agent's patch was wrong\". They are "
         "different defects with different owners, and conflating them is how a "
         "team spends a quarter upgrading models to fix a verifier."),
  ("py", '''def classify(produced_wrong_output, harness_accepted_it, action_taken):
    """The decision rule that separates capability from verification."""
    if not produced_wrong_output:
        return "not a model failure"
    if not harness_accepted_it:
        return "capability — the harness caught it, the loop worked"
    if action_taken:
        return "VERIFICATION — the harness shipped wrong work"
    return "verification (contained) — accepted but nothing acted on it"

CASES = [
 ("patch did not compile, loop retried",  True,  False, False),
 ("patch passed CI, shipped SQLi",        True,  True,  True),
 ("patch wrong, accepted, never merged",  True,  True,  False),
 ("patch correct",                        False, True,  True),
]
for name, wrong, accepted, acted in CASES:
    print(f"{name:38s} → {classify(wrong, accepted, acted)}")
print("\\nThe model was equally wrong in the first three. Only one is YOUR defect.")
'''),
  ("md", "## 4 · The control — classify automatically from the trace\n\n"
         "The taxonomy is only useful if applying it is cheap. Most of the "
         "classification is derivable from what the harness already records."),
  ("py", '''def classify_from_trace(trace):
    """trace: dict of facts the harness already has."""
    if trace.get("denied_by_policy"):        return "authority"
    if trace.get("denied_by_sandbox"):       return "containment"
    if trace.get("instruction_source") not in (None, "principal"):
        return "injection"
    if trace.get("stopped_by", "").startswith(("step budget", "time budget")):
        return "budget"
    if trace.get("duplicate_effect"):        return "idempotency"
    if trace.get("verifier_passed") and trace.get("outcome_wrong"):
        return "verification"
    if trace.get("outcome_wrong"):           return "capability"
    return "success"

TRACES = [
 {"verifier_passed": False, "outcome_wrong": True, "stopped_by": "step budget (5 steps)"},
 {"verifier_passed": True,  "outcome_wrong": True},
 {"denied_by_policy": True},
 {"denied_by_sandbox": True},
 {"instruction_source": "pull-request-diff"},
 {"stopped_by": "time budget (300s)"},
 {"duplicate_effect": True},
 {"verifier_passed": True,  "outcome_wrong": False},
]
for t in TRACES:
    cls = classify_from_trace(t)
    owner = TAXONOMY.get(cls, ("", "—"))[1]
    print(f"{cls:14s} {owner:32s} {t}")

counts = {}
for t in TRACES:
    c = classify_from_trace(t); counts[c] = counts.get(c, 0) + 1
print(f"\\ndistribution: {counts}")
assert classify_from_trace(TRACES[1]) == "verification"
'''),
 ],
 "expect": "The eight incidents classify across all seven classes with a named "
           "owner each. The capability-vs-verification rule separates the "
           "compile failure (capability — the loop worked) from the shipped SQL "
           "injection (verification — your defect). Automatic classification from "
           "trace facts reproduces the same labels.",
 "challenge": "Take your last five agent incidents and assign exactly one class "
              "to each. Any incident that seems to need two classes is really two "
              "incidents, and separating them usually reveals that one of them "
              "was never fixed.",
},

"B2.7": {
 "concept": """
A self-improving scaffold edits its own prompts, tools or routing based on how
well it is doing. It is genuinely effective, and it makes evaluation
non-optional rather than good practice.

The reason is mechanical. Optimisation moves toward whatever the metric rewards.
If the scaffold's metric is its own verifier, the scaffold will converge on
**satisfying the verifier**, which is only the same thing as doing the job if
the verifier is perfect. B2.2 established that yours is not.

So the loop is:

1. scaffold changes itself,
2. its own metric improves,
3. actual capability does not,
4. the dashboard is monotone and green.

The control is a **held-out signal**: a set of cases the scaffold cannot see,
cannot train on, and cannot reach — including through its logs. And the hard
part is not building it. It is keeping it held out.
""",
 "steps": [
  ("md", MODEL_NOTE),
  ("md", "## 2 · Demo — a scaffold optimising against its own judge"),
  ("py", '''import random

TASKS = [{"id": i, "input": i, "correct": i * 2} for i in range(1, 21)]

class Scaffold:
    """Adjusts its own strategy based on feedback. DETERMINISTIC — not a model."""
    def __init__(self):
        self.strategy = "double"        # starts correct
        self.history = []

    def solve(self, task):
        if self.strategy == "double":     return task["input"] * 2
        if self.strategy == "constant":   return 42
        return task["input"]

    def improve(self, score):
        """Move toward whatever scored better last round."""
        self.history.append((self.strategy, score))
        if len(self.history) >= 2 and self.history[-1][1] <= self.history[-2][1]:
            order = ["double", "constant", "identity"]
            self.strategy = order[(order.index(self.strategy) + 1) % 3]

def own_judge(task, answer):
    """The scaffold's own verifier: is the answer a plausible-looking number?"""
    return isinstance(answer, int) and answer > 0

def held_out_oracle(task, answer):
    """The truth. The scaffold never sees this."""
    return answer == task["correct"]

def evaluate(scaffold, verifier, tasks):
    return sum(verifier(t, scaffold.solve(t)) for t in tasks) / len(tasks)

s = Scaffold()
print(f"{'round':6s}{'strategy':11s}{'own judge':11s}{'held-out truth':15s}")
print("-" * 46)
for r in range(1, 7):
    own = evaluate(s, own_judge, TASKS)
    truth = evaluate(s, held_out_oracle, TASKS)
    print(f"{r:<6}{s.strategy:11s}{own:<11.2f}{truth:<15.2f}")
    s.improve(own)
'''),
  ("md", "## 3 · Where it breaks — the self-metric cannot fall\n\n"
         "The judge scores 1.00 for every strategy, including `constant`, which "
         "returns 42 for everything. There is no gradient for the scaffold to "
         "follow toward correctness, and no signal that anything is wrong. The "
         "dashboard is green in every round.\n\n"
         "Now let the scaffold drift, and watch the two curves separate."),
  ("py", '''s2 = Scaffold()
s2.strategy = "constant"            # a drift that the judge cannot penalise
print(f"{'round':6s}{'strategy':11s}{'own judge':11s}{'held-out truth':15s}verdict")
print("-" * 62)
for r in range(1, 5):
    own = evaluate(s2, own_judge, TASKS)
    truth = evaluate(s2, held_out_oracle, TASKS)
    verdict = "looks fine" if own > 0.9 else "alert"
    real = "BROKEN" if truth < 0.9 else "ok"
    print(f"{r:<6}{s2.strategy:11s}{own:<11.2f}{truth:<15.2f}{verdict} / actually {real}")
    s2.improve(own)
'''),
  ("md", "## 4 · The control — a held-out set, and keeping it held out\n\n"
         "Building the set is easy. The three ways it leaks are not obvious, and "
         "each one silently converts your held-out signal into another self-metric."),
  ("py", '''LEAKS = [
 ("the scaffold reads its own logs, which contain held-out failures",
  "it optimises against them without anyone deciding to"),
 ("held-out cases are added to the prompt as 'examples of hard tasks'",
  "the most common leak, and it looks like good engineering"),
 ("the same corpus is used for both tuning and evaluation",
  "the number becomes a training metric and rises forever"),
 ("a human adjusts the scaffold after reading held-out results",
  "slower leak, same effect — the human is the gradient"),
]
for how, why in LEAKS:
    print(f"✗ {how}\\n    → {why}\\n")

def evaluation_is_sound(scaffold_can_read_logs, cases_in_prompt,
                        same_corpus, human_tunes_on_results):
    problems = []
    if scaffold_can_read_logs:    problems.append("scaffold can read held-out outcomes")
    if cases_in_prompt:           problems.append("held-out cases appear in the prompt")
    if same_corpus:               problems.append("tuning and eval share a corpus")
    if human_tunes_on_results:    problems.append("human closes the loop manually")
    return (not problems), problems

for label, args in (("as usually built", (True, True, True, True)),
                    ("after the fix",    (False, False, False, False))):
    ok, problems = evaluation_is_sound(*args)
    print(f"{label:18s} sound={ok}")
    for p in problems: print(f"      ⚠ {p}")
'''),
  ("py", '''# Verify: gate the scaffold on the held-out signal, not its own.
def gated_improve(scaffold, tasks, holdout_tasks):
    before = evaluate(scaffold, held_out_oracle, holdout_tasks)
    candidate = Scaffold(); candidate.strategy = "constant"
    after = evaluate(candidate, held_out_oracle, holdout_tasks)
    if after < before:
        return scaffold, f"REJECTED change: held-out {before:.2f} → {after:.2f}"
    return candidate, f"accepted: held-out {before:.2f} → {after:.2f}"

HOLDOUT = [{"id": 100+i, "input": 100+i, "correct": (100+i)*2} for i in range(10)]
good = Scaffold()
kept, why = gated_improve(good, TASKS, HOLDOUT)
print(why)
print("final strategy:", kept.strategy)
assert kept.strategy == "double"
print("\\nThe scaffold's own judge would have accepted the change. The held-out")
print("oracle rejected it, which is the only reason the system still works.")
'''),
 ],
 "expect": "The self-judge scores 1.00 in every round regardless of strategy, "
           "while held-out truth is 1.00 only for `double`. With the scaffold "
           "drifted to `constant`, the judge still reports 1.00 and \"looks "
           "fine\" while held-out truth is 0.00 and the system is BROKEN. The "
           "leak checklist flags all four paths, and the held-out gate rejects "
           "the change the self-judge would have accepted.",
 "challenge": "For any self-tuning component you run, answer one question: can it "
              "see the outcomes of its evaluation, through any path including "
              "logs? If yes, you have a self-metric with extra steps.",
},

"B2.8": {
 "concept": """
Your agent will do the same thing twice. Retries, restarts, a duplicated webhook,
a loop that lost track — the cause varies and the outcome does not.

Whether that matters depends entirely on the action:

- **Naturally idempotent**: setting a config value, adding a label. Doing it
  twice is doing it once.
- **Accumulating**: posting a comment, sending an email. Twice is noise.
- **Dangerous**: issuing a refund, rotating a credential, scaling a cluster.
  Twice is an incident.

The mechanism is an **idempotency key**: a caller-supplied identifier derived
from the *intent*, so a retry of the same intent lands once. The subtlety is
choosing what goes into the key. Include a timestamp and every retry is a new
operation. Include too little and two genuinely different requests collide.

The second half of this lesson is **replay** — the same property viewed from
forensics. A run you cannot deterministically replay is a run you can describe
but not demonstrate, and D2.5 depends on this being right.
""",
 "steps": [
  ("md", "## 2 · Demo — the same action, three natures"),
  ("py", '''import hashlib, json
from dataclasses import dataclass, field

@dataclass
class Ledger:
    applied: dict = field(default_factory=dict)
    effects: list = field(default_factory=list)

    def apply(self, key, op, **args):
        if key in self.applied:
            self.effects.append(f"SKIP  {op} (key {key[:8]} already applied)")
            return False
        self.applied[key] = (op, args)
        self.effects.append(f"APPLY {op} {args}")
        return True

def idem_key(op, **args):
    """Derived from INTENT. No timestamp, no attempt number."""
    blob = json.dumps({"op": op, "args": args}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()

led = Ledger()
# the agent retries the same refund three times
for attempt in range(3):
    k = idem_key("issue_refund", order="ORD-4471", amount=250)
    led.apply(k, "issue_refund", order="ORD-4471", amount=250)
# a genuinely different refund
led.apply(idem_key("issue_refund", order="ORD-4472", amount=90),
          "issue_refund", order="ORD-4472", amount=90)

print("\\n".join(led.effects))
print(f"\\n4 calls → {len(led.applied)} effects")
'''),
  ("md", "## 3 · Where it breaks — a key that includes the wrong thing"),
  ("py", '''import time

def bad_key_timestamp(op, **args):
    return hashlib.sha256(f"{op}{args}{time.time()}".encode()).hexdigest()

def bad_key_too_narrow(op, **args):
    return hashlib.sha256(op.encode()).hexdigest()          # op only!

led2 = Ledger()
for attempt in range(3):
    led2.apply(bad_key_timestamp("issue_refund", order="ORD-4471", amount=250),
               "issue_refund", order="ORD-4471", amount=250)
print("key includes a timestamp — every retry is a new operation:")
print("\\n".join(led2.effects))
print(f"→ refunded {sum(1 for e in led2.effects if e.startswith('APPLY')) * 250} "
      f"instead of 250\\n")

led3 = Ledger()
led3.apply(bad_key_too_narrow("issue_refund", order="ORD-4471", amount=250),
           "issue_refund", order="ORD-4471", amount=250)
led3.apply(bad_key_too_narrow("issue_refund", order="ORD-9999", amount=800),
           "issue_refund", order="ORD-9999", amount=800)
print("key includes only the op — different refunds collide:")
print("\\n".join(led3.effects))
print("→ the second customer never got their money")
'''),
  ("md", "## 4 · The control — classify the action, then key on intent"),
  ("py", '''ACTIONS = {
 "set_config":     ("naturally idempotent", False),
 "add_label":      ("naturally idempotent", False),
 "post_comment":   ("accumulating",         True),
 "send_email":     ("accumulating",         True),
 "issue_refund":   ("dangerous",            True),
 "rotate_secret":  ("dangerous",            True),
 "scale_cluster":  ("dangerous",            True),
}
print(f"{'action':16s}{'nature':22s}needs a key")
print("-" * 52)
for a, (nature, needs) in ACTIONS.items():
    print(f"{a:16s}{nature:22s}{needs}")

def guarded_call(led, op, **args):
    nature, needs_key = ACTIONS[op]
    if not needs_key:
        led.effects.append(f"APPLY {op} {args} (idempotent by nature)")
        return True
    return led.apply(idem_key(op, **args), op, **args)

led4 = Ledger()
for _ in range(2):
    guarded_call(led4, "set_config", key="tls_min", value="1.2")
    guarded_call(led4, "issue_refund", order="ORD-4471", amount=250)
print("\\n" + "\\n".join(led4.effects))
'''),
  ("py", '''# Verify — replay: the forensic half of the same property.
@dataclass
class Replay:
    prompts: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)
    model_version: str = ""
    seed: object = None
    def replayable(self):
        missing = []
        if not self.prompts:      missing.append("prompts not recorded")
        if not self.tool_results: missing.append("tool results not recorded — "
                                                 "the agent saw a world you cannot rebuild")
        if not self.model_version: missing.append("model version not pinned — "
                                                  "a silent upgrade changes the output")
        if self.seed is None:     missing.append("no seed — sampling makes it unrepeatable")
        return (not missing), missing

for name, r in (("fully instrumented", Replay(["p"], ["tool out"], "glm-4.6@2026-07", 42)),
                ("typical production", Replay(["p"], ["tool out"], "", None)),
                ("actions only",       Replay([], [], "", None))):
    ok, missing = r.replayable()
    print(f"{name:22s} replayable={ok}")
    for m in missing: print(f"      ✗ {m}")
assert Replay(["p"], ["t"], "m", 1).replayable()[0]
'''),
 ],
 "expect": "Four refund calls with intent-derived keys produce two effects. A "
           "timestamped key refunds 750 instead of 250; an op-only key collides "
           "and the second customer is never refunded. The action table marks "
           "config and labels as needing no key. The replay check passes only the "
           "fully instrumented run, flagging the typical production run for a "
           "missing pinned model version and seed.",
 "challenge": "List the actions your harness can take and mark the dangerous "
              "ones. Then check whether each has a key, and what goes into it. A "
              "key containing a timestamp or an attempt number is not a key.",
},

"B2.11": {
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

A **harness** is everything wrapped around that model which turns it into
something that gets work done:

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

"B2.9": {
 "concept": """
Teams build a SAST harness, then a threat-modelling harness, then a DAST
harness, then a pentest harness — and re-decide loop control, budgets, retries
and verification four times. The loops end up nearly identical, and the four
teams each get one thing wrong in their own way.

They are the same skeleton. Plan a candidate, act on it, verify it, stop. What
actually differs between the four is two things, and both belong to the domain
rather than to the loop:

**The oracle** — what decides a candidate is real. Reachability plus a failing
test for static analysis. A diff against the previous model for threat
modelling. An observed change in a response for DAST. A shell, a row or a file
for a pentest. The oracle is the whole value of the harness: everything else is
plumbing you have already built once.

**The blast radius** — what acting costs if the candidate is wrong. Reading
source costs nothing. Sending a request to a replica costs a little. Running an
exploit against a live host costs an incident, so it needs an authorisation the
loop cannot grant itself.

Build the skeleton once. Then a new domain is an oracle, a blast radius, and
nothing else.
""",
 "steps": [
  ("md", "## 2 · One skeleton, and the two things a domain supplies"),
  ("py", '''DOMAINS = {
 "sast":         {"reads": "source at a commit",     "blast": "read-only"},
 "threat model": {"reads": "architecture and IaC",   "blast": "read-only"},
 "dast":         {"reads": "a running replica",      "blast": "replica-write"},
 "pentest":      {"reads": "an owned host in scope", "blast": "live-action"},
}
ORACLES = {
 "sast":         ("reachable from an entrypoint AND a failing test",
                  lambda e: e["reachable"] and e["failing_test"]),
 "threat model": ("present in the new model and absent from the old",
                  lambda e: e["in_new"] and not e["in_old"]),
 "dast":         ("response differs from the control request",
                  lambda e: e["response_differs"]),
 "pentest":      ("an artefact that should not have been obtainable",
                  lambda e: e["artefact"] is not None),
}
AUTHORISED = {"read-only", "replica-write"}      # live-action needs a signed scope

def harness(domain, candidates, oracle, budget=6, scope_signed=False):
    """The skeleton. Identical for all four domains."""
    blast = DOMAINS[domain]["blast"]
    if blast not in AUTHORISED and not scope_signed:
        return {"domain": domain, "refused": "live action without a signed scope",
                "confirmed": [], "steps": 0}
    confirmed, steps = [], 0
    for c in sorted(candidates, key=lambda c: c["id"]):
        if steps >= budget:
            break
        steps += 1
        if oracle(c["evidence"]):
            confirmed.append(c)
    return {"domain": domain, "refused": None, "confirmed": confirmed, "steps": steps}

for d in sorted(DOMAINS):
    print(f"{d:14s}{DOMAINS[d]['blast']:14s}oracle: {ORACLES[d][0]}")
'''),

  ("md", "## 3 · Four domains through the same loop"),
  ("py", '''CANDIDATES = {
 "sast": [
  {"id": "unit_07 CWE-89 in build_query", "real": True,
   "evidence": {"reachable": True,  "failing_test": True}},
  {"id": "unit_12 CWE-89 in log_line",    "real": False,
   "evidence": {"reachable": False, "failing_test": False}},
  {"id": "unit_31 CWE-22 in export_path", "real": True,
   "evidence": {"reachable": True,  "failing_test": True}}],
 "threat model": [
  {"id": "worker -> db crosses trust 0 to 2", "real": True,
   "evidence": {"in_new": True,  "in_old": False}},
  {"id": "component web renamed to frontend", "real": False,
   "evidence": {"in_new": True,  "in_old": True}},
  {"id": "/admin/export on an untrusted entry", "real": True,
   "evidence": {"in_new": True,  "in_old": False}}],
 "dast": [
  {"id": "GET /v1/users returns 200 unauthenticated", "real": True,
   "evidence": {"response_differs": True}},
  {"id": "banner discloses framework version",        "real": False,
   "evidence": {"response_differs": False}},
  {"id": "POST /report reflects payload unencoded",   "real": True,
   "evidence": {"response_differs": True}}],
 "pentest": [
  {"id": "password auth permits spraying, no lockout", "real": True,
   "evidence": {"artefact": "session as svc-reports"}},
  {"id": "expired certificate on the partner CDN",     "real": False,
   "evidence": {"artefact": None}},
  {"id": "/backup listing exposes a database dump",    "real": True,
   "evidence": {"artefact": "orders.sql, 41 MB"}}],
}

def precision(result, candidates):
    if not result["confirmed"]:
        return None
    return sum(c["real"] for c in result["confirmed"]) / len(result["confirmed"])

print(f"{'domain':14s}{'confirmed':>10}{'precision':>11}  note")
for d in sorted(DOMAINS):
    r = harness(d, CANDIDATES[d], ORACLES[d][1], scope_signed=True)
    p = precision(r, CANDIDATES[d])
    print(f"{d:14s}{len(r['confirmed']):>10}{p:>11.2f}  {ORACLES[d][0][:38]}")

r = harness("pentest", CANDIDATES["pentest"], ORACLES["pentest"][1])
print(f"\\npentest without a signed scope: {r['refused']}")
assert r["confirmed"] == []
'''),

  ("md", "## 4 · Where it breaks — the oracle everyone reaches for\\n\\n"
         "Every one of those four oracles is a fact about the target. The "
         "tempting fifth is the model's own opinion, because it is the only one "
         "that works in every domain without being built."),
  ("py", '''def model_oracle(evidence):
    """The model read the evidence and is confident. Confidence is not an oracle."""
    return True

print(f"{'domain':14s}{'confirmed':>10}{'precision':>11}")
for d in sorted(DOMAINS):
    r = harness(d, CANDIDATES[d], model_oracle, scope_signed=True)
    print(f"{d:14s}{len(r['confirmed']):>10}{precision(r, CANDIDATES[d]):>11.2f}")

total = sum(len(CANDIDATES[d]) for d in CANDIDATES)
real = sum(c["real"] for d in CANDIDATES for c in CANDIDATES[d])
print(f"\\nevery one of {total} candidates confirmed; {real} of them are real.")
print("Precision 0.67 in every domain, and it looks like 1.00 from inside the")
print("harness, because the thing producing the finding is also the thing")
print("agreeing with it.")
assert all(precision(harness(d, CANDIDATES[d], model_oracle, scope_signed=True),
                     CANDIDATES[d]) < 1.0 for d in DOMAINS)
'''),

  ("md", "## 5 · The control — classify the oracle, gate on the class"),
  ("py", '''ORACLE_CLASS = {
 "sast":         "deterministic",   # re-runs to the same answer on the same commit
 "threat model": "deterministic",
 "dast":         "observational",   # a real observation, but of a system that moves
 "pentest":      "observational",
 "model":        "judgement",       # not re-checkable, not falsifiable
}
MAY_FILE = {"deterministic", "observational"}

def dispatch(domain, oracle_name, result):
    cls = ORACLE_CLASS[oracle_name]
    return {"domain": domain, "oracle_class": cls,
            "action": "file the finding" if cls in MAY_FILE else "queue for a human",
            "count": len(result["confirmed"])}

for d in sorted(DOMAINS):
    good = harness(d, CANDIDATES[d], ORACLES[d][1], scope_signed=True)
    bad  = harness(d, CANDIDATES[d], model_oracle, scope_signed=True)
    print(dispatch(d, d, good))
    print(dispatch(d, "model", bad))

print()
print("The skeleton did not change once across four domains. What changed was")
print("the oracle and the blast radius - which is the whole argument for")
print("building the loop once and never again.")
assert dispatch("sast", "model", harness("sast", CANDIDATES["sast"], model_oracle,
                scope_signed=True))["action"] == "queue for a human"
'''),
 ],
 "expect": "One skeleton runs all four domains unchanged. With each domain's own "
           "oracle every confirmed finding is real — precision 1.00 across sast, "
           "threat model, dast and pentest — and the pentest run refuses "
           "outright without a signed scope, because its blast radius is live "
           "action. Swapping in the model's own confidence as the oracle confirms "
           "all 12 candidates, 8 of which are real: precision 0.67 in every "
           "domain, invisible from inside the harness.",
 "challenge": "Name the oracle for the harness you are building. If the sentence "
              "contains the words 'the model determines', you have a judgement, "
              "not an oracle — and the finding belongs in a human queue rather "
              "than in a ticket.",
},

"B2.10": {
 "concept": """
Two questions get confused here, and only one of them is worth your time.

The first is *which model is best for security work right now*. As of writing:
Kimi K2.6 and K2.7-Code hold up well on long-horizon repository work, the GLM-5.x
line performs strongly on vulnerability discovery, and frontier models still lead
on deep exploitation chains. That paragraph will be wrong within a quarter, and
anything built on it will be wrong with it.

The second question is the one that lasts: **can you substitute the backbone
without rewriting the harness?** If swapping a model means touching prompt
assembly, tool schemas, parsing and retry logic, then the honest answer is that
you did not choose a model — you married one.

So the discipline is:

- Evaluate on **your corpus**, not a vendor chart. The chart measures a
  distribution that is not yours, on tasks that are not yours.
- Put the backbone behind an **interface** — one adapter, one place to change.
- Keep the eval so a substitution is a measurement, not an argument.
- Weigh what the chart never shows: data sovereignty, cost per finding, and
  whether your estate is allowed to send code to that endpoint at all.
""",
 "steps": [
  ("md", "## 2 · An interface, so the backbone is a parameter\\n\\n"
         "Three stand-in backbones with deliberately different behaviour. None "
         "is a language model; each stands in for one so substitution is visible."),
  ("py", '''CORPUS = [
 # (unit, true_cwe)
 ("get_report",   "CWE-22"), ("run_export", "CWE-78"), ("safe_query", None),
 ("legacy_dump",  "CWE-89"), ("render_row", None),     ("admin_purge", "CWE-78"),
]

def backbone_a(unit):                 # strong on injection, misses traversal
    return {"run_export": "CWE-78", "legacy_dump": "CWE-89",
            "admin_purge": "CWE-78"}.get(unit)
def backbone_b(unit):                 # broad recall, some false positives
    return {"get_report": "CWE-22", "run_export": "CWE-78", "legacy_dump": "CWE-89",
            "admin_purge": "CWE-78", "render_row": "CWE-79"}.get(unit)
def backbone_c(unit):                 # conservative
    return {"run_export": "CWE-78"}.get(unit)

BACKBONES = {"kimi-k2.6-stand-in": backbone_a,
             "glm-5.2-stand-in":   backbone_b,
             "small-local-stand-in": backbone_c}

def harness(find, corpus):
    """The harness. Note it takes `find` as an argument - that is the point."""
    return [(u, find(u)) for u, _ in corpus if find(u)]

for name in sorted(BACKBONES):
    out = harness(BACKBONES[name], CORPUS)
    print(f"{name:22s}{len(out)} findings")
'''),

  ("md", "## 3 · Score them on your corpus, not on a chart"),
  ("py", '''def score(find, corpus, cost_per_call=0.004):
    truth = dict(corpus)
    found = harness(find, corpus)
    tp = [u for u, c in found if truth.get(u) == c]
    fp = [u for u, c in found if truth.get(u) != c]
    planted = [u for u, c in corpus if c]
    fn = [u for u in planted if u not in [x for x, _ in found]]
    recall = len(tp) / len(planted)
    prec = len(tp) / len(found) if found else 0.0
    spend = len(corpus) * cost_per_call
    return {"recall": recall, "precision": prec, "tp": len(tp), "fp": len(fp),
            "fn": len(fn), "spend": spend,
            "cost_per_tp": (spend / len(tp)) if tp else float("inf")}

print(f"{'backbone':22s}{'recall':>8}{'prec':>7}{'tp':>4}{'fp':>4}{'fn':>4}{'$/finding':>11}")
results = {}
for name in sorted(BACKBONES):
    s = score(BACKBONES[name], CORPUS)
    results[name] = s
    print(f"{name:22s}{s['recall']:>7.0%}{s['precision']:>7.0%}"
          f"{s['tp']:>4}{s['fp']:>4}{s['fn']:>4}{s['cost_per_tp']:>10.3f}")
best_recall = max(results, key=lambda n: (results[n]["recall"], n))
best_cost = min(results, key=lambda n: (results[n]["cost_per_tp"], n))
print(f"\\nbest recall        : {best_recall}")
print(f"best cost/finding  : {best_cost}")
print("They are not the same backbone, and which one you want depends on")
print("whether an analyst reviews the output or a ticket is opened from it.")
'''),

  ("md", "## 4 · Where it breaks — the harness that married its model"),
  ("py", '''def coupled_harness(unit, backbone_name):
    """Prompt assembly, parsing and retry all keyed to one vendor's quirks."""
    if backbone_name == "kimi-k2.6-stand-in":
        raw = backbone_a(unit)
        return raw                                   # returns a bare CWE
    if backbone_name == "glm-5.2-stand-in":
        raw = backbone_b(unit)
        return {"cwe": raw} if raw else None         # returns an object
    raise KeyError(f"no parsing branch for {backbone_name}")

for name in sorted(BACKBONES):
    try:
        out = [u for u, _ in CORPUS if coupled_harness(u, name)]
        print(f"   {name:22s}{len(out)} findings")
    except KeyError as e:
        print(f"   {name:22s}FAILS: {e}")
print()
print("Adding a third backbone to the coupled harness is a code change in the")
print("parser, the prompt and the retry path. Adding it to the harness above is")
print("a dictionary entry. Same models, same corpus - the difference is where")
print("the vendor's shape was allowed to leak to.")
'''),

  ("md", "## 5 · The control — substitute behind an unchanged interface"),
  ("py", '''def substitute(harness_fn, corpus, frm, to):
    before = score(BACKBONES[frm], corpus)
    after  = score(BACKBONES[to], corpus)
    return {"from": frm, "to": to,
            "recall": (before["recall"], after["recall"]),
            "precision": (before["precision"], after["precision"]),
            "cost_per_tp": (round(before["cost_per_tp"], 3), round(after["cost_per_tp"], 3)),
            "harness_changed": False}

sw = substitute(harness, CORPUS, "kimi-k2.6-stand-in", "glm-5.2-stand-in")
for k, v in sw.items():
    print(f"   {k:16s}{v}")
print()
print("Recall up, precision down, cost per finding down. That is a decision with")
print("numbers behind it, taken in one line, and reversible in one line.")
assert sw["harness_changed"] is False
'''),

  ("md", "## 6 · Verify — the constraints the chart never shows"),
  ("py", '''CONSTRAINTS = {
 "kimi-k2.6-stand-in":   {"weights": "open", "self_hostable": True,  "code_leaves_estate": False},
 "glm-5.2-stand-in":     {"weights": "open", "self_hostable": True,  "code_leaves_estate": False},
 "frontier-api-stand-in":{"weights": "closed","self_hostable": False, "code_leaves_estate": True},
}
print(f"{'backbone':24s}{'weights':9s}{'self-host':11s}source code leaves the estate")
for n in sorted(CONSTRAINTS):
    c = CONSTRAINTS[n]
    print(f"{n:24s}{c['weights']:9s}{str(c['self_hostable']):11s}{c['code_leaves_estate']}")
print()
eligible = [n for n, c in sorted(CONSTRAINTS.items()) if not c["code_leaves_estate"]]
print(f"eligible where source may not leave the estate: {eligible}")
print()
print("For a great many organisations this single column removes the top of")
print("every published leaderboard before accuracy is discussed at all - which")
print("is the strongest argument for designing the substitution seam early.")
assert "frontier-api-stand-in" not in eligible
'''),
 ],
 "expect": "Three stand-in backbones are scored on the same corpus: the one with "
           "the best recall is not the one with the best cost per finding. A "
           "harness that couples to vendor output shapes fails outright on the "
           "third backbone, while the interface version substitutes in a single "
           "line and reports the recall, precision and cost deltas. A data-"
           "sovereignty column then removes the closed-weights option entirely.",
 "challenge": "Time how long it takes to swap the backbone in your own harness. "
              "If it is more than an afternoon, that number — not a benchmark — "
              "is what will decide your model choice for the next two years.",
},

"B2.12": {
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
