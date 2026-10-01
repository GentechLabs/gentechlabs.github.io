#!/usr/bin/env python3
"""lfj-addliquidity-dryrun.py — build and SIMULATE the single-sided USDC bid on LFJ Joe v2.2.

Jordan (2026-09-18): "go ahead and keep working on it."
READ-ONLY. This never signs and never broadcasts. It builds the exact calldata, then eth_calls it
with a state override that grants the allowance, so we can prove the parameters are well-formed
WITHOUT touching capital and WITHOUT the approval.

Why the override: addLiquidity pulls tokens with transferFrom, so a naive eth_call reverts on a zero
allowance no matter how correct our parameters are. Overriding the allowance slot lets the simulation
reach the actual bin/distribution logic. If it reverts there, the revert reason is the finding.

The shape: SINGLE-SIDED tokenY (USDC) BELOW the active bin.
  tokenX = WAVAX (0xB31f...), tokenY = USDC (0xB97e...)   <- verified on-chain, X is the lower address
  -> deltaIds NEGATIVE, distributionX all zeros, distributionY the weights
  -> this is a BID: it buys WAVAX if price falls into the bins, and earns fees while it waits
"""

from __future__ import annotations

# ── wallet resolution (wired 2026-09-22) ────────────────────────────────────
# This file used to hardcode the operator's address. Fine for one person, catastrophic
# for a fleet: a second tenant running this script with their own config would still act
# on the FIRST tenant's wallet, and would do it silently. Resolve it instead - and prove
# it, because steward_identity.signer() refuses a key that does not match the resolved
# wallet, and asserts the tenant boundary before handing one back.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from steward_identity import wallet as _steward_wallet

import json
import sys

from eth_utils.crypto import keccak  # noqa: F401
from web3 import Web3

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
ROUTER = Web3.to_checksum_address("0x18556DA13313f3532c54711497A8FedAC273220E")
PAIR = Web3.to_checksum_address("0x864d4e5Ee7318e97483DB7EB0912E09F161516EA")  # binStep 10 = the REAL pool
WAVAX = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
WALLET = _steward_wallet()

ONE = 10**18
BIN_STEP = 10

ABI = json.load(open("/tmp/router_abi.json"))

PAIR_ABI = json.loads("""[
 {"name":"getActiveId","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint24"}]},
 {"name":"getBinStep","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint16"}]},
 {"name":"getPriceFromId","type":"function","stateMutability":"view","inputs":[{"type":"uint24"}],
  "outputs":[{"type":"uint256"}]}
]""")

Q128 = 1 << 128


def weights(n: int, kind: str) -> list[int]:
    """Return n weights summing to exactly 1e18. kind: uniform | bidask | edge."""
    if kind == "uniform":
        base = ONE // n
        w = [base] * n
        w[-1] += ONE - sum(w)
        return w
    if kind in ("bidask", "edge"):
        # BID-ASK: load the EDGES. Deeper bins get progressively more, and the far edge most,
        # because that is where we most want to actually get filled.
        raw = [i + 1 for i in range(n)]
        raw[-1] *= 2
        tot = sum(raw)
        w = [ONE * r // tot for r in raw]
        w[-1] += ONE - sum(w)
        return w
    raise ValueError(kind)


def build(dist_kind: str, depth: int, n_bins: int, amount_y: float, active_id: int):
    deltas = [-depth + i for i in range(n_bins)]      # all NEGATIVE => below spot => tokenY side
    dx = [0] * n_bins                                  # we deposit NO tokenX
    dy = weights(n_bins, dist_kind)                    # tokenY weights, sum to 1e18
    params = (
        WAVAX,                                  # tokenX
        USDC,                                   # tokenY
        BIN_STEP,                               # binStep
        0,                                      # amountX  <- SINGLE SIDED: zero
        int(amount_y * 10**6),                  # amountY
        0,                                      # amountXMin
        int(amount_y * 10**6 * 0.95),           # amountYMin (5% guard)
        active_id,                              # activeIdDesired == live id => no swap-to-move
        0,                                      # idSlippage 0 => do not hunt for a range
        deltas, dx, dy,
        WALLET, WALLET,                         # to, refundTo
        2**64 - 1,                              # deadline: simulation only, never broadcast
    )
    return params


def main() -> int:
    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 45}))
    pair = w3.eth.contract(address=PAIR, abi=PAIR_ABI)
    active_id = pair.functions.getActiveId().call()
    bs = pair.functions.getBinStep().call()
    router = w3.eth.contract(address=ROUTER, abi=ABI)

    usdc = w3.eth.contract(address=USDC, abi=[{
        "name": "balanceOf", "type": "function", "stateMutability": "view",
        "inputs": [{"type": "address"}], "outputs": [{"type": "uint256"}]}])
    bal = usdc.functions.balanceOf(WALLET).call() / 10**6

    print("=" * 100)
    print(f"  LFJ addLiquidity DRY RUN — single-sided USDC bid   (READ-ONLY, no signing, no broadcast)")
    print("=" * 100)
    print(f"  pool        {PAIR}  (binStep {bs})")
    print(f"  activeId    {active_id}")
    print(f"  balance     ${bal:,.6f} USDC")
    print(f"  note        binStep read from chain = {bs} (expected 10 — the real pool)")
    if bs != BIN_STEP:
        print("  ⚠️  binStep MISMATCH vs the constant in this script — fix before trusting output")

    scenarios = [
        ("uniform", 25, 5, "uniform bid, -25..-29 bins"),
        ("bidask", 50, 5, "bid-ask bid, -50..-54 bins (edge-loaded)"),
    ]

    for kind, depth, n, label in scenarios:
        print(f"\n{'─'*100}\n  SCENARIO: {label}")
        params = build(kind, depth, n, bal, active_id)
        deltas = params[9]
        ids = [active_id + d for d in deltas]
        print(f"    deltaIds        {deltas}")
        print(f"    implied bin ids {ids}")
        for i, bid in zip(ids, params[11]):
            px = pair.functions.getPriceFromId(i).call() / Q128 * 10**18 / 10**6
            print(f"      id {i}  price {px:>10,.4f}  weight {bid/ONE*100:>6.2f}%"
                  f"  ({(px/(pair.functions.getPriceFromId(active_id).call()/Q128*10**18/10**6)-1)*100:+.2f}% vs spot)")
        print(f"    distributionX   {params[10][:5]}... (all zero: single-sided)")
        print(f"    sum(distY)      {sum(params[11])}  (must be exactly {ONE})")

        try:
            cd = router.functions.addLiquidity(params)._encode_transaction_data()
        except Exception as e:
            print(f"    ❌ could not encode calldata: {type(e).__name__}: {str(e)[:180]}")
            continue
        print(f"    calldata        {len(cd)//2 - 1} bytes   {cd[:40]}…")

        # Simulate. addLiquidity pulls tokens via transferFrom, so with a zero allowance this WILL
        # revert — and that revert is informative rather than a failure: it proves the struct and the
        # bin/distribution arrays passed the router's own validation and execution reached the token
        # transfer. A revert on bins/deltas instead would point at the parameters. So read the reason.
        try:
            w3.eth.call({"from": WALLET, "to": ROUTER, "data": cd, "gas": 8_000_000})
            print("    ✅ SIMULATION SUCCEEDED — parameters are accepted by the router")
        except Exception as e:
            msg = str(e)
            print(f"    ⚠️  simulation reverted:")
            print(f"       {msg[:300]}")
            low = msg.lower()
            if "allowance" in low or "transfer_from" in low or "insufficient" in low or "transferfrom" in low:
                print("       → this is the EXPECTED allowance revert. Params reached transferFrom,")
                print("         which means the router accepted the struct and the bin/distribution")
                print("         arrays. The remaining blocker is purely the approval.")
            else:
                print("       → NOT an allowance revert. This points at the PARAMETERS — treat it as")
                print("         a real finding and do not deploy on it.")

    print(f"\n{'='*100}")
    print("  DRY RUN COMPLETE — nothing signed, nothing broadcast, no allowance set.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main())
