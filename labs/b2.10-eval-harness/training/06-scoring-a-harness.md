# Chapter 6 — Scoring a Harness (the Sola Four-Stage Method)

**Board time:** ~30 min · **Prereqs:** Ch 1–5 · **Markers:** white, green, red, orange, blue

### Learning objectives
1. Walk the four stages: **ingest → match → expert score → judge.**
2. Compute an **expert-proxy score** ({0, 0.5, 1}) by hand for a few files.
3. Explain why we use **two LLM judges with MIN aggregation.**

---

## Panel 1 — The pipeline, end to end

**🖊️ DRAW:** Four white boxes left to right: **1 Ingest → 2 Match → 3 Expert
Score → 4 Judge.** Findings (red) enter box 1; answer key (blue) joins at box 2;
a number (green) exits box 4.

```
   findings ─▶ [1 Ingest] ─▶ [2 Match] ─▶ [3 Expert] ─▶ [4 Judge] ─▶ SCORE
                              ▲ answer key (blue)
```

**🎙️ SAY:** "Scoring has four stages. **Ingest**: read the harness's findings and
normalize each vuln_type into a CWE. **Match**: line each finding up to the
answer key using the parent+filename tail from last chapter. **Expert score**:
the hard 0/0.5/1 grade. **Judge**: softer quality metrics from LLM judges. Let's
do the two scoring stages by hand — this is where it clicks."

---

## Panel 2 — Expert-proxy: the {0, 0.5, 1} rule

**🖊️ DRAW:** A decision tree. Top split: **is the file vulnerable?** Left branch
(vulnerable, red): three leaves — **right CWE = 1.0**, **wrong CWE = 0.5**,
**missed = 0**. Right branch (safe, green): two leaves — **flagged = 0 (false
positive)**, **left alone = 1.0**.

```
                 file vulnerable?
                /                \
             YES (red)          NO / safe (green)
           /    |     \           /        \
   right CWE  wrong  missed   flagged     ignored
     = 1.0    = 0.5   = 0     = 0 (FP)    = 1.0
```

**🎙️ SAY:** "This is the **expert-proxy** score — how a human expert would grade
each answer-key row. If the file really is vulnerable: full point for the right
CWE, half for right-file-wrong-CWE, zero for missing it. If the file is safe:
zero if the harness *flagged* it — that's a false positive, and we punish it — and
full point for correctly leaving it alone. Add up all rows, divide by count →
**Expert Accuracy**. Let's grade four files together."

**🖊️ DRAW (add):** A worked mini-table:
```
   file        truth       harness said     score
   1.py        CWE-89      CWE-89           1.0
   2.c         CWE-476     CWE-22           0.5   (right file, wrong class)
   3.c         CWE-787     (nothing)        0.0   (missed)
   p_1.py      safe        CWE-89           0.0   (false positive)
                                    mean =  0.375
```

**🎙️ SAY:** "Four rows, scores 1.0, 0.5, 0.0, 0.0 → average 0.375. That single
number is comparable across harnesses and across models. Notice how the wrong-CWE
half-credit and the false-positive zero both matter — this rule rewards
*understanding*, not just noise."

---

## Panel 3 — Why judges, and why two

**🖊️ DRAW:** The finding (red) fed to **two orange judge boxes** ("Judge A",
"Judge B"). Each outputs metrics: **faithfulness, hallucination-free,
correctness…**. Combine with a **MIN** gate (draw a `∧` / "take the lower").

```
   finding ─┬─▶ [Judge A] ─▶ scores ─┐
            └─▶ [Judge B] ─▶ scores ─┴─ MIN ─▶ final
                                   (take the LOWER of the two)
```

**🎙️ SAY:** "The expert score checks 'right file, right class.' But we also want
softer qualities: is the *explanation* faithful to the code, is it free of
hallucination, does it actually use the evidence? Those are fuzzy, so we ask
**LLM judges** to rate them. Two judges, not one — and we take the **minimum** of
their scores. Why the minimum? Because we want to be *conservative*: a finding
only gets credit for a quality if **both** judges agree it's there. One skeptical
judge can veto. That's how you keep an eval from grading itself too kindly."

**📓 FIELD NOTE:** "Using an LLM to judge an LLM sounds circular, but with two
independent judges, a MIN gate, and a hard expert score alongside, it's a
reasonable triangulation. The failure mode to avoid is a *single* lenient judge —
that's a rubber stamp."

---

## Panel 4 — The output you read

**🖊️ DRAW:** A mock report card: **Expert Accuracy 0.90**, a small **by-CWE**
table with one low row circled red (**CWE-476 0.33**), and **judge metrics**.

```
   === report ===
   Expert Accuracy : 0.90
   by-CWE:
     CWE-89  1.00
     CWE-476 0.33   ◀ weak spot
   judge: faithfulness 0.94 …
```

**🎙️ SAY:** "The scorer prints a report card: one headline Expert Accuracy, a
**by-CWE breakdown** so you see *which class* the harness is bad at — here CWE-476
is the weak row — and the mean judge metrics. That by-CWE table is where you stop
saying 'the tool is 90% good' and start saying 'the tool is great except it can't
tell a NULL-pointer bug from path traversal.' That specificity is the whole payoff."

---

## ✅ Recap
- Four stages: **Ingest → Match → Expert score → Judge.**
- **Expert-proxy {0,0.5,1}:** vulnerable → 1 right-CWE / 0.5 wrong-CWE / 0 miss; safe → 0 if flagged / 1 if ignored.
- Mean of those = **Expert Accuracy**, comparable across harnesses and models.
- **Two LLM judges, MIN-aggregated** = conservative quality metrics; both must agree.
- The **by-CWE** breakdown tells you *where* a tool fails, not just how much.

## 🧠 Check yourself
1. A safe file the harness ignored — what score? A safe file it flagged?
2. Why take the **minimum** of the two judges rather than the average?
3. What does a low by-CWE row tell you that the headline accuracy doesn't?

## 🛠️ Try it on the board's source
Score the sample and read the exact report from this chapter:
`python bench/run_benchmark.py --findings data/mantis_findings.sample.jsonl
--gt-source secllmholmes-handcrafted`. The scoring rules are in `bench/score.py`
(`expert_score`, `judge`).
