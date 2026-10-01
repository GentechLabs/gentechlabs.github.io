#!/usr/bin/env python3
"""lfj-bin-rehearsal.py — READ-ONLY rehearsal for Liquidity Book (LFJ Joe v2.2) before capital moves.

Jordan (2026-09-18): "The bin shapes change the game" — and "yes work on this".

Why this exists
---------------
Everything we have run so far is Black Hole CL: tick-based, one range, uniform liquidity inside
it, a fixed fee tier, two-sided only. Liquidity Book is a different machine:

  * BIN IDs, not ticks          — discrete fixed-price bins, not continuous ticks
  * SHAPES, not ranges          — distributionX/distributionY per bin decide "how much, where"
  * SINGLE-SIDED allowed        — deposit ONE asset. This is the whole point for us: we hold USDC
                                  only, so we can be a BID under spot with no swap at all
  * SURGE PRICING               — the take rate moves with volatility; a quoted APR is a snapshot

This script verifies, against live Avalanche contracts, the things that would silently break a
DEPLOY if we assumed they were like Black Hole:

  1. the factory/router really are deployed and what they are
  2. the WAVAX/USDC LBPair exists, and at WHICH bin step
  3. which of the two tokens is X and which is Y  (this decides everything about direction)
  4. the active bin, the bin step, and the resulting price
  5. the token ORDER that dictates where a single-sided USDC position must be placed
  6. whether our own USDC can actually be deposited as a single side (the delta direction test)

NOTHING IS EXECUTED. This makes eth_call reads only. No transaction, no approval, no capital.
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
import math
import sys
import time

from web3 import Web3

# ── AVAX RPC ROTATION — DEFINED BEFORE ITS FIRST USE (2026-09-30) ────────────────────────────────
# DEFECT FIXED: this helper was defined 70 lines BELOW `RPC = _avax_url()`, so the module died on a
# NameError at import and the whole rehearsal was unreachable. It is the BLOCKING PREREQ named by
# build-queue #14, and a prereq whose tool cannot start looks exactly like a prereq nobody has done.
# Python executes module level top to bottom: a function used at import time must be defined above it.
#
# Its fallback also CALLED ITSELF (`return _avax_url()`), which is an infinite recursion the moment the
# import fails -- a last resort that could never be reached. It now falls back to a literal provider.
def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        return "https://avalanche-c-chain-rpc.publicnode.com"   # last resort only


RPC = _avax_url()

# ── LFJ Joe v2.2 on Avalanche (from docs.lfj.gg/lfj-dex/contracts.md) ────────
FACTORY = Web3.to_checksum_address("0xb43120c4745967fa9b93E79C149E66B0f2D6Fe0c")
ROUTER  = Web3.to_checksum_address("0x18556DA13313f3532c54711497A8FedAC273220E")
LIMIT_ORDER = Web3.to_checksum_address("0x03Cf7a8238dA2239BDDE9349f41fa14A81d3Af3d")

WAVAX = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC  = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")

FACTORY_ABI = json.loads("""[
 {"name":"getNumberOfLBPairs","type":"function","stateMutability":"view",
  "inputs":[{"type":"address"},{"type":"address"}],"outputs":[{"type":"uint256"}]},
 {"name":"getAllLBPairs","type":"function","stateMutability":"view",
  "inputs":[{"type":"address"},{"type":"address"}],
  "outputs":[{"components":[{"name":"binStep","type":"uint16"},{"name":"LBPair","type":"address"},
                            {"name":"createdByOwner","type":"bool"},{"name":"ignoredForRouting","type":"bool"}],
              "type":"tuple[]"}]},
 {"name":"getLBPairInformation","type":"function","stateMutability":"view",
  "inputs":[{"type":"address"},{"type":"address"},{"type":"uint256"}],
  "outputs":[{"components":[{"name":"binStep","type":"uint16"},{"name":"LBPair","type":"address"},
                            {"name":"createdByOwner","type":"bool"},{"name":"ignoredForRouting","type":"bool"}],
              "type":"tuple"}]}
]""")

PAIR_ABI = json.loads("""[
 {"name":"getActiveId","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint24"}]},
 {"name":"getBinStep","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint16"}]},
 {"name":"getTokenX","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"address"}]},
 {"name":"getTokenY","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"address"}]},
 {"name":"getReserves","type":"function","stateMutability":"view","inputs":[],
  "outputs":[{"type":"uint128"},{"type":"uint128"}]},
 {"name":"getBin","type":"function","stateMutability":"view","inputs":[{"type":"uint24"}],
  "outputs":[{"type":"uint128"},{"type":"uint128"}]},
 {"name":"getPriceFromId","type":"function","stateMutability":"view","inputs":[{"type":"uint24"}],
  "outputs":[{"type":"uint256"}]},
 {"name":"getStaticFeeParameters","type":"function","stateMutability":"view","inputs":[],
  "outputs":[{"name":"baseFactor","type":"uint16"},{"name":"filterPeriod","type":"uint16"},
             {"name":"decayPeriod","type":"uint16"},{"name":"reductionFactor","type":"uint16"},
             {"name":"variableFeeControl","type":"uint16"},{"name":"protocolShare","type":"uint16"},
             {"name":"maxVolatilityAccumulator","type":"uint32"}]},
 {"name":"getFeeParameters","type":"function","stateMutability":"view","inputs":[],
  "outputs":[{"name":"baseFactor","type":"uint16"},{"name":"filterPeriod","type":"uint16"},
             {"name":"decayPeriod","type":"uint16"},{"name":"reductionFactor","type":"uint16"},
             {"name":"variableFeeControl","type":"uint16"},{"name":"protocolShare","type":"uint16"},
             {"name":"volatilityAccumulator","type":"uint32"}]}
]""")

ERC20_ABI = json.loads("""[
 {"name":"symbol","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"string"}]},
 {"name":"decimals","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint8"}]},
 {"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"type":"address"}],
  "outputs":[{"type":"uint256"}]},
 {"name":"allowance","type":"function","stateMutability":"view",
  "inputs":[{"type":"address"},{"type":"address"}],"outputs":[{"type":"uint256"}]}
]""")

WALLET = _steward_wallet()

Q128 = 1 << 128

# Selectors computed with keccak rather than hand-typed. Guessed selectors are how a live function
# reads as "reverted" — and a reverted eth_call returns 0x, which naive parsers read as zero.
from eth_utils import keccak as _keccak  # noqa: E402

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.

STATIC_FEE_SEL = "0x" + _keccak(text="getStaticFeeParameters()")[:4].hex()
VAR_FEE_SEL = "0x" + _keccak(text="getVariableFeeParameters()")[:4].hex()


def price_from_id(active_id: int, bin_step: int, dec_x: int, dec_y: int) -> float:
    """LB price for a bin id, in human units.

    LB bin ids are offset by 2**23, so the raw relation is  price = (1 + binStep/1e4) ** (id - 2**23).
    The first version of this function omitted the offset and raised 1.01 ** 8388608 — which is why
    every pair read as an OverflowError instead of a price. Raising a float that far is out of range;
    the offset is what keeps the exponent small.

    Even with the offset this is OUR arithmetic. The contract has getPriceFromId(id) and that is
    chain truth — main() prefers it and only falls back to this.
    """
    exp = active_id - (1 << 23)
    return math.exp(exp * math.log1p(bin_step / 10_000)) * (10 ** dec_x) / (10 ** dec_y)


def main() -> int:
    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 45}))
    if not w3.is_connected():
        print("  RPC unreachable — aborting rather than guessing")
        return 1

    print("=" * 100)
    print(f"  LFJ LIQUIDITY BOOK — BIN REHEARSAL (READ-ONLY, no transactions)   {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}")
    print("=" * 100)

    f = w3.eth.contract(address=FACTORY, abi=FACTORY_ABI)
    r = w3.eth.contract(address=ROUTER, abi=ERC20_ABI) if False else None

    # 1 ── contracts really exist
    print("\n1 ── CONTRACTS ON AVALANCHE")
    for name, addr in (("Factory V2.2", FACTORY), ("Router V2.2", ROUTER), ("Limit Order V3", LIMIT_ORDER)):
        code = w3.eth.get_code(addr)
        print(f"   {name:<16} {addr}  {'✅ ' + str((len(code) - 2) // 2) + ' bytes' if len(code) > 2 else '❌ NOT DEPLOYED'}")

    # 2 ── which token is X, which is Y (address order decides; this governs everything)
    print("\n2 ── TOKEN ORDER (the lower address is X; this decides where a single-sided position goes)")
    x_addr, y_addr = sorted([WAVAX, USDC], key=lambda a: int(a, 16))
    print(f"   tokenX (lower addr) = {x_addr}")
    print(f"   tokenY (higher addr) = {y_addr}")
    is_wavax_x = x_addr == WAVAX
    print(f"   → {'WAVAX' if is_wavax_x else 'USDC'} is X, {'USDC' if is_wavax_x else 'WAVAX'} is Y")
    print(f"   → we hold USDC, so USDC is token{'X' if not is_wavax_x else 'Y'}")
    print(f"   → price P = tokenY per tokenX = {'USDC per WAVAX' if is_wavax_x else 'WAVAX per USDC'}")
    print("   → a SINGLE-SIDED position in tokenY must sit BELOW the active bin (it buys tokenX as price falls)")
    print("   → a SINGLE-SIDED position in tokenX must sit ABOVE the active bin")

    # 3 ── find the pair(s)
    print("\n3 ── THE WAVAX/USDC PAIR(S) IN THE V2.2 FACTORY")
    try:
        n = f.functions.getNumberOfLBPairs(WAVAX, USDC).call()
        print(f"   getNumberOfLBPairs(WAVAX, USDC) = {n}")
    except Exception as e:
        print(f"   getNumberOfLBPairs failed: {type(e).__name__}: {str(e)[:160]}")
        n = 0
    pairs = []
    try:
        allp = f.functions.getAllLBPairs(WAVAX, USDC).call()
        for p in allp:
            pairs.append((p[0], p[1], p[2], p[3]))
            print(f"   binStep {p[0]:>6}  pair {p[1]}  ownerMade={p[2]}  ignored={p[3]}")
    except Exception as e:
        print(f"   getAllLBPairs failed: {type(e).__name__}: {str(e)[:160]}")

    if not pairs:
        print("\n   ❌ no WAVAX/USDC LBPair found in the V2.2 factory — stopping here rather than")
        print("      rehearsing against a pool that is not there.")
        return 1

    # 4 ── read each pair's live state
    # FOUR pairs exist for the same token pair at different bin steps, and only ONE of them carries
    # liquidity. The others still answer getActiveId/getPriceFromId, so they return a CONFIDENT and
    # WRONG price ($10.15 / $29.12 / $34.85 against a real market near $7.98). Nothing about them
    # looks broken. Selecting by "first result" would silently price us 27%-337% off market.
    # So: pick by HIGHEST LIQUIDITY — the same rule that stops the remnant-NFT bug on the CL side.
    print("\n4 ── LIVE PAIR STATE (what a deposit would actually meet)")
    rows = []
    for bin_step, addr, _own, _ign in pairs:
        try:
            p = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=PAIR_ABI)
            aid = p.functions.getActiveId().call()
            bs = p.functions.getBinStep().call()
            tx_ = p.functions.getTokenX().call()
            ty_ = p.functions.getTokenY().call()
            rx, ry = p.functions.getReserves().call()
            dx = w3.eth.contract(address=tx_, abi=ERC20_ABI).functions.decimals().call()
            dy = w3.eth.contract(address=ty_, abi=ERC20_ABI).functions.decimals().call()
            # CHAIN TRUTH FIRST. getPriceFromId is the pair's own answer; our arithmetic is only a
            # cross-check. If they disagree, the disagreement is the finding — not something to
            # silently paper over with whichever number looks nicer.
            try:
                raw = p.functions.getPriceFromId(aid).call()
                px_chain = raw / Q128 * (10 ** dx) / (10 ** dy)
            except Exception as e:
                px_chain = None
                print(f"     getPriceFromId failed: {type(e).__name__}: {str(e)[:110]}")
            px = price_from_id(aid, bs, dx, dy)
            if px_chain is not None:
                drift = abs(px - px_chain) / px_chain * 100 if px_chain else 0
                agree = "✅ agree" if drift < 0.5 else f"❌ DISAGREE by {drift:.2f}%"
            else:
                agree = "(chain read unavailable — using our arithmetic)"
            rows.append(dict(bin_step=bs, addr=addr, active_id=aid, rx=rx, ry=ry,
                             px=(px_chain if px_chain is not None else px),
                             px_local=px, px_chain=px_chain, dx=dx, dy=dy, tx=tx_, ty=ty_))
            print(f"\n   pair {addr}   (binStep {bs})")
            print(f"     activeId   = {aid}   (offset from 2^23: {aid - (1 << 23):+,})")
            print(f"     tokenX     = {tx_}  ({'WAVAX' if tx_ == WAVAX else 'USDC'}, {dx} dec)")
            print(f"     tokenY     = {ty_}  ({'WAVAX' if ty_ == WAVAX else 'USDC'}, {dy} dec)")
            print(f"     reserves   = {rx / 10**dx:,.4f} X   /   {ry / 10**dy:,.4f} Y")
            if px_chain is not None:
                print(f"     price      = {px_chain:,.4f} {('USDC per WAVAX' if tx_ == WAVAX else 'WAVAX per USDC')}"
                      f"   [chain]")
                print(f"     our math   = {px:,.4f}   → {agree}")
        except Exception as e:
            print(f"   pair {addr}: read failed {type(e).__name__}: {str(e)[:140]}")

    # 4b ── pick the REAL pool by liquidity, and say out loud what the others are
    print("\n4b ── WHICH PAIR IS REAL")
    for row in rows:
        tvl_usd = row["rx"] / 10**row["dx"] * row["px"] + row["ry"] / 10**row["dy"]
        row["tvl_usd"] = tvl_usd
        ok = "  ✅ REAL" if tvl_usd > 1000 else "  ⚠️  EMPTY/DECOY — returns a confident WRONG price"
        print(f"   binStep {row['bin_step']:>3}  {row['addr']}  ≈ ${tvl_usd:,.0f}{ok}")
    if rows:
        real = max(rows, key=lambda r: r["tvl_usd"])
        empties = [r for r in rows if r is not real]
        print(f"\n   → the pool to use is binStep {real['bin_step']} at {real['addr']}")
        if empties:
            print(f"   → {len(empties)} other pair(s) exist for the SAME token pair with no liquidity.")
            print("     They answer every call normally and quote prices"
                  f" {min(e['px'] for e in empties):.2f}–{max(e['px'] for e in empties):.2f}")
            print(f"     against a real market of {real['px']:.2f}. Nothing about them looks broken.")
            print("     SELECT BY HIGHEST LIQUIDITY, never by first result.")

    # 5 ── the single-side test: where would OUR USDC go, and does it sit below spot
    print("\n5 ── SINGLE-SIDED USDC PLACEMENT TEST")
    for row in rows:
        bs, aid = row["bin_step"], row["active_id"]
        p = w3.eth.contract(address=Web3.to_checksum_address(row["addr"]), abi=PAIR_ABI)
        usdc_is_y = row["ty"] == USDC
        print(f"\n   binStep {bs}: USDC is token{'Y' if usdc_is_y else 'X'}")
        if usdc_is_y:
            print("     → place BELOW the active bin: deltaIds NEGATIVE, distributionX = [0], distributionY = weights")
            print("     → behaviour: as price falls into our bins we BUY WAVAX; we earn fees on the crossing swaps")
        else:
            print("     → place ABOVE the active bin: deltaIds POSITIVE, distributionX = weights, distributionY = [0]")
        for d in (1, 5, 10, 25, 50):
            lo = aid - d
            try:
                px_lo = p.functions.getPriceFromId(lo).call() / Q128 * (10 ** row["dx"]) / (10 ** row["dy"])
            except Exception:
                px_lo = price_from_id(lo, bs, row["dx"], row["dy"])
            drop = (px_lo / row["px"] - 1) * 100 if row["px"] else 0
            print(f"       -{d:>3} bins → id {lo:>6}  price {px_lo:>10,.4f}  ({drop:+.2f}% vs spot)")

    # 6 ── the fee law: is it fixed (Black Hole) or dynamic (surge)?
    # The getters that revert on V2.2 are getFeeParameters()/getBaseFee(); the ones that ANSWER are
    # getStaticFeeParameters() and getVariableFeeParameters(). Decode by hand — a decode failure is
    # not a missing function, and a reverted call is not a zero.
    print("\n6 ── FEE LAW — this is where LB differs from Black Hole CL")
    for row in rows:
        p = w3.eth.contract(address=Web3.to_checksum_address(row["addr"]), abi=PAIR_ABI)
        bs = row["bin_step"]
        try:
            raw = w3.provider.make_request(
                "eth_call", [{"to": row["addr"], "data": STATIC_FEE_SEL}, "latest"])
            if raw.get("error"):
                print(f"   binStep {bs}: getStaticFeeParameters reverted")
                continue
            res = raw["result"][2:]
            if len(res) < 224:
                print(f"   binStep {bs}: unexpected return length {len(res)//2}B")
                continue
            w = [int(res[i * 64:(i + 1) * 64], 16) for i in range(7)]
            base_factor, filt, decay, red, var_ctl, proto_share, max_vol = w

            vraw = w3.provider.make_request(
                "eth_call", [{"to": row["addr"], "data": VAR_FEE_SEL}, "latest"])
            vol_acc = vol_ref = None
            if not vraw.get("error") and len(vraw["result"]) >= 130:
                v = [int(vraw["result"][2:][i * 64:(i + 1) * 64], 16) for i in range(4)]
                vol_acc, vol_ref = v[0], v[1]

            # LB fee law, both terms in 1e18 units:
            #   baseFee     = baseFactor x binStep x 1e10
            #   variableFee = (volatilityAccumulator x binStep)^2 x variableFeeControl / 100
            base_fee = base_factor * bs * 10**10
            var_fee = ((vol_acc * bs) ** 2 * var_ctl) // 100 if vol_acc is not None else 0
            total = base_fee + var_fee
            max_var = ((max_vol * bs) ** 2 * var_ctl) // 100
            print(f"   binStep {bs}  ({row['addr']})")
            print(f"     baseFactor={base_factor}  filterPeriod={filt}  decayPeriod={decay}  "
                  f"reductionFactor={red}")
            print(f"     variableFeeControl={var_ctl}  protocolShare={proto_share} "
                  f"(={proto_share/100:.2f}% to protocol)  maxVolatilityAccumulator={max_vol:,}")
            print(f"     volatilityAccumulator NOW = {vol_acc:,}  (reference {vol_ref:,})")
            print(f"     base fee     = {base_fee/1e18*100:.4f}%")
            print(f"     variable fee = {var_fee/1e18*100:.4f}%   ← the SURGE term")
            print(f"     TOTAL TAKE   = {total/1e18*100:.4f}%   ← what a swap pays right now")
            print(f"     at MAX volatility the take would be "
                  f"{(base_fee+max_var)/1e18*100:.4f}%  "
                  f"({(base_fee+max_var)/total:.1f}x today)")
            print(f"     LP keeps {100 - proto_share/100:.2f}% of that")
        except Exception as e:
            print(f"   binStep {bs}: fee read failed {type(e).__name__}: {str(e)[:140]}")

    # 7 ── our wallet, read-only
    print("\n7 ── OUR WALLET (read-only)")
    print(f"   {WALLET}")
    try:
        usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
        wavax = w3.eth.contract(address=WAVAX, abi=ERC20_ABI)
        print(f"   USDC  balance : {usdc.functions.balanceOf(WALLET).call() / 1e6:,.6f}")
        print(f"   WAVAX balance : {wavax.functions.balanceOf(WALLET).call() / 1e18:,.9f}")
        print(f"   AVAX  balance : {w3.eth.get_balance(WALLET) / 1e18:,.9f}")
        print(f"   USDC allowance to Router V2.2: {usdc.functions.allowance(WALLET, ROUTER).call() / 1e6:,.6f}"
              f"   ← must be raised before a deposit; NOT done here")
    except Exception as e:
        print(f"   wallet read failed: {type(e).__name__}: {str(e)[:160]}")

    print("\n" + "=" * 100)
    print("  REHEARSAL COMPLETE — reads only. No approval, no deposit, no transaction of any kind.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main())
