# Track A3 — The Platform & Cloud Security Engineer

**Function A · Security Architecture & Platform**  
*The people who decide what is structurally possible. If they get it wrong, no amount of downstream diligence recovers it.*

**Job titles:** Cloud Security Engineer, Platform Security Engineer, Infrastructure Security

**What changes:** The sandbox is your product. Permission prompts inside the agent are somebody else's defence-in-depth; the boundary is yours.

**Autonomy focus:** Containment is what lets you say yes to L2.5 without pretending the agent is trustworthy.

**Deliverable:** A hardened runtime that survives a deliberate injected payload with a measured blast radius of zero outside the sandbox.

> Prerequisite: [Module 0](module-0.md). Every session below ships commands that actually execute — against open-weight models and open-source tooling. See [MODELS.md](../MODELS.md) for getting the models free.

---

### A3.1 — Sandboxing is the perimeter

`Security of AI`

- **Risk** — Tier chosen by convenience, not by action class.
- **Control** — Process → container → microVM → ephemeral workstation → air-gapped runner, chosen deliberately.
- **Lab** — Run the same agent in three tiers and measure escape surface in each.
- **Tools** — `gVisor`, `Firecracker`, `Docker`
- **Models** — `Llama 3.3`

**Run it** — Measure escape surface across three sandbox tiers.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.1.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.1   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a3-sandbox
./run-tier.sh docker      && ./measure-escape.sh
./run-tier.sh gvisor      && ./measure-escape.sh
./run-tier.sh firecracker && ./measure-escape.sh
```

*Expect:* A table of syscall surface and reachable host resources per tier — a number you can put in a design review.

---

### A3.2 — Egress control for agents

`Security of AI`

- **Risk** — An agent with unrestricted egress has no other meaningful control.
- **Control** — Allowlists, inspecting proxies, DNS conditional forwarding, data perimeters.
- **Lab** — Put a Squid allowlist in front of an agent and watch exfiltration fail.
- **Tools** — `Squid`, `Cilium`, `Kyverno`
- **Models** — `GLM-4.6`

**Run it** — Prove an agent with no egress control has no other meaningful control.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.2.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.2   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a3-sandbox
docker compose up -d squid agent
./exfil.sh            # baseline: data leaves
./apply-allowlist.sh  # squid allowlist + DNS conditional forwarding
./exfil.sh            # same payload, now blocked
```

*Expect:* Identical agent, identical payload; the only variable is egress policy.

---

### A3.3 — Filesystem and path guards

`Security of AI`

- **Risk** — The agent iterating on code wanders into credentials.
- **Control** — Workspace scoping, mount discipline, ephemeral state.
- **Lab** — Attempt credential read from inside the sandbox; close it with mount policy.
- **Tools** — `Docker`, `Kyverno`

**Run it** — Stop the agent wandering from code into credentials.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.3.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.3   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a3-sandbox
./run-agent.sh --workspace /work --task 'read ../../.aws/credentials'   # succeeds: bad
./apply-mounts.sh   # workspace scoping + ephemeral state
./run-agent.sh --workspace /work --task 'read ../../.aws/credentials'   # denied
```

*Expect:* Same task, same agent; only the mount discipline changed.

---

### A3.4 — MCP is not a security boundary

`Security of AI`

- **Risk** — Connector chaining as privilege escalation; unpinned servers.
- **Control** — Server scanning, version pinning with hash verification, self-hosting.
- **Lab** — Chain two MCP connectors to escalate, then pin and scan to stop it.
- **Tools** — `kmcp`, `MCP Inspector`, `Sigstore`
- **Models** — `GLM-4.6`

**Run it** — Escalate through connector chaining, then pin and scan to stop it.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.4.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.4   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a3-sandbox/mcp
python3 chain.py --from filesystem --to http   # exfil via two 'safe' connectors
kmcp scan ./servers/ && kmcp pin --hash-verify
python3 chain.py --from filesystem --to http   # blocked
```

*Expect:* Neither connector is dangerous alone. The chain is the vulnerability.

---

### A3.5 — Tool permission models

`Security of AI`

- **Risk** — The confused deputy at the tool layer.
- **Control** — Capability scoping, allowlisted actions, structured output contracts, read-only defaults.
- **Lab** — Redesign a dangerous tool so the dangerous call doesn't exist.
- **Tools** — `kmcp`, `OPA`

**Run it** — Design the dangerous call out of existence.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.5.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.5   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a3-sandbox/tools
python3 audit_tools.py --manifest before.json   # finds an unrestricted shell tool
python3 refactor.py --split shell --into read_file,list_dir,run_tests
python3 audit_tools.py --manifest after.json
```

*Expect:* The capability the agent needed survives; the arbitrary-execution path does not exist to block.

---

### A3.6 — Runtime containment levers

`Security of AI`

- **Risk** — The stop lever is built during the incident.
- **Control** — Throttle, scope-reduce, reroute, force HITL, hard stop — built and tested first.
- **Lab** — Wire all five levers and prove each fires under load.
- **Tools** — `Falco`, `Kyverno`, `kagent`

**Run it** — Build the five containment levers before you need them.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.6.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.6   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a3-sandbox/levers
./arm.sh              # throttle, scope-reduce, reroute, force-HITL, hard-stop
./fire.sh --lever all --under-load
./assert-fired.sh
```

*Expect:* Each lever fires under load and is timed. A lever that only works when idle is not a lever.

---

### A3.7 — The unmanaged agent problem

`Security of AI`

- **Risk** — Personal, non-sandboxed agents on managed endpoints.
- **Control** — Endpoint + secure web gateway, behavioural monitoring — with an honest account of the gap.
- **Lab** — Detect an unmanaged local agent by its egress and filesystem signature.
- **Tools** — `Falco`, `osquery`

**Run it** — Detect an unmanaged personal agent on a managed endpoint.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.7.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.7   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a3-sandbox
sudo falco -r rules/unmanaged-agent.yaml &
./simulate-personal-agent.sh   # local model + outbound tool calls
grep 'unmanaged_agent' /var/log/falco.log
```

*Expect:* Detected by egress + filesystem signature. Read the chapter's honest note on why this case has no clean answer yet.

---

### A3.8 — Environment separation

`Security of AI`

- **Risk** — "The agent knows not to" is not separation.
- **Control** — Dev-agent credentials structurally unable to reach production.
- **Lab** — Prove the dev SVID cannot mint a prod token, by construction.
- **Tools** — `SPIRE`, `OPA`

**Run it** — Make dev-agent credentials structurally unable to reach production.

```bash
# --- the notebook: runs anywhere, stdlib only, no install ---
jupyter notebook labs/notebooks/A3.8.ipynb    # or open it on the lesson page
python3 scripts/run_notebooks.py --session A3.8   # run it headless and check it

# --- the full variant, against the real tooling (needs a container registry) ---
cd labs/a3-sandbox
./try-cross-env.sh --from dev-agent --to prod-api   # must fail
python3 prove_separation.py --spiffe-id spiffe://cybercommons/dev/agent
```

*Expect:* The dev SVID cannot mint a prod token by construction — not because a policy said no.

---
