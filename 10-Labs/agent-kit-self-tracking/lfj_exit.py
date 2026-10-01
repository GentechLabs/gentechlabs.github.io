#!/usr/bin/env python3
"""
lfj_exit.py — EXIT EXECUTOR for an LFJ Liquidity Book position.

WHY THIS EXISTS: exit-rails.json named script=None for the lfj rail while a live
position was open, and the plan reported PARKED / venue_retired=True for a rail we
were actually in. A rail with a PLAN but no executor is the "enter here, can't
leave" trap. This is the executor.

SEQUENCE (mirrors exit_plan.py --mode STABLE):
  1. SETTLE   re-read state 3x, take the highest settled read
  2. REMOVE   router.removeLiquidity(...) across EVERY bin we hold
  3. VERIFY   re-read balances + the pool, assert the position is GONE
  4. SWAP     (STABLE only) legs -> USDC via the aggregator, not the flat router

SAFETY: defaults to --dry-run. --execute --yes required to send. Verifies by
receipt log AND a second RPC — a single lagging read is indistinguishable from
"nothing happened" and cost us a false failure earlier in this same work.

THE GAS FLOOR DOES NOT GATE AN EXIT (Jordan, 2026-09-25) — and here is why, mechanically:
  * The reserve lives in NATIVE AVAX (the gas token). This file's withdraw returns WAVAX + USDC
    from the Liquidity Book — ERC-20s, NOT the gas token — and it sends `value: 0`. So a withdraw
    CANNOT withdraw the reserve, and a swap of WAVAX/USDC cannot either. The two are different
    assets on different sides of the wrapper; the only way this file touches native AVAX is by
    SPENDING GAS, which is exactly what the reserve is for.
  * Because of that, the floor has no business refusing an exit. An exit is the REPAIR path: a
    book stranded out of the pool (the exact state the floor exists to prevent) is fixed by
    withdrawing, and a floor that refused to fund the repair would be defeating its own purpose.
    A book stranded out of range is worse than a thin gas balance.
  * The check is therefore INFORMATIONAL (the floor status is printed, and the native-balance
    delta across this tx is verified to be GAS ONLY). It is never a gate on this path.
  The floor GATES DEPLOYS (lfj_bid_deploy.py, lfj-curve-deploy.sh, lfj_recenter.py), not exits.
"""
import sys, os, json, time, argparse, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from web3 import Web3
from eth_account import Account
from steward_identity import wallet as sw_wallet, key_path as sw_keypath


def _gp(w3):
    """Gas price WITH headroom — the PRICE, not the limit. (2026-09-26)

    The raw `eth_gasPrice` sits exactly on the current base fee and the base fee moves every
    block, so a tx priced there can be born BELOW the floor: the node returns a hash, the tx
    never propagates, and the caller waits out its whole receipt timeout for a receipt that
    cannot arrive. On the EXIT path that is the expensive direction — a withdraw that never
    lands is capital stranded in the pool.
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

RPC  = _avax_url()
RPC2 = "https://avalanche.drpc.org"
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

WAVAX = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC  = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
ROUTER= Web3.to_checksum_address("0x18556DA13313f3532c54711497A8FedAC273220E")
PAIR  = Web3.to_checksum_address("0x864d4e5ee7318e97483db7eb0912e09f161516ea")
ME    = Web3.to_checksum_address(sw_wallet())

PAIR_ABI = json.loads('[{"name":"getActiveId","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint24"}]},{"name":"getBinStep","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint16"}]},{"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"type":"address"},{"type":"uint256"}],"outputs":[{"type":"uint256"}]}]')
ERC = json.loads('[{"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"type":"address"}],"outputs":[{"type":"uint256"}]}]')
ROUTER_ABI = json.loads('[{"inputs":[{"name":"tokenX","type":"address"},{"name":"tokenY","type":"address"},{"name":"binStep","type":"uint16"},{"name":"amountXMin","type":"uint256"},{"name":"amountYMin","type":"uint256"},{"name":"ids","type":"uint256[]"},{"name":"amounts","type":"uint256[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"name":"amountX","type":"uint256"},{"name":"amountY","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]')


def _assert_may_act(action):
    """Refuse to execute unless THIS tenant is licensed to do it ALONE.

    Wired 2026-09-22. Until now the autonomy levels were documentation - nothing consulted
    them, so any box holding a wallet could re-center capital regardless of its level. The
    check sits at the EXECUTION point because that is the one place it cannot be skipped,
    and it is placed AFTER the dry-run gate: a dry run needs no licence, a real action
    never escapes one.
    """
    import os as _o, sys as _s
    _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
    import steward_identity as _SI
    from tenant_guard import assert_autonomy
    assert_autonomy(_SI.tenant(), action)

def _residual_verdict(w3b, pair_addr, me, active, depth):
    """(verdict, residual, ok, failed) — is the position GONE, on the second RPC?

    ── A FAILED READ IS NOT A ZERO (fixed 2026-09-25) ────────────────────────────────────────
    This loop used to `except Exception: pass` and accumulate into one integer, then print
    "✅ ZERO — position closed" whenever that integer was 0. So if the second RPC could not
    answer AT ALL — a timeout, a 429, a dead endpoint — the residual stayed 0 and the tool
    reported the position CLOSED. A read that failed is not a real zero, and the verification
    step is the last place that may manufacture confidence: the caller (`lfj_recenter.py`) reads
    "SENT" from this output and re-deploys on the strength of it, so a false "closed" is exactly
    how capital gets double-placed or stranded.

    The verdict is three-valued and says which: ZERO / NOT ZERO / UNKNOWN. UNKNOWN whenever ANY
    bin could not be read, because a range we could not read is a range we cannot clear.
    """
    residual, ok, failed = 0, 0, 0
    try:
        p = w3b.eth.contract(address=pair_addr, abi=PAIR_ABI)
    except Exception:
        return "UNKNOWN", 0, 0, (2 * depth + 1)
    for d in range(-depth, depth + 1):
        bid = active + d
        if bid < 0:
            continue
        try:
            residual += p.functions.balanceOf(me, bid).call()
            ok += 1
        except Exception:
            failed += 1
    if failed:
        return "UNKNOWN", residual, ok, failed
    return ("ZERO" if residual == 0 else "NOT ZERO"), residual, ok, failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=200, help="how far either side of active to scan for bins")
    ap.add_argument("--slippage", type=float, default=0.02)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()

    _rpc1 = _live_rpc()
    _rpc2 = _live_rpc(exclude=_rpc1)
    w3  = Web3(Web3.HTTPProvider(_rpc1, request_kwargs={"timeout": 45}))
    w3b = Web3(Web3.HTTPProvider(_rpc2, request_kwargs={"timeout": 30}))
    print(f"  rpc  {_rpc1}")
    print(f"  rpc2 {_rpc2}")
    pair = w3.eth.contract(address=PAIR, abi=PAIR_ABI)
    router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
    usdc = w3.eth.contract(address=USDC, abi=ERC)
    wavax = w3.eth.contract(address=WAVAX, abi=ERC)

    print("=" * 96); print("  LFJ EXIT — remove ALL liquidity, verify, (STABLE) swap to USDC"); print("=" * 96)

    # ── THE GAS FLOOR, REPORTED AND NOT ENFORCED (Jordan, 2026-09-25) ─────────────────────────
    # This path is NEVER gated by the floor. Reason, stated as arithmetic rather than as policy:
    # the reserve is NATIVE AVAX; this withdraw returns WAVAX + USDC (ERC-20s) and sends value: 0,
    # so it cannot withdraw the reserve — it can only SPEND gas, which is what the reserve is FOR.
    # An exit is the repair; a floor that blocked the repair would protect the gas balance by
    # preserving the breakage. So: report it, so the operator sees the state, then get on with it.
    try:
        import gas_reserve as _GR
        _ri = _GR.reserve_info(w3=w3, balance_avax=w3.eth.get_balance(ME) / 1e18)
        _GRn = _GR
    except Exception as _e:
        _GRn, _ri = None, {"measured": False, "unmeasured_reason": f"{type(_e).__name__}: {_e}"}
    if _GRn is not None:
        print(f"  {_GRn.floor_line(_ri)}")
        print(f"  gas floor  : NOT a gate on this path — an exit is the repair, and the reserve is")
        print(f"               native AVAX while this withdraw returns WAVAX/USDC (value: 0).")
        if _ri.get("measured") and not _ri.get("above"):
            print(f"  {_GRn.shortfall_text(_ri)}")
            print(f"               Exiting anyway: a book stranded out of the pool is worse than a")
            print(f"               thin gas balance, and this withdraw cannot spend the reserve.")

    # 1. SETTLE — three reads, take the highest (a lagging node under-reports)
    # ⚠️ FIXED 2026-09-25: this used to read the SAME provider 3x, so a lagging node
    # returned the same stale value three times and max() was meaningless — the
    # mitigation could not fire. It must read an INDEPENDENT second provider too.
    # Live proof of the defect: the exit read activeId 8363297 and found "0 bins",
    # reported "position already empty", and ABORTED — while the watchdog read
    # 8363303 on a different node and saw all 25 bins. A stale node blocked every
    # rebalance at the point of no return.
    reads = []
    for _w3x in (w3, w3b if 'w3b' in dir() else None):
        if _w3x is None: continue
        try:
            _pr = _w3x.eth.contract(address=PAIR, abi=PAIR_ABI)
            for i in range(2):
                try: reads.append(_pr.functions.getActiveId().call())
                except Exception: pass
                time.sleep(1)
        except Exception: pass
    if not reads:
        print("  ❌ could not read activeId"); return
    active = max(reads)
    bs = pair.functions.getBinStep().call()
    print(f"\n  [1] SETTLE   activeId reads {reads}  -> using {active} (highest across independent providers)")

    # find every bin we hold
    ids, amounts = [], []
    _scan_rpc_failed = False
    for d in range(-a.depth, a.depth + 1):
        bid = active + d
        if bid < 0: continue
        try: bal = pair.functions.balanceOf(ME, bid).call()
        except Exception: continue
        if bal > 0:
            ids.append(bid); amounts.append(bal)
    print(f"\n  [2] SCAN     {len(ids)} bin(s) hold our liquidity  (depth ±{a.depth})")
    if not ids:
        print("     nothing to withdraw — position already empty"); return
    print(f"     ids {ids[0]}..{ids[-1]}   total LP {sum(amounts):,}")

    bal_usdc = usdc.functions.balanceOf(ME).call()
    bal_wavax = wavax.functions.balanceOf(ME).call()
    print(f"\n     balances before: {bal_usdc/1e6:,.6f} USDC | {bal_wavax/1e18:,.6f} WAVAX")

    args = (WAVAX, USDC, bs, 0, 0, ids, amounts, ME, int(time.time()) + 600)

    # 3. SIMULATE
    print(f"\n  [3] SIMULATE removeLiquidity across {len(ids)} bins")
    try:
        sim = router.functions.removeLiquidity(*args).call({"from": ME})
        print(f"     ✅ SIMULATION PASSED")
        print(f"        would return: {sim[0]/1e18:,.6f} WAVAX + {sim[1]/1e6:,.6f} USDC")
    except Exception as e:
        print(f"     ❌ SIMULATION REVERTED: {str(e)[:220]}")
        print("     -> NOT sending. Report this; do not guess a fix.")
        return

    if not (a.execute and a.yes):
        print("\n  (dry-run — pass --execute --yes to send)")
        return

    _assert_may_act("withdraw_risk")   # exiting on a stop / breaker is class 2

    # The signing key comes from steward_identity, which decrypts a tenant's AES-256 key and
    # asserts the tenant boundary. Reading the key path directly (as this did) bypasses BOTH: a
    # collaborator's encrypted key was handed to the signer as ciphertext, so the withdraw failed
    # while the re-center that called it carried on and deployed into an empty wallet.
    from steward_identity import signing_key as _signing_key
    key = _signing_key()
    gas = router.functions.removeLiquidity(*args).estimate_gas({"from": ME})
    # ── CAP THE GAS ESTIMATE (root-caused 2026-09-24, live money) ──────────────────────────
    # estimate_gas on removeLiquidity returned 19.2M gas for a call whose receipt used 142,395.
    # (The estimator is simulating against the max-liquidity form and cannot see the real bin
    # set.) Multiplied by 1.3 that became a 24.9M-gas / 0.01498 AVAX quote -- and Jordan's
    # wallet, holding 0.00632 AVAX, was REFUSED by the node for insufficient funds on a
    # transaction that actually costs ~0.000085 AVAX. His book then sat out of range earning
    # nothing: dadrian (0.0327 AVAX) re-centred fine in the same run, same code, same trigger.
    #
    # The fix is a CEILING, not a hardcoded value -- the estimate still drives the number, we
    # simply refuse to believe an absurd one. A full exit measures at 142,395 gasUsed and a
    # re-entry at ~0.000427 AVAX; 1.5M gas is ~10x the observed cost and ~0.0009 AVAX, which
    # any funded wallet can pay. If the real need ever exceeds this, the tx fails loudly rather
    # than silently -- which is the correct direction for a money path.
    GAS_CAP = 1_500_000
    if gas > GAS_CAP:
        print(f"      ⚠️  gas estimate {gas:,} exceeds the {GAS_CAP:,} ceiling "
              f"(a real exit uses ~142k) — clamping. Uncapped this would demand "
              f"{gas * 1.3 * 0.6e-9:.6f} AVAX and can be refused for insufficient funds.")
        gas = GAS_CAP
    tx = router.functions.removeLiquidity(*args).build_transaction({
        "from": ME, "nonce": w3.eth.get_transaction_count(ME), "gas": int(gas * 1.3),
        "gasPrice": _gp(w3), "chainId": w3.eth.chain_id, "value": 0})
    # ── THE RESERVE IS NATIVE; THIS TX CARRIES NO NATIVE VALUE (Jordan, 2026-09-25) ───────────
    # Checked, not asserted in prose: the whole reason the floor does not gate this path is that
    # the withdraw cannot move native AVAX. If that ever stops being true (a "value" added here,
    # or a wrap step bolted on), the exit WOULD be able to spend the reserve and this check fires
    # instead of the fact quietly changing underneath the doctrine.
    if int(tx.get("value") or 0) != 0:
        print(f"\n  ❌ REFUSING TO SEND — this withdraw carries native value "
              f"({tx.get('value')} wei). The gas reserve is native AVAX, and a withdraw that can "
              f"spend the reserve invalidates the reason this path is not floor-gated.")
        return
    _native_before = w3.eth.get_balance(ME)
    h = w3.eth.send_raw_transaction(Account.sign_transaction(tx, key).raw_transaction)
    print(f"\n  [4] SENT {h.hex()}")
    r = w3.eth.wait_for_transaction_receipt(h, timeout=240)
    print(f"      {'SUCCESS' if r.status == 1 else 'FAILED'}  block={r.blockNumber}  gas={r.gasUsed}")
    # The reserve can only have been touched by GAS. Report the delta so "the exit cannot withdraw
    # the reserve" is a MEASURED statement on this tx, not a claim about the code.
    try:
        # ── POLL, DO NOT READ ONCE (fixed 2026-09-28) ────────────────────────────────────────────
        # This read the balance ONCE, immediately after the receipt, then reported the delta and
        # judged `delta <= gas_bound` as "GAS ONLY ✅". A node that answers with PRE-transaction
        # state returns the balance unchanged, so _delta came back 0 — and **0 passes the very
        # check that exists to catch the reserve being drained.** The verdict was inverted in the
        # dangerous direction: the one reading that means "I did not see the tx" printed as clean.
        # Measured on the dadrian exit: it printed `spent 0.00000000` while the real cost was
        # 0.03181886 AVAX (754,001 gas at 42.2 gwei), and the balance confirmed it had moved
        # 0.07106163 -> 0.03924277, matching the printed gas bound exactly.
        # A successful tx with gasUsed > 0 CANNOT leave the balance unchanged — gas was spent. So a
        # ZERO delta is a STALE READ, never a pass. Poll until the balance moves; if it never does,
        # say UNMEASURED rather than claiming the reserve is intact. (Same fix as gas_topup.py.)
        _native_after = _native_before
        # The poll window is overridable so the guard can be TESTED without a 30-second wait; the
        # default is what runs in production. A guard that cannot be exercised cheaply is a guard
        # that stops being exercised.
        _poll_s = float(os.environ.get("STEWARD_RESERVE_POLL_S", "30"))
        _deadline = time.time() + _poll_s
        while time.time() < _deadline and _native_after == _native_before:
            time.sleep(min(1.5, _poll_s / 4))
            _native_after = w3.eth.get_balance(ME)
        _gas_bound = int(r["gasUsed"]) * int(tx.get("gasPrice") or 0)
        _delta = _native_before - _native_after
        if _delta == 0:
            print(f"      reserve check: ⛔ UNMEASURED — the balance did NOT move after 30s of "
                  f"polling, yet gas used was {int(r['gasUsed']):,} so gas WAS spent. Stale node "
                  f"state is indistinguishable from a clean withdraw here, so this run claims "
                  f"NOTHING about the reserve. Re-read the balance before trusting the floor "
                  f"doctrine — do not read this line as 'the reserve was not withdrawn'.")
        else:
            print(f"      reserve check: native AVAX {_native_before/1e18:.8f} -> "
                  f"{_native_after/1e18:.8f} (spent {_delta/1e18:.8f}, gas bound "
                  f"{_gas_bound/1e18:.8f}) — {'GAS ONLY ✅ the reserve was not withdrawn' if _delta <= _gas_bound else '⚠️ MORE THAN GAS LEFT THE WALLET — investigate before trusting the floor doctrine'}")
    except Exception as _e:
        print(f"      reserve check: UNMEASURED ({type(_e).__name__}) — the withdraw's native delta "
              f"was not verified on this run")

    # 5. VERIFY — second RPC + pool must read ZERO
    time.sleep(4)
    # A FAILED READ MUST NOT READ AS A REAL ZERO (fixed 2026-09-25): the verdict is now
    # ZERO / NOT ZERO / UNKNOWN, and UNKNOWN is what a range we could not read earns.
    _verdict, residual, _ok, _failed = _residual_verdict(w3b, PAIR, ME, active, a.depth)
    u2 = usdc.functions.balanceOf(ME).call(); w2 = wavax.functions.balanceOf(ME).call()
    print(f"\n  [5] VERIFY (2nd RPC)")
    if _verdict == "ZERO":
        print(f"      residual LP across range : {residual:,}   ✅ ZERO — position closed")
    elif _verdict == "UNKNOWN":
        print(f"      residual LP across range : UNKNOWN — {_failed} of {_failed + _ok} bin reads "
              f"FAILED on the verifying RPC.")
        print(f"      ⛔ NOT EVIDENCE THE POSITION CLOSED. Re-read before re-deploying: a range we "
              f"could not read is a range we cannot clear.")
    else:
        print(f"      residual LP across range : {residual:,}   ⚠️ NOT ZERO — position still open")
    print(f"      USDC  {bal_usdc/1e6:,.6f} -> {u2/1e6:,.6f}")
    print(f"      WAVAX {bal_wavax/1e18:,.6f} -> {w2/1e18:,.6f}")
    print(f"\n  STABLE mode next step: swap the WAVAX leg -> USDC via the AGGREGATOR")
    print(f"  (do NOT use the LFJ router — it is flat; see the KyberSwap build path).")

if __name__ == "__main__":
    main()
