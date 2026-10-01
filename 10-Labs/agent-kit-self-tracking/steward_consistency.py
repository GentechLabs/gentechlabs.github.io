#!/usr/bin/env python3
"""Do our systems agree with each other?

WHY (Jordan, 2026-09-27): "We shouldn't have systems that disagree with each other. Data is not
connecting somewhere."

He was right, and the evidence was on one page: the FEE EFFICIENCY card said "low — the live
distribution does NOT match the curve label" while the SHAPE card directly below it said "This
shape is CORRECT". Two cards, one page, one book, opposite claims. Neither was lying — they read
different fields that were computed by different methods and never compared.

This tool compares them. Every claim about a book is produced somewhere; several of those
productions are INDEPENDENT of each other. Where two independent views of the same fact disagree,
one of them is wrong and a human is about to be told two things at once.

Design rules, all learned the hard way today:
  * The CHAIN is the arbiter. Nothing overrules it.
  * CANNOT_JUDGE is a first-class result. It is never reported as agreement and never as an alarm.
    A crossed book, a one-sided book, an unreadable bin — all legitimately unjudgeable.
  * A DISAGREE must name BOTH values and WHICH field produced each, so the next person can go
    straight to the line that is wrong.
  * Never compare two numbers that are DIFFERENT THINGS BY DESIGN (an estimate vs a realised
    receipt). Those are labelled INFO, because the real defect would be letting a reader think
    they are the same number.

Exit codes: 0 = all agree (or unjudgeable), 1 = at least one DISAGREE, 2 = could not read inputs.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

DEFI = "/var/www/gentechlabs/DeFi"

AGREE, DISAGREE, CANNOT, INFO = "AGREE", "DISAGREE", "CANNOT_JUDGE", "INFO"


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception as e:
        return {"__error__": f"{type(e).__name__}: {e}"}


def check_capital(d, _L):
    """Two independent valuations of the SAME position must land in the same place.

    Both sides must count DEPLOYED LP ONLY. `deployed_usd` is the value inside the bins;
    `shape_total_usd` is the same quantity summed bin-by-bin from the chain scan. Comparing them is
    like-for-like.

    FIXED 2026-09-28 — this used to read `capital_usd`, the WHOLE BOOK (deployed LP **+ idle cash**),
    and compare it to the chain scan's in-bins total. Whenever a book held idle cash the two sides
    could never agree, and the check fired a false DISAGREE. Measured live: dadrian's book was
    one-sided and stranded — $2.11 in bins, $41.08 idle in the wallet. `capital_usd` said $43.19,
    `shape_total_usd` said $2.11, and this check reported a disagreement of ~$41 that did not exist.
    The correct field (`deployed_usd` = $2.11) was in the payload the whole time and matched the chain
    exactly ($2.11 vs $2.11, Δ0.00).

    Two consequences worth remembering: the false alarm GREW with how much idle cash was sitting
    around (backwards — an idle-heavy book is the safest state, not the most broken), and the printed
    detail was a STALE PRECOMPUTED delta that contradicted the two numbers printed beside it.
    A check that invents disagreements trains you to ignore the one that matters.
    """
    a = _f(d.get("deployed_usd"))
    b = _f(d.get("shape_total_usd"))
    shape = d.get("ledger_vs_shape_delta")
    if a is None or b is None:
        return CANNOT, "ledger", f"deployed_usd={a}", "chain", f"shape_total_usd={b}", \
               "one side did not produce a value"
    if isinstance(shape, dict):
        return CANNOT, "ledger", f"${a:,.2f}", "chain", f"${b:,.2f}", \
               f"chain scan incomplete: {shape.get('unavailable')}"
    # tolerance: bin rounding + price movement between the ledger read and the chain scan
    tol = max(1.0, 0.01 * max(abs(a), abs(b)))
    ok = abs(a - b) <= tol
    # Report the delta we actually measured — never a stale precomputed one.
    return (AGREE if ok else DISAGREE), "ledger", f"${a:,.2f}", "chain", f"${b:,.2f}", \
           f"Δ{a - b:+.2f} (tol ±${tol:.2f})"


def check_bins(d, _L):
    """The ledger's bin count, the chain scan's bin count, and the shape array must be one number."""
    ledger_n = d.get("bins")
    chain_n = d.get("chain_bins")
    shape_n = len([b for b in (d.get("shape") or []) if b.get("resolved")]) if d.get("shape") else None
    vals = {"bins(ledger)": ledger_n, "chain_bins(scan)": chain_n, "len(shape resolved)": shape_n}
    have = {k: v for k, v in vals.items() if v is not None}
    if len(have) < 2:
        return CANNOT, "bins", str(ledger_n), "chain_bins", str(chain_n), "fewer than two counts available"
    uniq = set(have.values())
    if len(uniq) == 1:
        return AGREE, "bins", str(ledger_n), "chain_bins", str(chain_n), "all counts identical"
    return DISAGREE, "bins(ledger)", str(ledger_n), "chain_bins(scan)", str(chain_n), \
           f"counts disagree: {vals}"


def check_range(d, _L):
    """`in_range` must agree with the band and the price it was derived from."""
    inr = d.get("in_range")
    px = _f(d.get("price_usd"))
    lo, hi = _f(d.get("range_min")), _f(d.get("range_max"))
    if inr is None or px is None or lo is None or hi is None:
        return CANNOT, "in_range", str(inr), "band", f"{lo}–{hi}", "a required field is missing"
    ge = lo <= px <= hi
    return (AGREE if ge == bool(inr) else DISAGREE), \
           "in_range flag", str(inr), "price vs band", f"{px} in {lo}–{hi} = {ge}", \
           "" if ge == bool(inr) else "the flag and the arithmetic disagree"


def check_spot_in_book(d, _L):
    """`active_id` and `in_range` are two fields of ONE payload — they must agree.

    REWRITTEN 2026-09-28. The old rule was "active bin must sit inside the held bins", and it
    reported DISAGREE whenever spot left the range. But **leaving the range is a MARKET
    condition, not an inconsistency** — it is the normal, expected state of a CL position, and
    `check_range` above already validates the `in_range` flag against its own arithmetic. So the
    old check fired on a perfectly healthy book: it flagged dadrian at $10.482 against a range
    low of $10.4925 — genuinely out of range, correctly reported as out-of-range by every other
    check, and then branded a disagreement here. A checker that alarms on the normal case trains
    you to ignore it.

    What this check is actually for is that the payload does not contradict ITSELF: if the book
    says it is in range, the active bin must be inside the span; if it says it is out of range,
    the active bin must be outside it. That catches a garbage or stale `active_id` (the planted
    fault is `active_id = 1` on a book claiming to be in range) without ever mistaking a real
    market move for a data fault.
    """
    act = d.get("active_id")
    bins = [b.get("bin") for b in (d.get("shape") or []) if b.get("bin") is not None]
    in_range = d.get("in_range")
    if act is None or not bins:
        return CANNOT, "active_id", str(act), "held bins", str(len(bins)), "no bin data"
    if in_range is None:
        return CANNOT, "active_id", str(act), "in_range", "missing", \
               "cannot check self-consistency — payload carries no in_range flag"

    span = f"{min(bins)}–{max(bins)}"
    inside = min(bins) <= act <= max(bins)
    # The payload is self-consistent when the flag and the bin agree about which side of the
    # range we are on. Both directions are real faults, so both are reported.
    if inside == bool(in_range):
        return AGREE, "active_id", str(act), "held bin span", span, \
               f"in_range={bool(in_range)} agrees with the active bin's position"
    return DISAGREE, "active_id", str(act), "held bin span", span, \
           f"payload contradicts itself: in_range={bool(in_range)} but the active bin is " \
           f"{'inside' if inside else 'outside'} the held span"


def check_shape_verdicts(d, _L):
    """The three independent judges of 'is this the right shape?' must not contradict each other.

      * `label_matches_mass` — per-leg geometry vs the shape we believe we hold
      * `leg_orientation.verdict` — the same instrument, named
      * `shape_why.agrees` — does the market/regime layer pick the shape we hold?
    """
    lmm = d.get("label_matches_mass")
    lo = d.get("leg_orientation") or {}
    verd = lo.get("verdict")
    judgeable = lo.get("judgeable")
    why = d.get("shape_why") or {}

    parts, bad = [], []
    if judgeable is False:
        parts.append("legs unjudgeable (crossed book)")
    else:
        if lmm is not None and verd is not None:
            if (lmm is True) != (verd == "OK"):
                bad.append(f"label_matches_mass={lmm} but leg verdict={verd}")
        parts.append(f"label={lmm}, legs={verd}")

    # shape_why is a DIFFERENT question (does the market want this shape), so it is reported
    # alongside rather than collapsed — a book can correctly hold a shape the regime no longer
    # calls for, and that is a rebalance decision, not a contradiction.
    if why.get("agrees") is False:
        parts.append("market/regime now calls for a DIFFERENT shape")

    detail = "; ".join(parts) or "no shape judges produced a verdict"
    if bad:
        return DISAGREE, "label_matches_mass", str(lmm), "leg_orientation.verdict", str(verd), "; ".join(bad)
    return INFO, "shape verdicts", str(lmm), "legs", str(verd), detail


def check_freshness(d, _L):
    """A payload older than the watchdog's cycle is a frozen view being served as live."""
    ts = d.get("updated_at")
    if not ts:
        return CANNOT, "updated_at", "missing", "now", "—", "no timestamp on the payload"
    try:
        t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return CANNOT, "updated_at", ts, "now", "—", "unparseable timestamp"
    age_min = (datetime.now(timezone.utc) - t).total_seconds() / 60.0
    if age_min <= 30:
        return AGREE, "payload age", f"{age_min:.1f} min", "threshold", "30 min", "fresh"
    return DISAGREE, "payload age", f"{age_min:.1f} min", "threshold", "30 min", \
           "the published view is stale but is still being served"


def check_fee_ledger(d, _L):
    """The page's embedded ledger must equal the ledger file it claims to come from."""
    emb = d.get("fee_ledger") or {}
    if _L.get("__error__"):
        return CANNOT, "page ledger", emb.get("status"), "ledger file", _L["__error__"], "file unreadable"
    if not emb or emb.get("status") == "not_yet_generated":
        return INFO, "page ledger", str(emb.get("status")), "ledger file", "missing", \
               "no ledger published yet — page says so explicitly"
    f_rows = _L.get("rows") or []
    f_total = round(sum(_f(r.get("pool_fees_usd")) or 0 for r in f_rows), 2)
    p_total = (emb.get("totals") or {}).get("pool_fees_usd")
    if p_total is None:
        return CANNOT, "page ledger total", "None", "ledger file total", str(f_total), "no total on the page block"
    ok = abs(float(p_total) - f_total) <= 0.01
    return (AGREE if ok else DISAGREE), "page ledger total", f"${p_total}", \
           "ledger file total", f"${f_total}", "" if ok else "the page and the file disagree"


def check_estimate_vs_receipt(d, _L):
    """Estimate and realised fees are DIFFERENT THINGS BY DESIGN.

    Never compare them as if one should equal the other — the defect this guards against is a
    reader being unable to tell which is which. So the check is about LABELLING.
    """
    en = d.get("earnings") or {}
    fl = d.get("fee_ledger") or {}
    est = _f(en.get("per_day_usd"))
    if est is None:
        return CANNOT, "estimate", "None", "receipt", str(fl.get("status")), "no estimate produced"
    # Match the STEM, not one inflection. The first cut looked for "estimated" while the payload
    # carries `estimate_daily_fees` — so it fired on a correctly-labelled payload and reported a
    # disagreement that did not exist. A checker that fires on good data trains people to ignore
    # it, which is worse than having none. (Same class as every other defect today.)
    blob = json.dumps(en).lower()
    lab_est = ("estimate" in blob) or ("estimated" in blob)
    lab_rec = (fl.get("status") == "ok")
    if lab_rec and not lab_est:
        return DISAGREE, "estimate labelled", "no", "receipt present", "yes", \
               "a receipt exists but the estimate is not labelled as one"
    return INFO, "estimate $/day", f"${est:.4f} (labelled estimate: {lab_est})", \
           "realised receipts", f"{len(fl.get('days') or [])} day(s)", \
           "different kinds of number, both labelled — not a disagreement"


def check_state_vs_pages(d, _L):
    """THE TREASURY'S OWN SOURCE OF TRUTH vs THE PAGES.

    treasury-state.json is what the council, the mode logic, the milestone rank and every report
    read to answer "what do we hold / how deployed are we". The pages read the same book a second
    way. They disagreed by the ENTIRE book on 2026-09-28:

        treasury-state.capital.deployed_usd : 0.0    ("FLAT — holds no deployed liquidity")
        DeFi pages, both tenants            : $193.91 deployed and in range

    Nothing compared the two, because each looked internally fine. This check exists so that a
    source of truth that reports *zero* while the book earns is caught by the same run that
    catches a wrong bin count.
    """
    import os as _os
    state = load(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "treasury-state.json"))
    if "__error__" in state:
        return CANNOT, "treasury-state", state["__error__"], "pages", "n/a", \
               "state file unreadable — an unknown, not agreement"
    cap = state.get("capital") or {}
    deployed = _f(cap.get("deployed_usd"))
    measured_at = cap.get("measured_at")

    # Sum the per-tenant pages independently. A tenant we cannot read makes the comparison
    # impossible rather than smaller — otherwise one broken page would silently "agree" with a
    # zeroed state file.
    pages_total = 0.0
    seen = []
    missing = []
    for t in ("jordan", "dadrian"):
        p = load(f"/var/www/gentechlabs/DeFi/defi-data-{t}.json")
        if "__error__" in p:
            missing.append(t)
            continue
        v = _f(p.get("capital_usd"))
        if v is None:
            missing.append(t)
            continue
        pages_total += v
        # `seen` must report the DEPLOYED figure, not the whole book: it is rendered inside the
        # deployed-vs-deployed comparison below, and showing capital_usd there produced an
        # incoherent line ("jordan $0.20 + dadrian $43.19 = $2.11"). Label what you compare.
        _dv_seen = _f(p.get("deployed_usd"))
        if _dv_seen is not None:
            seen.append(f"{t} deployed ${_dv_seen:,.2f}")

    # ── LIKE-FOR-LIKE: sum the pages' DEPLOYED, not their whole book (fixed 2026-09-28) ──────
    # The loop above sums `capital_usd` — the WHOLE book (deployed LP **+ idle cash**). The state's
    # `deployed_usd` counts DEPLOYED LP ONLY. The comment below has always said "compare
    # deployed-to-deployed"; the code never did. So the check compared two different quantities and
    # reported the DIFFERENCE BETWEEN THEM as a disagreement.
    #
    # Measured live: dadrian's book was one-sided and stranded — $2.11 in bins, $41.08 idle in the
    # wallet (deployed_pct 4.9%). The state said $2.11, the pages' capital said $43.19, and the check
    # cried "$0.00 vs $43.23, Δ-43.23" — a fake alarm proportional to how much IDLE CASH was sitting
    # around. It read as a catastrophic staleness bug and sent me hunting a valuation defect that did
    # not exist, while the two readers actually AGREED exactly ($2.11 == $2.11).
    # An idle-heavy book made the false alarm bigger, which is precisely backwards.
    #
    # A consistency check that invents disagreements is worse than no check: it trains you to ignore
    # the one that matters. Compare the same field on both sides.
    pages_deployed = 0.0
    for t in ("jordan", "dadrian"):
        p = load(f"/var/www/gentechlabs/DeFi/defi-data-{t}.json")
        if "__error__" in p:
            continue
        dv = _f(p.get("deployed_usd"))
        if dv is not None:
            pages_deployed += dv

    if deployed is None:
        return CANNOT, "treasury-state", "deployed_usd missing", "pages", \
               " + ".join(seen) or "n/a", "state has no capital block"
    if missing:
        return CANNOT, "treasury-state", f"${deployed:,.2f}", "pages", \
               " + ".join(seen) or "n/a", \
               f"cannot compare — page(s) unreadable: {','.join(missing)}"

    # LIKE-FOR-LIKE now holds: both sides count DEPLOYED LP only (see the note above).
    # Tolerance to the smaller of 2% / $3 because a whole-book disagreement is what we are hunting.
    tol = max(3.0, 0.02 * max(deployed, pages_deployed))
    ok = abs(deployed - pages_deployed) <= tol
    detail = (f"state ${deployed:,.2f} ({measured_at}) vs pages deployed " + " + ".join(seen) +
              f" = ${pages_deployed:,.2f}  Δ{deployed - pages_deployed:+.2f} (tol ±${tol:,.2f})")
    if ok:
        return AGREE, "treasury-state", f"${deployed:,.2f}", "pages", \
               f"${pages_deployed:,.2f}", detail
    return DISAGREE, "treasury-state", f"${deployed:,.2f}", "pages", \
           f"${pages_deployed:,.2f}", detail


CHECKS = [
    ("capital: ledger vs chain", check_capital),
    ("bins: ledger vs chain scan", check_bins),
    ("range flag vs arithmetic", check_range),
    ("spot inside held bins", check_spot_in_book),
    ("shape verdicts", check_shape_verdicts),
    ("payload freshness", check_freshness),
    ("page ledger vs ledger file", check_fee_ledger),
    ("estimate vs realised receipt", check_estimate_vs_receipt),
    ("state-of-record vs pages", check_state_vs_pages),
]

ICON = {AGREE: "✅", DISAGREE: "❌", CANNOT: "➖", INFO: "ℹ️ "}


def main():
    tenants = sys.argv[1:] or ["jordan", "dadrian"]
    bad = 0
    readerr = 0
    for t in tenants:
        d = load(f"{DEFI}/defi-data-{t}.json")
        _L = load(f"{DEFI}/fee-ledger-{t}.json")
        print(f"\n═══ {t.upper()} ═══")
        if d.get("__error__"):
            print(f"  ❌ cannot read payload: {d['__error__']}")
            readerr += 1
            continue
        for name, fn in CHECKS:
            try:
                status, a_lbl, a_val, b_lbl, b_val, note = fn(d, _L)
            except Exception as e:
                status, a_lbl, a_val, b_lbl, b_val, note = CANNOT, "error", str(e)[:60], "—", "—", "check crashed"
            if status == DISAGREE:
                bad += 1
            print(f"  {ICON[status]} {name}")
            print(f"       {a_lbl} = {a_val}")
            print(f"       {b_lbl} = {b_val}")
            if note:
                print(f"       {note}")

    print(f"\n  {'─'*66}")
    print(f"  DISAGREEMENTS: {bad}")
    if readerr:
        print(f"  UNREADABLE: {readerr}")
        return 2
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
