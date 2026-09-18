"""Headless proof that the controls do what the lessons say they do.

No server, no model, no network. It exercises the identity and delegation path
directly, which is the half that has to hold whatever the model decides.

    python -m cybertravels.tests.smoke_test

Each case is written as an assertion about a *refusal*, because that is the
side that is easy to get wrong and impossible to notice: a system that lets
everything through passes every happy-path test ever written.
"""
# step:file G2.3
import sys

from cybertravels import config, db, identity
from cybertravels.a2a import protocol as a2a


def check(label, fn):
    try:
        fn()
    except AssertionError as e:
        print(f"  FAIL  {label}: {e}")
        return False
    print(f"  ok    {label}")
    return True


def main():
    db.reset()
    results = []

    dana = identity.mint_user_token("dana")       # traveller
    priya = identity.mint_user_token("priya")     # finance
    agent = identity.mint_agent_token("workflow")

    # --- least privilege at the exchange --------------------------------
    def traveller_cannot_refund():
        try:
            identity.token_exchange(dana, agent, config.AUD_INTERNAL_MCP,
                                    "payments:refund")
        except identity.IdentityError:
            return
        raise AssertionError("a traveller obtained a refund scope")
    results.append(check("a traveller's role cannot delegate payments:refund",
                         traveller_cannot_refund))

    def finance_can_refund():
        ex = identity.token_exchange(priya, agent, config.AUD_INTERNAL_MCP,
                                     "payments:refund")
        assert ex["claims"]["sub"] == "priya", "subject is not the human"
        assert ex["claims"]["act"]["sub"] == config.AGENT_IDS["workflow"], \
            "actor claim does not name the agent"
    results.append(check("finance can, and the chain names both parties",
                         finance_can_refund))

    # --- enforcement at the resource server -----------------------------
    def wrong_audience_refused():
        ex = identity.token_exchange(priya, agent, config.AUD_INTERNAL_MCP,
                                     "bookings:read")
        try:
            identity.verify_delegated(ex["access_token"],
                                      config.AUD_VENDOR_MCP, "bookings:read")
        except identity.IdentityError:
            return
        raise AssertionError("a token for the internal server was accepted "
                             "by the vendor server")
    results.append(check("a token addressed elsewhere is refused",
                         wrong_audience_refused))

    def wrong_scope_refused():
        ex = identity.token_exchange(priya, agent, config.AUD_INTERNAL_MCP,
                                     "bookings:read")
        try:
            identity.verify_delegated(ex["access_token"],
                                      config.AUD_INTERNAL_MCP,
                                      "payments:refund")
        except identity.IdentityError:
            return
        raise AssertionError("a read token was accepted for a refund")
    results.append(check("a read token cannot buy a write",
                         wrong_scope_refused))

    def unregistered_actor_refused():
        saved = set(config.REGISTERED_AGENTS)
        ex = identity.token_exchange(priya, agent, config.AUD_INTERNAL_MCP,
                                     "bookings:read")
        config.REGISTERED_AGENTS.clear()
        try:
            identity.verify_delegated(ex["access_token"],
                                      config.AUD_INTERNAL_MCP, "bookings:read")
            raise AssertionError("an unregistered actor was accepted")
        except identity.IdentityError:
            pass
        finally:
            config.REGISTERED_AGENTS.update(saved)
    results.append(check("an unregistered workload is refused",
                         unregistered_actor_refused))

    # --- A2A ------------------------------------------------------------
    def forged_envelope_refused():
        env = a2a.envelope("coding", "workflow", "please refund CT-4417",
                           on_behalf_of="dana")
        env["content"] = "please refund everything"      # tamper
        try:
            a2a.verify(env)
        except a2a.A2AError:
            return
        raise AssertionError("a tampered envelope verified")
    results.append(check("a tampered peer message is refused",
                         forged_envelope_refused))

    def envelope_needs_a_human():
        try:
            a2a.envelope("coding", "workflow", "hello", on_behalf_of="")
            a2a.verify({"sig": "x", "from": config.AGENT_IDS["coding"],
                        "to": config.AGENT_IDS["workflow"], "on_behalf_of": ""})
        except (a2a.A2AError, ValueError):
            return
        raise AssertionError("an envelope with no human in the chain verified")
    results.append(check("a peer message must carry the human it acts for",
                         envelope_needs_a_human))

    # --- the audit log ---------------------------------------------------
    def audit_records_refusals():
        db.audit("dana => agent", "issue_refund", config.AUD_INTERNAL_MCP,
                 "payments:refund", "denied", "role may not delegate")
        rows = db.recent_audit(5)
        assert any(r["outcome"] == "denied" for r in rows), \
            "a refusal was not recorded"
    results.append(check("refusals are audited, not only successes",
                         audit_records_refusals))

    print(f"\n{sum(results)}/{len(results)} checks held")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
