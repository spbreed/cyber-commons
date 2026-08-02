# Chapter 5 — Building the Answer Key (Ground Truth)

**Board time:** ~30 min · **Prereqs:** Ch 1–4 · **Markers:** blue, white, red, green

### Learning objectives
1. Name the two ground-truth sources and what each provides.
2. Explain the **Checkov-as-oracle** trick for cloud config.
3. Understand the **path-matcher trap** — the subtle bug that silently breaks scoring.

---

## Panel 1 — Two sources of truth

**🖊️ DRAW:** Two blue cylinders (databases). Left: **"SecLLMHolmes — labeled
code."** Right: **"TerraGoat — cloud config."** Both flow into one white box
**"vulnbench.db (552 rows)."**

```
   [ SecLLMHolmes ]  ─┐
    labeled code       ├─▶  [ vulnbench.db ]  552 rows
   [ TerraGoat.tf ]  ─┘         the answer key
```

**🎙️ SAY:** "Our answer key is built from two open-source projects that are
vulnerable *on purpose*. **SecLLMHolmes** gives us labeled code — hand-crafted
files with known CWEs, plus real historical CVEs. **TerraGoat** gives us
deliberately-misconfigured cloud Terraform. We load both into one SQLite
database, `vulnbench.db`, about 552 labeled rows. That database is the blue
'answer key' from Chapter 4, made concrete."

---

## Panel 2 — SecLLMHolmes: vulnerable + patched twins

**🖊️ DRAW:** A CWE folder tree. Under **CWE-89**: red **`1.py 2.py 3.py`**
(vulnerable) and green **`p_1.py p_2.py p_3.py`** (safe). Beside it a blue tag
**"+ rationale text."**

```
   CWE-89/
     1.py 2.py 3.py     (red   → vulnerable, CWE-89)
     p_1.py p_2.py p_3  (green → safe / patched)
     + ground-truth/… rationale for each
```

**🎙️ SAY:** "Inside SecLLMHolmes, each CWE has vulnerable files (`1.py`) and their
patched twins (`p_1.py`) — exactly the vuln/safe pairs from Chapter 2 — and an
expert-written rationale explaining each. So every file becomes one row in our
answer key: *path, vulnerable?, which CWE*. The real CVE set works the same way
with `vuln.c` / `patch.c` pairs from actual disclosed bugs."

---

## Panel 3 — TerraGoat + Checkov: the oracle trick

**🖊️ DRAW:** A red Terraform file → orange... no, blue box **"Checkov (271
rules)"** → a red list of **"failed checks."** Each failed check becomes a blue
row: **"file X → misconfig category."**

```
   terraform/*.tf ─▶ [ Checkov ] ─▶ ✗ CKV_AWS_18 no logging
                                     ✗ CKV_AWS_16 no encryption
                                        ↓ each = one ground-truth row
```

**🎙️ SAY:** "For cloud config we don't hand-label — we let a trusted rule scanner
do it. **Checkov** runs 271 rules over TerraGoat and lists every failed check.
We treat each failed check as a labeled 'this file has this misconfiguration' row.
This is the **oracle** pattern: use a deterministic tool you trust to *manufacture*
ground truth at scale. 474 rows appear almost for free. The catch — Checkov is a
great oracle but not perfect — we'll respect in Chapter 7."

**📓 FIELD NOTE:** "The oracle pattern is a superpower for evals: wherever a
reliable deterministic checker exists, you can bootstrap ground truth without
armies of human labelers. Just never forget the oracle has its own blind spots."

---

## Panel 4 — The path-matcher trap (the invariant)

**🖊️ DRAW:** Two different files that share a **basename**: `CWE-89/1.py` (red)
and `CWE-22/1.py` (red). An arrow from a finding "bug in `1.py`" pointing
ambiguously at both, with a red **"COLLISION!"** Then draw the fix: match on
**`CWE-89/1.py`** (parent + name), green ✔.

```
   finding: "bug in 1.py"
              ├─?─▶ CWE-89/1.py
              └─?─▶ CWE-22/1.py     ✗ basename collision → mis-scored
   FIX: match on  parent/name = "CWE-89/1.py"   ✅ unique
```

**🎙️ SAY:** "Now the subtle bug that ruins evaluations — and the single most
important invariant in this repo. To score a finding we must match its file to
the answer key. The naïve way is to match on the **basename**, `1.py`. But
SecLLMHolmes *reuses* `1.py` across many CWE folders! Match on basename and you
match the wrong file — you might grade a SQL-injection finding against a
path-traversal answer, and your whole scoreboard is quietly garbage. The fix:
match on the **parent directory plus filename** — `CWE-89/1.py` — and only when
that tail is *unique*. Exact path first, unique tail second, **never bare
basename**. We even keep a regression test so nobody re-introduces the basename
bug."

**📓 FIELD NOTE:** "This is the kind of bug that makes a benchmark *confidently
wrong* — every number looks fine, all of them are lies. When you inherit an eval,
the first thing to audit is how it matches findings to truth."

---

## Panel 5 — What one row looks like

**🖊️ DRAW:** A blue table with columns **`source | file_path | is_vulnerable |
cwe | rationale`** and one filled example row.

```
   source                 | file_path        | vuln | cwe     | rationale
   secllmholmes-handcrafted| CWE-89/1.py      |  1   | CWE-89  | "unsanitized % format …"
```

**🎙️ SAY:** "Put it together and every row of the answer key is just this: where
the code is, whether it's vulnerable, which CWE, and why. 552 of these and you can
grade any harness that tells you 'file + CWE.' That's the foundation the scorer
stands on — next chapter."

---

## ✅ Recap
- Ground truth comes from **SecLLMHolmes** (labeled code + CVEs) and **TerraGoat** (cloud config).
- SecLLMHolmes gives **vuln/patched twins** with CWEs and rationale.
- **Checkov** is an **oracle**: its failed checks manufacture 474 IaC rows for free.
- The **path-matcher invariant**: match on **parent+filename tail**, never bare basename — or scoring silently breaks.
- Each row = `file_path, is_vulnerable, cwe, rationale`.

## 🧠 Check yourself
1. What's the difference between how we label SecLLMHolmes vs TerraGoat rows?
2. Why is matching on bare basename dangerous here?
3. What does it mean to use a tool "as an oracle"?

## 🛠️ Try it on the board's source
Build the answer key yourself: `python ingest/build_datasource.py` (expect ~552
rows). The path-matcher lives in `bench/score.py` (`path_tail`, `Matcher`), and
`make verify` is the regression test that guards it.
