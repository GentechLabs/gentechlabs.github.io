#!/usr/bin/env python3
"""Shared silence state for Steward watchdogs — suppress-until-resolution.

Jordan's rule (Aug 7 2026, reaffirmed Sep 3 2026): alert ONCE per condition,
then stay SILENT until it resolves or changes. A 10-minute cron must never
re-print the same failed attempt every run — that's noise, not monitoring.

Pattern (applies to every Steward watchdog by default):
    if silenced(key, retry_hours=6):
        return                      # already reported, unresolved -> quiet
    ... do work / print report ...
    if ok:   mark_success(key)      # condition resolved -> re-arm for next time
    else:    mark_failure(key, err) # condition persists -> suppression window

The suppression window doubles as a periodic-reminder timer: after N hours of
an UNRESOLVED condition, silenced() returns False again so Jordan gets one
reminder (not a spam stream). Any state change resets the cycle naturally.

State: one shared JSON file, atomic writes, safe for concurrent crons.
"""
import json
import os
import time
from datetime import datetime, timezone

STATE_FILE = os.environ.get(
    "STEWARD_SILENCE_STATE",
    "/root/.hermes/profiles/gentech-treasury/scripts/.steward-silence-state.json")


def _load() -> dict:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def silenced(key: str, retry_hours: float = 6.0) -> bool:
    """True -> suppress output this run (condition already reported, unresolved).

    Returns False when: never reported, resolved (re-armed), or the suppression
    window expired (periodic reminder of a persisting condition is allowed).
    """
    entry = _load().get(key)
    if not entry:
        return False
    if entry.get("resolved"):
        return False
    age_h = (time.time() - entry.get("ts", 0)) / 3600.0
    limit = float(entry.get("retry_hours", retry_hours))
    return age_h < limit


def mark_success(key: str, note: str = "") -> None:
    """Condition resolved — clear suppression so the NEXT occurrence alerts."""
    state = _load()
    if key in state:
        del state[key]
        _save(state)


def mark_failure(key: str, err: str = "", retry_hours: float = 6.0) -> None:
    """Condition persists (action failed or stayed actionable) — start/refresh
    the suppression window so the cron stays quiet until retry_hours elapse."""
    state = _load()
    prev = state.get(key, {})
    now = time.time()
    state[key] = {
        "ts": now,
        "resolved": False,
        "err": str(err)[:400],
        "count": int(prev.get("count", 0)) + 1,
        "retry_hours": float(retry_hours),
        "since": prev.get("since") or datetime.fromtimestamp(
            now, timezone.utc).isoformat(),
    }
    _save(state)


def status_line(key: str) -> str:
    """Human-readable one-liner about a key's suppression state (for reports)."""
    entry = _load().get(key)
    if not entry:
        return ""
    age_h = (time.time() - entry.get("ts", 0)) / 3600.0
    return (f"suppressed {age_h:.1f}h · {entry.get('count', 0)} attempts · "
            f"last: {str(entry.get('err', ''))[:120]}")