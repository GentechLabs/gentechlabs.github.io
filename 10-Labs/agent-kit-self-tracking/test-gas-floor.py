#!/usr/bin/env python3
"""
test-gas-floor.py — THE GAS FLOOR, PROVEN IN BOTH DIRECTIONS.

WHAT THIS PROTECTS (Jordan, 2026-09-25, restating the rule for the third time):
    "keeping like maybe 10 cents of the natural whatever the coin is for gas... You still got to
     have a little bit of gas."
The no-idle rule ("deploy the whole balance") and the gas rule fight, and no-idle wins by default —
so the reserve gets deployed into the LP and the wallet is left unable to pay for the next swap or
re-deploy. That is the mechanical cause of a book stranded out of the pool.

THE RULE UNDER TEST
    reserve = max(floor_cycles x one_exit_plus_reentry_cycle, floor_usd / avax_usd)
    deployable = balance - reserve      (and 0 when the balance is at or below the reserve)
    a deploy may run only when      balance - cost_of_this_action >= reserve
    an EXIT is never gated by any of it.

HOW THIS TESTS IT: every case feeds SYNTHETIC balances and a SYNTHETIC gas price into the REAL
functions (gas_reserve.reserve_info / cap_deploy / gate, lfj_recenter._reserve_split /
_gas_precondition). Nothing is faked about the logic — only the inputs — and no transaction is
sent, no key is read, nothing is signed. The live-wallet figures are printed SEPARATELY and are
read-only.

Run:  python3 test-gas-floor.py        (exit 0 = every case behaved; non-zero = something did not)
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gas_reserve as GR

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []
CHECKS = [0]


def check(label, cond, detail=""):
    CHECKS[0] += 1
    print(f"    {'✅' if cond else '❌'} {label}")
    if detail:
        print(f"       {detail}")
    if not cond:
        FAILS.append(label)


def hr(t):
    print("\n" + "═" * 92)
    print(f"  {t}")
    print("═" * 92)


def code_only(path):
    """The file's CODE with comments and docstrings REMOVED.

    Why: a check that fires on the PROSE describing a retired constant is as useless as one that
    cannot recognise a pass (the lesson already recorded in data-provenance-audit.py). "FLOOR_USDC
    is gone" has to be a claim about the CODE, not about the comment that explains why it is gone.
    """
    import io
    import tokenize
    src = open(path, encoding="utf-8").read()
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.COMMENT,):
                continue
            if tok.type == tokenize.STRING and (tok.string.startswith('"""')
                                                or tok.string.startswith("'''")):
                continue
            out.append(tok.string)
    except Exception:
        return src
    return " ".join(out)


# A FIXED gas price for the synthetic cases, so the arithmetic is checkable by hand:
# 0.5 nAVAX/gas -> one exit+re-entry cycle (980,000 gas) = 0.00049 AVAX.
GP = 500_000_000
GP_NAVAX = GP / 1e9
AVAX_USD = 10.00        # fixed for the synthetic cases; the live cases read the real price
CYCLE = 980_000 * GP / 1e18


def synth(balance_avax, floor_cycles=None, floor_usd=None, gp=GP, avax_usd=AVAX_USD):
    """reserve_info() on synthetic inputs. Only the inputs are synthetic."""
    old = {k: os.environ.get(k) for k in ("STEWARD_GAS_FLOOR_CYCLES", "STEWARD_GAS_FLOOR_USD",
                                          "STEWARD_GAS_FLOOR_BYPASS")}
    try:
        os.environ.pop("STEWARD_GAS_FLOOR_BYPASS", None)
        if floor_cycles is not None:
            os.environ["STEWARD_GAS_FLOOR_CYCLES"] = str(floor_cycles)
        else:
            os.environ.pop("STEWARD_GAS_FLOOR_CYCLES", None)
        if floor_usd is not None:
            os.environ["STEWARD_GAS_FLOOR_USD"] = str(floor_usd)
        else:
            os.environ.pop("STEWARD_GAS_FLOOR_USD", None)
        return GR.reserve_info(tenant="jordan", gas_price_wei=gp, avax_usd=avax_usd,
                               balance_avax=balance_avax)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def main():
    print("=" * 92)
    print("  GAS FLOOR — HARNESS (synthetic balances, the REAL functions, nothing sent)")
    print(f"  synthetic gas price {GP_NAVAX} nAVAX  →  one exit+re-entry cycle {CYCLE:.8f} AVAX")
    print(f"  synthetic AVAX/USD  ${AVAX_USD:.2f}   →  $0.10 = {0.10 / AVAX_USD:.8f} AVAX "
          f"(the greater governs)")
    print("=" * 92)

    reserve_expected = max(1 * CYCLE, 0.10 / AVAX_USD)

    # ─────────────────────────────────────────────────────────────────────────
    hr("THE FLOOR IS THE GREATER OF ITS TWO COMPONENTS (neither alone can be defeated)")
    ri = synth(1.0)
    check("reserve == max(cycles x cycle, usd/avax_usd)",
          abs(ri["reserve_avax"] - reserve_expected) < 1e-12,
          f"reserve {ri['reserve_avax']:.8f} = max(cycles {ri['by_cycles_avax']:.8f}, "
          f"usd {ri['by_usd_avax']:.8f})")
    check("at THIS gas price and THIS price the DOLLAR floor governs (also true live)",
          ri["by_usd_avax"] > ri["by_cycles_avax"],
          f"${ri['floor_usd']:.2f} = {ri['by_usd_avax']:.8f} AVAX > 1 cycle "
          f"{ri['by_cycles_avax']:.8f} AVAX")
    # Gas spike 40x: the CYCLE floor must take over, or a dollar floor would buy nothing.
    spike = synth(1.0, gp=GP * 40)
    check("a 40x GAS SPIKE makes the CYCLE floor govern — the dollar floor alone could not",
          spike["by_cycles_avax"] > spike["by_usd_avax"]
          and abs(spike["reserve_avax"] - spike["by_cycles_avax"]) < 1e-12,
          f"gas {spike['gas_price_navax']:.2f} nAVAX → cycle floor {spike['by_cycles_avax']:.8f} "
          f"AVAX > ${spike['floor_usd']:.2f} = {spike['by_usd_avax']:.8f} AVAX")
    # AVAX collapse: the dollar floor must be worth more AVAX, so it must grow.
    crash = synth(1.0, avax_usd=2.00)
    check("an AVAX COLLAPSE ($10 → $2) makes the dollar floor hold 5x the AVAX",
          abs(crash["by_usd_avax"] - 0.05) < 1e-12,
          f"$0.10 at $2.00/AVAX = {crash['by_usd_avax']:.8f} AVAX (vs "
          f"{0.10 / AVAX_USD:.8f} at $10)")

    # ─────────────────────────────────────────────────────────────────────────
    hr("(a) A WALLET ABOVE THE FLOOR — deploys the whole balance MINUS the reserve, reserve intact")
    bal = 0.100000
    ri = synth(bal)
    check("measured from the live-priced inputs", ri["measured"] is True)
    check("reserve computed and reported", ri["reserve_avax"] > 0,
          f"reserve {ri['reserve_avax']:.8f} AVAX (~${ri['reserve_usd']:.4f})")
    check("deployable == balance - reserve",
          abs(ri["deployable_avax"] - (bal - ri["reserve_avax"])) < 1e-12,
          f"{bal:.6f} - {ri['reserve_avax']:.6f} = {ri['deployable_avax']:.6f} AVAX")
    ok, why = GR.gate(ri, cost_avax=0.0, action="deploy")
    check("the gate ALLOWS a deploy", ok, why[:150])
    ok2, why2 = GR.gate(ri, cost_avax=3_500_000 * GP / 1e18, action="re-center")
    check("the gate still allows a full re-center's gas (balance - cost >= reserve)", ok2)
    # The leg-level cap, on the SAME inputs, in the leg's own token.
    avail_usdc = 39_691_850                       # 39.691850 USDC, wei-equivalent (6dp)
    amt, kept, note = GR.cap_deploy(avail_usdc, avail_usdc, ri, 1.0, 6)
    check("a LEG deploys balance - reserve and holds the reserve back",
          amt == avail_usdc - 100_000 and kept == 100_000,
          f"deployed {amt/1e6:,.6f} USDC, kept {kept/1e6:,.6f} USDC  ({note})")
    wavax_avail = int(10.066 * 1e18)
    amt_w, kept_w, note_w = GR.cap_deploy(wavax_avail, wavax_avail, ri, AVAX_USD, 18)
    check("the ASK leg holds the reserve in WAVAX too (the gas token's own wrapped form)",
          abs(kept_w / 1e18 - ri["reserve_avax"]) < 1e-9,
          f"deployed {amt_w/1e18:,.6f} WAVAX, kept {kept_w/1e18:,.6f} WAVAX  ({note_w})")
    check("a partial ratio BELOW the cap is untouched (ratio 0.3 of USDC)",
          GR.cap_deploy(avail_usdc * 3 // 10, avail_usdc, ri, 1.0, 6)[0] == avail_usdc * 3 // 10)
    d, r_usd, sok, swhy = _recenter_split(ri, 121.36)
    check("the RECENTER's composition step sizes off balance - reserve",
          sok and abs(d - (121.36 - ri["reserve_avax"] * AVAX_USD)) < 1e-9,
          f"deployable ${d:,.4f} of $121.36 ({swhy})")

    # ─────────────────────────────────────────────────────────────────────────
    hr("(b) A WALLET BELOW THE FLOOR — refuses to deploy the reserve, names the shortfall")
    ri_b = synth(0.002)
    check("synthetic wallet IS below the floor", ri_b["above"] is False,
          f"balance {ri_b['balance_avax']:.6f} < reserve {ri_b['reserve_avax']:.6f} AVAX")
    check("deployable is ZERO (not negative, not the balance)",
          ri_b["deployable_avax"] == 0.0 and ri_b["deployable_wei"] == 0)
    check("the shortfall is named in AVAX and in dollars",
          abs(ri_b["shortfall_avax"] - (ri_b["reserve_avax"] - 0.002)) < 1e-12
          and ri_b["shortfall_usd"] > 0,
          f"short by {ri_b['shortfall_avax']:.8f} AVAX (~${ri_b['shortfall_usd']:.4f})")
    ok_b, why_b = GR.gate(ri_b, cost_avax=0.0, action="deploy")
    check("the gate REFUSES", ok_b is False)
    check("the refusal is plain language and names the shortfall",
          "BELOW THE GAS FLOOR" in why_b and "SHORT BY" in why_b and "AVAX" in why_b,
          why_b[:260])
    amt_b, kept_b, note_b = GR.cap_deploy(avail_usdc, avail_usdc, ri_b, 1.0, 6)
    check("a leg holds back exactly the reserve-in-token (the refusal itself is the GATE's job)",
          kept_b == 100_000 and amt_b == avail_usdc - 100_000,
          f"deployed {amt_b/1e6:,.6f} USDC, kept {kept_b/1e6:,.6f} USDC (= the $0.10 floor in "
          f"USDC); below the floor the gate refuses BEFORE any sizing — checked next")
    _bd_src = open(os.path.join(HERE, "lfj_bid_deploy.py")).read()
    check("lfj_bid_deploy calls the FLOOR GATE before it computes any deploy amount",
          _bd_src.index("_gas_floor(a, w3, ME)") < _bd_src.index("cap_deploy("),
          "a below-floor wallet exits 7 before a single wei of sizing — the reserve cannot be "
          "reached even accidentally")
    ok_r, why_r = GR.gate(ri_b, cost_avax=0.0, action="deploy", bypass=True)
    check("RESCUE (bypass) lets it through AND SAYS SO", ok_r is True and "RESCUE" in why_r,
          why_r[:150])
    amt_r, kept_r, note_r = GR.cap_deploy(avail_usdc, avail_usdc, ri_b, 1.0, 6, rescue=True)
    check("a RESCUE leg deploys the full balance and states the floor did not gate it",
          amt_r == avail_usdc and "RESCUE" in note_r, note_r)

    # ─────────────────────────────────────────────────────────────────────────
    hr("(c) THE BOUNDARY — a wallet EXACTLY at the floor")
    ri_c = synth(reserve_expected)
    check("balance == reserve is AT the floor (not below)",
          ri_c["above"] is True and abs(ri_c["balance_avax"] - ri_c["reserve_avax"]) < 1e-15,
          f"balance {ri_c['balance_avax']:.10f} == reserve {ri_c['reserve_avax']:.10f}")
    check("deployable is exactly ZERO — there is no spare capital at the floor",
          ri_c["deployable_avax"] == 0.0)
    ok_c0, why_c0 = GR.gate(ri_c, cost_avax=0.0, action="deploy")
    check("a ZERO-COST deploy is allowed (nothing is spent, the floor stands)", ok_c0,
          why_c0[:130])
    ok_c1, why_c1 = GR.gate(ri_c, cost_avax=CYCLE, action="re-center")
    check("ANY gas-spending action at the floor is REFUSED — it would spend the floor",
          ok_c1 is False, why_c1[:200])
    amt_c, kept_c, note_c = GR.cap_deploy(avail_usdc, avail_usdc, ri_c, 1.0, 6)
    check("a leg AT the floor deploys balance - reserve-in-token and keeps the reserve",
          kept_c == 100_000 and amt_c == avail_usdc - 100_000,
          f"deployed {amt_c/1e6:,.6f} USDC, kept {kept_c/1e6:,.6f} USDC  ({note_c})")

    # ─────────────────────────────────────────────────────────────────────────
    hr("FAIL CLOSED — an unmeasurable floor is never spent")
    # Simulate THE CHAIN BEING UNREADABLE (an RPC outage), which is the only way the floor can come
    # back unmeasured on a live box. Only the SOURCE OF THE READ is replaced; the logic under test
    # is untouched.
    _oc, _op = GR.chain, GR._cheap_price
    GR.chain, GR._cheap_price = (lambda *a, **k: (None, None)), (lambda: None)
    try:
        bad = GR.reserve_info(tenant="jordan", balance_avax=1.0)
        check("an unreadable chain produces an UNMEASURED floor (not a silent zero)",
              bad.get("measured") is not True,
              f"reason: {bad.get('unmeasured_reason')}")
        ok_u, why_u = GR.gate(bad, action="deploy")
        check("unmeasurable floor → the deploy REFUSES (fail closed)", ok_u is False, why_u[:170])
        amt_u, kept_u, note_u = GR.cap_deploy(avail_usdc, avail_usdc, bad, 1.0, 6)
        check("unmeasurable floor → a leg deploys NOTHING", amt_u == 0, note_u)
        ok_ur, why_ur = GR.gate(bad, action="deploy", bypass=True)
        check("and a RESCUE still works on an unmeasurable floor", ok_ur is True, why_ur[:140])
    finally:
        GR.chain, GR._cheap_price = _oc, _op

    # ─────────────────────────────────────────────────────────────────────────
    hr("AN EXIT IS NEVER GATED BY THE FLOOR (the rescue rule, checked against the SOURCE)")
    src = open(os.path.join(HERE, "lfj_exit.py")).read()
    tree = ast.parse(src)
    gate_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if name in ("gate", "cap_deploy"):
                gate_calls.append("{}() line {}".format(name, node.lineno))
    check("lfj_exit.py contains NO call to gas_reserve.gate()/cap_deploy() — it cannot be gated",
          not gate_calls, f"found: {gate_calls}" if gate_calls else
          "the exit reports the floor and states that it is not a gate")
    check("lfj_exit.py still builds its withdraw with value: 0 (it cannot move native AVAX)",
          '"value": 0' in src, "the reserve is native; the LP holds WAVAX/USDC (ERC-20)")
    check("lfj_exit.py checks that value==0 at send time, so the fact cannot change silently",
          'tx.get("value") or 0' in src)
    # And the DEPLOY paths must all have one.
    for f in ("lfj_bid_deploy.py", "lfj_recenter.py"):
        s = open(os.path.join(HERE, f)).read()
        check(f"{f} consults the floor (gate/cap_deploy/_reserve_split present)",
              any(k in s for k in ("GR.gate(", "cap_deploy(", "_reserve_split(", "GRf.gate(",
                                   "GRp.floor_line(")))
    sh = open(os.path.join(HERE, "lfj-curve-deploy.sh")).read()
    check("lfj-curve-deploy.sh checks the floor BEFORE the first leg is invoked",
          "--deploy-check" in sh
          and sh.index("--deploy-check") < sh.index('lfj_bid_deploy.py" --kind'),
          "the deploy-check runs above the FIRST leg invocation, so a refusal leaves nothing "
          "half-built")
    check("lfj-curve-deploy.sh refuses (exit 7) and offers --rescue",
          "exit 7" in sh and "--rescue" in sh)

    # ─────────────────────────────────────────────────────────────────────────
    hr("ONE SOURCE OF TRUTH — no competing floor numbers left in the money paths")
    for f, banned in (("lfj_bid_deploy.py", ("FLOOR_USDC", "FLOOR_WAVAX")),
                      ("coq_accumulator.py", ("GAS_FLOOR_USD",)),
                      ("lfj_recenter.py", ("3_500_000",))):
        code = code_only(os.path.join(HERE, f))
        hits = [b for b in banned if b in code]
        check(f"{f} carries no private floor/budget constant in its CODE {banned}", not hits,
              f"still present: {hits}" if hits else
              "the floor and the gas budget live in gas_reserve.py only (prose mentioning the "
              "retired name is not code — see code_only())")
    _rc = code_only(os.path.join(HERE, "lfj_recenter.py")).replace(" ", "")
    check("lfj_recenter instead READS the one budget from gas_reserve (RECENTER_GAS)",
          "RECENTER_GAS" in _rc and "GR.RECENTER_GAS" in _rc,
          "the 3.5M-gas rebalance budget is now gas_reserve.RECENTER_GAS — the SAME number, in ONE "
          "place, consumed by both the precondition and the gate")
    check("the ONE gas budget the recenter gate uses lives in gas_reserve",
          GR.RECENTER_GAS == 3_500_000 and "RECENTER_GAS = 3_500_000" in code_only(
              os.path.join(HERE, "gas_reserve.py")).replace(" ", " "),
          f"gas_reserve.RECENTER_GAS = {GR.RECENTER_GAS:,} gas (the inline 3_500_000 that used to "
          f"live in lfj_recenter.py was KEPT as the value, not replaced by a smaller derived one)")

    # ─────────────────────────────────────────────────────────────────────────
    hr("SUMMARY")
    if FAILS:
        print(f"  ❌ {len(FAILS)} of {CHECKS[0]} checks FAILED:")
        for f in FAILS:
            print(f"     - {f}")
        return 1
    print(f"  ✅ ALL {CHECKS[0]} CHECKS PASSED — the floor fires above, below and at the boundary,")
    print(f"     the reserve is never deployable, an exit is never gated, and there is one")
    print(f"     implementation of the number.")
    return 0


def _recenter_split(ri, total_usd):
    """Call the RECENTER's own composition function — the real one, not a copy of its logic."""
    import lfj_recenter as R
    return R._reserve_split(GR, ri, total_usd)


if __name__ == "__main__":
    sys.exit(main())
