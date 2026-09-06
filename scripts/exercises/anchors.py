"""What each Function E lesson contributes to, or takes from, the indicator in E1.1.

Function E was written as three separate arguments — a control framework, a
regulatory map, and a programme — and each was internally coherent. What it did
not have was a unit. E1.1 supplies one: a **key control indicator**, computed
from the estate, with a denominator and a target written before it is measured.

So every other lesson in E states its relationship to that unit in one line,
rendered right under the concept. The line is not decoration: reading the first
draft of each anchor against its own lesson body found five of twenty-nine
describing something the lesson does not contain — a column that is not there,
a sequencing rule the lesson argues against, four metrics in place of the
lesson's five. That is the point of making a spine explicit, and it is also the
warning: the gate below checks that an anchor exists and renders, and cannot
check that it is true.

E1.0 and E1.1 are the two exceptions, and they are exceptions for the same
reason: E1.1 defines the unit and E1.0 introduces the function that is told in
it, so an anchor on either would restate the concept above it.

`check_lessons.py` fails the build if any other Function E lesson has no anchor,
so the next lesson added to E has to say where it sits before it can ship.
"""
from __future__ import annotations

ANCHORS: dict[str, str] = {

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
 "before the incident or are guessing at during it. D5.3 re-measures the "
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
 "recovery indicators — the same ones D5.3 re-reads after a fix. Prevention "
 "has no honest indicator on a system that changes weekly, which is why the "
 "maturity model does not use one.",

}
