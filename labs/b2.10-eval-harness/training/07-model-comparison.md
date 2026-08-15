# Chapter 7 — Comparing Models: Which Engine for Which Job

**Board time:** ~35 min · **Prereqs:** Ch 1–6 · **Markers:** orange, green, red, blue, white

### Learning objectives
1. Run the **same blind audit across models** and read the results table.
2. Explain each model's **failure theme** and why ranking isn't monotonic.
3. Pick the right model per task and **reduce token cost** with evidence.

---

## Panel 1 — Same harness, swap the engine

**🖊️ DRAW:** One white harness box with a swappable orange **"MODEL"** slot.
Three chips lined up to drop in: **Opus / Sonnet / Haiku.** Same blue answer key
underneath.

```
   [ Cyber Harness  ( MODEL ⬒ ) ]  ←  Opus | Sonnet | Haiku
                 same code, same prompt, same answer key
```

**🎙️ SAY:** "Back to Chapter 3's punchline: the model is the swappable engine.
So we run the *identical* blind audit — same files, same prompt, same answer key
— three times, once per model. Anything that differs is the model, not the setup.
This is a controlled experiment."

---

## Panel 2 — The results (three tasks × three models)

**🖊️ DRAW:** A 3×3 grid. Rows = tasks (**SAST**, **CVE**, **IaC**). Columns =
models. Fill the headline numbers; circle the best in each row green.

```
   task \ model   Opus     Sonnet    Haiku
   SAST (synth)   (0.90)*   0.75      0.61
   CVE  (real)    0.87     (0.95)*    0.47
   IaC  (config)  (0.76)*   0.66      0.58     *=best
```

**🎙️ SAY:** "Read the grid. On synthetic SAST, Opus wins (0.90). On **real CVE
code, Sonnet wins big — 0.95** — while Haiku collapses to 0.47. On IaC, Opus again.
Two lessons jump out. One: the model matters *enormously* — the same code swings
from 0.47 to 0.95 just by changing engines. Two: **the ranking flips between rows**
— nobody wins everywhere. That non-monotonic pattern is the interesting result,
and it's why you benchmark on *your* task instead of trusting a leaderboard."

---

## Panel 3 — Failure themes (why each model loses)

**🖊️ DRAW:** Three orange model boxes, each with a red "theme" tag.
Opus → **"misses NULL-deref (CWE-476)."** Sonnet → **"false positives on safe
toys."** Haiku → **"misses real bugs."**

```
   Opus   ──▶ blind spot: CWE-476 NULL-deref (reads it as path traversal)
   Sonnet ──▶ over-flags SAFE synthetic files (but precise on real code!)
   Haiku  ──▶ defaults to "safe" → misses real vulns (recall 0.20)
```

**🎙️ SAY:** "Averages hide *how* a model fails, so we read the failing questions.
**Opus** is calibrated but has one blind spot: NULL-pointer bugs, which it keeps
labeling as path traversal. **Sonnet** over-flags the *safe* synthetic files —
lots of false positives on toys — yet on real code that same eagerness becomes
*zero* false positives and the best score. **Haiku** does the opposite on real
code: it plays it safe and *misses* most real bugs, recall just 0.20. Same models,
opposite failure directions. You cannot get this from a single accuracy number —
only from the by-CWE and failing-question breakdowns."

**📓 FIELD NOTE:** "'Which model is best?' is the wrong question. 'Best at what,
failing how, at what cost?' is the right one. A model that over-flags is a triage
problem; a model that under-flags is a *coverage* problem — and coverage gaps are
the ones that get you breached."

---

## Panel 4 — Which model, where

**🖊️ DRAW:** A routing diagram: a task icon splitting into three arrows →
**SAST → Opus**, **Pentest/CVE → Sonnet**, **IaC → Opus**. A red ✗ over
"**Haiku as filter on real code**."

```
   task ─┬─ SAST triage      ─▶ Opus
         ├─ pentest / real CVE ─▶ Sonnet
         ├─ IaC / threat model ─▶ Opus
         └─ cheap pre-filter on real code ─▶ ✗ NOT Haiku (recall 0.20)
```

**🎙️ SAY:** "Turn the evidence into a routing rule. SAST triage and IaC → Opus,
most consistent. Real-CVE / pentest reasoning → Sonnet, best where it counts.
And a hard *don't*: never use Haiku as a cheap 'is this safe? skip it' filter on
real code — at 0.20 recall it would wave through four out of five real bugs. The
cheap-filter trick only works when the cheap model has *high recall*."

---

## Panel 5 — Token-maxxing (cost vs accuracy)

**🖊️ DRAW:** A scatter: x-axis **tokens (cost)**, y-axis **accuracy**. Plot three
dots: Haiku (low cost, low acc), Opus (high cost, high acc), Sonnet (high cost,
highest acc on real). Circle Sonnet as **"best value on real code."**

```
   acc ▲
   .95 |                 ● Sonnet  ← best value (real)
   .87 |            ● Opus
   .47 | ● Haiku
       └───────────────────────▶ tokens
```

**🎙️ SAY:** "Finally, cost. More tokens = more money, so match the model to the
job instead of maxing everything. Measured tips: **route by task** — IaC costs
about the same for all three, so take the best (Opus); on real code Sonnet
matches Opus's tokens at higher accuracy. **Batch files per call** so you pay for
the instructions once. **Constrain the output** to a compact verdict, not an
essay — output tokens dominate. And the anti-pattern: don't 'save money' with a
cheap first-pass model that has low recall — you're not saving, you're *missing
bugs*."

---

## ✅ Recap
- Swap only the **model** to isolate its effect; run the same blind audit 3×.
- Results are **non-monotonic**: Opus best on SAST/IaC, Sonnet best on real CVEs, Haiku weak on real code.
- **Failure themes:** Opus misses CWE-476; Sonnet false-positives on safe toys; Haiku misses real bugs.
- **Route by task**; never use a low-recall model as a cheap filter.
- **Reduce tokens** by routing, batching, and constraining output — not by under-powering the audit.

## 🧠 Check yourself
1. Why run the *same* files/prompt across all three models?
2. Sonnet over-flags toys but is best on real code — what does that tell you about synthetic benchmarks?
3. Why is a low-recall "cheap filter" a false economy?

## 🛠️ Try it on the board's source
Reproduce the grid: `python work_mantis/compare_models.py` (code) and
`python work_mantis/compare_iac.py` (IaC). Read failure themes in
`work_mantis/failing_questions.md` and the full write-up in
[`../docs/MODEL_COMPARISON.md`](../docs/MODEL_COMPARISON.md).
