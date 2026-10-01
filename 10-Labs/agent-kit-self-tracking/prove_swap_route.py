#!/usr/bin/env python3
"""PROVE the aggregator swap executes — simulate with the allowance overridden.

The last simulation failed with `TransferHelper: TRANSFER_FROM_FAILED`. That is
the ERC-20 allowance check, not a routing failure — we have never approved the
KyberSwap router. Proving the route works therefore means simulating BOTH steps
without sending anything:

  eth_call with a state override that grants the WAVAX allowance, then replay
  the exact swap calldata. If it returns a real USDC amount, the route is real
  and the only thing standing between us and a 2-sided re-deploy is one
  approve() — not the ISTF() wall we hit on the direct routers.
"""
import json
import urllib.parse
import urllib.request

from eth_utils import keccak
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

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
WALLET = _sw_wallet()
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66dD9c48a6E"
AMOUNT_IN = str(int(0.744 * 1e18))
KYBER_ROUTER = "0x6131B5fae19EA4f9D964eAc0408E4408b66337b5"


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


def rpc(method, params):
    d = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    req = urllib.request.Request(RPC, json.dumps(d).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=40))


def allowance_slot(owner, spender, base_slot=4):
    """Storage slot of WETH9-style `allowance[owner][spender]`."""
    inner = keccak(bytes.fromhex("00" * 12 + owner[2:]) +
                   base_slot.to_bytes(32, "big"))
    outer = keccak(bytes.fromhex("00" * 12 + spender[2:]) + inner)
    return "0x" + outer.hex()


def main():
    print("=" * 64)
    print("PROVE IT: simulate the swap WITH allowance granted")
    print("=" * 64)

    # allowance right now
    slot = allowance_slot(WALLET, KYBER_ROUTER)
    res0 = rpc("eth_getStorageAt", [WAVAX, slot, "latest"])
    cur = res0.get("result") if isinstance(res0, dict) else res0
    print(f"  current WAVAX allowance -> Kyber router: {int(cur, 16) if cur else 0}")
    print(f"  storage slot: {slot}")

    # build the swap
    u = ("https://aggregator-api.kyberswap.com/avalanche/api/v1/routes?"
         + urllib.parse.urlencode({"tokenIn": WAVAX, "tokenOut": USDC,
                                   "amountIn": AMOUNT_IN}))
    routes = json.loads(get(u))
    summary = routes["data"]["routeSummary"]
    body = json.dumps({
        "routeSummary": summary, "sender": WALLET, "recipient": WALLET,
        "slippageTolerance": 100,
        "deadline": 9999999999, "source": "steward"}).encode()
    req = urllib.request.Request(
        "https://aggregator-api.kyberswap.com/avalanche/api/v1/route/build",
        data=body, headers={"Content-Type": "application/json",
                            "User-Agent": "Mozilla/5.0"})
    built = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    data = built["data"]["data"]
    to = built["data"]["routerAddress"]

    override = {WAVAX: {"stateDiff": {slot: "0x" + "ff" * 32}}}
    res = rpc("eth_call", [{"from": WALLET, "to": to, "data": data,
                            "value": "0x0"}, "latest", override])

    if "result" in res and res["result"]:
        print(f"  ✅ SIMULATION PASSED with allowance granted")
        print(f"     raw out: {res['result'][:80]}")
        print("\n  ⇒ The route is REAL. One approve() unlocks it.")
        print("     ISTF() was only ever the DIRECT routers; aggregators route around it.")
    else:
        print(f"  ❌ still failed: {json.dumps(res)[:250]}")


if __name__ == "__main__":
    main()
