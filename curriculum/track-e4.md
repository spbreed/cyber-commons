# Track E4 — Respond — From a Conclusion to the Actor Stopped

**Function E · The Agentic SOC**  
*Detecting, attributing and stopping an actor that is not a person and does not slow down — built for a fleet of agents like CyberTravels'.*

**Job titles:** Incident Responder, SOAR Engineer, Platform Security Engineer

**What changes:** A response whose blast radius is known before it fires: actions classified on reversibility and radius, tiers derived from that rather than from their author, containment timed against the attacker, and a fleet stop that revokes as well as terminates. 5 lessons.

**Autonomy focus:** Automated revocation of a non-human identity is pre-authorised; the same action against a human is not, and that asymmetry is what makes machine-speed containment safe.

**Deliverable:** A remediation policy and three runbooks, one per tier, each timed end to end against a measured breakout time.

> Every session below ships a runnable agent skill that actually executes on your own machine — against open-weight models and open-source tooling. `python3 scripts/install_skills.py --all` links them into whichever agent CLI you use; see [MODELS.md](../MODELS.md) for getting the models free.

---

### E4.1 — Remediation policy — what may be done without asking

- **Risk** — Automation scope is decided per runbook by whoever wrote it, so the blast radius of the response is unknown until it fires.
- **Control** — One remediation policy keyed on blast radius and reversibility, from which each runbook's tier is derived rather than chosen.
- **Lab** — Classify a set of remediation actions against the policy and see which tier each lands in, and why.
- **Tools** — `OPA`

**Run it** — Classify a set of remediation actions against the policy and see which tier each lands in, and why.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E4.1

# --- 3 · in your agent, open this folder and pick the skill:
#         e4-1-remediation-policy
#         (Claude Code and Copilot: /e4-1-remediation-policy · Cursor: type / and
#         search · Codex: $e4-1-remediation-policy). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E4.1
```

---

### E4.2 — Runbook tiers — fully automated, human in the loop, manual

- **Risk** — Everything is written as fully automated because that is the impressive demo, and the first wrong action is unrecoverable.
- **Control** — Tier assigned from the remediation policy, with the human-in-the-loop tier carrying a real decision point rather than a confirmation dialog.
- **Lab** — Take one incident and run its response at all three tiers, comparing what each costs and what each risks.
- **Tools** — `kagent`

**Run it** — Take one incident and run its response at all three tiers, comparing what each costs and what each risks.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E4.2

# --- 3 · in your agent, open this folder and pick the skill:
#         e4-2-runbook-tiers
#         (Claude Code and Copilot: /e4-2-runbook-tiers · Cursor: type / and
#         search · Codex: $e4-2-runbook-tiers). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E4.2
```

---

### E4.3 — Containment at machine speed

- **Risk** — Mass revocation takes down the business.
- **Control** — Throttle → scope-reduce → reroute → force HITL → revoke → hard stop, in order.
- **Lab** — Exercise the ladder against a live misbehaving agent.
- **Tools** — `agentgateway`, `Keycloak`

**Run it** — Exercise the ladder against a live misbehaving agent.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E4.3

# --- 3 · in your agent, open this folder and pick the skill:
#         e4-3-containment-at-machine-speed
#         (Claude Code and Copilot: /e4-3-containment-at-machine-speed · Cursor: type / and
#         search · Codex: $e4-3-containment-at-machine-speed). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E4.3
```

---

### E4.4 — Stop authority — who halts a fleet, and how long it takes

- **Risk** — Nobody has rehearsed halting an autonomous workflow.
- **Control** — Named holder, measured time-to-stop, tested.
- **Lab** — Time your own stop authority end to end.
- **Tools** — `kagent`

**Run it** — Time your own stop authority end to end.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E4.4

# --- 3 · in your agent, open this folder and pick the skill:
#         e4-4-stop-authority
#         (Claude Code and Copilot: /e4-4-stop-authority · Cursor: type / and
#         search · Codex: $e4-4-stop-authority). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E4.4
```

---

### E4.5 — The fleet kill switch

- **Risk** — Terminating agents while their tokens stay valid leaves the persistence in place. In the incident, third-party access ended when the third party revoked keys — not when the agents stopped.
- **Control** — A tested kill path independent of the agent execution path, snapshot before terminate, revocation in the same action, a measured activation target and named authority to pull it (C8.3).
- **Lab** — Kill a fleet, then check what the revoked-credential step changes about what an attacker still holds afterwards.
- **Tools** — `Vault`, `Kubernetes`

**Run it** — Kill a fleet, then check what the revoked-credential step changes about what an attacker still holds afterwards.

```bash
# --- 1 · the repository. master is the trunk. ---
git clone --branch master https://github.com/spbreed/cyber-commons.git && cd cyber-commons

# --- 2 · link this lesson's skill into your agent, once. On Windows,
#         use `python` where this says `python3`. ---
python3 scripts/install_skills.py --all --lessons E4.5

# --- 3 · in your agent, open this folder and pick the skill:
#         e4-5-the-fleet-kill-switch
#         (Claude Code and Copilot: /e4-5-the-fleet-kill-switch · Cursor: type / and
#         search · Codex: $e4-5-the-fleet-kill-switch). It ends with a readback. ---

# --- or, with no agent, run the same lesson yourself ---
python3 scripts/lesson.py E4.5
```

---
