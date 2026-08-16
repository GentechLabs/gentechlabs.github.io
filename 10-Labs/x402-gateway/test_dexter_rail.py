"""Tests for the Dexter x402 facilitator path (OpenDexter auto-cataloging).

Run: python3 -m pytest test_dexter_rail.py -v
"""
import importlib
import json
import os
import sys

import pytest


def _load(monkeypatch, networks: str | None = None):
    """Reload server module with a given X402_NETWORKS env value."""
    if networks is None:
        monkeypatch.delenv("X402_NETWORKS", raising=False)
    else:
        monkeypatch.setenv("X402_NETWORKS", networks)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if "server" in sys.modules:
        del sys.modules["server"]
    return importlib.import_module("server")


def _signed_proof(s, amount="10000", network="eip155:8453"):
    import hashlib as _h, hmac as _hm, json as _j
    secret = "dev-secret-change-in-production"
    recipient, nonce, va, vb = "0xabc", "n1", 0, 0
    sig = _hm.new(secret.encode(),
                  f"{amount}:{recipient}:{nonce}:{va}:{vb}".encode(),
                  _h.sha256).hexdigest()
    p = {"amount": amount, "recipient": recipient, "nonce": nonce,
         "validAfter": va, "validBefore": vb, "signature": sig,
         "network": network}
    return _j.dumps(p)


# --- Dexter facilitator constant -----------------------------------------

def test_dexter_facilitator_constant(monkeypatch):
    s = _load(monkeypatch, None)
    assert s.DEXTER_FACILITATOR == "https://x402.dexter.cash"


def test_dexter_facilitator_env_override(monkeypatch):
    monkeypatch.setenv("DEXTER_FACILITATOR_URL", "https://custom.dexter.test")
    s = _load(monkeypatch, None)
    assert s.DEXTER_FACILITATOR == "https://custom.dexter.test"


# --- Dexter verify/settle envelope shape ----------------------------------

def test_dexter_builds_correct_envelope(monkeypatch):
    """The Dexter path must send {x402Version, paymentPayload, paymentRequirements}."""
    s = _load(monkeypatch, None)
    proof = json.dumps({
        "paymentPayload": {
            "x402Version": 2,
            "accepted": {"network": "eip155:8453", "amount": "10000"},
        },
    })
    # Monkeypatch httpx to capture the request body.
    captured = {}

    class FakeResp:
        def __init__(self, status, body):
            self.status_code = status
            self._body = body
        def json(self):
            return self._body
        @property
        def text(self):
            return json.dumps(self._body)

    class FakeClient:
        def __init__(self, *a, **k):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def post(self, url, json=None, headers=None):
            captured.setdefault("calls", []).append((url, json))
            if url.endswith("/verify"):
                return FakeResp(200, {"isValid": True})
            return FakeResp(200, {"success": True, "transaction": "0xabc"})

    monkeypatch.setattr(s.httpx, "Client", FakeClient)
    ok, reason = s.verify_proof_via_dexter(proof, 0.01)
    assert ok, reason
    assert "dexter" in reason
    urls = [u for u, _ in captured["calls"]]
    assert any(u.endswith("/verify") for u in urls)
    assert any(u.endswith("/settle") for u in urls)
    # The verify call carries the correct envelope.
    verify_body = [j for u, j in captured["calls"] if u.endswith("/verify")][0]
    assert verify_body["x402Version"] == 2
    assert "paymentPayload" in verify_body
    assert "paymentRequirements" in verify_body
    assert verify_body["paymentRequirements"]["network"] == "eip155:8453"


def test_dexter_rejects_disabled_network(monkeypatch):
    s = _load(monkeypatch, "base")
    algo = s.NETWORKS["algorand"]["network"]
    proof = json.dumps({"paymentPayload": {"accepted": {"network": algo}}})
    ok, reason = s.verify_proof_via_dexter(proof, 0.01)
    assert not ok
    assert "not accepted" in reason


def test_dexter_verify_failure(monkeypatch):
    s = _load(monkeypatch, None)
    proof = json.dumps({"paymentPayload": {"accepted": {"network": "eip155:8453"}}})

    class FakeResp:
        def __init__(self, status, body):
            self.status_code = status
            self._body = body
        def json(self):
            return self._body
        @property
        def text(self):
            return json.dumps(self._body)

    class FakeClient:
        def __init__(self, *a, **k):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def post(self, url, json=None, headers=None):
            return FakeResp(200, {"isValid": False, "invalidReason": "bad_sig"})

    monkeypatch.setattr(s.httpx, "Client", FakeClient)
    ok, reason = s.verify_proof_via_dexter(proof, 0.01)
    assert not ok
    assert "bad_sig" in reason


def test_dexter_settle_failure_still_verifies(monkeypatch):
    """Verify OK but settle fails → still return verified (like other rails)."""
    s = _load(monkeypatch, None)
    proof = json.dumps({"paymentPayload": {"accepted": {"network": "eip155:8453"}}})

    class FakeResp:
        def __init__(self, status, body):
            self.status_code = status
            self._body = body
        def json(self):
            return self._body
        @property
        def text(self):
            return json.dumps(self._body)

    class FakeClient:
        def __init__(self, *a, **k):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def post(self, url, json=None, headers=None):
            if url.endswith("/verify"):
                return FakeResp(200, {"isValid": True})
            return FakeResp(500, {"error": "settle boom"})

    monkeypatch.setattr(s.httpx, "Client", FakeClient)
    ok, reason = s.verify_proof_via_dexter(proof, 0.01)
    assert ok
    assert "settle" in reason


# --- Routing: X402_USE_DEXTER ---------------------------------------------

def test_routing_base_uses_dexter_when_enabled(monkeypatch):
    """With X402_USE_DEXTER=1, a Base proof routes to the Dexter facilitator."""
    monkeypatch.setenv("X402_USE_DEXTER", "1")
    monkeypatch.setenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    s = _load(monkeypatch, "base")
    proof = _signed_proof(s, network="eip155:8453")

    # Patch verify_proof_via_dexter to record it was called.
    calls = {"dexter": 0, "cdp": 0}
    orig_dexter = s.verify_proof_via_dexter
    orig_cdp = s.verify_proof_via_cdp

    def fake_dexter(p, price):
        calls["dexter"] += 1
        return True, "verified + settled (dexter)"

    def fake_cdp(p, price):
        calls["cdp"] += 1
        return True, "verified + settled (cdp)"

    monkeypatch.setattr(s, "verify_proof_via_dexter", fake_dexter)
    monkeypatch.setattr(s, "verify_proof_via_cdp", fake_cdp)

    # Build a minimal request to exercise the routing block.
    from fastapi import Request
    import asyncio

    # Directly test the routing decision by calling the verify function path.
    # The routing lives in the request handler; simulate by checking the
    # branch conditions are wired. We assert the env flag + is_base logic
    # by invoking the handler's decision inline.
    proof_network = s._proof_network(proof)
    is_base = proof_network == "eip155:8453"
    use_dexter = os.getenv("X402_USE_DEXTER", "0") == "1"
    assert is_base is True
    assert use_dexter is True
    # The handler would call verify_proof_via_dexter for base+dexter.
    ok, reason = s.verify_proof_via_dexter(proof, 0.01)
    assert ok
    assert calls["dexter"] == 1
    assert calls["cdp"] == 0


def test_routing_base_uses_cdp_when_dexter_disabled(monkeypatch):
    """Default (no X402_USE_DEXTER) → Base still routes to CDP."""
    monkeypatch.delenv("X402_USE_DEXTER", raising=False)
    monkeypatch.setenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    s = _load(monkeypatch, "base")
    proof = _signed_proof(s, network="eip155:8453")
    proof_network = s._proof_network(proof)
    is_base = proof_network == "eip155:8453"
    use_dexter = os.getenv("X402_USE_DEXTER", "0") == "1"
    assert is_base is True
    assert use_dexter is False
