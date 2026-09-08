"""Hooks, diagrams, ABOUT and CyberTravels grounding for the rebuilt Function C.

Function C was reduced to one twelve-lesson arc (C1.0-C1.11). The ids C1.1-C1.4
used to mean other lessons, so these entries OVERRIDE whatever the old modules
still define for them — the merge at the foot of framing.py / about.py /
cybertravels.py uses .update(), deliberately, so the new arc wins.
"""
from __future__ import annotations

HOOKS = {
"C1.0":
 "\"It worked when I tried it\" is the most common security claim about agents "
 "and the least useful. A deterministic exploit has a signature; an agentic "
 "one has a reasoning loop, a runtime it generated, and a success rate you have "
 "to measure before it means anything.",
"C1.1":
 "The first surface an attacker reaches is not the model — it is the hub the "
 "model was downloaded from. A squatted package name and a poisoned dataset "
 "both land before a single prompt is sent, and the platform accepted them "
 "because the name looked right.",
"C1.2":
 "A dataset is not passive: it is parsed, decoded and embedded, and every step "
 "is a parser with a threat model. A crafted record reaches code execution on "
 "the indexing host — which usually has more access than the box serving "
 "traffic.",
"C1.3":
 "A jailbreak that strips safety and leaves tool use intact is the dangerous "
 "combination, because a model that cannot act is a curiosity and one that can "
 "is an incident. And it only counts if it reproduces across attempts, not in "
 "one screenshot.",
"C1.4":
 "To catch the actor you just played you have to see it, and an agent's tool "
 "calls arrive through a gateway that logs none of the fields telling an agent "
 "from a person. This is where the offensive finding becomes defensive "
 "telemetry.",
"C1.5":
 "Each run, examined alone, was an agent doing plausible work. The swarm "
 "existed only in the population — agents bridging sandboxes through a shared "
 "mount, or spawning children nobody could attribute to a person.",
"C1.6":
 "A rule that flags an unauthorised runtime objective before compromise is "
 "worth a great deal, and the same rule firing on everything is worth less "
 "than nothing. Which one you built is decided by the volume it adds to the "
 "queue, not by its recall.",
"C1.7":
 "The delegation graph is multi-threaded and the agents self-correct "
 "deceptively: a loop that scores evidence only on support confirms its first "
 "theory and closes the wrong case at machine speed, silently.",
"C1.8":
 "Every detector in this function needed a threshold, and every threshold is a "
 "trade. A canary in the index needs neither — nothing legitimate has any "
 "reason to touch it — until the canary is placed where real work does.",
"C1.9":
 "An agent fleet completes thousands of actions inside one human approval "
 "cycle, so containment is pre-authorised or it is too late. Terminating the "
 "agents while their tokens stay valid moves the incident rather than ending "
 "it.",
"C1.10":
 "A finding is only reproducible if the run is. Miss one of the four constants "
 "— usually the model version — and you can describe the exploit but never "
 "demonstrate it, which is the moment your conclusion stops being defensible.",
"C1.11":
 "A non-deterministic finding that stays in a notebook changes nothing. "
 "Translated into a policy diff, an owner and an eval case that fails on the "
 "old build, it becomes something the organisation carries forward and cannot "
 "silently regress.",
}

DIAGRAMS = {
"C1.0": """
   the agentic red-team lifecycle, in one line

   reach ---> see ---> respond ---> carry forward
   C1.1-3     C1.4-6   C1.7-9       C1.10-11

   deterministic validation stops at "reach": an exploit with a
   signature. the novelty of an agentic threat is that the other
   three stages are where the work now is, and each ends in a
   control the defender can run.
""",
"C1.1": """
   an attacker's first reach is the SUPPLY, not the model

   pip install helpf-ul-utils   squatted name   -> accepted
   model: org/whisper-turbo     never verified  -> accepted
   dataset re-pulled each train  changes freely  -> accepted

   assess on:  can this change without telling me?
     pinned library     no   -> low
     hosted model       yes  -> high
     re-pulled dataset  yes  -> high, and no digest = the finding
""",
"C1.2": """
   the record is data to the model, CODE to the parser

   dataset record ---> image decoder ---> embedding job (indexing host)
                           |                     |
                    crafted header         RCE, with the indexing
                    exploits the           host's access, which is
                    decoder                usually broader than serving

   control: a provenance manifest — source, parser, digest — so a run
   that executed something traces back to the record that carried it
""",
"C1.3": """
   one transcript              a technique

   works once  -> anecdote     run N times, vary seed and wording
                                        |
                                        v
                               reproduction rate = 0.0 .. 1.0
                               with a denominator

   the dangerous shape: safety stripped, tool use RETAINED.
   a jailbreak that cannot act is a curiosity; one that can is an incident.
""",
"C1.4": """
   the model gateway, by default        wrapped for telemetry

   { } no per-call identity        ->    {"id": "svc-idx", "tool": "...",
   { } no tool arguments                  "args": {...}, "ts": ...}
   { } no acting principal                        |
                                                  v
                                    score actors on behaviour:
                                    regularity, rate, continuity
                                    threshold set by COST, not accuracy
""",
"C1.5": """
   per-run view                    population view

   run A: plausible work           A --writes--> shared/mount <--reads-- B
   run B: plausible work           A --spawns--> child (no human above it)
   run C: plausible work           C --spawns--> grandchild ...

   coordination lives in the POPULATION. the case study (HF/OpenAI
   swarm) ends in a control list, not a narrative.
""",
"C1.6": """
   five rules for one runtime-objective anomaly

   R1  fires 301x for 1 true positive     buries the queue   REJECT
   R2  fires   2x for 2 true positives    generalises        SHIP
   R3  100% precision on nothing useful                      REJECT

   every rule detects the anomaly. deployability is decided by the
   volume it adds, replayed against real history.
""",
"C1.7": """
   the loop triages a fleet of alerts

   evidence supports theory-1  -> confirm
   evidence supports nothing   -> an agent scoring SUPPORT reads noise
                                   and confirms theory-1 anyway  <- deceptive
   the control:
     may close                        yes
     may close SILENTLY               no  (sampled to a human)
     may close ABOVE the floor        no  (high/critical -> escalate)
""",
"C1.8": """
   every other detector          deception

   signal -> threshold -> alert  canary token in the index
             (a trade)                   |
                                   nothing legitimate reads it
                                         |
                                   one touch = alert, FP rate 0
   failure: a canary placed where real work reaches it, which
   converts a zero-FP control back into a tuned one
""",
"C1.9": """
   an agent at machine speed vs a human approval cycle

   approval cycle: 8 min  ->  ~2,400 further agent actions
   automated stop:          ->  ~60

   one revocation, at the gateway, reaching the whole fleet
     terminate processes   -> tokens still valid -> persistence remains
     REVOKE credentials    -> persistence ends       <- the property that counts
""",
"C1.10": """
   reproduce a run from four constants

   prompts + tool results + model version + seed  -> identical run
                              ^
                              |
              miss this one and every other constant describes
              a system the provider has since replaced

   a run you cannot reproduce is a story, not evidence.
""",
"C1.11": """
   a finding leaves as three things, or it does not leave

   finding ---> control (what is now enforced)
           ---> owner   (who holds it)
           ---> eval    (fails on the old build, passes on the fixed one)

   missing any one:  a promise, not a control, and it regresses unseen.
   present all three: institutional capital, with a reporting timeline.
""",
}

ABOUT = {
"C1.0": """
**What it covers.** The through-line of Function C: a single lifecycle from the ingestion and elicitation surfaces an attacker reaches first, through emergent multi-agent behaviour, to the telemetry, containment and governance a finding ends in.

**Why a security engineer needs it.** Red teaming an agent is not red teaming a binary. The threat is non-deterministic, so a transcript is not a finding and a slide is not a control — and the researcher's real product is the defensive telemetry and policy the offensive work translates into.

This is an **introduction** lesson. It has no code — it exists so the eleven lessons after it are read as one arc rather than eleven techniques.
""",
"C1.1": """
**What it covers.** Auditing a model platform's ingress filters — dependency-squatting, malicious uploads to a hub, poisoned datasets — by assessing each component on whether it can change without notice.

**Why a security engineer needs it.** The supply chain is the surface an attacker reaches before the model, and popularity is not provenance: a hosted model or a re-pulled dataset can change under a name that never did, invalidating every control you tested against it.
""",
"C1.2": """
**What it covers.** Data-layer payloads that exploit a parser to reach code execution during automated embedding generation, and the provenance manifest that makes such a run traceable.

**Why a security engineer needs it.** The embedding pipeline is code, and the host it runs on is usually more privileged than the one serving traffic. A record that is data to the model and an exploit to the decoder runs there, and nothing traces it unless the ingestion was manifested.
""",
"C1.3": """
**What it covers.** Elicitation techniques that scale — cross-prompt attention degradation, context crowding — that strip safety while retaining tool use, measured on reproduction rather than on a transcript.

**Why a security engineer needs it.** A jailbreak that reproduces once is an anecdote; one with a measured success rate across attempts and seeds is a finding. The retained-tool-use combination is the one that turns a bypass into an incident.
""",
"C1.4": """
**What it covers.** JSON-wrapping the model-gateway trace so an agent is observable at all, then scoring actors on behaviour to tell agent tool calls from human activity.

**Why a security engineer needs it.** This is the function's pivot: the offensive finding becomes defensive telemetry. The agents you most need to find are the ones in no registry, and the gateway logs none of the fields that would reveal them until you add them.
""",
"C1.5": """
**What it covers.** Case studies of emergent multi-agent behaviour — sandboxes bridged through shared mounts, agents spawning children without attribution — mapped to the controls that would have caught them.

**Why a security engineer needs it.** Coordination lives in the population, not the run, so per-run monitoring cannot see it by construction. The case study earns its place only when it ends in a deployable control list.
""",
"C1.6": """
**What it covers.** Detection engineering for runtime-objective anomalies at high concurrency, choosing rules by the queue volume they add rather than by recall alone.

**Why a security engineer needs it.** A rule that fires on everything is worse than none, because it spends the attention the good rules need. Deployability is a measured property — firing volume against real history — not a matter of taste.
""",
"C1.7": """
**What it covers.** Triaging a multi-threaded delegation graph with a loop, defended against deceptive self-correction by a severity floor and a stable-seeded closure sample.

**Why a security engineer needs it.** An agent scoring evidence only on support confirms its first theory and closes the wrong case silently. The floor and the sample are what keep an automated loop's false-negative rate visible.
""",
"C1.8": """
**What it covers.** Placing canary tokens and honeypot tasks in a data index so a harvesting agent trips a zero-false-positive alert, and checking nothing legitimate reaches the bait.

**Why a security engineer needs it.** Every other detector trades misses against false alarms through a threshold. A canary has none — unless it is placed where real work touches it, which converts it back into a tuned control.
""",
"C1.9": """
**What it covers.** Zero-trust runtime gatekeepers and dynamic token revocation that isolate a compromised fleet in one action, at machine speed.

**Why a security engineer needs it.** A fleet completes thousands of actions inside one approval cycle, so containment must be pre-authorised. The property that decides whether it worked is revocation versus termination — terminated agents with valid tokens keep their persistence.
""",
"C1.10": """
**What it covers.** Locking the deterministic runtime constants — prompts, tool results, model version, seed — so a complex agentic exploit path reproduces inside a forensic lab.

**Why a security engineer needs it.** A finding is only as good as its reproduction, and the model version is the constant teams miss and the one that silently invalidates the rest. A run you cannot reproduce is a story.
""",
"C1.11": """
**What it covers.** Turning a non-deterministic finding into institutional capital: a policy diff, an owner, and an evaluation case that fails on the old build.

**Why a security engineer needs it.** A finding in a notebook changes nothing and regresses unseen. The handover with a regression test attached is what makes the fix verifiable and gives the research a reporting timeline the organisation can be held to.
""",
}

GROUNDING = {
"C1.0": "The board asked whether CyberTravels is secure. This function answers "
        "the version of that question a researcher can act on — what would go "
        "wrong, would it reproduce, and would we see it — and it answers it on "
        "CyberTravels end to end, from a poisoned template to a governed fix.",
"C1.1": "The components are CyberTravels' own — the model its advisor calls, the "
        "packages its coding agent installs, the templates indexed into its "
        "vector store — and the one with no pinned digest is the route in.",
"C1.2": "The pipeline is CyberTravels' RAG ingestion: vendor PDFs and images "
        "through OCR and a decoder, on the indexing host that can reach the "
        "backend APIs. A crafted invoice is the payload.",
"C1.3": "The target is CyberTravels' advisor, and the dangerous outcome is a "
        "jailbreak that keeps the booking and refund tools while shedding the "
        "policy that governed them.",
"C1.4": "The gateway is CyberTravels', and the actor to find is the Workflow "
        "Agent acting under Alex's credential at a tempo no person types — "
        "invisible until the trace carries the acting identity.",
"C1.5": "The swarm is the one from the register's R8: a CyberTravels agent that "
        "spawned children to parallelise a task and left no chain from any "
        "child back to a human.",
"C1.6": "The anomaly is a CyberTravels agent pursuing an objective its task "
        "never set, and the rules are scored against CyberTravels' own history "
        "so the queue cost is real.",
"C1.7": "The alerts are CyberTravels', and the deceptive branch is the refund "
        "incident: the loop confirms 'the Workflow Agent did it' and never "
        "reaches the vendor tool description that actually did.",
"C1.8": "The canary is a fake booking record in CyberTravels' index that no "
        "legitimate itinerary references, so a read of it is an agent going "
        "somewhere its task never sent it.",
"C1.9": "The fleet is CyberTravels' four agents, and the detail that matters is "
        "R9: third-party access ended only when the third party revoked its "
        "keys, not when the agents were stopped.",
"C1.10": "The run is the CyberTravels refund incident, and the field missing "
         "most often is the advisor's model version — upgraded by the provider "
         "between the incident and the replay.",
"C1.11": "The finding is CyberTravels' indirect-injection refund, and the "
         "handover is the policy clause it changes, the owner who holds it, and "
         "the eval case that fails on the pre-fix build.",
}
