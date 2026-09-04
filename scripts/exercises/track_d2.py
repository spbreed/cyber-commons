"""D2 — The Incident Responder. Eight sessions.

Three things change when the actor is an agent, and each has a lesson:

    scope is a graph, not a host        — it follows the delegation chain
    containment must beat the loop      — a human in the path arrives too late
    attribution is a design property    — you cannot recover it afterwards

    D2.1  agent-assisted reconstruction
    D2.2  when the actor is an agent
    D2.3  scoping an agentic incident
    D2.4  containment at machine speed
    D2.5  replay and forensics
    D2.6  the post-incident change surface
    D2.7  stop authority
    D2.8  the regulatory clock
"""

from .skills import SKILL_RUNTIME

from . import diagrams as D

EXERCISES: dict[str, dict] = {

"D2.1": {
 "concept": """
Reconstruction is the first phase of any incident: build the timeline, establish
what happened, decide what to contain.

An agent makes this faster and more dangerous at the same time. Faster, because
a model can correlate thousands of log lines in seconds. More dangerous, because
it will produce a fluent, confident narrative from logs that were never
sufficient to support one — and a fluent narrative is much harder to challenge
than an obviously incomplete one.

So the discipline is to separate two questions that feel like one:

1. **What do the logs say?**
2. **What can the logs support?**

The gap between them is where reconstruction goes wrong, and it is the responder's
job to state that gap explicitly in the incident record.
""",
 "steps": [
  ("md", "## 2 · Demo — a timeline that reads perfectly"),
("md", "## 3 · Where it breaks — the confident wrong narrative"),
("md", "## 4 · The control — state what the evidence can support\n\n"
         "The fix is not a better model. It is a reconstruction step that reports "
         "its own evidentiary limits before it reports a conclusion."),
],
 "expect": "The timeline attributes every action to `dana@corp`. The fluent "
           "narrative recommends suspending her. The truth view shows "
           "`patch-agent` performed the credential read and the external POST; "
           "reconstruction reports BROKEN attribution with 3 misattributed lines. "
           "The evidence check flags the missing acting-identity field, the "
           "missing chain, and a non-human action rate.",
 "challenge": "Take a real incident timeline from your own history and ask what "
              "it would look like if an agent had been operating on the user's "
              "credential. If you cannot tell from the logs, your reconstructions "
              "already carry this risk.",
},

"D2.2": {
 "concept": """
Three responder instincts are correct for human incidents and misfire when the
actor is an agent.

1. **Disable the account.** For a human this stops them. For an agent holding an
   already-issued bearer token, it may not — the token remains valid until it
   expires.
2. **Interview the user.** They were asleep. They authorised a task; a model
   chose the actions. They cannot tell you what happened.
3. **Assume one actor.** There were three, in a chain, and only the last one
   touched the resource.

The correct first action is to **revoke the agent identity**, which is only
possible if A2 was done. This lesson is where the identity track's value becomes
operational rather than architectural.
""",
 "steps": [
  ("md", "## 2 · Demo — the three instincts, tested"),
("md", "## 4 · The control — revoke the agent identity first"),
("html", D.table(
    ["the runbook you have", "the runbook this incident needs"],
    [["1. disable the user account",
      "1. identify the <b>acting</b> identity from the act chain (A2.5)"],
     ["2. interview the user",
      "2. revoke that identity — no approval needed for a non-human (A3.6)"],
     ["3. review the user's recent activity",
      "3. scope by walking the delegation chain, not the host list (D2.3)"],
     ["", "4. preserve the run trace before anything restarts (D2.5)"],
     ["", "5. only then consider the human's account, and say why"]],
    emphasise=1,
    caption="Every step on the left is correct for a human actor and wrong here. "
            "The human authorised a task; the actions were chosen by a model.")),
 ],
 "expect": "Disabling the human's account leaves both agents able to act on "
           "already-issued tokens. The interview establishes the user authorised "
           "a task, not the actions. The chain shows three actors where the logs "
           "show one. Revoking `patch-agent`'s identity stops it in 12 seconds "
           "while dana and `deploy-agent` continue working.",
 "challenge": "Write your agentic incident runbook's first three steps. If step "
              "one is \"disable the user account\", rewrite it — and check "
              "whether you can currently revoke a single agent identity at all.",
},

"D2.3": {
 "concept": """
Scoping answers "what was touched?" For a host-based incident you enumerate
hosts. For an agentic incident, **scope follows the delegation graph**.

The agent that touched the resource is usually the *last* actor in a chain. If
you scope only that actor, you miss everything the earlier actors reached — and
because authority narrows down the chain, the earlier actors typically had
*more* access, not less.

The undercount is systematic and it grows with delegation depth, which is the
operational reason B2.0 bounds delegation depth in the first place.
""",
 "steps": [
  ("md", "## 2 · Demo — scope the chain, not the actor"),
("md", "## 3 · Where it breaks — the undercount grows with depth"),
("md", "## 4 · The control — scope from the act chain, then widen by shared resources"),

  ("md", "## 6 · Scoping as a skill\n\n"
         "Scoping a human incident asks where someone logged in. Scoping this "
         "one asks what the agent **decided** — every action was individually "
         "authorised, so nothing looks wrong at the authentication layer.\n\n"
         "Two fields in the contract carry most of the weight. `reach` and "
         "`confirmed_exfiltration` are separate numbers, because reach is the "
         "scope until proven otherwise and the smaller number must never stand "
         "in for the larger in a notification decision. And `does_not_stop` "
         "makes containment state its own limits."),
  ("skill", "secops/incident-scoping"),

],
 "expect": "Scoping the last actor finds `cluster-prod` alone; the whole chain "
           "reaches six resources, missing five, with an undercount factor of "
           "6.0. The undercount grows with each hop. Transitive scoping adds five "
           "second-order identities that shared a resource, explicitly marked as "
           "in scope rather than confirmed compromised.",
 "challenge": "For your last incident involving a service account, recompute the "
              "scope by walking what else that account could reach. The number is "
              "almost always larger than what was written in the report.",
},

"D2.4": {
 "concept": """
Containment has always been a race. With an agent, the other runner got much
faster and you did not.

The numbers decide the design. An agent operating at 300 actions per minute
completes 2,400 further actions during an eight-minute approval cycle, against
about 60 under automated containment. That ratio is the argument for
pre-authorised, automated revocation of non-human identities.

The asymmetry that makes it safe: revoking a **human's** access needs care,
because a false positive locks a person out mid-shift. Revoking a **non-human**
identity is cheap to get wrong — the agent re-requests, or an on-call re-enables
it in a minute. So the two should have different policies, and almost nowhere do.
""",
 "steps": [
  ("md", "## 2 · Demo — the race, in actions rather than minutes"),
("md", "## 3 · Where it breaks — approval latency is not the only delay"),
("md", "## 4 · The control — pre-authorise on high-confidence signals"),
],
 "expect": "The race table shows 2,400 versus 60 actions at 300/min for an "
           "eight-minute approval. The full containment path totals about 920 "
           "seconds, of which the revocation itself is 12. Four of five signals "
           "auto-revoke for non-human identities and none do for a human subject, "
           "cutting the path to 21 seconds and preventing roughly 4,500 actions.",
 "challenge": "Time your own containment path end to end, step by step. The "
              "revocation is almost never the slow part — queue depth and "
              "approval are, and both are policy choices rather than technical "
              "limits.",
},

"D2.5": {
 "concept": """
Forensics for an agent means answering: *why did it do that?*

For ordinary software the answer is in the code. For an agent the answer is in
the run — the prompts, the tool results it saw, the model version, the sampling.
Reproduce those four and the run is deterministic. Miss one and you can describe
what happened but never demonstrate it, which matters the moment anyone
disputes your conclusion.

The field teams miss most often is the **model version**, and it is the one that
silently invalidates everything else: a provider-side upgrade changes the
behaviour with no change on your side, so a reconstruction performed after the
upgrade does not reproduce the incident that happened before it.
""",
 "steps": [
  ("md", "## 2 · Demo — the four fields, and what each buys"),
("md", "## 3 · Where it breaks — the silent upgrade"),
("md", "## 4 · The control — record the four, cheapest first"),
],
 "expect": "Only the fully instrumented run is replayable; the typical production "
           "run is missing the model version and seed. Replaying the incident "
           "under two later model versions produces a different action, so the "
           "original run does not reproduce. Adding the two cheapest fields "
           "(model version and seed) makes the typical production run replayable.",
 "challenge": "Add model version and seed to your agent's run records this week. "
              "Both are one field each, and together they are the difference "
              "between forensics and storytelling.",
},

"D2.6": {
 "concept": """
After an incident you change something. For ordinary software that change goes
through code review, CI and a deploy — a process that records what changed and
who approved it.

For an agent the fix may be a prompt, a tool manifest, a model version, a policy
file or an approval toggle. Only some of those go through any process at all,
and the ones that do not are precisely the ones most likely to be adjusted at
2am during an incident.

The consequence is a system whose security-relevant configuration drifts with no
record, and a post-incident action list where half the items cannot be verified
as done six weeks later.
""",
 "steps": [
  ("md", "## 2 · Demo — where post-incident changes actually land"),
  ("html", D.table(
    ["change surface", "in change management?", "what happens today"],
    [["application code", "yes", "pull request, review, CI, deploy"],
     ["agent prompt", "<b>no</b>", "edited in a console, no diff retained"],
     ["tool manifest", "<b>no</b>", "a config change, with no threat-model diff"],
     ["model version", "<b>no</b>", "provider-side; you may not be told"],
     ["policy", "yes", "if it is in git — often it is not"],
     ["approval settings", "<b>no</b>", "a toggle in an admin UI"],
     ["egress allowlist", "sometimes", "depends whether it is IaC or a console"]],
    emphasise=1,
    caption="The same surfaces D1.7 watches for drift. There they were the "
            "things that change without anyone deciding; here they are the "
            "things you change on purpose, after an incident — and four of "
            "seven still leave no record that you did.")),
  ("md", "## 3 · Where it breaks — six weeks later"),
  ("html", D.table(
    ["the action, as written in the report", "where it landed",
     "still verifiable in six weeks?"],
    [["revoke the compromised agent identity", "identity provider", "<b>yes</b>"],
     ["add collect.example.com to the egress denylist", "a console", "no"],
     ["remove read access to /home/app/.aws", "tool manifest", "no"],
     ["require approval for http_post", "an admin toggle", "no"],
     ["add a regression test for the credential read", "code", "<b>yes</b>"],
     ["update the prompt to warn about credential files", "a console", "no"]],
    emphasise=2,
    caption="Two of six survive as something you can check. The other four exist "
            "only in the incident document — and the last of them is not a "
            "control at all: it is a request for the model to behave better, and "
            "the next prompt edit will silently revert it.")),
  ("md", "## 4 · The control — the manifest diff, and a verification date"),
],
 "expect": "Four of seven change surfaces bypass change management. Only 2 of 6 "
           "post-incident actions are verifiable six weeks later, and one of them "
           "is a prompt edit that is guidance rather than a control. The manifest "
           "diff records the gating change with the blast radius dropping from 40 "
           "to 3, and the action review flags the prompt update as weak.",
 "challenge": "Take your last incident's action list and mark each item's landing "
              "surface. Anything landing in a console has no record and no "
              "verification path — move those into git before the next one.",
},

"D2.7": {
 "concept": """
Stop authority is the control everyone assumes exists and almost nobody has
timed.

Five questions decide whether you have it, and each needs a name or a number
rather than an intention:

1. **Who** can halt an agent fleet without seeking approval?
2. **What** is the mechanism — and is it revocation, which survives a restart,
   or process termination, which does not?
3. **How long** does it take, measured end to end, not estimated?
4. **What breaks** when it fires — and has the business already agreed to that?
5. **Who turns it back on**, and against what evidence?

An untested stop button is a belief. The purpose of this lesson is to convert it
into a measurement, because the measurement is what an auditor, a regulator and
a board will each ask for in different words.
""",
 "steps": [
  ("md", "## 2 · Demo — the five questions, answered badly and well"),
("md", "## 3 · Where it breaks — mechanism matters more than speed"),
("md", "## 4 · The control — run the game day and record the number"),
],
 "expect": "The vague and concrete answers print side by side. Killing the "
           "process stops the agent but does not survive a restart, while "
           "identity revocation does. The game-day timeline gives a measured "
           "12-second time-to-stop, permitting 12 to 240 further actions "
           "depending on rate. The readiness check fails the vague version on "
           "three counts and passes the tested one.",
 "challenge": "Run the game day. The deliverable is the number, and the number is "
              "what goes in the evidence pack for E1.7 and the board slide for "
              "E3.5. An untested stop button is a belief.",
},

"D2.8": {
 "concept": """
Regulatory clocks start at **awareness** — the point at which you know a
reportable event may have occurred. Not at confirmation, not at containment.

Two consequences that teams discover on day three:

1. **Containing fast does not buy reporting time.** You can contain in an hour
   and still miss a 72-hour deadline, because the clock never paused.
2. **Broken attribution consumes the clock.** If you cannot say who acted
   (D2.1), scoping takes days, and those days are deadline days.

Containment and disclosure are separate workstreams competing for the same
people. If your runbook has one owner for both, one of them is being done badly
under time pressure.
""",
 "steps": [
  ("md", "## 2 · Demo — the clock under four scenarios"),
("md", "## 3 · Where it breaks — the clock starts earlier than people think"),
("md", "## 4 · The control — separate owners, and a shortest-clock register"),
],
 "expect": "One-hour containment still misses the 72-hour deadline in the "
           "slow-scoping scenario, and broken attribution misses it by 20 hours. "
           "The same incident is met or missed depending on which point is "
           "treated as awareness. The obligation register shows DORA's 4-hour "
           "clock as the binding one, and the runbook check flags a shared owner "
           "and a late clock start.",
 "challenge": "Build your shortest-clock register: every obligation, its deadline, "
              "and who notifies. Then check whether your runbook starts the clock "
              "at awareness or at confirmation. The gap between those two is "
              "often more than a day.",
},
}
