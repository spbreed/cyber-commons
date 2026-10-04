# Track A0 — Set Up — Your Machine, How to Use This, and the Words for an Agent

**Function A · Getting Started — Building Agentic AI**  
*Build the system first. A working agentic platform — the loop, MCP tools, identity and delegation, memory, agent-to-agent messaging, a human gate, spans and an audit trail — and the harness that makes it operable. Each of the nine words for an agent — harness, memory and state, RAG, MCP, skills, guardrails, evals, A2A and multi-agent — is a component built here. Everything the other five functions attack, defend, detect and govern is built here, by you, before any of it is called a risk.*

**Job titles:** Anyone, in any of the five roles. This chapter assumes no security background. It does assume you can install software on the machine in front of you.

**What changes:** Two lessons. The first is the whole front door on one page: what the commons is and who it is for, the developer AI tools compared on context window and real cost, the clone, and the model endpoint every later lesson depends on, proven with one run — then how a lesson page is built, which function to open first, what Day 0/1/2 mean, the open-source-first rule, and the four frameworks. The second is the nine words for an agent — harness, memory and state, RAG, MCP, skills, guardrails, evals, A2A and multi-agent — drawn on one page and placed in CyberTravels. 2 lessons.

**Autonomy focus:** Read it once and run it once before opening a second lesson.

**Deliverable:** A machine that can run any lesson in the commons — a model endpoint configured and proven — a route through it chosen for your role, and the vocabulary Function A builds in.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### A0.0 — Set up your computer — what this is, who it is for, and the model every lesson runs on

- **Lab** — Set your computer up from nothing, run one skill and read back which model answered, then find your role's row and the lesson it starts at.
- **Tools** — `ollama`, `git`, `python3`

**Run it** — Set your computer up from nothing, run one skill and read back which model answered, then find your role's row and the lesson it starts at.

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

### A0.1 — Nine words for an agent — harness to multi-agent, and where each is built

- **Lab** — Find all nine in the finished CyberTravels tree (checkpoint A2.5) — a file for each — and count how many you placed.
- **Tools** — `MCP`, `A2A`, `Agent Skills`

**Run it** — Find all nine in the finished CyberTravels tree (checkpoint A2.5) — a file for each — and count how many you placed.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons A0.1

# --- 3 · in your agent, open this folder and pick the skill:
#         a0-1-nine-words-for-an-agent
#         (Claude Code and Copilot: /a0-1-nine-words-for-an-agent · Cursor: type / and
#         search · Codex: $a0-1-nine-words-for-an-agent). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py A0.1
```

---
