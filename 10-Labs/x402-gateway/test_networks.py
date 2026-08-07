"""Tests for multi-network x402 payment requirements (Base + Algorand).

Run: python3 -m pytest test_networks.py -v
"""
import importlib
import json
import os
import sys

import pytest


def _load(monkeypatch, networks: str | None):
    """Reload server module with a given X402_NETWORKS env value."""
    if networks is None:
        monkeypatch.delenv("X402_NETWORKS", raising=False)
    else:
        monkeypatch.setenv("X402_NETWORKS", networks)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if "server" in sys.modules:
        del sys.modules["server"]
    return importlib.import_module("server")


# --- network registry ---------------------------------------------------

def test_registry_has_base_and_algorand(monkeypatch):
    s = _load(monkeypatch, None)
    assert "base" in s.NETWORKS
    assert "algorand" in s.NETWORKS
    assert s.NETWORKS["base"]["network"] == "eip155:8453"
    # Full CAIP-2 — MUST match the GoPlausible facilitator's /supported string
    # so Algorand proofs verify. A truncated genesis-hash makes the rail unmatchable.
    assert s.NETWORKS["algorand"]["network"] == "algorand:wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="


def test_algorand_uses_usdc_asa_id(monkeypatch):
    s = _load(monkeypatch, None)
    algo = s.NETWORKS["algorand"]
    # USDC on Algorand mainnet is ASA 31566704, 6 decimals
    assert algo["asset"] == "31566704"
    assert algo["decimals"] == 6


# --- default behaviour (backward compat) --------------------------------

def test_default_is_base_only(monkeypatch):
    s = _load(monkeypatch, None)
    payload = s.build_payment_required("Token Security", 0.01)
    assert len(payload["accepts"]) == 1
    assert payload["accepts"][0]["network"] == "eip155:8453"


def test_base_accept_shape_unchanged(monkeypatch):
    s = _load(monkeypatch, None)
    acc = s.build_payment_required("Token Security", 0.01)["accepts"][0]
    assert acc["scheme"] == "exact"
    assert acc["asset"] == "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    assert acc["amount"] == "10000"  # 0.01 * 1e6
    assert acc["maxTimeoutSeconds"] == 300
    assert acc["extra"]["name"] == "USD Coin"


# --- multi-network ------------------------------------------------------

def test_two_networks_emits_two_accepts(monkeypatch):
    monkeypatch.setenv("X402_PAYTO_ALGORAND", "A" * 58)
    s = _load(monkeypatch, "base,algorand")
    accepts = s.build_payment_required("Token Security", 0.01)["accepts"]
    assert len(accepts) == 2
    nets = [a["network"] for a in accepts]
    assert "eip155:8453" in nets
    assert any(n.startswith("algorand:") for n in nets)


def test_algorand_amount_is_atomic_for_its_decimals(monkeypatch):
    monkeypatch.setenv("X402_PAYTO_ALGORAND", "A" * 58)
    s = _load(monkeypatch, "algorand")
    acc = s.build_payment_required("Token Security", 0.25)["accepts"][0]
    assert acc["amount"] == "250000"  # 0.25 * 1e6


def test_algorand_accept_carries_challenge_tag(monkeypatch):
    """Algorand rail must carry the x402-global-challenge tag (Algorand Global
    x402 Challenge: the tag in the resource x402 config is how activity is
    attributed to the competition)."""
    monkeypatch.setenv("X402_PAYTO_ALGORAND", "A" * 58)
    s = _load(monkeypatch, "algorand")
    acc = s.build_payment_required("Token Security", 0.01)["accepts"][0]
    assert acc["extra"].get("tag") == "x402-global-challenge"


def test_unknown_network_is_ignored_not_fatal(monkeypatch):
    s = _load(monkeypatch, "base,dogecoin")
    accepts = s.build_payment_required("Token Security", 0.01)["accepts"]
    assert len(accepts) == 1
    assert accepts[0]["network"] == "eip155:8453"


def test_all_networks_unknown_falls_back_to_base(monkeypatch):
    s = _load(monkeypatch, "dogecoin,litecoin")
    accepts = s.build_payment_required("Token Security", 0.01)["accepts"]
    assert len(accepts) == 1
    assert accepts[0]["network"] == "eip155:8453"


def test_algorand_omitted_when_no_payto_configured(monkeypatch):
    """Never advertise a network we cannot actually receive on."""
    monkeypatch.delenv("X402_PAYTO_ALGORAND", raising=False)
    s = _load(monkeypatch, "base,algorand")
    accepts = s.build_payment_required("Token Security", 0.01)["accepts"]
    nets = [a["network"] for a in accepts]
    assert not any(n.startswith("algorand:") for n in nets)
    assert "eip155:8453" in nets


# --- proof network matching ---------------------------------------------

def test_proof_network_accepted_when_enabled(monkeypatch):
    monkeypatch.setenv("X402_PAYTO_ALGORAND", "A" * 58)
    s = _load(monkeypatch, "base,algorand")
    algo_caip = s.NETWORKS["algorand"]["network"]
    assert s.is_network_accepted(algo_caip) is True
    assert s.is_network_accepted("eip155:8453") is True


def test_proof_network_rejected_when_not_enabled(monkeypatch):
    s = _load(monkeypatch, "base")
    algo_caip = s.NETWORKS["algorand"]["network"]
    assert s.is_network_accepted(algo_caip) is False


def test_missing_network_field_defaults_to_accepted(monkeypatch):
    """Older clients omit `network`; don't break them."""
    s = _load(monkeypatch, "base")
    assert s.is_network_accepted(None) is True
    assert s.is_network_accepted("") is True


# --- payload still serializes -------------------------------------------

def test_payload_json_serializable(monkeypatch):
    monkeypatch.setenv("X402_PAYTO_ALGORAND", "A" * 58)
    s = _load(monkeypatch, "base,algorand")
    payload = s.build_payment_required("Token Security", 0.01)
    blob = json.dumps(payload)
    assert json.loads(blob)["x402Version"] == 2


# --- verification path integration --------------------------------------

def _signed_proof(s, amount="10000", network=None):
    import hashlib as _h, hmac as _hm, json as _j
    secret = "dev-secret-change-in-production"
    recipient, nonce, va, vb = "0xabc", "n1", 0, 0
    sig = _hm.new(secret.encode(),
                  f"{amount}:{recipient}:{nonce}:{va}:{vb}".encode(),
                  _h.sha256).hexdigest()
    p = {"amount": amount, "recipient": recipient, "nonce": nonce,
         "validAfter": va, "validBefore": vb, "signature": sig}
    if network is not None:
        p["network"] = network
    return _j.dumps(p)


def test_simulation_accepts_enabled_network(monkeypatch):
    monkeypatch.setenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    s = _load(monkeypatch, "base")
    ok, reason = s.verify_proof_simulation(_signed_proof(s, network="eip155:8453"), 0.01)
    assert ok, reason


def test_simulation_rejects_disabled_network(monkeypatch):
    monkeypatch.setenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    s = _load(monkeypatch, "base")
    algo = s.NETWORKS["algorand"]["network"]
    ok, reason = s.verify_proof_simulation(_signed_proof(s, network=algo), 0.01)
    assert not ok
    assert "not accepted" in reason


def test_simulation_accepts_algorand_when_enabled(monkeypatch):
    monkeypatch.setenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    monkeypatch.setenv("X402_PAYTO_ALGORAND", "A" * 58)
    s = _load(monkeypatch, "base,algorand")
    algo = s.NETWORKS["algorand"]["network"]
    ok, reason = s.verify_proof_simulation(_signed_proof(s, network=algo), 0.01)
    assert ok, reason


def test_simulation_legacy_proof_without_network_still_works(monkeypatch):
    monkeypatch.setenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    s = _load(monkeypatch, "base")
    ok, reason = s.verify_proof_simulation(_signed_proof(s), 0.01)
    assert ok, reason


# --- GoPlausible routing ---------------------------------------------------

def test_proof_network_extraction_v2_envelope(monkeypatch):
    s = _load(monkeypatch, None)
    algo = s.NETWORKS["algorand"]["network"]
    proof = json.dumps({
        "paymentPayload": {"accepted": {"network": algo}},
    })
    assert s._proof_network(proof) == algo


def test_proof_network_extraction_flat(monkeypatch):
    s = _load(monkeypatch, None)
    proof = json.dumps({"network": "eip155:8453"})
    assert s._proof_network(proof) == "eip155:8453"


def test_proof_network_returns_none_on_garbage(monkeypatch):
    s = _load(monkeypatch, None)
    assert s._proof_network("not-json-{{") is None
    assert s._proof_network("") is None
