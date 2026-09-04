#!/usr/bin/env python3
"""
steward_decisions.py — the Steward's decision journal + report.

Every autonomous action the treasury takes is logged here with a RATIONALE (the
"why"), not just the "what". Jordan's rule (Aug 21 2026): whenever the treasury
makes a change, write him a report of what was decided AND why — the why is the
most important part because it proves the treasury is watching the data,
narratives, and regime, not just acting.

Two modes:
  --log  <json> : append one decision to the journal (called by an action).
                  Expects a JSON object via arg or stdin: {ts, action, symbol,
                  rationale, data}.
  (default)      emit the decisions since the last report (watermark), then
                  advance the watermark. Used by a no_agent cron so Jordan gets
                  a report of what changed and why — nothing spammy on idle.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

JOURNAL = os.environ.get(
    "STEWARD_DECISIONS_FILE",
    "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/steward-decisions.jsonl")
WATERMARK = JOURNAL + ".last_report"
# Fresh-truth audit (Aug 31 2026): the journal went 9.2 days without a write
# while this report kept firing "ok" every 4h — silence had become
# indistinguishable from a dead writer. A quiet journal now self-reports.
JOURNAL_LIVENESS_H = 72.0


def _journal_liveness_line() -> str:
    """Non-empty warning string if the journal looks orphaned, else ''."""
    try:
        age_h = (time.time() - os.path.getmtime(JOURNAL)) / 3600.0
    except OSError:
        return ("⚠️ **DECISIONS JOURNAL MISSING** — the journal file could not be "
                "read; autonomous decisions are not being recorded.")
    if age_h > JOURNAL_LIVENESS_H:
        return (f"⚠️ **JOURNAL QUIET {age_h/24:.1f}d** — no decisions logged since "
                f"{datetime.fromtimestamp(os.path.getmtime(JOURNAL), timezone.utc):%b %d %H:%M UTC}. "
                "Not a report of decisions: a health check. Council/executor "
                "writers should call steward_decisions.py --log on every action.")
    return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_entry(entry: dict) -> None:
    """Append one decision to the journal (append-only)."""
    entry.setdefault("ts", _now_iso())
    entry.setdefault("agent", "steward")
    os.makedirs(os.path.dirname(JOURNAL), exist_ok=True)
    with open(JOURNAL, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _read_entries() -> list:
    try:
        with open(JOURNAL) as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []
    except Exception:
        return []


def report() -> str:
    """Emit a human-readable report of the decisions taken since the last
    report, then advance the watermark. Empty output if nothing new."""
    entries = _read_entries()
    if not entries:
        # Fresh-truth audit (Aug 31 2026): empty journal used to mean "nothing to
        # report". But a MISSING journal is a dead writer, not a quiet one — that
        # must always speak. A present-but-quiet journal is surfaced by the
        # liveness check below instead of total silence.
        warn = _journal_liveness_line()
        if "MISSING" in warn:
            return warn
        return ""
    # Watermark = ts of the last entry we've already reported.
    last_ts = None
    try:
        with open(WATERMARK) as f:
            last_ts = f.read().strip()
    except FileNotFoundError:
        pass
    new = [e for e in entries if last_ts is None or e.get("ts", "") > last_ts]
    if not new:
        # Nothing new since the last report — but if the journal itself looks
        # orphaned, say so. Silence must not be a mask for a dead writer.
        return (_journal_liveness_line() or "").strip()

    lines = ["🛡️ STEWARD DECISIONS — what I did and why"]
    for e in new:
        lines.append("")
        lines.append(f"• **{e.get('action','action').upper()}** — {e.get('symbol','')}".rstrip())
        why = e.get("rationale") or e.get("why") or ""
        if why:
            lines.append(f"  **Why:** {why}")
        for k in ("data", "detail"):
            v = e.get(k)
            if v:
                lines.append(f"  {json.dumps(v) if isinstance(v,(dict,list)) else v}")
        lines.append(f"  _when: {e.get('ts','')}_")
    lines.append("")

    # advance watermark
    try:
        with open(WATERMARK, "w") as f:
            f.write(new[-1].get("ts", ""))
    except OSError:
        pass
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--log":
        payload = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        try:
            log_entry(json.loads(payload))
            print("logged")
        except Exception as e:
            print(f"log error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(report())
