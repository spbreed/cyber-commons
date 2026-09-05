# Track A0 — Running the Commons — GitHub, Kaggle, and What You Need First

**Function A · Securing AI Architectures**  
*CyberTravels as built, every risk that architecture carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Anyone. This chapter assumes no security background and no setup.

**What changes:** One lesson. The two free routes through the commons, what each needs, and what the single code cell in every lesson is doing — demonstrated by running a real lesson's procedure three times, twice in the ways it breaks. 1 lesson.

**Autonomy focus:** Run one lesson end to end before reading a second one.

**Deliverable:** One lesson executed on a host you did not configure, with its output checksum matching the one recorded here.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A0.1 — Run your first lesson — GitHub, Kaggle, and what you need first

`both directions`

- **Risk** — A reader opens the first code cell, finds twenty lines of subprocess and no procedure, and concludes the lessons are stubs — or runs one on a hosted kernel with no network and reports a broken lesson when the fetch is what failed.
- **Control** — A preflight that inventories the tree from disk and reproduces both failure conditions before reporting the host ready.
- **Lab** — Run the preflight on both routes and compare the output checksum.

**Run it** — Run one lesson end to end on either free route, and see the two ways the arrangement fails before it works.

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
