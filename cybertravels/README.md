# CyberTravels — the sample repository

The system the whole commons is taught on, as source you can scan.

Every lesson names a component of the agentic reference architecture drawn in
[A1.1](https://spbreed.github.io/cyber-commons/lessons/A1.1.html). Until now
each skill carried its own small fixture of that system inline, which meant a
reader met a slightly different CyberTravels in every lesson. This is the one
tree they all point at.

| directory | component (A1.1) | trust |
|---|---|---|
| `ingress/` | ingress — traveller text, unauthenticated until it is not | 0 |
| `orchestrator/` | orchestrator — routes a request to an agent | 2 |
| `agents/` | agent runtime — the loop that turns text into consequence | 2 |
| `tools/` | tools — the only components that change anything | 3 |
| `mcp/` | MCP servers — one internal, one a third party's process | 1 |
| `knowledge/` | knowledge and memory — retrieved text nobody on staff wrote | 0 |
| `messaging/` | agent-to-agent messaging | 2 |

`egress/` is deliberately absent: CyberTravels has no gateway, which is why
A3.7 exists as a lesson rather than an assumption. A component that is missing
is a decision, and a map that does not show it implies it exists.

## It is meant to be defective

This is a corpus for scanners, not a reference implementation. The defects in
it are labelled in `LABELS.md`, which is the ground truth the skills score
themselves against — written by hand, before any scanner ran. A key written
after the scan is a description of the scan.

Nothing here connects to a network or a database. `DB`, `HTTP` and the MCP
clients are stubs, so the tree can be parsed, scanned and imported safely and
gives the same answer on every machine.

## Who reads it

- `appsec/sast-semgrep-deterministic` — real Semgrep, scored on recall
- `appsec/idor-detection-recall` — the defect class no pattern expresses
- `appsec/dead-code-ast-reachability` — the call graph, from the AST
- `appsec/supply-chain-decompile` — `sbom.cdx.json` and what is not in it
