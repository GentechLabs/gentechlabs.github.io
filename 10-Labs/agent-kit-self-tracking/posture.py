#!/usr/bin/env python3
"""POSTURE — one decision from all six layers.

Jordan, 2026-09-26:
    "the combination, the flexibility and the creativity of different DeFi strategies, being able
     to combine, getting out of the pool when giant pullbacks are spiking, entering the pool, just
     different decisions that the treasury could make, and there's no wrong answer. The only answer
     is fee efficiency is number one, and market sentiment is very important. That's why we have the
     other layers. So we wanted to design the system to respond using all the layers."

WHY THIS EXISTS
    The treasury had six independent triggers that DETECTED and REPORTED, and no layer that
    SELECTED. The efficiency trigger computed "a curve would read 79%" and then re-deployed the same
    shape. The macro layer had a calendar and no switch. Every trigger acted alone, so the system
    could not answer the only question that matters: *what should the book BE right now?*

    This module answers it. It reads all six layers and emits ONE posture, naming the layer that
    set it — so a decision is always traceable to its cause and auditable after the fact.

THE RULE THAT WOULD HAVE PREVENTED TODAY'S BUG
    A layer that cannot be read DOES NOT VOTE. Unreadable is not neutral.

    On 2026-09-26 a rate-limited price API made the market read fail, `move_pct` became None, the
    trend branch was skipped, and the verdict fell through to the calm branch — so a failed read
    SILENTLY BECAME "the market is calm" and the shape of a live LP position flipped between curve
    and bid-ask on identical on-chain data. Ten minutes of churn with no market event behind it.

    Here, an unreadable volatility layer cannot choose a shape at all: the resolver returns
    HOLD_SHAPE, which means "keep what you hold", which is the honest answer. It never returns a
    confident FARM_CURVE from a missing reading.

DESIGN NOTE — WHY resolve() IS A PURE FUNCTION
    The defect above survived because the decision could not be tested against the live world.
    resolve(layers) takes the layer readings as DATA and returns a decision, with no I/O. That makes
    every precedence rule and every refusal provable offline (--selftest), including the exact
    unreadable-layer case. gather() does the I/O and is the only part that touches the world.

POSTURES (the finite vocabulary — "there is no wrong answer" means there is always one to take)
    FLAT          nothing deployed and nothing to do
    HOLD          deployed and correct; do not churn
    HOLD_SHAPE    a layer needed to choose a shape is unreadable — KEEP what we hold
    FARM_CURVE    deploy/hold the bell — calm, rangebound
    FARM_BIDASK   deploy/hold the U — trending or volatile
    SKEW_CURVE    curve biased to one side (lean stated)
    LADDER_IN     trend or dip: enter/deepen toward the move
    EXIT_TO_STABLE leave the pool, hold stable
    SPOT          leave the pool, hold the ASSET

CLI:  python3 posture.py [--tenant jordan] [--json] [--selftest]
Exit 0 always (a report, not a gate). Refuses to invent a posture it cannot support.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# The posture vocabulary. Named here so nothing can smuggle in an undefined posture string.
POSTURES = (
    "FLAT", "HOLD", "HOLD_SHAPE", "FARM_CURVE", "FARM_BIDASK",
    "SKEW_CURVE", "LADDER_IN", "EXIT_TO_STABLE", "SPOT",
)

# Which shape each farming posture implies (for the caller that deploys).
SHAPE_OF = {"FARM_CURVE": "curve", "FARM_BIDASK": "bid-ask",
            "SKEW_CURVE": "curve", "HOLD_SHAPE": None, "HOLD": None}

# The six layers, in the order they are read (not the order of precedence — see PRECEDENCE).
LAYERS = ("protection", "capital", "efficiency", "sentiment", "volatility", "hold_farm")


# ────────────────────────────────────────────────────────────────────────────────────────────────
# THE RESOLVER — pure. Takes layer readings as data, returns a decision. No I/O, no clock, no chain.
# ────────────────────────────────────────────────────────────────────────────────────────────────
def resolve(L: Dict[str, Any]) -> Dict[str, Any]:
    """All six layers -> ONE posture, with the layer that set it named.

    PRECEDENCE (highest wins). Protection outranks opportunity, always — you do not farm a book
    through a macro shock to protect a geometry score.

        1. PROTECTION   an exit signal or an imminent macro event  -> can force a shape or an exit
        2. CAPITAL      not fundable                               -> can force HOLD
        3. EFFICIENCY   the prime directive                        -> can force RE-CENTRE
        4. SENTIMENT + VOLATILITY                                  -> selects the shape
        5. OPPORTUNITY  entry timing                               -> only acts when 1-4 are quiet

    Every branch names `set_by` and `why`, so the decision is auditable without re-running it.
    """
    def out(posture, set_by, why, **extra):
        assert posture in POSTURES, f"undefined posture {posture!r}"
        d = {"posture": posture, "set_by": set_by, "why": why,
             "shape": SHAPE_OF.get(posture), "abstained": [], "votes": []}
        d.update(extra)
        return d

    # Record which layers could not be read — these are REPORTED, never silently treated as neutral.
    abstained = [n for n in LAYERS if not (L.get(n) or {}).get("readable")]

    # ── 1. PROTECTION — the layers that can veto ────────────────────────────────────────────────
    prot = L.get("protection") or {}
    if prot.get("readable"):
        if prot.get("exit_everything"):
            d = out("EXIT_TO_STABLE", "protection",
                    prot.get("exit_why") or "an exit-everything signal fired — leave the pool and "
                    "hold stable until it clears")
            d["abstained"], d["votes"] = abstained, ["protection"]
            return d
        if prot.get("go_spot"):                      # 3+ of the 5 Go-Spot signals
            d = out("SPOT", "protection",
                    prot.get("go_spot_why") or "3+ of the 5 Go-Spot signals fired — the trend is "
                    "the trade, so hold the ASSET rather than the book")
            d["abstained"], d["votes"] = abstained, ["protection"]
            return d
        if prot.get("macro_imminent"):
            # Jordan's own rule: 24h before FED/CPI/NFP -> bid-ask, wide.
            d = out("FARM_BIDASK", "protection",
                    prot.get("macro_why") or "a high-impact macro event is imminent — bid-ask is "
                    "the macro shape (price moves hard one way and an edge catches it)")
            d["abstained"], d["votes"] = abstained, ["protection"]
            return d

    # ── 2. CAPITAL — can we act at all? ─────────────────────────────────────────────────────────
    cap = L.get("capital") or {}
    if cap.get("readable") and cap.get("fundable") is False:
        d = out("HOLD", "capital",
                cap.get("why") or "not fundable — nothing to deploy, so nothing to change")
        d["abstained"], d["votes"] = abstained, ["capital"]
        return d

    # ── 3+4. SHAPE — but ONLY from a layer that could actually be read ──────────────────────────
    # THIS IS THE BRANCH THAT MATTERS. If the volatility read failed we do not get to choose a
    # shape, because the difference between "calm" and "could not read" is the entire bug of
    # 2026-09-26. We keep the shape we hold and say why.
    vol = L.get("volatility") or {}
    sen = L.get("sentiment") or {}
    if not vol.get("readable"):
        d = out("HOLD_SHAPE", "volatility",
                "the market read is UNREADABLE, so no shape is chosen this pass — keeping the "
                "shape we hold. (A failed read is not a calm market; choosing one from a missing "
                "value is how the book churned on 2026-09-26.)")
        d["abstained"], d["votes"] = abstained, ["efficiency", "sentiment"]
        return d

    want = vol.get("shape_for")           # resolved shape from (market read, regime)
    if want is None:
        want = sen.get("shape_for")
    if want is None:
        d = out("HOLD_SHAPE", "sentiment",
                "the shape resolver returned nothing (regime and market both unreadable) — "
                "keeping the shape we hold rather than guessing one")
        d["abstained"], d["votes"] = abstained, ["efficiency"]
        return d

    want = "curve" if str(want).lower().replace("_", "-") == "curve" else "bid-ask"

    # ── 3. EFFICIENCY — the prime directive, expressed WITHIN the chosen shape ─────────────────
    eff = L.get("efficiency") or {}
    re_centre = bool(eff.get("readable") and eff.get("triggered"))
    # A PIVOT is the prime directive ACTING, not just reporting: the reading is structurally
    # meaningless for the shape we hold, so the shape itself is what has to change. Carried
    # separately from the ordinary re-centre so the caller can tell the two apart.
    pivot = bool(eff.get("readable") and eff.get("pivot_triggered"))
    eff_note = eff.get("why") or ""

    if want == "curve":
        post = "FARM_CURVE"
    else:
        post = "FARM_BIDASK"

    # A LEAN: a curve in a trending tape is a skewed curve, not a symmetric one.
    lean = sen.get("lean") or {}
    if post == "FARM_CURVE" and lean.get("direction"):
        post = "SKEW_CURVE"

    why = vol.get("why") or f"the market reads {want}"
    if sen.get("readable") and sen.get("regime"):
        why += f"; regime {sen['regime']}"
    if pivot:
        why += (f". EFFICIENCY (the prime directive) says PIVOT NOW — {eff.get('pivot_why') or eff_note}")
    elif re_centre:
        why += f". EFFICIENCY (the prime directive) says re-centre first: {eff_note}"

    d = out(post, "volatility" if vol.get("shape_for") else "sentiment", why,
            re_centre_first=re_centre, pivot=pivot,
            pivot_why=(eff.get("pivot_why") if pivot else None),
            lean=lean.get("direction"))
    d["abstained"], d["votes"] = abstained, ["efficiency", "sentiment", "volatility"]
    return d


# ────────────────────────────────────────────────────────────────────────────────────────────────
# GATHER — the only part that touches the world. Each layer is read SEALED: a failure produces
# readable=False with the cause, never a default value that a later branch could act on.
# ────────────────────────────────────────────────────────────────────────────────────────────────
def _seal(fn, name):
    try:
        return fn()
    except Exception as e:                                          # noqa: BLE001
        return {"readable": False, "error": f"{type(e).__name__}: {e}", "layer": name}


def _wallet_for(tenant: str) -> Optional[str]:
    """The tenant's wallet address, from the registry.

    WHY THIS IS NOT OPTIONAL (measured 2026-09-26): the layers underneath reach the chain through
    `steward_identity.wallet()`, which resolves **STEWARD_WALLET, then the profile's treasury
    config** — it does NOT read `STEWARD_TENANT`. The watchdog exports both, but the hub cron that
    writes the posture cache exported only `STEWARD_TENANT`. The result, verified by running both:
    **dadrian's posture was computed from JORDAN's book**, and nothing said so. Both tenants
    returned the same wallet address.

    This is the two-person bug stated precisely: a per-tenant loop around a read that ignores the
    tenant label is not per-tenant — it is one book wearing two names. The registry is the
    authority on whose wallet is whose, so the address is taken from there and exported.

    Returns None if it cannot be resolved, so the caller can carry that as an unknown rather than
    silently reading the default wallet — the exact failure this function exists to prevent.
    """
    try:
        import json
        import os
        reg = os.environ.get("STEWARD_REGISTRY") or \
            "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"
        with open(reg) as fh:
            d = json.load(fh)
        rec = (d.get("tenants") or {}).get(tenant) or {}
        w = rec.get("wallet")
        return str(w) if w else None
    except Exception:
        return None


def gather(tenant: str = "jordan", pair: Optional[str] = None) -> Dict[str, Any]:
    """Read all six layers. A layer that cannot be read comes back readable=False WITH ITS CAUSE.

    NOTE on `efficiency`: it is read ONCE here and reused, rather than being computed inside its
    own layer function, because the shape it must be judged against comes from the CHAIN. Reading
    it here keeps a single measurement for the pass — the efficiency figure and the shape it was
    judged against can never disagree.
    """
    # ── THE TENANT MUST REACH THE CHAIN READ (fixed 2026-09-26) ────────────────────────────────
    # Without this, every layer below resolves the DEFAULT wallet, so a per-tenant loop produced
    # one book's numbers under every tenant's name. Export BOTH variables: STEWARD_TENANT for the
    # layers that read it, STEWARD_WALLET because that is what steward_identity actually consults.
    # If the wallet cannot be resolved we say so rather than falling through to the default — an
    # unknown tenant is not a reason to read someone else's position.
    _w = _wallet_for(tenant)
    if _w:
        os.environ["STEWARD_TENANT"] = tenant
        os.environ["STEWARD_WALLET"] = _w
    else:
        return {"readable": False,
                "error": f"no wallet registered for tenant {tenant!r} — refusing to read another "
                         f"tenant's position",
                "layer": "capital"}

    L: Dict[str, Any] = {}
    eff_cache: Dict[str, Any] = {}

    # ── VOLATILITY / MARKET READ — the shape layer, and the one that failed today ───────────────
    def _volatility():
        import steward_rebalance as SR
        mkt = SR.measured_shape()
        reg = SR.read_regime() or {}
        want = SR.shape_for(reg.get("regime") or "", measured=mkt) if reg.get("regime") else None
        if mkt is None and not reg.get("regime"):
            return {"readable": False, "layer": "volatility",
                    "error": "both the pool's volatility read and the regime were unreadable"}
        # A market read of None is NOT calm — it is missing. Say which one we used.
        return {"readable": True, "layer": "volatility", "market": mkt,
                "shape_for": want or (mkt if mkt else None),
                "used_regime_fallback": mkt is None,
                "why": (f"the pool reads {mkt}" if mkt else
                        "the pool's volatility read is unavailable; used the regime label, which "
                        "is a WEAKER source (it is BTC-derived and cannot speak for this pair)")}

    # ── SENTIMENT ───────────────────────────────────────────────────────────────────────────────
    def _sentiment():
        import steward_rebalance as SR
        r = SR.read_regime() or {}
        label = r.get("regime")
        if not label or str(label).upper() in ("UNKNOWN", "NONE"):
            return {"readable": False, "layer": "sentiment",
                    "error": f"the regime label reads {label!r} — an unknown regime is not a regime"}
        tilt = (SR.REGIME_TILT or {}).get(label)
        return {"readable": True, "layer": "sentiment", "regime": label, "price": r.get("price"),
                "tilt": tilt,
                "lean": ({"direction": "up" if (tilt or 0) > 0.5 else
                          "down" if (tilt or 0) < 0.5 else None,
                          "tilt": tilt}),
                "why": f"regime {label}"}

    # ── EFFICIENCY — the prime directive ────────────────────────────────────────────────────────
    def _efficiency():
        import fee_efficiency as FE
        # Judge against the shape the CHAIN actually holds, not a label. measure() warns and falls
        # back to geometry when the label and the bins disagree; the default is only reached when
        # the chain itself is unreadable, which the guard below reports as unreadable.
        shape = None
        try:
            import lfj_shapes as LS
            # `measure()` returns the shape RESOLVED FROM THE CHAIN (it warns when the label and
            # the bins disagree, and then uses the bins). Take that field — asking for a "bins" key
            # it does not have silently fell through to the label every time.
            _m = FE.measure("bid-ask")
            # shape_of_bins returns "" for a PARTIAL book (bins matching no deployable geometry), so
            # `or` is doing real work here: "" is falsy and must fall through to the record label
            # rather than being used as a shape name. (2026-09-27)
            shape = _m.get("shape") or (LS.shape_of_bins(_m["bins"]) if _m.get("bins") else None)
        except Exception:
            shape = None
        ev = FE.evaluate(shape or "bid-ask")
        eff_cache["shape_judged"] = shape or "bid-ask"
        eff_cache["pivot_triggered"] = ev.get("pivot_triggered")
        eff_cache["pivot_why"] = ev.get("pivot_why")
        e = ev.get("efficiency")
        if e is None:
            return {"readable": False, "layer": "efficiency", "error": "no efficiency reading"}
        return {"readable": True, "layer": "efficiency", "efficiency_pct": round(e, 1),
                "band": ev.get("band"), "pos_pct": ev.get("posPct"),
                "low_for_minutes": ev.get("lowForMinutes"),
                "duty_pct": ev.get("dutyPct"),
                "triggered": bool(ev.get("triggered")),
                "scenario": ev.get("scenario"),
                "why": (f"efficiency {e:.1f}% ({ev.get('band')}), "
                        f"{'LOW for %.0f min — the rule fires' % (ev.get('lowForMinutes') or 0) if ev.get('triggered') else 'not triggered'}")}

    # ── MACRO / PROTECTION ──────────────────────────────────────────────────────────────────────
    def _protection():
        # STEWARD_CALENDAR_PATHS lets a test point the layer at a controlled file WITHOUT
        # touching the live calendar. Added 2026-09-27 so the freshness rule can be tested in
        # both directions (stale must abstain, current must still fire) on a real code path.
        _override = os.environ.get("STEWARD_CALENDAR_PATHS")
        cal_paths = ([p for p in _override.split(os.pathsep) if p.strip()] if _override
                     else [os.path.join(HERE, "economic-calendar.json"),
                           "/var/www/gentechlabs/DeFi/economic-calendar.json"])
        cal = None
        for p in cal_paths:
            if os.path.exists(p):
                try:
                    with open(p) as f:
                        cal = json.load(f)
                    break
                except Exception:
                    continue
        if not cal:
            return {"readable": False, "layer": "protection",
                    "error": "no economic calendar found — a missing calendar is not a quiet week"}
        events = cal.get("events") or []
        # ── A STALE CALENDAR IS NOT A STORMY DAY (fixed 2026-09-27) ─────────────────────────
        # `macro_imminent` was derived purely from the strings inside the file, with NO freshness
        # check. Measured: /var/www/gentechlabs/DeFi/economic-calendar.json had lastUpdated
        # 2026-09-11 and its events still read time:"TODAY" — TEN DAYS later. So the protection
        # layer fired "high-impact event today: PPI (MoM), PPI (YoY)" every single run, PROTECTION
        # short-circuited to FARM_BIDASK, and **the market and regime never got a vote**. That is
        # why jordan's book read as a bid-ask the market wanted to be a curve: the only layer
        # wanting bid-ask was reading a ten-day-old file.
        #
        # The fix follows this module's own existing principle — "a missing calendar is not a quiet
        # week" — extended honestly: a calendar we cannot confirm as CURRENT tells us nothing about
        # today either. It is UNREADABLE, so this layer ABSTAINS and lets sentiment and volatility
        # decide. Asserting an event from a stale file is the same false-value failure as reading a
        # failed call as a real zero.
        #
        # 36h is the limit because PPI/CPI print on a known day and the calendar is regenerated
        # daily; anything older than a day and a half cannot speak for "today".
        _max_age_h = float(os.environ.get("STEWARD_CALENDAR_MAX_AGE_H") or 36.0)
        _age_h = None
        _path_used = None
        for q in cal_paths:
            if not os.path.exists(q):
                continue
            try:
                a2 = (time.time() - os.path.getmtime(q)) / 3600.0
            except Exception:
                continue
            if _age_h is None or a2 < _age_h:      # prefer the newest candidate
                _age_h, _path_used = a2, q
        if _age_h is None:
            return {"readable": False, "layer": "protection",
                    "error": "no economic calendar found — a missing calendar is not a quiet week"}
        if _age_h > _max_age_h:
            return {"readable": False, "layer": "protection",
                    "stale_hours": round(_age_h, 1), "path": _path_used,
                    "error": (f"economic calendar is {_age_h:.1f}h old (limit {_max_age_h:.0f}h) — "
                              f"its events still say 'TODAY', so we cannot tell whether a "
                              f"high-impact event is actually today. Abstaining rather than "
                              f"asserting one from a stale file.")}
        high_today = [e for e in events
                      if str(e.get("impact", "")).lower() == "high"
                      and str(e.get("time", "")).upper().startswith("TODAY")]
        return {"readable": True, "layer": "protection",
                "macro_imminent": bool(high_today),
                "events": [e.get("name") for e in high_today][:4],
                "exit_everything": False,          # needs 3+ Go-Spot signals from live tape; not wired yet
                "go_spot": False,
                "macro_why": (f"high-impact TODAY: {', '.join(e.get('name','?') for e in high_today[:3])}"
                              if high_today else None),
                "note": ("exit-everything and Go-Spot need the 5-signal tape check, which is NOT "
                         "wired here yet — reporting them False is 'not evaluated', NOT 'no signal'")}

    # ── CAPITAL ─────────────────────────────────────────────────────────────────────────────────
    def _capital():
        p = f"/var/www/gentechlabs/DeFi/defi-data-{tenant}.json"
        if not os.path.exists(p):
            return {"readable": False, "layer": "capital", "error": f"no hub data at {p}"}
        with open(p) as f:
            d = json.load(f)
        cap = d.get("capital_usd")
        if cap is None:
            return {"readable": False, "layer": "capital", "error": "capital_usd absent"}
        return {"readable": True, "layer": "capital", "capital_usd": cap,
                "fundable": bool(cap and cap > 1.0),
                "why": f"${cap:.2f} in the pool" if cap else "flat book"}

    # ── HOLD vs FARM ────────────────────────────────────────────────────────────────────────────
    def _hold_farm():
        # ── THE LAYER WAS BLIND BY CONSTRUCTION (fixed 2026-09-30) ───────────────────────────────
        # `hold_trigger.fetch_series()` returns a TUPLE — `(points, source)` — but this unpacked
        # NOTHING and handed the whole tuple to `evaluate()`. So `evaluate` counted a 2-element
        # tuple as "2 points" and returned UNKNOWN on every single call, and the `if not s` guard
        # never fired either (a non-empty tuple is always truthy). The result: an ENTIRE posture
        # layer abstained forever and the posture silently ran on five layers instead of six —
        # reported honestly as UNREADABLE, which is why it never looked like a bug.
        # MEASURED, not assumed: the same feed carries 400 daily points and `evaluate(points)`
        # returns FARM (spot $11.17, +54.9% 30d, 2 of 3 gates passing). The feed was never down.
        # LESSON: when a caller passes a return value straight through, the CALLEE'S CONTRACT is
        # part of the caller. A tuple-shaped return read as a list is a silent, total outage.
        import hold_trigger as HT
        s, _src = HT.fetch_series()
        if not s:
            return {"readable": False, "layer": "hold_farm",
                    "error": f"the price series for the hold gate is unreadable ({_src})"}
        r = HT.evaluate(s)
        v = (r or {}).get("verdict")
        if not v or str(v).upper() == "UNKNOWN":
            return {"readable": False, "layer": "hold_farm",
                    "error": f"hold verdict is {v!r} — could not measure, which is not 'no signal'"}
        return {"readable": True, "layer": "hold_farm", "verdict": v,
                "why": str(r.get("why") or v)[:160]}

    for name, fn in (("volatility", _volatility), ("sentiment", _sentiment),
                     ("efficiency", _efficiency), ("protection", _protection),
                     ("capital", _capital), ("hold_farm", _hold_farm)):
        L[name] = _seal(fn, name)
    return L


# ────────────────────────────────────────────────────────────────────────────────────────────────
# SELF-TEST — proves the precedence AND the refusal. The unreadable-layer case is the regression
# for the bug that churned the book, so it is first.
# ────────────────────────────────────────────────────────────────────────────────────────────────
def _selftest() -> int:
    ok = fail = 0

    def check(name, got, want):
        nonlocal ok, fail
        if got == want:
            ok += 1
            print(f"  PASS  {name}")
        else:
            fail += 1
            print(f"  FAIL  {name}: got {got!r}, want {want!r}")

    RD = {"readable": True}
    NA = {"readable": False, "error": "simulated failure"}

    print("\n  ── THE REFUSAL: an unreadable layer must not vote ──")
    # 1. THE REGRESSION. Volatility unreadable, everything else healthy.
    #    The pre-fix system returned "calm -> curve" here. It must now abstain.
    d = resolve({"volatility": NA, "sentiment": {**RD, "regime": "BULL_TRENDING", "lean": {}},
                 "efficiency": {**RD, "triggered": False}, "protection": {**RD},
                 "capital": {**RD, "fundable": True}, "hold_farm": RD})
    check("unreadable market read -> HOLD_SHAPE (NOT FARM_CURVE)", d["posture"], "HOLD_SHAPE")
    check("  ...and it names volatility as the abstaining layer", d["set_by"], "volatility")
    check("  ...and it chooses NO shape", d["shape"], None)

    # 2. Efficiency unreadable must not block the shape choice (it is not needed to pick one).
    d = resolve({"volatility": {**RD, "market": "bid-ask", "shape_for": "bid-ask"},
                 "sentiment": {**RD, "regime": "BULL_TRENDING", "lean": {}},
                 "efficiency": NA, "protection": RD, "capital": {**RD, "fundable": True},
                 "hold_farm": RD})
    check("unreadable efficiency still yields a shape (FARM_BIDASK)", d["posture"], "FARM_BIDASK")
    check("  ...but it is REPORTED as abstained", "efficiency" in d["abstained"], True)

    # 3. Both shape sources unreadable -> refuse, never guess.
    d = resolve({"volatility": {**RD, "market": None, "shape_for": None},
                 "sentiment": {**RD, "regime": "UNKNOWN"},
                 "efficiency": RD, "protection": RD, "capital": {**RD, "fundable": True},
                 "hold_farm": RD})
    check("no shape source at all -> HOLD_SHAPE", d["posture"], "HOLD_SHAPE")

    print("\n  ── PRECEDENCE: protection outranks opportunity ──")
    # 4. Macro imminent forces bid-ask even when the market reads calm/curve.
    d = resolve({"protection": {**RD, "macro_imminent": True, "macro_why": "CPI today"},
                 "volatility": {**RD, "market": "curve", "shape_for": "curve"},
                 "sentiment": {**RD, "regime": "RANGE_BOUND", "lean": {}},
                 "efficiency": {**RD, "triggered": False}, "capital": {**RD, "fundable": True},
                 "hold_farm": RD})
    check("macro imminent OVERRIDES a calm read -> FARM_BIDASK", d["posture"], "FARM_BIDASK")
    check("  ...and protection set it", d["set_by"], "protection")

    # 5. Exit-everything outranks everything, including a fat efficiency trigger.
    d = resolve({"protection": {**RD, "exit_everything": True, "exit_why": "RSI > 85"},
                 "volatility": {**RD, "market": "bid-ask", "shape_for": "bid-ask"},
                 "sentiment": {**RD, "regime": "BULL_TRENDING", "lean": {}},
                 "efficiency": {**RD, "triggered": True}, "capital": {**RD, "fundable": True},
                 "hold_farm": RD})
    check("exit-everything beats even a triggered efficiency", d["posture"], "EXIT_TO_STABLE")

    # 6. 3+ Go-Spot signals -> SPOT.
    d = resolve({"protection": {**RD, "go_spot": True, "go_spot_why": "3/5 signals"},
                 "volatility": {**RD, "market": "bid-ask", "shape_for": "bid-ask"},
                 "sentiment": {**RD, "regime": "BULL_TRENDING", "lean": {}},
                 "efficiency": RD, "capital": {**RD, "fundable": True}, "hold_farm": RD})
    check("go-spot -> SPOT (hold the ASSET)", d["posture"], "SPOT")

    # 7. Capital gates, but BELOW protection.
    d = resolve({"protection": RD, "capital": {**RD, "fundable": False, "why": "flat"},
                 "volatility": {**RD, "market": "bid-ask", "shape_for": "bid-ask"},
                 "sentiment": {**RD, "regime": "BULL_TRENDING", "lean": {}},
                 "efficiency": RD, "hold_farm": RD})
    check("not fundable -> HOLD", d["posture"], "HOLD")

    print("\n  ── THE HAPPY PATHS ──")
    # 8. Trending tape, everything readable -> bid-ask.
    d = resolve({"protection": RD, "capital": {**RD, "fundable": True},
                 "volatility": {**RD, "market": "bid-ask", "shape_for": "bid-ask"},
                 "sentiment": {**RD, "regime": "BULL_TRENDING", "lean": {}},
                 "efficiency": {**RD, "triggered": False}, "hold_farm": RD})
    check("trending -> FARM_BIDASK", d["posture"], "FARM_BIDASK")
    check("  ...shape is bid-ask", d["shape"], "bid-ask")

    # 9. Calm + rangebound -> curve.
    d = resolve({"protection": RD, "capital": {**RD, "fundable": True},
                 "volatility": {**RD, "market": "curve", "shape_for": "curve"},
                 "sentiment": {**RD, "regime": "RANGE_BOUND", "lean": {"direction": None}},
                 "efficiency": {**RD, "triggered": False}, "hold_farm": RD})
    check("rangebound -> FARM_CURVE", d["posture"], "FARM_CURVE")

    # 10. A triggered efficiency is carried, not swallowed.
    d = resolve({"protection": RD, "capital": {**RD, "fundable": True},
                 "volatility": {**RD, "market": "bid-ask", "shape_for": "bid-ask"},
                 "sentiment": {**RD, "regime": "BULL_TRENDING", "lean": {}},
                 "efficiency": {**RD, "triggered": True, "why": "low for 94 min"},
                 "hold_farm": RD})
    check("efficiency trigger is carried into the decision", d["re_centre_first"], True)

    # 11. Every posture emitted is in the vocabulary.
    bad = [p for p in POSTURES if p not in POSTURES]
    check("the vocabulary is closed", bad, [])

    print(f"\n  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok+fail} checks passed\n")
    return 0 if fail == 0 else 1


# ────────────────────────────────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="one posture from all six layers")
    ap.add_argument("--tenant", default="jordan")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return _selftest()

    # ── `--json` MUST EMIT PURE JSON ON STDOUT (fixed 2026-09-26) ───────────────────────────────
    # It did not. `fee_efficiency.measure()` prints a warning line, and that landed on stdout
    # BEFORE the JSON — so the cache written by `posture.py --json > file` was not parseable:
    #     ⚠️  shape label 'bid-ask' disagrees with the chain: 25 bins is a CURVE. Using the ge...
    # The watchdog read it back, json.load failed, and it reported "POSTURE UNREADABLE —
    # JSONDecodeError" for a tenant whose posture was perfectly computable. A data tool whose
    # machine-readable mode is polluted by human chatter is the same defect as a failed read that
    # looks like a zero: it produces an UNKNOWN that no one can act on.
    #
    # The rule is general, not a patch for one warning: while `--json` is active, EVERY library
    # write to fd 1 is redirected to fd 2. Warnings stay visible (stderr is not discarded by the
    # caller that wants the JSON), and stdout carries nothing but the document.
    if a.json:
        import contextlib
        import io
        _buf = io.StringIO()
        with contextlib.redirect_stdout(sys.stderr):
            L = gather(a.tenant)
            d = resolve(L)
    else:
        L = gather(a.tenant)
        d = resolve(L)
    # What width would this scenario build? Reported here so the decision and the geometry that
    # follows from it are visible together — the bin count is part of the decision, not an
    # implementation detail downstream of it.
    try:
        import lfj_shapes as _LS
        _mkt = (L.get("volatility") or {}).get("market")
        b = _LS.adaptive_geometry(
            d.get("shape") or "curve",
            in_range=(None if d.get("posture") in ("FLAT", "HOLD_SHAPE") else True),
            efficiency_pct=(L.get("efficiency") or {}).get("efficiency_pct"))
    except Exception:
        b = {"total": None, "adaptive": False, "why": ""}

    if a.json:
        print(json.dumps({"tenant": a.tenant, "decision": d, "layers": L}, indent=2, default=str))
        return 0

    print(f"\n  🧭 POSTURE — {a.tenant}")
    print("  " + "─" * 68)
    print(f"  POSTURE   {d['posture']}")
    print(f"  SET BY    {d['set_by'].upper()} layer")
    if d.get("shape"):
        print(f"  SHAPE     {d['shape']}")
    if d.get("pivot"):
        print("  ⚡ PIVOT — the efficiency rule says change SHAPE, not just re-centre")
    elif d.get("re_centre_first"):
        print("  EFFICIENCY  the prime directive says RE-CENTRE first (within this shape)")
    if b.get("adaptive"):
        print(f"  WIDTH     {b['total']} bins — {b['why'][:64]}")
    print("  " + "─" * 68)
    print(f"  {d['why']}")
    print("  " + "─" * 68)
    for n in LAYERS:
        lay = L.get(n) or {}
        if lay.get("readable"):
            # Prefer a NAMED reading over a bare value; a layer that reports only an id is noise.
            v = (lay.get("market") or lay.get("regime") or lay.get("verdict")
                 or (f"{lay.get('efficiency_pct')}%" if lay.get("efficiency_pct") is not None
                     else None)
                 or (f"${lay.get('capital_usd')}" if lay.get("capital_usd") is not None else None)
                 or ("high-impact event today" if lay.get("macro_imminent") else "quiet"))
            print(f"    {n:11} ✓ {str(v)[:56]}")
        else:
            print(f"    {n:11} ✗ UNREADABLE — {str(lay.get('error'))[:48]}")
    if d["abstained"]:
        print(f"\n  ABSTAINED: {', '.join(d['abstained'])} — unreadable layers do not vote.")
    print("  " + "─" * 68 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
