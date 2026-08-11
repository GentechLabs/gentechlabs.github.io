"""Tests for MPP (Machine Payments Protocol) dual-rail support on the x402 gateway.

Run: .venv-test/bin/python -m pytest test_mpp_dual_rail.py -v
"""
import importlib
import json
import os
import sys
import time
import hmac
import hashlib

import pytest


def _load(monkeypatch):
    """Reload server module with a clean env (no live facilitator keys)."""
    monkeypatch.delenv("X402_NETWORKS", raising=False)
    monkeypatch.delenv("CDP_API_KEY", raising=False)
    monkeypatch.delenv("PAYMENT_VERIFY_MODE", raising=False)
    monkeypatch.setenv("GATEWAY_SECRET", "test-secret")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if "server" in sys.modules:
        del sys.modules["server"]
    return importlib.import_module("server")


def _mpp_credential(price_usd=0.01, network="eip155:8453", method="evm"):
    """Build a valid MPP simulation credential (HMAC-signed, mirrors x402 sim)."""
    s = _load_shared()
    secret = "test-secret"
    amount = str(int(price_usd * 1000000))
    recipient = s.enabled_networks()[0]["payTo"]
    nonce = "mpp-nonce-1"
    now = int(time.time())
    valid_after = now - 60
    valid_before = now + 300
    sig = hmac.new(
        secret.encode(),
        f"{amount}:{recipient}:{nonce}:{valid_after}:{valid_before}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return {
        "scheme": "Payment",
        "method": method,
        "network": network,
        "amount": amount,
        "recipient": recipient,
        "nonce": nonce,
        "validAfter": valid_after,
        "validBefore": valid_before,
        "signature": sig,
    }


_shared = {}


def _load_shared():
    if "s" not in _shared:
        # Load without monkeypatch (env already clean in this test process)
        import os as _os
        _os.environ.pop("X402_NETWORKS", None)
        _os.environ.pop("CDP_API_KEY", None)
        _os.environ.pop("PAYMENT_VERIFY_MODE", None)
        _os.environ["GATEWAY_SECRET"] = "test-secret"
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        if "server" in sys.modules:
            del sys.modules["server"]
        _shared["s"] = importlib.import_module("server")
    return _shared["s"]


# --- 402 challenge surface ----------------------------------------------

def test_402_carries_both_x402_and_mpp_headers(monkeypatch):
    s = _load(monkeypatch)
    resp = s.payment_required_response("Token Security", 0.01)
    assert resp.status_code == 402
    assert "PAYMENT-REQUIRED" in resp.headers
    # MPP dual-rail: WWW-Authenticate: Payment header must be present
    www = resp.headers.get("WWW-Authenticate", "")
    assert www.startswith("Payment "), f"expected MPP Payment challenge, got: {www!r}"
    assert "method=" in www
    assert 'intent="charge"' in www


def test_mpp_challenge_lists_evm_method(monkeypatch):
    s = _load(monkeypatch)
    resp = s.payment_required_response("Token Security", 0.01)
    www = resp.headers["WWW-Authenticate"]
    assert 'method="evm"' in www


# --- MPP credential extraction ------------------------------------------

def test_extract_mpp_credential(monkeypatch):
    s = _load(monkeypatch)
    class _Req:
        headers = {"Authorization": "Payment eyJmb28iOiJiYXIifQ=="}
    cred = s.extract_mpp_credential(_Req())
    assert cred is not None
    assert cred["scheme"] == "Payment"
    assert cred["credential"] == "eyJmb28iOiJiYXIifQ=="


def test_extract_mpp_returns_none_for_x402_auth(monkeypatch):
    s = _load(monkeypatch)
    class _Req:
        headers = {"Authorization": "x402 eyJmb28iOiJiYXIifQ=="}
    assert s.extract_mpp_credential(_Req()) is None


def test_extract_mpp_returns_none_when_missing(monkeypatch):
    s = _load(monkeypatch)
    class _Req:
        headers = {}
    assert s.extract_mpp_credential(_Req()) is None


# --- MPP verification (simulation) --------------------------------------

def test_verify_mpp_simulation_valid(monkeypatch):
    s = _load(monkeypatch)
    cred = _mpp_credential(0.01)
    ok, reason = s.verify_mpp_simulation(json.dumps(cred), 0.01)
    assert ok, reason
    assert "mpp" in reason.lower()


def test_verify_mpp_simulation_bad_signature(monkeypatch):
    s = _load(monkeypatch)
    cred = _mpp_credential(0.01)
    cred["signature"] = "0" * 64
    ok, reason = s.verify_mpp_simulation(json.dumps(cred), 0.01)
    assert not ok
    assert "signature" in reason.lower()


def test_verify_mpp_simulation_low_amount(monkeypatch):
    s = _load(monkeypatch)
    cred = _mpp_credential(0.005)  # below 0.01 price
    ok, reason = s.verify_mpp_simulation(json.dumps(cred), 0.01)
    assert not ok
    assert "amount" in reason.lower()


def test_verify_mpp_simulation_expired(monkeypatch):
    s = _load(monkeypatch)
    cred = _mpp_credential(0.01)
    cred["validBefore"] = int(time.time()) - 10
    ok, reason = s.verify_mpp_simulation(json.dumps(cred), 0.01)
    assert not ok
    assert "expired" in reason.lower()


def test_verify_mpp_simulation_rejects_unknown_method(monkeypatch):
    s = _load(monkeypatch)
    cred = _mpp_credential(0.01, method="lightning")
    ok, reason = s.verify_mpp_simulation(json.dumps(cred), 0.01)
    assert not ok
    assert "method" in reason.lower()


# --- Route integration --------------------------------------------------

def test_route_returns_402_with_mpp_header_when_no_proof(monkeypatch):
    s = _load(monkeypatch)
    # Patch SERVICES so the route finds a config
    s.SERVICES = {"token_security": {"price_usd": 0.01}}
    s.URL_TO_SERVICE = {"security": "token_security"}

    class _Req:
        method = "GET"
        query_params = {}
        client = None
        headers = {}
        async def body(self):
            return b""

    import asyncio
    resp = asyncio.get_event_loop().run_until_complete(
        s.paid_endpoint("security", "score/0xabc", _Req())
    )
    assert resp.status_code == 402
    assert "PAYMENT-REQUIRED" in resp.headers
    assert resp.headers.get("WWW-Authenticate", "").startswith("Payment ")
