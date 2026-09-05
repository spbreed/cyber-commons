"""A0 — how to run the commons, before anything in it is read.

One lesson, and it is the only one whose subject is the repository rather than
the systems the repository is about. It exists because the shape of every other
lesson is unusual enough to need saying once: the page you read carries no
procedure, the notebook you run carries no code, and both are pointing at files
in `skills/`.

A reader who does not know that reads the first code cell, sees eight lines of
`subprocess`, and concludes the lessons are stubs.
"""

from . import diagrams as D
from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"A0.1": {
 "concept": """
Every lesson in this commons is three things, and only the first of them is on
the page you are reading.

**The lesson** — the hook, the framework, the idea. Prose and a diagram. This
is the part that is read.

**The skill** — a `SKILL.md` in [`skills/`](https://github.com/spbreed/cyber-commons/tree/claude/vulnbench-setup-scheduling-81aqov/skills):
YAML frontmatter that tells an agent *when* to load the procedure, and markdown
that says *what the procedure is*. It is written for an agent and it reads
perfectly well as a checklist for a person. 120 of them.

**The script** — the executable half of the same skill, in
`skills/<area>/<name>/scripts/`. Standard library only, deterministic, and it
runs against a synthetic CyberTravels estate so two runs can be diffed.

The notebook holds **none** of those. It holds one cell, about twenty lines,
that finds the skills tree — cloning it if it is not already there — and runs
the script as a subprocess. That is deliberate and it is the reason the code
in front of you is short: a fix to a procedure is one edit to one file, not a
rebuild of 120 notebooks each carrying its own copy. Before this arrangement
existed the notebooks held 34,112 lines of code, 9,730 of them identical
copies of the same parser. They now hold 2,373.

The consequence you have to know about is that **a lesson has a dependency it
does not show you**. On your own machine the tree is simply there, because you
cloned the repository to get the notebook. On a hosted kernel it is not, and
the cell fetches it — which needs the kernel's network switched on. That is one
checkbox, and it is the only prerequisite in this whole commons that anybody
gets stuck on.

So there are two routes, and they differ in exactly one respect:

- **GitHub** — clone once, run any lesson, nothing to configure. The tree is
  already on disk, so no lesson fetches anything and no lesson needs a network.
- **Kaggle** — nothing to install, a free CPU kernel, and the notebook fetches
  the tree on first run. Needs **Internet on** in the notebook's settings panel,
  which Kaggle gates behind a verified phone number.

Neither needs a paid account, a GPU, a model, or an API key. A model is
optional everywhere: six skills call one, and all six fall back to a
labelled offline replay when no backend is configured, so the default path
through all 120 lessons is free and offline. [MODELS.md](https://github.com/spbreed/cyber-commons/blob/claude/vulnbench-setup-scheduling-81aqov/MODELS.md)
has the open-weight setup if you want the real thing.
""",
 "steps": [
  ("md", "## 2 · What you need, and what you do not"),
  ("html", D.table(
    ["you need", "for what", "cost"],
    [["A browser", "reading all 120 lessons, and the recorded output of every one",
      "free"],
     ["<span>A Kaggle account, <b>Internet on</b> in notebook settings</span>",
      "running a lesson on a hosted CPU kernel, nothing installed",
      "free · needs a verified phone number"],
     ["<span>Or: <code>git</code> and Python 3.11</span>",
      "running any lesson locally", "free"],
     ["An OpenAI-compatible endpoint", "the six skills that call a model, "
      "against a real model instead of the replay", "optional"]],
    caption="There is no fifth row. No GPU, no paid API, no framework, no "
            "install step — every script is standard library only.")),

  ("md", "## 3 · Route one — GitHub\\n\\n"
         "Clone it, run it. `run_notebooks.py` executes a lesson's cells "
         "headless and writes what it printed, which is the same thing CI does "
         "for all 120 before anything ships.\\n\\n"
         "```bash\\n"
         "git clone https://github.com/spbreed/cyber-commons\\n"
         "cd cyber-commons\\n"
         "python3 scripts/run_notebooks.py --session A0.1   # this lesson\\n"
         "python3 scripts/run_notebooks.py                  # or all 120\\n"
         "```\\n\\n"
         "Or open `labs/notebooks/A0.1.ipynb` in Jupyter and run the cells. "
         "Because the tree is already on disk, nothing is fetched and the "
         "lesson runs with the network off.\\n\\n"
         "To run a skill without a notebook at all — which is what the "
         "notebook does anyway:\\n\\n"
         "```bash\\n"
         "PYTHONPATH=skills/_runtime python3 "
         "skills/programme/lesson-preflight/scripts/lesson_preflight.py\\n"
         "```"),

  ("md", "## 4 · Route two — Kaggle\\n\\n"
         "Every lesson page carries a **Run on Kaggle** button. It opens the "
         "notebook on a free CPU kernel with nothing installed.\\n\\n"
         "1. Open the lesson page and press **Run on Kaggle**.\\n"
         "2. In the settings panel on the right, switch **Internet** to *on*. "
         "Kaggle only offers that toggle once the account has a verified phone "
         "number — Settings → Phone Verification, and it takes a minute.\\n"
         "3. Run the cell.\\n\\n"
         "The first run spends about three seconds on the fetch: a shallow, "
         "blobless, sparse clone that takes the `skills` directory and neither "
         "the history nor the other 119 notebooks. Every run after that is "
         "instant.\\n\\n"
         "**If phone verification is not available to you**, the same tree is "
         "published as the Kaggle dataset `cybercommons/cyber-commons-skills`. "
         "Attach it in the same settings panel and the cell finds it at the "
         "mount point instead of fetching anything. The failure message in the "
         "cell says so too, because being told at the point of failure is worth "
         "more than being told here."),

  ("md", "## 5 · Reading a lesson page\\n\\n"
         "Every lesson page shows the output of a real run — not a transcript "
         "somebody pasted. `run_notebooks.py` executes the notebook here and "
         "records what it printed; `kaggle_verify.py` then pushes the same "
         "notebook to Kaggle, runs it there, and compares the two byte for "
         "byte. All 120 currently match. So the block on the page under **Out** "
         "is what you will get, and if you get something else, one of us has a "
         "bug worth reporting."),

  *skill_steps("programme/lesson-preflight",
               "## 6 · The whole mechanism, demonstrated on itself\\n\\n"
               "The rest of this lesson is the mechanism running. The skill "
               "below is a preflight: it inventories the tree this host "
               "fetched, then runs a real lesson's procedure three times — "
               "twice in the two ways it actually breaks, once correctly.\\n\\n"
               "The two failures are the two you will meet. **(a)** is a "
               "host with no network and nothing fetched. **(b)** is a tree "
               "that arrived but a shared library that is not on the import "
               "path — 13 skills import the runtime rather than carrying a "
               "copy, and the lesson cell is what puts it there. The "
               "procedure it runs correctly in **(c)** is A1.2's, the next "
               "executable lesson after this one, so what you see below is "
               "literally the next page's output."),
 ],
 "expect": "The tree, inventoried from disk rather than asserted \u2014 14 "
           "areas and 120 skills, 119 of them with a script, at the time of "
           "writing; it is a count of what was fetched, so it grows as the "
           "commons does. Then "
           "the same procedure failing twice and working once — exit 2 with "
           "`[Errno 2]` when nothing was fetched, exit 1 with "
           "`ModuleNotFoundError` when the runtime is off the path, and exit "
           "0 with twelve lines and a CRC when both conditions hold. `ready` "
           "is true only because both failures were reproduced; a preflight "
           "that shows only the success has tested one path in three.",
 "challenge": "Run it on the other route. If you read this on Kaggle, clone "
              "the repository and run the same command locally; if you read it "
              "locally, press **Run on Kaggle**. Compare the CRC on the last "
              "line — it should be identical, because the procedure is the "
              "same file in both cases. If it is not, you have found either a "
              "non-determinism in the procedure or a difference between the "
              "hosts, and both are worth an issue.",
},

}
