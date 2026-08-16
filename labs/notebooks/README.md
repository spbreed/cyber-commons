# Lesson notebooks

One Python notebook per curriculum session — **104 of them**, generated from the
single source of truth and executed in CI before they ship.

```
labs/notebooks/<SESSION>.ipynb     e.g. A2.5.ipynb, M0.4.ipynb, B2.10.ipynb
labs/notebooks/_results.json       execution evidence, written by run_notebooks.py
```

## Running one

**In your browser, no setup —** open the lesson page and press **▶ Run on
Kaggle**. It creates the notebook as a new kernel in *your own* Kaggle account;
the first cell clones this repository so the lab library is available. Nothing
is written back here.

**Locally —**

```bash
git clone https://github.com/spbreed/cyber-commons && cd cyber-commons
jupyter notebook labs/notebooks/A2.5.ipynb
```

**Headless, to check it —**

```bash
python3 scripts/run_notebooks.py --session A2.5
python3 scripts/run_notebooks.py              # all 104, writes _results.json
```

## What they run against

Every notebook imports [`labs/cybercommons`](../cybercommons), the shared lab
library. It is **standard library only** — a deliberate constraint, so the
notebooks run on a Kaggle kernel with the internet switched off, on an
air-gapped laptop, and in CI, with nothing to install and no API key.

Where a lesson names a real tool you would actually deploy — Falco, OPA, SPIRE,
Keycloak, garak — the notebook models the *decision* that tool makes. The
`run` block in [`curriculum/labs.json`](../../curriculum/labs.json) keeps the
real invocation underneath, labelled as the full-infrastructure variant.

Check the library itself with:

```bash
python3 labs/cybercommons/selftest.py    # 32 checks, each one a claim a lesson makes
```

## Editing a lesson

**Never edit an `.ipynb` here by hand** — they are generated and will be
overwritten. Change the source and rebuild:

| To change… | Edit |
|---|---|
| Title, risk, control, tools, models | `site/data/curriculum.json` |
| The exercise: prose, code cells, "Your turn" | `scripts/exercises/<track>.py` |
| The goal and the "Expect" line | `curriculum/labs.json` |
| The library the exercises call | `labs/cybercommons/*.py` |

```bash
python3 scripts/build_notebooks.py   # regenerate all 104
python3 scripts/run_notebooks.py     # prove they still run, refresh the evidence
python3 scripts/build_site.py        # re-render the lesson pages
```

CI runs all three with `--check` and fails on drift, so the notebook you read on
the site is always the notebook that ran.

## Pushing them to Kaggle

`scripts/kaggle_push.py` publishes the notebooks as Kaggle kernels and polls
their status, so "did it execute remotely" has an evidenced answer.

```bash
python3 scripts/kaggle_push.py --check          # verify auth + reachability
python3 scripts/kaggle_push.py --all --wait     # push all 104, poll until done
```

Credentials come from `$KAGGLE_USERNAME`/`$KAGGLE_KEY` or
`~/.kaggle/kaggle.json` — **never from this repository**. The script refuses to
read a credential file located inside the repo, `.gitignore` excludes
`kaggle.json`, and `scripts/check_secrets.py` runs as a pre-commit hook and in
CI to block anything credential-shaped from being committed. Install the hook
once with `./scripts/install-hooks.sh`.
