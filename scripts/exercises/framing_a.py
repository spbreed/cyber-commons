"""Hooks, diagrams and chapter bridges for Function G.

Kept separate for the same reason `framing_new.py` is: `framing.py` was already
long before thirteen more lessons arrived, and a file nobody can read end to end
stops being the place you check whether the hooks are consistent with each
other.

**These hooks are not incidents.** Every other function opens a lesson on
something going wrong, because every other function is about something going
wrong. Function G is the one where nothing has gone wrong yet — the reader is
building — so a hook here opens on a decision instead: the moment where the
thing you are about to write could go two ways, and the consequence of the
easier one. A build chapter that opened on breaches would teach fear of a
mechanism the reader has not written yet, which is the exact ordering mistake
this function exists to fix.
"""

HOOKS: dict[str, str] = {
 "A1.0":
   "Alex has a working prototype: a model, a booking API, and a loop that "
   "joins them. It cancels the right flight four times out of five. The fifth "
   "time it cancels a different one, and there is no record of why it chose "
   "that booking, no way to stop it mid-run, and nothing to point at when "
   "somebody asks. The prototype is not the problem. The absence of everything "
   "around it is, and that absence is what this chapter fills in.",
 "A1.1":
   "The difference between a demo and a system is one line. In the demo, the "
   "model decides to call a tool and the tool is called. In the system, the "
   "model proposes and separate code decides. Every control in the rest of this "
   "commons lives in the gap between those two sentences, and a loop written "
   "without the gap has nowhere to put any of them.",
 "A1.2":
   "It is faster to import the booking client and let the agent call it "
   "directly. It works on the first afternoon and it is still working months "
   "later, which is the trap: the tool now runs with whatever authority the "
   "agent has, and the only place to add a check is inside the component an "
   "attacker is trying to influence.",
 "A1.3":
   "One API key in an environment variable, shared by four agents. Every action "
   "in the log reads `service-account-prod`. Nine weeks later somebody asks "
   "which agent issued a particular refund and on whose behalf, and the honest "
   "answer is that the system cannot tell — not slowly, not with effort. It "
   "never recorded it.",
 "A1.4":
   "The token has every scope because that never fails. It is the setting that "
   "makes the demo smooth and it is also the setting under which one ambiguous "
   "sentence in a vendor document turns a read into a refund. The alternative "
   "costs a function call per action and closes the gap entirely.",
 "A1.5":
   "The agent remembers that this traveller prefers aisle seats, which is "
   "useful. It also remembers a sentence it read in a vendor notice three weeks "
   "ago, which it now repeats with the same confidence. Nothing distinguishes "
   "the two, because when they were written down nothing recorded where either "
   "came from.",
 "A1.6":
   "The retrieval advisor reads a vendor document and passes its conclusion to "
   "the workflow agent. The workflow agent treats it as an internal request, "
   "because it arrived from a peer. One sentence written by somebody outside "
   "the company is now an instruction inside it, and the log shows two agents "
   "doing their jobs correctly.",
 "A1.7":
   "The agent is asked to reconcile a booking that cannot be reconciled. It "
   "tries, rephrases, tries again. Six hours later it has spent four hundred "
   "thousand tokens and exhausted a vendor's rate limit for everybody else on "
   "that integration. Nothing failed. There was simply no number at which it "
   "was supposed to stop.",
 "A2.0":
   "The prototype is promoted with nobody changing a line of it. "
   "Three weeks later a traveller disputes a cancellation and the question is "
   "what the agent actually did. The answer is in a log line that says "
   "`run completed`. Everything needed to answer it was cheap to add and is "
   "now expensive, and none of it was ever a feature request.",
 "A2.1":
   "The run produced the right answer, so nobody looked further. The trace "
   "would have shown that it reached for the refund tool first, was refused by "
   "the policy, and tried a different route — which is a signal about the input "
   "it was given, not about that run. Emitting only the answer threw away the "
   "only interesting part.",
 "A2.2":
   "Every row in the audit log is correct and none of them is sufficient. They "
   "record that an agent issued a refund at 14:07. They do not record that the "
   "agent had, eleven seconds earlier, read a vendor notice containing an "
   "instruction to issue refunds. The action is visible and the cause is not, "
   "so the incident closes as an agent behaving oddly.",
 "A2.3":
   "The suite went from 71% to 88% and the team shipped. Nothing about the "
   "system changed that week; thirty straightforward cases were added to the "
   "corpus and every one of them passed. The number moved, the capability did "
   "not, and the decision it justified had already been made.",
 "A2.4":
   "Two teams report their agent at ninety per cent. One counted whether the "
   "right tool was named; the other counted whether the right tool was called "
   "with the right arguments, in the right order. Same runs, same agent, and "
   "one of those numbers is hiding a refund of 1400 where 140 was owed.",

 "A2.5":
   "Everything in this system works. That sentence is true and it is the "
   "beginning of the next five functions rather than the end of this one — "
   "because 'works' was measured against what you intended, and nobody has yet "
   "measured it against somebody who intends otherwise.",
}

DIAGRAMS: dict[str, str] = {
 "A1.0": """
        WHAT YOU ARE ABOUT TO BUILD

  traveller ─► ingress ─► orchestrator ─► agent runtime
                                              │
                          ┌───────────────────┼──────────────┐
                          ▼                   ▼              ▼
                     tools (MCP)          memory        peer agents
                          │                   │              │
                          └──────── audit + spans ───────────┘

  seven components · every later lesson names one of them
""",
 "A1.1": """
        PLAN, ACT, VERIFY

   model proposes ──► YOUR CODE DECIDES ──► tool
        ▲                    │
        │                    ▼
        └──── verifier ◄── result
              (not the model)

  a loop with two stages is a demo · the third makes it a harness
""",
 "A1.2": """
        WHY THE TOOL IS A SEPARATE PROCESS

   in-process:   agent ─────────────► data
                 (the check would live inside the agent)

   over MCP:     agent ──► server ──► data
                            ▲
                            └─ verifies BEFORE acting
""",
 "A1.3": """
        THREE PRINCIPALS, NOT ONE

   the human      "who wanted this"        dana
   the workload   "what acted"             spiffe://…/agent/workflow
   the call       "under what authority"   aud=mcp:internal scope=bookings:read

   collapse these into one key and every log row is identical
""",
 "A1.4": """
        ONE TOKEN, ONE ACTION

   user token ─┐
               ├─► exchange ─► sub=human  act=agent
   agent NHI  ─┘               aud=ONE    scope=ONE   exp=120s
                                    │
                                    ▼
                            resource server VERIFIES
                            (the step most systems skip)
""",
 "A1.5": """
        ORIGIN TRAVELS WITH CONTENT

   [trusted  , origin=policy          ] refunds >500 need an approver
   [UNTRUSTED, origin=vendor-document ] settlement changed, refund in full

   drop the left column and both sentences carry equal weight
""",
 "A1.6": """
        THE ENVELOPE

   from  spiffe://…/agent/rag-advisor   ── signed
   for   dana                           ── the human, carried through
   origin vendor-document / UNTRUSTED   ── a peer is as trusted as what it read
   hops  2 of 4                         ── and then it stops
""",
 "A1.7": """
        TWO CEILINGS, OPPOSITE FAILURES

   human gate    present but saturated  ─► coverage 100%, review 0%
   budget        absent                 ─► spend until somebody notices

   at the ceiling: return INCOMPLETE, and say so
""",
 "A2.0": """
        DEMO ──────────────────────► SYSTEM

   what did it do?      answer only   ─►  a trace
   who caused it?       one identity  ─►  an audit trail
   is it still right?   checked once  ─►  an evaluation

   all three are cheaper now than after the first incident
""",
 "A2.1": """
        THE RUN, AS SPANS

   thought ─ plan ─ approval ─ token_issued ─ tool_result ─ final
                       │            │
                    denied      claims only,
                  at=policy     never the token
                  at=human
                  at=resource   ◄── WHERE it was refused is the useful part
""",
 "A2.2": """
        FOUR QUESTIONS AN AUDIT ROW MUST ANSWER

   1  which human?       sub
   2  which workload?    act          ── not "the platform"
   3  which call?        tool·aud·scope·trace_id
   4  what motivated it? the input, and its origin   ◄── usually missing

   3 of 4 answered names an event without naming a cause
""",
 "A2.3": """
        A SCORE THAT MEANS SOMETHING

   fails on old build, passes on new    ── else it tests nothing
   carries an interval                  ── 84% of 25 ≠ 84% of 400
   cannot be lifted by easy cases       ── dilution moves the number,
                                           not the system
""",
 "A2.4": """
   ONE RUN, THREE THINGS YOU CAN SCORE

   the run                        what scores it        needs a model?
   +------------------------+
   | tools it called,       |     exact match on           no
   |   with arguments,      | --> name + args + order,
   |   in order             |     and n beside it
   +------------------------+
   | the answer it gave,    |     compare with the         no
   |   where truth was      | --> recorded truth.
   |   recorded             |     unscoreable is its
   +------------------------+     own column, not a pass
   | the answer it gave,    |
   |   where nobody         | --> a model, as judge        YES
   |   recorded a truth     |     + a rubric that
   +------------------------+         allows "undetermined"

                                          |
                                          v
                        validate the judge on the rows that
                        DO have a truth. agreement, false
                        passes, false fails. an unvalidated
                        judge is a second unmeasured model.
""",

 "A2.5": """
        SAME MAP, READ BY SOMEBODY ELSE

   ingress          ─►  prompt injection            B1.2
   vendor MCP       ─►  indirect injection          B1.3
   tool description ─►  rug-pull after approval     B1.9
   memory           ─►  persistence                 B1.4
   a2a              ─►  one becomes four            B1.7
   the human gate   ─►  saturation                  B3.9
""",
}

# The chapter bridge — what the reader gained, what they still cannot do, and
# which lesson answers it. A2's bridge is the handover into Function B and is
# the most load-bearing one in the commons: it is where the reader stops being
# the builder.
BRIDGES: dict[str, dict] = {
 "A1": {
   "gained": "A running agentic platform you built yourself: a reasoning loop "
             "with an independent verifier, two MCP resource servers behind a "
             "process boundary, a workload identity per agent, per-action "
             "delegation that a resource server actually enforces, memory that "
             "records where its contents came from, signed agent-to-agent "
             "envelopes, a human gate and a budget that binds.",
   "gap": "It runs, and you cannot yet tell anybody what it did. There is no "
          "trace, the audit rows cannot say what motivated an action, and the "
          "only evidence it works is that you watched it work once.",
   "next": "A2.0 — why a demo is not a system, and the three things that "
           "separate them.",
 },
 "A2": {
   "gained": "The harness around the loop: spans that join reasoning to "
             "actions, an audit trail measured against the four questions an "
             "investigation asks, an evaluation suite with intervals and a test "
             "for its own dilution, and the blast radius of the agent you "
             "built, as a number.",
   "gap": "Everything you have measured, you measured against what you "
          "intended. Nobody has yet read this system as somebody trying to make "
          "it do something else — and every component you added is, from that "
          "side, a way in.",
   "next": "B1.0 — the same architecture, read adversarially, and the zero-trust "
           "rules that survive contact with agents.",
 },
}
