# Chapter 3 — AI, Agents, and Cyber Harnesses

**Board time:** ~30 min · **Prereqs:** Ch 1–2 · **Markers:** orange, white, blue, green

### Learning objectives
1. Explain in one breath what an **LLM** is and why it's non-deterministic.
2. Explain the ladder: **model → agent → coding agent → cyber harness**.
3. Describe the **Mantis** pipeline and the two shapes of finding it emits.

---

## Panel 1 — What an LLM is (just enough)

**🖊️ DRAW:** An orange box **"LLM"**. Left arrow in: **"prompt (text)"**. Right
arrow out: **"next words, by probability"**. Under it, a tiny bar chart of word
probabilities.

```
   "The capital of France is ___"  ─▶  [ LLM ]  ─▶  Paris (92%)
                                                     Lyon  (3%)
                                                     ...
```

**🎙️ SAY:** "A Large Language Model is, at heart, a very good *next-word guesser*
trained on huge amounts of text. You give it a prompt, it predicts likely
continuations. That's it — but at scale it can read code, reason, and write. The
crucial property for us: it works in **probabilities**, so the same question can
produce different answers. That's the non-determinism we met in Chapter 1, and
it's *why* we have to measure these tools instead of trusting them."

---

## Panel 2 — The ladder to a harness

**🖊️ DRAW:** A vertical ladder of four orange boxes, each building on the last:
**Model → Agent → Coding Agent → Cyber Harness.** Short label on each rung.

```
   ┌─────────────────────────────┐
   │ 4. Cyber Harness            │  runs a security *process*
   ├─────────────────────────────┤
   │ 3. Coding Agent             │  + reads/edits files, runs tools
   ├─────────────────────────────┤
   │ 2. Agent                    │  + can take actions in a loop
   ├─────────────────────────────┤
   │ 1. Model (LLM)              │  predicts text
   └─────────────────────────────┘
```

**🎙️ SAY:** "Build up one rung at a time. Rung 1, a **model** just emits text.
Rung 2, wrap it in a loop that lets it *take actions* and see results — now it's
an **agent**. Rung 3, give that agent tools to read files, run commands, edit
code — a **coding agent** (Claude Code, Gemini CLI). Rung 4, point a coding agent
at a *security* process — 'find vulnerabilities, verify them, suggest patches' —
and you have a **cyber harness**. Mantis lives on rung 4. Notice the model at the
bottom is the engine: swap Opus for Haiku and the whole harness behaves
differently. Remember that — it's the punchline of Chapter 7."

**📓 FIELD NOTE:** "People argue about 'is it an agent?' The useful question is
'how much can it *do* on its own, and what happens if it's wrong?' Higher rungs =
more capability *and* more blast radius. Evaluation matters more the higher you climb."

---

## Panel 3 — Mantis: a harness is a pipeline of steps

**🖊️ DRAW:** A left-to-right chain of white boxes (Mantis stages):
**history → threat-model → research → critic → reproduce → patch → report.**
Circle **research** and **critic** in orange.

```
   history → threat-model → RESEARCH → CRITIC → reproduce → patch → report
                              ↑ finds        ↑ filters
                              bugs           false positives
```

**🎙️ SAY:** "Google's Mantis isn't one prompt — it's a *pipeline of skills*, each
a step a coding agent runs. **history** learns from past fixes. **research** is
the auditor that reads code and proposes findings. **critic** and **reproduce**
try to shoot those findings down and confirm the real ones. **patch** proposes a
fix; **report** writes it up. The step we benchmark most in this repo is
**research** — the core 'read the code, find the bug' judgment — because that's
where the model's skill shows up most directly."

---

## Panel 4 — What a finding looks like (the contract)

**🖊️ DRAW:** A blue box titled **"finding (JSON)"** with field lines:
`title, description, code_paths:["file:line"], vuln_type/cwe, status, mitigation`.

```
   {
     title:       "SQL injection in login"
     code_paths:  ["auth/login.py:42"]
     cwe:         "CWE-89"
     status:      VALID | FALSE_POSITIVE | DUPLICATE
     mitigation:  "use parameterized query"
   }
```

**🎙️ SAY:** "Every Mantis finding is structured data — a JSON object with fixed
fields: what file and line, which CWE, a status like VALID or FALSE_POSITIVE, a
suggested fix. This **contract** is gold for us: because the shape is fixed, we
can (a) check that a harness emits *valid* output — that's **conformance**, next
chapter — and (b) automatically compare `code_paths` and `cwe` to our answer key
— that's **accuracy**. Structure is what makes automatic scoring possible."

**📓 FIELD NOTE:** "When you adopt any AI security tool, first ask: 'what's your
output schema?' No stable schema means no automated evaluation, no CI gate, no
trend line. Structure is a security feature."

---

## ✅ Recap
- An **LLM** predicts likely text; it is **probabilistic**, hence must be measured.
- The ladder: **Model → Agent → Coding Agent → Cyber Harness**; the model is the swappable engine.
- **Mantis** is a *pipeline* (history→…→report); we benchmark the **research** stage most.
- Findings are **structured JSON** — a contract that enables both conformance and accuracy checks.

## 🧠 Check yourself
1. Why does the same LLM give different answers to the same prompt?
2. What turns a plain "agent" into a "cyber harness"?
3. Name two finding fields we compare against the answer key.

## 🛠️ Try it on the board's source
Read the real Mantis contract we vendored: `bench/mantis_schema.json` (and
`bench/MANTIS_SCHEMA_PROVENANCE.md`). Find the `finding` and `learning_entry`
definitions — those are the JSON shapes from this chapter.
