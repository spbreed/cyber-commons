# Track A0 — Set Up — Your Development Environment, and How to Use This

**Function A · Getting Started — Building Agentic AI**  
*Build the system first. A working agentic platform — the loop, MCP tools, identity and delegation, memory, agent-to-agent messaging, a human gate, spans and an audit trail — and the harness that makes it operable. Everything the other four functions attack, defend, detect and govern is built here, by you, before any of it is called a risk.*

**Job titles:** Anyone, in any of the five roles. This chapter assumes no security background. It does assume you can install software on the machine in front of you.

**What changes:** Two lessons. First the setup — the developer AI tools compared on context window and real cost, the clone, and the model endpoint every later lesson depends on. Then who the commons is for, how a lesson page is built, which function to open first, what Day 0/1/2 mean, how to use the labs and skills, the open-source-first rule, and the four frameworks. 2 lessons.

**Autonomy focus:** Read it once and run it once before opening a second lesson.

**Deliverable:** A machine that can run any lesson in the commons — a model endpoint configured and proven — and a route through it chosen for your role.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### A0.0 — Dev environment and IDE setup — the AI tools, and the model every lesson runs on

- **Risk** — A reader arrives, clones the repository, runs a lesson and gets an error they read as a broken repository rather than as an unconfigured machine — and leaves. Nothing in the commons executes without a model endpoint, and that is the first thing anybody hits.
- **Control** — One setup lesson that ends in a verified model call: the tool chosen against its real context window and cost, the clone from master, the three environment variables, and a skill run whose output names the model that produced it.
- **Lab** — Configure a model endpoint, then run one skill and read back which model answered.
- **Tools** — `ollama`, `git`, `python3`

**Run it** — Configure a model endpoint, then run one skill and read back which model answered.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of A0.0:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at A0.0 --out work/cybertravels
python3 scripts/checkpoint.py --at A0.0 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/programme/dev-environment-preflight/scripts/dev_environment_preflight.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* The runtime resolving from skills/_runtime, your endpoint and model named, and the key reported as present rather than printed. Then exit code 2 from a deliberate unconfigured run, so you meet that refusal here rather than on lesson forty. Then one real model call: which model answered, how many contract violations were in its reply, and the filled-in contract as JSON.

---

### A0.1 — Start here — what this is, who it is for, and how to run it

- **Risk** — A reader lands mid-curriculum, reads the hook as a summary, finds it vague and leaves — or opens the first code cell, finds twenty lines of subprocess and no procedure, and concludes the lessons are stubs.
- **Control** — One page that says what the commons is for, which track your job maps to, and what the code cell is doing — then a preflight that reproduces both ways the arrangement fails before reporting the host ready.
- **Lab** — Run the preflight on both routes and compare the output checksum.

**Run it** — Run the preflight on both routes and compare the output checksum.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · your copy of CyberTravels as it stood at the END of A0.1:
#         everything taught so far, nothing taught after it. Named
#         cybertravels/ so it imports. ---
mkdir -p work && python3 scripts/checkpoint.py --at A0.1 --out work/cybertravels
python3 scripts/checkpoint.py --at A0.1 --diff      # what this lesson changed

# --- 3 · a model. A signed-in Claude Code CLI needs no API key: ---
claude --version        # prints a version? nothing else to configure

# --- 4 · run the skill against its committed fixture ---
python3 skills/programme/dev-environment-preflight/scripts/dev_environment_preflight.py

# --- or install it into your own agent and ask in your own words ---
python3 scripts/install_skills.py --all
```

*Expect:* The tree inventoried from disk — 14 areas, 139 skills, 139 with a script — then the same procedure run three times: exit 2 with [Errno 2] when nothing was fetched, exit 1 with ModuleNotFoundError when the shared runtime is off the import path, and exit 0 with twelve lines and a CRC when both conditions hold. The CRC is the same on both routes, because it is the same file.

---
