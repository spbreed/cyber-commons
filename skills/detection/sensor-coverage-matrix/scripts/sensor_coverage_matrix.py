#!/usr/bin/env python3
"""Score the sensor classes an estate already owns against what an agent actually does.

This is the executable half of the `sensor-coverage-matrix` skill: the check the
SKILL.md next to it describes, run against the CyberTravels estate so two runs
can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle kernel with the
internet switched off.
"""

# Four sensor classes almost every estate has bought, with an open-source
# reference product so the claim is checkable rather than vendor-shaped.
SENSORS = [
    ("EDR",   "Wazuh agent",          "process, file and network activity on a host"),
    ("DLP",   "regex + Wazuh FIM",    "sensitive content leaving a monitored channel"),
    ("CSPM",  "Prowler / ScoutSuite", "cloud configuration, evaluated periodically"),
    ("CNAPP", "Falco + Trivy",        "container runtime syscalls and image contents"),
]

# What CyberTravels' agents do in an ordinary day. Each row records, per sensor,
# whether it sees the action at all — not whether it would alert on it.
#   full    the action is visible with enough fidelity to reason about
#   partial something is visible, but not the part that decides
#   none    the sensor is not in the path
ACTIONS = [
    ("write a file into the agent workdir",        {"EDR": "full",    "DLP": "none",    "CSPM": "none",    "CNAPP": "full"}),
    ("open an outbound TLS session to a model API", {"EDR": "partial", "DLP": "none",    "CSPM": "none",    "CNAPP": "partial"}),
    ("read a customer record through an internal API", {"EDR": "none", "DLP": "none",    "CSPM": "none",    "CNAPP": "none"}),
    ("place 900 tokens of that record in a prompt", {"EDR": "none",    "DLP": "none",    "CSPM": "none",    "CNAPP": "none"}),
    ("call a vendor MCP tool",                     {"EDR": "none",     "DLP": "none",    "CSPM": "none",    "CNAPP": "none"}),
    ("issue a refund through the payments API",    {"EDR": "none",     "DLP": "none",    "CSPM": "none",    "CNAPP": "none"}),
    ("assume a wider IAM role",                    {"EDR": "none",     "DLP": "none",    "CSPM": "partial", "CNAPP": "none"}),
    ("spawn a child agent process",                {"EDR": "full",     "DLP": "none",    "CSPM": "none",    "CNAPP": "full"}),
    ("exfiltrate to an allowed SaaS domain",       {"EDR": "partial",  "DLP": "partial", "CSPM": "none",    "CNAPP": "partial"}),
]

WEIGHT = {"full": 1.0, "partial": 0.5, "none": 0.0}
MARK = {"full": "##", "partial": "..", "none": "  "}


def main() -> int:
    names = [s[0] for s in SENSORS]

    print("the sensor estate, as bought")
    for name, product, sees in SENSORS:
        print(f"  {name:<6} {product:<22} {sees}")

    width = max(len(a) for a, _ in ACTIONS)
    print(f"\ncoverage of what the agents actually do  "
          f"(## full  .. partial  blank none)\n")
    print(f"  {'action':<{width}}  " + "  ".join(f"{n:<5}" for n in names))
    uncovered = []
    for action, row in ACTIONS:
        cells = "  ".join(f"{MARK[row[n]]:<5}" for n in names)
        print(f"  {action:<{width}}  {cells}")
        if all(row[n] == "none" for n in names):
            uncovered.append(action)

    print("\nper-sensor coverage of the agent's day")
    for n in names:
        got = sum(WEIGHT[row[n]] for _, row in ACTIONS)
        print(f"  {n:<6} {got:>4.1f} / {len(ACTIONS)}   "
              f"{got / len(ACTIONS):.0%}")

    best = max(names, key=lambda n: sum(WEIGHT[row[n]] for _, row in ACTIONS))
    union = sum(max(WEIGHT[row[n]] for n in names) for _, row in ACTIONS)
    print(f"\n  best single sensor   {best}")
    print(f"  all four combined    {union:.1f} / {len(ACTIONS)}   "
          f"{union / len(ACTIONS):.0%}")

    print(f"\n{len(uncovered)} of {len(ACTIONS)} actions are seen by NO sensor class:")
    for a in uncovered:
        print(f"  - {a}")
    print("\nnote what they have in common: every one of them happens inside the")
    print("agent's reasoning loop or behind an API the host never observes.")
    print("buying a fifth product of the same four kinds does not move this column.")
    print("D1.3 is the source that does, and D2.1 is where it has to land.")

    assert union < len(ACTIONS), "a full-coverage estate would make this lesson wrong"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
