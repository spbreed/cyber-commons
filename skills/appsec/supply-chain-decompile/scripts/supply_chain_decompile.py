#!/usr/bin/env python3
"""Scan an SBOM, reconcile it against the filesystem, and decompile the library no manifest declares.

This is the executable half of the `supply-chain-decompile` skill. Three of the
four inputs are ordinary fixtures — a CycloneDX SBOM, an OSV-shaped advisory
extract, and an image inventory. The fourth is a **real compiled Java class**,
built with javac and committed next to this script; the parser below reads its
constant pool the way `jadx` or `procyon` read one, and never sees the source.

The source is in `evidence/provenance/` so a reader can check the recovered
strings against it. A vendor does not give you that, which is the point.

Standard library only, and deterministic.
"""

import json
import struct
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / "evidence"


# --------------------------------------------------------------- version order
def parts(v):
    """Compare versions numerically. '1.9' < '1.10' lexically is false, and
    that single mistake silently drops the most common kind of finding."""
    return tuple(int(x) if x.isdigit() else 0 for x in v.split("."))


def affected(version, introduced, fixed):
    return parts(introduced) <= parts(version) < parts(fixed)


# ------------------------------------------------------ 1 · scan what was declared
sbom = json.loads((EV / "sbom.cdx.json").read_text())
advisories = json.loads((EV / "osv_extract.json").read_text())
inventory = json.loads((EV / "disk_inventory.json").read_text())

report = {"sbom": {"components": len(sbom["components"])}, "advisories": []}
print(f"SBOM: {sbom['metadata']['component']['name']} "
      f"{sbom['metadata']['component']['version']} · "
      f"{len(sbom['components'])} declared components")
print()

for c in sorted(sbom["components"], key=lambda c: c["purl"]):
    base, version = c["purl"].rsplit("@", 1)
    for a in advisories:
        if a["package"] == base and affected(version, a["introduced"], a["fixed"]):
            print(f"   {a['severity']:<9}{c['name']} {version:<8}{a['id']}")
            print(f"             {a['summary']}  -> fixed in {a['fixed']}")
            report["advisories"].append({"package": c["name"], "version": version,
                                         "id": a["id"], "severity": a["severity"],
                                         "fixed": a["fixed"]})
report["sbom"]["vulnerable"] = len({a["package"] for a in report["advisories"]})
print()
print(f"{report['sbom']['vulnerable']} of {len(sbom['components'])} declared "
      f"components carry a published advisory. This is the whole of what a")
print("dependency scanner reports, and every word of it is true.")
print()

# ------------------------------------------------- 2 · reconcile against the disk
declared = {c["purl"] for c in sbom["components"]}
on_disk = {i["purl"] for i in inventory if i["purl"]}
undeclared = [i for i in inventory if not i["purl"]]

report["reconciliation"] = {
    "undeclared_on_disk": [i["path"] for i in undeclared],
    "declared_not_present": sorted(declared - on_disk),
}
print("reconciliation — the SBOM against what is in the image")
print(f"   declared and present   : {len(declared & on_disk)}")
print(f"   in the SBOM, not on disk: {len(declared - on_disk)}")
print(f"   on disk, in no SBOM     : {len(undeclared)}")
for i in undeclared:
    print(f"      {i['path']}  <- {i['note']}")
print()
print("No scanner reported that file. It has no purl, so there is nothing to")
print("look up, so there is no advisory, so the report was clean about it.")
print()

# --------------------------------------- 3 · read the artefact nobody declared
# The JVM constant pool: tag byte, then a fixed or length-prefixed payload.
# Longs and doubles take two slots, which is the one rule that breaks a naive
# parser halfway through the table.
WIDTH = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4,
         15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}


def constant_pool(blob):
    magic, _minor, major, count = struct.unpack_from(">IHHH", blob, 0)
    if magic != 0xCAFEBABE:
        raise ValueError("not a class file")
    pool, i, off = {}, 1, 10
    while i < count:
        tag = blob[off]; off += 1
        if tag == 1:                                     # CONSTANT_Utf8
            (n,) = struct.unpack_from(">H", blob, off); off += 2
            pool[i] = ("utf8", blob[off:off + n].decode("utf-8", "replace")); off += n
        else:
            w = WIDTH[tag]
            pool[i] = (tag, struct.unpack_from(">H", blob, off)[0] if w == 2
                       else struct.unpack_from(">HH", blob, off) if w == 4 else None)
            off += w
            if tag in (5, 6):                            # long/double eat two slots
                i += 1
        i += 1
    return pool, major


blob = (EV / "VendorTelemetry.class").read_bytes()
pool, major = constant_pool(blob)
utf8 = {i: v for i, (t, v) in pool.items() if t == "utf8"}

# CONSTANT_String (8) -> a literal the code actually uses.
literals = sorted({utf8[v] for t, v in pool.values() if t == 8 and v in utf8})
# CONSTANT_Class (7) -> everything it references, including the JDK.
classes = sorted({utf8[v].replace("/", ".") for t, v in pool.values()
                  if t == 7 and v in utf8})

print(f"decompiling {len(blob)} bytes of {undeclared[0]['artefact']} "
      f"(class file version {major}, no source, no manifest)")
print()
print("   string literals in the constant pool:")
for s in literals:
    print(f"      {s}")
print()
print("   classes it references:")
for c in classes:
    print(f"      {c}")
print()

# ------------------------------------- 4 · capabilities, which are provable
CAPS = [("network egress", ("java.net.URL", "java.net.HttpURLConnection")),
        ("cryptography", ("javax.crypto.Cipher",))]
caps = [name for name, needed in CAPS if all(c in classes for c in needed)]
print(f"   capabilities: {', '.join(caps)}")
print()
print("   A hardcoded endpoint, a credential-shaped literal, an HTTP client and")
print("   a cipher, in a library that appears in no manifest and that the")
print("   booking provider ships as part of an integration bundle.")
print()
print("   What is provable from the constant pool is that this artefact CAN")
print("   reach that endpoint. What is sent is not in the constant pool, so it")
print("   is not in this finding - write it as a capability and it survives")
print("   review; write it as exfiltration and it is dismissed along with")
print("   everything next to it.")
print()

report["decompiled"] = [{"artefact": undeclared[0]["artefact"],
                         "strings": literals, "classes": classes,
                         "capabilities": caps}]
report["unassessable_by_sbom"] = len(undeclared)

print(f"unassessable by SBOM: {report['unassessable_by_sbom']}")
print("That number is the finding. A dependency report that omits it has")
print("claimed the undeclared code is clean, on evidence it never had.")

assert report["advisories"], "the declared scan found nothing - check the ranges"
assert any(a["package"].endswith("commons-text") for a in report["advisories"]), \
    "1.9 < 1.10.0 must compare numerically or Text4Shell is silently dropped"
assert "network egress" in caps, "the decompiler recovered no capability"
assert report["unassessable_by_sbom"] > 0
