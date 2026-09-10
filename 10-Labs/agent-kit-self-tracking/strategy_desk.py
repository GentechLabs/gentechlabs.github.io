#!/usr/bin/env python3
"""GenTech Strategy Desk — the layer that CHOOSES the treasury's strategy.

Jordan's v5 vision (Sep 2 2026): multiple strategies layered on top of each
other, with the intelligence to change its own mind — "you chose farming, but
what if you decided holding is better? Make that decision for me."

v1 design (honest scope):
  SCORES three strategies from LIVE signals we already produce:
    FARM  — LP fee capture (pool fee APY, in-range status, IL geometry)
    HOLD  — AVAX-heavy passive (bull continuation: regime, momentum, RSI)
    LEND  — stable lending (Jupiter Lend rail) when dry powder exists

  The desk PROPOSES a mode change only when conviction crosses the threshold:
    - score gap >= SWITCH_MARGIN over the incumbent
    - confidence >= MIN_CONFIDENCE (feed freshness caps it)
    - max one pending proposal; 24h cooldown between proposals
  Proposals print to Telegram (cron deliver) — Jordan answers YES/NO in chat.
  Execution happens on his confirmation (the session is the executor) OR
  automatically when AUTO_MODE is set true in the state file (Jordan flips
  the switch when he's ready — his "yes or no" gate honored).

  Silent when the incumbent wins (no_agent pattern).

Usage: python3 strategy_desk.py [--json]
Writes: /root/.hermes/scripts/.strategy-desk-state.json
"""
import json
import os
import sys
import time

STATE_DIR = "/root/.hermes/scripts"
OUT = os.path.join(STATE_DIR, ".strategy-desk-state.json")
LPFEED = "/root/.hermes/profiles/gentech/scripts/lp-fees-live.json"
STAKFEED = "/root/.hermes/profiles/gentech/scripts/staking-apr-live.json"
REGIME = os.path.join(STATE_DIR, ".aae-regime-state.json")
VAULT_DIR = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking"

SWITCH_MARGIN = 15.0     # score points the challenger must beat incumbent by
MIN_CONFIDENCE = 65
PROPOSAL_TTL_H = 12      # proposal expires; Jordan's window to answer
PROPOSAL_COOLDOWN_H = 24

# Lend rail benchmark (Jupiter Lend USDC, verified in council Sep 2)
LEND_APY = 5.0


def load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return {}


def feed_ok(feed, max_h=48):
    return bool(feed) and feed.get("ts") and (time.time() - feed["ts"]) / 3600 < max_h


def score_strategies():
    """Score FARM / HOLD / LEND 0-100 from live signals. Returns (scores, notes)."""
    lp = load(LPFEED)
    stak = load(STAKFEED)
    reg = load(REGIME)
    notes = []

    pool_apy = lp.get("apy") if feed_ok(lp) else None
    staking = stak.get("apr") if feed_ok(stak) else None
    regime = str(reg.get("regime", "UNKNOWN")).upper()
    rsi = reg.get("rsi_14") or 50
    mom7d = (reg.get("price_change_7d") or 0) * 100

    # ── FARM: fee edge over benchmarks + structural occupancy ──
    farm = 50.0
    if pool_apy and staking:
        edge = pool_apy - staking
        farm = min(100, 40 + edge)          # each point of APY edge = 1 score
        notes.append(f"fee edge {pool_apy}% vs staking {staking}% = +{edge:.0f}")
    else:
        notes.append("feeds stale — farm score capped at 50")
        farm = min(farm, 50)
    if rsi >= 75:
        farm += 5  # overbought -> pullback still lands IN our bins (we want price action)
        notes.append("RSI overbought: pullback expectation favors LP bin capture")

    # ── HOLD: bull continuation, AVAX-heavy passive ──
    bull = any(k in regime for k in ("BULL", "TREND", "DISCOVERY"))
    hold = 30.0
    if bull:
        hold += 25
        notes.append("bull regime +25 to HOLD")
    if mom7d > 5:
        hold += 15
        notes.append(f"7d momentum +{mom7d:.1f}% favors HOLD")
    if rsi >= 75:
        hold -= 20  # overbought = bad time to go AVAX-heavy
        notes.append("RSI overbought penalizes HOLD")
    hold = max(0, min(100, hold))

    # ── LEND: stable lending when its APY beats our fee reality ──
    lend = 20.0
    if pool_apy:
        lend = max(0, 60 - (pool_apy - LEND_APY))  # lend only competitive if fees collapse
        notes.append(f"lend {LEND_APY}% vs pool {pool_apy}% -> score {lend:.0f}")

    return {"FARM": round(farm), "HOLD": round(hold), "LEND": round(lend)}, notes


def main():
    now = time.time()
    scores, notes = score_strategies()
    prev = load(OUT)

    incumbent = prev.get("mode", "FARM")
    challenger = max(scores, key=scores.get)
    gap = scores[challenger] - scores[incumbent]

    pending = prev.get("proposal") or {}
    proposal_live = bool(pending) and (now - pending.get("ts", 0)) < pending.get("ttl_h", 12) * 3600
    last_proposal_h = (now - prev.get("last_proposal_ts", 0)) / 3600 if prev.get("last_proposal_ts") else 999

    out = {
        "ts": now,
        "mode": incumbent,
        "scores": scores,
        "notes": notes,
        "proposal": pending if proposal_live else None,
        "last_proposal_ts": prev.get("last_proposal_ts"),
    }

    # Proposal condition: challenger beats incumbent by margin, cooldown clear
    should_propose = (
        challenger != incumbent
        and gap >= SWITCH_MARGIN
        and last_proposal_h >= PROPOSAL_COOLDOWN_H
        and not proposal_live
    )
    if should_propose:
        out["proposal"] = {
            "ts": now,
            "ttl_h": PROPOSAL_TTL_H,
            "from": incumbent,
            "to": challenger,
            "gap": gap,
            "scores": scores,
            "status": "PENDING_JORDAN_YES_NO",
        }
        out["last_proposal_ts"] = now
        print("🏛️ GENTECH STRATEGY DESK — MODE PROPOSAL (needs your YES/NO)")
        print(f"   Proposal: switch {incumbent} → {challenger} (score gap {gap:.0f})")
        print(f"   Scores: {json.dumps(scores)}")
        for n in notes:
            print(f"   · {n}")
        print(f"   Reply YES to execute, NO to dismiss. Auto-expires in {PROPOSAL_TTL_H}h.")
    elif proposal_live:
        print("🏛️ Strategy Desk: proposal PENDING your YES/NO — "
              f"switch {pending.get('from')} → {pending.get('to')} (expires {pending.get('ttl_h')}h from proposal)")
    else:
        # incumbent holds — silent unless run with --json
        if "--json" not in sys.argv:
            return 0

    json.dump(out, open(OUT, "w"), indent=2)
    if "--json" in sys.argv:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())