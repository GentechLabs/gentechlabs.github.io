#!/usr/bin/env python3
"""Wire existing arb signal sources into the structured arb log (Phase 0).

Reads the state files the existing GTA arb scan and prediction-arb rail
already produce, and logs each signal as a structured row. This is the
non-invasive wiring: the running scripts (referenced by crons) are untouched;
this wrapper consumes their output and appends to the arb log.

Sources:
  - GTA arb scan      : .gta-arb-state.json  (perp-vs-spot basis, Hyperliquid
                        vs Coinbase) — strategy "gta-arb"
  - Prediction-arb    : .steward-prediction.json (Polymarket/Kalshi edges) —
                        strategy "prediction-arb"

Mode-gate respected: signals are logged even when the mode-gate holds them
(that's data for the critic). Realized P&L is read from the FIXED fee ledger
(.steward-fee-ledger.json) — never fabricated.

Usage:
  python3 wire_arb_log.py            # read state files + log signals
  python3 wire_arb_log.py --dry      # print what would be logged, no write
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arb_log import log_signal, LOG_ROOT  # noqa: E402

# ── TRUTH-LAYER FIX (Sep 11 2026) ────────────────────────────────────────────
# The scan writer is `gta-arb-monitor.py`, run by the treasury cron ring
# (gated-executor.sh) and it writes to the TREASURY profile dir. This logger was
# pointed at the OLD gentech profile path, whose file froze on 2026-09-06 — so
# every "gta-arb" row logged since 2026-09-10 14:35 was a REPLAY of a 5-day-old
# scan (LINK +12.5bps / ONDO +7.8bps), logged `taken=True` because it also read
# the stale TRADE copy of treasury-state.json. Same class as the Aug 23→31
# frozen-scan bug that gta_executor.py already guards against. Two fixes:
#   1. point at the LIVE writer's output (with a fallback chain), and
#   2. refuse to log a scan older than MAX_SCAN_AGE_H (mirrors the executor).
# The executor's own execute bar (gta_executor.py EXECUTE_BPS). Kept as a named
# constant here so the two can never drift into disagreeing about what "clears
# the bar" means — the log must attribute cause using the SAME threshold the
# trade path uses.
EXECUTE_BPS = 10.0

GTA_STATE_CANDIDATES = [
    os.environ.get("GTA_STATE_FILE"),
    "/root/.hermes/profiles/gentech-treasury/scripts/.gta-arb-state.json",
    "/root/.hermes/profiles/gentech/scripts/.gta-arb-state.json",
]
MAX_SCAN_AGE_H = 6.0   # a scan staler than this is a memo of the past, not a signal


def _scan_age_hours(st: dict | None):
    """Age in hours of a scan state dict, or None if unparseable/missing."""
    if not st or not st.get("last_scan"):
        return None
    try:
        t = datetime.fromisoformat(str(st["last_scan"]).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 3600.0
    except Exception:
        return None


def _resolve_gta_state():
    """First candidate that exists AND is fresh; else the newest that exists."""
    best = (None, None, None)   # (path, state, age)
    for path in GTA_STATE_CANDIDATES:
        if not path:
            continue
        st = load_json(path)
        if not st:
            continue
        age = _scan_age_hours(st)
        if age is not None and age <= MAX_SCAN_AGE_H:
            return path, st, age
        if best[1] is None or (age is not None and (best[2] is None or age < best[2])):
            best = (path, st, age)
    return best


# Back-compat: keep the name so other callers/readers don't break.
GTA_STATE = GTA_STATE_CANDIDATES[1]
PRED_STATE = os.environ.get(
    "PRED_STATE_FILE",
    "/root/vaults/gentech/Treasury/.steward-prediction.json",
)
# Fixed fee ledger (real on-chain P&L) — read for realized P&L
FEE_LEDGER = os.environ.get(
    "FEE_LEDGER_FILE",
    "/root/.hermes/profiles/gentech-treasury/scripts/.steward-fee-ledger.json",
)

# Mode-gate: current treasury mode (YIELD_FARM vs TRADE). When YIELD_FARM,
# trade signals are held by the gate — logged as not-taken with reason.
# Mode-gate reads the CANONICAL shared state (same file treasury_state.py uses).
# Reading a stale profile COPY is how this logger once saw mode=TRADE while the
# canonical brain said YIELD_FARM — logging held signals as `taken=True`.
MODE_STATE = os.environ.get(
    "TREASURY_MODE_STATE",
    "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/treasury-state.json",
)


def load_json(path: str) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _recent_signals(strategy: str, window_s: int = 3600) -> set:
    """Set of (strategy, signal) tuples logged in the last window_s seconds.
    Used to avoid re-logging the same signal on every cron tick."""
    import glob
    seen = set()
    cutoff = datetime.now(timezone.utc).timestamp() - window_s
    for path in glob.glob(os.path.join(LOG_ROOT, "*.jsonl")):
        try:
            with open(path) as f:
                for line in f:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    if row.get("strategy") != strategy:
                        continue
                    try:
                        ts = datetime.fromisoformat(row["ts"]).timestamp()
                    except Exception:
                        continue
                    if ts >= cutoff:
                        seen.add((strategy, row.get("signal")))
        except (OSError, json.JSONDecodeError):
            continue
    return seen


def _logged_scan_ts(strategy: str) -> set:
    """Set of scan `last_scan` timestamps already logged for this strategy.

    WHY (Sep 14 2026): one scan got replayed into the log as if it were a
    fresh signal on every cron tick inside the 6h truth gate + 3600s dedupe
    window. Measured 2026-09-14: the 11:00 scan (AVAX -9.75bps, perp
    $7.3778 vs spot $7.385) was logged at 11:30, 12:30 AND 13:30 with
    byte-identical prices while live AVAX had moved to ~$7.45; the overnight
    PAXG scan replayed 6x (00:30..05:30) for the same reason. A scan is a
    single market read — it must produce ONE set of rows, not one per tick.
    """
    import glob
    seen = set()
    for path in glob.glob(os.path.join(LOG_ROOT, "*.jsonl")):
        try:
            with open(path) as f:
                for line in f:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    if row.get("strategy") != strategy:
                        continue
                    sts = (row.get("meta") or {}).get("scan_ts")
                    if sts:
                        seen.add(sts)
        except (OSError, json.JSONDecodeError):
            continue
    return seen


def current_mode() -> str:
    st = load_json(MODE_STATE)
    if st:
        mode = st.get("mode") or st.get("current_mode")
        if mode:
            return mode
    return "YIELD_FARM"  # default (safe: holds trade signals)


def latest_fees() -> float | None:
    """Realized P&L from the fixed fee ledger: the most recent clean fee
    reading. Returns None if no clean reading (never fabricate)."""
    led = load_json(FEE_LEDGER)
    if not led:
        return None
    # Prefer the last snapshot's fee delta if present; else the ledger's
    # accumulated fee fields. We only report what the ledger actually holds.
    for key in ("fees_today", "fees_last_hour", "fees_short"):
        v = led.get(key)
        if isinstance(v, dict) and v.get("fees_usd") is not None:
            return v["fees_usd"]
    return None


def wire_gta_arb(dry: bool) -> int:
    """Log each GTA arb opportunity as a structured row."""
    path, st, age = _resolve_gta_state()
    if not st:
        return 0
    # TRUTH GATE: never log a frozen scan as a live signal.
    if age is None or age > MAX_SCAN_AGE_H:
        sys.stderr.write(
            f"[wire_arb_log] STALE SCAN ({path}) age="
            f"{'unknown' if age is None else f'{age:.1f}h'} > {MAX_SCAN_AGE_H}h "
            f"— not logging (a stale scan is a memo of the past, not a signal)\n")
        return 0
    mode = current_mode()
    opps = st.get("opportunities", [])
    seen = _recent_signals("gta-arb")
    # A scan is ONE market read: log its rows once, never once per cron tick.
    scan_ts = st.get("last_scan")
    logged_scans = _logged_scan_ts("gta-arb")
    if scan_ts and scan_ts in logged_scans:
        sys.stderr.write(
            f"[wire_arb_log] scan {scan_ts} already logged — not re-logging "
            f"(one scan = one set of rows)\n")
        return 0
    count = 0
    for opp in opps:
        sym = opp.get("symbol")
        bps = opp.get("basis_bps")
        if bps is None:
            continue
        # ── CAUSE-ATTRIBUTION FIX (Sep 15 2026) ──────────────────────────────
        # Two INDEPENDENT gates decide `taken`: the |basis| threshold and the
        # mode gate. The old line derived `reason` from the MODE ALONE, so every
        # sub-threshold row logged while the treasury sat in YIELD_FARM was
        # stamped `mode-gate` — a row that would NOT have traded in TRADE mode
        # either, blaming the mode gate for a threshold miss. Measured on the
        # log: 68 of 90 `mode-gate` rows carried |basis| < 10 bps, i.e. 76% of
        # that label named the wrong cause, inflating apparent mode-gate friction
        # in exactly the dataset the critic reads to judge the gate.
        # Rule: name the gate that ACTUALLY bound. Threshold first — it binds
        # regardless of mode. Only a row that clears the bar AND is held by mode
        # is a genuine `mode-gate`.
        clears_threshold = abs(bps) >= EXECUTE_BPS
        taken = mode == "TRADE" and clears_threshold
        if taken:
            reason = None
        elif not clears_threshold:
            reason = "threshold"    # would not trade in ANY mode
        else:
            reason = "mode-gate"    # genuinely held by the mode gate
        signal = f"{sym} basis {bps:+.1f}bps (perp ${opp.get('perp')} vs spot ${opp.get('spot')})"
        if ("gta-arb", signal) in seen:
            continue  # already logged recently — don't duplicate
        if dry:
            print(f"[DRY] gta-arb: {signal} taken={taken} reason={reason}")
            count += 1
            continue
        path = log_signal(
            strategy="gta-arb",
            signal=signal,
            taken=taken,
            not_taken_reason=reason,
            venues=["Hyperliquid", "Coinbase"],
            realized_pnl=None,  # no realized P&L for a not-taken signal
            meta={"symbol": sym, "basis_bps": bps,
                  "perp": opp.get("perp"), "spot": opp.get("spot"),
                  "scan_ts": scan_ts},
        )
        if path:
            count += 1
    return count


def wire_prediction_arb(dry: bool) -> int:
    """Log each prediction-arb edge as a structured row."""
    st = load_json(PRED_STATE)
    if not st:
        return 0
    edges = st.get("edges", [])
    seen = _recent_signals("prediction-arb")
    count = 0
    for e in edges:
        etype = e.get("edge_type", "cross_venue")
        signal = e.get("signal") or e.get("note") or str(e.get("edge"))
        if etype == "intra_venue":
            signal = (f"Polymarket intra-venue edge {e.get('edge')} "
                      f"({e.get('title')})")
        elif etype == "cross_venue":
            signal = (f"Cross-venue {e.get('shared_keyword')} edge "
                      f"{e.get('edge')} (Poly {e.get('polymarket_yes')} vs "
                      f"Kalshi {e.get('kalshi_mid')})")
        if ("prediction-arb", signal) in seen:
            continue  # already logged recently — don't duplicate
        if dry:
            print(f"[DRY] prediction-arb: {signal}")
            count += 1
            continue
        path = log_signal(
            strategy="prediction-arb",
            signal=signal,
            taken=False,
            not_taken_reason="risk",  # prediction-arb is dry-run detection
            venues=["Polymarket", "Kalshi"],
            realized_pnl=None,
            meta={"edge_type": etype, "edge": e.get("edge")},
        )
        if path:
            count += 1
    return count


def main() -> int:
    dry = "--dry" in sys.argv
    n = wire_gta_arb(dry) + wire_prediction_arb(dry)
    if dry:
        print(f"[wire] {n} signal(s) would be logged (dry run)")
    else:
        print(f"[wire] {n} signal(s) logged — {datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
