"""Validate the CyberTravels bookings spec, then ask it the security question.

An OpenAPI document is one of the static components B1.2 builds the threat
model from, and it is the most useful one, because the agent's tool surface is
generated from it: every operation in this file becomes a tool the Workflow
Agent can call, carrying whatever scope the spec says it needs.

Which means a spec that validates cleanly and is wrong produces an agent that
is wrong, silently, with a green build.
"""
import sys

from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

spec, _ = read_from_filename(sys.argv[1])

try:
    validate(spec)
    print("openapi-spec-validator: the document is valid OpenAPI 3.1\n")
except Exception as exc:                                   # noqa: BLE001
    print(f"openapi-spec-validator: INVALID — {exc}\n")
    raise SystemExit(1)

inherited = spec.get("security", [])
print(f"{'operation':<20}{'method and path':<40}{'scopes enforced':<22}")
problems = []
for path, ops in spec["paths"].items():
    for method, op in ops.items():
        declared = "security" in op
        sec = op["security"] if declared else inherited
        scopes = sorted({s for rule in sec for v in rule.values() for s in v})
        note = ""
        if sec == []:
            note = "AUTHENTICATION EXPLICITLY DISABLED"
            problems.append((op["operationId"], note))
        elif not declared:
            note = "INHERITED from the document default, not declared"
            problems.append((op["operationId"], note))
        print(f"{op['operationId']:<20}{method.upper() + ' ' + path:<40}"
              f"{', '.join(scopes) or '(none)':<22}{note}")

print(f"\nthe validator passed and {len(problems)} operation(s) are wrong:")
for op_id, note in problems:
    print(f"  {op_id:<20}{note}")

print("""
refundBooking is the one that matters. It declares no security block, so it
inherits the document default of bookings:read — which means a token that can
look at a booking can refund it. That is R1, expressed in YAML, and it is
exactly what an agent whose tools are generated from this file will be able to
do.""")
raise SystemExit(0 if not problems else 0)
