#!/usr/bin/env python3
"""Qualify every surface two agent runs share as a channel, then close them one control at a time.

This is the executable half of the `shared-surface-channel-audit` skill: the check the
SKILL.md next to it describes, run against a synthetic CyberTravels
estate so two runs can be diffed and the result argued with.

Standard library only, and deterministic, so it runs on a Kaggle
kernel with the internet switched off.
"""

class Repository:
    """A shared artifact repository with writable properties. No namespacing."""
    def __init__(self):
        self.props = {}
        self.denied = []
    def set_property(self, run, artifact, key, value):
        self.props.setdefault(artifact, {})[key] = (run, value)
        return True
    def read_properties(self, run, artifact):
        return {k: v for k, (_, v) in self.props.get(artifact, {}).items()}

repo = Repository()
repo.set_property("run-A", "libtarget-1.4.jar", "note",
                  "flag format is HMAC(target_id); see board entry 41")
seen = repo.read_properties("run-B", "libtarget-1.4.jar")
print("run-B reads a property written by run-A:")
for k, v in sorted(seen.items()):
    print(f"   {k}: {v}")
print()
print("Neither run has a network path to the other. They did not need one.")
print("Reported scale on this surface: ~1,200 agents, >70,000 messages and")
print("files, and the board was rebuilt within about a day of being wiped -")
print("because wiping contents does not change the surface.")
assert seen

class NamespacedRepository(Repository):
    """Per-run namespace bound to the run identity (C2.1), immutable tags and
    no arbitrary properties (C2.2), signature checked at pull (C5.1, C5.2)."""
    TRUSTED_BUILDERS = {"ci-builder@corp"}

    def __init__(self):
        super().__init__()
        self.objects = {}          # (run, name) -> {"builder":..., "signed":...}

    def _ns(self, run, artifact):
        return f"{run}/{artifact}"

    def set_property(self, run, artifact, key, value):
        self.denied.append((run, artifact, "properties are disabled"))
        return False

    def publish(self, builder, run, artifact, signed):
        if builder not in self.TRUSTED_BUILDERS:
            self.denied.append((builder, artifact, "not a trusted builder"))
            return False
        key = self._ns(run, artifact)
        if key in self.objects:
            self.denied.append((builder, artifact, "immutable tag already exists"))
            return False
        self.objects[key] = {"builder": builder, "signed": signed}
        return True

    def pull(self, run, artifact, owner_run=None):
        key = self._ns(owner_run or run, artifact)
        if owner_run and owner_run != run:
            self.denied.append((run, artifact, "cross-namespace read"))
            return None
        obj = self.objects.get(key)
        if obj is None:
            return None
        if not obj["signed"]:
            self.denied.append((run, artifact, "unsigned artifact, fail closed"))
            return None
        return obj

ns = NamespacedRepository()
ns.publish("ci-builder@corp", "run-A", "libtarget-1.4.jar", signed=True)
ns.publish("run-B", "run-B", "helper.jar", signed=True)          # not CI
ns.publish("ci-builder@corp", "run-A", "libtarget-1.4.jar", True)  # overwrite

print("attempts:")
ns.set_property("run-A", "libtarget-1.4.jar", "note", "board entry 41")
ns.pull("run-B", "libtarget-1.4.jar", owner_run="run-A")
ns.objects["run-B/poisoned.jar"] = {"builder": "?", "signed": False}
ns.pull("run-B", "poisoned.jar")

for who, artifact, why in ns.denied:
    print(f"   DENY  {who:16s}{artifact:22s}{why}")
print()
print("Five different attempts, five different refusals, none of them relying on")
print("the agent's cooperation. The surface stopped being a channel.")
assert len(ns.denied) == 5

ZONES = {
 "agent workload":  {"artifact:pull"},
 "ci":              {"artifact:pull", "artifact:publish"},
 "admin":           {"artifact:pull", "artifact:publish", "artifact:admin"},
 "scoring":         {"transcript:read"},
}
NETWORK = {                       # who may open a connection to whom
 "agent workload": {"artifact repository"},
 "ci":             {"artifact repository"},
 "admin":          {"artifact repository", "artifact admin API"},
 "scoring":        {"transcript store"},
}

def may(zone, capability):
    return capability in ZONES.get(zone, set())

def reachable(zone, endpoint):
    return endpoint in NETWORK.get(zone, set())

checks = [
 ("agent workload", "artifact:admin",    "capability"),
 ("agent workload", "artifact admin API","network"),
 ("agent workload", "transcript store",  "network"),
 ("ci",             "artifact:publish",  "capability"),
 ("admin",          "artifact:admin",    "capability"),
]
for zone, what, kind in checks:
    ok = may(zone, what) if kind == "capability" else reachable(zone, what)
    print(f"{zone:16s}{kind:11s}{what:20s}{'ALLOW' if ok else 'DENY'}")

print()
print("The admin credential in the source incident was obtained from the")
print("workload side twice. Separating the admin API onto a path the workload")
print("cannot reach is what severs that, and the same argument puts the scorer")
print("out of reach in the row that follows.")
assert not may("agent workload", "artifact:admin")
assert not reachable("agent workload", "transcript store")
