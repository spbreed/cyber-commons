#!/usr/bin/env python3
"""Bind a grant to one scope, one resource and one task, and show what it refuses once the task closes.

This is the executable half of the `entitlement-overprivilege-analyzer` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

GRANTS = {}
CLOCK = {"now": 1000}

def grant(task_id, principal, scope, resource, ttl=120):
    """Purpose-bound: this scope, on this resource, for this task."""
    GRANTS[task_id] = {"principal": principal, "scope": scope, "resource": resource,
                       "expires": CLOCK["now"] + ttl, "open": True}
    return task_id

def use(task_id, scope, resource):
    g = GRANTS.get(task_id)
    if not g:                                return False, "no such grant"
    if not g["open"]:                        return False, "task closed"
    if CLOCK["now"] > g["expires"]:          return False, "expired"
    if scope != g["scope"]:                  return False, f"scoped to {g['scope']}"
    if resource != g["resource"]:            return False, f"bound to {g['resource']}"
    return True, "permitted"

def close(task_id):
    if task_id in GRANTS:
        GRANTS[task_id]["open"] = False       # revoked on completion, not on expiry

grant("t-1", "dana@corp", "reports:write", "report/8812")

attempts = [
 ("the task's own write",        "reports:write", "report/8812"),
 ("a different report",          "reports:write", "report/9999"),
 ("a different scope",           "db:admin",      "report/8812"),
]
for label, scope, resource in attempts:
    ok, why = use("t-1", scope, resource)
    print(f"   {label:26s}{'ok' if ok else 'REFUSED':8s}{why}")

close("t-1")
ok, why = use("t-1", "reports:write", "report/8812")
print(f"   {'after the task completes':26s}{'ok' if ok else 'REFUSED':8s}{why}")

CLOCK["now"] = 2000
GRANTS["t-2"] = dict(GRANTS["t-1"], open=True, expires=1500)
ok, why = use("t-2", "reports:write", "report/8812")
print(f"   {'after the TTL expires':26s}{'ok' if ok else 'REFUSED':8s}{why}")
print()
print("An injection landing at 09:14 needs a task to be open, on the resource")
print("it wants, holding the scope it wants. Standing authority required none")
print("of those three things to line up.")
assert use("t-1", "reports:write", "report/8812")[0] is False
