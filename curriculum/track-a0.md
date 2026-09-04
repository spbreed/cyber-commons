# Track A0 — How This Commons Runs

**Function A · Securing AI Architectures**  
*CyberTravels as built, every risk that architecture carries, and the controls that close them. Get this layer wrong and no amount of downstream diligence recovers it.*

**Job titles:** Everyone, once

**What changes:** One lesson on the mechanism every other lesson uses: an agent skill, a shared runtime, and a Kaggle kernel. 1 lesson.

**Autonomy focus:** Read it once and the other 116 lessons stop being magic.

**Deliverable:** The same runtime wired into a notebook of your own.

> Every session below ships a runnable notebook that actually executes — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A0.1 — How a lesson runs — skills, one shared runtime, and Kaggle

`both directions`

- **Risk** — A curriculum whose mechanism is undocumented teaches people to run cells they cannot explain, and copies its own boilerplate into every notebook until a fix means rebuilding all of them.
- **Control** — One skill format, one shared runtime loaded rather than copied, and an output contract whose ceiling is stated out loud.
- **Lab** — Load a skill with the shared runtime, check an instance against its contract, and watch a vacuous result conform.

**Run it** — Run the mechanism every other lesson uses, on itself: load the shared runtime, split a SKILL.md, check an instance against its output contract, and see what conformance does not prove.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A0.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A0.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
# --- the notebook: stdlib only, no install ---
jupyter notebook labs/notebooks/A0.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A0.1   # run it headless and check it
```

*Expect:* The runtime reports that it was loaded once and shared. The frontmatter splits from the body. An instance built from this skill conforms to its own contract — and so does a vacuous one, while a value outside an enumeration is caught.

---
