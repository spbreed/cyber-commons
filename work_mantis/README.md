# Real Mantis runs — corpora, answer keys, and evidence

This directory holds the **committed evidence** for the real (non-simulated)
Mantis runs described in [`docs/REAL_MANTIS_RUN.md`](../docs/REAL_MANTIS_RUN.md)
and [`docs/MODEL_COMPARISON.md`](../docs/MODEL_COMPARISON.md). Everything needed
to reproduce and audit the results is checked in.

## Blind corpora (committed)

- `blind/` — the 48 SecLLMHolmes **hand-crafted** files copied to opaque names
  (`sample_001.c` …). 24 vulnerable, 24 patched/safe.
- `blind_rw/` — the 30 **real-world CVE** files copied to opaque names
  (`rw_001.c` …). 15 vulnerable pre-fix + 15 patched revisions from libtiff,
  gpac, the Linux kernel, and pjsip.

These are copies of already-public OSS code (SecLLMHolmes). They are committed
so the exact inputs each model saw are inspectable.

## Answer keys (committed)

- `.labels.secret.json` — hand-crafted map: `blind_id → {orig_path,
  is_vulnerable, cwe}`.
- `.labels_rw.secret.json` — real-world map (adds `cve`, `proj`).

(The `.secret` in the filename is historical — they were held out **during**
each run and are now published as evidence. Because they are committed, a future
agent with repo access is no longer truly blind; the *past* runs remain blind,
proven by git history showing each model's `verdicts_*.json` committed before
the keys were published.)

## Per-model verdicts (committed, locked before scoring)

| File | Model | Corpus |
|------|-------|--------|
| `verdicts.json`            | Opus (interactive)  | hand-crafted |
| `verdicts_sonnet.json`     | Sonnet (subagent)   | hand-crafted |
| `verdicts_haiku.json`      | Haiku (subagent)    | hand-crafted |
| `verdicts_rw_opus.json`    | Opus (subagent)     | real-world |
| `verdicts_rw_sonnet.json`  | Sonnet (subagent)   | real-world |
| `verdicts_rw_haiku.json`   | Haiku (subagent)    | real-world |

Each is `{"model": …, "verdicts": {blind_id: {"v": 0|1, "cwe"?, "why"}}}`.

## Reproduce the scores

```bash
python work_mantis/compare_models.py     # precision/recall/F1/CWE-acc/Expert per run
```

Cross-check any single run through the official scorer by emitting a Mantis
findings file from a verdicts file (translating blind_id → real path via the
answer key) and running `bench/run_benchmark.py` — e.g. the committed
`data/mantis_claude_blind.historical_learnings.jsonl` (Opus) and
`data/mantis_sonnet_blind.historical_learnings.jsonl` (Sonnet) reproduce
Expert 0.8958 / 0.7500 respectively.

## Instruction brief given to every model

`AGENT_INSTRUCTIONS.md` — identical for all models: run the real
`mantis-researcher` methodology, contents-only, constrained to the 8-CWE
SecLLMHolmes taxonomy, no peeking at answer keys.
