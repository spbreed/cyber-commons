# step:file D1.0
"""The red-team lifecycle — a campaign, not an anecdote.

Function B reviewed CyberTravels' code. This package attacks the running
system, and the thing it builds first is not an attack. It is the arithmetic
that decides whether an attack result means anything.

**The failure this whole chapter is organised against is the anecdote.** A
technique worked. It worked once, on one target, on one model, in one session,
and it is now in a slide with the word "critical" beside it. Nobody knows the
rate, nobody re-ran it, and when it stops working nobody will notice — because
there was never a number to move.

Three things turn a result into a finding, and every lesson here adds one:

* **a stated criterion**, decided before the run. "Did it work" is not a
  criterion; "the agent issued a refund against a booking the caller does not
  own" is.
* **a rate with an interval**, over enough trials to distinguish 9/10 from
  6/10 — which, at ten trials, you cannot.
* **an ablation**, so the number separates the *model* effect from the
  *harness* effect. Most published jailbreak rates are harness rates.

And one thing turns a finding into something that outlives the engagement:
a handoff that ends in a control, an eval case and a detection (D1.11).

    D1.0  campaign.py    cases, trials, ASR with an interval, the ablation
    D1.1  ingestion.py   what CyberTravels ingests, and from whom
    D1.2  ingestion.py   weaponising that path
    D1.3  elicitation.py a technique's reproduction rate, not its best run
    D1.4  actor.py       telling the agent from the person, in the trace
    D1.5  swarm.py       many runs, and what is only visible across them
    D1.6  swarm.py       detections that survive the volume
    D1.7  swarm.py       triage with a floor
    D1.8  deception.py   canaries whose alert cannot be a false positive
    D1.9  containment.py the kill switch, and what it does not stop
    D1.10 forensics.py   can the run be reconstructed from the record
    D1.11 handoff.py     finding -> eval case + control + detection

Nothing here is a new attack. Every technique it runs is one Function A named
and Function B found; what is new is that the result carries a denominator.
"""

# What a campaign has to state before it starts, in the order it has to state
# them. Kept as data because a campaign that decides its criterion after
# seeing the results has measured nothing, and the only defence against that
# is writing the criterion down first.
PRECONDITIONS = (
    ("criterion", "what counts as success, decided before the first trial"),
    ("trials", "how many, decided from the difference worth detecting"),
    ("benign_cases", "what must NOT trip it, or the rate is meaningless"),
    ("ablation", "what the harness contributes with the model held constant"),
    ("scope", "C2.10's boundary — this package attacks a replica"),
)
