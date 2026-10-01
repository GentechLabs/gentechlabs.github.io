#!/usr/bin/env python3
"""
gas_reserve.py — THE TREASURY FUNDS ITS OWN GAS.  (the instrument — and now the FLOOR)

Jordan, 2026-09-24:
    "we should always keep a buffer for the gas fee. So that way you won't really need me to send
     anything, because we want the treasury to truly manage itself."

Jordan, 2026-09-25 — RE-STATED FOR THE THIRD TIME, so it is a GATE from now on, not a note:
    "One of the most important rules that we have is keeping like maybe 10 cents of the natural
     whatever the coin is for gas, right? Because you never know when you'll need to make a swap
     or need to redeploy, right even though redeploying is pretty much almost free. You still got
     to have a little bit of gas."

THE POINT: a treasury that needs the owner to send gas is not self-managing. It is a treasury with
a dependency on a human, and that dependency surfaces at the worst possible moment -- when a
position needs re-centering and the wallet cannot pay for the re-center.

The good news, and it is the whole reason this is solvable: on Avalanche the volatile leg IS the
gas token. A book holding WAVAX/AVAX can always pay for its own operations, because the asset it
holds IS the asset gas is denominated in. The treasury never needs an external top-up; it needs the
discipline to KEEP A SLICE BACK.

===== THE FLOOR THE NO-IDLE RULE MUST RESPECT (2026-09-25) =====================================
THE ROOT CONFLICT this closes: the treasury runs a NO-IDLE-CAPITAL rule ("deploy the whole balance
-- idle capital is the failure mode"), and that rule FIGHTS the gas rule. No-idle wins by default,
so the gas reserve gets deployed into the LP and the wallet is left unable to pay for the very next
swap or redeploy. That is the mechanical cause of the repeated strandings, including jordan's book
being left out of the pool with 0.000025 AVAX to fix it (2026-09-25).

THE FIX, in one line: **"deploy the whole balance" means "deploy the whole balance MINUS the
reserve."** The reserve is a FLOOR the no-idle rule is not allowed to cross.

TWO FLOORS, TAKE THE GREATER, so neither alone can be defeated:
  * FLOOR_CYCLES full exit+re-entry cycles, priced at the LIVE gas price. This is the floor that
    scales with GAS: if gas spikes 50x, a dollar floor silently stops being one full cycle.
  * FLOOR_USD of native AVAX at the live AVAX price (Jordan's "10 cents"). This is the floor that
    scales with the ASSET: if AVAX halves, 200 cycles of gas can be worth pennies.
  reserve = max(FLOOR_CYCLES x cycle_cost, FLOOR_USD / avax_usd), both measured LIVE.

THE RULE AS IT NOW EXISTS IN CODE:
  "Every path that decides how much capital to deploy computes the reserve from the LIVE gas price
   and the LIVE AVAX price as max(floor_cycles x one exit+re-entry cycle, floor_usd in AVAX) and
   may deploy only the balance ABOVE it. An exit is never gated by the floor -- a book stranded out
   of the pool is worse than a thin gas balance -- and a deploy below the floor refuses in plain
   language naming the shortfall."

OVERRIDABLE BY ENV (the operator's knob, no code change needed):
  STEWARD_GAS_FLOOR_CYCLES=200   raise the cycle floor (the instrument's comfort number is 200)
  STEWARD_GAS_FLOOR_USD=0.25     raise the dollar floor
  STEWARD_GAS_FLOOR_BYPASS=1     RESCUE ONLY: the floor stops gating (loud, never silent)

===== LIBRARY API — CALL THIS, DO NOT REBUILD IT ================================================
Every money path imports THIS module; there is exactly one implementation of the floor.
    cycle_cost(w3=None)                        -> dict: live gas price + one exit/re-entry/cycle
    reserve_info(tenant, w3, avax_usd, ...)    -> dict: THE ONE COMPUTATION (see its docstring)
    reserve_in_token_wei(info, usd, decimals)  -> the reserve expressed in a LEG's own token (wei)
    cap_deploy(amt_wei, avail_wei, info, ...)  -> "the whole balance MINUS the reserve", in wei
    gate(info, cost_avax, action, bypass)      -> (ok, why): may this DEPLOY proceed?
    shortfall_text(info)                       -> plain language, naming the shortfall
    floor_line(info) / status_lines(info)      -> display, consistent everywhere

THE RESCUE RULE (why the floor can never block an exit):
  An exit is a REPAIR, and gas is what pays for repairs. Refusing to leave a broken state because
  the repair would cost the reserve is the floor defeating its own purpose. So: lfj_exit.py is NOT
  gated by the floor at all, and a deploy can only be forced through by an EXPLICIT --rescue flag
  (or STEWARD_GAS_FLOOR_BYPASS=1) that prints "the floor does not gate this action". Automatic
  bypasses do not exist: a floor with an automatic exception is not a floor.
  A recenter also refuses to START below the floor rather than withdrawing first -- "refusing to
  begin is free; abandoning halfway is not" -- so a book is never withdrawn and left stranded.

CLI (all read-only; this file never sends a transaction):
  --report (DEFAULT)  the live balance, the live gas price, the reserve and the runway
  --plan              also print the swap that would top the wallet up
  --json              the reserve_info dict, machine-readable
  --deploy-check      KEY=VALUE for shells; exit 0 above the floor, 3 below, 4 unmeasurable

This is READ-ONLY by design. Moving capital is a separate, verified step -- and per the standing
rule, a money path is proven in every state (including the empty book) before it ships.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WEBROOT = "/var/www/gentechlabs"

# ── THE FLOOR ────────────────────────────────────────────────────────────────────────────────
# ONE floor constant, two components, GREATER governs (see the header for why neither alone works).
# FLOOR_CYCLES: the rule's own unit -- Jordan: "you never know when you'll need to make a swap or
#   need to redeploy". At least ONE full exit + ONE full re-entry has to be payable at all times.
#   Raise it with STEWARD_GAS_FLOOR_CYCLES if the house wants the instrument's 200-cycle comfort
#   level to be the GATE as well; the gate default stays the rule as Jordan stated it.
FLOOR_CYCLES = 1
# FLOOR_USD: Jordan's rule, stated twice. Originally "maybe 10 cents of the natural whatever the
# coin is"; on 2026-09-27 he raised it to a firm standard: *"the rule of keeping gas to always keep
# yourself in good standing is also something that needs to be followed. I guess maybe we should go
# back to setting a standard of 20 cents... because most rebalances don't cost that much, but every
# once in a while the price goes up. So maybe we should carry 20 cents worth of AVAX or whatever the
# gas token is to make sure we're always good."*
# "GO BACK TO" is the operative phrase: 20 cents was the original standing, and the constant had
# drifted to 0.10. This restores the stated standard.
#
# WHY max() MAKES THIS SAFE: the dollar term can only ever RAISE the floor, never lower it, so a
# gas spike is already covered by the cycle term. Measured 2026-09-27 at 5.2064 nAVAX:
#     the floor's cycle (1.816M gas)  = $0.104   <- BELOW 20c, so the dollar term now governs
#     the deploy gate's budget (3.5M) = $0.201   <- already ~20c, unchanged
# So both terms land at ~20 cents today, and the rule reads as Jordan stated it: never carry less
# than ~20c of gas, and always carry enough for one full repair. Whichever is larger wins.
FLOOR_USD = 0.20
# COMFORT_CYCLES is a REPORTING threshold, NOT a gate. It is the instrument's original number,
# kept unchanged so no existing signal moves: it answers "how much headroom is there", which is a
# different question from "may we spend the last of it".
COMFORT_CYCLES = 200
RESERVE_TARGET_OPERATIONS = 600  # what a top-up aims to restore
SWAP_FEE_PCT = 0.30             # LFJ base fee 0.05% x2 legs + slippage headroom, generous
# The gas a FULL recenter needs (withdraw + rebalance swap + two leg deploys + approvals). Measured:
# a full exit uses ~142,395 and each single-sided leg ~1.2M (the estimator's figure, which is the
# safe one to budget). This is the START-GATE budget -- "can this action FINISH?" -- and it is a
# different quantity from the floor's one-exit+one-re-entry cycle. BOTH live here, and both are
# priced at the same LIVE gas price, so there is one place to look and no competing numbers.
RECENTER_GAS = 3_500_000



def _env_int(name, default):
    try:
        v = os.environ.get(name)
        return int(v) if v not in (None, "") else default
    except Exception:
        print(f"  ⚠️  {name} is not an integer — using the default {default}", file=sys.stderr)
        return default


def _env_float(name, default):
    try:
        v = os.environ.get(name)
        return float(v) if v not in (None, "") else default
    except Exception:
        print(f"  ⚠️  {name} is not a number — using the default {default}", file=sys.stderr)
        return default


def _tenant_floor_override(name: str, current_tenant: str = None):
    """(found, value) — a per-tenant override for a floor setting, read from tenants.json.

    Jordan, 2026-09-27: the gas floor was still a module constant while the registry had just grown
    a per-tenant ceiling. That is the FOURTH per-person setting found with nowhere to live in one
    day (shape, capital ceiling, deposit baselines, now the floor) — so the registry is made the
    place they all live, rather than growing a fourth special case.

    A per-tenant value is OPTIONAL and absent means "use the module default", so nothing changes
    for any tenant that does not set one. Precedence: env var (a one-off run) > tenant registry
    (that person's standing value) > module default.

    Returns (False, None) on any failure so the caller falls through to the default. A floor that
    cannot be read must not become zero — a zero floor spends the reserve that pays for repairs.
    """
    t = (current_tenant or os.environ.get("STEWARD_TENANT") or "jordan").strip().lower()
    try:
        import json as _j
        here = os.path.dirname(os.path.abspath(__file__))
        for p in (os.environ.get("STEWARD_REGISTRY"),
                  os.path.join(here, "tenants.json"),
                  "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"):
            if not p or not os.path.exists(p):
                continue
            with open(p) as f:
                d = _j.load(f)
            rec = (d.get("tenants") or {}).get(t) or {}
            gas = rec.get("gas") or {}
            if name in gas and gas[name] is not None:
                return True, gas[name]
            return False, None
    except Exception:
        return False, None
    return False, None


def floor_cycles():
    """The cycle floor: env (one-off run) > this tenant's registry value > the module default."""
    v = os.environ.get("STEWARD_GAS_FLOOR_CYCLES")
    if v not in (None, ""):
        return max(0, _env_int("STEWARD_GAS_FLOOR_CYCLES", FLOOR_CYCLES))
    found, tv = _tenant_floor_override("floor_cycles")
    if found:
        try:
            return max(0, int(tv))
        except (TypeError, ValueError):
            print(f"  ⚠️  tenant gas.floor_cycles is not an integer — using {FLOOR_CYCLES}",
                  file=sys.stderr)
    return max(0, FLOOR_CYCLES)


def floor_usd():
    """The dollar floor: env (one-off run) > this tenant's registry value > the module default."""
    v = os.environ.get("STEWARD_GAS_FLOOR_USD")
    if v not in (None, ""):
        return max(0.0, _env_float("STEWARD_GAS_FLOOR_USD", FLOOR_USD))
    found, tv = _tenant_floor_override("floor_usd")
    if found:
        try:
            return max(0.0, float(tv))
        except (TypeError, ValueError):
            print(f"  ⚠️  tenant gas.floor_usd is not a number — using {FLOOR_USD}", file=sys.stderr)
    return max(0.0, FLOOR_USD)


def bypass_armed():
    """RESCUE ONLY. True when STEWARD_GAS_FLOOR_BYPASS is set to a truthy value."""
    return str(os.environ.get("STEWARD_GAS_FLOOR_BYPASS", "")).strip().lower() in ("1", "true", "yes", "on")


def wallet_of(tenant):
    """Read the wallet from tenants.json -- NEVER re-type an address (see claim-provenance)."""
    import json as _j
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, "tenants.json"),
              "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"):
        try:
            with open(p) as f:
                d = _j.load(f)
            t = d.get("tenants", d).get(tenant) or {}
            w = t.get("wallet")
            if w:
                return w
        except Exception:
            continue
    return None


# gas UNITS per operation, measured from real receipts (see gas_runway.py for the full table).
# Exported so a long-runway reader and this file cannot drift apart.
#
# ── "mint" WAS A 3x UNDER-ESTIMATE AND IT STRANDED A LIVE BOOK (fixed 2026-09-27) ──────────────
# MEASURED, from the failed transaction itself:
#     Web3RPCError: insufficient funds for gas * price + value:
#         balance 4584049209086108, tx cost 6620230615071780, overshot 2036181405985672
# tx cost 0.0066203 AVAX at the gas price of the moment => **1,324,046 gas** for a 25-bin curve
# re-entry (2 approvals + mint). This table budgeted 530,000 — under by 2.5x — on the strength of a
# "mint: 420_000" entry that is a bare `mint()` and not the whole `mint()` on a 25-bin curve from
# the LFJ router, which is where the remaining ~900k goes.
# The consequence was not a refusal (over-charging is safe); it was the OPPOSITE: the gate asked
# "can this re-entry pay for itself?" with a number 2.5x too small, said YES, and the mint then
# failed on-chain — leaving jordan's book withdrawn and idle while the watchdog repeated the same
# doomed rescue every 10 minutes for hours.
# Approvals re-measured live via eth_estimateGas on the real tokens (57,774 + 47,988 = 105,762);
# the mint figure is the measured residual of the real failed tx. Rounded UP and generous on
# purpose: under-budgeting is what broke this, over-budgeting only refuses early.
# ── THE WITHDRAW WAS UNDER-BUDGETED BY ~3x (measured live, 2026-09-27) ───────────────────────
# `decreaseLiquidity` stood at 210,000 gas. Measured on dadrian's 25-bin book, the withdraw tx
# needs **1,328,018 gas** — the chain rejected it with:
#     insufficient funds for gas * price + value:
#     balance 4584049209086108, tx cost 6640088805636669, overshot 2056039596550561
# 450,000 budgeted (210k + 80k + 160k) against 1,328,018 spent: the exit line was 2.95x too low,
# and it scales with the number of bins (53,121 gas/bin at 25 bins).
#
# WHY THIS MATTERS MORE THAN A WRONG CONSTANT: the gate exists to prove a cycle can FINISH before
# it starts. Under-budgeting the WITHDRAW defeats that check in the exact direction it was written
# to prevent — the gate says "you can afford this", the withdraw then dies on-chain for funds, and
# on the recenter path the withdraw is step ONE of two. This is the same defect the REENTRY_GAS
# note above describes, on the opposite phase: a number from a table where a measurement was
# required. Both halves have now been corrected from live receipts rather than estimates.
#
# Budgeted generously above the measurement, per the standing rule: an over-budget only refuses
# early (recoverable, nothing spent), while an under-budget spends a tx and then fails the next.
#
# ── ⚠️ THE WITHDRAW FIGURE WAS SET FROM A RE-ENTRY MEASUREMENT — MY OWN MISATTRIBUTION ───────
# (2026-09-27, corrected the same day, before any capital moved.)
#
# This entry was briefly raised to 1,400,000 and then to a per-bin 53,121 gas/bin (2,390,445 for a
# 45-bin book), on the reasoning that "the withdraw scales with bins, measured 53,121 gas/bin". That
# reasoning rests on a number that belongs to a DIFFERENT OPERATION:
#
#   * git shows the 1,324,046 measurement (fb3ba25b7) is documented in this very file as
#     **"1,324,046 gas for a 25-bin curve RE-ENTRY (2 approvals + mint)"** — it came from the total
#     cost of a failed re-deploy tx, and at that commit `OP_GAS_UNITS` read
#         "decreaseLiquidity": 210_000,  "mint": 1_250_000
#     i.e. 1,324,046 was the MINT-side number, never the withdraw's.
#   * 1,328,018 / 25 = 53,121 "per bin" was therefore a RE-ENTRY rate applied to the withdraw.
#   * The file that actually sends the withdraw, `lfj_exit.py`, records the measured truth:
#     **"a full exit measures at 142,395 gasUsed"**, which is why its own ceiling is 1.5M with the
#     note "a real exit uses ~142k". A whole-book exit is ~142k gas, not ~1.3M and not per-bin.
#
# So the withdraw is NOT the expensive leg and does NOT carry that per-bin rate. The re-entry (mint)
# is the leg that measures ~1.3M, and it is already budgeted separately above.
#
# KEPT AT 210,000: ~1.5x the measured 142,395 receipt — deliberately generous, because
# under-budgeting is the direction that strands capital (the gate says yes, the withdraw dies
# on-chain for funds, the mint never runs). Over-budgeting only refuses early and costs nothing.
#
# ⚠️ THE LESSON, because this is a repeat offence in this file: a gas figure measured for ONE
# operation must never be reused for another just because both are "gas this cycle". The table is
# per-operation for that reason. If a number is about to be moved between rows, go back to the
# receipt that produced it and read which operation it measured.
# ══ ⚠️ SETTLED BY THE RECEIPTS, NOT BY THE DOCSTRING (2026-09-27, third pass) ═══════════════
# This constant was argued over three times today. The argument is over: the successful repair at
# 19:00Z left receipts on chain. Reading them ends it.
#
#   Dadrian's repair, measured from the actual transactions (25-bin book):
#     block 96276762   759,027 gas   -> THE WITHDRAW (decreaseLiquidity + collect), LB router
#     block 96276822   150,263 gas   -> the rebalance swap
#     block 96276826   702,895 gas   -> BID leg mint
#     block 96276834   737,703 gas   -> ASK leg mint
#
#   So, measured:
#     the WITHDRAW   ~759,027 gas   (a 25-bin book)
#     the RE-ENTRY   ~1,440,598 gas (702,895 + 737,703 — BOTH legs)
#
# ── WHAT WENT WRONG IN EACH OF THE THREE POSITIONS TAKEN TODAY ─────────────────────────────
#   1. 210,000 (the original). Under the withdrawal by 3.6x. This is the value the gate used when
#      dadrian's first repair was refused — it priced a 759k withdrawal at 210k and the withdraw
#      then died on-chain: "insufficient funds for gas * price + value".
#   2. 2,390,445 per-bin (2,390,445 = 53,121 x 45). WRONG NUMBER, right instinct: 1,328,018 was
#      the FAILED tx's total cost, not the withdraw's gas, so the per-bin rate was derived from a
#      number that did not describe the operation.
#   3. 210,000 again, on the reasoning that "a full exit measures at 142,395 gas" — a note in
#      lfj_exit.py. That note is a STALE FILE READING, and it is wrong for this book: the
#      withdrawal we actually ran measured 759,027. A docstring is not a receipt.
#
# THE LESSON, AND IT IS THE ONE THAT KEEPS RECURRING HERE: every one of the three positions was
# argued from a DOCUMENT — a table, a rate, a note — and the argument only ended when the CHAIN
# was read. One measured point beats three confident readings of files.
#
# BUDGETED ABOVE THE MEASUREMENT, per the standing rule: an over-budget refuses early and costs
# nothing; an under-budget spends the withdraw and then fails the re-deploy, stranding capital.
OP_GAS_UNITS = {
    "approve": 58_000, "collect": 80_000, "swap": 160_000,
    # MEASURED 759,027 on the 25-bin withdrawal (block 96276762). A second LB-router tx of 150,865
    # sits in the same window and MAY also belong to the withdraw phase, so the budget is set above
    # the worst joint reading (909,892) rather than the single clearest one. Over-budget refuses
    # early and costs nothing; the alternative is the under-budget that stranded capital today.
    "decreaseLiquidity": 1_000_000,
    # MEASURED: 702,895 + 737,703 = 1,440,598 for BOTH mint legs. The old 1,250,000 under-budgeted
    # the pair by ~190k — the same defect on the opposite phase.
    "mint": 1_500_000,
}

# ── THE FLAT-BOOK RE-ENTRY BUDGET (fixed 2026-09-27) ───────────────────────────────────────────
# A flat book re-entry does NOT withdraw — there is nothing to withdraw. It is approve x2 + mint and
# nothing else.
#
# The gate on the flat-book path used to charge RECENTER_GAS (3,500,000) — **6.6x what the action
# actually spends** — because two different questions were sharing one number:
#     * "can a FULL recenter finish?"        -> the start-gate budget (3.5M, deliberately generous,
#                                               measured against a 420k+ per-leg estimate)
#     * "can this RE-ENTRY pay for itself?"  -> approve x2 + mint ONLY
# Over-charging a gate is not the safe direction. It refused a live book that was earning nothing,
# over ~$0.007 it was never going to spend, and the refusal sent a human to top up a wallet that did
# not need it.
#
# ── BUT UNDER-CHARGING IS NOT SAFE EITHER, AND THAT IS THE DIRECTION THAT BROKE (2026-09-27) ──
# This note used to argue the number was "the safe one of the pair" because it was the LARGER of two
# independent estimates (530,000 vs 412,000). Both estimates were wrong in the same direction: the
# real re-entry measures **1,324,046** gas. Taking the larger of two under-estimates is still an
# under-estimate, and "we picked the bigger of our two guesses" is not a safety argument.
# The safe direction for a budget whose FAILURE MODE IS AN ON-CHAIN REJECTION is to exceed the
# measured cost, because an over-budget only refuses early (recoverable, no gas spent) while an
# under-budget spends the withdraw and then fails the mint (capital stranded, gas burned).
REENTRY_GAS = OP_GAS_UNITS["approve"] * 2 + OP_GAS_UNITS["mint"]


def per_op_costs(w3):
    """Measure the operation costs from the LIVE gas price -- never a remembered constant."""
    gp = w3.eth.gas_price
    return {k: (v * gp) / 1e18 for k, v in OP_GAS_UNITS.items()}, gp


# ── THE PRICE TO PUT ON A TRANSACTION (2026-09-26) ───────────────────────────────────────
# WHY HEADROOM IS NOT OPTIONAL. On Avalanche the base fee moves EVERY BLOCK, and `eth_gasPrice`
# returns the CURRENT base fee with a zero priority tip -- i.e. exactly the floor, with no
# margin at all. A transaction priced at that snapshot is therefore priced at the floor of the
# block it was read in; the instant the base fee ticks up, the tx is BELOW the floor and is
# INVALID. The node still returns a hash and the call looks successful, but the tx never
# propagates to any validator and the nonce never advances, so the caller waits out its entire
# receipt timeout for a receipt that cannot arrive.
#
# MEASURED LIVE (dadrian, 2026-09-26 09:51Z): the deploy legs were built at 0.097612 nAVAX
# while the chain's base fee had risen to 0.100841 -- 3.2% BELOW the floor. Both legs were
# absent from FOUR independent RPCs (publicnode, api.avax.network, drpc, 1rpc), the account
# nonce was still 249 (unused) on every one of them, ~$28 of capital sat idle earning nothing,
# and the 5-minute watchdog had been retrying into the same wall since 08:09Z.
#
# The gas LIMIT already carried x1.3; the gas PRICE carried none. Multiplying the wrong
# quantity by 1.3 is not headroom -- it is a long gas allowance at a price that cannot be
# mined. Headroom belongs on the PRICE.
GAS_PRICE_MULT = 1.3
GAS_PRICE_MULT_ENV = "STEWARD_GAS_PRICE_MULT"


def gas_price_wei(w3=None, mult=None):
    """The gas price to BUILD a transaction with: the live price WITH headroom.

    Returns max(suggested x mult, live baseFee x mult), so it is above the floor even when
    `eth_gasPrice` under-reports it. Raises rather than guessing -- a price we could not read
    is not a price.
    """
    if w3 is None:
        _px, w3 = chain()
    if w3 is None:
        raise RuntimeError("no chain connection — a gas price we cannot read is not a gas price")
    mult = mult if mult is not None else _env_float(GAS_PRICE_MULT_ENV, GAS_PRICE_MULT)
    gp = int(w3.eth.gas_price)
    try:
        _base = int(w3.eth.get_block("latest").get("baseFeePerGas") or 0)
    except Exception:                                                 # noqa: BLE001
        _base = 0
    return max(int(gp * mult), int(_base * mult))


def gas_price_navax(w3=None, mult=None):
    """Same, for display: the price in nAVAX, and the headroom it carries."""
    return gas_price_wei(w3, mult) / 1e9


def _cheap_price():
    """Live AVAX/USD without needing a chain connection (the fee ledger quotes it)."""
    try:
        import steward_fee_ledger as _L
        return float(_L.avax_usd())
    except Exception:
        return None


def chain():
    """(avax_usd, w3) -- the LIVE price and a connected Web3, or (None/px, None)."""
    try:
        import cascade_guard as CG
        _px, _w3, _pair, _act = CG.read_price()
        if _px and _w3:
            return float(_px), _w3
    except Exception:
        pass
    px = _cheap_price()
    try:
        from avax_rpc import connect
        w3 = connect(timeout=30)
    except Exception:
        w3 = None
    return px, w3


def cycle_cost(w3=None):
    """One full exit + one full re-entry + their sum, at the LIVE gas price.

    Returns a dict so every caller reads the same named quantities:
        gas_price_wei, gas_price_navax, exit_avax, reentry_avax, cycle_avax, cycle_gas_units
    Never a remembered gas price: `gp` is `eth_gasPrice` at call time.
    """
    if w3 is None:
        _px, w3 = chain()
    if w3 is None:
        raise RuntimeError("no chain connection — a gas price we cannot read is not a gas price")
    costs, gp = per_op_costs(w3)
    exit_avax = costs["decreaseLiquidity"] + costs["collect"] + costs["swap"]
    reentry_avax = costs["approve"] * 2 + costs["mint"]
    return {
        "gas_price_wei": int(gp),
        "gas_price_navax": gp / 1e9,
        "exit_avax": exit_avax,
        "reentry_avax": reentry_avax,
        "cycle_avax": exit_avax + reentry_avax,
        "cycle_gas_units": (OP_GAS_UNITS["decreaseLiquidity"] + OP_GAS_UNITS["collect"]
                            + OP_GAS_UNITS["swap"] + OP_GAS_UNITS["approve"] * 2
                            + OP_GAS_UNITS["mint"]),
    }


def reserve_info(tenant=None, w3=None, avax_usd=None, balance_avax=None, gas_price_wei=None):
    """THE ONE COMPUTATION. Every money path sizes its gas reserve from THIS.

    Inputs may be injected (a harness feeds synthetic balances and gas prices; a caller with an
    open connection passes its own `w3` so the deploy and the floor are priced off the same read).

    Returns a dict, never an opinion:
        measured / unmeasured_reason   was the gas price, the AVAX price and the balance all read?
        tenant, wallet
        gas_price_wei, gas_price_navax
        exit_avax, reentry_avax, cycle_avax, cycle_gas_units
        ops_runway                     full cycles the balance funds (the old RUNWAY number)
        floor_cycles, floor_usd
        by_cycles_avax, by_usd_avax    the two floors, each in AVAX
        reserve_avax, reserve_usd      max() of the two -- THE FLOOR
        balance_avax, balance_wei
        deployable_avax, deployable_wei   balance - reserve, floored at 0 when below
        above                          bool: is the balance at or above the floor?
        shortfall_avax, shortfall_usd  how far below, when it is below
    """
    info = {
        "measured": False, "unmeasured_reason": None,
        "tenant": tenant, "wallet": None,
        "gas_price_wei": None, "gas_price_navax": None,
        "exit_avax": None, "reentry_avax": None, "cycle_avax": None, "cycle_gas_units": None,
        "ops_runway": None, "floor_cycles": floor_cycles(), "floor_usd": floor_usd(),
        "by_cycles_avax": None, "by_usd_avax": None, "reserve_avax": None, "reserve_usd": None,
        "balance_avax": None, "balance_wei": None,
        "deployable_avax": 0.0, "deployable_wei": 0, "above": False,
        "shortfall_avax": None, "shortfall_usd": None, "avax_usd": avax_usd,
    }
    if tenant is None:
        tenant = os.environ.get("STEWARD_TENANT") or None
    if tenant is None:
        try:
            import steward_identity as _SI
            tenant = _SI.tenant()
        except Exception:
            tenant = None
    info["tenant"] = tenant
    info["wallet"] = wallet_of(tenant) if tenant else None

    # ONE connection for both the gas price and the balance, so the floor and the deploy that
    # consults it are priced off the same chain read (two reads = two answers, see bug class #10).
    if w3 is None and (gas_price_wei is None or balance_avax is None):
        _px, w3 = chain()
        if avax_usd is None and _px:
            avax_usd = _px
    if avax_usd is None:
        avax_usd = _cheap_price()
    info["avax_usd"] = avax_usd

    try:
        if gas_price_wei is not None:
            gp = int(gas_price_wei)
            costs = {k: (v * gp) / 1e18 for k, v in OP_GAS_UNITS.items()}
            cc = {
                "gas_price_wei": gp, "gas_price_navax": gp / 1e9,
                "exit_avax": costs["decreaseLiquidity"] + costs["collect"] + costs["swap"],
                "reentry_avax": costs["approve"] * 2 + costs["mint"],
            }
            cc["cycle_avax"] = cc["exit_avax"] + cc["reentry_avax"]
            cc["cycle_gas_units"] = (OP_GAS_UNITS["decreaseLiquidity"] + OP_GAS_UNITS["collect"]
                                     + OP_GAS_UNITS["swap"] + OP_GAS_UNITS["approve"] * 2
                                     + OP_GAS_UNITS["mint"])
        else:
            cc = cycle_cost(w3)
    except Exception as e:
        info["unmeasured_reason"] = f"gas price unreadable ({type(e).__name__}: {e})"
        return info
    info.update(cc)

    if balance_avax is None:
        try:
            if w3 is None or not info["wallet"]:
                raise RuntimeError("no chain connection or no wallet for this tenant")
            from web3 import Web3 as _W3
            info["balance_wei"] = int(w3.eth.get_balance(_W3.to_checksum_address(info["wallet"])))
            balance_avax = info["balance_wei"] / 1e18
        except Exception as e:
            info["unmeasured_reason"] = f"balance unreadable ({type(e).__name__}: {e})"
            return info
    info["balance_avax"] = float(balance_avax)
    if info["balance_wei"] is None:
        info["balance_wei"] = int(round(float(balance_avax) * 1e18))

    if not avax_usd or float(avax_usd) <= 0:
        info["unmeasured_reason"] = ("AVAX/USD unreadable — a dollar floor cannot be priced "
                                     "without a price")
        return info

    info["by_cycles_avax"] = info["floor_cycles"] * info["cycle_avax"]
    info["by_usd_avax"] = info["floor_usd"] / float(avax_usd)
    info["reserve_avax"] = max(info["by_cycles_avax"], info["by_usd_avax"])
    info["reserve_usd"] = info["reserve_avax"] * float(avax_usd)
    info["ops_runway"] = int(info["balance_avax"] / info["cycle_avax"]) if info["cycle_avax"] else 0
    info["above"] = info["balance_avax"] >= info["reserve_avax"]
    info["deployable_avax"] = max(0.0, info["balance_avax"] - info["reserve_avax"])
    info["deployable_wei"] = int(round(info["deployable_avax"] * 1e18))
    info["shortfall_avax"] = max(0.0, info["reserve_avax"] - info["balance_avax"])
    info["shortfall_usd"] = info["shortfall_avax"] * float(avax_usd)
    info["measured"] = True
    return info


def deployable_native(tenant=None, **kw):
    """(avax_above_the_floor, info) -- what a path that SPENDS NATIVE gas may use."""
    info = kw.pop("info", None) or reserve_info(tenant=tenant, **kw)
    return (info.get("deployable_avax") or 0.0), info


def reserve_in_token_wei(info, token_usd, decimals):
    """The floor expressed in ONE LEG'S OWN TOKEN, in wei -- what that leg must leave loose.

    The reserve is denominated in NATIVE AVAX because that is what gas is paid in. A deploy leg
    moves an ERC-20 (USDC or WAVAX), so the floor has to be converted: the treasury buys its gas by
    ROTATING a sliver of its own loose book, and a wallet that is 100% deployed has nothing to
    rotate. Returns None when the reserve could not be measured (the caller must then fail closed).
    """
    if not info or not info.get("measured") or not token_usd or float(token_usd) <= 0:
        return None
    usd = info["reserve_avax"] * float(info["avax_usd"])
    return int(round(usd / float(token_usd) * (10 ** decimals)))


def cap_deploy(amt_wei, avail_wei, info, token_usd, decimals, rescue=False):
    """(amount_wei, kept_wei, note) -- "the whole balance MINUS the reserve", in wei.

    `amt_wei` is the already-computed deploy amount (the caller keeps its own exact-integer ratio
    math). This caps it at (balance - reserve): an amount may never reach into the floor. A rescue
    (`rescue=True`) removes the cap and says so -- it never happens automatically.
    """
    amt_wei = int(max(0, amt_wei))
    avail_wei = int(max(0, avail_wei))
    if rescue:
        return min(amt_wei, avail_wei), max(0, avail_wei - min(amt_wei, avail_wei)), \
               "RESCUE — the floor is NOT held back"
    floor_wei = reserve_in_token_wei(info, token_usd, decimals)
    if floor_wei is None:
        # Fail CLOSED on an unmeasurable floor: a deploy must not spend a reserve it cannot size.
        return 0, avail_wei, "REFUSED — the floor is UNMEASURABLE, so it cannot be held back"
    ceiling = max(0, avail_wei - floor_wei)
    if amt_wei > ceiling:
        return ceiling, avail_wei - ceiling, (f"capped to leave the reserve "
                                             f"({floor_wei / 10 ** decimals:,.6f} of this token)")
    return amt_wei, avail_wei - min(amt_wei, avail_wei), "above the reserve — no cap needed"


def shortfall_text(info):
    """Plain language, naming the shortfall. This is what a refusal PRINTS (requirement: say it)."""
    if not info or not info.get("measured"):
        why = (info or {}).get("unmeasured_reason") or "the floor could not be measured"
        return (f"⚠️  BELOW THE GAS FLOOR? UNKNOWABLE — {why}. A reserve that cannot be sized "
                f"cannot be held back, so this deploy refuses (the exit path is never gated).")
    return (
        f"⚠️  BELOW THE GAS FLOOR — balance {info['balance_avax']:.6f} AVAX, reserve "
        f"{info['reserve_avax']:.6f} AVAX (max of {info['floor_cycles']} cycle(s) = "
        f"{info['by_cycles_avax']:.6f} and ${info['floor_usd']:.2f} = {info['by_usd_avax']:.6f} "
        f"AVAX, at {info['gas_price_navax']:.4f} nAVAX live) — SHORT BY "
        f"{info['shortfall_avax']:.6f} AVAX (~${info['shortfall_usd']:.4f}). "
        f"Deploying it would leave the treasury unable to pay for the next swap or re-deploy."
    )


def _avax_s(v):
    """Format an AVAX amount that may legitimately be UNMEASURED.

    A rescue message must never be the thing that crashes the rescue. (Found by test-gas-floor.py:
    gate(bypass=True) on an unmeasured floor raised
    `TypeError: unsupported format string passed to NoneType.__format__` — the one code path that
    exists to let a repair through was blowing up exactly when the box was in trouble.)
    """
    return f"{v:.6f} AVAX" if isinstance(v, (int, float)) else "UNMEASURED"


def gate(info, cost_avax=0.0, action="deploy", bypass=None):
    """(ok, why) -- MAY THIS DEPLOY PROCEED?

    The test is one line of arithmetic: `balance - cost_of_this_action >= reserve`. The reserve is
    spent by GAS, so an action that will spend gas has to leave the floor standing behind it.

    THIS IS A DEPLOY GATE ONLY. Never call it to allow or refuse an exit: the floor must not be able
    to block a rescue (see the header). `bypass=True` (or STEWARD_GAS_FLOOR_BYPASS=1, or the
    caller's --rescue) forces it through LOUDLY -- a floor with a silent exception is not a floor.
    """
    if bypass is None:
        bypass = bypass_armed()
    if bypass:
        return True, (f"RESCUE/BYPASS — the floor does NOT gate this {action} "
                      f"(balance {_avax_s((info or {}).get('balance_avax'))}, reserve "
                      f"{_avax_s((info or {}).get('reserve_avax'))}). Refusing to repair a broken "
                      f"state to preserve a gas balance is the floor defeating its own purpose.")
    if not info or not info.get("measured"):
        return False, shortfall_text(info)
    left = info["balance_avax"] - float(cost_avax)
    if left < info["reserve_avax"]:
        if info["balance_avax"] >= info["reserve_avax"] and cost_avax:
            # THE WALLET IS FINE; THIS ACTION IS NOT. Two different refusals, two different
            # sentences: "you are below the floor" (shortfall_text) vs "this action would put you
            # there". They were one sentence once, and it printed "SHORT BY 0.000000 AVAX" on a
            # wallet that was ABOVE the floor — a refusal nobody can act on (found live, 2026-09-25).
            proj = info["reserve_avax"] - left
            return False, (
                f"⚠️  THIS {action.upper()} WOULD SPEND THE GAS FLOOR — balance "
                f"{info['balance_avax']:.6f} AVAX, reserve {info['reserve_avax']:.6f} AVAX (max of "
                f"{info['floor_cycles']} cycle(s) = {info['by_cycles_avax']:.6f} and "
                f"${info['floor_usd']:.2f} = {info['by_usd_avax']:.6f} at "
                f"{info['gas_price_navax']:.4f} nAVAX live). This {action} spends ~"
                f"{float(cost_avax):.6f} AVAX of gas and leaves {left:.6f} — SHORT BY {proj:.6f} "
                f"AVAX (~${proj * info['avax_usd']:.4f}). Top the wallet up (gas_reserve.py --plan), "
                f"or force it as a rescue if the book is broken.")
        return False, shortfall_text(info)
    return True, (f"floor respected — balance {info['balance_avax']:.6f} AVAX - cost "
                  f"{float(cost_avax):.6f} >= reserve {info['reserve_avax']:.6f} AVAX "
                  f"({info['floor_cycles']} cycle(s) / ${info['floor_usd']:.2f} at "
                  f"{info['gas_price_navax']:.4f} nAVAX live)")


def floor_line(info):
    """One line, identical in every tool, so the same number is never described two ways."""
    if not info or info.get("measured") is not True:
        return (f"gas floor: UNMEASURED — {(info or {}).get('unmeasured_reason') or 'no reading'}")
    return (f"gas floor: reserve {info['reserve_avax']:.6f} AVAX "
            f"(max of {info['floor_cycles']} cycle(s) {info['by_cycles_avax']:.6f} and "
            f"${info['floor_usd']:.2f} = {info['by_usd_avax']:.6f}) at {info['gas_price_navax']:.4f} "
            f"nAVAX LIVE | balance {info['balance_avax']:.6f} | deployable above it "
            f"{info['deployable_avax']:.6f}")


def status_lines(info):
    """The display block, built from the SAME dict every tool gates on."""
    out = []
    if not info or info.get("measured") is not True:
        out.append("  status        ⚠️  UNMEASURED — "
                   + str((info or {}).get("unmeasured_reason") or "could not read the floor"))
        return out
    out.append(f"    balance       {info['balance_avax']:.6f} AVAX   (deployable above the floor "
               f"{info['deployable_avax']:.6f})")
    out.append(f"    THE FLOOR     {info['reserve_avax']:.6f} AVAX  = max({info['floor_cycles']} "
               f"cycle(s) {info['by_cycles_avax']:.6f}, ${info['floor_usd']:.2f} = "
               f"{info['by_usd_avax']:.6f} AVAX)  (~${info['reserve_usd']:.4f})")
    if info["above"]:
        out.append(f"    status        ✅ AT/ABOVE the floor — {info['ops_runway']} cycles of "
                   f"runway, {info['ops_runway'] - info['floor_cycles']} above the floor "
                   f"(comfort threshold {COMFORT_CYCLES} cycles: "
                   f"{'met' if info['ops_runway'] >= COMFORT_CYCLES else 'NOT met — thin, but usable'})")
    else:
        out.append(f"    status        ⚠️  BELOW the floor — short "
                   f"{info['shortfall_avax']:.6f} AVAX (~${info['shortfall_usd']:.4f}); "
                   f"{info['ops_runway']} cycles of runway left")
    return out


def report(tenant, plan=False):
    """The CLI body. Reads the SAME reserve_info() the money paths gate on — one implementation."""
    info = reserve_info(tenant=tenant)
    if not info["wallet"]:
        print(f"  {tenant}: wallet not found in tenants.json — refusing to guess an address")
        return 1
    print(f"\n  ── {tenant} ─────────────────────────────────────────────────────────")
    print(f"    wallet        {info['wallet']}")
    if info.get("measured") is not True:
        print(f"    ⚠️  UNMEASURED — {info.get('unmeasured_reason')}")
        print(f"    (a reserve that cannot be sized cannot be held back — every deploy path "
              f"refuses on this state; the exit path never does)")
        return 1
    print(f"    AVAX          {info['balance_avax']:.6f}   "
          f"(~${info['balance_avax'] * info['avax_usd']:.4f} at ${info['avax_usd']:.4f})")
    print(f"    gas price     {info['gas_price_navax']:.4f} nAVAX  (live, not remembered)")
    print(f"    one full exit {info['exit_avax']:.6f} AVAX   one re-entry {info['reentry_avax']:.6f} AVAX")
    print(f"    one cycle     {info['cycle_avax']:.6f} AVAX  ({info['cycle_gas_units']:,} gas units)")
    print(f"    RUNWAY        {info['ops_runway']} full cycles")
    for l in status_lines(info):
        print(l)
    if not info["above"] and plan:
        need = info["shortfall_avax"]
        print(f"    TOP-UP PLAN   sell ~${(need * info['avax_usd']) / (1 - SWAP_FEE_PCT / 100):.4f} "
              f"of the book's USDC into AVAX (fee+slippage {SWAP_FEE_PCT}%)")
        # This line used to read "-> restores 600 cycles", from RESERVE_TARGET_OPERATIONS — a
        # constant that appears NOWHERE ELSE in this file and is used by no calculation at all.
        # The top-up restores the FLOOR (one cycle, plus headroom), not 600 cycles. A display
        # line asserting a number nothing computes is the false-value family this codebase keeps
        # re-learning, so it now states what the arithmetic actually does.
        print(f"                  -> restores the floor ({info['reserve_avax']:.6f} AVAX, "
              f"~{max(1, int(info['reserve_avax'] / info['cycle_avax']))} cycle(s))")
        print(f"                  RUN IT:  python3 gas_topup.py --execute --yes")
        print(f"                  the book is WAVAX/USDC, so this is a rotation WITHIN the "
              f"position, not an outside deposit")
    return 0


def _deploy_check(tenant, cost_gas=None):
    """Shell entry point: KEY=VALUE on stdout, exit 0 above the floor / 3 below / 4 unmeasurable.

    The gate charges the gas the CALLER is about to spend, defaulting to RECENTER_GAS (the full
    withdraw+redeploy cycle) so a shell check in front of a two-leg deploy is exactly as strict as
    the legs it is protecting. `--cost-gas 0` checks the bare floor instead.
    """
    info = reserve_info(tenant=tenant)
    if cost_gas is None:
        cost_gas = RECENTER_GAS
    try:
        cost_avax = (int(cost_gas) * int(info["gas_price_wei"])) / 1e18 if info.get("gas_price_wei") else 0.0
    except Exception:
        cost_avax = 0.0
    ok, why = gate(info, cost_avax=cost_avax, action="deploy")
    print(f"MEASURED={1 if info.get('measured') else 0}")
    print(f"TENANT={info.get('tenant') or ''}")
    print(f"WALLET={info.get('wallet') or ''}")
    for k, key in (("gas_price_navax", "GAS_PRICE_NAVAX"), ("cycle_avax", "CYCLE_AVAX"),
                   ("floor_cycles", "FLOOR_CYCLES"), ("floor_usd", "FLOOR_USD"),
                   ("by_cycles_avax", "BY_CYCLES_AVAX"), ("by_usd_avax", "BY_USD_AVAX"),
                   ("reserve_avax", "RESERVE_AVAX"), ("balance_avax", "BALANCE_AVAX"),
                   ("deployable_avax", "DEPLOYABLE_AVAX"),
                   ("ops_runway", "RUNWAY_CYCLES")):
        v = info.get(k)
        print(f"{key}={'' if v is None else v}")
    # ── ABOVE MUST MATCH THE EXIT CODE (fixed 2026-09-28) ─────────────────────────────────────
    # `ABOVE` and `SHORTFALL_AVAX` were printed from `info` — the BARE floor — while the verdict
    # (`ok`, and therefore the exit code) came from `gate(info, cost_avax=<the caller's cost>)`.
    # Measured live on dadrian: the tool exited **3 (below the floor)** while printing
    # `ABOVE=1` and `SHORTFALL_AVAX=0.0`. A shell that reads `ABOVE=1` instead of the exit code is
    # told the floor is clear by the exact tool that says otherwise — the tool contradicting itself.
    # Both must describe the SAME question: the caller's cost, not the bare floor.
    _cost = float(cost_avax or 0.0)
    _bal = float(info.get("balance_avax") or 0.0)
    _res = float(info.get("reserve_avax") or 0.0)
    _short = max(0.0, (_res + _cost) - _bal) if info.get("measured") else 0.0
    print(f"COST_AVAX={_cost}")
    print(f"ABOVE={1 if ok else 0}")
    print(f"SHORTFALL_AVAX={_short}")
    print(f"REASON={why}")
    if not info.get("measured"):
        return 4
    return 0 if ok else 3


def main():
    ap = argparse.ArgumentParser(description="Gas reserve — does the treasury fund its own gas?")
    ap.add_argument("--tenant", default=None)
    ap.add_argument("--plan", action="store_true", help="also print the top-up plan")
    ap.add_argument("--json", action="store_true", help="the reserve_info dict, machine-readable")
    ap.add_argument("--deploy-check", action="store_true",
                    help="KEY=VALUE for shells; exit 0 above the floor, 3 below, 4 unmeasurable")
    ap.add_argument("--cost-gas", type=int, default=None,
                    help="gas units the caller is about to spend, charged against the floor by "
                         "--deploy-check (default RECENTER_GAS; 0 = check the bare floor)")
    a = ap.parse_args()

    import json as _j
    here = os.path.dirname(os.path.abspath(__file__))
    tenants = ["jordan", "dadrian"]
    for p in (os.path.join(here, "tenants.json"),
              "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"):
        try:
            with open(p) as f:
                d = _j.load(f)
            tenants = list((d.get("tenants", d) or {}).keys())
            tenants = [t for t in tenants if wallet_of(t)]
            break
        except Exception:
            continue

    # ── A GATE MUST ACT ON EXACTLY ONE TENANT ─────────────────────────────────────────────────
    # `--deploy-check` is consumed by shells as a GATE. Looping every tenant and OR-ing the exits
    # would refuse jordan's deploy because dadrian is below the floor — one tenant's thinness
    # blocking another tenant's money. So the check resolves ONE tenant: --tenant, else
    # STEWARD_TENANT (the fleet convention — an env var, never a flag), else steward_identity.
    if a.deploy_check:
        if not a.tenant:
            try:
                import steward_identity as _SI
                a.tenant = os.environ.get("STEWARD_TENANT") or _SI.tenant()
            except Exception:
                a.tenant = os.environ.get("STEWARD_TENANT") or (tenants[0] if tenants else None)
        return _deploy_check(a.tenant, a.cost_gas)

    sel = a.tenant or (os.environ.get("STEWARD_TENANT") or None)
    if sel:
        if a.json:
            print(_j.dumps(reserve_info(tenant=sel), indent=2, default=str))
            return 0
        return report(sel, a.plan)

    if a.json:
        print(_j.dumps({t: reserve_info(tenant=t) for t in tenants}, indent=2, default=str))
        return 0

    print("=" * 92)
    print("  GAS RESERVE — can the treasury pay for its own operations?")
    print("  Jordan: 'always keep a buffer for the gas fee... we want the treasury to truly manage")
    print("  itself.' On Avalanche the volatile leg IS the gas token, so a WAVAX book already")
    print("  holds everything it needs — the discipline is keeping a slice back.")
    print("  THE FLOOR THE NO-IDLE RULE MUST RESPECT: \"deploy the whole balance\" means")
    print("  \"deploy the whole balance MINUS the reserve\".")
    print("=" * 92)
    rc = 0
    for t in tenants:
        try:
            rc |= report(t, a.plan)
        except Exception as e:
            print(f"  {t}: error {type(e).__name__}: {e}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
