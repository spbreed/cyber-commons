# Chapter 1 — Why AI Security, and Why We Must Evaluate

**Board time:** ~25 min · **Prereqs:** none · **Markers:** white, orange, red, blue

### Learning objectives
By the end you can, at the board, explain:
1. The two directions of "AI and security" — **AI for Security** vs **Security for AI**.
2. Why an AI security *tool* is itself a probabilistic system that can be wrong.
3. Why "it found a bug!" is not enough — you need **measured accuracy**.

---

## Panel 1 — The fork in the road

**🖊️ DRAW:** Center the board with the phrase **"AI + Security"** in white. Draw
two arrows splitting out. Left arrow → box **"AI *for* Security"** (orange).
Right arrow → box **"Security *for* AI"** (orange).

```
                 AI + Security
                 /            \
        AI for Security     Security for AI
        (AI finds bugs)     (protect the AI)
```

**🎙️ SAY:** "Whenever someone says 'AI and security,' they mean one of two very
different things. On the left — *AI for Security*: we point AI at our systems to
*find* problems. Think of an AI that reads code and reports vulnerabilities. On
the right — *Security for AI*: we protect the AI systems themselves — the models,
the data, the agents. This whole course lives at the intersection: we use an AI
tool to find bugs (left), and we treat that tool as something that must itself be
tested and trusted (right)."

**📓 FIELD NOTE:** "Teams that only think 'AI for Security' buy a shiny scanner
and trust its output. The mature teams also ask, 'how do we *know* this scanner
is right?' That question is the entire job here."

---

## Panel 2 — What a "cyber harness" is

**🖊️ DRAW:** An orange box labeled **"Cyber Harness (AI)"**. Feed it a white box
**"code / config"** on the left. Out the right, a red box **"findings"** listing
three bullet lines.

```
   code/config  →  [ Cyber Harness (AI) ]  →  findings:
                                                • bug in file X (CWE-89)
                                                • bug in file Y
                                                • bug in file Z
```

**🎙️ SAY:** "A cyber harness is an AI tool — often an LLM driving a set of steps —
that reads code or cloud config and produces *findings*: 'this file has this kind
of vulnerability.' Google's **Mantis** is exactly this. So are Big Sleep,
Aardvark, XBOW. They read, they reason, they report."

---

## Panel 3 — The catch: it's probabilistic

**🖊️ DRAW:** Under the findings box, mark each finding with a colored check.
Green ✓ next to one, red ✗ next to another, an orange **"?"** next to the third.
Write big underneath in red: **"some are wrong."**

```
   findings:
     • bug in X (CWE-89)   ✓ real
     • bug in Y            ✗ hallucinated
     • bug in Z            ? right bug, wrong reason
                    → SOME ARE WRONG
```

**🎙️ SAY:** "Here's the catch that makes AI security different from a normal
tool. A traditional scanner runs the same rule every time — deterministic. An AI
harness is **probabilistic**. Ask it twice, you might get two answers. Some
findings are real. Some are **hallucinated** — confidently described bugs that
don't exist. And some are 'right bug, wrong reason' — it flagged the correct file
but named the wrong weakness. You cannot tell which is which just by reading the
report — they all *look* equally confident."

**📓 FIELD NOTE:** "The scariest failure is the confident hallucination. A junior
engineer files it as a real bug; a senior wastes an afternoon; trust in the tool
erodes. Confidence is not correctness."

---

## Panel 4 — So we measure

**🖊️ DRAW:** Draw a blue box labeled **"Answer Key (ground truth)"**. Put the
findings box next to it and draw a two-headed arrow between them labeled
**"compare → SCORE"**. Under it write: **Accuracy = how often it's right.**

```
   [ findings ]  ⇄ compare ⇄  [ Answer Key (ground truth) ]
                     ↓
              SCORE / Accuracy
```

**🎙️ SAY:** "The only way to trust a probabilistic tool is to *measure* it. We
take code where we already know the right answers — a blue **answer key**, also
called *ground truth* — run the harness on it, and compare. That gives a number:
accuracy. 'This harness gets 9 out of 10 right' is a sentence you can make a
decision with. 'It found a bug once' is not. That measurement is what this whole
repository builds."

---

## Panel 5 — Where this sits in a security program

**🖊️ DRAW:** A horizontal pipeline of 3 white boxes: **"pick tool"** →
**"EVALUATE"** (circle this one in green) → **"deploy in pipeline"**. Put a red
"🚫" over an arrow that tries to skip from "pick tool" straight to "deploy."

```
   pick tool  →  [ EVALUATE ]  →  deploy in pipeline
        └────────🚫 skip? no ────────┘
```

**🎙️ SAY:** "In a real AI-security program there's a gate — the book calls it the
**Evaluation & Risk Gate** — between choosing an AI tool and letting it into your
pipeline. You do not let a probabilistic vulnerability finder touch production
decisions ungraded. Cyber Harness Eval *is* that gate. Everything in the next
seven chapters is how you build and run it."

---

## ✅ Recap
- **AI for Security** = AI finds bugs. **Security for AI** = protect the AI. We do both.
- A **cyber harness** (e.g. Mantis) reads code/config and emits findings.
- It is **probabilistic**: findings can be real, hallucinated, or right-bug-wrong-reason — and they all look confident.
- Trust requires **measurement against an answer key (ground truth)** → an accuracy number.
- Evaluation is a **gate** before deployment, not an afterthought.

## 🧠 Check yourself
1. Give one example each of "AI for Security" and "Security for AI."
2. Why can't you trust a harness finding just because it sounds confident?
3. What do you need, besides the harness, to produce an accuracy number?

## 🛠️ Try it on the board's source
Open [`../README.md`](../README.md) and find the "Summary of findings" table —
those 0.47–0.95 numbers are exactly the "how often it's right" measurement this
chapter argues for. We'll rebuild them from scratch by Chapter 7.
