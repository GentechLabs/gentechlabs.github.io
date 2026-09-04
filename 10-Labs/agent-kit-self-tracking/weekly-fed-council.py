#!/usr/bin/env python3
"""
Weekly Fed Council Meeting — voiced by Steve Harvey (Aug 21 2026)

Jordan's idea: instead of (or alongside) the weekly narrative rotation, hold a
weekly Fed council meeting where Steve Harvey's voice delivers the summary —
what happened this week, what we're looking forward to, and the decision for
next week. Sunday is the rest day and sets up the week ahead.

Flow:
  1. Gather the week's decisions from the Steward decision journal.
  2. Pull the week's council minutes from the Strategy-Journal.
  3. Write a Steve Harvey-style script (concrete-before-abstract, preacher cadence).
  4. Voice it with the Steve Harvey ElevenLabs clone.
  5. Deliver the audio path (cron sends it to the treasury group).

Reuses: steve-harvey-tts.py (voice generation) + steward_decisions.py (journal).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

JOURNAL = os.environ.get(
    "STEWARD_DECISIONS_FILE",
    "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/steward-decisions.jsonl")
JOURNAL_DIR = "/root/vaults/gentech/Treasury/Strategy-Journal"
TTS_SCRIPT = "/root/.hermes/profiles/gentech/scripts/steve-harvey-tts.py"
OUTPUT_DIR = "/tmp/steve-harvey-fed"

# How many days back counts as "this week" (Sunday meeting covers the prior 7).
WEEK_DAYS = 7


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _read_journal() -> list:
    try:
        with open(JOURNAL) as f:
            return [json.loads(l) for l in f if l.strip()]
    except FileNotFoundError:
        return []
    except Exception:
        return []


def _read_minutes() -> list:
    """Read this week's council minutes from the Strategy-Journal."""
    files = []
    try:
        for p in Path(JOURNAL_DIR).glob("*-council-*.md"):
            files.append(p)
    except Exception:
        return []
    # Filter to this week
    cutoff = _now() - timedelta(days=WEEK_DAYS)
    this_week = []
    for p in files:
        try:
            # filename like 2026-08-21-council-...
            date_str = p.name[:10]
            d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if d >= cutoff:
                this_week.append(p)
        except Exception:
            continue
    this_week.sort()
    return this_week


def _extract_minute_summary(path) -> str:
    """Pull the verdict + action lines from a council minute file."""
    try:
        text = path.read_text()
    except Exception:
        return ""
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## Verdict") or s.startswith("## Action") or s.startswith("**Verdict"):
            lines.append(s)
        elif s.startswith("- ") and any(k in s for k in ("HOLD", "deploy", "watch", "stay", "AVAX", "BTC")):
            lines.append(s)
    return " ".join(lines)[:600]


def _build_script(decisions: list, minutes: list) -> str:
    """Write the Steve Harvey-style Fed council script.

    Structure (concrete-before-abstract, preacher cadence):
      - Open: the week in one line
      - What happened (the decisions + market moves)
      - What we're looking forward to
      - The decision for next week
      - Close: the call to action
    """
    now = _now()
    week_start = (now - timedelta(days=WEEK_DAYS)).strftime("%B %d")
    week_end = now.strftime("%B %d")

    L = []
    L.append(f"Alright, listen. The Fed council is in session. This is the week of {week_start} to {week_end}, and we got some things to talk about.")

    # What happened — the decisions
    if decisions:
        L.append("Here's what we did this week. We made moves, and we made them on purpose.")
        for d in decisions[-5:]:
            action = d.get("action", "ACTION").upper()
            sym = d.get("symbol", "")
            why = d.get("rationale") or d.get("why") or ""
            if why:
                L.append(f"We {action.replace('_',' ').lower()} on {sym or 'the treasury'}. And here's the why: {why}")
    else:
        L.append("This week we held steady. No big moves, but we were watching.")

    # Market context from minutes
    if minutes:
        L.append("Now let me tell you what the market was doing.")
        for m in minutes[-3:]:
            summary = _extract_minute_summary(m)
            if summary:
                L.append(summary)

    # Looking forward
    L.append("Looking ahead, here's what we're watching. The regime is telling us where the money wants to go, and we're going to follow the data, not the noise.")

    # Decision for next week
    L.append("So here's the decision for next week. We stay disciplined. We let the farm earn, we keep the long riding, and we only move when the data says move. That's the play.")

    # Close
    L.append("That's the Fed council for this week. Stay sharp, stay patient, and let's go get it. God bless, and I'll see you next Sunday.")

    return " ".join(L)


def _voice(script: str) -> str:
    """Voice the script with the Steve Harvey clone. Returns the audio path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = _now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(OUTPUT_DIR, f"fed_council_{ts}.mp3")
    proc = subprocess.run(
        [sys.executable, TTS_SCRIPT, script],
        capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        print(f"ERROR: TTS failed: {proc.stderr[-500:]}", file=sys.stderr)
        return ""
    # steve-harvey-tts.py prints the output path
    path = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    if path and os.path.exists(path):
        return path
    return ""


def main() -> int:
    decisions = _read_journal()
    minutes = _read_minutes()

    script = _build_script(decisions, minutes)
    print("🎙️ WEEKLY FED COUNCIL — Steve Harvey")
    print(f"   Week: {(_now()-timedelta(days=WEEK_DAYS)).strftime('%b %d')} – {_now().strftime('%b %d')}")
    print(f"   Decisions this week: {len(decisions)} | Council minutes: {len(minutes)}")
    print("")
    print("📜 SCRIPT:")
    print(script)
    print("")

    audio = _voice(script)
    if audio:
        print(f"🎵 AUDIO: {audio}")
        print(f"MEDIA:{audio}")
    else:
        print("⚠️ Voice generation failed — script above is the fallback.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
