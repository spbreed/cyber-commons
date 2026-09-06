"""Hooks, diagrams and chapter bridges for the lessons added with the D restructure.

Kept beside `framing.py` rather than inside it: that file is already long, and
these eleven arrived as one set. `framing.py` merges them, so there is still one
HOOKS and one DIAGRAMS as far as the build is concerned.
"""
from __future__ import annotations

HOOKS: dict[str, str] = {

"A0.2":
 "A prompt-injection finding filed as a NIST function tells a regulator "
 "nothing and a developer less. The four vocabularies in this field answer "
 "four different questions, and picking the wrong one is how a real finding "
 "becomes a paragraph nobody actions.",

"D1.5":
 "The alert queue has been quiet for a fortnight and nobody believes it. "
 "Hunting is the pass that finds what no rule was written for — and the "
 "hypothesis that feels most obviously right is usually a description of "
 "the overnight batch doing its job.",

"D2.2":
 "You have just reconstructed an incident and the rule almost writes itself. "
 "That is the problem: every rule you could write catches the incident, "
 "because you wrote it from the incident. What decides whether it ships is "
 "the traffic it fires on when nothing is wrong.",

"D3.2":
 "The investigating agent is granted broad read across production so it can "
 "find the problem. Broad read across production is frequently what the "
 "problem was. Admission rules are how the response avoids becoming the "
 "second incident.",

"D3.3":
 "An agent forms a hypothesis at step one and spends the rest of the "
 "incident finding evidence for it. The evidence that should have stopped it "
 "supports nothing at all — which is exactly why an agent scoring only "
 "support reads it as noise and carries on.",

"D4.1":
 "Every runbook in the drawer picked its own automation tier, chosen by "
 "whoever wrote it on the day. So the blast radius of your incident response "
 "is unknown until the response fires, which is the worst moment to find out.",

"D4.2":
 "Fully automated contains in fourteen seconds and is wrong eight times in a "
 "hundred. Manual is almost never wrong and takes thirty-four minutes, "
 "against a breakout time of twenty-nine. Neither of those is the safe "
 "option; they fail differently.",

"D5.2":
 "The postmortem says the on-call engineer missed the alert. It is true, it "
 "is useless, and it will be true again next quarter about somebody else. A "
 "root cause names a control, or it names nothing that can be built.",

"D5.3":
 "The ticket is closed and the incident is marked remediated. Re-measure the "
 "indicators it moved and two of them never came back — including the "
 "detection time, which improved from 194 minutes to 118 and is still eight "
 "times its target.",

"D5.5":
 "The incident produced a fix to what is deployed and no change at all to "
 "what is allowed. So the next system built under the same policy "
 "reproduces the same conditions, and the postmortem sits in a folder being "
 "correct.",

"E1.13":
 "The register says the control is in place. Nobody has computed it from the "
 "estate, so the first evidence either way will be an incident. An indicator "
 "you cannot calculate today is a sentence in a policy wearing a number's "
 "clothes.",

}

DIAGRAMS: dict[str, str] = {

"A0.2": """
   THE QUESTION                       THE VOCABULARY THAT ANSWERS IT

   "what can go wrong in this      -> OWASP LLM Top 10      LLM01..LLM10
    feature?"                         OWASP Agentic Top 10  T1..T15

   "what did the attacker do?"     -> MITRE ATLAS           tactics

   "how do we organise to          -> NIST AI RMF           GOVERN  MAP
    find out?"                                              MEASURE MANAGE

   "what must we be able          -> EU AI Act             Art. 9, 12,
    to show, and by when?"                                  14, 15, 26 ...

   one control usually needs one of each: a threat it addresses, a tactic
   it frustrates, a function it belongs to, an obligation it discharges
""",

"D1.5": """
   DETECTION                          HUNTING

   behaviour  ->  rule  ->  alert     hypothesis
   (already understood)                    |
                                           v
                                      run over stored traces
                                           |
                          +----------------+----------------+
                          v                v                v
                      promote            tune            discard
                   (with an FP rate)  (fires on the      (describes
                                       job itself)        nothing)

   the middle branch is where quarters go: a hypothesis that matches
   fourteen runs to find two, because twelve are the nightly batch
""",

"D2.2": """
   incident trace
        |
        v
   +----------------------+     every candidate catches the incident,
   | candidate rules      |     so that cannot be the selection test
   |   any refund         |
   |   refund w/o approval|
   |   refund on BK-772   |
   +----------+-----------+
              |
              v
       benign corpus  (must contain LEGITIMATE refunds)
              |
      +-------+--------+---------------+
      v                v               v
   21% FP           0% FP           0% FP
   buries the       generalises     matches this
   queue            AND quiet       incident only
   REJECT           SHIP            REJECT
""",

"D3.2": """
   investigation class: agent-misuse
   +--------------------------------------------------+
   |  sources   agent.traces  gateway.logs  tool.audit |   allowlist
   |  fields    NOT payment_card, passport_no,         |   denied
   |            message_body                           |
   |  volume    <= 5000 rows                           |   cap
   +--------------------------------------------------+
              |
      query --+--> admitted   -> runs, logged
              |
              +--> refused    -> logged WITH the query text
                               -> a human can grant it deliberately

   the volume cap is the one people leave out: same source, same fields,
   400 rows is an investigation and 90,000 is a copy
""",

"D3.3": """
   evidence        supports?        the plan

   1 refund at 03:14   misuse|theft   agent-misuse
   2 agent's session   misuse         agent-misuse
   3 SPIFFE, no human  misuse         agent-misuse
   4 plan has no       --- nothing -- agent-misuse   <- refutes, supports
     refund step                                        nothing, and an
                                                        agent scoring only
                                                        support skips it
   5 vendor tool desc  injection      REPLAN -------> indirect-injection
   6 desc changed      injection      indirect-injection

   the abandoned branch stays in the trace: a reviewer must see that
   agent-misuse was considered and dropped, not that it was never raised
""",

"D4.1": """
                    reversible without a human?
                    yes                     no
                +---------------------+-------------------+
   one agent    |  AUTOMATED          |  MANUAL           |
                +---------------------+-------------------+
   one tenant   |  HUMAN IN THE LOOP  |  MANUAL           |
                +---------------------+-------------------+
   the estate   |  HUMAN IN THE LOOP  |  MANUAL           |
                +---------------------+-------------------+

   reversibility outranks radius, and that ordering IS the policy:
     delete one agent's workdir   one agent, no undo    -> manual
     force HITL on every agent    whole estate, a flag  -> HITL
""",

"D5.2": """
   control chain for INC-2026-114        status

   A2.6  provenance at ingress           absent   <- first absent = ROOT
   A3.1  default-deny on the tool call   wrong scope
   D2.1  detection: refund w/o approval  absent   <- contributing
   D1.3  drift on vendor tool descs      absent   <- contributing
   D4.4  stop authority in the window    PRESENT  <- and never reached

   a control that exists but is never reached is not a mitigating factor.
   it is evidence about the detection in front of it.

   statement test:  names a control -> usable
                    names a person  -> rejected, however true
""",

"D5.3": """
   kci        healthy   during     after fix    verdict

   KCI-01      1.00      0.41       1.00        restored
   KCI-02      1.00      0.00       1.00        restored
   KCI-03      1.00      0.86       0.94        NOT restored
   KCI-04      9 min     194 min    118 min     NOT restored
   KCI-05      1.00      0.97       1.00        restored

                                    ^
                                    |
              the incident record would have said "remediated"
              for all five. improvement is not restoration.
""",

"E1.13": """
   cybertravels/  (read at run time, not from a register)
        |
        v
   +--------------------------------------------------------+
   | KCI-01  handlers comparing an owner    == 1.00   0.29 X |
   | KCI-02  HTTP calls verifying TLS       == 1.00   0.00 X |
   | KCI-03  no eval of caller text            == 0   1.00 X |
   | KCI-04  no shell w/ model argument        == 0   1.00 X |
   | KCI-05  egress control present            == 1   0.00 X |
   | KCI-06  no credential literal             == 0   0.00 v |
   +--------------------------------------------------------+
        |                                              |
        v                                              v
   gap  -> the lesson that closes it        one PASSING indicator,
           (A2.4, B2.7, A3.4, A3.7)         so the set can be seen
                                            to discriminate
""",

}

# D4.2 and D5.5 reuse the shape of their neighbours rather than inventing one.
DIAGRAMS["D4.2"] = """
   one incident, three tiers

   tier                 decide      contain      wrong / 100
   automated                1s          14s              8.0
   human in the loop      240s         253s              1.2
   manual                1800s        2072s              0.2
                                        ^
                        breakout time is 29 min = 1740s
                        manual contains AFTER the attacker finished

   deliberately no fourth column ranking these: seconds of exposure and
   wrongly-contained agents are different units, and any single score
   has an exchange rate hidden in it that somebody chose
"""

DIAGRAMS["D5.5"] = """
   root cause record
        |
        v
   +--------------------------------------------------------------+
   | clause                          from -> to            why     |
   | mcp.vendor.tool_descriptions    trusted -> pinned     the     |
   | tool.call.provenance            when present ->       altered |
   |                                 required, else refuse desc    |
   | payments.refund.approval        >500 -> every amount  KCI-03  |
   +--------------------------------------------------------------+
        |
        v
   NOT addressed: KCI-04
   the policy already required 15 minutes. the control was never built
   to meet it -> engineering item, named here so it is not lost between
   the two functions
"""

BRIDGES: dict[str, dict[str, str]] = {

"D1": {
 "gained": "You can collect agent telemetry, tell an agent's tempo from a "
           "human's, watch for behavioural drift, and run a hypothesis-first "
           "hunt that reports precision rather than anecdotes.",
 "gap": "Everything you found is a finding in a notebook. Nothing you have "
        "built fires on its own tomorrow, and a hunt that is not promoted to "
        "a detection is a quarter spent proving something once.",
 "next": "Chapter D2 is detection engineering: turning what the hunt found "
         "into rules, generating them from incidents, and measuring the "
         "false-positive rate before any of them ship.",
},

"D2": {
 "gained": "You can write detections for agent behaviour, generate them from "
           "a reconstructed incident, score them against benign traffic, and "
           "cover the agent platform itself rather than only its output.",
 "gap": "A detection fires. It does not investigate. You have no way yet to "
        "let an agent pull the evidence together without granting it the "
        "access the incident was about.",
 "next": "Chapter D3 is investigation: admission rules on what the "
         "investigating agent may touch, plans that survive contradiction, "
         "and correlation across a fleet.",
},

"D3": {
 "gained": "You can scope an agentic incident, bound what the investigating "
           "agent may read, correlate across a fleet, and read a trace where "
           "the investigation changed its mind and said so.",
 "gap": "You know what happened and you have not stopped it. Every lever you "
        "might pull is still chosen in the moment by whoever is awake.",
 "next": "Chapter D4 is response: the remediation policy that decides what "
         "may happen without asking, and the three runbook tiers that policy "
         "produces.",
},

"D4": {
 "gained": "You can classify a remediation action on reversibility and blast "
           "radius, derive its runbook tier from policy rather than "
           "confidence, contain at machine speed and stop a fleet.",
 "gap": "The incident is contained and nothing has been learned. No control "
        "has been named, no indicator re-measured, and the policy that "
        "allowed it is exactly as it was.",
 "next": "Chapter D5 closes the loop: the root cause record, validating the "
         "fix against the KCIs, and proposing the policy change with the "
         "incident attached as evidence.",
},

"D5": {
 "gained": "You can close an incident with a root cause that names a control, "
           "prove the fix by re-measuring the indicators it claimed to "
           "restore, and propose the policy change as a reviewable diff.",
 "gap": "All of it runs inside your own organisation. Nothing here tells you "
        "which of these controls a regulator will ask for, on what date, or "
        "what evidence they will accept.",
 "next": "Function E is governance: the framework, the obligations, and the "
         "programme that has to answer for all five phases you have just "
         "built.",
},

}
