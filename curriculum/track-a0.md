# Track A0 — Set Up — Your Development Environment, and How to Use This

**Function A · Getting Started — Building Agentic AI**  
*Build the system first. A working agentic platform — the loop, MCP tools, identity and delegation, memory, agent-to-agent messaging, a human gate, spans and an audit trail — and the harness that makes it operable. Everything the other four functions attack, defend, detect and govern is built here, by you, before any of it is called a risk.*

**Job titles:** Anyone, in any of the five roles. This chapter assumes no security background. It does assume you can install software on the machine in front of you.

**What changes:** Two lessons. First the setup — the developer AI tools compared on context window and real cost, the clone, and the model endpoint every later lesson depends on. Then who the commons is for, how a lesson page is built, which function to open first, what Day 0/1/2 mean, how to use the labs and skills, the open-source-first rule, and the four frameworks. 2 lessons.

**Autonomy focus:** Read it once and run it once before opening a second lesson.

**Deliverable:** A machine that can run any lesson in the commons — a model endpoint configured and proven — and a route through it chosen for your role.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### A0.0 — Set up your computer — the AI tools, and the model every lesson runs on

- **Lab** — Set your computer up from nothing, then run one skill and read back which model answered.
- **Tools** — `ollama`, `git`, `python3`

**Run it** — Set your computer up from nothing, then run one skill and read back which model answered.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A0.0

# --- 3 · in your agent, open this folder and pick the skill:
#         a0-0-set-up-your-computer
#         (Claude Code and Copilot: /a0-0-set-up-your-computer · Cursor: type / and
#         search · Codex: $a0-0-set-up-your-computer). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A0.0
```

---

### A0.1 — Start here — what this is, who it is for, and how to run it

- **Lab** — Do this lesson by picking its skill in your agent, then run it by hand and compare the two readbacks.

**Run it** — Do this lesson by picking its skill in your agent, then run it by hand and compare the two readbacks.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A0.1

# --- 3 · in your agent, open this folder and pick the skill:
#         a0-1-start-here
#         (Claude Code and Copilot: /a0-1-start-here · Cursor: type / and
#         search · Codex: $a0-1-start-here). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A0.1
```

---
