"""The agentic penetration-testing lessons, B2.10-B2.14.

B2.10 is the offensive loop and its containment (it began life as C1.1, when
Function C still mixed pentesting with model red teaming). B2.11-B2.13 are the
same loop under white-, black- and grey-box access, and B2.14 is the safety
preflight every offensive engagement runs inside. Kept in one file because they
are one arc; `exercises/__init__.py` merges it like any other track.
"""
from __future__ import annotations

from . import diagrams as D
from .skills import skill_steps

EXERCISES: dict[str, dict] = {

"B2.10": {
 "concept": """
Penetration testing has always been a loop: **recon → hypothesis → test →
escalate → report.** What has changed is who runs each turn.

**Manual (still the baseline).** A human runs `nmap`, reads the output, forms a
hypothesis, tries it. Slow, and the quality is entirely the tester's.

**Scripted.** The recon is automated — Nuclei templates, a Burp scan. The
hypothesis and the escalation are still human. This is where most teams are.

**Semi-autonomous.** An open-weight model reads the recon output and *proposes*
which findings are worth chasing and what to try next. The human approves each
action. The gain is triage speed on a large surface: 400 findings ranked in
minutes rather than a day.

**Autonomous.** The model proposes and the harness executes, within a
pre-approved scope and tool set, verifying its own results. This is real and it
works, and it is also where the engagement becomes a safety problem — because an
agent that has not understood the scope will happily test something outside it
at machine speed.

The professional obligations do not change with autonomy. They get harder,
because scope enforcement can no longer live in the tester's attention — it has
to live in the harness, and then underneath the harness in the network.

The three lessons after this one are the same loop run with different access:
**white box** with the source (B2.11), **black box** from outside with no
credential (B2.12), and **grey box** with one credential per role (B2.13).
What changes between them is not the tooling — it is what a finding is allowed
to claim, and B2.14 is the controls all three run inside.

That second half is why containment belongs in this lesson rather than in a
later one. An offensive harness has a property no other agent has: **everything
it reads is hostile by design.** Banner strings, error bodies, file contents —
all of it comes from a system you are attacking, which may itself already be
attacker-controlled. Containment there protects three parties at once: the
client (scope and rate limits, so you do not break their production), everyone
else (egress control, so a compromised harness cannot pivot outward), and you
(findings and client data must not leave by a route the agent chooses).
""",
 "steps": [
("md", "## 2 · Demo — the four generations on the same recon output\n\n"
         "Realistic scan output from an authorised engagement against hosts you "
         "own. The question at every generation is the same: what do I chase first?"),
("md", "## 3 · Where it breaks — generation 4, and the scope problem\n\n"
         "The model's top-ranked item is correct. Its reasoning on F-06 is also "
         "correct — *out of scope, do not touch*. Now make it autonomous and "
         "remove the human from the loop. What stops it acting on a finding it "
         "has correctly identified as out of scope?\n\n"
         "Nothing in the model. Its judgement about scope is a *proposal*, on the "
         "decision plane, exactly like everything else it produces."),

  ("md", "## 5 · The control — and the layer underneath it\\n\\n"
         "The scope check above lives in the harness, which is one process away "
         "from the loop it constrains. On an engagement a single control is a "
         "single point of failure, and the failure is a professional incident. "
         "The same rule therefore gets restated where the agent cannot reach it: "
         "the sandbox's own request path."),
  *skill_steps('redteam/offensive-agent-containment',
               "## 2 · The procedure, as a skill\n\nModel triage beats severity sorting on CyberTravels' findings and correctly calls the partner CDN out of scope — and can be argued into calling it critical. The skill runs both, then re-runs with scope enforced outside the model, where the persuaded model still proposes the call and nothing acts on it."),
],
 "expect": "Severity sorting puts 2 of 3 exploitable findings in the top 3; model "
           "triage puts 3 of 3, and correctly reasons that the partner CDN is out "
           "of scope. With the model adversarially convinced that the "
           "out-of-scope host is critical, the unenforced harness acts on it and "
           "the enforced harness refuses. Underneath the harness the sandbox "
           "refuses three requests for three different reasons — rate limit, "
           "engagement boundary, and cloud metadata — without consulting the model "
           "at all.",
 "challenge": "Write your engagement scope as a data structure your harness reads, "
              "not as a paragraph in a PDF. Then ask what your current tooling "
              "would do if a target redirected to a host you were not authorised "
              "to touch.",
},




"B2.11": {
 "concept": """
White box is the engagement where you are handed everything: the repository at a
pinned commit, the dependency lock, the IaC plan, the tool and MCP manifests,
the IAM policy, the API schema. An agent with all of that can enumerate more in
an afternoon than a black-box tester finds in a week.

It can also produce the least useful report in security, and usually does: a
list of every sink that exists, with no statement about whether anything reaches
them or who is allowed to. That list is unactionable in exactly the way a
scanner dump is, which wastes the access.

Two distinctions turn the dump into findings, and both are cheap once the agent
has drawn the paths rather than the sinks.

**Reachability.** A sink with no path from any entry point is a different object
from one with three. Report the unreachable ones *as* unreachable — they are one
feature away from being findings, and the feature that adds the route will not
re-run this analysis.

**Authentication is not authorisation.** `session` proves the caller is
somebody. `owner == caller` proves they are entitled to *this* object. A
reachable path carrying only the first kind is the shape of every BOLA finding,
and it is the shape of the CyberTravels refund incident — the caller was
authenticated from end to end.

The data sources are the point of the mode: name which one establishes each
fact, and the finding is checkable rather than asserted.
""",
 "steps": [
  ("md", "## 2 · Demo — what the engagement was handed, and what each source proves"),
  ("md", "## 3 · Where it breaks — a sink list with no reachability is a scanner dump"),
  ("md", "## 4 · The control — paths, predicates, and the authn/authz split"),
  *skill_steps('redteam/whitebox-path-reachability',
               "## 2 · The procedure, as a skill\n\nThe skill enumerates paths from four CyberTravels entry points to their sinks, classifies the predicate on each hop as authentication or authorisation, and separates reachable sinks from ones that are merely present."),
],
 "expect": "Of seven sinks in the tree, five are reachable from an entry point "
           "and two are reported as present-but-unreachable rather than dropped. "
           "Three of the reachable five carry only a session or service-account "
           "check — authentication, not authorisation — including the refund "
           "path, which is the incident's shape stated before the incident.",
 "challenge": "Take one endpoint in your own estate and trace it to its sink by "
              "hand. Count the hops that check the caller is somebody against the "
              "hops that check they own this object. If the second count is zero, "
              "you have found your first finding.",
},

"B2.12": {
 "concept": """
Black box is the mode with the least information and the most room to narrate.
An agent handed status codes, headers, error strings and timings will produce a
fluent architecture, and every sentence of it will be plausible. Some of it is
entailed by the evidence. Most of it is not, and the report does not separate
them unless you make it.

The single discipline is provenance per claim. For each thing the agent wants
to assert, keep the actual observation beside it and ask one question: does this
evidence *entail* the claim, or is it merely *consistent* with it?

- A 404 on a random id is consistent with a missing object **and** with correct
  authorisation refusing you. It entails neither.
- A `csrftoken` cookie is consistent with Django and with anything that copied
  its conventions.
- 1.9-second latency on refunds is consistent with synchronous processing and
  with a dozen other causes.

Observed claims are findings. Inferred ones are open questions, and they carry
**no severity** — because an inference with a CVSS number beside it reads as a
finding to everyone downstream, and the person who has to retract it is never
the person who wrote it.

The open questions are not filler. Each one says what mode would resolve it, and
the ones that need a second credential are telling you the engagement should
become grey box (B2.13) rather than a more elaborate black-box guess.
""",
 "steps": [
  ("md", "## 2 · Demo — twelve claims from an external probe, with their evidence"),
  ("md", "## 3 · Where it breaks — the fluent architecture the evidence does not support"),
  ("md", "## 4 · The control — observed vs inferred, and no severity on a guess"),
  *skill_steps('redteam/blackbox-claim-provenance',
               "## 2 · The procedure, as a skill\n\nThe skill takes twelve claims from an external probe of CyberTravels, splits them on whether the evidence entails or merely suggests each, and reports findings and open questions separately — with a severity on neither guess."),
],
 "expect": "Five claims are entailed by their evidence and reported as findings; "
           "seven are only consistent with it and become open questions with no "
           "severity attached. The one that matters — whether the refund endpoint "
           "accepts a booking it does not own — is untestable with one account, "
           "so it is escalated to a grey-box test rather than guessed at.",
 "challenge": "Take your last external report and mark every claim observed or "
              "inferred. The inferred ones that carry a severity are the ones a "
              "client can disprove, and disproving one is how they learn to "
              "discount the rest.",
},

"B2.13": {
 "concept": """
Grey box is the mode that can actually find broken object-level authorisation,
because it holds more than one identity. It is also the mode most often reported
wrong, because the engagement touches every endpoint, calls itself complete, and
never notices that authorisation is a property of the **cell** — this role, this
object, this verb — and not of the endpoint.

The matrix is the whole method. Roles down one axis, objects and verbs across
the other, and every cell in one of three states: tested, with what came back;
mismatched, where the estate disagrees with the design; or **untested**, which
is data rather than a gap to hide.

Two numbers fall out that an endpoint-coverage report cannot produce. The
mismatches are the findings. The untested cells, ranked by what a wrong answer
would cost rather than by the order the endpoints appear in the schema, are the
backlog — and the coverage fraction is what stops "we tested everything"
standing when 40% of the cells were never sent a request.

One credential per role is the minimum and the enabling fact. With one account
you can test that a feature works; the second account is what turns a
functionality test into a security test.
""",
 "steps": [
  ("md", "## 2 · Demo — three roles, five objects, two verbs, thirty cells"),
  ("md", "## 3 · Where it breaks — every endpoint touched, most cells untested"),
  ("md", "## 4 · The control — the matrix, its mismatches, and the ranked gaps"),
  *skill_steps('redteam/greybox-authorization-matrix',
               "## 2 · The procedure, as a skill\n\nThe skill fills the roles-by-objects-by-verbs matrix for CyberTravels against what the design intends, flags the cells where the estate disagrees, and ranks the untested cells by blast radius rather than by schema order."),
],
 "expect": "The engagement exercises 12 of 30 cells (40%) and finds two "
           "mismatches — a traveller reading another traveller's booking and the "
           "agent service writing one — while the two highest-cost cells, both "
           "on the audit log, were never sent a request. Endpoint coverage would "
           "have called this complete.",
 "challenge": "Build the matrix for one service you own with two real accounts. "
              "The cell you least want to test — an admin verb on another "
              "tenant's object — is the one whose result you most need to know.",
},

"B2.14": {
 "concept": """
An offensive agent is the most capable and least supervised thing in the estate.
It scans, reasons and exploits at machine speed, on credentials you issued,
against systems you care about — and its traffic is, by design,
indistinguishable from an attack. That combination is why the controls go on
*before* it starts, and why this is a gate rather than a checklist.

Seven controls, and six of them are **blocking** — the engagement does not begin
without them, because each one's absence is invisible until it has already cost
something:

- **zero data retention** — the provider keeps no prompts or completions, so
  target data does not enter a third party's training set;
- **sandboxing** — a disposable workspace, so a payload that escapes lands
  nowhere that matters;
- **egress control** — an allowlist, so a compromised harness cannot pivot;
- **secret management** — credentials injected at call time, never in a prompt
  or a repo;
- **human in the loop** — a named approver on every destructive action;
- **deterministic guardrails** — scope and rate enforced *outside* the model,
  because scope the model is merely asked to respect can be argued away.

The seventh, **SOC notification**, is advisory — not because it matters less,
but because its absence is recoverable: you can pick up the phone mid-engagement.
And the brief carries one instruction the SOC skips at its peril — do not mute
the rules. An engagement your own detection team suppressed produces a clean
report and no evidence anything would have been caught, which was half the
reason to run it.
""",
 "steps": [
  ("md", "## 2 · Demo — two engagement configurations through the preflight"),
  ("md", "## 3 · Where it breaks — the quick-look run that skips the invisible controls"),
  ("md", "## 4 · The control — refuse with a reason, then brief the SOC"),
  *skill_steps('redteam/offensive-agent-safety-preflight',
               "## 2 · The procedure, as a skill\n\nThe skill runs two CyberTravels engagement configurations through the preflight, refuses the one missing blocking controls with the reason for each, and prints the SOC brief for the one that may start."),
],
 "expect": "The quick-look configuration is refused with four blocking controls "
           "named — zero retention, egress allowlist, human in the loop and "
           "deterministic guardrails — while the fully configured engagement is "
           "cleared and produces a SOC brief with its window, source addresses "
           "and expected signatures, ending on the instruction not to mute.",
 "challenge": "Write your own engagement scope as a structure the harness reads, "
              "not a paragraph in a PDF, and run this preflight against it. The "
              "control you cannot currently satisfy is the one to fix before the "
              "next engagement, not after it.",
},

}
