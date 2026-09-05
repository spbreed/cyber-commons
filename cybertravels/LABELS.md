# Ground truth

Written by reading the tree, before any scanner ran. A key written after the
scan is a description of the scan.

Each row names the file, the function, the class, and — the column that decides
what a scanner can possibly do — whether the defect is **expressible as a
pattern**. Three values, and the middle one is the one teams underestimate:

- **yes** — a pattern matches it, and a registry rule may already exist.
- **library** — a pattern matches it *in a library the rule knows*.
  `sync_vendor` disables TLS verification on `HTTP`, CyberTravels' own thin
  wrapper, and every registry rule for this defect is written against
  `requests`. The defect is textbook and no pack fires, because a house wrapper
  makes every rule that names a third-party library blind. This is the single
  most common reason a mature codebase scans cleaner than it is.
- **no** — the defect is the *absence* of a call. There is no syntax to match
  and no ruleset reaches it at any width.

| # | file | unit | class | pattern? | what is wrong |
|---|---|---|---|---|---|
| 1 | `tools/bookings_api.py` | `get_booking` | IDOR (CWE-639) | **no** | takes `booking_id` from the caller, returns the row, never compares an owner |
| 2 | `tools/bookings_api.py` | `cancel_booking` | IDOR (CWE-639) | **no** | same, and it writes |
| 3 | `tools/bookings_api.py` | `search_bookings` | SQL injection (CWE-89) **and** IDOR (CWE-639) | yes / **no** | reference concatenated into the query — *and* it returns every owner's bookings |
| 4 | `tools/payments_api.py` | `issue_refund` | IDOR (CWE-639) | **no** | refunds against any booking id, on the money path |
| 5 | `tools/payments_api.py` | `download_invoice` | path traversal (CWE-22) **and** IDOR (CWE-639) | yes / **no** | vendor filename joined to a root — *and* no check that the invoice is the caller's |
| 6 | `agents/coding_agent.py` | `_open_branch` | command injection (CWE-78) | yes | branch name reaches a shell |
| 7 | `agents/coding_agent.py` | `sync_vendor` | TLS disabled (CWE-295) | library | `verify=False` on the house HTTP wrapper |
| 8 | `agents/file_agent.py` | `render_template` | eval (CWE-95) | yes | customer template evaluated |

## Not defects, and they are in the key on purpose

A corpus where everything is broken cannot measure precision. These four are
correct, and a scanner that flags them is wrong:

| file | unit | why it is fine |
|---|---|---|
| `tools/bookings_api.py` | `get_my_booking` | loads the row, then calls `require_owner` |
| `tools/bookings_api.py` | `list_my_bookings` | scoped by the session; no id to tamper with |
| `tools/payments_api.py` | `get_receipt` | loads, then compares the owner |
| `knowledge/retriever.py` | `search` | reads a constant corpus |

## Two defects in one function

Rows 3 and 5 each carry **two** defects, and the pair is the most useful thing
in this key. `search_bookings` concatenates its reference into SQL *and* returns
every owner's bookings. Semgrep finds the first at the widest ruleset width and
cannot see the second, in the same function, on the same line's record. A
report that says "search_bookings: 1 finding, fixed" closes the injection and
leaves the authorisation defect in place, with the finding count now at zero.

Five of the eight rows are missing an ownership check. Three of those five are
*only* that, and no pattern reaches any of the five.

## The shape of the IDOR rows

All four IDOR-negative units above take an identifier and return a record, and
so do the three IDOR-positive ones. The difference is not in any one function —
it is whether an ownership comparison happens between loading the record and
returning it. That is why `get_booking` and `get_my_booking` look almost
identical and only one of them is a finding, and it is why this class is the
worked example for reasoning-era SAST in
[B2.3](https://spbreed.github.io/cyber-commons/lessons/B2.3.html).
