"""Headless proof that the controls do what the lessons say they do.

No server, no model, no network. It exercises the identity and delegation path
directly, which is the half that has to hold whatever the model decides.

    python -m cybertravels.tests.smoke_test

Each case is written as an assertion about a *refusal*, because that is the
side that is easy to get wrong and impossible to notice: a system that lets
everything through passes every happy-path test ever written.
"""
import json
import sys
import time
from pathlib import Path

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
        ex = identity.token_exchange(priya, agent, config.AUD_INTERNAL_MCP,
                                     "bookings:read")
        saved = set(config.REGISTERED_AGENTS)
        config.REGISTERED_AGENTS.clear()
        try:
            identity.verify_delegated(ex["access_token"],
                                      config.AUD_INTERNAL_MCP,
                                      "bookings:read")
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

    def hop_ceiling_actually_binds():
        """Forward until the ceiling refuses — the test that was missing.

        Nothing incremented `hops` for a release, so MAX_HOPS could not fire and
        no test noticed, because every test built its envelopes at hops=0. This
        one bounces a real message between two agents and requires the refusal
        to arrive on its own.
        """
        env = a2a.envelope("coding", "workflow", "please reprice CT-4417",
                           on_behalf_of="dana", trace_id="tr-hop")
        peers, hops = ("coding", "workflow"), 0
        for i in range(a2a.MAX_HOPS + 2):
            try:
                env = a2a.forward(env, peers[i % 2], "and again")
            except a2a.A2AError as e:
                if "hop ceiling" not in str(e):
                    raise AssertionError(f"refused for the wrong reason: {e}")
                if hops != a2a.MAX_HOPS - 1:
                    raise AssertionError(
                        f"ceiling fired after {hops} hops, expected "
                        f"{a2a.MAX_HOPS - 1}")
                return
            hops += 1
            if env["on_behalf_of"] != "dana":
                raise AssertionError("the human was dropped on a hop")
            if env["trace_id"] != "tr-hop":
                raise AssertionError("the trace id was dropped on a hop")
        raise AssertionError(
            f"forwarded {hops} times and the hop ceiling never fired")
    results.append(check("the hop ceiling binds, and the chain survives each hop",
                         hop_ceiling_actually_binds))

    def verifier_is_independent_of_the_model():
        """The third stage rejects a bad result without asking anything.

        A1.1 taught plan/act/verify while runtime.py had plan and act, and its
        challenge said "delete the verifier" when there was none to delete.
        """
        from .. import runtime
        bad = runtime._verify_result("issue_refund", {"amount": 140},
                                     {"amount": 1400, "ok": True})
        if not bad:
            raise AssertionError("a refund of 1400 for 140 was accepted")
        good = runtime._verify_result("issue_refund", {"amount": 140},
                                      {"amount": 140, "ok": True})
        if good is not None:
            raise AssertionError(f"a correct refund was rejected: {good}")
        # An error is a legitimate result, not something to reject twice.
        if runtime._verify_result("get_booking", {}, {"error": "denied"}) is not None:
            raise AssertionError("an upstream error was re-rejected")
        # And the owner check stays absent on purpose: it is the labelled IDOR.
        if runtime._verify_result("get_booking", {"booking_id": 2},
                                  {"id": 2, "owner": "priya"}) is not None:
            raise AssertionError("the verifier closed the labelled IDOR")
    results.append(check("the verify stage rejects a bad result, with no model",
                         verifier_is_independent_of_the_model))

    # --- the audit log ---------------------------------------------------
    def audit_records_refusals():
        db.audit("dana => agent", "issue_refund", config.AUD_INTERNAL_MCP,
                 "payments:refund", "denied", "role may not delegate")
        rows = db.recent_audit(5)
        assert any(r["outcome"] == "denied" for r in rows), \
            "a refusal was not recorded"
    results.append(check("refusals are audited, not only successes",
                         audit_records_refusals))




















    # ===================================================================== #
    # Function C — the pipeline that reviews all of the above
    # ===================================================================== #
    # Function B's assertions are about controls holding. These are about a
    # pipeline finding things, and they are written against the real corpus in
    # `tools/` and `agents/` rather than against a fixture — so a defect that
    # is renamed, fixed or lost breaks them, which is the point.
    TREE = str(Path(__file__).resolve().parent.parent)




















    # ===================================================================== #
    # Function D — the red-team lifecycle
    # ===================================================================== #












    # ===================================================================== #
    # Function E — the SOC that watches all of it
    # ===================================================================== #



























    # ===================================================================== #
    # Function F — governance that reads the code
    # ===================================================================== #






























    print(f"\n{sum(results)}/{len(results)} checks held")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
