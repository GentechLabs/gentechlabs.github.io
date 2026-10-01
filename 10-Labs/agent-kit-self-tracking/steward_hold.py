#!/usr/bin/env python3
"""
steward_hold.py — the operator's "I am out of the market ON PURPOSE" flag.

WHY THIS EXISTS (2026-09-28)
    Jordan exited the LFJ pool deliberately, ahead of a macro event, to hold USDC dry powder
    ("getting out of the pool and holding dry powder... we'll just get out for now and come back
    maybe some time next week").

    Ninety seconds later the Position Watchdog re-entered his capital.

    Nothing was broken. The machine did exactly what it was told to do. `lfj_recenter.py` carries
    this line at the flat-book branch:

        "A book with a funded wallet and no position is not a report, it is a task. Deploy it."

    That rule is RIGHT in almost every case — it is the fix for the real, repeated failure of a
    book sitting flat all night because nobody ran a command. But it made flatness a CONDITION TO
    REPAIR, with no way for the operator to say "flat is the position." A human instruction to hold
    dry powder and an autonomy rule to deploy idle capital were in direct conflict, and the rule
    won — silently, in a five-minute loop, with no dialogue anywhere that could express the
    difference.

    This module is that missing dialogue. It is a HOLD flag: when set for a tenant, a flat book is
    a DELIBERATE STATE, not a defect, and the automation must not re-enter it.

DESIGN RULES (each one is a defect we have already paid for)
    1. FAIL OPEN, NEVER SILENTLY FAIL CLOSED. Any read problem — missing file, unreadable, bad
       JSON, unexpected type — resolves to "no hold", i.e. the old behaviour. A flag store that
       fails closed would strand capital because of a typo, which is worse than the bug it fixes.
    2. THE REASON IS PART OF THE FLAG. A bare boolean cannot answer "why is this book flat?" six
       hours later. `set_hold` requires a reason and refuses without one.
    3. IT EXPIRES. A hold nobody remembers to clear is a treasury that has quietly stopped working.
       `until` is mandatory and bounded; `is_hold()` treats an elapsed hold as released and says so.
    4. IT IS DATED. Jordan's standing rule is "no stale data" — a hold with no timestamp cannot be
       told from a hold set last week.

CLI (used by agents and by Jordan):
    python3 steward_hold.py --tenant jordan --reason "dry powder ahead of the 2pm ET speech" \
        --until 2026-10-05T00:00:00Z
    python3 steward_hold.py --tenant jordan --clear
    python3 steward_hold.py --tenant jordan --status
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HOLD_PATH = os.path.join(HERE, ".steward-hold.json")

# The longest a hold may run unattended. A hold is a decision with a date, not a new default.
MAX_HOLD_DAYS = 60


def _now():
    return datetime.now(timezone.utc)


def _parse_ts(value):
    """Parse an ISO stamp tolerantly; return None when it cannot be trusted."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None
    if not isinstance(value, str):
        return None
    s = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _load(path=None):
    """Return the holds dict. NEVER raises — an unreadable store means 'no holds', not a crash."""
    path = path or os.environ.get("STEWARD_HOLD_PATH") or DEFAULT_HOLD_PATH
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    holds = data.get("holds") if isinstance(data, dict) else None
    return holds if isinstance(holds, dict) else {}


def _save(holds, path=None):
    path = path or os.environ.get("STEWARD_HOLD_PATH") or DEFAULT_HOLD_PATH
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w") as fh:
        json.dump({"holds": holds, "updated_at": _now().isoformat()}, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def is_hold(tenant, path=None):
    """
    THE GATE. Returns (held: bool, why: str).

    held=True  -> this tenant is deliberately flat; DO NOT auto re-enter.
    held=False -> no hold, or the hold could not be read, or it has expired. Proceed as before.

    Fails OPEN on every error path: a broken flag store must never strand capital.
    """
    try:
        holds = _load(path)
        entry = holds.get(tenant)
        if not isinstance(entry, dict):
            return False, ""
        until = _parse_ts(entry.get("until"))
        if until is None:
            # An undated hold cannot be distinguished from a forgotten one. Release it and say so.
            return False, ""
        if _now() >= until:
            return False, ""
        reason = str(entry.get("reason") or "no reason recorded")
        since = str(entry.get("since") or "unknown time")
        return True, f"{reason} (held since {since}, until {until.isoformat()})"
    except Exception:
        # Fail open. Every line above is already guarded, but a gate that can strand a treasury
        # must not depend on that: if anything unforeseen happens, proceed.
        return False, ""


def set_hold(tenant, reason, until, path=None):
    """Set a hold. Requires a tenant, a reason and an expiry — all three, or it refuses."""
    if not tenant:
        raise ValueError("set_hold requires a tenant")
    if not (reason or "").strip():
        raise ValueError("set_hold requires a reason — a bare flag cannot answer 'why is this flat?'")
    dt = _parse_ts(until)
    if dt is None:
        raise ValueError(f"set_hold requires a parseable 'until' (got {until!r}) — an unbounded "
                         f"hold is a treasury that quietly stops working")
    now = _now()
    if dt <= now:
        raise ValueError(f"'until' {dt.isoformat()} is not in the future")
    if (dt - now).days > MAX_HOLD_DAYS:
        raise ValueError(f"'until' is more than {MAX_HOLD_DAYS} days away — keep it bounded")
    holds = _load(path)
    holds[tenant] = {"reason": reason.strip(), "since": now.isoformat(),
                     "until": dt.isoformat(), "set_by": os.environ.get("STEWARD_HOLD_SET_BY", "agent")}
    _save(holds, path)
    return holds[tenant]


def clear_hold(tenant, path=None):
    """Clear a hold. Returns True if something was cleared, False if there was nothing to clear."""
    holds = _load(path)
    existed = tenant in holds
    holds.pop(tenant, None)
    _save(holds, path)
    return existed


def status(path=None):
    """Every hold with its live/expired state — for the hub, the council and the watchdog."""
    holds = _load(path)
    out = []
    for tenant, entry in sorted(holds.items()):
        if not isinstance(entry, dict):
            continue
        until = _parse_ts(entry.get("until"))
        live = until is not None and _now() < until
        out.append({"tenant": tenant, "reason": entry.get("reason"),
                    "since": entry.get("since"), "until": entry.get("until"),
                    "live": live, "expired": until is not None and not live})
    return out


def main():
    ap = argparse.ArgumentParser(description="Operator HOLD flag — a deliberate flat book.")
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--reason")
    ap.add_argument("--until", help="ISO timestamp the hold expires (required to set)")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()

    if a.clear:
        print(f"✅ hold cleared for {a.tenant}" if clear_hold(a.tenant)
              else f"no hold was set for {a.tenant} — nothing to clear")
        return 0
    if a.status:
        rows = status()
        # DEFECT FIXED (2026-09-28): --status ignored --tenant and always listed every hold. Asking
        # "is jordan held?" and getting "jordan: HELD" was right by accident; asking about a tenant
        # with NO hold printed ANOTHER tenant's line, which reads as an answer about the wrong book.
        # --tenant is required by the parser, so honour it.
        rows = [r for r in rows if r["tenant"] == a.tenant]
        if not rows:
            print(f"no hold set for {a.tenant} — this book is free to re-enter")
            return 0
        for r in rows:
            print(f"  {r['tenant']}: {'⏸ HELD' if r['live'] else '⌛ EXPIRED'} — {r['reason']} "
                  f"(until {r['until']})")
        return 0
    if not a.reason or not a.until:
        print("❌ to SET a hold you need --reason and --until (both are required)")
        return 1
    try:
        e = set_hold(a.tenant, a.reason, a.until)
    except ValueError as exc:
        print(f"❌ {exc}")
        return 1
    print(f"⏸ HOLD SET for {e and a.tenant} — {e['reason']} (until {e['until']})")
    print("   the automation will NOT auto re-enter this book while the hold is live.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
