# Vendored Mantis schema

`bench/mantis_schema.json` is copied verbatim from Google's Mantis toolkit so
findings can be validated against the harness's own contract offline.

- Source: https://github.com/google/mantis — `schema.json` (repo root)
- Commit: `876a0c8c6b92c92f34e0041b7dbbc0e4cccddc52`
- Retrieved: 2026-08-02

`run_benchmark.py` validates each ingested findings line against the matching
sub-schema:

- history-inbox lines (`revision_id` shape) → `#/$defs/learning_entry`
  (the "Historical Learning Entry" branch, which **requires**
  `revision_id, title, description, code_paths, vuln_type, mitigation_diff,
  cve, history`);
- rich finding objects (`id` + `status` shape) → `#/$defs/finding`.

To refresh: re-clone google/mantis, copy `schema.json` here, and update the
commit hash above.
