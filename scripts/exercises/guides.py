"""Course-guide narrative for Functions B to F — the teaching notes only.

**How this differs from `guide_a.py`, and why it has to.** Function A has
sixteen lessons and its guide carries a hand-verified expected output for every
one, because every one was run and the printed result copied down. B to F are
133 lessons. Hand-verifying 133 outputs is not something this file can honestly
claim to have done, and writing a plausible one for each would be the exact
failure the whole curriculum is about: text with the right shape and no
relationship to what the command does.

So the split is different, and the pages say so:

* **Per chapter, hand-written here.** The arc, what the chapter proves, where a
  reader gets stuck, what to do about it. Thirteen chapters is a tractable
  amount of judgement to write down.
* **Per lesson, derived by `build_guide.py`.** Risk and Control and the lab
  line from `curriculum.json`, Day 0/1/2 from `days.py`, the measure from
  `metrics.py`, the anchor from `anchors.py`, and — instead of an output
  somebody typed — the audit skill's own **committed example run** and the
  top-level keys of its **declared output contract**, both read out of
  `SKILL.md`. Those are maintained artefacts that CI already checks, so they
  cannot drift away from the skill the way a transcription would.

`who`, `day0`, `day1` and `day2` are not here either: `days.FUNCTION_DAYS`
already holds them per function and the lesson pages render them, so repeating
them would be a second copy to correct.

The taught duration is derived rather than typed. Function A is sixteen lessons
in about four hours, which is the only measured pace this curriculum has; every
other function states its own estimate at that pace and prints the derivation,
because a guide that asserts "about nine hours" with no arithmetic behind it is
a number a reader cannot check.
"""

# ---------------------------------------------------------------- per function
#
# `board`  — the one sentence to hold for the whole function, as A has.
# `framing`— the opening module: the idea the rest hangs off, for a reader who
#            has nobody at the front of a room to say it.
# `solo` / `room` — how to work through it, per reader.
# `short`  — what to cut when there is half the time. `short_room` is the part
#            that only applies with an audience.
# `entry`  — the lesson that is the function's own introduction, so the guide
#            can point at it rather than restate it.

FUNCTIONS = {

"B": {
 "board": "Name the risk before you choose the control",
 "entry": "B1.0",
 "framing": [
  "Function A built the platform. **This function is the one that asks what "
  "can go wrong with it**, and it spends its whole first chapter — twenty "
  "lessons — doing nothing but naming risks against components you already "
  "wrote. That order is the argument: a control chosen before the risk is "
  "named is a control chosen because it was easy to buy.",
  "The shape is three chapters and it is deliberate. **B1 is the register**: "
  "every risk CyberTravels carries, one lesson each, ending in the register "
  "itself and the control index. **B2 closes the two controls that shut the "
  "most of them** — knowing who is calling, and marking what came in from "
  "outside. **B3 is the layer that still holds after identity has been "
  "defeated**: default-deny on the tool call, a sandbox, egress, budgets, and "
  "an approval path that survives volume.",
  "The thing to keep saying out loud is that **B1 is not the scary chapter and "
  "B2–B3 the reassuring one**. B1.18's register is a scorecard with a column "
  "for the owning control, and most of that column is empty when you first "
  "fill it in. The empty cells are the backlog, in the same units as "
  "everything else — that is what makes this function usable rather than "
  "alarming.",
 ],
 "solo": "Do B1 in order but do not try to do it in one sitting — twenty "
         "risks is a lot of adversary to hold. B1.18 and B1.19 are the two "
         "that make the other eighteen add up, so do not stop before them. "
         "B2 and B3 are each a single arc and read better in one go.",
 "room": "B1 is the chapter that benefits most from pairs arguing: give each "
         "pair two risks and have them present the CyberTravels component it "
         "attaches to, rather than walking all twenty from the front.",
 "short": "B1.0, B1.1, then any six risks from B1.2–B1.17 — pick the ones "
          "that match what your team is building — then B1.18 and B1.19 "
          "whole, because the register and the control index are what turn "
          "the six into a method. B2.1, B2.3 and B2.6 are the minimum of B2. "
          "From B3 take B3.1, B3.4 and B3.6.",
 "short_room": "Split B1.2–B1.17 across the room rather than cutting them: "
               "two risks per pair, three minutes each, and everybody leaves "
               "having read sixteen risks even though each person only ran "
               "two.",
 "outcomes": [
  ("Draw the agentic reference architecture and mark where trust changes",
   ["B1.1"], "A diagram with the boundary edges marked, not a box diagram"),
  ("Name a risk against a named component, rather than in the abstract",
   ["B1.2", "B1.3", "B1.9"],
   "Each risk cites the CyberTravels file it attaches to"),
  ("Fill a risk register whose control column is honest about what is missing",
   ["B1.18", "B1.19"], "Risks with a named owning control, out of the total"),
  ("Make a delegation that narrows, and show it in an audit row",
   ["B2.3", "B2.7"], "A token with one scope, and a row naming the human"),
  ("Mark untrusted content at the door and keep the mark",
   ["B2.6"], "An origin label that survives into the prompt"),
  ("Put a runtime layer under the identity layer, and say what each stops",
   ["B3.1", "B3.2", "B3.3", "B3.4"],
   "Four controls, each with the attack it closes and the one it does not"),
  ("Show where an approval gate stops working, with a number",
   ["B3.6"], "The volume at which coverage stays at 100% and review does not"),
 ],
 "pitfalls": [
  ("Treating B1 as a list to read rather than a register to fill",
   "Every risk lesson ends with it attached to a component. If you cannot "
   "name the file, you have read the risk and not placed it — and B1.18 will "
   "not add up.",
   "Have pairs write the component on the board as they go, so the register "
   "assembles in front of the room."),
  ("Reaching for a control in the middle of B1",
   "Write it in the parking lot and carry on. The control index is B1.19 and "
   "it is better for having been earned.",
   "This is the single most common interruption in this function. A visible "
   "parking lot is what keeps B1 on time."),
  ("Reading B2 as \"identity solves it\"",
   "B3 exists because identity gets defeated. The two chapters are layers, "
   "not alternatives, and B3.1's default-deny assumes the caller is already "
   "who they claim to be.",
   ""),
  ("Skipping B1.19 because B1.18 feels like the conclusion",
   "The register names risks; the control index names the controls, including "
   "the ordinary ones that predate agents. A programme built from the "
   "register alone covers only the AI-specific rows.",
   ""),
 ],
 "capstone": [
  "**Fill the register for something you actually own.** Run B1.18's skill "
  "against your own system rather than CyberTravels, and count the risks with "
  "a named owning control. The share, not the count, is the number.",
  "**Name the control you would buy first, and why it is not the one that "
  "shuts the most risks.** Most people's first answer is a filter. B1.19's "
  "index is the check.",
  "**Say which B3 control you would add if identity were already perfect.** "
  "If the answer is none, re-read B3.1 — the question is the whole point of "
  "the chapter.",
 ],
 "capstone_room": [
  "Collect the registers and read out the control-coverage shares without "
  "names attached. The spread is the discussion.",
 ],
 "quick_check": [
  ("Why does B1 name twenty risks before B2 closes any of them?",
   "A control chosen before the risk is named is chosen for being easy to buy"),
  ("What is the difference between prompt injection and indirect prompt "
   "injection?",
   "Where the text came from: the user's own message, versus a document the "
   "agent was asked to read"),
  ("Which two controls shut the most risks in the register?",
   "Knowing who is calling, and marking what came in from outside — B2"),
  ("Why is there a B3 at all, if B2 establishes identity?",
   "Identity gets defeated; B3 is the layer that still holds when it has"),
  ("An approval gate covers 100% of irreversible actions. What is missing?",
   "The volume. At four hundred a day coverage is unchanged and review is zero"),
  ("What does an empty cell in the register's control column mean?",
   "A risk with no owning control — the backlog, in the same units as the rest"),
 ],
 "handover": [
  ("The risk register you filled", "C2.0",
   "becomes the thing an AppSec pipeline has to find in code"),
  ("The controls you chose", "D1.0",
   "get attacked by a red team that does not believe them"),
  ("The audit trail from B2.7", "E1.0",
   "becomes the telemetry a SOC has to detect from"),
  ("The control index from B1.19", "F1.1",
   "becomes key control indicators somebody has to evidence"),
 ],
 "chapters": {
  "B1": {
   "intro":
    "Twenty lessons, each one risk, each attached to a component you built in "
    "Function A. The chapter is front-loaded on purpose: B1.0 says what "
    "securing an architecture means and B1.1 draws the reference architecture, "
    "and everything from B1.2 to B1.17 hangs off that drawing.\n\n"
    "**B1.18 and B1.19 are not optional.** The register turns eighteen "
    "separate risks into one scorecard, and the control index adds the "
    "controls that are not new — the ordinary ones a programme built only from "
    "the agentic rows would miss entirely.",
   "teach":
    "This is nine lessons longer than any other chapter in the curriculum. "
    "Budget for it as two sessions with the register opening the second, not "
    "as one long one.",
  },
  "B2": {
   "intro":
    "Eight lessons on the two things that shut the most of B1's register: "
    "**who is calling**, and **what came in from outside**. The arc runs from "
    "the three principals in any action, through bootstrapping the first "
    "credential and narrowing a delegation, to an audit trail the workload "
    "itself cannot forge.\n\n"
    "B2.8 is the one people underestimate. An audit trail the acting workload "
    "can write to is a record of what the workload chose to admit.",
   "teach": "",
  },
  "B3": {
   "intro":
    "Eleven lessons on the layer that holds **after** identity has been "
    "defeated. Default-deny on the tool call, a sandbox, egress control, "
    "budgets, validating what comes back, and an approval path measured at "
    "volume — then the gateway that gives you one choke point when there are "
    "more agents than you can configure individually.\n\n"
    "The last three are the ones nobody plans for: shared infrastructure "
    "between runs, turning a control off without turning the system into an "
    "experiment, and the agent's own escalation path — what an agent does when "
    "it notices something outside its task and has no way to say so.",
   "teach":
    "B3.6 and B3.9 are the two to protect if you are running short. They are "
    "the lessons that change how somebody runs a platform rather than how they "
    "configure one.",
  },
 },
},

"C": {
 "board": "A pipeline is a harness, and a harness needs a verifier",
 "entry": "C2.0",
 "framing": [
  "**One chapter, twenty lessons, one pipeline built end to end.** C2.0 splits "
  "it the way the function is organised: what runs *before* a deploy, and what "
  "runs *after*. Everything else is one stage of that pipeline, in the order "
  "it runs.",
  "The spine is: threat model from what the estate already knows → "
  "deterministic SAST, then a model pass → deduplicate and verify in context → "
  "filter to what is reachable → replicate in a sandbox → supply chain → "
  "dynamic exploitation → chaining → the agentic pentest in three colours "
  "(white, black, grey box) → severity and reporting → remediation proven "
  "before the merge request → context engineering to cut the false positives "
  "→ attesting control intent.",
  "The argument underneath all twenty is C2.1's: **this is security "
  "engineering, so build a harness rather than a prompt.** Every stage has a "
  "deterministic half and a model half, and the deterministic half is what "
  "makes the model half checkable. A pipeline whose only verifier is another "
  "model has no verifier.",
 ],
 "solo": "Do it in pipeline order; the stages genuinely depend on each other "
         "and C2.4's deduplication is meaningless before C2.3 has produced "
         "duplicates. The two Bonus lessons (C2.14, C2.19) can be read at any "
         "point.",
 "room": "This is the function that works best with one shared screen and the "
         "pipeline drawn across a whiteboard, one stage added per lesson, "
         "because the value is the shape of the whole thing rather than any "
         "single stage.",
 "short": "C2.0, C2.1, C2.3, C2.4, C2.5, C2.15 and C2.16 — the harness "
          "argument, the two-pass scan, the two filters that make a queue "
          "workable, and the two that get a fix merged. That is the pipeline "
          "in miniature and it still has a verifier.",
 "short_room": "Run C2.10–C2.13 as one 20-minute discussion of what each "
               "colour of pentest can and cannot prove, rather than four "
               "labs.",
 "outcomes": [
  ("Say what makes a pipeline a harness rather than a prompt",
   ["C2.1"], "Can name the deterministic half of a stage and what it verifies"),
  ("Run a two-pass scan and explain why the deterministic pass goes first",
   ["C2.3"], "Semgrep findings, then the model pass, scored separately"),
  ("Cut a findings queue without cutting real defects",
   ["C2.4", "C2.5", "C2.17"],
   "Distinct defects out of raw findings, and the reachability filter's basis"),
  ("Prove a finding rather than assert it, inside a replica",
   ["C2.6", "C2.8"], "A reproduction, and the control probe that bounds it"),
  ("Say what each colour of agentic pentest can prove",
   ["C2.11", "C2.12", "C2.13"],
   "Black-box claims separated into entailed and merely suggested"),
  ("Gate a fix on evidence rather than on a green build",
   ["C2.16"], "A test that fails on the unpatched code and passes on the fix"),
 ],
 "pitfalls": [
  ("Calling the model pass the scan",
   "The deterministic pass is what the model pass is scored against. Run "
   "C2.3 both ways and compare — the lesson prints both.",
   ""),
  ("Reading a smaller queue as a better queue",
   "C2.4 and C2.5 cut findings for two different reasons — duplicates, and "
   "unreachable code — and only one of them is about risk. A queue cut by the "
   "wrong filter is a queue missing defects.",
   ""),
  ("Treating the pentest lessons as an attack class",
   "C2.14 is in the chapter because an offensive agent needs controls around "
   "it. Do not skip it to get to C2.19.",
   "Say before C2.10 that C2.14 is coming, or the room will ask for it four "
   "lessons early."),
  ("Accepting a green CI run as proof a vulnerability is closed",
   "C2.16 is the whole lesson: the test has to fail against the unpatched "
   "code. Hand it one that passes both ways and it refuses.",
   ""),
 ],
 "capstone": [
  "**Run the pipeline against `cybertravels/` and compare your findings with "
  "`cybertravels/LABELS.md`.** That file is the hand-written key four of these "
  "skills score recall and precision against. Report both, and report what you "
  "missed.",
  "**Name the stage whose output you trust least, and what would change that.** "
  "The honest answer is usually a stage with no deterministic half.",
  "**State the difference between your pipeline's conformance and its "
  "accuracy.** If you cannot, re-read C2.15.",
 ],
 "capstone_room": [
  "Have each pair report recall against LABELS.md without saying which stage "
  "they trusted — then reveal both. The correlation is the lesson.",
 ],
 "quick_check": [
  ("What makes a security pipeline a harness rather than a prompt?",
   "A deterministic half that the model half is scored against"),
  ("Why does the deterministic scan run before the model pass?",
   "So the model pass has something to be measured against"),
  ("C2.4 and C2.5 both shrink the queue. What is the difference?",
   "One removes duplicate reports of one defect; the other removes defects in "
   "code nothing calls — only the second is a statement about risk"),
  ("What must a remediation test do before a fix can be merged?",
   "Fail against the unpatched code"),
  ("A black-box probe reports a finding confidently. What do you ask?",
   "Which part the evidence entails and which part it merely suggests"),
  ("Conformance is near 100%. What does that tell you about quality?",
   "Nothing. Conformance is schema validity; accuracy is correctness"),
 ],
 "handover": [
  ("The pipeline you built", "D1.0",
   "gets a red team that attacks the pipeline rather than the application"),
  ("The findings it produces", "E2.5",
   "become detections, and the benign corpus that decides them"),
  ("The attestations from C2.18", "F1.5",
   "become evaluation output offered as audit evidence"),
 ],
 "chapters": {
  "C2": {
   "intro":
    "One chapter and the whole function. Twenty lessons in pipeline order, "
    "from the threat model to the attestation, with the before-deploy and "
    "after-deploy split named in C2.0 and held for the rest.\n\n"
    "Two of the twenty are marked **Bonus** — C2.14 on the controls an "
    "offensive agent runs inside, and C2.19 on the pipeline in production. "
    "Neither is optional reading if you intend to run an offensive agent "
    "against anything you do not own.",
   "teach":
    "Twenty dependent stages is the longest single arc in the curriculum. "
    "Draw the pipeline once and add to it, rather than re-drawing per lesson.",
  },
 },
},

"D": {
 "board": "If you cannot reproduce it, you have not found it",
 "entry": "D1.0",
 "framing": [
  "**One red-team lifecycle, twelve lessons, start to finish.** Not a catalogue "
  "of attacks — a single engagement run end to end, from the ingestion path "
  "through to the governance record it leaves behind.",
  "The thing that makes this function different from the usual red-team "
  "material is D1.0's subject: **non-deterministic threat simulation**. An "
  "attack that works once against a model is not a finding. Most of this "
  "function is about the arithmetic of that — rates with intervals, seed "
  "spread beside the rate, floors, and what a swarm does to a triage queue "
  "that was built for individual alerts.",
  "The second half turns around. D1.4 onwards is the defender's side of the "
  "same lifecycle: telemetry, high-concurrency detection, triaging the swarm, "
  "deception and threshold failures, machine-speed containment, forensic "
  "replay, and the compliance record. **Red and blue are the same twelve "
  "lessons read from two ends**, which is why the function is one chapter.",
 ],
 "solo": "Twelve lessons in order, and do not skip the arithmetic ones (D1.3, "
         "D1.7). They are the reason the findings in this function are "
         "reportable.",
 "room": "The shortest function in the curriculum and the one that fits a "
         "single session most comfortably. Run it as one engagement with the "
         "room as the team.",
 "short": "D1.0, D1.2, D1.3, D1.7 and D1.9 — the framing, the weaponised "
          "path, the scaling arithmetic, the swarm triage, and the "
          "containment. That keeps both ends of the lifecycle.",
 "short_room": "D1.5 and D1.8 demo well from one machine and read poorly as "
               "individual labs, so run those two from the front.",
 "outcomes": [
  ("Say why one successful attack against a model is not a finding",
   ["D1.0", "D1.3"], "A rate with an interval, and the seed spread beside it"),
  ("Weaponise an ingestion path and record what it actually reached",
   ["D1.1", "D1.2"], "The path, and the authority it inherited"),
  ("Scale elicitation and report the result honestly",
   ["D1.3"], "Attack success rate with its denominator and its spread"),
  ("Detect the actor rather than the payload",
   ["D1.4", "D1.6"], "Detections that survive high concurrency"),
  ("Triage a non-deterministic swarm without a per-alert queue",
   ["D1.7"], "A floor, and what the sample found below it"),
  ("Contain at machine speed and prove the containment held",
   ["D1.9"], "Fleet revocation, and what still held a valid token after it"),
  ("Leave a record an auditor can use",
   ["D1.10", "D1.11"], "A replayable run, and the governance artefact"),
 ],
 "pitfalls": [
  ("Reporting a single successful prompt as a vulnerability",
   "Run it again with a different seed. D1.3 is the lesson, and the seed "
   "spread is usually larger than the rate.",
   ""),
  ("Letting the swarm lessons become a discussion about model capability",
   "D1.5 and D1.6 are about concurrency and detection engineering. The "
   "capability question belongs in D1.3.",
   "Park it. This is the most common derail in this function."),
  ("Skipping D1.11 because the engagement is over",
   "The institutional record is what makes the next engagement cheaper, and "
   "it is the only lesson in the function that an auditor will read.",
   ""),
  ("Running offensive tooling outside a replica",
   "C2.14 and D1.8 both cover the controls. An engagement against something "
   "you do not own is not in scope for this curriculum.",
   "State the authorisation boundary out loud before D1.2."),
 ],
 "capstone": [
  "**Pick one finding from your run and state its rate, its denominator and "
  "its seed spread.** If any of the three is missing, it is not yet a finding.",
  "**Say which of your detections would survive the swarm in D1.5.** Most "
  "per-run detections do not, and that is the point of D1.6.",
  "**Produce the replay.** D1.10's run should be reproducible by somebody who "
  "was not there. If it is not, the forensic half of the lifecycle is missing.",
 ],
 "capstone_room": [
  "Have one pair attempt to reproduce another pair's finding from their "
  "record alone. Whether they can is the honest score for the whole session.",
 ],
 "quick_check": [
  ("Why is one successful attack against a model not a finding?",
   "It is not reproducible; a rate needs a denominator and an interval"),
  ("What is usually larger than the attack success rate, and almost never "
   "reported?", "The spread across seeds"),
  ("What does a swarm do to an alert queue built for individual alerts?",
   "Saturates it — which is why D1.7 triages with a floor instead"),
  ("Containment at machine speed: what does a fleet revocation leave behind?",
   "Tokens already issued, and evidence the stop itself destroyed"),
  ("Who reads the output of D1.11?",
   "An auditor — it is the only lesson in the function written for one"),
 ],
 "handover": [
  ("The detections you wrote", "E2.2",
   "get a subject, and a mapping to ATT&CK and ATLAS"),
  ("The containment you proved", "E4.3",
   "becomes a runbook with a tier and a stop authority"),
  ("The replay from D1.10", "E5.1",
   "becomes the forensic reproduction an incident depends on"),
  ("The record from D1.11", "F1.5",
   "becomes evaluation output offered as audit evidence"),
 ],
 "chapters": {
  "D1": {
   "intro":
    "One chapter, one engagement, twelve lessons. D1.0 to D1.3 are the "
    "offensive half — ingestion, weaponisation, and the arithmetic that turns "
    "a successful prompt into a reportable rate. D1.4 to D1.11 are the same "
    "lifecycle from the defender's end.\n\n"
    "The hinge is D1.4. Everything before it is about producing an effect; "
    "everything after is about whether anybody could see it, stop it, and "
    "later prove what happened.",
   "teach":
    "Twelve lessons is one comfortable session. Say the authorisation "
    "boundary before D1.2 and you will not have to say it again.",
  },
 },
},

"E": {
 "board": "Every detection has a subject, and a clock",
 "entry": "E1.0",
 "framing": [
  "**Five chapters that are five intervals of one clock.** E1.0 sets it up and "
  "every lesson in the function is anchored back to it: discover, detect, "
  "understand, respond, recover. Each chapter shortens one interval, and the "
  "anchor line on every page says which.",
  "The agent-shaped problem runs through all five. A sensor estate built for "
  "people sees an agent as either a volume anomaly or nothing at all; an alert "
  "queue built for one analyst reading one alert does not survive a fleet; a "
  "containment plan built around disabling an account does not stop a workload "
  "holding an issued token. **Each chapter is the same correction applied to a "
  "different interval.**",
  "The one sentence to keep returning to is that **a detection without a named "
  "subject is a volume rule**. E2.2's subject is the agent, E2.3's is the agent "
  "platform, and E3.4 is the lesson on the three instincts that misfire when "
  "the actor turns out to be an agent rather than a person.",
 ],
 "solo": "Chapter by chapter, in order, and re-read E1.0 before each one — the "
         "anchor on every page refers back to it and the function stops "
         "cohering if the clock is not in mind. E3 is the longest chapter and "
         "splits naturally after E3.4.",
 "room": "Put the five intervals on the board on the first slide and mark "
         "which one each lesson shortens. A room that loses the clock reads "
         "this function as thirty-one separate detections.",
 "short": "E1.0 and E1.1, then E2.1 and E2.2, E3.1 and E3.4, E4.3 and E4.4, "
          "and E5.2. That is one lesson or two per interval and the clock "
          "still closes.",
 "short_room": "E3.5–E3.10 run well as a single discussion of what an "
               "investigating agent may touch and what it must not, rather "
               "than six labs.",
 "outcomes": [
  ("Say which of the five intervals a given control shortens",
   ["E1.0"], "The anchor on any page, answered without reading it"),
  ("Separate an agent's tempo from a person's, with signals",
   ["E1.1", "E1.2"], "Action rate, variance, session length, tool breadth"),
  ("Write a detection whose subject is named, and score it before it ships",
   ["E2.2", "E2.3", "E2.5"],
   "Precision, recall and firing volume against a benign corpus"),
  ("Investigate an agent actor without the three instincts that misfire",
   ["E3.4"], "Naming all three, and what each one gets wrong"),
  ("Bound what an investigating agent may touch",
   ["E3.2"], "Admission rules, written before the investigation starts"),
  ("Contain at machine speed and know what the stop left behind",
   ["E4.3", "E4.4", "E4.5"],
   "Time to halt a fleet, and the tokens still valid afterwards"),
  ("Write a root cause that names a control rather than a person",
   ["E5.2", "E5.4"], "A control, and the indicators the fix moved"),
 ],
 "pitfalls": [
  ("Reading the function as thirty-one detections",
   "It is five intervals. The anchor line on every page names which one, and "
   "E1.0 is the lesson that makes the rest add up.",
   "Keep the five intervals visible for the whole session."),
  ("Writing a detection with no subject",
   "A rule that fires on volume is a rule about volume. E2.2 and E2.3 are two "
   "different subjects on the same events, and the difference is the lesson.",
   ""),
  ("Shipping a rule because it caught the incident",
   "E2.5 scores a candidate against a benign corpus first. A rule with no "
   "measured false-positive rate is a rule nobody will work.",
   ""),
  ("Containing by disabling the human's account",
   "E4.3 and the agent-actor material are explicit: a workload holding an "
   "issued token is not stopped by disabling the person who asked.",
   ""),
  ("Letting the root cause name a person",
   "E5.2 is the whole lesson. A root cause naming a person ends no interval, "
   "because nothing about the system changed.",
   "This is the one worth stopping the room for."),
 ],
 "capstone": [
  "**Put a number on each of the five intervals for a system you own.** Most "
  "people can produce three. Which two are missing is the finding.",
  "**Take one detection you already run and name its subject.** If the answer "
  "is \"unusual activity\", it is a volume rule.",
  "**Say what your containment leaves behind.** Issued tokens, destroyed "
  "evidence, and the runs that should have been preserved — E4.5's three.",
 ],
 "capstone_room": [
  "Collect the five-interval numbers anonymously and show the spread. The "
  "interval everybody is missing is almost always the same one.",
 ],
 "quick_check": [
  ("Name the five intervals.",
   "Discover, detect, understand, respond, recover"),
  ("What makes a detection something other than a volume rule?",
   "A named subject — the agent, or the agent platform"),
  ("Why does a human-tuned volume rule misfire on an agent?",
   "Agent tempo, variance and tool breadth are nothing like a person's"),
  ("Three instincts misfire when the actor is an agent. Name one.",
   "Disabling the account — the workload still holds issued tokens"),
  ("Before a generated rule ships, what has to be measured?",
   "Its firing rate against a benign corpus"),
  ("Why must a root cause name a control rather than a person?",
   "Naming a person ends no interval; nothing about the system changed"),
 ],
 "handover": [
  ("The five intervals", "F1.1",
   "become key control indicators with dates on them"),
  ("The incident record", "F2.6",
   "meets a disclosure clock that starts at awareness, not confirmation"),
  ("The stop authority from E4.4", "F3.2",
   "becomes a policy attached to autonomy rather than to tools"),
 ],
 "chapters": {
  "E1": {
   "intro":
    "Four lessons. E1.0 sets up the clock the whole function is anchored to, "
    "and the other three are the discover interval: what an EDR, DLP, CSPM or "
    "CNAPP estate actually sees when the actor is an agent, what drift does to "
    "a control that was signed off against behaviour that no longer exists, "
    "and how to find the agents nobody registered.\n\n"
    "**E1.0 is the most load-bearing lesson in Function E.** Every later page "
    "carries an anchor line back to it.",
   "teach":
    "Do not shorten E1.0. The anchors on the other thirty pages stop meaning "
    "anything without it.",
  },
  "E2": {
   "intro":
    "Six lessons on the detect interval. Where agent telemetry lands, then "
    "two chapters' worth of argument compressed into four lessons: a detection "
    "whose subject is the agent, one whose subject is the platform, one "
    "written by a loop and shipped by a human, one generated from an incident "
    "and decided by a benign corpus — and the honeypot, which is the detector "
    "with no threshold.\n\n"
    "E2.6 is the odd one out and worth the time: an alert with no structurally "
    "possible false positive is a different kind of object from everything "
    "else in the chapter.",
   "teach": "",
  },
  "E3": {
   "intro":
    "Ten lessons, the longest chapter in the function, on the understand "
    "interval. It splits cleanly: **E3.1–E3.4** are the operator's shift — "
    "going from an alert queue to running a loop, bounding what the "
    "investigating agent may touch, the context that makes triage work, and "
    "the three instincts that misfire when the actor is an agent. "
    "**E3.5–E3.10** are the investigation itself: reconstruction, replanning, "
    "scoping along the delegation graph, fleet-level correlation, third-party "
    "intel, and hunting.\n\n"
    "E3.8 is the one that only makes sense at fleet level: every run passes "
    "every per-run check and something is still wrong.",
   "teach":
    "Split this chapter after E3.4. Ten lessons is too long for one sitting "
    "and the break is already in the material.",
  },
  "E4": {
   "intro":
    "Five lessons on the respond interval, and the chapter where the "
    "arithmetic is most brutal. What may be done without asking, three runbook "
    "tiers at three different speeds, containment at machine speed, who holds "
    "stop authority and how long they take to use it, and the fleet kill "
    "switch.\n\n"
    "E4.5 is the lesson about what a stop leaves behind — valid tokens, "
    "destroyed evidence, and the runs that should have been preserved. Test "
    "the switch before relying on it.",
   "teach": "",
  },
  "E5": {
   "intro":
    "Six lessons on recover and root cause: reproducing a run you can defend, "
    "a root cause record that names a control, picking the layer the fix "
    "belongs in, re-measuring the indicators the incident moved, proposing the "
    "policy change and saying what it does not fix, and the regulatory clock — "
    "which starts at **awareness**, not confirmation.\n\n"
    "E5.6 is where Function E hands over to Function F, and the awareness "
    "point is the one that surprises people.",
   "teach": "",
  },
 },
},

"F": {
 "board": "A control you cannot evidence is a control you do not have",
 "entry": "F1.0",
 "framing": [
  "**Three chapters: build the framework, build the platform, run the "
  "programme.** F1 turns framework controls into indicators somebody can "
  "compute. F2 maps those outward to the regulations that apply. F3 is the "
  "CISO office — sequencing, org design, metrics, and how to say no.",
  "F1.1 is the hinge of the whole function and every F page anchors back to "
  "it: **from framework control to key control indicator**. A control in a "
  "framework is a sentence. An indicator is a number with a date on it, "
  "computed from an artefact, which is the only form in which a control "
  "survives supervision.",
  "The direction of mapping is the argument, and it runs one way only: "
  "**controls outward to frameworks, never frameworks inward to controls.** A "
  "programme built per framework builds the same control three times and "
  "evidences it none. F2.3 picks the framework that covers the most of your "
  "controls as a spine and supplies the remainder from the others.",
 ],
 "solo": "F1 in order and do not skip F1.1 — the anchors on all thirty "
         "other pages refer to it. F2 reads as reference material and can be "
         "taken by the regimes that apply to you. F3 is the one to read last "
         "and twice.",
 "room": "The function most likely to have a mixed room — risk, audit, legal "
         "and engineering. F1.10's stakeholder map is worth doing early rather "
         "than in sequence, because it tells the room who owns what before "
         "they argue about it.",
 "short": "F1.0, F1.1, F1.3, F1.7 and F1.13 from the framework; F2.1 and "
          "F2.3 from the platform; F3.1, F3.6 and F3.8 from the programme. "
          "That is the indicator argument, the spine argument, and the three "
          "programme lessons that change behaviour.",
 "short_room": "F2.4–F2.8 are reference material. Name them and move on "
               "rather than teaching them, unless a sector overlay actually "
               "applies to the room.",
 "outcomes": [
  ("Turn a framework control into an indicator somebody can compute",
   ["F1.1", "F1.4"], "A number, its artefact, and the date it was taken"),
  ("Tier a use case by what it can do rather than which model it uses",
   ["F1.3"], "The disagreement between the two tierings, named"),
  ("Offer evaluation output as audit evidence, and say what it does not prove",
   ["F1.5", "F1.7"], "An indicator with a freshness window"),
  ("Map your controls outward to the regimes that apply",
   ["F2.1", "F2.3"], "One spine, with the remainder supplied from the others"),
  ("Say what an autonomous action's audit trail must answer",
   ["F2.8"], "A record that is complete, consistent — and could still be false"),
  ("Translate agentic risk upward without losing it",
   ["F3.1", "F3.5"], "Three indicators a board can act on"),
  ("Say yes with conditions rather than no",
   ["F3.6"], "Conditions that are testable and time-bound"),
 ],
 "pitfalls": [
  ("Mapping frameworks inward to controls",
   "It builds the same control three times and evidences it none. F2.3 is the "
   "lesson: your controls are the spine, frameworks are the labels.",
   "This is the derail that costs the most time in a mixed room."),
  ("Treating a control as operating because it exists",
   "F1.6 separates operating from watched. A control is operating when "
   "something enforces it, not when something documents it.",
   ""),
  ("Reporting a control as evidenced against behaviour that has changed",
   "F1.7 and F1.9: a retrain, a fine-tune or a re-index invalidates a "
   "reading. The control has not failed — it is unevidenced, which is a "
   "different and more honest state.",
   ""),
  ("Answering a regulator with coverage instead of accuracy",
   "F2.9 rehearses the three openings that actually get used. Conformance and "
   "expert accuracy get reported separately or not at all.",
   ""),
  ("Reading F3 as the soft chapter",
   "F3.3's sequencing and F3.7's build curve are the two lessons that decide "
   "whether a programme has control coverage or demos at the end of a year.",
   ""),
 ],
 "capstone": [
  "**Compute three indicators for a system you own, with dates.** F1.13 does "
  "it for CyberTravels; do it for yours, and note which artefact each number "
  "came from.",
  "**Pick your spine.** Run F2.3's comparison across the regimes that apply "
  "and say which framework covers the most of your control set — and what the "
  "remainder is supplied from.",
  "**Write one conditional yes.** Take a request you would currently refuse "
  "and write the conditions that make it safe, testable and time-bound. F3.6 "
  "is the lesson; a flat no costs visibility you do not get back.",
 ],
 "capstone_room": [
  "Have the engineering and the risk halves of the room each write the same "
  "indicator independently, then compare. The gap is usually the artefact, "
  "not the definition.",
 ],
 "quick_check": [
  ("What turns a framework control into something you can report?",
   "An indicator: a number, from a named artefact, with a date on it"),
  ("Which direction does control-to-framework mapping run, and why?",
   "Controls outward to frameworks — inward builds the same control three "
   "times and evidences none"),
  ("When is a control operating rather than merely watched?",
   "When something enforces it, not when something documents it"),
  ("A model was retrained. What happened to your control evidence?",
   "It is unevidenced — not failed, which is a different and more honest state"),
  ("What starts the regulatory clock?",
   "Awareness, not confirmation"),
  ("Why is a flat no expensive?",
   "The capability ships anyway and you lose the visibility — F3.6"),
 ],
 "handover": [
  ("The indicators you defined", "F1.13",
   "get computed against CyberTravels, gaps and all"),
  ("The programme you sequenced", "F3.8",
   "gets measured on resilience rather than on perfection"),
 ],
 "chapters": {
  "F1": {
   "intro":
    "Fourteen lessons building the framework. F1.0 says what AI governance "
    "means and **F1.1 is the hinge the other thirty F pages anchor to**: from "
    "framework control to key control indicator.\n\n"
    "The arc runs inventory → risk tiering → control mapping → evaluation as "
    "evidence → operating versus outcome guardrails → continuous verification "
    "→ supply chain → lifecycle → stakeholders → model risk → the seams, and "
    "ends at F1.13, which computes the indicators against CyberTravels and "
    "reports the gaps.",
   "teach":
    "F1.10's stakeholder map is worth pulling forward in a mixed room. It "
    "settles who owns what before the room spends an hour discovering it.",
  },
  "F2": {
   "intro":
    "Nine lessons mapping your controls outward. The regulatory map, "
    "horizontal regulation, voluntary frameworks as a spine, sector overlays, "
    "privacy, incident and disclosure obligations, documentation that survives "
    "supervision, auditability of autonomous action, and the regulator "
    "conversation itself.\n\n"
    "**F2.3 is the load-bearing one.** Pick the framework that covers the most "
    "of your controls, use it as the structure, and supply the remainder from "
    "the others.",
   "teach":
    "Much of F2 is reference. Teach F2.1, F2.3 and F2.9, and name the rest "
    "unless a specific overlay applies to the room.",
  },
  "F3": {
   "intro":
    "Eight lessons on running the programme. Translating risk upward, "
    "governing autonomy rather than approving tools, sequencing, org design, "
    "the metrics that matter at your level, saying no and saying yes with "
    "conditions, building the capability, and resilience over perfection.\n\n"
    "F3.3 and F3.7 are the two that decide whether a year of work produces "
    "control coverage or a set of demos, and F3.8 is the one that says what "
    "the programme is actually measured on.",
   "teach": "",
  },
 },
},
}

# ------------------------------------------------------------------ the index
#
# The guide index page. One line per function saying who it is for in the
# fewest words that are still true; the long version is in days.FUNCTION_DAYS
# and the generator renders it from there.

INDEX_BLURB = {
 "A": "The system the other five tracks are about. Set your machine up and "
      "build it. Start here whatever your job is.",
 "B": "What changes in architecture and infrastructure security. Name every "
      "risk the system carries, then close them — identity and ingress first, "
      "then the runtime layer under both.",
 "C": "What changes in application security when agents write the code: a "
      "pipeline that keeps up, with a check that is not another model.",
 "D": "What changes in a red team. One lifecycle end to end, and findings "
      "that happen again rather than once.",
 "E": "What changes in a SOC, across five intervals of one clock: would you "
      "see it, could you stop it, and could you prove what happened.",
 "F": "What changes in governance. Framework controls become numbers somebody "
      "can compute, mapped out to the rules that apply to you, in a programme "
      "ordered to produce coverage rather than demos.",
}


# ----------------------------------------------- the introductory video script
#
# Spoken narrative for one video about the commons as a whole, rendered into
# LIGHTBOARD.md by `build_lightboard.py` and shown on the home page once
# `recordings/intro.mp4` exists.
#
# `{placeholders}` are filled from the tree by the generator — lesson, chapter,
# function and skill counts, and the reading volume. None of them is typed
# here, for the same reason none of the course guides' numbers are: this is the
# first thing a visitor watches, and a wrong count in the first thirty seconds
# is the most expensive wrong count in the project.
#
# Five beats, the same shape as every lesson script, so somebody recording this
# after recording lessons is not learning a new format.

INTRO = {
 "title": "Cyber Commons — what this is, and how to use it",
 "board": "How the work changes when agents do it.",
 "beats": [
  ("① WHAT THIS IS", [
   "This is Cyber Commons. It is free, open training for security teams, and "
   "it comes in {functions} tracks.",
   "The first builds an agentic system. The other five each take one part of a "
   "security organisation — architecture and infrastructure, application "
   "security, offensive security, the SOC, and governance — and teach the same "
   "thing about each: how that work changes when agents do it. {sessions} "
   "lessons in all, and every one of them runs on your own computer.",
   "A commons is a shared resource no one owns and everyone may draw from. "
   "This one is open, and it is openly corrected — if a lesson is wrong, the "
   "fix is a pull request.",
  ]),
  ("② WHY IT EXISTS", [
   "Here is the problem it was built for.",
   "Breakout time — how long it takes an attacker to get in and start moving "
   "sideways — is down to twenty-nine minutes. The fastest on record is "
   "twenty-seven seconds. Now think about how most security work is actually "
   "done. Architecture reviewed every few months. Alerts read one at a time. "
   "Controls checked once a year for an auditor.",
   "Attackers are already using AI to go faster. You cannot close that gap by "
   "reading faster. The work itself has to be done differently, and that takes "
   "knowing how — which is what this is for.",
   "There is a second half, and it matters just as much. The systems you are "
   "defending are becoming agents themselves. A chatbot that is wrong says "
   "something wrong. An agent that is wrong does something wrong — it cancels "
   "a booking, or moves money, or deletes a row. So the same technology you "
   "are using to go faster is also your newest attack surface. Both halves are "
   "in here.",
  ]),
  ("③ WHAT YOU BUILD", [
   "You do not read about a system. You build one.",
   "CyberTravels is a corporate travel company with an agentic platform — four "
   "agents that book trips, issue refunds, read vendor documents and write "
   "code. The first track has you build it, one piece per lesson. It is hard "
   "to secure an agent you have never built.",
   "Then the five tracks after it each take one part of a security "
   "organisation and show you what changes. Track B is architecture and "
   "infrastructure: a design review that ends with a list of risks and owners "
   "instead of an opinion. Track C is application security: a pipeline that "
   "keeps up with code an agent wrote. Track D is offensive security: findings "
   "that happen again rather than once. Track E is the SOC: an analyst "
   "directing a loop instead of reading alerts one at a time. Track F is "
   "governance: a number somebody can compute, with a date on it, instead of a "
   "control statement.",
   "That is why there is one system and not six examples. A sharper example is "
   "not worth you holding a second system in your head.",
  ]),
  ("④ HOW IT ACTUALLY WORKS", [
   "Three things to know before you start.",
   "First, there is nothing to install beyond Python and Git. No account with "
   "us, no hosted notebook, no API key of ours. The one thing you need is a "
   "model, and a signed-in Claude command line counts.",
   "Second, every lesson answers three questions, in order, because that is "
   "what it takes to change how work gets done rather than just demonstrate "
   "something. Day 0, why this is worth doing. Day 1, the thing you build. Day "
   "2, the number that tells you next quarter that it still works. The third "
   "one is what most training leaves out, and it is the one your own "
   "organisation will ask you for.",
   "Third, {skills} procedures in here are written as skills. A skill is a "
   "document and an instruction in the same bytes, so what you read is exactly "
   "what runs. And nothing is ever put in place of a model's answer: if there "
   "is no model configured, the program stops and says so rather than printing "
   "something that looks plausible.",
  ]),
  ("⑤ WHERE TO START", [
   "Start at A0.0, whatever your job is. It sets your machine up, and the "
   "whole first track is about {reading_minutes} minutes of reading, so you "
   "are not committing a quarter to find out whether this is for you.",
   "After that, take the track that matches your job. There are {chapters} "
   "chapters and nobody takes all {sessions} lessons — architecture and "
   "infrastructure go to track B, application security to C, offensive "
   "security to D, the SOC to E, governance to F. Each one has a course "
   "guide: a short brochure at the top, a run sheet for every lesson "
   "underneath, and a button to save it as a PDF.",
   "One sentence to take with you, because the rest of it is the second half "
   "of that sentence. The model proposes. Your code decides.",
  ]),
 ],
 "directions": {
  "① WHAT THIS IS": "Write CYBER COMMONS on the board, and under it HOW THE "
                    "WORK CHANGES. Then the numbers: {sessions} lessons, "
                    "{functions} tracks.",
  "② WHY IT EXISTS": "Two columns. Left, THE ATTACKER: 29 minutes, 27 "
                     "seconds, using AI. Right, THE WORK: reviewed every few "
                     "months, one alert at a time, checked once a year. "
                     "Circle the space between the columns.",
  "③ WHAT YOU BUILD": "Draw four boxes labelled workflow, advisor, coding, "
                      "files, and one box around all four: CYBERTRAVELS. Then "
                      "five arrows out of it, labelled ARCHITECTURE, APPSEC, "
                      "OFFENSIVE, SOC, GOVERNANCE.",
  "④ HOW IT ACTUALLY WORKS": "Three ticks down the left, then DAY 0 / DAY 1 / "
                             "DAY 2 across. Do not run anything here — this "
                             "beat is the promise, not the demo.",
  "⑤ WHERE TO START": "Write A0.0 large. Then B to F down the side, each with "
                      "the part of the organisation it is about.",
 },
}

# ------------------------------------------ the per-function overview videos
#
# One recording per course guide: what the function is for, before anybody
# commits several hours to it. The substance comes from `days.FUNCTION_DAYS`
# and the narrative above, so an overview cannot describe a function that has
# changed. These two lines per function are the only part written here.

# Written to be read aloud, by somebody who has not rehearsed it. That is a
# different job from writing for a page, and the first version of these did the
# page's job: it spliced in `days.FUNCTION_DAYS`, which is written to be read on
# a screen. Measured, the longest sentence in each script ran 31 to 65 words,
# every script carried three to eight em-dashes, and the vocabulary was the
# page's own - "workload identity", "SAST", "denominator", "adjudicated".
#
# So these are written for the ear. Short sentences, one idea each. No dashes,
# semicolons or brackets, because a reader cannot say them and has to decide on
# camera what to do with them. Technical terms are explained or left out. The
# facts all come from the same place the page's do (Day 0/1/2, the outcomes, the
# chapter notes), restated; **no number is copied from them**, because a number
# typed into a script is a number that goes stale. Lessons, chapters, skills,
# reading time and taught time are filled in from the tree by the generator.
#
# `build_lightboard.py` fails the build if a line here breaks those rules, so a
# later edit cannot quietly put the dashes back.
#
# Per function: `who`, `problem`, `what`, `can` (what you will be able to do),
# `chapters` (one plain line per chapter id) and `start`. Each list item is one
# paragraph in the script.

OVERVIEW = {

"A": {
 "who": [
  "This is Function A. It is called Getting Started, Building Agentic AI.",
  "It is for everyone, whatever your job.",
  "You do not need a security background. It helps if you can read a little Python.",
  "Do this one first. The other five functions are all about the system you build here.",
 ],
 "problem": [
  "An agent is a program that does things, not just a program that answers.",
  "A chatbot that is wrong says something wrong. An agent that is wrong does something wrong.",
  "Most advice on securing agents gets read, agreed with, and never put in place.",
  "That is usually because people have never built one.",
 ],
 "what": [
  "So you build one, on your own computer.",
  "It belongs to a made-up travel company called CyberTravels. Its agents book trips, issue refunds, read documents and write code.",
  "You build it one piece at a time. Then you add a record of what it did, checks on its work, and a way to score how well it performs.",
  "At the end, you work out how much damage it could do.",
 ],
 "can": [
  "Name the nine parts of an agent.",
  "Explain the main idea. The model proposes. Your code decides.",
  "Show five controls working, with real output.",
  "Say how much damage your agent could do.",
 ],
 "chapters": {
  "A0": "Set up your computer, and learn the nine words for an agent.",
  "A1": "Build the agent, from a simple loop to a running platform.",
  "A2": "Turn the demo into a real system. Record what it does, check it, and score it.",
 },
 "start": "Start at A0.0.",
},

"B": {
 "who": [
  "This is Function B. It is called Securing AI Architectures.",
  "It is for security architects, and for the engineers who build agent features.",
  "If you have ever been asked whether something is safe to ship, this is for you.",
 ],
 "problem": [
  "Before you pick any control, you need to know what can go wrong, and where.",
  "If you pick controls first, you tend to buy the ones that are easy to buy.",
  "This function gives you the full list of risks. It ties each one to the part of the system it hits.",
 ],
 "what": [
  "So you start by drawing the architecture.",
  "Then you close the two controls that shut the most risks. One is knowing who is calling. The other is marking what came in from outside.",
  "Then you add a layer that still protects you if identity fails. It blocks any tool call that was not allowed. It limits what the agent can reach. And it keeps human approvals useful, even when there are lots of them.",
 ],
 "can": [
  "Draw the architecture, and mark where trust changes.",
  "Name each risk against the part of the system it hits.",
  "Fill in a risk register that is honest about what is missing.",
  "Show the point where an approval step stops working.",
 ],
 "chapters": {
  "B1": "Every risk the system carries, one lesson each. It ends with a risk register.",
  "B2": "Who is calling, and what came in from outside.",
  "B3": "The protection that still holds when identity fails.",
 },
 "start": "Do the first chapter before anyone buys a control. Start at B1.0.",
},

"C": {
 "who": [
  "This is Function C. It is called Application Security with an AI SDLC.",
  "It is for application security engineers, code reviewers and penetration testers.",
  "You already run a security check on every release. Now you have to keep up with code that an agent wrote.",
 ],
 "problem": [
  "You already scan code, test it, and run a penetration test before launch.",
  "Two things have changed.",
  "When an agent writes code, a model's output ends up in charge of real actions. Fixed rules cannot catch every kind of mistake that causes.",
  "And coding agents now open pull requests faster than anyone can read them.",
 ],
 "what": [
  "So you build the pipeline in order, one stage at a time.",
  "You start with a threat model. Then you scan the code twice, once with fixed rules and once with a model.",
  "You remove duplicates, and anything that cannot be reached. You prove what is left in a safe copy of the system.",
  "Then you rate how serious it is, and hand the fix to a person.",
  "You also learn three kinds of penetration test run by an agent, and the safeguards an attacking agent needs.",
 ],
 "can": [
  "Explain why a pipeline needs a check that is not another model.",
  "Cut a long list of findings without losing the real problems.",
  "Prove a finding, instead of just claiming it.",
  "Hold back a fix until it shows evidence that it works.",
 ],
 "chapters": {
  "C2": "The whole function is this one chapter. It follows the pipeline in order, from the threat model to the final fix. Two of the lessons are bonus lessons.",
 },
 "start": "Start at C2.0.",
},

"D": {
 "who": [
  "This is Function D. It is called Agentic Evaluation and Red Teaming.",
  "It is for red team operators and AI security researchers. It is also for the defenders who receive what they find.",
  "What changes is what counts as a finding. It has to happen again. It is not enough that it worked once.",
 ],
 "problem": [
  "Nobody can tell you how your agent system fails until someone has tried to break it.",
  "An agent failure is a chain of reasoning, code written on the fly, and tool calls at machine speed. A scanner cannot see that.",
  "If you do nothing, your first real evidence arrives as an incident.",
 ],
 "what": [
  "So you work through one full attack, from start to finish.",
  "You begin with the ways in that an attacker reaches first. Then you scale the attack up.",
  "Then you switch sides. You turn what you found into logs and alerts, and a rule you can deploy. You add a plan for sorting alerts, a way to contain the damage, and a replay of what happened.",
  "You hand all of that over as policy.",
 ],
 "can": [
  "Say why one successful attack is not a finding.",
  "Report how often an attack works, and how many times you tried.",
  "Stop an attack at machine speed, and prove that it held.",
  "Leave a record that an auditor can use.",
 ],
 "chapters": {
  "D1": "One attack from start to finish. The first lessons attack. The rest defend, and they end with a record for auditors.",
 },
 "start": "Start at D1.0.",
},

"E": {
 "who": [
  "This is Function E. It is called The Agentic SOC.",
  "SOC means security operations centre. It is the team that watches for attacks.",
  "This function is for analysts, detection engineers, incident responders and threat hunters.",
  "Your SOC now has agents in it, and agents to watch. What changes is the analyst's job. You direct a loop. You stop reading alerts one at a time.",
 ],
 "problem": [
  "Your SOC was set up for people.",
  "An agent works far faster than a person, so the limits and alerts you set for people do not fit it.",
  "And some of what an agent does in an ordinary day is not seen by any sensor you already own.",
 ],
 "what": [
  "So you build it in five steps, using open source tools you can run.",
  "First, discover. Second, detect. Third, understand what happened. Fourth, respond. Fifth, recover.",
  "Each step has a number you measure. For example, how long it takes to detect a problem, or to contain it.",
 ],
 "can": [
  "Say which step a control makes faster.",
  "Tell an agent's pace from a person's pace.",
  "Write a detection rule, and test it before you use it.",
  "Contain an attack at machine speed, and know what the stop left behind.",
 ],
 "chapters": {
  "E1": "Discover. Find out what your sensors can and cannot see.",
  "E2": "Detect. Where the agent data lands, and the rules that catch it.",
  "E3": "Understand. Investigate, join up the evidence, and hunt.",
  "E4": "Respond. Contain an attack, and decide who is allowed to stop it.",
  "E5": "Recover. Find the root cause, and fix it for good.",
 },
 "start": "Start at E1.0. It sets up the clock that the rest of the function uses.",
},

"F": {
 "who": [
  "This is Function F. It is called AI Governance for Agentic Systems.",
  "It is for risk and compliance teams, control owners, privacy engineers and the CISO office.",
  "It is for anyone who has to answer for the system, rather than build it.",
  "What changes is what you hand over. It is a number that someone can check, with a date on it. It is no longer just a sentence saying a control exists.",
 ],
 "problem": [
  "Someone signed off on the platform when it was a chatbot.",
  "Now it moves money, ships code and reads contracts, and the approval process did not notice.",
  "A control that was tested six months ago is not passing. It is unproven.",
  "Most tools cannot show that. So a report can look fully green, and still have nothing behind it.",
 ],
 "what": [
  "So you build a set of numbers you can check.",
  "You start with a list of what you have. You rate each use by its risk. You match each control to the thing it protects. And you name an owner for each one.",
  "Then you re-check the controls, so you are not relying on last year's result.",
  "After that, you point the same numbers at regulators, and run it all as a programme, in a sensible order.",
 ],
 "can": [
  "Turn a framework control into a number someone can check.",
  "Rate a use of AI by what it can do, not by which model it uses.",
  "Map your controls to the rules that apply to you.",
  "Say yes with conditions, instead of just saying no.",
 ],
 "chapters": {
  "F1": "Build the framework. Turn controls into numbers you can check.",
  "F2": "Build the platform. Map your controls to the rules that apply.",
  "F3": "Run the programme. Report to leaders, set priorities, and say yes or no with conditions.",
 },
 "start": "Start at F1.0. Lesson F1.1 is the one the rest of the function builds on.",
},
}
