#!/usr/bin/env python3
"""Arb Log — Phase 0 structured signal logger for the self-improving arb loop.

Append-only JSONL, one file per month, at Treasury/arb-log/YYYY-MM.jsonl.
One row per arb signal. Real P&L only (from the fixed fee ledger — never
fabricated). Mode-gate respected: signals are logged even when the mode-gate
holds them (that's data for the critic).

Schema (per handoff 2026-09-10-self-improving-arb-loop-phase0):
  ts            : UTC ISO timestamp
  strategy      : gta-arb | prediction-arb | cross-venue | yield-farm-switch
  signal        : human-readable description (e.g. "ONDO basis +12.5bps")
  taken         : true/false
  not_taken_reason : mode-gate | threshold | risk | none (when taken)
  venues        : list of venue codes (LFJ/Blackhole/Meteora/Orca/Raydium/
                  Hyperliquid/OKX/Coinbase/Polymarket/Kalshi)
  realized_pnl  : float USD from the fixed fee ledger, or null (no trade)
  regime        : market regime at signal time (Bull/Range/CRAB + vol)
  meta          : optional dict of extra structured fields

Usage:
  from arb_log import log_signal
  log_signal(strategy="gta-arb", signal="ONDO basis +12.5bps",
             taken=False, not_taken_reason="mode-gate",
             venues=["Hyperliquid","Coinbase"], realized_pnl=None,
             regime="RANGE_BOUND", meta={"basis_bps":12.5})
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

# Default log root: Treasury/arb-log/ under the vault. Overridable so the
# running profile scripts can point at the same shared location.
DEFAULT_LOG_ROOT = "/root/vaults/gentech/Treasury/arb-log"
LOG_ROOT = os.environ.get("ARB_LOG_ROOT", DEFAULT_LOG_ROOT)

# Regime state file (written by regime_classifier.py). Read for the regime
# label at signal time. Falls back to "UNKNOWN" if unavailable.
REGIME_STATE = os.environ.get(
    "AAE_REGIME_STATE", "/root/.hermes/scripts/.aae-regime-state.json"
)


def _month_path() -> str:
    """Path to the current month's JSONL file."""
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return os.path.join(LOG_ROOT, f"{month}.jsonl")


def read_regime() -> dict:
    """Read the current market regime from the classifier state file."""
    try:
        with open(REGIME_STATE) as f:
            st = json.load(f)
        regime = st.get("regime", "UNKNOWN")
        conf = st.get("confidence")
        atr = (st.get("details") or {}).get("atr_pct")
        return {
            "regime": regime,
            "confidence": conf,
            "atr_pct": atr,
            "volatility": "HIGH" if (atr or 0) > 0.08 else
                          ("LOW" if (atr or 0) < 0.03 else "MED"),
        }
    except Exception:
        return {"regime": "UNKNOWN", "confidence": None,
                "atr_pct": None, "volatility": None}


def log_signal(*, strategy: str, signal: str, taken: bool,
               not_taken_reason: str | None = None,
               venues: list[str] | None = None,
               realized_pnl: float | None = None,
               regime: str | None = None,
               meta: dict | None = None) -> str | None:
    """Append one signal row to the arb log. Returns the file path, or None
    on write failure (never raises — logging must not break the caller)."""
    reg = read_regime()
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "strategy": strategy,
        "signal": signal,
        "taken": bool(taken),
        "not_taken_reason": not_taken_reason if not taken else None,
        "venues": venues or [],
        "realized_pnl": realized_pnl,  # real on-chain only, else None
        "regime": regime or reg.get("regime", "UNKNOWN"),
        "regime_volatility": reg.get("volatility"),
        "meta": meta or {},
    }
    try:
        os.makedirs(LOG_ROOT, exist_ok=True)
        path = _month_path()
        with open(path, "a") as f:
            f.write(json.dumps(row) + "\n")
        return path
    except OSError as e:
        import sys
        sys.stderr.write(f"[arb_log] write failed: {e}\n")
        return None


if __name__ == "__main__":
    # Smoke test: log a synthetic row to prove the writer works.
    p = log_signal(strategy="gta-arb", signal="SMOKE-TEST row",
                   taken=False, not_taken_reason="threshold",
                   venues=["Hyperliquid", "Coinbase"], realized_pnl=None,
                   meta={"test": True})
    print(f"wrote -> {p}")
