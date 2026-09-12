# Track A0 — Introduction — What This Is, Who It Is For, and How to Use It

**Function A · Securing AI Architectures**  
*CyberTravels as built, every risk that architecture carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Anyone, in any of the five roles. This chapter assumes no security background and no setup.

**What changes:** One lesson. Who the commons is for, how a lesson page is built, which function to open first, what Day 0/1/2 mean, how to use the labs and skills, the open-source-first rule, the four frameworks, and how to run a lesson on either free route — demonstrated by running a real lesson's procedure three times, twice in the ways it breaks. 1 lesson.

**Autonomy focus:** Read it once and run it once before opening a second lesson.

**Deliverable:** A route through the commons chosen for your role, and one lesson executed on a host you did not configure with its output checksum matching the one recorded here.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A0.1 — Start here — what this is, who it is for, and how to run it

- **Risk** — A reader lands mid-curriculum, reads the hook as a summary, finds it vague and leaves — or opens the first code cell, finds twenty lines of subprocess and no procedure, and concludes the lessons are stubs.
- **Control** — One page that says what the commons is for, which track your job maps to, and what the code cell is doing — then a preflight that reproduces both ways the arrangement fails before reporting the host ready.
- **Lab** — Run the preflight on both routes and compare the output checksum.

**Run it** — Run the preflight on both routes and compare the output checksum.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A0.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A0.1   # run it headless and check it

# --- route one, from nothing: clone once and nothing is fetched afterwards ---
git clone https://github.com/spbreed/cyber-commons && cd cyber-commons
PYTHONPATH=skills/_runtime python3 \
  skills/programme/lesson-preflight/scripts/lesson_preflight.py

# --- route two: press 'Run on Kaggle' on the lesson page, then switch
#     Internet on in the settings panel (Kaggle needs a verified phone). ---
```

*Expect:* The tree inventoried from disk — 14 areas, 120 skills, 119 with a script at the time of writing, and the count moves as the commons grows — then the same procedure run three times: exit 2 with [Errno 2] when nothing was fetched, exit 1 with ModuleNotFoundError when the shared runtime is off the import path, and exit 0 with twelve lines and a CRC when both conditions hold. The CRC is the same on both routes, because it is the same file.

---
