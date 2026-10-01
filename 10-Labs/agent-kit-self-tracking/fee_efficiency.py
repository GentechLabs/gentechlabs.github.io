#!/usr/bin/env python3
"""Fee-efficiency rule — shape-aware, live, and wired to a 10-minute trigger.

RECOVERED FROM THE BRAIN (Jordan, 2026-09-21): "I had rules in place for this. The cron Job
should see the fee efficiency has been low for 10 mins and rebalance based on scenario."

The rule already existed in `/root/vaults/gentech/scripts/defi-rebalance.py`:
    bid-ask -> U-shape : EDGES pay, CENTER does not      (2*|n-0.5|*100)
    curve   -> bell    : CENTER pays, EDGES do not       ((1-2*|n-0.5|)*100)
    bands   -> >=70 hold & earn | 50-70 hold/reduced | <50 WATCH — LOW EFFICIENCY

WHY IT NEVER FIRED: the original file was hardcoded to a position we no longer hold --
RANGE_LOW=6.70 / RANGE_HIGH=6.88 while AVAX trades ~$11.13 and our real range is
$10.95-$11.47; AVAX_HELD=3.812 / USDC_HELD=18.73 against a book of 5.84 WAVAX + 47.78 USDC;
and it ran twice a day (1:00pm + 8:30pm EST), never on a 10-minute cadence. A rule pinned to a
stale range cannot detect a low-efficiency condition in the position we actually hold.

This module reads the LIVE range from the chain and the deploy config, so the rule is evaluated
against the position that exists rather than the one that was hardcoded.
"""
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, "/root/.hermes/profiles/gentech-treasury/scripts")

from web3 import Web3
from eth_abi import encode as abi_encode

import discover_positions as DP

PAIR = Web3.to_checksum_address("0x864d4e5Ee7318e97483DB7EB0912E09F161516EA")
DEPLOY_SH = "/root/.hermes/profiles/gentech-treasury/scripts/lfj-curve-deploy.sh"

# Bands — from the recovered rule.
BAND_HOLD = 75.0          # JORDAN, 2026-09-30: "we should shoot for always staying above 75% fee
                          # efficiency and rebalance if needed... unless we're in a bid-ask and we're
                          # gathering up the dip." Raised from 70 -> 75, and the TRIGGER now reads
                          # BAND_HOLD rather than BAND_REDUCED, so the band a book is shown in and the
                          # line that fires on it are THE SAME NUMBER. Before this, "Hold & Earn" began
                          # at 70 while the trigger fired below 50 — a book could be displayed as
                          # healthy and be governed by a line 20 points away.
                          # NOTE THE DISCREPANCY THIS SETTLED: Jordan recalled the old rule as 60;
                          # the code held 50. Neither number was written anywhere he could read.
BAND_REDUCED = 50.0

# Trigger: efficiency must be low for this long before acting.
LOW_EFF_MINUTES = 10.0
# ── DUTY-CYCLE TRIGGER (Jordan, 2026-09-23) ────────────────────────────────────────
# An UNINTERRUPTED streak can never fire on a price that oscillates through the low zone -- and
# oscillation is precisely when placement is worst. So the condition is also satisfied by a
# sustained DUTY CYCLE: low for >=LOW_DUTY_MIN of the last LOW_DUTY_WINDOW_SEC. Both tests are
# reported so the log shows which one fired.
LOW_DUTY_MIN = 0.70          # >=70% of samples low
LOW_DUTY_WINDOW_SEC = 20 * 60
LOW_EFF_THRESHOLD = BAND_HOLD             # JORDAN, 2026-09-30: stay above 75%.
                          # WAS BAND_REDUCED (50). The exemption below is what makes 75 safe:
                          # `is_low` also requires `not _nominal`, and at_designed_geometry() returns
                          # False for every shape EXCEPT bid-ask -- so a bid-ask correctly sitting at
                          # its junction (~33%) is exempt, while a CURVE is held to 75. That is
                          # exactly Jordan's carve-out: "unless we're in a bid-ask and we're gathering
                          # up the dip". Without it, a 75 line on a bid-ask would fire on every pass
                          # forever and the book would never stop rebuilding.

# ── TENANT-SCOPED STATE (fixed 2026-09-22) ──────────────────────────────────────────────
# This was ONE global file, `.fee-efficiency-state.json`, shared by every tenant. The
# low-streak is exactly the kind of state that must not be shared: Jordan's "low for 12
# minutes" and Dadrian's healthy read wrote the same keys, so whichever tenant ran last
# owned them. A sustained low on one book could be cleared by an unrelated read of the
# other, and the 10-minute requirement became untrackable. lfj_recenter.py already scopes
# ITS state per tenant (".steward-recenter-state-<tenant>.json"); this is the same rule.
# Filename carries the tenant so two tenants in the same window cannot collide.
def _state_file() -> str:
    import os
    t = (os.environ.get("STEWARD_TENANT") or "").strip().lower()
    if not t:
        try:
            import steward_identity as _si
            t = (getattr(_si, "tenant", None) and _si.tenant()) or "default"
        except Exception:
            t = "default"
    return f"/root/.hermes/profiles/gentech-treasury/scripts/.fee-efficiency-state-{t}.json"


STATE_FILE = _state_file()


def _w3():
    # POA middleware via the shared helper: Avalanche's eth_getBlock returns a 90-byte extraData
    # that web3's default validator rejects. Do not build a bare Web3(HTTPProvider(...)) here.
    return DP.make_w3("avalanche")


def _price_at(w3, bin_id: int) -> float:
    raw = int.from_bytes(w3.eth.call({
        "to": PAIR,
        "data": Web3.keccak(text="getPriceFromId(uint24)")[:4] + abi_encode(["uint24"], [bin_id])}), "big")
    return raw / 2 ** 128 * 1e18 / 1e6


def _legs_from_config(shape: str | None = None) -> dict:
    """Read the REAL leg geometry for a SHAPE — never assume it, never scrape it.

    2026-09-22: this used to regex the source text of lfj-curve-deploy.sh. That was fragile twice
    over — a second assignment line made the last match win (silently reporting the wrong shape),
    and when the geometry moved into lfj_shapes.py the regex found nothing at all and returned {}.
    The callers guard with `if {"BID_FAR","ASK_FAR"} <= legs.keys()`, so an empty dict did not
    crash: it just quietly stopped measuring. Ask the table instead.

    Keys keep their historical names (BID_NEAR/BID_FAR/ASK_NEAR/ASK_FAR) so callers are unchanged.
    """
    try:
        import lfj_shapes
    except Exception:
        return {}
    try:
        if shape is None:
            # No shape given: fall back to the tenant record, then to the wider book. Never guess
            # "curve" — picking the narrower geometry by accident under-reports the range.
            try:
                import json
                import os
                tp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tenants.json")
                with open(tp) as fh:
                    td = json.load(fh)
                rec = (td.get("tenants") or td)
                mine = os.environ.get("STEWARD_TENANT") or ""
                shape = (rec.get(mine) or {}).get("shape") if mine else None
            except Exception:
                shape = None
        w = lfj_shapes.widths(shape)
    except Exception:
        return {}
    return {
        "BID_NEAR": w["bid_near"], "BID_FAR": w["bid_far"],
        "ASK_NEAR": w["ask_near"], "ASK_FAR": w["ask_far"],
    }


def efficiency(price: float, low: float, high: float, shape: str) -> float:
    """The recovered rule, unchanged in meaning."""
    if high <= low:
        return 0.0
    if price < low or price > high:
        return 0.0
    n = (price - low) / (high - low)
    if shape == "bid-ask":
        e = 2 * abs(n - 0.5) * 100
    elif shape == "curve":
        e = (1 - 2 * abs(n - 0.5)) * 100
    else:  # spot
        e = 100 if abs(n - 0.5) < 0.1 else 50
    return min(100.0, max(0.0, e))


# ── A SHAPE'S STRUCTURAL BASELINE (fixed 2026-09-23) ─────────────────────────────────────────
# A check that cannot recognise a PASS is as unreadable as one that cannot fail.
#
# A bid-ask is DEPLOYED as BID_N below spot + ASK_N above it, so its designed spot position is
# the junction, n0 = BID_N / (BID_N + ASK_N). Our 15+30 geometry puts n0 at 33.3%. The formula
# above peaks at the EDGES, so a correctly-built bid-ask reads ~33% — and the low-efficiency
# trigger fires below 50%. The consequence, measured live on jordan: "efficiency 33.0% 🟠 WATCH
# — LOW FOR 94.93 MIN (trigger at 10 min) ✅ TRIGGERED" — withdraw + re-deploy, every cycle, on a
# book that was built exactly to spec. THE MACHINE WAS PUNISHING ITS OWN DESIGN, and that is the
# churn that kept flattening the wallet (see lfj_recenter.py §798 for the cooldown half of it).
#
# This does NOT redefine what the number MEANS — the truth is kept and still reported. It records
# the baseline so the caller can tell "at its designed geometry" (nominal) from "drifted off its
# designed geometry" (a real reason to act). Changing the SHAPE or the numbers is Jordan's call.
BID_ASK_DESIGNED_N = 15.0 / 45.0          # lfj_shapes.py: 15 bid + 30 ask = 45 bins


def designed_baseline(shape: str) -> float:
    """The efficiency a correctly-deployed book of this shape scores AT ITS DESIGNED GEOMETRY."""
    if shape == "bid-ask":
        return efficiency(BID_ASK_DESIGNED_N, 0.0, 1.0, "bid-ask")
    return 100.0                           # a centred curve is the peak of its own bell


def at_designed_geometry(e: float, shape: str, tol: float = 6.0) -> bool:
    """True when a reading is simply the shape sitting where it was BUILT to sit.

    -- ONE-SIDED TEST MADE THE BID-ASK TILE UNREADABLE (fixed 2026-09-24) -------------------
    This was `e >= designed_baseline(shape) - tol` -- NO CEILING. Every bid-ask reading ABOVE
    its baseline fell into the same bucket: a book placed perfectly at an edge (95%) printed
    the same words as one merely at its design point (33%). Jordan noticed the two shapes'
    descriptions were indistinguishable; the deeper fault was that the bid-ask had only TWO
    possible sentences, "Nominal" and "Watch", and nothing it could do well ever said so.

    A check that cannot recognise a PASS reads the same as one that cannot FAIL. Nominal now
    means what it says -- a WINDOW around the shape's designed baseline -- and above that
    window the book earns the Hold & Earn bands it deserves.
    """
    if shape != "bid-ask":
        return False
    base = designed_baseline(shape)
    return (base - tol) <= e <= (base + tol)


def band(e: float, shape: str | None = None) -> str:
    # ── A SPEC-BUILT BOOK MUST NOT READ AS WARNING (fixed 2026-09-23) ────────────────────────
    # The trigger no longer fires at the shape's structural baseline, but the BAND still printed
    # "🟠 WATCH — LOW EFFICIENCY" while the very next line said "no re-center needed" — a report
    # that argues with itself. A reader cannot tell "this is fine" from "this is fine for now",
    # which is how a real warning gets ignored. Say the truth: at its designed geometry, this is
    # the shape working as designed.
    # ── EACH SHAPE DESCRIBES ITSELF (Jordan, 2026-09-24) ──────────────────────────────
    # *"Can I get a different description for a curve versus a bid ask"*
    #
    # The verdict text used to be IDENTICAL for both shapes, and that is precisely what misreads:
    # 70% means "the price is near the CENTRE" for a curve but "near an EDGE" for a bid-ask. Same
    # number, opposite meaning, same words on the tile — so the reader must already know which
    # shape they own to know whether the sentence is good news.
    #
    # Each line now names the geometry that produced it, so the sentence is true standing alone:
    #   curve   -> earns at the CENTRE (a bell peaks at spot)
    #   bid-ask -> earns at the EDGES  (a U peaks away from spot)
    # A reader who knows nothing about shapes can still tell good from bad.
    _is_curve = (shape or "").strip().lower() == "curve"
    if shape is not None and at_designed_geometry(e, shape):
        return f"🟡 Nominal — {shape} at its designed geometry"
    if e >= BAND_HOLD:
        return ("🟢 Hold & Earn — price at the centre, where a curve collects"
                if _is_curve else
                "🟢 Hold & Earn — price at an edge, where a bid-ask collects")
    if e >= BAND_REDUCED:
        return ("🟡 Hold — drifting off centre, a curve earns less here"
                if _is_curve else
                "🟡 Hold — mid-U, away from the edges a bid-ask earns at")
    # -- A BID-ASK ABOVE ITS DESIGN POINT MUST NOT READ AS A WARNING (2026-09-24) -----------
    # The nominal window created an inversion: 33% printed "Nominal" while 40% printed "Watch",
    # so the tile got WORSE as the book got better placed. A verdict that moves the wrong way
    # with its input is unreadable at a glance -- the reader has to hold the geometry in their
    # head to know which sentence is good news. Between the design window and the hold band the
    # honest word is that the book is out-performing what it was built for.
    if (not _is_curve) and shape is not None and e > designed_baseline(shape) + 6.0:
        return "🟡 Better than designed — closer to an edge, collecting more"
    return ("🟠 Watch — far from centre; a curve collects little here"
            if _is_curve else
            "🟠 Watch — sitting at the trough; a bid-ask collects nothing here")


def _our_bins(w3, active: int, depth: int = 400, amounts: dict | None = None) -> list[int]:
    """The bin ids WE actually hold liquidity in — read from the book, not from config.

    Added 2026-09-22. `measure()` used to build its range from the configured leg geometry
    around the CURRENT active bin, i.e. `lo = price(active - BID_FAR)`, `hi = price(active +
    ASK_FAR)`. That makes the range a window CENTRED ON SPOT BY CONSTRUCTION, so spot always
    landed at ~50% of it, sat on the peak of the bell, and scored ~99% — from bin 8363351 to
    8363431 (80 bins of drift) the reading never moved off 99.4%. A metric that re-centres on
    whatever it is measuring cannot report the condition it exists to detect, so the 10-minute
    low-efficiency trigger had NEVER fired. That is Jordan's "why isn't there a rebalance?":
    the trigger was reading a number that is structurally incapable of going low.

    Read the real position instead. Uses discover_positions._batch_eth_call: sequential calls
    over a +/-400 window hung past the watchdog's timeout (the Sep 7 lesson), and a single
    oversized batch is answered with HTTP 500 and degrades to all-zeros, which renders as
    "no position" — a false negative that would silently disable this trigger again.
    """
    try:
        import steward_identity as _si
        who = Web3.to_checksum_address(_si.wallet())
    except Exception:
        return []
    if not who:
        return []
    bal_sel = "0x00fdd58e"                      # balanceOf(address,uint256)
    addr_hex = who.lower().replace("0x", "")
    out: list[int] = []
    STEP = 150                                  # chunk size the public RPC tolerates
    for start in range(-depth, depth + 1, STEP):
        chunk = list(range(start, min(start + STEP, depth + 1)))
        if not chunk:
            continue
        ids = [active + o for o in chunk if active + o >= 0]
        if not ids:
            continue
        reads = DP._batch_eth_call("avalanche", PAIR, bal_sel, addr_hex, ids)
        if reads is None:
            continue                            # skip a failed chunk, never claim "empty"
        for b_id, bal in zip(ids, reads):
            if bal and int(bal) > 0:
                out.append(b_id)
                # AMOUNTS ARE THE MEASUREMENT (2026-09-30): this loop already reads every per-bin
                # balance to FIND the bins, so the data the shape classifier needs was fetched and
                # discarded. Filled only when the caller asks -- every existing path is unchanged.
                if amounts is not None:
                    amounts[b_id] = int(bal)
    return out


def measure(shape: str = "bid-ask", w3=None) -> dict:
    w3 = w3 or _w3()
    active = int.from_bytes(w3.eth.call(
        {"to": PAIR, "data": Web3.keccak(text="getActiveId()")[:4]}), "big")
    legs = _legs_from_config()
    # ── THE RANGE MUST BE THE DEPLOYED POSITION, NOT A WINDOW AROUND SPOT ─────────────────
    # Prefer the bins we actually hold. Fall back to the configured geometry ONLY when we hold
    # nothing (so the caller still gets a number) and SAY which one was used.
    _amounts: dict = {}
    held = _our_bins(w3, active, amounts=_amounts)
    if held:
        lo = _price_at(w3, min(held))
        # ONE BIN HIGHER, and the reason matters. A DLMM bin `id` covers the price band
        # [p(id), p(id+1)) -- so the position's true TOP is the UPPER EDGE of the top bin,
        # p(max+1), not p(max). Using p(max) understates our own range by one bin, which
        # puts spot nearer the top than it is and depresses the efficiency reading.
        # defi_hub_data.py has always used max+1 (its own note: "price_of(max) is the LOWER
        # edge of the top bin; the range's true top is the upper edge, one binStep higher").
        # Two components, two definitions, two numbers for the same book -- the exact
        # false-value family we keep killing. Aligned 2026-09-23: the hub was right.
        hi = _price_at(w3, max(held) + 1)
        geom = f"ACTUAL deployed bins {min(held)}..{max(held)} ({len(held)} bins)"
        # ── THE SHAPE COMES FROM THE BINS WE JUST READ (Jordan, 2026-09-23) ────────────────
        # `shape` arrives as a parameter — normally from tenants.json via _tenant_shape(). BOTH
        # tenant records said "curve" while BOTH books were bid-asks on chain (told apart by the
        # gap at spot). The efficiency was therefore computed with the wrong rule: a curve's bell
        # peaks at the CENTRE, a bid-ask's U peaks at the EDGES. A stale label does not merely
        # mislabel a dashboard — it corrupts the number the rebalance rule acts on, which is the
        # silent-wrongness class this file has already been burned by twice today.
        # We have the bins in hand. Read the truth instead of trusting the label. Jordan:
        # "It should follow on chain data."
        _h = sorted(held)
        # ── THE SHAPE COMES FROM THE BIN COUNT, NOT FROM A HOLE (fixed 2026-09-25) ──────────
        # This was `_geom_shape = "bid-ask" if _gaps else "curve"` -- the SAME gap test as
        # lfj_recenter.py and the THIRD copy of it. A gap at spot is not a shape: a bid-ask is a
        # 1-bin hole at the junction of a 45-bin book, while a 25-bin CURVE whose second leg
        # landed one bin off has a 3-bin hole and is still a curve (that is exactly the book on
        # chain today). Classifying it as a bid-ask does not merely mislabel the tile -- it
        # computes the number with the OTHER shape's formula, and the two formulas are opposites:
        #     curve     e = (1 - 2|n-0.5|) * 100     peaks at the CENTRE
        #     bid-ask   e =      2|n-0.5|  * 100     peaks at the EDGES
        # A perfectly centred curve (n=0.5) therefore read 0.0% "🟠 WATCH — sitting at the trough",
        # and its LOW-FOR-N-MIN duty trigger armed a withdraw/re-deploy: the reader was punishing
        # the book for sitting exactly where it was built to sit. lfj_shapes.shape_of_bins is the
        # ONE classifier; ask it instead of re-deriving one from a hole.
        try:
            import lfj_shapes as _ls
            # MASS FIRST, COUNT AS FALLBACK (2026-09-30). shape_of_bins names a book by its BIN
            # COUNT, and the count is not the shape -- it has now failed three times (the gap test,
            # the headline count, the count with adaptive variants). Today a 40-bin BELL read
            # "bid-ask" and scored 1.0% while the hub, using the label, correctly read 98.9%:
            # two readers, two answers, one book. shape_of_mass reads WHERE THE MONEY SITS, which
            # is width-independent, so both readers agree by measurement instead of by label.
            _geom_shape = _ls.shape_of_mass(_amounts) or _ls.shape_of_bins(_h)
        except Exception as _e:                 # a classification we cannot make is not a guess
            _geom_shape = shape
            print(f"  ⚠️  SHAPE CLASSIFIER UNAVAILABLE ({type(_e).__name__}: {_e}) — keeping the "
                  f"label '{shape}'. THIS EFFICIENCY NUMBER IS UNVERIFIED.")
        # ── AN EMPTY ANSWER MEANS "MATCHES NO LEGAL GEOMETRY" (2026-09-27) ─────────────────────
        # shape_of_bins now returns "" when the bin count is more than 2 off EVERY geometry this
        # system can deploy. That is a PARTIAL book -- a leg sold off, a position partly drained --
        # not a coin-flip to resolve. Previously min() named it after the nearer design point, which
        # is how jordan's 12-bin partial book was labelled a CURVE by the engine while the page
        # labelled it a BID-ASK. The record label wins here because a partial book was BUILT from
        # one; the geometry simply cannot confirm which any more. Say so and keep scoring.
        if _geom_shape and shape != _geom_shape:
            print(f"  ⚠️  shape label '{shape}' disagrees with the chain: {len(_h)} bins "
                  f"is a {_geom_shape.upper()}. Using the geometry, not the label.")
            shape = _geom_shape
        elif not _geom_shape:
            print(f"  ℹ️  {len(_h)} bins matches no deployable geometry (curve 25/17, bid-ask 45/31) "
                  f"— this is a PARTIAL book. Keeping the label '{shape}' and scoring with it; "
                  f"the bin count alone cannot confirm the shape.")
    elif {"BID_FAR", "ASK_FAR"} <= legs.keys():
        # ── NO POSITION IS NOT A HEALTHY POSITION (fixed 2026-09-23) ────────────────────────
        # This fallback centred the range on spot, so spot was ALWAYS at ~50% and the bell
        # ALWAYS scored ~99.4% — a perfectly healthy reading from an EMPTY book. Both tenants
        # sat flat in their wallets while this reported "99.4% 🟢 Hold & Earn", which is why
        # nobody caught it. That is the whole false-value family in one line: a metric built
        # around the thing it measures cannot see that the thing is gone.
        #
        # If we hold nothing there IS no efficiency to measure, and inventing one is worse
        # than refusing. The caller gets an error it can act on (idle-capital / re-deploy)
        # instead of a number that says everything is fine.
        raise RuntimeError(
            "no LFJ position found for this tenant — the book is FLAT. There is no efficiency "
            "to measure; a fallback range would report a healthy number for an empty wallet.")
    else:
        lo, hi = _price_at(w3, active - 20), _price_at(w3, active + 20)
        geom = "DEGRADED — no position and no config; symmetric +/-20 (unreliable)"
    spot = _price_at(w3, active)
    # SANITY GATE. A garbage range read ($1.00 low against an $11.16 spot) previously produced a
    # confident "1.0% efficiency" instead of an error -- the same false-value family as the rest
    # of today. A range more than 50% away from spot is a BAD READ, not a finding, and it must
    # refuse rather than report.
    if hi <= lo or lo <= 0 or not (spot * 0.5 <= lo <= spot * 1.5) or not (spot * 0.5 <= hi <= spot * 1.5):
        raise RuntimeError(
            f"implausible range read: low={lo:.4f} high={hi:.4f} spot={spot:.4f} "
            f"— refusing to compute an efficiency from a bad read")
    n = ((spot - lo) / (hi - lo) * 100) if hi > lo else 0.0
    e = efficiency(spot, lo, hi, shape)
    return {"ts": time.time(), "shape": shape, "activeId": active, "spot": spot,
            "low": lo, "high": hi, "posPct": n, "efficiency": e, "band": band(e, shape),
            "geometry": geom, "legs": legs}


def evaluate(shape: str = "bid-ask", now: float | None = None) -> dict:
    """Measure and decide, persisting the low-efficiency streak across runs.

    The 10-minute requirement needs MEMORY across invocations -- a single reading cannot tell
    you how long a condition has held. State is kept in a small file so a cron every few minutes
    can enforce a sustained condition rather than reacting to one sample.
    """
    now = now or time.time()
    m = measure(shape)
    # NAME COLLISION FIX: `low` here means "efficiency is low", but measure() uses `low` for the
    # range-low PRICE. Assigning m["low"] = low overwrote the price with a boolean, which printed
    # as "$1.0000" while posPct (computed earlier from the real price) stayed correct -- an
    # internally contradictory report. Keep the names distinct.
    # ── A LOW READING AT THE SHAPE'S DESIGNED GEOMETRY IS NOT A LOW READING (fixed 2026-09-23) ─
    # `is_low` gated the 10-minute trigger. Our bid-ask is built 15 bid + 30 ask, so spot sits at
    # the junction (33.3%) by construction and the raw reading is ~33% — under the 50% threshold
    # for ever. Measured live on jordan: "LOW FOR 94.93 MIN (trigger at 10 min) ✅ TRIGGERED",
    # so the machine withdrew and re-deployed a book that was built exactly to spec, every cycle.
    # Excluding the structural baseline here is what stops the tigger firing on the shape's own
    # design. The number is still reported unchanged; only the automatic ACT is withheld.
    _nominal = at_designed_geometry(m["efficiency"], shape)
    is_low = m["efficiency"] < LOW_EFF_THRESHOLD and not _nominal
    try:
        st = json.load(open(STATE_FILE))
    except Exception:
        st = {}
    if is_low:
        first = st.get("lowSince") or now
        held_min = (now - first) / 60.0
    else:
        first, held_min = None, 0.0
    # ── THE STREAK MUST SURVIVE AN OSCILLATING TAPE (Jordan, 2026-09-23) ────────────────────
    # Jordan: "I care more about the auto rebalancer... the watcher would automatically know which
    # one to use and I wouldn't have to say too much" and "it just didn't feel like we were in the
    # pool that much today."
    #
    # The trigger above required an UNINTERRUPTED low streak. Price oscillating in and out of the
    # low zone resets `held_min` to zero on every pass, so a book could sit in the wrong place
    # earning ~20% all day while the trigger that exists for exactly that stayed silent. **A rule
    # that cannot fire on the tape it was written for.** (Same family as the 2-day volatility
    # memory that could not see its own move had finished.)
    #
    # Fix: judge the DUTY CYCLE -- what fraction of a rolling window was low -- instead of an
    # unbroken run. A book that is badly placed 70%+ of the last 20 minutes IS badly placed, even
    # if it briefly crossed back each time. Both readings are still reported, so the log says
    # which test passed and a human can see the oscillation rather than a misleading clean streak.
    try:
        hist = [h for h in (st.get("samples") or [])
                if isinstance(h, list) and len(h) == 2 and now - h[0] <= LOW_DUTY_WINDOW_SEC]
    except Exception:
        hist = []
    hist.append([now, 1 if is_low else 0])
    window_min = (now - hist[0][0]) / 60.0 if len(hist) > 1 else 0.0
    duty = (sum(h[1] for h in hist) / len(hist)) if hist else 0.0
    duty_held = bool(window_min >= LOW_EFF_MINUTES and duty >= LOW_DUTY_MIN)

    st.update({"lowSince": first, "lastEfficiency": m["efficiency"],
               "lastShape": shape, "lastTs": now, "samples": hist[-240:],
               "lastBand": m["band"], "heldMinutes": round(held_min, 2),
               "dutyPct": round(duty * 100, 1), "dutyWindowMin": round(window_min, 2),
               "dutyHeld": duty_held})
    try:
        json.dump(st, open(STATE_FILE, "w"), indent=2)
    except Exception:
        pass
    m["isLow"] = is_low
    m["lowForMinutes"] = round(held_min, 2)
    m["dutyPct"] = round(duty * 100, 1)
    m["dutyWindowMin"] = round(window_min, 2)
    # Trigger on EITHER test: an unbroken run (the strict case) or a sustained duty cycle (the
    # oscillating tape). Reporting both means the reason is always visible in the log.
    m["triggered"] = bool((is_low and held_min >= LOW_EFF_MINUTES) or duty_held)
    # ── THE PIVOT RULE (Jordan, 2026-09-26) ─────────────────────────────────────────────────────
    # Jordan: *"there should be a rule about fee efficiency for the different liquidity SHAPES ...
    # when I looked on the web page we were in the middle which means we're not earning as much at
    # all and we would need to pivot to a curve IMMEDIATELY."*
    #
    # The 10-minute gate above exists to stop a book churning on a momentary dip. It should not
    # make the treasury WAIT when the reading is STRUCTURALLY meaningless for the shape we hold:
    #   * a BID-ASK sitting in the middle of its range is a book that cannot earn — a bid-ask is a
    #     U, it is paid at the edges and collects nothing in the trough. Waiting 10 minutes there
    #     is 10 minutes of a provably-idle position, and no second reading can change the geometry.
    #     This is the same argument the watchdog already accepts for OUT OF RANGE ("that is
    #     arithmetic, not a trend, and no second reading can change it").
    #   * a CURVE off-centre is the mirror case: a bell earns at its centre, and its edge is where
    #     it earns least.
    # The gate still governs every AMBIGUOUS low reading — only the structural case is immediate.
    # This is a PIVOT, not an extra re-centre: the caller may change SHAPE, which is the thing the
    # old rule could never do (it computed the alternative and re-deployed the same shape anyway).
    _structurally_dead = bool(is_low and shape == "bid-ask" and _trough(m))
    _structurally_off = bool(is_low and shape == "curve" and not _centred(m))
    m["pivot_triggered"] = bool(_structurally_dead or _structurally_off)
    m["pivot_why"] = (
        "a bid-ask is sitting in the middle of its range — it is paid at the edges and collects "
        "nothing in the trough, so this is geometry, not a trend, and no second reading changes it"
        if _structurally_dead else
        "a curve is off its centre — a bell earns at the centre and its edge is where it earns "
        "least, so the range is misplaced" if _structurally_off else None)
    m["scenario"] = scenario(m, shape)
    return m


def _trough(m: dict, lo: float = 0.35, hi: float = 0.65) -> bool:
    """Is the spot inside the middle band where a bid-ask (a U) cannot earn?"""
    n = m.get("posPct")
    return bool(n is not None and lo <= (n / 100.0) <= hi)


def _centred(m: dict, tol: float = 0.15) -> bool:
    """Is the spot near the centre, where a curve (a bell) earns?"""
    n = m.get("posPct")
    return bool(n is not None and abs(n / 100.0 - 0.5) <= tol)


def scenario(m: dict, shape: str) -> dict:
    """What to DO — the 'rebalance based on scenario' half of the rule.

    A low reading is not one condition, so it does not get one action. Where the price sits
    inside the range decides which — AND THE SHAPE DECIDES WHICH WAY ROUND:

      * CURVE is a BELL: it peaks at the CENTRE. Mid-range is where it EARNS MOST, and its
        edges are where it earns least. So a curve that is mid-range is working as designed,
        and a curve that is off-centre is the one to re-centre.
      * BID-ASK is a U: it pays at the EDGES and earns nothing in the trough. So a bid-ask
        that is mid-range is the one to re-centre (toward an edge) or switch to curve.

    FIXED 2026-09-23. The mid-range branch used to return "re-centre so spot sits toward an
    edge" with NO shape test, so it gave BID-ASK advice to a CURVE. On Jordan's book that
    meant: sitting on the peak of the bell at 72.6% efficiency, and the tool recommending a
    move that would slide the position off its own peak. Advice that is right for one shape
    and backwards for the other is the false-value family again — it reads as confident and
    it points the wrong way.
    """
    n = m["posPct"]
    e = m["efficiency"]
    if m["spot"] < m["low"] or m["spot"] > m["high"]:
        return {"action": "REBALANCE — OUT OF RANGE", "detail":
                "price is outside the position; it is earning nothing at all",
                "shape": shape}

    centered = abs(n - 50) <= 20

    if shape == "curve":
        if centered:
            return {"action": "HOLD",
                    "detail": (f"mid-range ({n:.0f}%) is the PEAK of a curve's bell — "
                               f"this is the shape working as designed ({e:.0f}%)"),
                    "shape": shape}
        return {"action": "RE-CENTRE",
                "detail": (f"off-centre ({n:.0f}%) — a curve earns least at its edges; "
                           f"re-centre to put spot back on the peak"),
                "shape": shape}

    # bid-ask: a U pays at the edges
    if centered:
        # ── AT ITS DESIGNED GEOMETRY IS NOT A FAILURE (fixed 2026-09-23) ────────────────────
        # Our bid-ask is BUILT 15 bid + 30 ask, so spot sits at the junction (33.3%) by
        # construction — inside the `centered` band by ~3 points. Without this test the machine
        # told a spec-built book to "SWITCH SHAPE or RE-CENTRE" on every pass, for ever, because
        # its own geometry guarantees the reading can never clear the 50% trigger. That is the
        # churn (see the baseline block above `efficiency()`). Sitting at the junction means both
        # legs straddle spot and the book is in play — the same thing the curve branch calls
        # "the shape working as designed".
        if at_designed_geometry(e, shape):
            return {"action": "HOLD",
                    "detail": (f"spot at the bid/ask junction ({n:.0f}%) — this is the shape "
                               f"working as designed ({e:.0f}%; a {shape} is built as "
                               f"BID 15 + ASK 30, so this reading is its structural baseline, "
                               f"not a low reading)"),
                    "shape": shape, "nominal": True}
        alt_e = efficiency(m["spot"], m["low"], m["high"], "curve")
        if alt_e > e:
            # ── DO NOT PROMISE A SWITCH THAT CANNOT HAPPEN (fixed 2026-09-23) ──────────────────
            # This said "SWITCH SHAPE or RE-CENTRE". But the REGIME owns the shape (see the
            # one-shape-authority rule), so with a regime-driven bid-ask the efficiency trigger
            # canNOT switch anything: the run withdraws, the switch sets the side, the regime
            # re-imposes bid-ask, and the book is re-deployed as the shape it already was. The
            # advice named an action the path could not perform, which is how a withdrawal that
            # achieves nothing reads as a fix. Say only what will actually happen.
            return {"action": "RE-CENTRE",
                    "detail": (f"dragged to {n:.0f}% of the range, where a {shape} earns least "
                               f"({e:.0f}%). Re-centre so spot returns to the bid/ask junction. "
                               f"(A curve would read {alt_e:.0f}% here — but the REGIME owns the "
                               f"shape, so a switch happens only if the regime changes; this "
                               f"trigger cannot override it.)"),
                    "shape": shape, "altShape": "curve", "altEfficiency": alt_e}
        return {"action": "RE-CENTRE",
                "detail": f"mid-range ({n:.0f}%) — re-centre so spot sits toward an edge",
                "shape": shape}
    return {"action": "RE-CENTRE",
            "detail": f"off-centre ({n:.0f}%) and low ({e:.0f}%) — the range is mis-placed",
            "shape": shape}


REGISTRY = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"


def _tenant_shape(tenant: str | None = None) -> str | None:
    """The shape the TENANT RECORD declares — or None when it declares nothing.

    tenants.json shape_field_note: "Consumers MUST treat a missing value as UNKNOWN rather
    than defaulting — a defaulted shape makes every downstream efficiency reading describe a
    position nobody verified."

    The CLI used to do the exact thing that rule forbids: `shape = sys.argv[1] if ... else
    "bid-ask"`. So a human running `fee_efficiency.py` against Jordan's CURVE got bid-ask
    advice ("re-centre so spot sits toward an edge" — right for a U-shape, wrong for a bell)
    and, worse, whatever landed in argv[1] became the shape: passing `--tenant jordan` set
    the shape to the literal string "--tenant". Returns None rather than guessing.
    """
    import os, json
    t = tenant or os.environ.get("STEWARD_TENANT") or "jordan"
    try:
        with open(REGISTRY) as fh:
            reg = json.load(fh)
        return (reg.get("tenants", {}).get(t, {}) or {}).get("shape") or None
    except Exception:
        return None


def main():
    import argparse, os
    ap = argparse.ArgumentParser(description="Fee efficiency for a tenant's live LFJ book.")
    ap.add_argument("--tenant", default=os.environ.get("STEWARD_TENANT") or "jordan",
                    help="tenant id in tenants.json (default: $STEWARD_TENANT or jordan)")
    ap.add_argument("--shape", default=None,
                    help="override the shape; omit to use the shape the TENANT RECORD declares")
    args = ap.parse_args()
    os.environ["STEWARD_TENANT"] = args.tenant
    # ── SET BOTH, NOT JUST THE LABEL (fixed 2026-09-27) ──────────────────────────────────────
    # This line used to set STEWARD_TENANT alone. `steward_identity.wallet()` consults
    # STEWARD_WALLET and then the profile config — it never read the tenant label — so every
    # tenant's book read resolved the DEFAULT wallet. Measured: `--tenant dadrian` printed
    # "ACTUAL deployed bins 8363337..8363348 (12 bins)" — jordan's book — and scored 50.2% for
    # dadrian, whose real 25-bin book scores 52.4%. posture.py was already patched for exactly
    # this; the fix is now ALSO in steward_identity._from_env() so the other nine scripts that
    # set only the label are covered too. Belt and braces on purpose: this is the read that
    # decides whether a two-person treasury reports honest numbers.
    try:
        import steward_identity as _SI
        os.environ["STEWARD_WALLET"] = _SI.wallet()
    except Exception as _e:
        print(f"  ⚠️  could not resolve {args.tenant!r}'s wallet ({type(_e).__name__}: {_e}) — "
              f"this read may describe the default wallet, not {args.tenant!r}.")
    globals()["STATE_FILE"] = _state_file()

    shape = args.shape or _tenant_shape(args.tenant)
    if not shape:
        print(f"  FEE EFFICIENCY — {args.tenant}")
        print(f"    ⛔ tenant '{args.tenant}' declares no shape in tenants.json.")
        print("    Refusing to score: a defaulted shape describes a position nobody verified.")
        return 2
    m = evaluate(shape)
    print(f"  FEE EFFICIENCY — {args.tenant} as {m['shape']}   ({m['geometry']})")
    print(f"    range ${m['low']:.4f} .. ${m['high']:.4f}   spot ${m['spot']:.4f}"
          f"   at {m['posPct']:.1f}% of range")
    print(f"    efficiency {m['efficiency']:.1f}%   {m['band']}")
    print(f"    low for {m['lowForMinutes']:.2f} min (trigger at {LOW_EFF_MINUTES:.0f} min)"
          f"{'   ✅ TRIGGERED' if m['triggered'] else ''}")
    print(f"    scenario: {m['scenario']['action']} — {m['scenario']['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
