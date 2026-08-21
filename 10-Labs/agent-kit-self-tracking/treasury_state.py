#!/usr/bin/env python3
"""
treasury_state.py — the SHARED BRAIN for the Steward treasury.

Every cron job reads treasury-state.json through this module BEFORE it emits a
signal or acts. It enforces the single source of truth: there is ONE mode, ONE
regime, ONE capital picture — and no department gets to contradict it.

Fixes (Aug 21 2026): the trader executor fired "ENTER ONDO" while the council
was holding the yield farm — two departments reading two different state files.
Now there's one shared state every job respects.

Key functions:
  load_state()          -> dict (the shared treasury-state.json)
  get_mode()            -> str (YIELD_FARM | TRADE | DRY_POWDER)
  can_trade()           -> bool (mode allows trade signals?)
  assert_mode(*modes)   -> raises ModeGateError if current mode not allowed
  gated_signal(category, ...) -> None; a job that is mode-gated calls this to
                                 know whether it may EMIT its normal output.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

# Canonical state file. Cron jobs may point here via env override.
STATE_PATH = os.environ.get(
    "TREASURY_STATE_FILE",
    "/root/ProtoJay4789.github.io/10-Labs/agent-kit-self-tracking/treasury-state.json")

# Modes the treasury can be in. Only the council changes mode.
MODES = {"YIELD_FARM", "TRADE", "DRY_POWDER"}

# Which modes allow which department to emit its normal signal.
# - trader/executor only emits ENTER/EXIT when mode is TRADE.
# - arb monitor reports basis but never auto-pulls the farm.
# - watchdog/heartbeat always allowed (they maintain the farm).
MODE_ALLOW = {
    "trade_signal": {"TRADE"},
    "arb_autoexec": set(),          # never auto-exec a farm pull
    "arb_report": MODES,
    "farm_maintenance": MODES,      # watchdog re-center always allowed
    "status_pulse": MODES,
    "council_verdict": MODES,       # council always speaks (it changes mode)
}


class ModeGateError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state() -> dict:
    """Load the shared treasury state. Never raises on a transient read error —
    returns a conservative default so a gated job stays quiet rather than firing
    against an unknown mode."""
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except Exception:
        return {"mode": "YIELD_FARM", "regime": {"value": "UNKNOWN"}}


def get_mode(state: dict | None = None) -> str:
    state = state or load_state()
    mode = state.get("mode", "YIELD_FARM")
    return mode if mode in MODES else "YIELD_FARM"


def get_regime(state: dict | None = None) -> str:
    state = state or load_state()
    reg = state.get("regime", {})
    return reg.get("value", "UNKNOWN") if isinstance(reg, dict) else "UNKNOWN"


def can_trade(state: dict | None = None) -> bool:
    """True only when the treasury is explicitly in TRADE mode."""
    return get_mode(state) == "TRADE"


def assert_mode(category: str, state: dict | None = None) -> str:
    """Raise ModeGateError if the current mode is not allowed for `category`.

    A department that is mode-gated calls this; if it raises, the caller should
    stay SILENT (or emit a short 'held' line) instead of firing its normal signal.
    """
    allowed = MODE_ALLOW.get(category)
    if allowed is None:
        raise ModeGateError(f"unknown gated category: {category}")
    mode = get_mode(state)
    if mode not in allowed:
        raise ModeGateError(
            f"mode '{mode}' does not allow '{category}' (allowed: {sorted(allowed)})")
    return mode


def gated(category: str) -> bool:
    """Convenience: returns True if current mode allows this category to emit."""
    try:
        assert_mode(category)
        return True
    except ModeGateError:
        return False


def held_line(category: str, signal: str) -> str:
    """Build a single, non-conflicting 'held' line a gated job can emit instead
    of a full signal, so Jordan sees ONE coherent message."""
    return (f"⏸ [{category}] mode={get_mode()} — {signal} held "
            f"(signal noted, but treasury is not in a mode that acts on it)")


if __name__ == "__main__":
    s = load_state()
    print(f"mode={get_mode(s)} regime={get_regime(s)} can_trade={can_trade(s)}")
