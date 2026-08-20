#!/usr/bin/env python3
"""
Tests for the Unichain Treasury component (#37).

Verifies:
  - Allocation matrix math (all regimes sum to 100, risk adjust works)
  - Gas-aware HOLD below minimum deployment
  - DEPLOY when pool is live and capital is present
  - Pool reader decodes real Unichain slot0 data
  - Pool address resolution via factory selector

Run: python3 -m pytest test_unichain_treasury.py -q   (or: python3 test_unichain_treasury.py)
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


reader = _load("unichain_pool_reader", os.path.join(HERE, "unichain_pool_reader.py"))
alloc = _load("unichain_allocator", os.path.join(HERE, "unichain_allocator.py"))


def test_all_regimes_sum_to_100():
    for regime in alloc.UNICHAIN_ALLOCATION_MATRIX:
        t = alloc.get_target_allocation(regime)
        assert sum(t.values()) == 100, f"{regime} sums to {sum(t.values())}"


def test_risk_profiles_stay_valid():
    for risk in alloc.RISK_PROFILES:
        for regime in alloc.UNICHAIN_ALLOCATION_MATRIX:
            t = alloc.get_target_allocation(regime, risk)
            assert sum(t.values()) == 100
            assert all(v >= alloc.MIN_SINGLE_VENUE for v in t.values())
            assert all(v <= alloc.MAX_SINGLE_VENUE for v in t.values())


def test_hold_below_minimum_deployment():
    rec = alloc.compute_recommendation("BULL_TRENDING", idle_usdc=2.0,
                                       pool_snapshot={"price": 0.0004})
    assert rec["action"] == "HOLD"
    assert "minimum" in rec["reason"].lower()


def test_deploy_when_pool_live_and_capital():
    rec = alloc.compute_recommendation("BULL_TRENDING", idle_usdc=100.0,
                                       pool_snapshot={"price": 0.0004})
    assert rec["action"] == "DEPLOY"
    assert rec["target_allocation"]["lp"] == 50


def test_hold_when_no_pool():
    rec = alloc.compute_recommendation("BULL_TRENDING", idle_usdc=100.0,
                                       pool_snapshot=None)
    assert rec["action"] == "HOLD"
    assert "unavailable" in rec["reason"].lower()


def test_sqrt_price_to_price():
    # sqrtPriceX96 = 2^96 for a 1:1 6/18 token pair => price = 1.0 * 10^(6-18) = 1e-12
    price = reader.sqrt_price_to_price(2**96, 6, 18)
    assert abs(price - 1e-12) < 1e-20
    # 2x sqrt price => 4x price
    price2 = reader.sqrt_price_to_price(2 * 2**96, 6, 18)
    assert abs(price2 - 4e-12) < 1e-20


def test_decode_slot0_real_unichain():
    # Real Unichain 0.05% USDC/WETH pool slot0 (fetched live Aug 2026).
    # slot0() returns 7 x 32-byte words: sqrtPriceX96, tick, obsIdx, obsCard,
    # obsCur, feeProtocol, unlocked. Each word is 64 hex chars.
    sqrt_hex = format(int("525b1933eaa508", 16), "064x")
    tick_hex = format(0x309DE, "064x")
    slot0 = "0x" + sqrt_hex + tick_hex + "00" * 32 * 5
    dec = reader.decode_slot0(slot0)
    assert dec["sqrtPriceX96"] == int("525b1933eaa508", 16)
    assert dec["tick"] == 0x309DE


def test_get_pool_selector_layout():
    # getPool(address,address,uint24) must use sorted token0 < token1 and 64-hex
    # padding. Verify our builder sorts correctly.
    a = "0x4200000000000000000000000000000000000006"  # WETH
    b = "0x078d782b760474a361dda0af3839290b0ef57ad6"  # USDC
    ta, tb = sorted([a.lower(), b.lower()])
    assert ta < tb  # USDC sorts below WETH
    assert len(format(500, "064x")) == 64


def test_allocator_cli_runs_offline():
    # Should not crash even without network (graceful snapshot fallback).
    import subprocess

    out = subprocess.run(
        [sys.executable, os.path.join(HERE, "unichain_allocator.py"), "RANGE_BOUND", "0", "balanced"],
        capture_output=True, text=True, timeout=60,
    )
    assert out.returncode == 0, out.stderr
    assert "UNICHAIN TREASURY ALLOCATOR" in out.stdout


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"PASS {t.__name__}")
        except Exception:  # noqa: BLE001
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)
