# Track E3 — The BISO, Risk Communicator & CISO Office

**Function E · Governance, Risk, Compliance & the CISO Office**  
*The function that has to make all of the above defensible to a board, an auditor and a regulator — usually in that order.*

**Job titles:** BISO, Deputy CISO, Head of Security Strategy, CISO

**What changes:** You are being asked to approve a class of system whose failure modes your existing risk language cannot express, on a timeline set by the business.

**Autonomy focus:** You hold the authority to move any workflow down a rung — and the obligation to use it.

**Deliverable:** A one-page autonomy governance policy and a board-level narrative for one agentic programme.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### E3.1 — Translating agentic risk upward

`Security of AI`

- **Risk** — Blast radius explained in engineering terms to a board that needs consequence.
- **Control** — What can happen, how fast, who can stop it.
- **Lab** — Convert one blast-radius measurement into a board paragraph.

**Run it** — Turn a blast-radius measurement into a board paragraph.

```bash
cd labs/e3-ciso
python3 translate.py --input ../a1-control-plane/blast.md --audience board
python3 translate.py --input ../a1-control-plane/blast.md --audience board --check-jargon
```

*Expect:* What can happen, how fast, who can stop it — with the engineering vocabulary stripped out.

---

### E3.2 — Governing autonomy rather than approving tools

`Security of AI`

- **Risk** — A per-tool review queue becomes a bottleneck and then a bypass.
- **Control** — A policy on delegated authority instead of tool-by-tool approval.
- **Lab** — Write the delegated-authority policy.

**Run it** — Replace a per-tool review queue with a delegated-authority policy.

```bash
cp curriculum/templates/autonomy-policy.md labs/e3-ciso/policy.md
cd labs/e3-ciso && python3 policy_lint.py --policy policy.md --require promotion-criteria,demotion-authority,action-class-limits
```

*Expect:* The linter rejects aspirational language and demands named authority.

---

### E3.3 — Sequencing the programme

`Security of AI`

- **Risk** — Starting with the workflow that is most visible rather than most winnable.
- **Control** — Use the maturity model to order investment; choose your first hard "no".
- **Lab** — Sequence your first three workflows and name the no.

**Run it** — Sequence the first three workflows — and name the first hard no.

```bash
cd labs/e3-ciso
python3 sequence.py --candidates ../e1-grc/workflows.yaml --maturity agent --out roadmap.md
```

*Expect:* Ordered by winnability × risk retired, with one explicit refusal. A programme without a 'no' has no policy.

---

### E3.4 — Org design and ownership

`Security of AI`

- **Risk** — Harness engineering with no home; research as a hobby.
- **Control** — Identity owns the control plane; BUs own grants; security owns stop authority.
- **Lab** — Draw your org's ownership map against the topic matrix.

**Run it** — Draw your org's ownership map against the topic matrix.

```bash
cd labs/e3-ciso
python3 ownership.py --matrix ../../curriculum/templates/ownership-map.csv --org my-org.yaml
python3 ownership.py --find-gaps
```

*Expect:* Every topic cluster with zero owners or two owners is a finding — usually harness engineering and research.

---

### E3.5 — The metrics that matter at your level

`Security of AI`

- **Risk** — Reporting activity instead of exposure.
- **Control** — Inventory coverage, attested-identity share, standing-access reduction, MTT-revoke, blast-radius distribution, eval-gate pass rate.
- **Lab** — Instrument the six metrics from your lab stack.
- **Tools** — `OpenSearch`

**Run it** — Instrument the six board-level metrics from your own lab stack.

```bash
cd labs/e3-ciso
python3 metrics.py --spire --gateway --register agent-register.csv --evals ../b2.10-eval-harness/work_mantis/comparison_results.json
```

*Expect:* Inventory coverage, attested-identity share, standing-access reduction, MTT-revoke, blast-radius distribution, eval-gate pass rate.

---

### E3.6 — Saying no, and saying yes with conditions

`Security of AI`

- **Risk** — Conditional approval that is aspirational rather than enforceable.
- **Control** — Autonomy promotion as an earned event with named evidence.
- **Lab** — Write one enforceable conditional approval.

**Run it** — Make a conditional approval enforceable rather than aspirational.

```bash
cd labs/e3-ciso
python3 conditional.py --workflow patch-agent --conditions eval-gate>=0.85,hitl-on-merge,90d-review
python3 conditional.py --verify patch-agent   # checks the conditions are machine-checkable
```

*Expect:* Any condition that cannot be automatically verified is flagged. 'They'll be careful' does not compile.

---

### E3.7 — Building the capability

`Security of AI`

- **Risk** — Hiring for conceptual familiarity instead of practice.
- **Control** — Interview questions that separate the two; internal transition paths.
- **Lab** — Write the interview loop for an agentic security engineer.

**Run it** — Write an interview loop that separates familiarity from practice.

```bash
cd labs/e3-ciso
python3 interview.py --role agentic-security-engineer --generate-loop
python3 interview.py --calibrate --against ../b2.10-eval-harness   # ask them to read a real eval report
```

*Expect:* Questions with artefacts attached. Handing a candidate a real eval report separates the two groups fast.

---

### E3.8 — Resilience over perfection

`Security of AI`

- **Risk** — Trying to enumerate every failure mode of a probabilistic system.
- **Control** — Maturity measured by containment, detection and recovery — not prevention.
- **Lab** — Re-score your programme on the resilience axis.

**Run it** — Re-score your programme on containment/detection/recovery.

```bash
cd labs/e3-ciso
python3 resilience.py --score --axes containment,detection,recovery --evidence ../
python3 resilience.py --compare-to prevention-only
```

*Expect:* Prevention-only scoring flatters you. The resilience axes are where a probabilistic system is actually judged.

---
