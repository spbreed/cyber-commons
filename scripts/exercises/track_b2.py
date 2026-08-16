"""B2 — The Security Automation / Harness Engineer. Ten sessions.

The track builds one artefact, in order, and each lesson modifies the previous:

    B2.1  the loop            plan → act → verify → stop
    B2.2  the verifier        the single highest-value hour in the track
    B2.3  tool design         the signature is the control
    B2.4  budgets             what works when everything else has failed
    B2.5  model routing       inside the loop this time
    B2.6  sub-agents          depth, and what it does to authority
    B2.7  failure taxonomy    so "it broke" routes to the right owner
    B2.8  self-improvement    why a held-out signal stops being optional
    B2.9  idempotency         it will do the same thing twice
    B2.10 evaluation          conformance vs accuracy, and the matching bug
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
     "use for conformance ONLY, never for quality — see B2.10"),
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
Budgets are the only control that still works when everything else has failed —
including the verifier.

Two budgets, bounding different things:

- **Step budget** bounds *cost*. It caps how many times the loop can iterate.
- **Time budget** bounds *damage*. A loop calling a fast tool can complete
  thousands of actions in the seconds a step budget still permits.

You need both, and you need to decide what happens when one fires. There are
three options and they are not equivalent:

1. **Halt** — stop and leave the world as it is. Safe when actions are additive.
2. **Roll back** — undo the partial work. Requires every action to be undoable.
3. **Escalate** — hand to a human with the trace. The only right answer when
   the work is half-done and not undoable.

A harness that halts mid-way through a multi-step change and cannot say which
steps completed has not been contained; it has been abandoned.
""",
 "steps": [
  ("md", "## 2 · Demo — a loop that never converges"),
  ("py", '''import time
from dataclasses import dataclass, field

class ReplayModel:
    """DETERMINISTIC REPLAY — not a language model."""
    def __init__(self, proposals): self.proposals, self.calls = list(proposals), 0
    def propose(self, _):
        p = self.proposals[min(self.calls, len(self.proposals)-1)]; self.calls += 1
        return p

def never_satisfied(_): return False, "still not right"

def run(model, verifier, max_steps=5, max_seconds=10.0):
    steps, started = [], time.monotonic()
    for n in range(1, max_steps+1):
        p = model.propose("")
        ok, why = verifier(p)
        steps.append((n, p, ok, why))
        if ok:   return steps, "verifier satisfied"
        if time.monotonic() - started > max_seconds:
            return steps, f"time budget ({max_seconds}s)"
    return steps, f"step budget ({max_steps} steps)"

spinner = lambda: ReplayModel(["retrying the same approach"])
for limit in (1, 3, 10):
    steps, why = run(spinner(), never_satisfied, max_steps=limit)
    print(f"max_steps={limit:>3} → {len(steps):>3} steps, stopped by {why}")

steps, why = run(spinner(), never_satisfied, max_steps=10_000, max_seconds=0.05)
print(f"\\ntime budget      → {len(steps):>3} steps, stopped by {why}")
print("The step budget alone would have permitted 10,000 iterations.")
'''),
  ("md", "## 3 · Where it breaks — the loop stops half-way through a change\n\n"
         "Budgets that only halt leave the system in a state nobody chose. Here "
         "is a three-step remediation that gets cut off after step two."),
  ("py", '''@dataclass
class World:
    firewall_rule_added: bool = False
    service_restarted: bool = False
    monitoring_updated: bool = False
    def state(self):
        return {k: v for k, v in vars(self).items()}

PLAN = [("add firewall rule",  "firewall_rule_added"),
        ("restart service",    "service_restarted"),
        ("update monitoring",  "monitoring_updated")]

def apply_plan(world, budget):
    done = []
    for i, (label, attr) in enumerate(PLAN, 1):
        if i > budget:
            return done, f"budget exhausted after step {i-1}"
        setattr(world, attr, True)
        done.append(label)
    return done, "complete"

w = World()
done, why = apply_plan(w, budget=2)
print("plan:", [p[0] for p in PLAN])
print("done:", done)
print("why :", why)
print("world state:", w.state())
print("\\nThe firewall now blocks traffic the service needs, the service has been")
print("restarted into that condition, and monitoring does not know to alert.")
print("Halting was worse than either finishing or never starting.")
'''),
  ("md", "## 4 · The control — choose the stop behaviour per action class"),
  ("py", '''ACTIONS = {
 # action                 undoable?  safe to leave half-done?
 "add firewall rule":     (True,     False),
 "restart service":       (False,    False),
 "update monitoring":     (True,     True),
 "post a comment":        (False,    True),
 "open a pull request":   (True,     True),
 "merge a pull request":  (False,    False),
}
def stop_behaviour(action):
    undoable, safe_partial = ACTIONS[action]
    if safe_partial:            return "HALT — additive, safe to leave"
    if undoable:                return "ROLL BACK — undo what completed"
    return "ESCALATE — half-done and not undoable; hand the trace to a human"

for a in ACTIONS:
    print(f"{a:24s}{stop_behaviour(a)}")
'''),
  ("py", '''# Verify: a budgeted run that rolls back or escalates correctly.
@dataclass
class Runner:
    world: World = field(default_factory=World)
    applied: list = field(default_factory=list)

    def apply(self, label, attr):
        setattr(self.world, attr, True); self.applied.append((label, attr))

    def rollback(self):
        undone = []
        for label, attr in reversed(self.applied):
            if ACTIONS[label][0]:                       # undoable
                setattr(self.world, attr, False); undone.append(label)
            else:
                return undone, f"cannot undo {label!r} — escalating"
        return undone, "fully rolled back"

    def run(self, plan, budget):
        for i, (label, attr) in enumerate(plan, 1):
            if i > budget:
                worst = [l for l, _ in self.applied if not ACTIONS[l][1]]
                if not worst:
                    return "HALT", "all completed actions are safe to leave"
                undone, detail = self.rollback()
                return ("ESCALATE" if "escalat" in detail else "ROLLBACK"), detail
            self.apply(label, attr)
        return "COMPLETE", "plan finished"

for budget in (1, 2, 3):
    r = Runner()
    verdict, detail = r.run(PLAN, budget)
    print(f"budget={budget}  {verdict:9s} {detail}")
    print(f"          world: {r.world.state()}")
'''),
 ],
 "expect": "Each step budget is honoured exactly; the time budget stops the loop "
           "far short of 10,000 steps. The half-applied plan leaves a firewall "
           "rule blocking a service that was then restarted. The per-action table "
           "assigns HALT, ROLL BACK and ESCALATE correctly, and the budgeted "
           "runner rolls back at budget 1 and escalates at budget 2 because the "
           "service restart cannot be undone.",
 "challenge": "Classify every action your harness can take into the three "
              "columns. The ones that are neither undoable nor safe to leave "
              "half-done are the ones that need a human in the escalation path — "
              "and they are usually the ones nobody has thought about.",
},

"B2.5": {
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

"B2.6": {
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

"B2.7": {
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
| injection | it was told to by untrusted content | provenance (C1.3) |
| budget | it never stopped | harness engineer (B2.4) |
| idempotency | it did the right thing twice | harness engineer (B2.9) |

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
 "injection":    ("untrusted content drove it",             "provenance — C1.3"),
 "budget":       ("it never stopped",                       "harness engineer — B2.4"),
 "idempotency":  ("it did the right thing twice",           "harness engineer — B2.9"),
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

"B2.8": {
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

"B2.9": {
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

"B2.10": {
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
}
