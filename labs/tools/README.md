# Tool labs — the products, actually running

Everything in `labs/notebooks/` is standard library only, so it runs on a
Kaggle kernel with the internet switched off. That is a deliberate constraint
and it has a cost: a lesson that models RFC 8705 in eighty lines of Python
proves that the *protocol* works, not that the product you are about to deploy
implements it.

These four labs close that gap. Each one downloads a real open-source product,
runs it, and tests the claim the corresponding lesson makes.

| Lab | Product | Tests the claim in | Needs |
|---|---|---|---|
| [`keycloak-obo/`](keycloak-obo) | Keycloak 26.0.7 | [A2.3](../notebooks/A2.3.ipynb) — on-behalf-of tokens, RFC 8693, RFC 8705 | Java 21+, openssl, ~1 GB |
| [`semgrep-sast/`](semgrep-sast) | Semgrep 1.176.0 | [B2.3](../notebooks/B2.3.ipynb) — deterministic SAST, and what it misses | python3 |
| [`openapi-audit/`](openapi-audit) | openapi-spec-validator | [B2.2](../notebooks/B2.2.ipynb) — the threat model's static inputs | python3 |
| [`litellm-gateway/`](litellm-gateway) | LiteLLM 1.99.0 | [A3.7](../notebooks/A3.7.ipynb) — the agent gateway as a choke point | python3 |

```bash
cd labs/tools/keycloak-obo && ./run.sh
```

Each script is idempotent: it downloads into `./work/` (gitignored), skips what
is already there, and can be re-run. None of them needs a model API key. None
of them writes anything outside its own directory.

**[EVIDENCE.md](EVIDENCE.md) records what happened when these were last run**,
including the two findings that contradict what the specifications say should
happen — Keycloak's standard token exchange emits no `act` claim, and it drops
the `cnf` binding on the exchanged token. Those are the reason this directory
exists rather than a paragraph saying "and Keycloak does this for you".

## Why the split is worth keeping

A lesson that only ever ran the real product would not run on Kaggle, would
break when the product's next release changes a flag, and would teach the
product rather than the idea. A lesson that only ever modelled the protocol
would never have discovered that the exchanged token is unbound.

So: the notebook teaches the mechanism and runs anywhere; the lab checks the
mechanism against the thing you will actually deploy, and reports the
difference.
