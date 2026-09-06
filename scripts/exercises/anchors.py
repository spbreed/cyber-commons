"""Where each Function D and Function E lesson sits on its function's spine.

Two functions are long arguments rather than collections, and each is told in
one unit. A lesson that does not say which part of that unit it moves can be
internally coherent, read perfectly well on its own page, and belong to no
argument at all — which is a failure nothing else in the build can see.

**Function E's unit is a measurement.** E1.1 defines a **key control
indicator**: computed from the estate, with a denominator, and a target written
before it is measured. Every other lesson in E either produces one, supplies its
denominator, sets its target, decides who owns it, or presents it as evidence to
somebody outside the organisation.

**Function D's unit is an interval.** D1.0 defines five of them — discover,
detect, understand, contain, recover — one per chapter, between an agent doing
something it should not and the control that stopped it being back at target.
Every other lesson in D shortens one of those intervals, or spends one
deliberately to buy something else. The second kind matters as much as the
first: admission rules and human-in-the-loop runbooks both make an interval
longer on purpose, and saying so is more honest than pretending everything is an
improvement.

The line renders right under the concept, and it is not decoration: reading the
first draft of each E anchor against its own lesson body found five of
twenty-nine describing something the lesson does not contain — a column that is
not there, a sequencing rule the lesson argues against, four metrics in place of
the lesson's five. That is the point of making a spine explicit, and it is also
the warning: the gate checks that an anchor exists and renders, and cannot check
that it is true.

D1.0 and E1.1 carry no anchor, because they define the unit. E1.0 carries none
either — it introduces the function that is told in it, so an anchor would
restate the concept directly above it.

`check_lessons.py` fails the build if any other lesson in D or E has no anchor,
so the next lesson added to either has to say where it sits before it can ship.
"""
from __future__ import annotations

ANCHORS: dict[str, str] = {

# ==========================================================================
# Function D · the five intervals defined in D1.0
# ==========================================================================

# ---- D1 · discover — the interval before anything is visible --------------
"D1.1":
 "**Anchor → D1.0.** Every interval in D1.0's table is measured on telemetry, "
 "so this lesson sets the floor for all five: on data that was never emitted, "
 "discover does not take a long time — it never completes. The retention "
 "decision is the same argument, backwards: it fixes how far into the past an "
 "investigation is allowed to reach.",

"D1.2":
 "**Anchor → D1.0.** For an agent nobody registered, behaviour is the only "
 "clock running. Regularity, rate and continuity are what start the discover "
 "interval at all — and the error analysis is the honest part, because a "
 "classifier that is confidently wrong starts it on the wrong actor.",

"D1.3":
 "**Anchor → D1.0.** Intelligence shortens the *detect* interval before the "
 "incident rather than during it, and only by becoming a rule. That is why the "
 "single measure is detections produced: a narrative about adversary trends "
 "moves no interval, however well written.",

"D1.4":
 "**Anchor → D1.0.** Drift lengthens every interval at once, silently. The "
 "model was upgraded, a prompt was edited, and the control is now unevidenced "
 "against behaviour that no longer exists — so the discover clock restarts "
 "without anybody starting it.",

"D1.5":
 "**Anchor → D1.0.** Hunting is the only pass that shortens discover for "
 "behaviour no rule was written for, and it spends real time to do it. Hence "
 "the scoring: a hypothesis matching fourteen runs to find two, because twelve "
 "are the nightly batch, has bought nothing.",

# ---- D2 · detect — from visible to an alert -------------------------------
"D2.1":
 "**Anchor → D1.0.** This is the detect interval for the agent itself, and the "
 "classic baselines leave it at infinity. Two countries in an hour is an "
 "incident for a person and multi-region routine for an agent; three hundred "
 "file reads a minute is an incident for a person and idle for an agent; "
 "03:00 is suspicious for a person and meaningless for an agent.",

"D2.2":
 "**Anchor → D1.0.** A different subject is a different clock. Workload-layer "
 "detection does not fire late on a platform compromise — it does not fire at "
 "all, which is why these are separate rules, on separate data, with separate "
 "owners.",

"D2.3":
 "**Anchor → D1.0.** This shortens the gap between *a rule is needed* and *a "
 "rule exists*, which is a real interval and not the one that matters most. "
 "What it cannot shorten is the decision to ship, because the cost that "
 "decides it — analyst trust — is not in the telemetry.",

"D2.4":
 "**Anchor → D1.0.** The fastest route to a rule, and the one most likely to "
 "lengthen every other interval instead. A rule that fires on 21% of benign "
 "traffic spends the attention the rest of the queue needs, so the benign "
 "corpus is what decides, not the incident.",

"D2.5":
 "**Anchor → D1.0.** The only detector whose interval is the moment of touch. "
 "Every other one in the chapter trades detect time against false positives "
 "through a threshold; a canary has no threshold to trade, because nothing "
 "legitimate has any reason to touch it.",

# ---- D3 · investigate — from an alert to a conclusion ---------------------
"D3.1":
 "**Anchor → D1.0.** The understand interval stops being one analyst's reading "
 "speed and becomes the loop's, which moves the work rather than removing it: "
 "deciding what the loop may conclude, what it may do unsupervised, and which "
 "sample of the rest gets read.",

"D3.2":
 "**Anchor → D1.0.** This one **spends** the interval on purpose. Bounding the "
 "investigator before it runs is slower than handing it broad read, and broad "
 "read across the estate is frequently what the incident was — so the time buys "
 "not having a second one.",

"D3.3":
 "**Anchor → D1.0.** Acting identity, scopes held and the delegation chain are "
 "what let the interval end at all. Without them triage does not take longer; "
 "it stops being triage, because reading `.env` is alarming for one agent and "
 "routine for another and nothing on the alert says which.",

"D3.4":
 "**Anchor → D1.0.** Three responder instincts each burn the interval: "
 "disabling an account that does not stop an already-issued bearer token, "
 "interviewing a person who was asleep, and assuming one actor when there were "
 "three in a chain.",

"D3.5":
 "**Anchor → D1.0.** This shortens the interval and can end it in the wrong "
 "place at the same time. A model correlates thousands of log lines in seconds, "
 "and will produce a fluent narrative from logs that never supported one — "
 "which is harder to challenge than an obviously incomplete one, so a fast "
 "conclusion is not the same as a finished one.",

"D3.6":
 "**Anchor → D1.0.** An agent that scores evidence only on support never ends "
 "the interval; it spends the whole incident confirming step one. Refutation is "
 "what makes the investigation terminate, and the abandoned branch stays in the "
 "trace so a reviewer can see it did.",

"D3.7":
 "**Anchor → D1.0.** Scope decides what *understood* covers. Following the last "
 "actor rather than the delegation graph ends the interval early and wrong, and "
 "because authority narrows down the chain the earlier actors had more access — "
 "so the undercount grows with depth.",

"D3.8":
 "**Anchor → D1.0.** For a coordinated fleet, per-run monitoring never ends the "
 "interval — not because it is tuned badly but because of what it looks at. "
 "Every run examined alone was plausible work. Moving where the monitoring sits "
 "is the only thing that changes this one.",

# ---- D4 · respond — from a conclusion to the actor stopped ----------------
"D4.1":
 "**Anchor → D1.0.** This fixes the contain interval **before** the incident, "
 "from two properties of the action rather than from whoever wrote the runbook. "
 "Chosen per runbook, the blast radius of your response is unknown until the "
 "response fires.",

"D4.2":
 "**Anchor → D1.0.** Three tiers are three contain intervals at three different "
 "costs of being wrong: 14 seconds at eight errors per hundred, 2,072 seconds "
 "at 0.2, against a measured breakout time of 1,740. The manual tier is a risk "
 "decision, not the safe one.",

"D4.3":
 "**Anchor → D1.0.** The interval where the arithmetic is brutal. An agent at "
 "300 actions a minute takes about 2,400 further actions inside an eight-minute "
 "approval cycle and roughly 60 under automated containment — and revoking a "
 "non-human identity is not revoking a person, which is what makes it safe.",

"D4.4":
 "**Anchor → D1.0.** This is the interval itself, measured end to end rather "
 "than estimated. Five questions decide whether you have it, and each needs a "
 "name or a number: an untimed stop authority is an intention with a runbook "
 "attached.",

"D4.5":
 "**Anchor → D1.0.** Contain, when the unit is the fleet — and the detail that "
 "decides whether the interval ended at all. Terminating agents whose "
 "credentials stay valid leaves the persistence in place and moves the incident "
 "rather than ending it.",

# ---- D5 · recover — from stopped to the control back at target ------------
"D5.1":
 "**Anchor → D1.0.** Recovery starts from a run you can reproduce. Miss one of "
 "the four fields — most often the model version — and you can describe what "
 "happened but never demonstrate it, which is the moment the interval stops "
 "being yours to close.",

"D5.2":
 "**Anchor → D1.0.** A root cause naming a person ends no interval, because "
 "nothing in it can be built or measured. Naming the control that should have "
 "caught this gives the next two lessons something to change and something to "
 "re-read.",

"D5.3":
 "**Anchor → D1.0.** The fix lands at a layer, and the layers that pass through "
 "no process are exactly the ones adjusted at 2am. That is how the *next* "
 "incident's discover interval starts before anyone knows there is one.",

"D5.4":
 "**Anchor → D1.0.** This is where recover actually ends: an indicator back at "
 "target, not a closed ticket. CyberTravels' detection interval went from 194 "
 "minutes to 118 against a 15-minute target — a real improvement that every "
 "system not re-measuring would record as remediated.",

"D5.5":
 "**Anchor → D1.0.** Recovery that changes only what is deployed leaves the "
 "policy that permitted the incident intact, so the next system built under it "
 "reproduces the conditions. The diff is what stops the same intervals being "
 "measured again next quarter.",

"D5.6":
 "**Anchor → D1.0.** The one interval you neither own nor can shorten. It "
 "starts at awareness rather than confirmation, does not pause while you "
 "establish who acted, and containing in an hour buys none of it back.",

# ==========================================================================
# Function E · the key control indicator defined in E1.1
# ==========================================================================

# E1.0 and E1.1 carry no anchor. E1.1 defines the unit and E1.0 introduces the
# function that is told in it, so an anchor on either would restate the concept
# printed directly above it. `check_lessons.py` exempts exactly those two.

# ---- E1 · the framework that produces the indicators ---------------------
"E1.2":
 "**Anchor → E1.1.** The inventory is the **denominator**. Every indicator is "
 "a share — of agents, of tool calls, of handlers — and a share whose "
 "denominator is unknown is a count wearing a percentage sign. An incomplete "
 "inventory does not make your indicators wrong; it makes them unfalsifiable.",

"E1.3":
 "**Anchor → E1.1.** Risk tiering sets the **target**. The same indicator "
 "carries a different threshold on a tier-1 agent that moves money than on a "
 "tier-3 one that summarises documents, and E1.1's rule — the target is "
 "written before the measurement — is only meetable once the tier exists.",

"E1.4":
 "**Anchor → E1.1.** Control mapping is where an indicator gets its subject. "
 "A mapped control with no indicator behind it is the state E1.1 calls "
 "unevidenced: it is neither passing nor failing, and most GRC tooling will "
 "render it green.",

"E1.5":
 "**Anchor → E1.1.** An eval result **is** an indicator reading — the sample "
 "size is its denominator, the pass bar is its target, and the expiry is what "
 "stops it aging into a claim. Read it that way and the conformance/accuracy "
 "split stops being a presentation choice: conformance has no denominator "
 "worth quoting, so it is not an indicator at all.",

"E1.6":
 "**Anchor → E1.1.** Operating and outcome guardrails need different "
 "indicators, and confusing them is the most common way a control looks "
 "measured and is not. An operating indicator says the constraint was applied; "
 "an outcome indicator says it worked.",

"E1.7":
 "**Anchor → E1.1.** This is the machinery that re-measures. E1.1 argues that "
 "a control tested six months ago is unevidenced rather than passing; "
 "continuous verification is what shortens that window, and the freshness "
 "window per control is itself an indicator.",

"E1.8":
 "**Anchor → E1.1.** These are the indicators you **cannot compute yourself**. "
 "For a third-party model the estate holds no source to measure, so the "
 "indicator becomes an attestation with an expiry — which is a weaker "
 "instrument, and worth naming as one rather than scoring it the same.",

"E1.9":
 "**Anchor → E1.1.** A retrain, a fine-tune or a re-index **invalidates a "
 "reading**. Lifecycle governance is what tells the indicator set that its "
 "last measurement is stale, which is the difference between continuous "
 "assurance and a dashboard showing last quarter.",

"E1.10":
 "**Anchor → E1.1.** One indicator, five readers, five different questions. "
 "Legal reads a containment number as liability, model risk reads it as "
 "fitness, privacy reads it as exposure. Publishing the reading is not the "
 "same as it being consumed, and the question nobody asked is the one no "
 "indicator was built for.",

"E1.11":
 "**Anchor → E1.1.** Model risk management arrived at the same answer decades "
 "earlier: SR 11-7's *ongoing monitoring* is a KCI programme in older "
 "vocabulary. The lineage matters because it is the argument that convinces a "
 "risk function this is not new.",

"E1.12":
 "**Anchor → E1.1.** The seams are where an indicator has two consumers and no "
 "owner, so it is computed twice, differently, and the two numbers are used to "
 "argue with each other rather than with the estate.",

"E1.13":
 "**Anchor → E1.1.** This is E1.1 executed. Six indicators, computed from the "
 "CyberTravels tree at run time, reported as gaps with named mitigations "
 "rather than as a score.",

# ---- E2 · the indicators as regulatory evidence ---------------------------
"E2.1":
 "**Anchor → E1.1.** The reason one control set can satisfy several regimes is "
 "that regimes overlap on **evidence**, not on wording. An indicator computed "
 "once is quotable to each of them; a control described three ways is not.",

"E2.2":
 "**Anchor → E1.1.** Horizontal regulation asks whether a system is robust, "
 "overseen and documented. Each of those becomes a different indicator, and "
 "agentic deployment changes which one is hardest — oversight, because the "
 "action completes before a human sees it.",

"E2.3":
 "**Anchor → E1.1.** The framework spine is where indicators **attach**. Pick "
 "the spine first and each regulator's overlay maps onto indicators you "
 "already compute; pick the regulator first and you rebuild the set per "
 "jurisdiction.",

"E2.4":
 "**Anchor → E1.1.** A sector overlay mostly re-targets indicators you "
 "already compute — the same containment number against a stricter threshold. "
 "The exception is exit strategy, which no horizontal regime asks for and "
 "which almost nobody can currently measure at all.",

"E2.5":
 "**Anchor → E1.1.** Privacy indicators measure paths rather than outcomes — "
 "where inference ran, what retrieval touched, how long a trace was kept. They "
 "are computable, and they are the ones most often asserted instead.",

"E2.6":
 "**Anchor → E1.1.** A disclosure clock runs on facts you either measured "
 "before the incident or are guessing at during it. D5.4 re-measures the "
 "indicators after the fix; this lesson is why the pre-incident reading has to "
 "have existed at all.",

"E2.7":
 "**Anchor → E1.1.** Documentation that survives supervision is largely "
 "**indicator readings with dates on them**. A narrative describing a control "
 "is what supervision fails; a series of measurements is what it accepts.",

"E2.8":
 "**Anchor → E1.1.** The delegation chain is an indicator in its own right: "
 "the share of autonomous actions whose full chain — who authorised, on whose "
 "behalf, under what scope — can be reconstructed. Anything below 1.00 is the "
 "part you cannot audit.",

"E2.9":
 "**Anchor → E1.1.** A regulator conversation goes differently when bounded "
 "autonomy is presented as numbers that were computed rather than as a "
 "description of intent. Bring the indicator, its denominator, and the gaps "
 "you already know about.",

# ---- E3 · the indicators as a programme -----------------------------------
"E3.1":
 "**Anchor → E1.1.** Translating risk upward is mostly choosing which three "
 "indicators a board sees. Pick them from the set that already exists, or the "
 "board gets a number invented for the slide and nobody can re-compute it.",

"E3.2":
 "**Anchor → E1.1.** Governing autonomy rather than tools means the policy "
 "attaches to indicator thresholds — what an agent may do without asking is a "
 "function of measured containment, not of which vendor supplied it.",

"E3.3":
 "**Anchor → E1.1.** The order is a dependency order, not a gap-size order, "
 "and the indicators are why. Inventory first because it is every other "
 "indicator's denominator; evaluation late because a measured system nobody "
 "can switch off scores well and cannot be stopped. Sequencing on whichever "
 "number looks worst inverts it.",

"E3.4":
 "**Anchor → E1.1.** Org design decides who can actually compute each "
 "indicator. If identity owns the control plane and nobody owns the "
 "measurement of it, the indicator exists on a slide and nowhere else.",

"E3.5":
 "**Anchor → E1.1.** These **are** the indicators, at the level a CISO "
 "reports — exposure, likelihood, assurance, coverage, speed. The property "
 "that qualifies each of them is E1.1's: it is computed rather than assessed, "
 "so it degrades on its own. A number that stays flat under neglect is "
 "measuring activity.",

"E3.6":
 "**Anchor → E1.1.** Autonomy promotion as an earned event needs named "
 "evidence, and named evidence is an indicator crossing a threshold. Without "
 "one, 'yes with conditions' becomes 'yes' at the next review.",

"E3.7":
 "**Anchor → E1.1.** The build curve is unglamorous early precisely because "
 "indicators are: quarter one produces the denominator and nothing to demo. "
 "The capability being hired for is turning a control into something "
 "computable, which is what separates operating a GRC tool from measuring an "
 "estate.",

"E3.8":
 "**Anchor → E1.1.** Resilience is measured by the containment, detection and "
 "recovery indicators — the same ones D5.4 re-reads after a fix. Prevention "
 "has no honest indicator on a system that changes weekly, which is why the "
 "maturity model does not use one.",

}
