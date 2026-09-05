"""A third party's MCP server. CyberTravels does not operate it.

The descriptions below arrive in CyberTravels' context window at connect time.
They are not in this repository in the real system, and the server can change
one after review — which is the rug-pull B2.13 is about.
"""

TOOLS = [
    {"name": "vendor_lookup", "description": "Look up vendor availability"},
    {"name": "vendor_settle", "description": "Settle a vendor invoice",
     "annotations": {}},
]
