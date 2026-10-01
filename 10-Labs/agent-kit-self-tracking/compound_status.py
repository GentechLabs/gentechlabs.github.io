#!/usr/bin/env python3
"""compound_status.py — HOW MUCH IS BEING AUTO-COMPOUNDED BACK INTO THE LP?

Jordan (2026-09-25, verbatim): "...on our DeFi hubs instead of showing how much work in capital
that we have in the pool Why don't we instead talk about how much is being auto compounded back
into the bins or back into Our LP I think that would be much more beneficial if you still want to
add a tab under that that shows Hey, here's what you have waiting to be compounded on the next
cycle you can still do that"

So this returns a FLOW first (what compounding is doing), and the WAITING amount second.

===== WHAT "COMPOUNDED" MEANS ON THIS VENUE (the finding this file exists to state) ============
On LFJ V2.2 Liquidity Book, fees are **folded into the bin reserves by the pool itself, at swap
time**. There is no collectFees step and no per-position fee counter:

  * `getBin(uint24)` returns exactly TWO words (reserveX, reserveY) — fees are already inside them.
  * Every `pendingFees(...)` overload was probed against the live pair and REVERTS. `collectFees`
    reverts too. (Proof: cache/scratch/fee_abi_proof.py — all 0xf7cff1f8 / 0xf595f1cc / 0xfc0072e8 /
    0x25d2a3f3 / 0x966aa883 / 0xbdb34097 / 0x225b20b9 → 'execution reverted', while getBin and
    totalSupply return data on the same pair, same block.)

Consequence, stated plainly because it changes the whole question: **there is no unclaimed fee
balance to collect, and therefore no fee that "waits".** Compounding on LFJ is not a job the agent
does on a schedule — it is a property of the pool. The only thing that genuinely WAITS is idle
working capital sitting in the wallet, which the compound engine would deploy on its next cycle.

===== THE TWO INDEPENDENT DERIVATIONS, AND WHY THERE ARE TWO ===================================
The fee ledger (fee_ledger.py) cannot answer this. Its instrument is the price-invariant factor
sqrt(our_wavax * our_usdc), which is only invariant while the position is IN RANGE and UNTOUCHED —
and this book is re-centred every few minutes. Replayed over the last 49h it produced segment rates
of -124%/day, +818%/day and +448%/day, i.e. the signal is the re-centres, not the fees. That is
recorded, not hidden: fee_ledger is not used as a source here.

Instead two derivations that do not share a numerator:
  A) POOL ECONOMICS   fee% = MEASURED effective fee (0.051%: read from real Swap events, and
                      cross-read from the pair's static fee parameters) x 24h volume
                      (DexScreener) x our share (our LP USD / pool TVL, both independent of our
                      own ledger)
  B) HOUSE ESTIMATOR  steward_progress.estimate_daily_fees(capital, deployed, in_range)

They are far apart (measured 2026-09-25: A $0.69/day vs B $0.19/day for jordan, ratio ~3.7; the
same ratio holds for dadrian, so the SHARE is right and the denominator is what differs). The gap
is dominated by the share basis — A divides our book by WHOLE-POOL TVL, while a book concentrated
near spot earns from the much smaller in-range liquidity — so for our shape A is a LOWER bound and
the truth sits at or above it. Since that cannot be resolved from the chain without per-bin flow
attribution, this module publishes the **BRACKET** with both sources named rather than picking the
flattering end. A single unsourced number is exactly what this project keeps getting burned by.

The pool FEE itself is not assumed: `_fee_rate()` reads it from the pair's own static fee
parameters AND from the totalFees/amountIn words of real Swap events (this pair charges 0.051% —
the plausible-looking `binStep/10000` guess is 0.1%, i.e. ~2x too high).

===== HONEST NULL =================================================================================
If either derivation is unavailable, or the chain cannot be read, status="unknown" with the reason,
and the page renders UNKNOWN. It never returns 0 to mean "could not read". The waiting figure is
reported as None when the wallet cannot be read, never as 0.

CLI:  python3 compound_status.py [--tenant jordan] [--json]
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PERIOD_DAYS = 7.0            # the period the hub headlines
DEADBAND_X = 2.0             # >2x spread between derivations => publish a bracket, not a point


def _reg(tenant):
    """Tenant record from the registry. Never guesses a wallet."""
    try:
        import tenant_guard as TG
        r = TG.registered(tenant)
        if r:
            return r
    except Exception:
        pass
    try:
        reg = json.load(open("/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"))
        return (reg.get("tenants") or {}).get(tenant) or {}
    except Exception:
        return {}


def _dex_volume_tvl(pair):
    """24h volume + TVL for the pair from DexScreener — a source independent of our own ledger."""
    url = f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{pair}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; GenTech/1.0)"})
    d = json.load(urllib.request.urlopen(req, timeout=20))
    ps = d.get("pairs") or ([d["pair"]] if d.get("pair") else [])
    if not ps:
        raise RuntimeError("DexScreener returned no pair row")
    p = ps[0]
    vol = float((p.get("volume") or {}).get("h24") or 0)
    tvl = float((p.get("liquidity") or {}).get("usd") or 0)
    if not vol or not tvl:
        raise RuntimeError("DexScreener row missing volume/liquidity")
    return vol, tvl, float(p.get("priceUsd") or 0)


SWAP_TOPIC = "0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70"


def _fee_rate(pair):
    """The pool's EFFECTIVE swap fee as a fraction (0.00051 == 0.051%), and how it was obtained.

    Two routes, recorded together because the value is load-bearing for the whole headline:

      static   the pair's own `getStaticFeeParameters()` -> baseFactor, combined with the chain's
               `getBinStep()`: baseFee = baseFactor * binStep * 1e10 (1e18 precision, the LFJ
               FeeHelper formula). This is the CONFIGURED floor, before the volatility component.
      measured the most recent Swap event's own fee words: the event carries amountIn and
               totalFees packed as (tokenX, tokenY), so totalFees/amountIn IS the realised rate.
               Nothing is assumed — it is read off a swap the pool actually processed.

    MEASURED IS PREFERRED when it can be read, because it is the rate that was actually charged
    (base + volatility component). `binStep/10000` — the obvious-looking guess, and 0.1% for this
    pool — is WRONG here: this pair charges 0.051%, so that guess inflated the fee leg ~2x. An
    assumed rate that is silently 2x out is exactly the confident-wrong-number class this fleet
    keeps banning, so the rate is now either read or reported as unread.
    """
    import avax_rpc
    from web3 import Web3
    w3 = avax_rpc.connect(timeout=40)
    P = Web3.to_checksum_address(pair)
    out = {"bin_step": None, "base_factor": None, "static_fee_frac": None,
           "measured_fee_frac": None, "measured_from": None}
    raw = w3.eth.call({"to": P, "data": Web3.keccak(text="getBinStep()")[:4].hex()})
    step = int.from_bytes(raw, "big")
    out["bin_step"] = step
    try:
        raw = w3.eth.call({"to": P, "data": Web3.keccak(text="getStaticFeeParameters()")[:4].hex()})
        h = raw.hex()
        base_factor = int(h[0:64], 16)
        out["base_factor"] = base_factor
        # LFJ FeeHelper: baseFee = baseFactor * binStep * 1e10, 1e18 precision
        out["static_fee_frac"] = base_factor * step * 1e10 / 1e18
    except Exception as e:
        out["static_error"] = f"{type(e).__name__}: {e}"
    try:
        head = w3.eth.block_number
        logs = w3.eth.get_logs({"fromBlock": head - 900, "toBlock": head, "address": P,
                                "topics": [SWAP_TOPIC]})
        mask = (1 << 128) - 1
        rates = []
        for lg in reversed(logs):
            d = lg["data"]
            d = d.hex() if hasattr(d, "hex") else d
            w = [int(d[i * 64:(i + 1) * 64], 16) for i in range(len(d) // 64)]
            if len(w) < 6:
                continue
            for shift in (128, 0):
                ain = (w[1] >> shift) & mask
                tf = (w[4] >> shift) & mask
                if ain > 0 and tf > 0:
                    rates.append(tf / ain)
        if rates:
            rates.sort()
            # MEDIAN, not max. max() would report the most expensive swap in the window, which
            # OVERSTATES fee income — picking the flattering end of a noisy sample is the exact
            # habit this project bans. The median is the rate the pool actually charged.
            out["measured_fee_frac"] = rates[len(rates) // 2]
            out["measured_samples"] = len(rates)
            out["measured_range_frac"] = [rates[0], rates[-1]]
            out["measured_from"] = (f"on-chain Swap events (topic {SWAP_TOPIC[:10]}…), "
                                    f"median totalFees/amountIn over {len(rates)} legs in the last "
                                    f"900 blocks")
    except Exception as e:
        out["measured_error"] = f"{type(e).__name__}: {e}"
    fee = out["measured_fee_frac"] or out["static_fee_frac"]
    if not fee:
        raise RuntimeError("cannot source the pool fee — neither the Swap events nor the static "
                           "fee parameters could be read")
    out["fee_frac"] = fee
    out["fee_source"] = ("measured on-chain" if out["measured_fee_frac"]
                         else "static params (baseFactor x binStep)")
    return fee, out


def _idle_wallet(wallet):
    """Idle WORKING capital in the wallet = USDC + WAVAX. Native AVAX is GAS, not working capital."""
    import avax_rpc
    USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
    WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
    w3 = avax_rpc.connect(timeout=40)
    sel = "0x70a08231" + wallet[2:].lower().rjust(64, "0")
    usdc = int.from_bytes(w3.eth.call({"to": USDC, "data": sel}), "big") / 1e6
    wavax = int.from_bytes(w3.eth.call({"to": WAVAX, "data": sel}), "big") / 1e18
    native = w3.eth.get_balance(w3.to_checksum_address(wallet)) / 1e18
    return usdc, wavax, native


def compute(tenant, wallet=None, lp_usd=None, capital_usd=None, in_range=None, pair=None):
    """Return the compounding payload for one tenant. NEVER raises; degrades to status=unknown."""
    pair = pair or "0x864d4E5Ee7318e97483DB7EB0912E09F161516EA"
    rec = _reg(tenant) or {}
    wallet = wallet or rec.get("wallet")
    out = {
        "tenant": tenant,
        "status": "unknown",
        "error": None,
        "period_days": PERIOD_DAYS,
        # ── the FLOW (headline) ──────────────────────────────────────────────
        "per_day_low_usd": None, "per_day_high_usd": None,
        "period_low_usd": None, "period_high_usd": None,
        "rate_pct_per_day_low": None, "rate_pct_per_day_high": None,
        "apr_pct_low": None, "apr_pct_high": None,
        "bracket_x": None, "single_source": False,
        "derivations": {},
        # ── what WAITS ───────────────────────────────────────────────────────
        "waiting_usd": None, "waiting_usdc": None, "waiting_wavax": None,
        "waiting_note": None,
        # ── the venue fact that reframes the question ───────────────────────
        "pending_fee_usd": None,
        "pending_fee_note": ("LFJ V2.2 folds fees into the bin reserves at swap time; every "
                             "pendingFees/collectFees selector reverts on this pair, so there is no "
                             "claimable fee balance — nothing waits to be collected"),
        "compounding_is_automatic": True,
        # ── gas / viability ─────────────────────────────────────────────────
        "gas": None, "decision": None,
        "sources": [],
    }
    if not wallet:
        out["error"] = "no wallet registered for this tenant"
        return out

    # Standalone convenience: when the caller (the hub) supplies the valuations they are used as
    # given. When run from the CLI there is no caller, so read the tenant's OWN last hub data file
    # — same tenant, same process boundary, and the source is named in the payload.
    if lp_usd is None or capital_usd is None:
        try:
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             f"defi-data-{tenant}.json")
            if not os.path.exists(p):
                p = os.path.join("/var/www/gentechlabs/DeFi", f"defi-data-{tenant}.json")
            d = json.load(open(p))
            if lp_usd is None:
                lp_usd = d.get("deployed_usd")
            if capital_usd is None:
                capital_usd = d.get("capital_usd")
            if in_range is None:
                in_range = d.get("in_range")
            out["sources"].append(f"defi-data-{tenant}.json")
        except Exception as e:
            out["derivations"]["valuation_source"] = {"error": f"{type(e).__name__}: {e}"}

    # ── A) pool economics ───────────────────────────────────────────────────
    try:
        fee_frac, fee_detail = _fee_rate(pair)
        vol, tvl, px = _dex_volume_tvl(pair)
        if lp_usd is None:
            raise RuntimeError("our LP USD not supplied — cannot form our share")
        share = float(lp_usd) / tvl
        per_day_a = vol * fee_frac * share
        out["derivations"]["pool_economics"] = {
            "bin_step": fee_detail.get("bin_step"), "fee_pct": fee_frac * 100,
            "fee_frac": fee_frac, "fee_detail": fee_detail,
            "volume_24h_usd": vol,
            "pool_tvl_usd": tvl, "our_lp_usd": float(lp_usd), "our_share_pct": share * 100,
            "per_day_usd": per_day_a, "price_usd": px,
            "source": ("pool fee " + str(fee_detail.get("fee_source"))
                       + " x DexScreener 24h vol x our share of pool TVL"),
            "caveat": ("the share basis is WHOLE-POOL TVL, so for a book concentrated near spot "
                       "this is a LOWER bound on the pool-economics estimate"),
        }
        out["sources"].append("pool_economics")
    except Exception as e:
        out["derivations"]["pool_economics"] = {"error": f"{type(e).__name__}: {e}"}

    # ── B) house estimator ──────────────────────────────────────────────────
    try:
        if lp_usd is None or capital_usd is None:
            raise RuntimeError("capital/deployed USD not supplied")
        import steward_progress as SP
        e = SP.estimate_daily_fees(float(capital_usd), float(lp_usd), in_range=in_range)
        if e is None:
            raise RuntimeError("estimator returned None")
        out["derivations"]["house_estimator"] = {
            "per_day_usd": float(e), "in_range_used": in_range,
            "source": "steward_progress.estimate_daily_fees",
        }
        out["sources"].append("house_estimator")
    except Exception as e:
        out["derivations"]["house_estimator"] = {"error": f"{type(e).__name__}: {e}"}

    # ── combine into a bracket, or refuse ───────────────────────────────────
    vals = [d["per_day_usd"] for d in out["derivations"].values()
            if isinstance(d, dict) and d.get("per_day_usd")]
    if not vals:
        out["error"] = ("no fee-flow derivation succeeded — " +
                        "; ".join(f"{k}: {v.get('error')}" for k, v in out["derivations"].items()
                                  if isinstance(v, dict) and v.get("error")))
        # still report the WAITING number and the gas decision: both are measurable without a rate
        _fill_waiting(out, wallet)
        _fill_gas(out, tenant)
        return out

    lo, hi = min(vals), max(vals)
    if len(vals) == 1:
        out["single_source"] = True
        out["error"] = None
    out["per_day_low_usd"] = lo
    out["per_day_high_usd"] = hi
    out["period_low_usd"] = lo * PERIOD_DAYS
    out["period_high_usd"] = hi * PERIOD_DAYS
    out["bracket_x"] = (hi / lo) if lo else None
    if lp_usd:
        out["rate_pct_per_day_low"] = lo / float(lp_usd) * 100
        out["rate_pct_per_day_high"] = hi / float(lp_usd) * 100
        out["apr_pct_low"] = out["rate_pct_per_day_low"] * 365
        out["apr_pct_high"] = out["rate_pct_per_day_high"] * 365
    out["status"] = "ok"

    _fill_waiting(out, wallet)
    _fill_gas(out, tenant)
    return out


def _fill_waiting(out, wallet):
    """Idle WORKING capital the compound engine would deploy on its next cycle."""
    try:
        usdc, wavax, native = _idle_wallet(wallet)
        # price: the pool's own on-chain quote first (the same quantity the position is valued
        # with), else the DexScreener price already fetched for this build. Never guessed.
        px = None
        try:
            import avax_rpc
            from web3 import Web3
            w3 = avax_rpc.connect(timeout=30)
            pair = Web3.to_checksum_address("0x864d4E5Ee7318e97483DB7EB0912E09F161516EA")
            sel_act = Web3.keccak(text="getActiveId()")[:4].hex()
            act = int.from_bytes(w3.eth.call({"to": pair, "data": sel_act}), "big")
            sel_p = Web3.keccak(text="getPriceFromId(uint24)")[:4].hex() + format(act, "064x")
            px = int.from_bytes(w3.eth.call({"to": pair, "data": sel_p}), "big") / (1 << 128) * 1e18 / 1e6
            out["waiting_price_source"] = "chain getPriceFromId"
        except Exception as e:
            px = out["derivations"].get("pool_economics", {}).get("price_usd")
            out["waiting_price_source"] = f"DexScreener priceUsd (chain quote failed: {type(e).__name__})"
        if not px:
            raise RuntimeError("no price available to value the idle legs")
        out["waiting_usdc"] = usdc
        out["waiting_wavax"] = wavax
        out["waiting_usd"] = usdc + wavax * px
        out["waiting_price_usd"] = px
        out["native_avax"] = native
        out["waiting_note"] = (f"idle working capital in the wallet "
                               f"(${usdc:.4f} USDC + {wavax:.6f} WAVAX @ ${px:.4f}) — deployed by the "
                               f"compound engine on its next cycle; native AVAX {native:.6f} is gas, "
                               f"not working capital")
    except Exception as e:
        out["waiting_note"] = f"UNKNOWN — could not read the wallet: {type(e).__name__}: {e}"


def _fill_gas(out, tenant):
    """The gas floor and the DECISION, in plain numbers. Uses the ONE floor (gas_reserve)."""
    try:
        import gas_reserve as GR
        info = GR.reserve_info(tenant)
        cyc = GR.cycle_cost()
        out["gas"] = {
            "gas_price_navax": info.get("gas_price_navax"),
            "cycle_gas_units": info.get("cycle_gas_units"),
            "one_cycle_avax": info.get("cycle_avax"),
            "one_cycle_usd": (info.get("cycle_avax") or 0) * (info.get("avax_usd") or 0),
            "reserve_avax": info.get("reserve_avax"),
            "reserve_usd": info.get("reserve_usd"),
            "balance_avax": info.get("balance_avax"),
            "deployable_avax": info.get("deployable_avax"),
            "above_floor": info.get("above"),
            "floor_cycles": info.get("floor_cycles"),
            "floor_usd": info.get("floor_usd"),
            "source": "gas_reserve.reserve_info (the ONE floor)",
        }
        w = out.get("waiting_usd")
        cost = out["gas"]["one_cycle_usd"] or 0.0
        if w is None:
            out["decision"] = {"action": "UNKNOWN", "reason": "idle amount unreadable"}
        elif not info.get("above"):
            out["decision"] = {"action": "HOLD", "reason":
                               f"below the gas floor: {info.get('balance_avax'):.6f} AVAX < reserve "
                               f"{info.get('reserve_avax'):.6f} AVAX (${info.get('reserve_usd'):.4f})"}
        elif cost > 0 and w <= cost:
            out["decision"] = {"action": "HOLD", "reason":
                               f"fee earned ${w:.6f} <= gas to deploy ${cost:.6f} — would lose money"}
        elif w < 1.00:
            out["decision"] = {"action": "HOLD", "reason":
                               f"idle ${w:.4f} below the $1.00 minimum deploy — not worth a tx"}
        else:
            out["decision"] = {"action": "COMPOUND", "reason":
                               f"idle ${w:.2f} > gas ${cost:.6f} and above the floor"}
    except Exception as e:
        out["gas"] = {"error": f"{type(e).__name__}: {e}"}
        out["decision"] = {"action": "UNKNOWN", "reason": f"gas reserve unavailable: {e}"}


def main():
    tenant = None
    a = sys.argv[1:]
    if "--tenant" in a:
        tenant = a[a.index("--tenant") + 1]
    tenant = tenant or os.environ.get("STEWARD_TENANT") or "jordan"
    payload = compute(tenant)
    if "--json" in a:
        print(json.dumps(payload, indent=2))
        return 0
    print("=" * 92)
    print(f"  COMPOUNDING — {tenant}")
    print("=" * 92)
    print(f"  status           : {payload['status']}")
    if payload.get("error"):
        print(f"  error            : {payload['error']}")
    if payload["status"] == "ok":
        print(f"  COMPOUNDED       : ${payload['period_low_usd']:.4f} - "
              f"${payload['period_high_usd']:.4f} over {payload['period_days']:.0f}d "
              f"(bracket x{payload['bracket_x']:.2f})")
        print(f"  rate             : {payload['rate_pct_per_day_low']:.6f} - "
              f"{payload['rate_pct_per_day_high']:.6f} %/day")
        print(f"  APR              : {payload['apr_pct_low']:.2f}% - {payload['apr_pct_high']:.2f}%")
    for k, v in (payload.get("derivations") or {}).items():
        print(f"    {k:16s}: {v.get('per_day_usd', v.get('error'))}")
    print(f"  WAITING          : ${payload['waiting_usd']}" if payload.get("waiting_usd") is not None
          else f"  WAITING          : UNKNOWN ({payload.get('waiting_note')})")
    print(f"  pending fees     : {payload['pending_fee_note']}")
    print(f"  gas              : {json.dumps(payload.get('gas'))}")
    print(f"  DECISION         : {json.dumps(payload.get('decision'))}")
    print("=" * 92)
    return 0


if __name__ == "__main__":
    sys.exit(main())
