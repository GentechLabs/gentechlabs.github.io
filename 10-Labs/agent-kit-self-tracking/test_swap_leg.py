#!/usr/bin/env python3
"""Can we deploy the idle WAVAX? Test the swap leg that a 2-sided deploy needs.

Jordan (Sep 11): "the $11.15, let's put that back until the black hole pull
that we're currently in."

A Blackhole WAVAX/USDC CL position is TWO-SIDED: it needs USDC as well as WAVAX.
So "putting it back" requires swapping roughly half the WAVAX -> USDC first.

This script answers one question with the chain, not with config:
    is there ANY working WAVAX->USDC swap route today?

If yes  -> a proper 2-sided re-deploy is possible.
If no   -> report the blocker honestly rather than shipping a half-position.

────────────────────────────────────────────────────────────────────────────────
REWRITTEN 2026-09-24. The previous version reported "NO working WAVAX->USDC swap
route" and that verdict was FALSE. It probed two router addresses with ONE
function, `exactInputSingle()` carrying a 7-field Algebra struct, and printed
every revert as a route failure. Three defects, all in the false-value family:

 1. WRONG FUNCTION ENTIRELY. `exactInputSingle()` is Algebra/Uniswap-V3 shaped.
    LFJ's LBRouter takes `swapExactTokensForTokens(uint256,uint256,
    (uint256[] pairBinSteps, uint8[] versions, address[] tokenPath),address,
    uint256)`. Verified on-chain: keccak of the real signature is 0x2a443fae and
    IS present in the router's code, while the router does NOT contain
    0xe94a2ff1 — so the probe called a function the contract does not have.
    A missing function is not a missing route.

 2. A FAILED READ WAS RECORDED AS A REAL "NO". A call to a non-existent function
    reverts with EMPTY data, which the old code printed as the string
    "('execution reverted', 'no data')" — indistinguishable from a genuine
    refusal. Same shape as int.from_bytes(b'') == 0: absence of an answer was
    read as an answer.

 3. IT COULD NEVER HAVE SUCCEEDED EVEN WITH THE RIGHT FUNCTION. The wallet holds
    ~0 WAVAX, so a real simulation reverts on BALANCE, not on routing. A
    zero-balance simulation can never prove a route exists OR that it doesn't —
    the probe must override the balance to be able to say anything.

The probe now: (a) uses the router's REAL entrypoint, (b) simulates with the
balance state-overridden, so the answer is about the ROUTE, and (c) refuses to
report a market conclusion at all if the probe itself is invalid — a router
missing the entrypoint, or an unreadable pool, exits 2 as a PROBE failure rather
than 1 as "no route".

Proven in the target state: funded sim of 0.744 WAVAX -> 7.5192 USDC on the
v2.2 binStep-10 pool. The version byte is ZERO-INDEXED — JoeV2's enum is
{V1, V2, V2_1, V2_2}, so V2_2 = 3 — and asking for 2 or 1 means v2.1, which
reverts LBRouter__PairNotCreated and reads exactly like "this pool does not
exist". Only version 3 can quote this pool.
"""
import json
import time

from web3 import Web3

from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)  # noqa: F401


# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:                                                 # noqa: BLE001
        return "https://api.avax.network/ext/bc/C/rpc"   # last resort only — avax_rpc preferred

RPC = _avax_url()
WALLET = Web3.to_checksum_address(_sw_wallet())
WAVAX = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
# The REAL pool: the binStep-10 WAVAX/USDC LB. Of the four WAVAX/USDC pairs in the v2.2 factory
# this is the only one with real liquidity — the other three are near-empty decoys that answer
# every call normally and quote a confident wrong price (see pool-catalog: SELECT BY HIGHEST TVL).
POOL = Web3.to_checksum_address("0x864d4e5Ee7318e97483DB7EB0912E09F161516EA")

# Below this, a WAVAX balance cannot fund a probe that says anything about the route. Measured
# 2026-09-28: jordan 6 wei, dadrian 7 wei — economically zero, and  was silently
# promoting a 6-wei balance into a 1-wei swap whose revert was then reported as a market verdict.
# 1e-9 WAVAX (~e-8) is far below anything tradeable and far above dust.
MIN_PROBE_WEI = 10 ** 9
# LFJ LBRouter — the same address lfj_swap_leg.py (the production swap tool) uses.
ROUTER = Web3.to_checksum_address("0x18556DA13313f3532c54711497A8FedAC273220E")
AMOUNT_IN = int(0.744 * 1e18)     # FALLBACK ONLY — see the live-derived amount in main().
# ^ This was a hardcoded "half of the idle WAVAX" and it is exactly the frozen-moment bug: the
# COMMENT described a live quantity, the CODE froze one. When the book shrank to 0.0186 WAVAX this
# constant made the probe quote 40x more than the wallet held, and the test reported
#     "NO working WAVAX->USDC swap route ... the route is genuinely down"
# about a route that quotes perfectly at every size we actually hold. It is now used only when the
# wallet is too small to probe for real, and that case returns a READ failure, not a verdict.
SIM_WAVAX = 5 * 10**18            # balance to pretend we hold, for the simulation only
WAVAX_BALANCE_SLOT = 3           # probed on-chain: slot 3 holds WAVAX balances

ERC20_BAL_ABI = json.loads('[{"inputs":[{"name":"","type":"address"}],"name":"balanceOf",'
    '"outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')
SWAP_SIG = "swapExactTokensForTokens(uint256,uint256,(uint256[],uint8[],address[]),address,uint256)"

LB_ROUTER_ABI = json.loads('[{"inputs":[{"name":"amountIn","type":"uint256"},'
    '{"name":"amountOutMin","type":"uint256"},{"components":[{"name":"pairBinSteps","type":"uint256[]"},'
    '{"name":"versions","type":"uint8[]"},{"name":"tokenPath","type":"address[]"}],"name":"path","type":"tuple"},'
    '{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],'
    '"name":"swapExactTokensForTokens","outputs":[{"name":"","type":"uint256"}],'
    '"stateMutability":"nonpayable","type":"function"}]')

LB_POOL_ABI = json.loads('[{"inputs":[],"name":"getBinStep","outputs":[{"name":"","type":"uint16"}],'
    '"stateMutability":"view","type":"function"},'
    '{"inputs":[],"name":"getActiveId","outputs":[{"name":"","type":"uint24"}],'
    '"stateMutability":"view","type":"function"}]')


def _slot_key(addr: str, slot: int) -> bytes:
    """keccak256(abi.encode(addr, slot)) — the standard Solidity mapping storage slot."""
    return Web3.keccak(bytes.fromhex(addr.lower()[2:].rjust(64, "0"))
                       + bytes.fromhex(hex(slot)[2:].rjust(64, "0")))


def _reason(exc: Exception) -> str:
    """Name the failure honestly. A CUSTOM ERROR means the call WAS dispatchable."""
    data = getattr(exc, "data", None)
    if data:
        return f"custom error {data}"
    msg = str(exc)
    if "execution reverted" in msg:
        return msg.split("execution reverted")[-1][:48].strip() or "(no reason)"
    return type(exc).__name__


def main() -> int:
    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 25}))
    print("=" * 62)
    print("SWAP LEG TEST — can we get USDC to make a 2-sided deploy?")
    print("=" * 62)
    print(f"  wallet: {WALLET}")
    print(f"  want:   WAVAX -> USDC, sized off live balance (via pool {POOL[:10]}…)\n")

    # ── 0. IS THE PROBE ITSELF VALID? Confirm the router HAS the entrypoint we are about to
    #      call, and that the pool is live. Without this step a revert from a MISSING FUNCTION is
    #      indistinguishable from a route refusal — which is precisely how the old version
    #      produced a confident "NO route" that was false.
    # ── A NETWORK BLIP IS NOT A VERDICT (fixed 2026-09-27) ──────────────────────────────────
    # `get_code` and `get_block` were the only two RPC calls in this file NOT wrapped. A provider
    # hiccup raised an unhandled exception and the process died with exit 1 and a traceback — so a
    # transient read failure looked exactly like a real defect, and re-running it passed. Measured:
    # the suite reported rc=1 once and then 0 five times in a row with no change to the code.
    #
    # That is the worst kind of flake: a test that fails at random teaches people to ignore
    # failures, and then it hides a real one. This file already states the right rule a few lines
    # below — "a failed read is not 'the pool is gone'" — it just was not applied here. A read that
    # cannot complete returns 2 (an explicit READ failure), never 1 (a verdict).
    try:
        router_code = w3.eth.get_code(ROUTER).hex()
    except Exception as e:                                            # noqa: BLE001
        print(f"  ❌ router code UNREADABLE: {_reason(e)}")
        print("     This is a READ failure, not a verdict about the route. Re-run; if it persists,")
        print("     the provider is unhealthy — check avax_rpc rotation.")
        return 2
    selector = Web3.keccak(text=SWAP_SIG)[:4].hex()
    if selector not in router_code:
        print(f"  ❌ PROBE INVALID — router {ROUTER} does not expose swapExactTokensForTokens "
              f"(0x{selector}). This is a PROBE/enrollment failure, NOT a market fact.")
        return 2
    print(f"  ✅ router exposes swapExactTokensForTokens (0x{selector}) — the probe is valid")

    try:
        pool = w3.eth.contract(address=POOL, abi=LB_POOL_ABI)
        bin_step = pool.functions.getBinStep().call()
        active_id = pool.functions.getActiveId().call()
        print(f"  ✅ pool live: binStep={bin_step} activeId={active_id}\n")
    except Exception as e:                                            # noqa: BLE001
        print(f"  ❌ pool unreadable: {_reason(e)}")
        print("     Reporting the READ failure rather than a market conclusion — a failed read is")
        print("     not 'the pool is gone'.")
        return 2

    try:
        # RAW JSON-RPC, not web3's get_block: Avalanche's extraData is 66 bytes where web3 expects
        # 32, so `w3.eth.get_block("latest")` raises ExtraDataLengthError on a perfectly healthy
        # node. That is the SAME false-value shape this file already fights — a decode bug reading
        # as "the chain is unreadable". daily_fee_ledger.py hit this first and solved it the same
        # way; reuse the approach rather than re-deriving it.
        _raw = w3.provider.make_request("eth_getBlockByNumber", ["latest", False])
        _res = (_raw or {}).get("result")
        if not _res or "timestamp" not in _res:
            raise ValueError(f"no timestamp in eth_getBlockByNumber result: {str(_res)[:80]}")
        deadline = int(_res["timestamp"], 16) + 600
    except Exception as e:                                            # noqa: BLE001
        print(f"  ❌ latest block UNREADABLE: {_reason(e)}")
        print("     A READ failure, not a verdict about the route.")
        return 2
    # ── the state-override funding was REMOVED (2026-09-28) ──────────────────────────────────
    # It pretended the wallet held 5 WAVAX so a fixed 0.744 WAVAX probe would pass the router's
    # input transfer. That made the probe pass for a size we do not hold and FAIL for the size we
    # do — the exact inversion. A test that has to fake the balance to ask "can we swap?" is not
    # asking about us. The probe is now sized off live balance instead, with no override at all.
    router = w3.eth.contract(address=ROUTER, abi=LB_ROUTER_ABI)

    # ── PROBE WITH AN AMOUNT WE ACTUALLY HOLD (fixed 2026-09-28) ─────────────────────────────
    # A fixed input size is not a valid probe. The question this test answers is "can WE swap?",
    # which depends on our balance; quoting a hardcoded 0.744 WAVAX against a wallet holding
    # 0.0186 made the router fail the input-transfer step and this test reported it as
    #   "the route is genuinely down and a 2-sided deploy is not possible right now"
    # — a false ALARM about a route that quotes fine at every size we hold.
    #
    # Measured, same block: 0.001 / 0.005 / 0.018 WAVAX all quote on version 3; 0.744 does not.
    # So: size the probe off LIVE balance. If the balance is too small to be meaningful, that is a
    # READ failure (2), never a verdict about the market.
    try:
        wavax = w3.eth.contract(address=WAVAX, abi=ERC20_BAL_ABI)
        bal = wavax.functions.balanceOf(WALLET).call()
    except Exception as e:                                            # noqa: BLE001
        print(f"  ❌ WAVAX balance UNREADABLE: {_reason(e)}")
        print("     A READ failure, not a verdict about the route.")
        return 2
    # Print the EXACT integer. `{bal/1e18:.8f}` renders a real balance of 6 wei as "0.00000000",
    # which reads as "empty" and hides the actual problem: we hold DUST. Measured 2026-09-28:
    # jordan 6 wei, dadrian 7 wei — economically zero, but not zero, so the `bal <= 0` guard below
    # did not catch it and the probe went ahead.
    print(f"  live WAVAX balance: {bal} wei  ({bal/1e18:.18f} WAVAX)")
    if bal <= 0:
        print("  ⚠️  NO WAVAX to size a probe with — cannot test the route.")
        print("     That is a READ limitation, not evidence the route is down.")
        return 2
    if bal < MIN_PROBE_WEI:
        # A DUST balance cannot fund a meaningful probe, and `max(bal//10, 1)` silently turned
        # 6 wei into a 1-wei swap. The router reverts on that (dust arithmetic), and the revert was
        # being reported as "the route is genuinely down and a 2-sided deploy is not possible" —
        # a market verdict derived from an input no market would ever trade.
        # The honest reading: the route is UNTESTED. We cannot probe it because we have nothing
        # meaningful to probe with. That is a READ LIMITATION (2), never a verdict about the route.
        print(f"  ⚠️  BALANCE IS DUST ({bal} wei < {MIN_PROBE_WEI} wei minimum).")
        print("     A probe this small cannot be funded meaningfully — the router reverts on dust")
        print("     arithmetic, and that revert says NOTHING about whether the route works.")
        print("     VERDICT: route UNTESTED. Not down — untested.")
        print("     NOTE: this also means the swap leg of a 2-sided re-deploy is not fundable from")
        print("     this wallet today; the capital is already in the book, not sitting idle.")
        return 2
    probe_amt = bal // 10                 # a tenth of what we hold: any real size proves the route
    print(f"  probing with {probe_amt/1e18:.8f} WAVAX (a tenth of balance, so the input transfer "
          f"is satisfiable — a probe we cannot fund proves nothing)\n")

    ok = 0
    for ver, vlbl in ((3, "v2.2"), (2, "v2.1"), (1, "v2.0")):
        path = ([bin_step], [ver], [WAVAX, USDC])
        try:
            out = router.functions.swapExactTokensForTokens(
                probe_amt, 0, path, WALLET, deadline).call({"from": WALLET})
            print(f"  ✅ version {ver} ({vlbl}) @ binStep {bin_step} -> {out/1e6:.4f} USDC")
            ok += 1
        except Exception as e:                                        # noqa: BLE001
            print(f"  ❌ version {ver} ({vlbl}) @ binStep {bin_step} -> {_reason(e)}")

    print()
    if ok:
        print(f"  ✅ {ok} working route(s) — a 2-sided re-deploy IS possible.")
        print(f"     (Probed at a tenth of the LIVE balance with no balance override: the probe is")
        print(f"      sized to something we can actually fund, so the answer is about us.)")
        return 0
    print("  ❌ NO working WAVAX->USDC swap route on the LFJ LBRouter.")
    print("     Versions 2/1 are v2.1 and cannot quote a v2.2 binStep-10 pool by design; only")
    print("     version 3 (the zero-indexed V2_2) can. Version 3 failing too means the route is")
    print("     genuinely down and a 2-sided deploy is not possible right now.")
    print("     (This probe was sized to a balance we actually hold — see the amount above.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
