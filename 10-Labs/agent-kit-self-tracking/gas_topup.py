#!/usr/bin/env python3
"""
gas_topup.py — the executor `gas_reserve.py --plan` never had.

Jordan, 2026-09-27: *"The treasury needs to be able to manage itself."*

WHY THIS FILE EXISTS
--------------------
`gas_reserve.py --plan` has always PRINTED a top-up plan:

    TOP-UP PLAN   sell ~$0.0673 of the book's USDC into AVAX (fee+slippage 0.3%)
                  -> restores 600 cycles

and NOTHING COULD RUN IT. Nothing. On 2026-09-27 that gap stranded jordan's book for
hours: the rescue loop stopped (correctly — it was burning gas it could not afford), the
wallet sat at 0.00298 AVAX, the book sat entirely in the wallet earning nothing, and the
one tool that knew what to do could only describe it. A human had to unwrap WAVAX by hand.

A WAVAX/USDC BOOK CAN ALWAYS PAY FOR ITS OWN GAS — `gas_reserve.py` says so in its own
header ("A book holding WAVAX/AVAX can always pay for its own operations, because the asset
it holds IS the gas asset"). That was a true observation with no implementation behind it.
This is the implementation.

TWO STEPS, IN THIS ORDER, FOR A REASON
--------------------------------------
  1. UNWRAP  WAVAX -> native AVAX      (WAVAX.withdraw, ~36k gas, ONE call)
  2. ONLY IF the wallet holds no WAVAX:  sell USDC -> WAVAX (the proven lfj_swap_leg rail),
     then unwrap.

The unwrap FIRST because it is ~36k gas against a swap's ~160k+: it is the cheapest way to
turn value the book already holds into the gas it needs. The swap is the fallback, not the
default — the original `--plan` text said "sell USDC into AVAX", which needs a swap and a
wrap. Unwrapping gets there in one call from an asset the book already has.

THE BOOTSTRAP FLOOR — an honest limit, stated not hidden
--------------------------------------------------------
An unwrap is a transaction, so it needs a little gas to START. Measured: 35,259 gas.
At 5 nAVAX that is ~0.00018 AVAX. So this tool can rescue a wallet with ~0.0002 AVAX in it
and cannot rescue one with zero. Below BOOTSTRAP_FLOOR_AVAX it REFUSES and says so plainly,
because a silent failure here would look identical to a successful no-op — the false-value
family this codebase keeps re-learning.

THE UNWRAP IS NOT A COST, IT IS A ROTATION
------------------------------------------
WAVAX -> AVAX stays inside the position. It does not sell the asset, does not touch the LP,
and does not change the book's composition beyond the gas it funds. The only real cost is
the gas of the unwrap itself (~$0.002).

DRY-RUN BY DEFAULT. Pass --execute --yes to send. Same house pattern as every other script.

Usage:
    python3 gas_topup.py                  # dry run, report what it would do
    python3 gas_topup.py --execute --yes  # do it
    python3 gas_topup.py --target 3       # top up to N full cycles of runway
    python3 gas_topup.py --json           # machine-readable verdict
"""
import argparse
import json
import os
import sys
import time as _time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from web3 import Web3                                                    # noqa: E402
from eth_account import Account                                          # noqa: E402

import steward_identity as SI                                            # noqa: E402

WAVAX = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")   # NATIVE USDC
ERC20_ABI = [{"constant": True, "inputs": [{"name": "_owner", "type": "address"}],
              "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}],
              "stateMutability": "view", "type": "function"}]
WAVAX_ABI = [{"constant": False, "inputs": [{"name": "wad", "type": "uint256"}],
              "name": "withdraw", "outputs": [],
              "stateMutability": "nonpayable", "type": "function"}]

# Measured live 2026-09-27 on the real WAVAX contract: 35,259 gas.
UNWRAP_GAS = 60_000

# Measured: an unwrap needs ~0.00018 AVAX at 5 nAVAX to start. Below this the wallet cannot
# pay for the transaction that would fund it — reported, never silently skipped.
BOOTSTRAP_FLOOR_AVAX = 0.00025

# Headroom over the computed shortfall: covers the unwrap's own gas and a gas-price move
# between the read and the send. Over-topping is harmless (it just raises the runway);
# under-topping re-triggers the whole problem on the next pass.
HEADROOM = 1.20
MIN_UNWRAP_AVAX = 0.004      # below this a top-up is not worth a transaction's gas
# A swap leg buys AVAX with USDC; below this notional it cannot pay for its own gas either. The
# unwrap leg has always had a floor (MIN_UNWRAP_AVAX) — the swap leg never did, so a remainder of a
# fraction of a cent could still be planned as a real step (fixed 2026-09-28).
MIN_SWAP_USD = 0.05


def _rpc():
    """A connected Web3 — from the SAME helper gas_reserve uses, so this tool and the gate
    never price against two different chains. The hardcoded URL is only a last resort."""
    import gas_reserve as GR
    try:
        _px, w3 = GR.chain()
        if w3 is not None:
            return w3
    except Exception:
        pass
    return Web3(Web3.HTTPProvider("https://avalanche-c-chain-rpc.publicnode.com",
                                  request_kwargs={"timeout": 25}))


def unwrap(w3, me, acct, amount_avax, execute=False, amount_wei=None):
    """WAVAX -> native AVAX. One call. Returns (ok, detail, txhash).

    ── AMOUNT IS TAKEN IN INTEGER WEI WHEN GIVEN, AND IT MUST BE (fixed 2026-09-27) ─────────────
    The first version took a float and did `int(amount * 1e18)`. Unwrapping the FULL balance that
    way reverted with `execution reverted, no data`: the true balance was 0.009079999... WAVAX and
    the float round-trip produced 0.009080000... — a wei or two MORE than the wallet held, so the
    contract correctly refused. A balance is an integer; converting it to a float and back is a
    lossy reformat, and the value it corrupts is the one that must be exact.
    Callers now pass `amount_wei` from the raw `balanceOf` read, and the min() that clamps to the
    balance happens in integer space. The float parameter is kept only for display/tests.
    """
    if amount_wei is None:
        amount_wei = int(amount_avax * 1e18)
    amount_wei = int(amount_wei)
    if amount_wei <= 0:
        return False, "nothing to unwrap (amount is zero)", None
    c = w3.eth.contract(address=WAVAX, abi=WAVAX_ABI)
    tx = c.functions.withdraw(amount_wei).build_transaction({
        "from": me,
        "nonce": w3.eth.get_transaction_count(me),
        "gas": UNWRAP_GAS,
        "gasPrice": w3.eth.gas_price,
        "chainId": 43114,
    })
    est = w3.eth.estimate_gas({k: v for k, v in tx.items() if k != "gas"})
    if est > UNWRAP_GAS:
        return False, f"unwrap would need {est:,} gas > budgeted {UNWRAP_GAS:,}", None
    if not execute:
        return True, f"dry-run: would unwrap {amount_wei / 1e18:.6f} WAVAX (est {est:,} gas)", None
    signed = Account.sign_transaction(tx, acct.key)
    h = w3.eth.send_raw_transaction(signed.raw_transaction)
    rc = w3.eth.wait_for_transaction_receipt(h, timeout=180)
    if rc.status != 1:
        return False, f"unwrap REVERTED in block {rc.blockNumber} (tx 0x{h.hex()})", h.hex()
    return True, (f"unwrapped {amount_wei / 1e18:.6f} WAVAX, {rc.gasUsed:,} gas, "
                  f"block {rc.blockNumber}"), h.hex()


def main():
    ap = argparse.ArgumentParser(description="Fund the treasury's own gas from assets it already holds.")
    ap.add_argument("--tenant", default=None)
    ap.add_argument("--target", type=float, default=None,
                    help="top up to N full cycles of runway (default: restore the floor)")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    import gas_reserve as GR

    tenant = (a.tenant or SI.tenant() or "").strip()
    me = SI.wallet()
    w3 = _rpc()

    info = GR.reserve_info(tenant=tenant, w3=w3)
    if not info.get("measured"):
        print(f"  ⛔ CANNOT SIZE THE TOP-UP — {info.get('unmeasured_reason')}")
        print(f"     A top-up we cannot size is a top-up we cannot prove we can finish.")
        return 1

    balance = float(info["balance_avax"])
    floor = float(info["reserve_avax"])
    cycle_avax = float(info["cycle_avax"])
    gas_price = info["gas_price_wei"]
    avax_usd = float(info["avax_usd"])

    # ── WHAT ARE WE TOPPING UP TO? (fixed 2026-09-27, same day, second pass) ────────────────
    # The first version of this tool targeted the FLOOR, and it announced "✅ ALREADY ABOVE
    # TARGET — nothing to do" on a wallet that could NOT run a full re-center. It was measuring
    # the wrong thing, and a tool that reports success while the action it exists to enable is
    # still blocked is the false-value family this codebase keeps re-learning.
    #
    # THE REASON: two numbers in this codebase describe one wallet.
    #   * the FLOOR sizes a cycle from `cycle_gas_units` (decrease+collect+swap+approve*2+mint
    #     = 1,816,000 gas after the 2026-09-27 mint correction) — the MEASURED cost;
    #   * the DEPLOY GATE charges `RECENTER_GAS` (3,500,000) — deliberately generous, because a
    #     gate that over-charges only refuses early while one that under-charges strands capital.
    # Being above the floor therefore does NOT mean a cycle can run. What a wallet needs in order
    # to ACT is the strictest gate's requirement: the full recenter gas PLUS the floor left
    # intact. That is the number this targets, because "self-managing" means "can perform the
    # repair", not "is above a line that a stricter gate ignores."
    import gas_reserve as _GR
    recenter_avax = (_GR.RECENTER_GAS * gas_price) / 1e18
    # To pass `GR.gate(balance - cost >= reserve)` with the strictest action:
    self_sufficient = recenter_avax + floor

    want = self_sufficient * a.target if a.target else self_sufficient
    want_avax = want
    shortfall_native = max(0.0, want_avax - balance)

    print("=" * 88)
    print(f"  GAS TOP-UP — {tenant}")
    print("=" * 88)
    print(f"  wallet        {me}")
    print(f"  AVAX          {balance:.8f}  (~${balance * avax_usd:.4f})")
    print(f"  floor         {floor:.8f} AVAX   (one measured cycle = {cycle_avax:.8f} AVAX, "
          f"{info['cycle_gas_units']:,} gas)")
    print(f"  a FULL recenter costs {recenter_avax:.8f} AVAX ({_GR.RECENTER_GAS:,} gas, the gate's "
          f"budget)")
    print(f"  self-sufficient = recenter + floor = {self_sufficient:.8f} AVAX"
          + (f"  x{a.target:g}" if a.target else ""))

    if shortfall_native <= 0:
        print(f"  ✅ SELF-SUFFICIENT — a full recenter plus the floor is covered "
              f"({balance:.8f} >= {self_sufficient:.8f}).")
        if a.json:
            print(json.dumps({"tenant": tenant, "action": "none",
                              "balance_avax": balance, "shortfall_avax": 0.0,
                              "self_sufficient_avax": self_sufficient}, indent=2))
        return 0

    # ── WHAT DOES IT ACTUALLY COST TO ACQUIRE THIS AVAX? (fixed 2026-09-27, 5th pass) ────────
    # Previous versions counted only the UNWRAP gas (35,283) and called a 0.002 AVAX shortfall
    # "worth doing". A live run then LOWERED the wallet (0.02454 -> 0.02356), because buying AVAX
    # with a swap needs BOTH legs: the swap (150,833 gas measured live) AND the unwrap (35,283).
    # The swap is 4x the unwrap, and the estimate omitted it entirely — so the tool cheerfully
    # spent 186k gas (~$0.0093) to close a gap that was sometimes smaller than its own cost.
    # Under-counting the dominant cost is the same error as the gas budget that stranded the book.
    # The real cost depends on which path is needed, so it is computed AFTER we know that.
    unwrap_gas_cost = (UNWRAP_GAS * gas_price) / 1e18
    SWAP_GAS_EST = 165_000          # measured live: 150,833-170,089 across three runs
    swap_gas_cost = (SWAP_GAS_EST * gas_price) / 1e18

    # ── CAN THIS WALLET PAY FOR THE TRANSACTION THAT FUNDS IT? ────────────────────────────────
    # The bootstrap is real and cheap but not free: an unwrap is 35,259 gas (~0.00018 AVAX at
    # 5 nAVAX). Below BOOTSTRAP_FLOOR_AVAX the wallet cannot start, and saying so is the whole
    # point — a silent no-op here is indistinguishable from a successful top-up.
    if balance < BOOTSTRAP_FLOOR_AVAX:
        print(f"\n  ⛔ CANNOT BOOTSTRAP — the wallet holds {balance:.8f} AVAX, below the "
              f"{BOOTSTRAP_FLOOR_AVAX:.5f} an unwrap needs to start.")
        print(f"     The unwrap that would fund this wallet is itself a transaction. This needs a")
        print(f"     small outside deposit; no asset in this wallet can be moved without gas.")
        if a.json:
            print(json.dumps({"tenant": tenant, "action": "blocked_bootstrap",
                              "balance_avax": balance,
                              "bootstrap_floor_avax": BOOTSTRAP_FLOOR_AVAX}, indent=2))
        return 3

    wavax_wei = w3.eth.contract(address=WAVAX, abi=ERC20_ABI).functions.balanceOf(me).call()
    wavax = wavax_wei / 1e18
    # ── THE WALLET'S LIQUID USDC, NOT THE BOOK'S TOTAL VALUE (fixed 2026-09-27, 6th pass) ────
    # Run against dadrian this planned "sell ~$0.2952 of USDC" on a wallet holding $0.00001 — his
    # capital is DEPLOYED, in 21 LP bins, where a swap cannot reach it. The plan was unexecutable
    # and the tool did not know, which is the same false-value family as everything above: a plan
    # presented as available when the asset it needs is not there. A swap draws on the WALLET, so
    # the wallet is what must be checked — book value is not liquidity.
    usdc_wei = w3.eth.contract(address=USDC, abi=ERC20_ABI).functions.balanceOf(me).call()
    usdc = usdc_wei / 1e6
    unwrap_need = shortfall_native * HEADROOM
    print(f"  WAVAX held    {wavax:.6f}  (~${wavax * avax_usd:.4f})")
    print(f"  USDC  held    {usdc:.6f}  (liquid, in the WALLET — the LP's value is not swappable)")

    acct = SI.signer() if a.execute else None

    # ── USE WHAT THE BOOK HAS FIRST, THEN BUY ONLY THE REMAINDER (fixed 2026-09-27, 3rd pass)
    # The first version was all-or-nothing: if the wallet did not hold the WHOLE amount in WAVAX
    # it skipped straight to "sell USDC". That blocked a top-up it could actually have completed —
    # the wallet held 0.00908 WAVAX (of the 0.01155 wanted) and 0.102 USDC, so unwrapping what was
    # there and buying only the 0.0025 remainder from USDC would have worked, while "sell 0.128
    # USDC" did not (the wallet held 0.102). A tool that gives up on a solvable problem, and says
    # the problem is unsolvable, is worse than no tool.
    # So: unwrap the WAVAX that exists, then size the swap from the ACTUAL remainder. Partial
    # progress is progress; the only failure is spending nothing and claiming success.
    #
    # ALL CLAMPING HAPPENS IN INTEGER WEI. The float round-trip is what reverted the first live run:
    # `int(0.009079999... * 1e18)` -> 0.009080000... -> one wei more than the wallet held ->
    # `execution reverted`. Balances are integers; never route one through a float to size a tx.
    #
    # REMAINDER IN WEI, NOT FLOAT (fixed 2026-09-28). `remainder` used to be
    # `max(0.0, unwrap_need - plan_unwrap)` — a FLOAT subtraction of two floats that are each an
    # int-truncated wei count. The subtraction leaves BINARY FLOAT DUST: a measured 5.7% of plans
    # produced a "remainder" of ~1e-19 AVAX (roughly a hundred-millionth of a wei) purely from the
    # representation error. Any `remainder > 0` then appended a phantom
    # "sell ~$0.0000 of USDC -> WAVAX" LEG — a swap of nothing — and, worse, charged it the
    # swap+unwrap gas budget instead of the unwrap-only one, so the tool could decide a top-up was
    # "NOT WORTH IT" over a leg that buys no AVAX. It was INTERMITTENT (it depended on the exact
    # float bits of the live balance that second), which is the worst kind: it looks like a
    # one-off. The integer form makes it exact and impossible.
    need_wei = int(unwrap_need * 1e18)
    plan_wei = min(wavax_wei, need_wei)
    remainder_wei = max(0, need_wei - plan_wei)
    remainder = remainder_wei / 1e18
    plan_unwrap = plan_wei / 1e18
    # ── AND A MINIMUM NOTIONAL FOR THE SWAP LEG (fixed 2026-09-28) ───────────────────────────
    # The unwrap leg has always had MIN_UNWRAP_AVAX ("below this a top-up is not worth a
    # transaction's gas"); the SWAP leg never had one. Wei-exact arithmetic removes the dust, but a
    # genuinely tiny remainder is still not worth a swap's gas, so the same reasoning is applied.
    min_swap_wei = int((MIN_SWAP_USD / max(avax_usd, 1e-9)) * 1e18)
    remainder_wei = 0 if remainder_wei < max(1, min_swap_wei) else remainder_wei
    remainder = remainder_wei / 1e18
    steps = []
    if plan_wei >= int(MIN_UNWRAP_AVAX * 1e18):
        steps.append(f"unwrap {plan_unwrap:.6f} WAVAX -> native AVAX")
    elif wavax > 0:
        print(f"  (holding {wavax:.6f} WAVAX — below the {MIN_UNWRAP_AVAX} worth a transaction)")
    if remainder > 0:
        steps.append(f"sell ~${(remainder * avax_usd) / (1 - GR.SWAP_FEE_PCT / 100):.4f} of USDC "
                     f"-> WAVAX, then unwrap")

    if not steps:
        # ── "NO STEPS" HAS TWO VERY DIFFERENT CAUSES (fixed 2026-09-27, 7th pass) ─────────────
        # This printed "the wallet holds no usable asset" for jordan, whose wallet held 0.065 USDC
        # and 0.0009 WAVAX. The assets were there; the GAP was 0.0009 AVAX — below MIN_UNWRAP_AVAX,
        # so no step cleared its threshold. Two facts were collapsed into one message, and the
        # message named the wrong one. Same false-value family: a true-sounding sentence that does
        # not describe the state. Distinguish them, because the action is different for each.
        has_liquid = (wavax > 0) or (usdc > 0)
        if has_liquid:
            print(f"\n  ⏸  GAP TOO SMALL TO JUSTIFY A TRANSACTION — short "
                  f"{shortfall_native:.8f} AVAX (~${shortfall_native * avax_usd:.4f}).")
            print(f"     The wallet DOES hold assets ({wavax:.6f} WAVAX, {usdc:.6f} USDC), but every")
            print(f"     available step is below the threshold where a transaction pays for itself.")
            print(f"     Stopping is the CORRECT outcome; this is stated, not hidden. To buy real")
            print(f"     runway, re-run with --target 2.")
            # A refusal is a verdict, and a dry run must still say nothing moved (2026-09-28).
            print(f"     Nothing was spent.")
        else:
            print(f"\n  ⛔ NOTHING TO UNWRAP and no remainder to buy — the wallet holds no usable asset.")
            print(f"     Every asset this wallet owns is DEPLOYED in the LP. Gas must come from the")
            print(f"     wallet: either an outside deposit, or a partial exit that frees some USDC.")
            print(f"     (A WAVAX/USDC book can fund its own gas ONLY when some of it is undeployed —")
            print(f"     the deployed half is not reachable without first withdrawing from the pool.)")
            # ── SAY IT ON EVERY REFUSAL (fixed 2026-09-28) ────────────────────────────────────
            # The sibling branch above states "Nothing was spent."; this one did not. Both are
            # refusals in the same function, and both are dry runs that stopped without moving
            # anything — so the statement belongs on BOTH. Without it, the one branch that fires
            # on a FLAT book was the only path that never confirmed no capital moved, and a
            # reader cannot tell "stopped safely" from "stopped and something happened".
            # The test caught this as "a dry run always states that nothing was spent" — a real
            # red, not fixture rot: it fired precisely because the books are now flat, which is
            # the state this branch exists for.
            print(f"     Nothing was spent.")
        if a.json:
            print(json.dumps({"tenant": tenant,
                              "action": "gap_too_small" if has_liquid else "nothing_liquid",
                              "balance_avax": balance, "wavax": wavax, "usdc": usdc,
                              "shortfall_avax": shortfall_native}, indent=2))
        return 0 if has_liquid else 3
    # The swap can only draw on LIQUID usdc. If that cannot cover the remainder, say so and stop —
    # planning a swap the wallet cannot fund is how a tool reports success on an impossible action.
    if remainder > 0:
        need_usd = (remainder * avax_usd) / (1 - GR.SWAP_FEE_PCT / 100)
        if usdc < need_usd:
            # THE TENANT NAME MUST COME FROM THE RUNTIME, NOT FROM THE MESSAGE (fixed 2026-09-27).
            # This line said "21 bins for dadrian" while running as JORDAN — a copy-paste of the
            # case that first exposed the gap. A tool that names the wrong treasury in its own
            # refusal is the same false-value family as everything else: the text is a value, and
            # a wrong one is worse than none, because it reads as authoritative.
            # The bin count was also a HARDCODED number, so it is removed rather than re-faked —
            # this tool has no chain reader for it, and an invented count is not a repair.
            print(f"\n  ⛔ CANNOT BUY THE REMAINDER — the swap needs ${need_usd:.4f} of liquid USDC; "
                  f"the wallet holds ${usdc:.6f}.")
            print(f"     SHORTFALL     {remainder:.8f} AVAX cannot be closed from this wallet.")
            print(f"     The rest of {tenant}'s book is DEPLOYED in the LP, where a swap cannot")
            print(f"     reach it. Options, in order of cost: an outside AVAX deposit; or let the "
                  f"re-center's own")
            print(f"     withdraw free the USDC first, then top up from that. Nothing was spent.")
            if a.json:
                print(json.dumps({"tenant": tenant, "action": "illiquid",
                                  "need_usd": need_usd, "usdc_liquid": usdc,
                                  "balance_avax": balance}, indent=2))
            return 3

    # ── NOW we know the path, so we know the real cost. Is closing the gap worth it? ─────────
    acquire_cost_avax = unwrap_gas_cost if remainder <= 0 else (swap_gas_cost + unwrap_gas_cost)
    paths = "unwrap only" if remainder <= 0 else "swap + unwrap"
    print(f"  SHORTFALL     {shortfall_native:.8f} AVAX  (~${shortfall_native * avax_usd:.4f})")
    print(f"  COST TO CLOSE {acquire_cost_avax:.8f} AVAX  (~${acquire_cost_avax * avax_usd:.4f}) "
          f"via {paths}")
    if shortfall_native <= acquire_cost_avax:
        print(f"\n  ⏸  NOT WORTH IT — the shortfall is smaller than the gas needed to close it.")
        print(f"     Stopping is the CORRECT outcome here, not a failure. Stated plainly: this book")
        print(f"     still cannot run a full cycle on its own and the next attempt will be refused.")
        print(f"     Closing it needs a top-up larger than the gap — re-run with --target 2 to buy")
        print(f"     real runway instead of chasing a few thousandths of an AVAX.")
        if a.json:
            print(json.dumps({"tenant": tenant, "action": "below_cost",
                              "balance_avax": balance, "shortfall_avax": shortfall_native,
                              "acquire_cost_avax": acquire_cost_avax}, indent=2))
        return 0
    if balance >= floor:
        print(f"  ⚠️  you are ABOVE the floor but NOT able to run a full cycle — this is exactly "
              f"the state that stranded the book on 2026-09-27.")

    print(f"  ACTION        " + "\n                ".join(steps))
    print(f"                a ROTATION within the position, not a sale — WAVAX is the gas asset")

    # ── CAN THIS WALLET PAY FOR THE TRANSACTION THAT FUNDS IT? ────────────────────────────────
    # The bootstrap is real and cheap but not free: an unwrap is 35,259 gas (~0.00018 AVAX at
    # 5 nAVAX). Below BOOTSTRAP_FLOOR_AVAX the wallet cannot start, and saying so is the whole
    # point — a silent no-op here is indistinguishable from a successful top-up.
    if balance < BOOTSTRAP_FLOOR_AVAX:
        print(f"\n  ⛔ CANNOT BOOTSTRAP — the wallet holds {balance:.8f} AVAX, below the "
              f"{BOOTSTRAP_FLOOR_AVAX:.5f} an unwrap needs to start.")
        print(f"     The unwrap that would fund this wallet is itself a transaction. This needs a")
        print(f"     small outside deposit; no asset in this wallet can be moved without gas.")
        if a.json:
            print(json.dumps({"tenant": tenant, "action": "blocked_bootstrap",
                              "balance_avax": balance,
                              "bootstrap_floor_avax": BOOTSTRAP_FLOOR_AVAX}, indent=2))
        return 3

    if not (a.execute and a.yes):
        print(f"  (dry-run — pass --execute --yes to send)")
        if a.json:
            print(json.dumps({"tenant": tenant, "action": "topup", "dry_run": True,
                              "unwrap_avax": plan_unwrap, "swap_usd": remainder * avax_usd,
                              "shortfall_avax": shortfall_native}, indent=2))
        return 0

    import subprocess
    did_any = False

    # STEP 1 — unwrap what the book already holds. Integer wei, clamped to the live balance.
    if plan_wei >= int(MIN_UNWRAP_AVAX * 1e18):
        live_wei = w3.eth.contract(address=WAVAX, abi=ERC20_ABI).functions.balanceOf(me).call()
        ok, detail, txh = unwrap(w3, me, acct, 0, execute=True, amount_wei=min(plan_wei, live_wei))
        print(f"\n  STEP 1  {'✅' if ok else '❌'} {detail}")
        if not ok:
            print(f"  ❌ unwrap failed — not proceeding to the swap. Nothing further was spent.")
            return 1
        did_any = True
        # ── POLL THE BALANCE, DO NOT READ IT ONCE (fixed 2026-09-28) ──────────────────────────
        # This was a SINGLE `w3.eth.get_balance(me)` immediately after the unwrap's receipt. A node
        # that has not yet applied the block answers with the PRE-transaction value, so a SUCCESSFUL
        # unwrap reported "+0.00000000" and "still short" — measured live on dadrian: the unwrap
        # mined (block 96334761, 35,283 gas) and the tool printed no change, while the truth was
        # 0.036088 -> 0.080233 on BOTH providers. That is the SAME defect already fixed in
        # lfj_bid_deploy.py's allowance re-read: an unapplied read is indistinguishable from a
        # transaction that did nothing.
        # This one is worse than a cosmetic error — a verify that reports a stale zero after a
        # confirmed spend invites a REDUNDANT SECOND SPEND of real gas.
        # Poll the balance until it MOVES, then report. If it never moves, say so honestly.
        bal_after = w3.eth.get_balance(me) / 1e18
        _t0 = _time.time()
        while _time.time() - _t0 < 60 and abs(bal_after - balance) < 1e-9:
            _time.sleep(3)
            bal_after = w3.eth.get_balance(me) / 1e18
        _waited = _time.time() - _t0
        print(f"          AVAX now {bal_after:.8f}  ({bal_after - balance:+.8f})"
              f"{'' if _waited < 1 else f'  (after {_waited:.0f}s)'}")
        if abs(bal_after - balance) < 1e-9:
            print(f"  ⚠️  the unwrap is CONFIRMED MINTED but the balance read UNCHANGED for 60s.")
            print(f"      Re-read the chain before spending again — do NOT assume it failed.")

    # STEP 2 — buy only the remainder. Re-read the BALANCE (not an assumption) to size it.
    if remainder > 0:
        bal_now = w3.eth.get_balance(me) / 1e18
        still = max(0.0, want_avax - bal_now) * HEADROOM
        if still <= 0:
            print(f"\n  STEP 2  (skipped — the unwrap already reached the target)")
        else:
            usd = (still * avax_usd) / (1 - GR.SWAP_FEE_PCT / 100)
            print(f"\n  STEP 2  sell ~${usd:.4f} of USDC -> WAVAX via lfj_swap_leg.py")
            sw = subprocess.run([sys.executable, os.path.join(HERE, "lfj_swap_leg.py"),
                                 "--from", "usdc", "--amount", f"{usd:.4f}",
                                 "--execute", "--yes", "--rescue"],
                                capture_output=True, text=True, timeout=600)
            tail = "\n".join((sw.stdout or "").strip().splitlines()[-8:])
            print(tail if tail else "(no stdout)")
            if sw.returncode != 0:
                print(f"  ⚠️  swap failed (exit {sw.returncode}). The unwrap already landed, so "
                      f"the top-up is PARTIAL — not nothing.")
                return 0 if did_any else 1
            wavax2_wei = w3.eth.contract(address=WAVAX, abi=ERC20_ABI).functions.balanceOf(me).call()
            take_wei = min(int(still * 1e18), wavax2_wei)
            # ── THE FINISHING STEP HAS A DIFFERENT TEST THAN THE STARTING STEP (fixed 2026-09-27)
            # The live run stopped short because this unwrap was gated by MIN_UNWRAP_AVAX (0.004) —
            # a threshold whose job is "is this worth STARTING a top-up?" The swap bought 0.000914
            # WAVAX specifically to become gas, and the tool then declined to convert it because it
            # was under a threshold about INITIATING. The WAVAX sat idle and the wallet stayed short.
            # The right test for the finishing step is ECONOMIC, not a fixed floor: unwrap when the
            # gas it costs is less than the gas it produces. Below that, converting genuinely loses
            # money and skipping is correct — so the rule is stated as the comparison, not a guess.
            unwrap_cost_wei = int(UNWRAP_GAS * w3.eth.gas_price)
            if take_wei > unwrap_cost_wei:
                ok, detail, txh = unwrap(w3, me, acct, 0, execute=True, amount_wei=take_wei)
                print(f"          {'✅' if ok else '❌'} {detail}")
                did_any = did_any or ok
            else:
                print(f"          (swapped WAVAX is {take_wei / 1e18:.6f} — less than the "
                      f"{unwrap_cost_wei / 1e18:.6f} AVAX its own unwrap would cost; leaving it)")

    if did_any:
        final = w3.eth.get_balance(me) / 1e18
        print(f"\n  VERIFY        AVAX now {final:.8f}   target {want_avax:.8f}   "
              f"{'✅ SELF-SUFFICIENT' if final >= self_sufficient else '⚠️ still short'}")
        if final < balance:
            print(f"  ⚠️  the balance FELL below where it started — re-read the chain before trusting this.")
            return 1
        if a.json:
            print(json.dumps({"tenant": tenant, "action": "topup", "dry_run": False,
                              "balance_avax": final, "target_avax": want_avax,
                              "self_sufficient": final >= self_sufficient}, indent=2))
    return 0 if did_any else 1


if __name__ == "__main__":
    sys.exit(main())
