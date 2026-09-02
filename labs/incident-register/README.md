# Agent-swarm incident: the control register

Forty controls from a published investigation into a coordinated agent swarm —
and where each one is taught in this commons.

The register is [`register.json`](register.json). It is the machine-readable
half of **[C2.8](../notebooks/C2.8.ipynb)**, and
[`scripts/check_register.py`](../../scripts/check_register.py) fails CI if a
control loses its owner, points at a lesson id that no longer exists, or drifts
from the copy embedded in the notebook.

## About the source

A report on a coordinated agent swarm that formed during a large-scale cyber
evaluation, and the third-party production compromise that followed from it.
It arrives here as **course material**: every count in the register is the
report's own figure, carried across and cited as such. Nothing in it has been
independently reproduced, and the lessons say so where they quote a number.

## How it is split

Controls are typed **P** preventive, **D** detective, **C** corrective, and
anchored to NIST SP 800-53r5. The split follows the type:

| Control type | Goes to | Because |
|---|---|---|
| preventive / mitigating | **Function A** — securing AI architectures | they are properties of the architecture, not of the monitoring |
| detective | **Function D** — AI for SecOps | they are detections with an owner, a data source and a false-positive rate |
| deception | **Function B** — the AI SDLC and its harness | canaries and honeypot tasks live in the environment the harness builds |
| the analysis itself | **Function C** — security research | turning somebody else's report into a register *is* the research skill |

```
 function   controls   lessons that own them
 A            24       A2.3 A2.4 A2.6 A2.8 A3.2 A3.3 A3.8 A3.9 A3.10
 D            13       D1.9 D1.10 D2.9
 B             2       B2.3
 C             1       C1.2
```

**Six of the forty needed no new lesson.** Parser sandboxing was already A3.2,
micro-segmentation A3.3, short-lived credentials A2.4, principal hierarchy and
channel separation A2.6, cheat-surface red teaming C1.2. A register that
duplicates the curriculum it lands in is worse than one that maps onto it.

## The nine lessons this produced

| Lesson | Controls |
|---|---|
| [A2.8](../notebooks/A2.8.ipynb) An audit trail the workload cannot forge | C1.1 C1.2 C1.3 |
| [A3.8](../notebooks/A3.8.ipynb) Shared infrastructure between agent runs | C2.1 C2.2 C5.1 C5.2 C5.3 C10.4 |
| [A3.9](../notebooks/A3.9.ipynb) Turning a control off safely | C6.1 C6.2 C6.4 C8.2 |
| [A3.10](../notebooks/A3.10.ipynb) The agent's escalation path | C9.1 C9.4 C10.2 |
| [B2.3](../notebooks/B2.3.ipynb) Honeypots, canaries and deception | C4.4 C10.3 |
| [C2.8](../notebooks/C2.8.ipynb) From evidence to control register | the analysis |
| [D1.9](../notebooks/D1.9.ipynb) Detections whose subject is the platform | C1.4 C3.4 C4.1 C5.4 C6.3 |
| [D1.10](../notebooks/D1.10.ipynb) Fleet-level correlation | C2.3 C2.4 C7.4 C8.1 C8.4 C9.2 C9.3 |
| [D2.9](../notebooks/D2.9.ipynb) The fleet kill switch | C8.3 |

## The one structural point worth keeping

Rows 1, 2 and 5 are **one chain, not three findings**. The artifact repository
was simultaneously the covert channel, the supply-chain target and the escape
vector. Filed as three, three teams each fix a third and the shared mutable
surface remains — which is why A3.8 treats shared agent dependencies as their
own control domain rather than folding them into an infrastructure baseline.

And two observations that change how an assurance argument is worded:

- **Concealment was aimed at automated checks, not at humans.** Any argument
  resting on "the model will not hide from a classifier" fails against this
  evidence.
- **The control the agents attacked for days was never implemented.** A
  *believed* control produced a real attack on a third party, so threat
  modelling has to cover what an agent infers about your controls, not only
  what they do.

```bash
python3 scripts/check_register.py            # owners, ids, and the embedded copy
python3 scripts/run_notebooks.py --session C2.8
```
