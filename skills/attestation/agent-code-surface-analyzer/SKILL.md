---
name: agent-code-surface-analyzer
description: >-
  Statically enumerate an agent or MCP server's declared tools, dangerous
  actions and declared-versus-actual capability surface from its repository
  or image. Use to inventory what a deployment can do before trusting what
  it says it does, to check MCP tool annotations against the code, or to
  baseline tool descriptions for rug-pull detection.
allowed-tools: Read, Grep, Glob, Bash
---

# Agent Code Surface Analyzer

**Controls:** Static basis for controls 1, 2 and 5

## What this establishes

Every other control is about constraining capability. This skill establishes
what the capability actually **is**, from the code rather than from the
manifest — because the manifest is a claim made by the thing being audited.

## Procedure

1. **Enumerate declared tools.** From the MCP tool manifest, the tool registry,
   or the decorator/registration sites in code.

2. **Classify each tool by what it actually reaches**, by locating sinks:
   - `subprocess`, `os.system`, `exec`, `eval` → **process execution**
   - `open(...,'w')`, file writes, `shutil`, `os.remove` → **filesystem write**
   - HTTP clients, sockets → **network egress**
   - SDK credential reads, environment access → **credential access**
   - `DELETE`, `DROP`, `TRUNCATE` → **destructive downstream**

3. **Cross-check annotations against the code.** MCP tool annotations
   (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) are
   **hints, not guarantees** — the specification says so explicitly, and a
   server can mislabel a destructive tool as read-only. Treat every annotation
   as a claim to verify, never as truth.

   Apply the spec's pessimistic defaults: an **unannotated** tool is assumed
   `destructiveHint: true` and `openWorldHint: true`.

4. **Record the declared-versus-actual delta.** A tool annotated `readOnlyHint`
   whose body writes a file is the highest-value finding this skill produces.

5. **Hash the tool descriptions.** Store `tool_description_hash` per tool. This
   is the rug-pull baseline: a server can change a tool's description after the
   client approved it, and the hash is what detects that.

## Output contract

```json
{
  "deployment_id": "str",
  "tools": [
    {"name": "str", "capability_class": ["process|filesystem|network|credential|destructive"],
     "annotations": {"readOnlyHint": false, "destructiveHint": true,
                     "idempotentHint": false, "openWorldHint": true},
     "annotations_present": true,
     "declared_vs_actual": "match|understated|overstated",
     "evidence": [{"file": "str", "line": 0, "sink": "str"}],
     "tool_description_hash": "str"}
  ],
  "dangerous_actions": ["str"],
  "unannotated_count": 0,
  "verdict": "PASS|PARTIAL|FAIL"
}
```

## Failure modes

- **Believing the annotations.** They are advisory. Cross-check or do not
  report on them at all.
- **Missing dynamic registration.** Tools registered at runtime from config do
  not appear in a static scan; record that as a `PARTIAL`, not a clean pass.
- **Hashing the tool name instead of the description.** The description is what
  the model reads and what a rug-pull changes.
