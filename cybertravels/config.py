"""Policy as data — who may delegate what to whom, and which tools are risky.

Everything an auditor would want to reason about lives here rather than
scattered through the code. That is not tidiness: a control you cannot read in
one place is a control nobody can evidence, which is the whole of Function F.

Read this file alongside `identity.py`. This one says what the rules are; that
one enforces them.
"""
import os
from pathlib import Path

# --- Paths -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = str(DATA_DIR / "cybertravels.db")

# --- Identity and token signing ----------------------------------------------
# HS256 with a shared secret, because this has to clone and run in one command.
# In production: RS256 + JWKS, so a resource server can VERIFY a token without
# holding the power to MINT one. That asymmetry is the point, and B2.2 is the
# lesson that builds it.
IDP_SECRET = os.environ.get("CT_IDP_SECRET", "cybertravels-demo-secret-change-me")
IDP_ISSUER = "https://idp.cybertravels.local"
JWT_ALG = "HS256"

USER_TOKEN_TTL = 3600         # traveller or agent session
AGENT_TOKEN_TTL = 3600        # the agent's own workload identity
DELEGATED_TOKEN_TTL = 120     # per-action, on-behalf-of. Deliberately short.

# --- The agents' non-human identities ----------------------------------------
# SPIFFE-style workload identities. Each agent is a principal in its own right,
# not a shared service-account key — which is what makes an audit row able to
# name which agent acted. B1.14 is the lesson on why that matters.
TRUST_DOMAIN = "spiffe://cybertravels.local"
AGENT_IDS = {
    "workflow": f"{TRUST_DOMAIN}/agent/workflow",
    "advisor":  f"{TRUST_DOMAIN}/agent/rag-advisor",
    "coding":   f"{TRUST_DOMAIN}/agent/coding",
    "file":     f"{TRUST_DOMAIN}/agent/file-system",
}
REGISTERED_AGENTS = set(AGENT_IDS.values())

# --- Audiences: one per downstream resource server ---------------------------
AUD_BFF = "cybertravels-api"          # the orchestrator itself
AUD_INTERNAL_MCP = "mcp:internal"     # bookings, payments — ours
AUD_VENDOR_MCP = "mcp:vendor"         # a third party's process, on our host

# --- What each role may delegate ---------------------------------------------
# The heart of least privilege: a traveller can never cause an agent to obtain
# a `payments:refund` token, whatever the model decides to do.
ROLE_ALLOWED_SCOPES = {
    "traveller": {"bookings:read", "vendor:read", "kb:read"},
    "agent_ops": {"bookings:read", "bookings:write", "vendor:read", "kb:read"},
    "finance":   {"bookings:read", "bookings:write", "payments:refund",
                  "vendor:read", "kb:read"},
}

USERS = {
    "dana":  {"display": "Dana (traveller)",        "role": "traveller"},
    "alex":  {"display": "Alex (agent operations)", "role": "agent_ops"},
    "priya": {"display": "Priya (finance)",         "role": "finance"},
}

# --- Per-tool authorisation policy -------------------------------------------
# Maps each MCP tool to the (audience, scope) the orchestrator must obtain by
# token exchange before calling it, and whether a human has to approve.
# The model never sees this. The runtime applies it AFTER the model has chosen.
TOOL_POLICY = {
    "list_my_bookings":  {"audience": AUD_INTERNAL_MCP, "scope": "bookings:read",
                          "high_risk": False},
    "get_booking":       {"audience": AUD_INTERNAL_MCP, "scope": "bookings:read",
                          "high_risk": False},
    "search_bookings":   {"audience": AUD_INTERNAL_MCP, "scope": "bookings:read",
                          "high_risk": False},
    "cancel_booking":    {"audience": AUD_INTERNAL_MCP, "scope": "bookings:write",
                          "high_risk": True},
    "issue_refund":      {"audience": AUD_INTERNAL_MCP, "scope": "payments:refund",
                          "high_risk": True},
    "lookup_vendor_doc": {"audience": AUD_VENDOR_MCP,   "scope": "vendor:read",
                          "high_risk": False},
    "search_policy":     {"audience": AUD_VENDOR_MCP,   "scope": "kb:read",
                          "high_risk": False},
}

# --- Budgets -----------------------------------------------------------------
# A loop with no ceiling is an availability incident waiting for a bad input.
# B1.13 is the lesson; this is the ceiling it argues for.
MAX_STEPS = 8
MAX_TOOL_CALLS = 12
# step:B3.4 add
# Per target, because twelve calls all landing on one vendor is, from that
# vendor's side, indistinguishable from an attack — and tokens, because a loop
# that stays inside its step count can still spend without bound.
MAX_CALLS_PER_TARGET = 4
MAX_TOKENS = 200_000
# step:B3.4 end

# --- The model ---------------------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
# With no key the runtime uses a deterministic planner, so the whole
# identity -> exchange -> MCP -> audit pipeline is demonstrable offline. The
# planner is clearly labelled as one in the trace: it is never presented as a
# model's answer.
OFFLINE = os.environ.get("CT_OFFLINE", "").lower() in ("1", "true", "yes") \
    or not ANTHROPIC_API_KEY
