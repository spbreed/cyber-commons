# Chapter 2 — Cyber Fundamentals (for the complete newcomer)

**Board time:** ~30 min · **Prereqs:** Ch 1 · **Markers:** white, red, green, blue

### Learning objectives
1. Define a **vulnerability** and why the same file can be "vulnerable" or "safe."
2. Read a **CWE** and know why the *class* of bug matters, not just "is it buggy."
3. Tell apart the three review surfaces this repo covers: **SAST**, **pentest**, **IaC**.

---

## Panel 1 — What is a vulnerability?

**🖊️ DRAW:** A white box **"program"**. An attacker stick-figure (red) sends an
arrow **"evil input"** into it. The program does something it shouldn't (red
starburst) labeled **"unintended behavior."**

```
   attacker ──"../../etc/passwd"──▶ [ program ] ──▶ 💥 reads a file it shouldn't
```

**🎙️ SAY:** "A vulnerability is a flaw that lets someone make a system do
something it was never meant to do — read a file they shouldn't, run a command,
crash it, leak data. The key word is **untrusted input**: data from the outside
world that the program handles carelessly. Most bugs we'll see are 'the program
trusted input it should have checked.'"

---

## Panel 2 — Vulnerable vs. Safe (the twin files)

**🖊️ DRAW:** Two boxes side by side. Left, red, **"1.c — no check"**. Right,
green, **"p_1.c — adds check"**. Same shape, one small difference highlighted.

```
   VULNERABLE (red)              SAFE / patched (green)
   fopen(user_path)             realpath + verify inside dir
   → traversal                  → blocked
```

**🎙️ SAY:** "Here's a subtlety that trips people up. The *same* piece of code can
be vulnerable or safe depending on one check. In our datasets, a file named
`1.c` is the **vulnerable** version and `p_1.c` is its **patched twin** — nearly
identical, but the patched one adds the missing guard. Learning to spot that one
difference *is* vulnerability review. And notice: a good tool must not only find
the red one — it must **leave the green one alone**. Flagging a safe file is a
**false positive**, and false positives are how tools lose their users' trust."

**📓 FIELD NOTE:** "Vendors love to show recall — 'we caught the bug!' Ask them
about the patched twin. A tool that screams at safe code is worse than useless;
it trains your team to ignore it."

---

## Panel 3 — CWE: naming the *kind* of bug

**🖊️ DRAW:** A blue box **"CWE = Common Weakness Enumeration"**. Around it, five
small red tags: **CWE-89 SQL injection**, **CWE-79 XSS**, **CWE-22 path
traversal**, **CWE-787 out-of-bounds write**, **CWE-476 NULL deref**.

```
              ┌─ CWE-89  SQL injection
   CWE  ──────┼─ CWE-79  cross-site scripting
   (bug class)├─ CWE-22  path traversal
              ├─ CWE-787 out-of-bounds write
              └─ CWE-476 NULL-pointer deref
```

**🎙️ SAY:** "Security people don't just say 'it's buggy' — they name the *class*
of weakness using a **CWE** number, from the Common Weakness Enumeration. CWE-89
is SQL injection, CWE-22 is path traversal, and so on. Why does the class matter?
Because the *fix* depends on it, and because a tool that says 'vulnerable' but
names the wrong CWE only half-understands the bug. Later we'll score exactly
that: right file + right CWE = full credit; right file + wrong CWE = half credit."

**🖊️ DRAW (add):** Off to the side, a tiny scoring key in white:
**`right CWE = 1.0 · wrong CWE = 0.5 · missed = 0 · flag a safe file = 0`.**

---

## Panel 4 — Three surfaces: SAST, Pentest, IaC

**🖊️ DRAW:** Three columns. Column 1 white header **SAST** with a code icon.
Column 2 **Pentest** with a running-system icon. Column 3 **IaC** with a
cloud/config icon. One line each under.

```
   SAST                 PENTEST                IaC
   read the code        attack the running     read the cloud
   (static)             system (dynamic)       config (Terraform)
   e.g. "SQLi in 3.py"  e.g. "I got admin"     e.g. "S3 bucket public"
```

**🎙️ SAY:** "There are three places you look for security problems, and this repo
touches all three. **SAST** — Static Application Security Testing — reads the
source code *without running it*, like proofreading. **Pentest** — penetration
testing — actually *attacks* the running system to prove a path in. **IaC** —
Infrastructure as Code — reviews the *configuration* of your cloud, like a
Terraform file that accidentally makes a storage bucket public. Same goal —
find risk before an attacker does — but very different material."

**📓 FIELD NOTE:** "A finding in code (SAST) is a *possible* bug. A finding in a
pentest is a *proven* one. That's why serious harnesses like Mantis add a
'reproduce' step — they try to turn a maybe into a yes."

---

## Panel 5 — Why an oracle helps (Checkov)

**🖊️ DRAW:** For the IaC column, add a blue box **"Checkov (rule scanner)"**
pointing at a Terraform file, emitting a red list **"failed checks."** Label it
**"the oracle."**

```
   terraform.tf ──▶ [ Checkov ] ──▶ ✗ no encryption
                     (271 rules)     ✗ public access
                                     ✗ no logging
```

**🎙️ SAY:** "For cloud config we have a shortcut for building the answer key: a
deterministic scanner called **Checkov** with hundreds of rules. It reliably
lists what's misconfigured in a Terraform file. We'll treat Checkov as an
**oracle** — a trusted source of truth — and later ask, 'can an AI model
reproduce what Checkov knows?' Hold that thought; it's Chapter 7."

---

## ✅ Recap
- A **vulnerability** = untrusted input making a system misbehave.
- The **same file** can be vulnerable (`1.c`) or safe (`p_1.c`); flagging the safe one is a **false positive**.
- A **CWE** names the *class* of weakness; getting the class right matters for scoring and fixing.
- Three surfaces: **SAST** (read code), **Pentest** (attack running system), **IaC** (review cloud config).
- **Checkov** is a rule-based **oracle** we'll use to build IaC ground truth.

## 🧠 Check yourself
1. What makes `1.c` "vulnerable" but `p_1.c` "safe"?
2. Why is naming the CWE (not just "buggy") important?
3. Match: *"S3 bucket is public"*, *"SQL injection in login.py"*, *"I escalated to admin"* → SAST / Pentest / IaC.

## 🛠️ Try it on the board's source
Look at two real twins in the repo:
`ground-truth/secllmholmes/datasets/hand-crafted/dataset/CWE-89/1.py` (vulnerable)
vs `.../CWE-89/p_1.py` (safe). Spot the one-line difference — that's the whole game.
