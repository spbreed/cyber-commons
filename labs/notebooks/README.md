# Lesson notebooks

One Python notebook per curriculum session — **110 of them**, generated from the
single source of truth and executed in CI before they ship.

Each notebook is **self-contained**: it carries every line of code it runs. No
shared library, nothing to clone, no `pip install`. That is what lets it execute
on a Kaggle kernel with the internet switched off, and it means you can lift one
cell into your own repository without inheriting a dependency. The build refuses
any notebook that imports outside the standard library.

```
labs/notebooks/<SESSION>.ipynb     e.g. A2.5.ipynb, B1.16.ipynb, B2.10.ipynb
labs/notebooks/_results.json       execution evidence, written by run_notebooks.py
```

## Running one

**In your browser, no setup —** open the lesson page and press **▶ Run on
Kaggle**. It creates the notebook as a new kernel in *your own* Kaggle account
and runs it there. Nothing is written back here.

**Locally —**

```bash
git clone https://github.com/spbreed/cyber-commons && cd cyber-commons
jupyter notebook labs/notebooks/A2.5.ipynb
```

**Headless, to check it —**

```bash
python3 scripts/run_notebooks.py --session A2.5
python3 scripts/run_notebooks.py              # all 110, writes _results.json
```

## What they run against

Nothing but the Python standard library.

Where a lesson names a real tool you would actually deploy — SPIRE, OPA, Falco,
Keycloak, garak — the notebook models the *decision* that tool makes, so the
lesson still lands on a machine that cannot pull containers. The `run` block in
[`curriculum/labs.json`](../../curriculum/labs.json) keeps the real invocation
underneath, labelled as the full-infrastructure variant.

Where a lesson involves a model, it runs against a **deterministic stand-in**
that is labelled as a stand-in everywhere it appears — never presented as a
model's output. Each of those notebooks prints the exact command to point the
same code at a real open-weight model:

```bash
ollama pull glm-4.6            # or kimi-k2, llama3.3
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama MODEL=glm-4.6
```

## Editing a lesson

**Never edit an `.ipynb` here by hand** — they are generated and will be
overwritten. Change the source and rebuild:

| To change… | Edit |
|---|---|
| Title, risk, control, tools, models | `site/data/curriculum.json` |
| The exercise: concept, code cells, "Your turn" | `scripts/exercises/track_<id>.py` |
| The goal and the "Expect" line | `curriculum/labs.json` |

Every exercise needs a `concept` field. The build fails without one — a lesson
that opens with a risk teaches people to fear a mechanism they cannot describe.

```bash
python3 scripts/build_notebooks.py   # regenerate all 110
python3 scripts/run_notebooks.py     # prove they still run, refresh the evidence
python3 scripts/build_site.py        # re-render the lesson pages
```

CI runs all three with `--check` and fails on drift, so the notebook you read on
the site is always the notebook that ran.

## Pushing them to Kaggle

`scripts/kaggle_push.py` publishes the notebooks as Kaggle kernels and polls
their status, so "did it execute remotely" has an evidenced answer.

```bash
python3 scripts/kaggle_push.py --check                        # auth + reachability
python3 scripts/kaggle_push.py --all --wait --concurrency 4   # push, poll until done
```

Three Kaggle behaviours the script handles, each found by testing rather than by
reading documentation:

- **`KGAT_` tokens are Bearer tokens.** The older username+key Basic scheme
  returns `401 Unauthenticated` for them, which reads like a bad credential
  rather than a wrong scheme.
- **`/kernels/push` returns HTTP 200 with `hasError: true`** when it rejects a
  push. Checking only the status code reports every failed push as a success, so
  the client inspects the body.
- **Kaggle allows 5 concurrent batch CPU sessions**, and a kernel runs on push.
  Pushing them all at once fails most of them with *"Maximum batch CPU session
  count of 5 reached"* plus HTTP 429s, so the client pushes in batches and waits
  for each to finish.

Kernels are created **private**. Kaggle rejects a public push with HTTP 403
*"Phone verification is required to make a notebook public"* unless the owning
account has a verified phone number — an account setting, not something the
script should route around. Pass `--public` once it is verified.

## Verifying they actually produced the right output

A kernel status of `complete` only means Kaggle finished running it. **A
notebook that prints nothing also completes.** `scripts/kaggle_verify.py`
closes that gap: it pulls each kernel's remote stdout and compares it, line for
line, against a fresh local run of the same notebook.

```bash
python3 scripts/kaggle_verify.py --save     # writes _kaggle_verified.json
```

Because the notebooks are deterministic by design, byte-identical output from
two independent machines is the real evidence a lesson runs — and any
difference is a finding, not noise. It has already caught two:

- **B1.3** iterated a set difference into a stable sort. With tied threat
  scores the sort preserved set-iteration order, which Python randomises per
  process via `PYTHONHASHSEED`.
- **D1.1** seeded its sampling RNG from `hash(alert.aid)`. Python randomises
  string hashing per process, so the sampled subset changed on every run.

Neither showed up locally, where a single process runs every notebook with one
hash seed. If you write a lesson that samples, ranks, or iterates a set, seed
it from something stable (`zlib.crc32`, not `hash`) and give any sort a full
tiebreak.

Credentials come from `$KAGGLE_USERNAME`/`$KAGGLE_KEY` or
`~/.kaggle/kaggle.json` — **never from this repository**. The script refuses to
read a credential file located inside the repo, `.gitignore` excludes
`kaggle.json`, and `scripts/check_secrets.py` runs as a pre-commit hook and in
CI to block anything credential-shaped from being committed. Install the hook
once with `./scripts/install-hooks.sh`.
