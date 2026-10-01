#!/usr/bin/env python3
"""challenger.py — The Challenger node: DISSENTING GOVERNOR of the Fed-council swarm.

Jordan's directive (Aug 30 2026): the Challenger should behave like the dissenting
seat on the Fed council — when the room leans one way on market sentiment (e.g.
"everyone thinks we have one more dip left"), this node attacks that consensus
WITH DATA, from sources the rest of the estate does not read. Original mandate
(Aug 29): intelligence, not just data. Estate hygiene checks (R1-R6) are kept
as a secondary section.

How it forms the two sides:

  THE ROOM  = the estate's own lens stack (each lens = what a council member
  reads): regime classifier, sentiment radar BTC 7d, narrative momentum heat,
  BTC dominance delta, buy-zone posture, + the standing council verdict in
  treasury-state.json. Aggregated into a lean: BULLISH / BEARISH / no clear lean.

  THE DISSENT = independent live sources NO other node reads:
    - perp funding rates (Binance -> Bybit -> OKX fallback chain): crowded-long
      funding or shorts-paying funding directly tests the room's dip/bull story
    - Alternative.me Fear & Greed: euphoria vs capitulation
    - stablecoin supply delta (own baseline, CoinGecko): the dry-powder fuel

  It prints ONLY when its evidence materially contradicts the room's lean.
  Agreement = silence (estate healthy). Nothing self-applies; the chair (Jordan)
  rules on adoption. Env CHALLENGER_FORCE_ROOM=BULLISH|BEARISH and
  CHALLENGER_FORCE_EVIDENCE=BULL|BEAR are TEST-ONLY overrides for verifying
  the dissent path end-to-end.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

CANON = "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/treasury-state.json"
COPIES = [
    CANON,
    "/root/.hermes/profiles/gentech-treasury/scripts/treasury-state.json",
    "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/treasury-state.json",
]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REGIME_FILE_ALT = "/root/.hermes/scripts/.aae-regime-state.json"  # canonical post-Aug-29 fix (cron writes here)
CLARITY_FILE = os.path.join(SCRIPT_DIR, ".clarity-vote-state.json")
DOM_FILE = os.path.join(SCRIPT_DIR, ".btc-dominance-state.json")
RADAR_FILE = "/root/repos/gentechlabs.github.io/DeFi/rainbow/market-sentiment.json"
CHALLENGER_STATE = os.path.join(SCRIPT_DIR, ".challenger-state.json")

UA = {"User-Agent": "Mozilla/5.0 (Steward/1.0)", "Accept": "application/json"}

findings = []   # estate hygiene (R1-R6)
challenge = []  # market dissent lines


def age_hours(path):
    try:
        return (datetime.now(timezone.utc).timestamp() - os.path.getmtime(path)) / 3600
    except OSError:
        return None


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _http_json(url, timeout=10):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


# ════════════════════════════════════════════════════════════════════════
# PART 1 — THE ROOM'S LEAN (from the estate's own lenses)
# ════════════════════════════════════════════════════════════════════════

def room_lean():
    """Aggregate the estate's lenses into (score, detail_lines)."""
    score = 0
    lines = []

    # Lens 1: regime classifier (fresh only — same 6h rule the council uses)
    reg = None
    if os.path.exists(REGIME_FILE_ALT):
        reg = load(REGIME_FILE_ALT)
        if reg:
            ts = reg.get("timestamp")
            try:
                age = (datetime.now(timezone.utc) -
                       datetime.fromisoformat(ts)).total_seconds()
                if age > 6 * 3600:
                    reg = None
            except Exception:
                reg = None
    if reg:
        r = reg.get("regime", "")
        conf = reg.get("confidence", 0)
        if r in ("BULL_TRENDING", "ACCUMULATION", "PRICE_DISCOVERY"):
            score += 1
            lines.append(f"regime {r} {conf:.0%} → bull (+1)")
        elif r in ("BEAR_TRENDING", "HIGH_VOLATILITY"):
            score -= 1
            lines.append(f"regime {r} {conf:.0%} → bear (−1)")
        else:
            lines.append(f"regime {r} {conf:.0%} → neutral (0)")
    else:
        lines.append("regime: no fresh read (0)")

    # Lens 2: sentiment radar — BTC 7d + narrative heat
    radar = load(RADAR_FILE)
    if radar:
        try:
            btc7 = float(radar.get("btc", {}).get("change_7d", 0))
            if btc7 > 2:
                score += 1
                lines.append(f"BTC 7d {btc7:+.1f}% → bull (+1)")
            elif btc7 < -2:
                score -= 1
                lines.append(f"BTC 7d {btc7:+.1f}% → bear (−1)")
            else:
                lines.append(f"BTC 7d {btc7:+.1f}% → neutral (0)")
        except Exception:
            lines.append("BTC 7d: unreadable (0)")
        scores = [n.get("score", 0) for n in radar.get("narratives", [])]
        if scores:
            heat = sum(scores) / len(scores)
            if heat > 3:
                score += 1
                lines.append(f"narrative heat {heat:+.1f} avg → bull (+1)")
            elif heat < -3:
                score -= 1
                lines.append(f"narrative heat {heat:+.1f} avg → bear (−1)")
            else:
                lines.append(f"narrative heat {heat:+.1f} avg → neutral (0)")
    else:
        lines.append("sentiment radar: unavailable (0)")

    # Lens 3: dominance delta (rotation risk-on / risk-off)
    dom = load(DOM_FILE) or {}
    d_now, d_prev = dom.get("btc_dominance"), dom.get("prev_dominance")
    if isinstance(d_now, (int, float)) and isinstance(d_prev, (int, float)):
        delta = d_now - d_prev
        if delta <= -0.5:
            score += 1
            lines.append(f"BTC dominance {d_now:.1f}% ({delta:+.2f}) → rotation bull (+1)")
        elif delta >= 0.5:
            score -= 1
            lines.append(f"BTC dominance {d_now:.1f}% ({delta:+.2f}) → risk-off bear (−1)")
        else:
            lines.append(f"BTC dominance {d_now:.1f}% ({delta:+.2f}) → steady (0)")
    else:
        lines.append("dominance: no data (0)")

    # Lens 4: buy-zone posture on BTC (complacency vs capitulation)
    btc_price = None
    if radar:
        btc_price = radar.get("btc", {}).get("price")
    if btc_price:
        # zone table mirrors steward-council BUY_ZONES (BTC row, updated 2026-08-19)
        if btc_price >= 75000:
            score -= 1
            lines.append(f"BTC ${btc_price:,.0f} in Extended zone → complacent (−1)")
        elif btc_price < 58000:
            score += 1
            lines.append(f"BTC ${btc_price:,.0f} in Deep Value → capitulation-entry (+1)")
        else:
            lines.append(f"BTC ${btc_price:,.0f} Watch/Accumulate zone (0)")
    else:
        lines.append("buy-zone: no BTC price (0)")

    if os.environ.get("CHALLENGER_FORCE_ROOM") == "BULLISH":
        return 3, ["[TEST OVERRIDE] forced BULLISH lean (+3)"]
    if os.environ.get("CHALLENGER_FORCE_ROOM") == "BEARISH":
        return -3, ["[TEST OVERRIDE] forced BEARISH lean (−3)"]
    return score, lines


def lean_label(score):
    if score >= 2:
        return "BULLISH"
    if score <= -2:
        return "BEARISH"
    return None  # no clear lean


# ════════════════════════════════════════════════════════════════════════
# PART 2 — THE DISSENT (independent sources no other node reads)
# ════════════════════════════════════════════════════════════════════════

def fetch_funding():
    """Avg of last 3 perp funding rates (8h each) for BTC. Fallback chain.
    Returns (rate_pct_per_8h, venue) or (None, None)."""
    # Binance USDⓈ-M
    try:
        d = _http_json("https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=3")
        rates = [float(x["fundingRate"]) * 100 for x in d]
        return sum(rates) / len(rates), "Binance perp"
    except Exception:
        pass
    # Bybit v5 linear
    try:
        d = _http_json("https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT")
        fr = float(d["result"]["list"][0]["fundingRate"]) * 100
        return fr, "Bybit perp"
    except Exception:
        pass
    # OKX swap
    try:
        d = _http_json("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP")
        fr = float(d["data"][0]["fundingRate"]) * 100
        return fr, "OKX perp"
    except Exception:
        pass
    return None, None


def fetch_fng():
    """Alternative.me Fear & Greed (current + yesterday)."""
    try:
        d = _http_json("https://api.alternative.me/fng/?limit=2")
        cur = d["data"][0]
        return int(cur["value"]), cur.get("value_classification", "?")
    except Exception:
        return None, None


def stablecoin_read():
    """Combined USDT+USDC market cap vs our own stored baseline.
    Returns (total_usd, delta_pct_or_None)."""
    total = None
    try:
        d = _http_json("https://api.coingecko.com/api/v3/coins/markets"
                       "?ids=tether,usd-coin&vs_currency=usd")
        total = sum((c.get("market_cap") or 0) for c in d) or None
    except Exception:
        pass
    prev = load(CHALLENGER_STATE) or {}
    base = prev.get("stablecoin_baseline") or {}
    delta_pct = None
    if total and base.get("total") and base.get("age_days", 999) <= 14:
        delta_pct = (total - base["total"]) / base["total"] * 100
    # always refresh baseline if it's older than 1 day (keeps delta meaningful)
    now_ts = time.time()
    if total and (now_ts - base.get("ts", 0)) > 86400:
        prev["stablecoin_baseline"] = {"total": total, "ts": now_ts,
                                       "age_days": 0, "at": datetime.now(timezone.utc).isoformat()}
        try:
            with open(CHALLENGER_STATE, "w") as f:
                json.dump(prev, f, indent=2)
        except Exception:
            pass
    return total, delta_pct


def dissent_evidence():
    """Collect the challenger's independent evidence.
    Returns (evidence_score, lines, parts). Positive score = bull-side evidence,
    negative = bear-side evidence."""
    score = 0
    lines = []
    parts = {}

    # 1. Funding — positioning test
    fr, venue = fetch_funding()
    if fr is None:
        lines.append("funding: unavailable on all venues — no positioning read")
        parts["funding"] = None
    else:
        apr = fr * 3 * 365
        if fr > 0.03:      # >33% APR: longs crowded, upside is leveraged
            score -= 1
            lines.append(f"funding {fr:+.4f}%/8h (~{apr:.0f}% APR, {venue}) — longs CROWDED → squeeze fuel (bear-evidence −1)")
        elif fr < 0:       # shorts paying longs: dip is already shorted
            score += 1
            lines.append(f"funding {fr:+.4f}%/8h (~{apr:.0f}% APR, {venue}) — shorts PAYING → dip already crowded (bull-evidence +1)")
        else:
            lines.append(f"funding {fr:+.4f}%/8h (~{apr:.0f}% APR, {venue}) — neutral positioning (0)")
        parts["funding"] = fr

    # 2. Fear & Greed — sentiment extreme test
    fng, cls = fetch_fng()
    if fng is None:
        lines.append("fear & greed: unavailable — no sentiment-extreme read")
        parts["fng"] = None
    else:
        if fng >= 80:
            score -= 1
            lines.append(f"fear & greed {fng} ({cls}) — EUPHORIA zone (bear-evidence −1)")
        elif fng <= 25:
            score += 1
            lines.append(f"fear & greed {fng} ({cls}) — CAPITULATION zone, historically entry territory (bull-evidence +1)")
        else:
            lines.append(f"fear & greed {fng} ({cls}) — mid-range (0)")
        parts["fng"] = fng

    # 3. Stablecoin fuel — dry-powder flow test
    total, delta = stablecoin_read()
    if total is None:
        lines.append("stablecoin supply: read failed — no fuel read")
        parts["stables"] = None
    else:
        tstr = f"${total/1e9:,.1f}B"
        if delta is None:
            lines.append(f"stablecoin supply {tstr} — baseline recorded, delta available next run (0)")
        elif delta > 0.5:
            score += 1
            lines.append(f"stablecoin supply {tstr} ({delta:+.1f}% vs baseline) — fuel BUILDING (bull-evidence +1)")
        elif delta < -0.5:
            score -= 1
            lines.append(f"stablecoin supply {tstr} ({delta:+.1f}% vs baseline) — fuel DRAINING (bear-evidence −1)")
        else:
            lines.append(f"stablecoin supply {tstr} ({delta:+.1f}% vs baseline) — fuel steady (0)")
        parts["stables"] = delta

    return score, lines, parts


# ════════════════════════════════════════════════════════════════════════
# PART 3 — ESTATE HYGIENE (R1-R6, kept from the Aug 29 audit)
# ════════════════════════════════════════════════════════════════════════

def hygiene_checks():
    # R1 — state-copy divergence
    modes, pendings = {}, {}
    for p in COPIES:
        d = load(p)
        if d:
            modes[p] = d.get("mode")
            pendings[p] = (d.get("pending_mode") or {}).get("mode")
    if len(set(modes.values())) > 1:
        findings.append(("HIGH", "R1 state-copy divergence",
                         f"copies disagree on mode: {modes}",
                         "re-sync all copies from the canonical file"))
    if len(set(pendings.values())) > 1:
        findings.append(("HIGH", "R1 pending divergence",
                         f"copies disagree on pending_mode: {pendings}",
                         "re-sync all copies; confirm which request is real"))

    # R2 — stale canonical state
    a_canon = age_hours(CANON)
    if a_canon is None:
        findings.append(("HIGH", "R2 canonical state missing",
                         f"{CANON} not found", "recreate from vault copy or rebuild"))
    elif a_canon > 6:
        findings.append(("MED", "R2 stale treasury state",
                         f"canonical state {a_canon:.1f}h old (>6h)",
                         "council live-read fallback engaged; refresh state on next meeting"))

    # R3 — CLARITY tracker RETIRED 2026-09-21.
    # Both CLARITY cron jobs were removed by Jordan's decision (the Act is no longer a
    # dependency). The prior checks reported a MISSING or STALE state file as a MED finding,
    # which would have fired every single run forever with no way to clear - a check that can
    # only fail is not a check. Retired deliberately, not left to rot.

    # R4 — orphaned pending_mode
    canon = load(CANON) or {}
    if (canon.get("pending_mode") or {}).get("mode"):
        pm = canon["pending_mode"]
        findings.append(("MED", "R4 pending mode request open",
                         f"{pm.get('mode')} requested {str(pm.get('requested_at'))[:10]}",
                         "council must surface it every meeting until Jordan rules"))

    # R5 — dominance schema clobber recurrence
    dd = load(DOM_FILE)
    if dd and "btc_dominance" not in dd:
        findings.append(("MED", "R5 dominance schema clobbered again",
                         "btc_dominance key missing from .btc-dominance-state.json",
                         "market-sentiment RMW fix regressed? re-check the writer"))


# ════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════

def main():
    hygiene_checks()
    rscore, rlines = room_lean()
    lean = lean_label(rscore)
    escore, elines, parts = dissent_evidence()
    # TEST-ONLY evidence override (verifies the challenge path deterministically)
    _fe = os.environ.get("CHALLENGER_FORCE_EVIDENCE")
    if _fe == "BULL":
        escore = 2
        elines = ["[TEST OVERRIDE] forced bull-side evidence (+2)"] + elines
    elif _fe == "BEAR":
        escore = -2
        elines = ["[TEST OVERRIDE] forced bear-side evidence (−2)"] + elines

    # ── Decide whether the dissent materially contradicts the room ──
    headline = None
    severity = None
    if lean == "BULLISH" and escore <= -1:
        severity = "HIGH" if escore <= -2 else "MED"
        headline = ("The room reads BULLISH but positioning/sentiment data pushes back. "
                    "If you're leaning long here, size for a shakeout — the crowd already is.")
    elif lean == "BEARISH" and escore >= 1:
        severity = "HIGH" if escore >= 2 else "MED"
        headline = ("The room reads BEARISH (the \"one more dip\" call) but independent data "
                    "pushes back. If the dip comes it may already be crowded — watch for a "
                    "failed breakdown instead of a clean lower low.")
    elif lean is None and abs(escore) >= 2:
        severity = "LOW"
        direction = "bull-side" if escore > 0 else "bear-side"
        headline = (f"The estate's lenses have no clear lean, but the challenger's independent "
                    f"data stacks {direction}. The room should pick a side with eyes open.")
    # room and evidence agree, or both neutral-weak → silent on stance

    # ── Emit ──
    if not findings and headline is None:
        # record state silently (stablecoins baseline bookkeeping already done)
        prev = load(CHALLENGER_STATE) or {}
        prev["last_run"] = datetime.now(timezone.utc).isoformat()
        prev["last_room_lean"] = {"score": rscore, "lean": lean}
        prev["last_evidence"] = {"score": escore, "parts": parts}
        prev["last_challenge"] = None
        try:
            with open(CHALLENGER_STATE, "w") as f:
                json.dump(prev, f, indent=2)
        except Exception:
            pass
        sys.exit(0)  # silent — estate healthy, no material dissent

    print("😈 CHALLENGER — the dissenting governor")
    print("")
    print(f"🏛️ THE ROOM (estate lenses, score {rscore:+d}): {lean or 'no clear lean'}")
    for l in rlines:
        print(f"   · {l}")
    print("")
    print(f"😈 THE DISSENT (independent sources, evidence {escore:+d}):")
    for l in elines:
        print(f"   · {l}")
    if headline:
        print("")
        print(f"🔴 {severity} — CHALLENGE TO THE ROOM'S LEAN")
        print(f"   {headline}")
        print("   The chair rules: adopt the dissent, hold the room's lean, or split the difference.")
    print("")
    if findings:
        print("━━━ estate hygiene (secondary) ━━━")
        order = {"HIGH": 0, "MED": 1, "LOW": 2}
        for sev, check, ev, fix in sorted(findings, key=lambda x: order.get(x[0], 9)):
            print(f"🔴 {sev} — {check}")
            print(f"   evidence: {ev}")
            print(f"   proposal: {fix}")
        print("")
    print("Proposals are suggestions — nothing self-applies. The chair rules on adoption.")

    # ── Record state ──
    prev = load(CHALLENGER_STATE) or {}
    prev["last_run"] = datetime.now(timezone.utc).isoformat()
    prev["last_room_lean"] = {"score": rscore, "lean": lean, "lines": rlines}
    prev["last_evidence"] = {"score": escore, "parts": parts, "lines": elines}
    prev["last_challenge"] = {"severity": severity, "headline": headline} if headline else None
    try:
        with open(CHALLENGER_STATE, "w") as f:
            json.dump(prev, f, indent=2)
    except Exception:
        pass


if __name__ == "__main__":
    main()
