# Cyber Harness Eval — Lightboard Course

A hands-on course that teaches someone **new to cyber security *and* AI** how to
evaluate an AI-driven security tool, using this repo as the running example. It
is written as **lightboard scripts**: you (the instructor) stand behind a
lit glass board, draw sketches toward the camera with markers, and narrate.

Concepts are aligned with the *AI Security Engineering* reference book (Security
for AI, the threat landscape, cloud, and the pipeline **Evaluation & Risk Gate**)
but every idea is grounded in something you can actually run in this repo.

## Who this is for

- New engineers joining an AI-security or product-security team.
- Anyone who can read a little code but has **not** done vulnerability research
  or trained/operated LLMs.
- No prior cyber or ML background assumed — Chapters 2 and 3 build both.

## The chapters

| # | File | You will be able to… |
|---|------|----------------------|
| 1 | [01-why-ai-security.md](01-why-ai-security.md) | Explain *Security for AI* vs *AI for Security*, and why probabilistic tools must be evaluated |
| 2 | [02-cyber-fundamentals.md](02-cyber-fundamentals.md) | Define a vulnerability, CWE, vuln-vs-safe, and SAST / pentest / IaC |
| 3 | [03-ai-agents-and-harnesses.md](03-ai-agents-and-harnesses.md) | Explain LLMs, agents, coding agents, and what a "cyber harness" like Mantis is |
| 4 | [04-the-evaluation-problem.md](04-the-evaluation-problem.md) | Explain ground truth, blind testing, and **conformance vs accuracy** |
| 5 | [05-building-ground-truth.md](05-building-ground-truth.md) | Build an answer key from SecLLMHolmes + TerraGoat/Checkov, and the path-matcher trap |
| 6 | [06-scoring-a-harness.md](06-scoring-a-harness.md) | Score findings with the Sola four-stage method (expert proxy + LLM judges) |
| 7 | [07-model-comparison.md](07-model-comparison.md) | Run a blind model comparison and read failure themes / pick a model |
| 8 | [08-from-eval-to-pipeline.md](08-from-eval-to-pipeline.md) | Wire the eval in as a CI/pipeline gate, and handle cyber safeguards |

Work them in order; each ~20–35 min of board time.

## How to read a lightboard script

Every chapter is a sequence of **panels**. A panel = one board sketch plus its
narration:

- **🖊️ DRAW** — what to put on the glass (boxes, arrows, icons, labels). Keep it
  sparse; a lightboard sketch is a diagram, not a slide.
- **🎙️ SAY** — the words to speak while (and just after) you draw it.
- **📓 FIELD NOTE** — a short real-world aside to say to camera (the book calls
  these "Leadership Red Book" callouts).
- **✅ RECAP / 🧠 CHECK** — end-of-chapter summary and self-test questions.

### Board conventions (use consistently across all chapters)

| Marker color | Means |
|--------------|-------|
| **White** | neutral structure — boxes, systems, flow |
| **Green** | good / safe / correct / "patched" |
| **Red** | bad / vulnerable / wrong / attack |
| **Blue** | data, ground truth, evidence |
| **Orange** | the AI model / harness itself |

Practical lightboard tips: write **large**, 6–8 words per line max; box a concept
before you talk about it; use arrows for flow; erase between panels so the board
never crowds. (The camera mirrors your writing, so on-camera it reads normally —
just write naturally.)

## Runnable companion

Each chapter ends with a **"Try it on the board's source"** box pointing at the
exact repo command or file, so learners connect the sketch to real output —
e.g. `python work_mantis/compare_models.py`.
