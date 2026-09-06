# Function D restructure — the five-phase agentic SOC

Working plan. Delete this file once the restructure has shipped and verified.

D1 (Detection, 12) and D2 (Response, 9) become five phase chapters. Each
existing lesson moves; nothing is deleted. New lessons fill the capabilities
that had no lesson and no skill.

## D1 · Discover — threat intel, behaviour monitoring, hunting

| new | old | title |
|---|---|---|
| D1.0 | D1.0 | Start here — what AI for security operations means |
| D1.1 | D1.8 | Threat intel sub-lane |
| D1.2 | D1.5 | Agent telemetry as a data source |
| D1.3 | D1.7 | Drift monitoring |
| D1.4 | D1.6 | Distinguishing agent from human |
| D1.5 | NEW  | Hunting in agent telemetry |

## D2 · Detect — writing the rules, and generating them

| new | old | title |
|---|---|---|
| D2.1 | D1.3 | Agent-assisted detection engineering |
| D2.2 | NEW  | Generating detection rules from an incident |
| D2.3 | D1.4 | Detection engineering *for* agents |
| D2.4 | D1.9 | Detections whose subject is the agent platform |
| D2.5 | D1.11 | Honeypots, canaries and deception in the agent's environment |

## D3 · Investigate — admission, planning, correlation, triage

| new | old | title |
|---|---|---|
| D3.1 | D1.1 | From alert queue to loop operator |
| D3.2 | NEW  | Admission rules — what the investigating agent may touch |
| D3.3 | NEW  | Plan, then replan — an investigation that changes its mind |
| D3.4 | D1.10 | Fleet-level correlation: seeing a swarm |
| D3.5 | D2.1 | Agent-assisted reconstruction |
| D3.6 | D1.2 | Context that makes triage work |
| D3.7 | D2.2 | When the actor is an agent |
| D3.8 | D2.3 | Scoping an agentic incident |

## D4 · Respond — policy first, then the runbook tier

| new | old | title |
|---|---|---|
| D4.1 | NEW  | Remediation policy — what may be done without asking |
| D4.2 | NEW  | Runbook tiers: fully automated, human in the loop, manual |
| D4.3 | D2.4 | Containment at machine speed |
| D4.4 | D2.7 | Stop authority |
| D4.5 | D2.9 | The fleet kill switch |

## D5 · Recover and root cause

| new | old | title |
|---|---|---|
| D5.1 | D2.5 | Replay and forensics |
| D5.2 | NEW  | The root cause record |
| D5.3 | NEW  | Validating the fix against the KCIs |
| D5.4 | D2.6 | Post-incident change surface |
| D5.5 | NEW  | Proposing the policy change |
| D5.6 | D2.8 | Regulatory clock |

D goes from 21 lessons to 29. Seven new lessons, one existing lesson (D1.0)
keeps its id.

## New skills

| skill | phase | lesson |
|---|---|---|
| `detection/agent-telemetry-hunt` | discover | D1.5 |
| `detection/detection-rule-synthesis` | detect | D2.2 |
| `secops/investigation-admission-rules` | investigate | D3.2 |
| `secops/investigation-replan-trace` | investigate | D3.3 |
| `response/remediation-policy-check` | respond | D4.1 |
| `response/runbook-tier-assignment` | respond | D4.2 |
| `response/root-cause-record` | recover | D5.2 |
| `response/kci-fix-validation` | recover | D5.3 |
| `grc/policy-change-proposal` | recover | D5.5 |

## Elsewhere in this batch

- A0.2 — the frameworks, with a reference table each. New skill
  `regulatory/framework-reference-lookup`.
- E1.1 — reworked around building KCIs from framework controls.
- E1.13 — measuring those KCIs against CyberTravels, with gaps and
  mitigations. New skill `grc/kci-control-measurement`.

## Order of work

1. curriculum.json — renumber D, add the new sessions.
2. labs.json — move every lab block with its lesson.
3. frameworks.json — track rows for D1..D5, drop D1/D2 pair.
4. exercises — split track_d1.py / track_d2.py into five, keeping bodies.
5. skills — write the nine new ones, test each.
6. A0.2, E1.1, E1.13.
7. build_notebooks, run_notebooks, check everything.
8. One Kaggle push and verify at the end.

Cross-references to old D ids live in exercises, curriculum/track-*.md, the
incident register and skills. `grep -rn "D1\.\|D2\."` after the renumber.
