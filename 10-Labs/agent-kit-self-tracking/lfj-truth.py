#!/usr/bin/env python3
"""lfj-truth.py — reconcile the LFJ WAVAX/USDC discrepancy (90.7% vs 21.20%) on-chain.

Jordan (2026-09-19): "Yes I want the truth."

THE DISCREPANCY: our earlier measurement recorded LFJ Joe v2.2 WAVAX/USDC at apyBase 90.7%. It now
reports 21.20%, with apyBase7d reading 0.00%. A 4x move in our own lead venue, in a day, with no
corresponding market event. Three possible explanations, and they are distinguishable:

  (a) the aggregator is reporting a DIFFERENT PAIR than before — Joe v2.2 has many WAVAX/USDC pools,
      one per bin step, and we already established that only ONE of them carries real liquidity
  (b) the APR genuinely fell
  (c) the aggregator changed how it computes the fee leg

An aggregator cannot tell us which. The chain can. So: enumerate EVERY WAVAX/USDC Liquidity Book from
the factory, read each one's real reserves, bin step, and fee parameters, and compute the fee APR from
the pool's own on-chain state.

CHAIN IS THE SOURCE OF TRUTH. DefiLlama is the thing under test here, not a reference.
READ-ONLY.
"""
from __future__ import annotations

import json
import urllib.request

# Rotating providers via the shared module.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from avax_rpc import rpc_call as _rpc_call, RpcUnavailable
UA = {"User-Agent": "GenTech-Steward/1.0", "Content-Type": "application/json"}

FACTORY = "0xb43120c4745967fa9b93E79C149E66B0f2D6Fe0c"   # LB Factory (Joe v2.2) on Avalanche
                                                        # — the address our working rehearsal used.
                                                        # 0x9Ad6C38B... is a DIFFERENT factory and
                                                        # returns nothing for these calls.
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
BIN_STEPS = [1, 2, 5, 10, 15, 20, 25, 30, 50, 100]


def rpc(method, params):
    # ROTATES across providers instead of retrying one source-banned host (1015 is per-SOURCE).
    try:
        return _rpc_call(method, params, timeout=45)
    except RpcUnavailable:
        return None


def call(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])


def sel(sig):
    import hashlib
    k = hashlib.sha3_256()
    # keccak256 via pysha3-free path: use the 'sha3' name only if available; else fall back below
    return sig


def keccak(sig: str) -> str:
    try:
        from Crypto.Hash import keccak as _k
        h = _k.new(digest_bits=256)
        h.update(sig.encode())
        return "0x" + h.hexdigest()[:8]
    except Exception:
        pass
    try:
        from eth_utils.crypto import keccak as ek
        return "0x" + ek(text=sig).hex()[:8]
    except Exception:
        pass
    try:
        import sha3  # noqa
        return "0x" + sha3.keccak_256(sig.encode()).hexdigest()[:8]
    except Exception:
        raise RuntimeError("no keccak available")


def w3s():
    return "sha3_256"


# ── live price helper (added 2026-09-20) ───────────────────────────────────────
# Was hardcoded at 8.24 and silently under-valued every position by ~24%.
# A stale constant is not a crash — it is a confidently wrong number.
def _live_avax_usd():
    """Live AVAX/USD from Coinbase. Falls back to the old constant only if the
    network read fails, so the tool degrades rather than dies."""
    try:
        import urllib.request as _u
        _r = _u.urlopen(_u.Request(
            "https://api.exchange.coinbase.com/products/AVAX-USD/ticker",
            headers={"User-Agent": "GenTech-Steward/1.0"}), timeout=15)
        return float(json.loads(_r.read())["price"])
    except Exception:
        return 8.24


def main():
    print("=" * 106)
    print("  LFJ WAVAX/USDC — THE TRUTH, READ FROM THE CHAIN")
    print("=" * 106)

    f_get = keccak("getLBPairInformation(address,address,uint256)")
    f_res = keccak("getReserves()")
    f_bs = keccak("getBinStep()")
    print(f"\n  factory       : {FACTORY}")
    print(f"  selectors     : getLBPairInformation {f_get} · getReserves {f_res} · getBinStep {f_bs}")

    pad = lambda a: a.lower().replace("0x", "").rjust(64, "0")
    found = []
    print(f"\n  {'binStep':>8}  {'LBPair':<44}{'tokenX':<12}{'tokenY':<12}")
    print("  " + "-" * 96)
    for bs in BIN_STEPS:
        data = f_get + pad(WAVAX) + pad(USDC) + hex(bs)[2:].rjust(64, "0")
        raw = call(FACTORY, data)
        if not raw or len(raw) < 2 + 64 * 4:
            continue
        h = raw[2:]
        pair_addr = "0x" + h[64:128][24:]
        created = int(h[128:192], 16)
        ignored = int(h[192:256], 16)
        if int(pair_addr, 16) == 0:
            print(f"  {bs:>8}  0x0 — no pair created")
            continue
        found.append((bs, pair_addr, created, ignored))
        print(f"  {bs:>8}  {pair_addr:<44}created={created} ignored={ignored}")

    if not found:
        print("\n  ❌ no pairs returned — cannot reconcile. Reporting the blocker, not a guess.")
        return 1

    print("\n" + "=" * 106)
    print("  RESERVES + FEE PARAMS PER PAIR  (chain truth)")
    print("=" * 106)
    # Joe v2.2 LBPair getReserves returns (uint128 reserveX, uint128 reserveY)
    f_sfp = keccak("getStaticFeeParameters()")
    print(f"  {'binStep':>8}  {'LBPair':<44}{'resX(raw)':>22}{'resY(raw)':>22}")
    print("  " + "-" * 96)
    rows = []
    for bs, addr, created, ignored in found:
        raw = call(addr, f_res)
        rx = ry = None
        if raw and len(raw) >= 2 + 128:
            h = raw[2:]
            rx = int(h[0:64], 16)
            ry = int(h[64:128], 16)
        sfp = call(addr, f_sfp)
        print(f"  {bs:>8}  {addr:<44}{(f'{rx:,}' if rx is not None else 'n/a'):>22}"
              f"{(f'{ry:,}' if ry is not None else 'n/a'):>22}")
        rows.append({"bs": bs, "addr": addr, "rx": rx, "ry": ry, "sfp": sfp})

    print("\n" + "=" * 106)
    print("  WHICH PAIR IS REAL?  (decimals: WAVAX 18, USDC 6)")
    print("=" * 106)
    print(f"  {'binStep':>8}{'WAVAX':>16}{'USDC':>16}{'TVL @ $8.24':>16}   verdict")
    print("  " + "-" * 96)
    avax_usd = _live_avax_usd() or 8.24
    real = None
    for r in rows:
        if r["rx"] is None:
            continue
        wx = r["rx"] / 1e18
        uy = r["ry"] / 1e6
        tvl = wx * avax_usd + uy
        verdict = "✅ REAL" if tvl > 100_000 else ("· thin" if tvl > 100 else "· EMPTY / decoy")
        if real is None or tvl > real[2]:
            real = (r["bs"], r["addr"], tvl, wx, uy)
        print(f"  {r['bs']:>8}{wx:>16,.4f}{uy:>16,.2f}{tvl:>16,.0f}   {verdict}")

    if real:
        bs, addr, tvl, wx, uy = real
        print(f"\n  → THE REAL PAIR: binStep {bs} at {addr}")
        print(f"      {wx:,.4f} WAVAX + {uy:,.2f} USDC  =  ${tvl:,.0f} at ${avax_usd}/AVAX")

    print("\n" + "=" * 106)
    print("  THE FEE LAW — read from the pool itself, not from an aggregator")
    print("=" * 106)
    for r in rows:
        if r["sfp"] and len(r["sfp"]) > 2 + 64 * 6:
            h = r["sfp"][2:]
            bf = int(h[0:64], 16)
            vfc = int(h[64:128], 16)
            mvf = int(h[192:256], 16)
            ps = int(h[320:384], 16)
            step = r["bs"]
            base_fee_pct = bf * step / 10_000 / 100
            print(f"\n    binStep {step}  ({r['addr']})")
            print(f"      baseFactor {bf} · variableFeeControl {vfc} · "
                  f"maxVolatilityAccumulator {mvf} · protocolShare {ps}")
            print(f"      → BASE FEE (zero volatility): {base_fee_pct:.6f}%")
            print(f"        (baseFactor x binStep / 1e4 / 100 — the pool's own law)")
            break

    print("\n" + "=" * 106)
    print("  NEXT STEP: volume from chain (swap events) to compute the TRUE fee APR.")
    print("  TVL alone cannot settle a fee question — the aggregator's APR needs volume x take / TVL.")
    print("=" * 106)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
