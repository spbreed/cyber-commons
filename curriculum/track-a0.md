# Track A0 — Introduction — What This Is, Who It Is For, and How to Use It

**Function A · Securing AI Architectures**  
*CyberTravels as built, every risk that architecture carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Anyone, in any of the five roles. This chapter assumes no security background and no setup.

**What changes:** Five lessons. Who the commons is for and how a lesson page is built; which function to open first given your job; what Day 0/1/2 mean and how to use the labs, the skills and the CyberTravels case study; how to run a lesson on either free route; and the four frameworks with a reference table for each. 5 lessons.

**Autonomy focus:** Read A0.1 to A0.3, run A0.4 once, and come back to A0.5 when a label on a lesson page needs resolving.

**Deliverable:** A route through the commons chosen for your role, and one lesson executed on a host you did not configure with its output checksum matching the one recorded here.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A0.1 — What this is, who it is for, and what a lesson is made of

- **Risk** — A reader lands mid-curriculum, reads the hook as if it were a summary, finds it vague and leaves. The material was never the problem; the shape of the page was.
- **Control** — One fixed page structure, named: the hook is a scene, the description sits under it, and the framework comes before any code on every lesson without exception.
- **Lab** — No code. Open a lesson in a function that is not yours and find all seven sections on it.

---

### A0.2 — How to use this, by the chair you sit in

- **Risk** — Read front to back, the curriculum puts three weeks of architecture in front of a detection engineer who needed an alert, and four functions in front of a risk owner who needed one report.
- **Control** — An entry point per role, with the dependencies named — so a route skips everything it does not need and nothing it does.
- **Lab** — No code. Pick your row, open the lesson it starts at, and read only its Day 0 line.

---

### A0.3 — Day 0, Day 1, Day 2 — the labs, the skills, and open source first

- **Risk** — A control with no number cannot be defended in a budget conversation, and a product nobody has built a bad version of cannot be specified — only compared on the seller's feature list.
- **Control** — Three questions answered on every page, a runnable procedure behind every lesson, and an open-source reference for every control so the gap you hit is the buying requirement.
- **Lab** — No code. Take the Day 2 line of a lesson in your function and write the same sentence about a control you already run.

---

### A0.4 — Run your first lesson — GitHub, Kaggle, and what you need first

- **Risk** — A reader opens the first code cell, finds twenty lines of subprocess and no procedure, and concludes the lessons are stubs — or runs one on a hosted kernel with no network and reports a broken lesson when the fetch is what failed.
- **Control** — A preflight that inventories the tree from disk and reproduces both failure conditions before reporting the host ready.
- **Lab** — Run the preflight on both routes and compare the output checksum.

**Run it** — Run the preflight on both routes and compare the output checksum.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A0.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A0.4   # run it headless and check it

# --- route one, from nothing: clone once and nothing is fetched afterwards ---
git clone https://github.com/spbreed/cyber-commons && cd cyber-commons
PYTHONPATH=skills/_runtime python3 \
  skills/programme/lesson-preflight/scripts/lesson_preflight.py

# --- route two: press 'Run on Kaggle' on the lesson page, then switch
#     Internet on in the settings panel (Kaggle needs a verified phone). ---
```

*Expect:* The tree inventoried from disk — 14 areas, 120 skills, 119 with a script at the time of writing, and the count moves as the commons grows — then the same procedure run three times: exit 2 with [Errno 2] when nothing was fetched, exit 1 with ModuleNotFoundError when the shared runtime is off the import path, and exit 0 with twelve lines and a CRC when both conditions hold. The CRC is the same on both routes, because it is the same file.

---

### A0.5 — The four frameworks, and when each one is the right lens

- **Risk** — Four vocabularies get used interchangeably, so a threat id lands in a risk register and a NIST function lands in an incident write-up, and neither audience can act on it.
- **Control** — One lookup, both directions, read from the same mapping file every lesson page is labelled from.
- **Lab** — Look up what a lesson maps to, then the harder direction: which lessons address a given EU AI Act article.

**Run it** — Look up what a lesson maps to, then the harder direction: which lessons address a given EU AI Act article.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A0.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A0.5   # run it headless and check it
```

*Expect:* Look up what a lesson maps to, then the harder direction: which lessons address a given EU AI Act article.

---
