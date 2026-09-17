# Lesson notebooks

One Python notebook per curriculum session — **134 of them**, generated from the
single source of truth and executed in CI before they ship.

Each notebook is **code only** — one cell, no markdown. The prose lives on the
lesson page and nowhere else: it was in both places once, and the copy inside
the notebook was the one nobody could correct.

The notebook carries **no procedure of its own**. It fetches the skills tree — a
shallow, sparse clone of this repository, about three seconds — and runs one
script out of `skills/<area>/<name>/scripts/`. One fix to one file, not a
rebuild of 134 copies. Standard library only, no `pip install`; the build
refuses any notebook that imports outside it.

> **On Kaggle a kernel starts with no network**, so the clone fails with
> `Could not resolve host: github.com` until **Internet** is switched on in the
> settings panel. Every notebook's header comment says so, and says what to do
> without a phone-verified account: attach the
> [`cybercommons/cyber-commons-skills`](https://www.kaggle.com/datasets/cybercommons/cyber-commons-skills)
> dataset and nothing is fetched at all.

```
labs/notebooks/<SESSION>.ipynb     e.g. A2.5.ipynb, B2.10.ipynb, D3.8.ipynb
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
python3 scripts/run_notebooks.py              # all 134, writes _results.json
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
| The exercise: concept, steps, "Your turn" | `scripts/exercises/track_<id>.py` |
| The procedure the notebook actually runs | `skills/<area>/<name>/scripts/` |
| The goal and the "Expect" line | `curriculum/labs.json` |

Every exercise needs a `concept` field. The build fails without one — a lesson
that opens with a risk teaches people to fear a mechanism they cannot describe.
[CLAUDE.md](../../CLAUDE.md) is the full map of sources and what each generates.

```bash
python3 scripts/build_notebooks.py   # regenerate all 134
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

### Internet, and therefore frontier models, on Kaggle

Seven lessons can call a real model. On Kaggle that needs two things, and the
first one is an account setting rather than anything the code can arrange:

1. **Internet enabled on the notebook**, which Kaggle gates behind a
   **phone-verified account** — the same verification that gates public
   notebooks.
2. **The key in Add-ons → Secrets** as `ANTHROPIC_API_KEY`. The adapter reads
   it from there automatically (`kaggle_secrets` is pre-installed in the Kaggle
   image and the import is guarded, so nothing is added to the dependency set).

Pushed with `enableInternet: true` on an unverified account, the kernel runs and
reports:

```
  dns  api.anthropic.com: FAILED gaierror
  dns  pypi.org:          FAILED gaierror
  http api.anthropic.com: BLOCKED URLError: Temporary failure in name resolution
```

The flag is accepted by the API and silently not granted — the same shape as the
GPU flag. Until the account is verified, every lesson on Kaggle correctly stays
on the deterministic replay and says so, which is why the offline path is the
default rather than a fallback.

Kernels are created **private** and made public separately. Two things to know,
both learned the expensive way:

- **Publishing is capped at about 15 public notebooks per day.** That is a
  quota, not a rate limit: backoff does not clear it, and it resets on the day
  boundary. The API says so plainly — `HTTP 429 {"code":429,"message":"You have
  reached the limit for publishing public notebooks per day."}` — while the push
  client's own message reads "retries exhausted", which is misleading. Filling
  in the rest is a job measured in days.
- **Kaggle answers `HEAD` with 404 for a kernel that is public.** Probe with
  `GET`. `scripts/check_kaggle_public.py` does, and writes
  `_kaggle_public.json`; a `HEAD` probe reports every kernel private and
  silently disables every embed on the site.

A private kernel renders in an iframe as an **empty rectangle with no error** —
green build, finished-looking page, blank box. That is why the lesson page
embeds conditionally and otherwise shows the verified recorded output inline.

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
difference is a finding, not noise. **All 134 matched** at the last full
verification — the evidence is in
[`_kaggle_verified.json`](_kaggle_verified.json). It has already caught two that
did not:

- One iterated a set difference into a stable sort. With tied threat scores the
  sort preserved set-iteration order, which Python randomises per process via
  `PYTHONHASHSEED`.
- One seeded its sampling RNG from `hash(alert.aid)`. Python randomises string
  hashing per process, so the sampled subset changed on every run.

Both are fixed, and `scripts/check_determinism.py` now runs every notebook
across four hash seeds in CI, so the next one is caught in nine seconds rather
than after a full round of remote pushes.

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
