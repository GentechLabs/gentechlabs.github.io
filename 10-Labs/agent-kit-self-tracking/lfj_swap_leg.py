#!/usr/bin/env python3
"""
lfj_swap_leg.py — the LFJ Liquidity Book swap executor, BOTH directions.

Why this exists: find_real_swapper.py / prove_swap_route.py / rebalance_swap.py are
all DIAGNOSTIC — they prove a route exists but have no execute path. This is the
executor they are missing.

WHY IT NOW DOES BOTH DIRECTIONS (2026-09-22)
--------------------------------------------
It only ever did USDC -> WAVAX, which was fine while the book was being built out of
stablecoins. A CURVE needs both legs funded: USDC for the bid (below spot) and WAVAX
for the ask (above spot). When the book is 98% WAVAX and we want a curve, the swap we
need is WAVAX -> USDC — the direction this file could not do. So the direction is now
a parameter rather than an assumption baked into the path.

SAFETY: simulates every call with eth_call before sending. --execute --yes required.
Selectors are COMPUTED with Web3.keccak, never guessed (a guessed selector reverts
exactly like a missing function — that trap costs a false conclusion every time).
"""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
from steward_identity import wallet as sw_wallet, key_path as sw_keypath


def _gp(w3):
    """Gas price WITH headroom — the PRICE, not the limit. (2026-09-26)

    The raw `eth_gasPrice` sits exactly on the current base fee and the base fee moves every
    block, so a tx priced there can be born BELOW the floor: the node returns a hash, the tx
    never propagates, and the caller waits out its whole receipt timeout for a receipt that
    cannot arrive. The ratio-swap leg is on the re-center's critical path, so a swap that
    silently never lands strands the whole re-center.
    """
    try:
        import gas_reserve as _G
        return _G.gas_price_wei(w3)
    except Exception:                       # fallback is still strictly better than raw
        return int(w3.eth.gas_price * 1.3)

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
#
# ORDERING MATTERS: this is defined ABOVE its first use. It used to be defined at the BOTTOM of
# the file while being CALLED at module scope near the top, so the module raised
# `NameError: name '_avax_url' is not defined` on import — the tool could not run at all.
# py_compile passes on that (it checks syntax, not name resolution), which is exactly why it
# survived an "all files compile" sweep.
#
# The fallback is a LITERAL, not a self-call. It previously read `return _avax_url()`, i.e. it
# recursed into itself, so the "last resort" path was infinite recursion, not a URL.
_AVAX_URL_LAST_RESORT = "https://api.avax.network/ext/bc/C/rpc"


def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        return _AVAX_URL_LAST_RESORT


RPC       = _avax_url()
# RPC failover (2026-09-22). A fixed primary endpoint began returning 429 and these tools
# died on it — an exit could not read activeId and a send could not read a balance. A
# rate-limited endpoint must never be able to read as an unreachable chain or block a
# withdrawal. Probe the pool, take the first that actually answers. The "second RPC" used
# for verification is deliberately a DIFFERENT host — a second read from the same endpoint
# proves nothing.
RPC_CANDIDATES = [
    "https://avalanche-c-chain-rpc.publicnode.com",
    "https://avalanche.drpc.org",
    "https://rpc.ankr.com/avalanche",
    _avax_url(),
]


def _live_rpc(exclude=None):
    """First candidate that answers eth_blockNumber. Never returns `exclude`."""
    for _u in RPC_CANDIDATES:
        if exclude and _u == exclude:
            continue
        try:
            if Web3(Web3.HTTPProvider(_u, request_kwargs={"timeout": 20})).eth.block_number:
                return _u
        except Exception:
            continue
    return RPC_CANDIDATES[0]

WAVAX     = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC      = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
ROUTER    = Web3.to_checksum_address("0x18556DA13313f3532c54711497A8FedAC273220E")  # LFJ LBRouter
PAIR      = Web3.to_checksum_address("0x864d4e5ee7318e97483db7eb0912e09f161516ea")  # WAVAX/USDC LB
ME        = Web3.to_checksum_address(sw_wallet())
GAS_MULT  = 1.25
SLIPPAGE  = 0.015          # 1.5%

DEC = {"usdc": 6, "wavax": 18}
TOKEN = {"usdc": USDC, "wavax": WAVAX}

w3 = Web3(Web3.HTTPProvider(_live_rpc(), request_kwargs={"timeout": 30}))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)   # Avalanche is POA


def sel(sig):  return "0x" + Web3.keccak(text=sig)[:4].hex()


def eth_call(to, data):
    return w3.eth.call({"to": to, "data": data})


ERC20 = json.loads('[{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"s","type":"address"},{"name":"a","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"}]')


import steward_identity as _SI

def _decode_revert(msg):
    """Human reason from a web3 revert, or a selector. Do the ABI layout CORRECTLY.

    Error(string) is selector + offset(0x20) + length + bytes. Reading the FIRST word as the
    length (as an earlier attempt did) yields a 32-byte string of nulls and makes a perfectly
    clear message look like an undecodable blob. Decoding is not guessing.
    """
    i = msg.find("0x08c379a0")
    if i < 0:
        j = msg.find("0x")
        return msg[j:j + 10] if j >= 0 else "no revert data"
    body = msg[i + 10:]
    if len(body) < 128:
        return "truncated Error(string)"
    try:
        offset = int(body[0:64], 16)
        length = int(body[64:128], 16)
        if offset != 32 or length > 512:
            return f"Error(string) unexpected layout (offset={offset} length={length})"
        return "Error(\"" + bytes.fromhex(body[128:128 + length * 2]).decode("utf-8") + "\")"
    except Exception:
        return "Error(string) undecodable"


def send(fn, label, execute, key):
    """Simulate, then send. Refuses to send if simulation reverts."""
    try:
        gas = fn.estimate_gas({"from": ME})
        print(f"    sim OK  gas={gas}")
    except Exception as e:
        print(f"    ❌ SIMULATION REVERTED — {str(e)[:180]}")
        print(f"    -> not sending. {label} aborted.")
        return None
    if not execute:
        print(f"    (dry-run: would send {label})")
        return None
    tx = fn.build_transaction({
        "from": ME, "nonce": w3.eth.get_transaction_count(ME),
        "gas": int(gas * GAS_MULT), "gasPrice": _gp(w3),
        "chainId": w3.eth.chain_id,
    })
    signed = Account.sign_transaction(tx, key)
    h = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"    sent {h.hex()}")
    r = w3.eth.wait_for_transaction_receipt(h, timeout=180)
    print(f"    status={'SUCCESS' if r.status==1 else 'FAILED'}  block={r.blockNumber}  gasUsed={r.gasUsed}")
    return r if r.status == 1 else None


def _approval_needed(cur, amount_in, sane_max):
    """Re-approve when the standing grant is INSUFFICIENT **or OVERSIZED**.

    ── THE BOUNDED-APPROVAL POSTURE COULD NOT BE IN FORCE HERE (fixed 2026-09-25) ─────────────
    This was `if cur >= amount_in: skip` -- and the FIRST swap this file ever made granted an
    UNLIMITED allowance (`approve(ROUTER, 2**256-1)`, still the amount sent below). An unlimited
    grant is never `< amount_in`, so the approve branch was skipped on every wallet that had one,
    and the over-grant it should have replaced was never even examined. Measured live on both
    tenants 2026-09-25: USDC -> LBRouter allowance 2**256-1 minus prior spend (~1.16e71) and
    WAVAX -> LBRouter exactly 2**256-1. The treasury's stated posture -- "a compromised router can
    only ever reach a small, self-limiting amount" -- was not in force on the swap path, while the
    same fix WAS written into coq_accumulator.py, which is the defect shape that file documents:
    a comparison that can never be true against the value it guards.

    Bound BOTH ends, so the branch fires on the pre-existing over-grant as well as on a shortfall.
    """
    return bool(cur < amount_in or cur > sane_max)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm", choices=["usdc", "wavax"], default="usdc",
                    help="token to SELL (default usdc, the original direction)")
    ap.add_argument("--amount", type=float, default=None,
                    help="human units of the FROM token to sell (default: whole balance)")
    ap.add_argument("--pct", type=float, default=None,
                    help="fraction of the FROM balance to sell, 0-1 (e.g. 0.5)")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--rescue", action="store_true",
                    help="RESCUE ONLY: allow a swap that would reach into the gas reserve. Never "
                         "set automatically.")
    args = ap.parse_args()

    frm, to = args.frm, ("wavax" if args.frm == "usdc" else "usdc")
    fd, td = DEC[frm], DEC[to]
    f_addr, t_addr = TOKEN[frm], TOKEN[to]

    print("=" * 88); print(f"  LFJ SWAP LEG — {frm.upper()} -> {to.upper()}"); print("=" * 88)
    if not w3.is_connected():
        print("  ERROR: RPC unreachable"); sys.exit(1)

    # --- CORRECT SELECTORS, computed not guessed ---
    print("\n  computed selectors (Web3.keccak — not guessed):")
    for s in ["getBinStep()", "getActiveId()", "getReserves()",
              "swapExactTokensForTokens(uint256,uint256,(uint256[],uint8[],address[]),address,uint256)"]:
        print(f"    {s[:58]:<60} {sel(s)}")

    # --- pool facts ---
    print("\n  POOL:")
    bin_step = 10
    for lbl, s in [("binStep", "getBinStep()"), ("activeId", "getActiveId()")]:
        try:
            v = int.from_bytes(eth_call(PAIR, sel(s)), "big")
            print(f"    {lbl:<10} {v}")
            if lbl == "binStep": bin_step = v
        except Exception as e:
            print(f"    {lbl:<10} CALL FAILED: {str(e)[:70]}")

    f_tok = w3.eth.contract(address=f_addr, abi=ERC20)
    t_tok = w3.eth.contract(address=t_addr, abi=ERC20)
    fb = f_tok.functions.balanceOf(ME).call()
    tb = t_tok.functions.balanceOf(ME).call()
    print(f"\n  {frm.upper()} balance : {fb / 10**fd:.6f}")
    print(f"  {to.upper()} balance : {tb / 10**td:.6f}")
    if fb == 0:
        print(f"  nothing to swap"); sys.exit(0)

    if args.amount is not None:
        amount_in = int(args.amount * 10**fd)
    elif args.pct is not None:
        # ── A NEGATIVE PERCENTAGE IS A DIRECTION, NOT A MULTIPLIER (fixed 2026-09-24) ────────
        # The caller passes -0.249 to mean "sell 24.9% of the balance". Multiplying the balance
        # by a negative produced a negative amount, `min(negative, fb)` kept it negative, and the
        # zero-guard below refused. **This emptied a funded book**: lfj_recenter withdrew the whole
        # position, the swap leg computed a negative and exited 2, and the abort-before-redeploy
        # left $121 sitting in the wallet with nothing deployed — silently, for twenty minutes,
        # until Jordan noticed on his phone.
        #
        # The direction is ALREADY carried by --from/--to; the sign on --pct is redundant. Take
        # the magnitude. A money actor must not depend on a caller's sign convention to be safe.
        amount_in = int(fb * abs(args.pct))
    else:
        amount_in = fb
    amount_in = min(amount_in, fb)
    # ── THE RESERVE IS NOT SWAPPABLE CAPITAL EITHER (Jordan, 2026-09-25) ─────────────────────
    # The other leg of the same rule. "Deploy the whole balance" was the visible half; the swap is
    # the quiet half — a rotation that sells the last loose slice of the book for the other side
    # leaves a wallet with nothing it can turn into gas. The floor comes from gas_reserve.py (LIVE
    # gas price, LIVE AVAX price) and is held back IN THE TOKEN BEING SOLD, because that is the
    # asset this call is draining. It is a FLOOR, not a hoard: anything above it still swaps.
    _GR = None
    try:
        import gas_reserve as _GRm
        _GR = _GRm
        _ri = _GR.reserve_info(w3=w3, balance_avax=w3.eth.get_balance(ME) / 1e18)
        _from_usd = 1.0 if frm == "usdc" else float(_ri.get("avax_usd") or 0.0)
        _capped, _kept, _note = _GR.cap_deploy(amount_in, fb, _ri, _from_usd, fd, rescue=args.rescue)
        print(f"  {_GR.floor_line(_ri)}")
        print(f"  reserve      : {_kept / 10**fd:,.6f} {frm.upper()} held back  ({_note})")
        amount_in = _capped
    except Exception as _e:
        print(f"  gas floor    : UNMEASURABLE ({type(_e).__name__}: {_e}) — a reserve that cannot "
              f"be sized cannot be held back, so this swap refuses.")
        if not args.rescue:
            sys.exit(2)
        print(f"  ⚠️  --rescue: the floor does NOT gate this swap — proceeding with nothing held.")
    if amount_in <= 0:
        print("  ❌ computed amount is zero — refusing (the whole balance is inside the gas "
              "reserve; top it up with: python3 gas_reserve.py --plan)"); sys.exit(2)
    print(f"  swapping     : {amount_in / 10**fd:.6f} {frm.upper()}")

    # --- 1. approve the FROM token -> router ---
    print(f"\n  [1] APPROVE {frm.upper()} -> LBRouter")
    cur = f_tok.functions.allowance(ME, ROUTER).call()
    # Route through steward_identity: it asserts the tenant boundary AND decrypts a tenant's
    # AES-256 key. Opening the path here did neither - a collaborator's box crashed on
    # decode, and every box skipped the guard.
    key = _SI.signing_key() if args.execute else None
    # ── BOUND THE APPROVAL, AND CHECK BOTH ENDS OF THE BOUND (fixed 2026-09-25) ───────────────
    # The grant this file hands out was UNLIMITED and the skip test was one-sided
    # (`cur >= amount_in`), so an already-unlimited grant was never revisited (see
    # _approval_needed). We sell exactly `amount_in` here, so a few times that is plenty; a
    # router that turns hostile can only reach the bounded figure.
    SANE_MAX = int(amount_in) * 4 * 8
    if not _approval_needed(cur, amount_in, SANE_MAX):
        print(f"      already approved ({cur / 10**fd:.2f}) — skip")
    else:
        approve_amt = int(amount_in) * 4
        if cur > SANE_MAX:
            _shown = "UNLIMITED" if cur >= 2 ** 256 - 1 else f"{cur / 10**fd:,.2f}"
            print(f"      standing allowance is OVER-GRANTED ({_shown}) — re-approving to the "
                  f"bounded {approve_amt / 10**fd:.6f}")
        send(f_tok.functions.approve(ROUTER, approve_amt), f"approve {frm.upper()}",
             args.execute and args.yes, key)

    # --- 2. swap ---
    print(f"\n  [2] swapExactTokensForTokens  {frm.upper()} -> {to.upper()}  (binStep {bin_step})")
    deadline = int(time.time()) + 600
    router = w3.eth.contract(address=ROUTER, abi=json.loads('[{"inputs":[{"name":"amountIn","type":"uint256"},{"name":"amountOutMin","type":"uint256"},{"components":[{"name":"pairBinSteps","type":"uint256[]"},{"name":"versions","type":"uint8[]"},{"name":"tokenPath","type":"address[]"}],"name":"path","type":"tuple"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"name":"amountOut","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]'))

    # ── THE VERSION BYTE (fixed 2026-09-22) ──────────────────────────────────────────────
    # This file said `versions=[2]   # 2 = LFJ v2.2`. The comment was wrong and the byte was
    # wrong with it. JoeV2's enum is `Version { V1, V2, V2_1, V2_2 }` — ZERO-indexed, so
    # V2_2 = 3. Asking for version 2 against our v2.2 binStep-10 pool reverts with
    # LBRouter__PairNotCreated, which reads EXACTLY like "this pool does not exist" and is
    # how the LFJ router came to be written off as "flat" in favour of an aggregator. It was
    # never flat. We were asking for a pair that does not exist: v2.1 at binStep 10.
    # Probed all combinations: only (version 3, binStep 10) quotes for this pool.
    # So PROBE rather than assert — a hardcoded version is the same trap with a new number.
    out, used, reasons = None, None, {}
    for ver in (3, 2, 1):
        try:
            out = router.functions.swapExactTokensForTokens(
                amount_in, 0, ([bin_step], [ver], [f_addr, t_addr]), ME, deadline).call({"from": ME})
            used = ver
            break
        except Exception as e:
            reason = _decode_revert(str(e))
            reasons[ver] = reason
            print(f"      version {ver} @ binStep {bin_step}: {reason}")
    if out is None:
        # ── DO NOT BLAME THE PATH FOR AN ALLOWANCE PROBLEM (fixed 2026-09-22) ────────────────
        # This printed "no version quotes for this pair — fix the path before retry" for EVERY
        # failure. When the real cause was `ERC20: transfer amount exceeds allowance`, that
        # message sent the reader hunting a routing bug that did not exist — and the LFJ swap
        # route then got written off as "flat" and replaced with an aggregator. A WRONG
        # diagnosis costs more than no diagnosis: it hides the real fault and invents a second
        # one. So name the cause, and only blame the path when the path is actually at fault.
        joined = " ".join(reasons.values()).lower()
        if "allowance" in joined:
            print("      ❌ SWAP REFUSED — the token is NOT APPROVED to the router.")
            print(f"         {frm.upper()} allowance is the blocker, not the swap path.")
            print("         The approve above only broadcasts with --execute, so a dry run can")
            print("         never quote an unapproved token. Re-run with --execute --yes.")
        elif "pairnotcreated" in joined:
            print("      ❌ no pair for this version/binStep — the PATH is genuinely wrong.")
        else:
            print(f"      ❌ no version quotes — cause NOT identified, refusing to send. "
                  f"Reasons: {reasons}")
        sys.exit(1)

    print(f"      version {used} quoted  (V2_2 = 3, zero-indexed enum)")
    print(f"      quote: {amount_in / 10**fd:.6f} {frm.upper()} -> {out / 10**td:.6f} {to.upper()}")
    out_min = int(out * (1 - SLIPPAGE))
    print(f"      min out (1.5% slip): {out_min / 10**td:.6f} {to.upper()}")
    path = ([bin_step], [used], [f_addr, t_addr])

    # Pre-swap balances, captured BEFORE broadcasting so the post-state can state a DELTA.
    f_pre = f_tok.functions.balanceOf(ME).call() / 10**fd
    t_pre = t_tok.functions.balanceOf(ME).call() / 10**td

    if args.execute and args.yes:
        send(router.functions.swapExactTokensForTokens(amount_in, out_min, path, ME, deadline),
             "swap", True, key)
    else:
        print("      (dry-run: pass --execute --yes to send)")

    # ── POST-STATE — read on a DIFFERENT provider, and state the DELTA ────────────────
    # History: this block re-read on the SAME connection that had just broadcast, and on
    # 2026-09-22 it printed the PRE-swap balances immediately after a SUCCESSFUL swap
    # (USDC and WAVAX both "unchanged") — which reads exactly like a failed swap. The swap
    # HAD landed: confirmed on two independent RPCs as USDC -12.000000 / WAVAX +1.087376.
    # A single lagging read is not evidence of anything. So: read a SECOND provider, and
    # report the delta, so "not visible on this node yet" can never be mistaken for
    # "did not happen".
    print("\n  post-state:")
    _alt = None
    try:
        _cur = getattr(getattr(w3, "provider", None), "endpoint_uri", None)
        _alt = _live_rpc(exclude=_cur)
        _w3b = Web3(Web3.HTTPProvider(_alt, request_kwargs={"timeout": 30}))
        _w3b.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        _fb = _w3b.eth.contract(address=f_addr, abi=ERC20)
        _tb = _w3b.eth.contract(address=t_addr, abi=ERC20)
        f_post = _fb.functions.balanceOf(ME).call() / 10**fd
        t_post = _tb.functions.balanceOf(ME).call() / 10**td
        print(f"    (2nd provider: {_alt})")
    except Exception as _e:
        print(f"    ⚠️ 2nd provider unavailable ({type(_e).__name__}) — falling back to the "
              f"primary. Treat an unchanged figure below as UNVERIFIED, NOT as 'did not happen'.")
        f_post = f_tok.functions.balanceOf(ME).call() / 10**fd
        t_post = t_tok.functions.balanceOf(ME).call() / 10**td

    print(f"    {frm.upper()} {f_pre:.6f} -> {f_post:.6f}   (delta {f_post - f_pre:+.6f})")
    print(f"    {to.upper()} {t_pre:.6f} -> {t_post:.6f}   (delta {t_post - t_pre:+.6f})")

    # A successful send with NO movement on the verifying provider is the lagging-read case,
    # not a silent failure. Say so rather than letting the numbers imply a failed swap.
    if args.execute and args.yes and abs(f_post - f_pre) < 1e-9 and abs(t_post - t_pre) < 1e-9:
        print("    ⚠️ NO MOVEMENT on the verifying provider. If the tx above reported SUCCESS,")
        print("       this is a LAGGING NODE, not a failed swap — re-check on a third RPC")
        print("       before concluding anything. Do NOT re-send: that would double the swap.")


if __name__ == "__main__":
    main()
