#!/usr/bin/env python3
"""Test the SIE x402 service adapter — verifies 402 gating and health."""
import json
import sys
import httpx

BASE = "http://127.0.0.1:8101"


def test_health():
    r = httpx.get(f"{BASE}/v1/health", timeout=10)
    assert r.status_code == 200, f"health: {r.status_code}"
    body = r.json()
    assert body["status"] == "ok"
    print(f"  health ok: {body}")
    return body


def test_402_gate():
    # Direct call without x-402-token must be rejected with 402
    r = httpx.post(
        f"{BASE}/v1/embeddings",
        json={"model": "sentence-transformers/all-MiniLM-L6-v2", "input": "hello"},
        timeout=10,
    )
    assert r.status_code == 402, f"expected 402, got {r.status_code}: {r.text[:200]}"
    body = r.json()
    assert body["error"] == "payment_required"
    print(f"  402 gate ok: {body['error']}")
    return True


def test_paid_path():
    # With x-402-token set (as the gateway does after verify), the adapter
    # forwards to SIE. If SIE isn't running, we expect a 5xx from the proxy —
    # which proves the paid path is reached (not the 402 gate).
    r = httpx.post(
        f"{BASE}/v1/embeddings",
        json={"model": "sentence-transformers/all-MiniLM-L6-v2", "input": "hello"},
        headers={"x-402-token": "test-proof"},
        timeout=15,
    )
    print(f"  paid path (SIE down expected): HTTP {r.status_code}")
    # 5xx from proxy = reached backend; 200 = SIE live. Either is past the gate.
    assert r.status_code != 402, "paid path should not 402"
    return True


if __name__ == "__main__":
    print("Testing SIE x402 service adapter...")
    test_health()
    test_402_gate()
    test_paid_path()
    print("ALL TESTS PASSED")
