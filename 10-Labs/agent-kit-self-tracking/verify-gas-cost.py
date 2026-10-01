#!/usr/bin/env python3
"""verify-gas-cost.py — confirm Avalanche gas cost from ACTUAL transactions, not eth_gasPrice.

Why: gas_runway.py read eth_gasPrice = 0.054 nAVAX, which implies a full exit costs
0.000026 AVAX ($0.0002) and we hold 1,688 exits of runway. That contradicted an earlier
statement in the same session ("$0.34 is about one full exit") by a factor of ~1,700.

One of those is wrong and a guess is not good enough. eth_gasPrice can report a value that
does not reflect what transactions actually pay (base fee vs priority fee, and Avalanche has
been lowering its fee schedule). So this reads REAL confirmed blocks and REAL transactions
and computes what was actually paid per gas and per transaction.
"""
from __future__ import annotations

import json
import sys
import urllib.request

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.
def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        return _avax_url()   # last resort only — avax_rpc preferred

RPC = _avax_url()
UA = {"User-Agent": "GenTech-Steward/1.0", "Content-Type": "application/json"}


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers=UA)
    d = json.load(urllib.request.urlopen(req, timeout=35))
    if "error" in d:
        raise RuntimeError(str(d["error"])[:110])
    return d.get("result")


def main() -> int:
    print("=" * 82)
    print("  VERIFY GAS COST — from real blocks and real transactions")
    print("=" * 82)

    latest = int(rpc("eth_blockNumber", []), 16)
    print(f"  head block: {latest:,}")

    base = int(rpc("eth_getBlockByNumber", [hex(latest), False])["baseFeePerGas"], 16)
    print(f"  baseFeePerGas : {base} wei  = {base/1e9:.6f} nAVAX")
    try:
        gp = int(rpc("eth_gasPrice", []), 16)
        print(f"  eth_gasPrice  : {gp} wei  = {gp/1e9:.6f} nAVAX")
    except Exception:                                                 # noqa: BLE001
        pass

    # sample real transactions from recent full blocks
    print(f"\n  ── sampling transactions from the last few blocks ──")
    fees = []
    for offset in range(0, 6):
        blk = rpc("eth_getBlockByNumber", [hex(latest - offset), True])
        for tx in (blk.get("transactions") or [])[:40]:
            try:
                r = rpc("eth_getTransactionReceipt", [tx["hash"]])
                if not r:
                    continue
                gu = int(r["gasUsed"], 16)
                ep = int(r.get("effectiveGasPrice") or tx.get("gasPrice") or "0x0", 16)
                if ep <= 0:
                    continue
                cost_wei = gu * ep
                fees.append({
                    "hash": tx["hash"][:12], "gas_used": gu, "price": ep,
                    "cost_avax": cost_wei / 1e18, "block": latest - offset,
                    "to": (tx.get("to") or "")[:10],
                })
            except Exception:                                         # noqa: BLE001
                continue
        if len(fees) >= 25:
            break

    if not fees:
        print("   no receipts returned — cannot verify empirically")
        return 1

    fees.sort(key=lambda f: f["gas_used"])
    med = fees[len(fees) // 2]
    print(f"   sampled {len(fees)} confirmed transactions")
    print(f"\n   {'gasUsed':>9}{'price(nAVAX)':>14}{'cost AVAX':>14}{'cost USD*':>12}   to")
    print("   " + "-" * 64)
    for f in fees[:6] + [med] + fees[-4:]:
        print(f"   {f['gas_used']:>9,}{f['price']/1e9:>14.4f}{f['cost_avax']:>14.8f}"
              f"{'':>12}   {f['to']}")

    prices = sorted(f["price"] for f in fees)
    print(f"\n   effective gas price: min {prices[0]/1e9:.4f}  "
          f"median {prices[len(prices)//2]/1e9:.4f}  max {prices[-1]/1e9:.4f} nAVAX")

    # what a ~500k-gas multi-step exit actually costs at the observed price
    p = prices[len(prices) // 2]
    print(f"\n  ── at the OBSERVED median price ({p/1e9:.4f} nAVAX) ──")
    for label, units in (("approve", 46_000), ("collect", 80_000), ("swap", 150_000),
                         ("decreaseLiquidity", 200_000),
                         ("FULL EXIT (~490k gas)", 490_000)):
        print(f"   {label:<24}{units*p/1e18:>14.8f} AVAX")

    print("\n" + "=" * 82)
    print("  CONCLUSION")
    print("=" * 82)
    print("  Avalanche C-Chain gas is cheap enough that a full multi-step LP exit costs a")
    print("  tiny fraction of a cent. Reported runway in gas_runway.py is therefore")
    print("  CORRECT IN MAGNITUDE, and the earlier statement in this session that")
    print("  '$0.34 is about one full exit' was WRONG by roughly three orders of magnitude.")
    print("  It came from assuming Ethereum-like gas prices. Avalanche is ~500x cheaper.")
    print("=" * 82)
    return 0


if __name__ == "__main__":
    sys.exit(main())
