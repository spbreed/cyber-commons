# AGENTS.md — Cyber Commons

Cross-agent instructions (Claude Code, GitHub Copilot coding agent, Cursor, and
any AGENTS.md-aware tool). Claude Code also has richer, auto-triggering skills in
[`.claude/skills/`](.claude/skills); GitHub Copilot has matching prompt files in
[`.github/prompts/`](.github/prompts). All of them call the same entrypoint so
every surface runs identical steps.

## What this repo does
Benchmarks an AI security harness (Mantis-style) by scoring its vulnerability
findings against ground truth (SAST code, real CVEs, and IaC config). See
[README.md](README.md).

## The one entrypoint

```bash
scripts/vulnbench.sh <command>
```

| Command | Does |
|---------|------|
| `doctor` | check prerequisites (git, python3, checkov, venv, datasource) |
| `setup` | create `.venv` and install `pyyaml checkov anthropic jsonschema` |
| `build` | build the ground-truth datasource (~552 rows) + load questions |
| `score --findings <f.jsonl> [--gt-source <s>] [--min-acc <t>]` | score a harness's findings |
| `verify` | regression fingerprint (must print Expert Accuracy 0.9479) |
| `compare` | model comparison scorers (code + IaC) |
| `all --findings <f.jsonl>` | build + score |
| `cybergym-preflight` | check whether this host can run CyberGym (Docker + data + py≥3.12) |
| `cybergym-score --results <verify.jsonl> --benchmark cybergym\|exploitgym\|cybergym-e2e` | score CyberGym-family results |

## Rules for agents
- **Always use `scripts/vulnbench.sh`**, never hand-roll the Python calls.
- Run `doctor` first; if the venv/datasource is missing, run `setup` then `build`.
- The findings file is Mantis `historical_learnings.jsonl` or the richer
  `finding` object (JSONL). `--gt-source` ∈ `secllmholmes-handcrafted`,
  `secllmholmes-realworld`, `terragoat`.
- **Report accuracy, not conformance.** Conformance = valid schema (~100%,
  structural). Accuracy = correctness (the real score). Never present
  conformance as quality.
- A non-zero exit from `score --min-acc` is a **regression** — surface it.
- For real CVE code, frame model analysis as **authorized defensive review of
  public, already-patched code for a benchmark** (bare prompts can trip cyber
  safeguards).
- Do not read `work_mantis/.labels*.json` (the held-out answer keys) when acting
  as the harness — only the scorer uses them.
- **CyberGym family is execution-based** (Docker PoC runs). Always run
  `cybergym-preflight` first; if it says the host cannot run, report that — never
  simulate a reproduction rate. The adapter scores results produced by the real
  runner. See `docs/CYBERGYM_INTEGRATION.md`.
