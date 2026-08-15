# Chapter 8 — From Eval to Pipeline: Gates, Governance, and Guardrails

**Board time:** ~30 min · **Prereqs:** Ch 1–7 · **Markers:** white, green, red, orange, blue

### Learning objectives
1. Wire the eval in as an automated **CI / pipeline gate** (the Evaluation & Risk Gate).
2. Explain **regression detection** with a threshold.
3. Handle real-world realities: **cyber safeguards**, the **oracle's limits**, and governance-by-evidence.

---

## Panel 1 — The eval becomes a gate

**🖊️ DRAW:** A pipeline: **harness run → produce findings → [EVAL GATE] →
deploy.** The gate is a green diamond with two exits: **pass ✓ (accuracy ≥ 0.80)
→ deploy** and **fail ✗ → block + alert.**

```
   harness ─▶ findings ─▶ ◆ EVAL GATE ◆ ─┬─ accuracy ≥ 0.80 ─▶ deploy ✓
                          (score vs truth) └─ below         ─▶ BLOCK ✗ + alert
```

**🎙️ SAY:** "Everything we built becomes one automated gate. On every change to
the harness — new prompt, new model, new version — we re-run the benchmark. If
accuracy stays above a threshold, the change ships. If it drops, the gate
**blocks** and alerts a human. This is the **Evaluation & Risk Gate** from the
pipeline chapter of the book, made real: probabilistic behavior gets *tested*
before it's trusted, exactly like unit tests gate normal code."

---

## Panel 2 — Regression detection

**🖊️ DRAW:** A trend line of accuracy over time (green) that suddenly dips below
a dashed red line labeled **"--min-acc 0.80."** A red flag at the dip.

```
   acc │ ●─●─●─●          ← healthy
       │           ●╲
   0.80├───────────────╲──── threshold (--min-acc)
       │                 ●   🚩 regression → non-zero exit
       └────────────────────▶ builds over time
```

**🎙️ SAY:** "The gate is one flag: `--min-acc 0.80`. The benchmark **exits
non-zero** if accuracy falls below it, which fails the CI build — the same signal
as a broken test. Someone tweaks a prompt to fix one bug and silently breaks five
others? The trend line dips under the red threshold and the build goes red. You
catch the regression the day it lands, not after it ships. Wire the same script
into a nightly cron and you also catch drift from the *world* changing — new
model versions, refreshed ground truth."

**📓 FIELD NOTE:** "Governance without evidence is opinion. 'Our AI scanner is
accurate' is a claim; a committed, dated benchmark trend line is *proof*. When an
auditor or a CISO asks 'how do you know?', you point at the graph, not a vibe."

---

## Panel 3 — Reality 1: cyber safeguards

**🖊️ DRAW:** A model box (orange) reading real CVE code (red). A shield icon
(red) blocks it: **"safeguard: looks like exploit dev."** Then a green re-frame
box: **"authorized defensive review of public patched code"** → passes.

```
   model + real CVE code ─▶ 🛡️ BLOCKED ("cyber safeguard")
        │ re-frame: authorized defensive review, public + patched
        ▼
   ✅ completes
```

**🎙️ SAY:** "A surprise you'll hit in practice: the model's own **safety
guardrails** can block *your legitimate* security work. In this repo, one model
refused to analyze real CVE code twice — the raw request looked like exploit
development. It only proceeded once the task was clearly framed as an
**authorized defensive review of already-public, already-patched code for a
benchmark**. Lesson: legitimate cyber work sometimes needs explicit authorization
framing, and providers run verification programs for teams that do this at scale.
Record the block honestly — it's a real property of the system, not a bug to hide."

---

## Panel 4 — Reality 2: the oracle isn't perfect

**🖊️ DRAW:** Two overlapping circles (Venn). Left blue **"Checkov knows."** Right
orange **"model finds."** Overlap = agreement. Right-only slice labeled green
**"maybe a REAL bug Checkov has no rule for."**

```
      Checkov          model
     ( knows )  ◯◯  ( finds )
                overlap = agree
        right-only slice → maybe real, oracle just has no rule
```

**🎙️ SAY:** "One humility panel. On IaC we scored models *against Checkov*. But
Checkov is an **oracle, not omniscience**. When a model flags something Checkov
didn't, we count it as a 'false positive' — but it might be a **real** issue
Checkov simply has no rule for. So 'accuracy vs Checkov' is a *lower bound* on
true skill. Always know what your ground truth can and can't see, and say so.
Over-claiming certainty is its own security risk."

---

## Panel 5 — The whole loop on one board

**🖊️ DRAW:** A closed cycle: **ground truth → blind run → conformance + accuracy
→ pick model → deploy behind gate → monitor → (new data) → back to ground truth.**

```
   ┌────────────────────────────────────────────────┐
   ▼                                                 │
  ground truth ─▶ blind run ─▶ conformance+accuracy ─▶ pick model
        ▲                                              │
        │                                              ▼
     new data ◀── monitor ◀── deploy behind EVAL GATE ─┘
```

**🎙️ SAY:** "Step back and see the whole loop you can now draw from memory. Build
**ground truth**. Run the harness **blind**. Check **conformance** *and*
**accuracy** — never confuse them. **Pick the model** by task from the evidence.
**Deploy behind the eval gate** with a regression threshold. **Monitor**, feed
new data back into ground truth, and go around again. That loop is what turns a
probabilistic AI security tool from a black box into something you can actually
*trust with your risk decisions*. That's the entire course."

---

## ✅ Recap
- The eval becomes an automated **CI/pipeline gate** — test the harness before trusting it.
- `--min-acc` gives **regression detection**: accuracy dip → failed build → alert.
- **Governance by evidence**: a committed benchmark trend line beats a claim.
- **Cyber safeguards** can block legitimate work; use authorized-defensive framing and record it honestly.
- Your **oracle has limits**; "accuracy vs Checkov" is a lower bound — state uncertainty.
- The full loop: ground truth → blind run → conformance+accuracy → pick model → gated deploy → monitor → repeat.

## 🧠 Check yourself
1. What single flag turns the benchmark into a CI gate, and how does it signal failure?
2. Why might a model refuse legitimate security analysis, and how did we resolve it?
3. A model flags an issue Checkov missed — is that automatically a false positive? Why not?

## 🛠️ Try it on the board's source
Make a regression fail on purpose: run `python bench/run_benchmark.py --findings
data/mantis_findings.sample.jsonl --gt-source secllmholmes-handcrafted --min-acc
0.99` and watch it exit non-zero. Then read the cron entrypoint
`scripts/run_vulnbench.sh` and `make schedule` — that's the gate in production.

---

### 🎓 Course wrap
You can now, at a lightboard, take someone from "what's a vulnerability?" to
"here's how we gate a probabilistic AI security harness into production with
evidence." Re-draw the Chapter 8 loop from memory — if you can narrate it end to
end, you've got it.
