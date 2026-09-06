"""ABOUT and CyberTravels grounding for the lessons added with the D restructure.

Merged into `about.py` and `cybertravels.py` at import, for the same reason
`framing_new.py` exists: those files were already long, and these eleven arrived
as one set.
"""
from __future__ import annotations

ABOUT: dict[str, str] = {

"A0.2": """
**What it covers.** The four control vocabularies this curriculum labels against — OWASP's LLM and Agentic Top 10s, MITRE ATLAS, the NIST AI RMF and the EU AI Act — what question each one answers, and a reference table for each.

**Why a security engineer needs it.** These get used interchangeably and they are not interchangeable. A threat id in a risk register and a NIST function in a vulnerability report are both category errors, and both produce findings the receiving audience cannot act on. The lookup also runs the direction an auditor actually asks in: not "what does this lesson map to" but "show me every lesson that addresses human oversight".
""",

"D1.5": """
**What it covers.** Hypothesis-first hunting over agent telemetry: stating a falsifiable hypothesis, naming the population before running it, scoring what it caught against what it missed, and deciding to promote, tune or discard.

**Why a security engineer needs it.** Detections encode behaviour somebody already understood. Everything outside them is invisible, and the agent behaviour worth catching is usually behaviour nobody had thought to write a rule for. The discipline is in the scoring: the hypothesis that feels most obviously right is often a description of normal work, and shipping it costs a quarter of everyone's attention.
""",

"D2.2": """
**What it covers.** Generating a detection rule from a reconstructed incident, and measuring it against benign traffic before it ships.

**Why a security engineer needs it.** An incident is the richest source of a good rule and the easiest source of a bad one, because every candidate you write from it catches it. The property that decides deployability is the false-positive rate on traffic that is not the incident — which means a benign corpus containing the hard cases, not unrelated noise.
""",

"D3.2": """
**What it covers.** Admission rules for an investigating agent: which sources it may reach, which fields it may never see, how much it may pull, and why every refusal is recorded with its query.

**Why a security engineer needs it.** Incident response grants the broadest read access in the organisation, at the moment of least supervision, often to an agent. That grant is frequently larger than the incident being investigated. Bounding it per investigation class, in advance, is the difference between a response and a second breach — and the refusal log is the evidence you were on the right side of that.
""",

"D3.3": """
**What it covers.** Investigations that abandon a hypothesis when the evidence refutes it, and keep the abandoned branch visible in the trace.

**Why a security engineer needs it.** Agents score evidence on support, so evidence that supports nothing reads as noise — and refutation is precisely what should force a replan. The result is an investigator that spends the whole incident confirming step one. A conclusion with no visible alternatives also cannot be audited: a reviewer needs to see what was considered and dropped.
""",

"D4.1": """
**What it covers.** The remediation policy: classifying every response action on reversibility and blast radius, and deriving each runbook's automation tier from that rather than from its author.

**Why a security engineer needs it.** If tiers are chosen per runbook, the blast radius of your incident response is unknown until it fires. Two properties of the action decide it, and reversibility outranks radius — which is why deleting one agent's workdir is manual while forcing human-in-the-loop across the whole estate is not.
""",

"D4.2": """
**What it covers.** The three runbook tiers — fully automated, human in the loop, manual — timed against one incident, with the cost of acting on a bad signal beside the time to contain.

**Why a security engineer needs it.** "Automate everything" and "keep a human in it" are both asserted constantly and neither is a position. The tiers trade time against the cost of being wrong, and the right trade depends on the detection's measured false-positive rate. Against a 29-minute breakout time, a manual tier that contains in 34 minutes is a risk decision — just an unstated one.
""",

"D5.2": """
**What it covers.** The root cause record: walking the control chain, marking each control present, absent or present-but-wrong, and testing whether the resulting statement names a control rather than a person.

**Why a security engineer needs it.** Incidents that close with a narrative recur, because nothing in a narrative can be built or measured. Naming the control makes the finding actionable and gives the next stage something to verify. The test is mechanical on purpose — "the engineer missed the alert" is true, and it is not a root cause.
""",

"D5.3": """
**What it covers.** Re-measuring the key control indicators an incident moved, after the fix, and reporting which were actually restored.

**Why a security engineer needs it.** A closed ticket is not evidence that a control came back. Automating the re-measurement is what makes it happen on every fix rather than the memorable ones — and it routinely finds that an indicator improved without reaching target, which reads as "done" in every system that does not check.
""",

"D5.5": """
**What it covers.** Turning a root cause record into a policy diff, with the incident's measured numbers as the reason, and naming what the diff does not fix.

**Why a security engineer needs it.** Most incidents change what is deployed and leave what is *allowed* untouched, so the next system built under the same policy reproduces the conditions. A diff can be argued with; a postmortem paragraph cannot. And an indicator that no policy change can fix is an engineering item — saying so in the proposal is what stops it falling between two functions.
""",

"E1.13": """
**What it covers.** Turning mapped controls into indicators that can be computed from the repository, running them against CyberTravels, and reporting each gap with the lesson that closes it.

**Why a security engineer needs it.** A control asserted in a register and never measured has no evidence behind it until an incident supplies some. The test for a real indicator is mechanical — can this be computed from the estate today, without asking anyone — and the output has to be a gap list rather than a score, because nobody can action 72%.
""",

}

CYBERTRAVELS: dict[str, str] = {

"A0.2": "CyberTravels is the system every label in this curriculum is applied "
        "to, so the reference tables here are not abstract: the coverage "
        "counts are how many lessons about this one estate address each "
        "control. A framework with one lesson behind it is a thin spot in "
        "CyberTravels' defence, stated in the regulator's own vocabulary.",

"D1.5": "The corpus is CyberTravels' agent runs — the Workflow Agent and the "
        "RAG Advisor, forty runs across a fortnight. The overnight batch that "
        "wrecks the working-hours hypothesis is CyberTravels' own nightly "
        "reconciliation, which is exactly the kind of legitimate oddity that "
        "makes an obvious hunt useless in a real estate.",

"D2.2": "The incident is CyberTravels': the Workflow Agent issued a refund "
        "against a booking nobody asked it to touch. The benign corpus is the "
        "hard one on purpose — CyberTravels processes eighteen legitimate "
        "refunds in the same window, and a rule that cannot tell them apart "
        "is a rule that alerts on the business.",

"D3.2": "The admission set is written for CyberTravels' agent-misuse class: "
        "agent traces, gateway logs and the tool audit are in; the bookings "
        "database, with its payment cards, is not. The refused query that "
        "matters is the one asking for ninety thousand rows of a source that "
        "IS admitted — CyberTravels' whole gateway log, which is a copy.",

"D3.3": "The investigation is CyberTravels' refund incident, and the branch "
        "that gets abandoned is the one everybody starts with: the Workflow "
        "Agent issued the refund, so the Workflow Agent is the problem. The "
        "evidence that kills it is that the agent's own plan for that run "
        "contains no refund step — the instruction came from a vendor MCP "
        "server's tool description, which is A1.13's risk arriving as an "
        "incident.",

"D4.1": "The nine actions are CyberTravels' actual response levers, from "
        "throttling one agent to rotating the estate's root CA. The pair "
        "worth reading together is deleting a single agent's working "
        "directory — manual, because there is no undo — against forcing "
        "human-in-the-loop on every agent in the estate, which is one flag.",

"D4.2": "The incident is CyberTravels' runaway Workflow Agent, and the "
        "numbers are its containment ladder from A3.9 timed three ways. "
        "Manual takes thirty-four minutes against a breakout time of "
        "twenty-nine, which for CyberTravels means the refunds have already "
        "moved before anybody has decided anything.",

"D5.2": "The control chain is CyberTravels': provenance at ingress (A2.6), "
        "default-deny on the tool call (A3.1), the detection that should have "
        "caught a refund without an approval, and the stop authority that "
        "existed and was never reached. The first absent one is the root "
        "cause; the stop lever nobody pulled is evidence about the detection "
        "in front of it.",

"D5.3": "The six indicators are CyberTravels' own, and two of them do not "
        "come back: refunds carrying an approval, and the time to detect a "
        "scope breach. CyberTravels' detection went from 194 minutes to 118 "
        "against a fifteen-minute target — a real improvement that would "
        "still let the same incident run for two hours.",

"D5.5": "The diff is against CyberTravels' policy, and the expensive line is "
        "the one that says a tool call without provenance is refused rather "
        "than recorded. That will break CyberTravels' vendor integrations, "
        "which is precisely the review that should happen before it ships.",

"E1.13": "The indicators are computed from the CyberTravels repository itself "
         "— the same tree B2.3 scans and A1.1 draws. Five of six report gaps, "
         "and KCI-05 is the honest one: it measures an egress control that "
         "CyberTravels has never built, so it reads zero and will keep reading "
         "zero until A3.7's gateway exists. That is the backlog in the same "
         "units as everything else.",

}
