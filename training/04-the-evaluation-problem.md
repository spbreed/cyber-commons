# Chapter 4 — The Evaluation Problem: Ground Truth, Blind Testing, and Conformance vs Accuracy

**Board time:** ~30 min · **Prereqs:** Ch 1–3 · **Markers:** blue, orange, red, green

### Learning objectives
1. Explain **ground truth** and why evaluation is impossible without it.
2. Explain **blind testing** and how label leakage fakes good scores.
3. Draw the single most important distinction in this course: **conformance vs accuracy.**

---

## Panel 1 — You can't grade without an answer key

**🖊️ DRAW:** A student's exam paper (white) and, beside it, a blue **"answer
key."** Arrow from key to paper labeled **"grade."** Then cross out the answer
key with red and put a **"?"** over the grade.

```
   exam  +  [ANSWER KEY]  →  grade: 8/10
   exam  +     ???        →  grade: ??  ← can't
```

**🎙️ SAY:** "Grading an exam only works because you hold the answer key. Same for
a security tool: to say 'it's 90% accurate,' you must already know the right
answers for the code you test it on. That labeled set — 'this file is vulnerable,
CWE-89; that file is safe' — is called **ground truth**. No ground truth, no
score, just vibes. Building ground truth is Chapter 5; today is *why* it matters
and the traps around it."

---

## Panel 2 — Blind testing (don't let it peek)

**🖊️ DRAW:** A folder of files with names like **`CWE-89/1.py`** (red — name
leaks the answer!). Arrow to a second folder where they're renamed
**`sample_017.py`** (white — opaque). Label the second **"BLIND."**

```
   CWE-89/1.py   ← name screams "SQL injection here"
        │  rename, hide labels
        ▼
   sample_017.py ← opaque   ✅ BLIND
```

**🎙️ SAY:** "Here's a trap. If the folder is literally named `CWE-89`, a smart
model can *read the answer off the path* without understanding the code — and
you'd record a fake-high score. So we test **blind**: copy every file to an
opaque name like `sample_017.py`, put the real labels in a sealed answer key the
model never sees, and only reveal them when scoring. That's the difference
between an honest number and a demo. In this repo the blind run scored **0.90**;
a hand-authored demo scored **0.95** — the honest one is lower, and that's the
point."

**📓 FIELD NOTE:** "If a vendor's benchmark number seems too clean, ask: 'was the
model blind to the labels?' Data leakage is the oldest way to inflate an eval,
and it usually isn't even on purpose."

---

## Panel 3 — The BIG distinction: conformance vs accuracy

**🖊️ DRAW:** Split the board with a vertical line. Left header **"CONFORMANCE"**
(blue). Right header **"ACCURACY"** (green). Fill two rows.

```
   CONFORMANCE                 |   ACCURACY
   "is it VALID output?"       |   "is it CORRECT?"
   JSON shape vs schema        |   vuln/safe + CWE vs truth
   ~100%  (by construction)    |   0.47 – 0.95  (the real skill)
   plumbing                    |   the score that matters
```

**🎙️ SAY:** "This is the slide to tattoo on your brain. There are **two**
different checks and people constantly confuse them. **Conformance**, on the
left, asks: *is the finding valid Mantis output?* — does the JSON have the right
fields. It's almost always **100%**, because we *build* the output to fit the
schema. It says **nothing** about whether the bug is real. **Accuracy**, on the
right, asks: *is the finding correct?* — did it match the answer key. That's the
0.47-to-0.95 number, the actual skill. A finding that says 'SQL injection in a
totally safe file' is **100% conformant and 0% accurate** — perfectly formatted,
completely wrong."

**🖊️ DRAW (add):** In the corner, write the killer example in red:
**`{well-formed} + {wrong bug} = conforms ✔  accurate ✘`**

---

## Panel 4 — Why conformance is still worth checking

**🖊️ DRAW:** A timeline: **`0/24 → 23/24 → 24/24`** with a red note at the first
step: **"missing `history` field."**

```
   conformance history:
     0/24   ← forgot the required `history` array
     23/24  ← one line had mitigation_diff = null
     24/24  ← fixed
```

**🎙️ SAY:** "So if conformance is usually 100%, why check it at all? Because when
it *isn't* 100%, your pipeline silently breaks — a downstream step can't parse
the finding. In this repo the first sample scored **0 out of 24** conformant
because we forgot a field the real Google schema requires. Conformance caught a
plumbing bug before it could cause a mystery failure. So: check conformance to
keep the pipes connected; quote **accuracy** to judge the tool."

**📓 FIELD NOTE:** "Two dashboards, never one. A green 'schema valid' light next
to a separate 'accuracy 0.61' number. The day someone reports 'conformance 100%'
as if it were quality, stop the meeting and draw this panel."

---

## ✅ Recap
- **Ground truth** = the labeled answer key; without it there is no score.
- **Blind testing** = opaque names + hidden labels, so the model can't read the answer off the path. Honest > flattering.
- **Conformance** (valid output, ~100%, structural) ≠ **Accuracy** (correct output, the real skill).
- A perfectly formatted finding can be completely wrong — that's why you never quote conformance as quality.
- Check conformance to keep the pipeline unbroken; check accuracy to judge the harness.

## 🧠 Check yourself
1. Why does renaming `CWE-89/1.py` to `sample_017.py` matter?
2. A tool reports "100% schema-conformant." What have you learned about its bug-finding skill? (Trick question.)
3. Give an example of a finding that conforms but is inaccurate.

## 🛠️ Try it on the board's source
See both ideas live: the blind answer key is `work_mantis/.labels.secret.json`;
the conformance-vs-accuracy split is in [`../README.md`](../README.md) under
"Conformance vs Accuracy." Run `python work_mantis/compare_models.py` and note it
reports *accuracy*, not conformance.
