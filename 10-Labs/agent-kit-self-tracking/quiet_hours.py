#!/usr/bin/env python3
"""
Quiet Hours helper for cron scripts.
Silences non-critical jobs overnight: 22:00 - 08:00 ET (America/New_York).

Exposes a single function `is_quiet_hours()` that returns True when the
current ET wall-clock time falls in the quiet window. Scripts that import
this should `sys.exit(0)` (silent) when it returns True.

The window is configurable via QUIET_START / QUIET_END env vars (0-23) so
other jobs can reuse the module with their own schedule.
"""

import os
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Python < 3.9 fallback
    import time

    class _ZoneInfo:
        def __init__(self, key):
            self.key = key

        def __eq__(self, other):
            return isinstance(other, _ZoneInfo) and self.key == other.key

    def _now_et_hour():
        # Best-effort: EST = UTC-5 (winter), EDT = UTC-4 (summer). Approx.
        ts = time.time()
        # Approximate DST: US DST runs 2nd Sun Mar to 1st Sun Nov.
        lt = time.localtime(ts)
        is_dst = lt.tm_isdst
        offset = -4 if is_dst else -5
        return (datetime.utcfromtimestamp(ts).hour + 24 + offset) % 24

    def _get_hour():
        return _now_et_hour()
else:
    def _get_hour():
        return datetime.now(ZoneInfo("America/New_York")).hour


def is_quiet_hours():
    """Return True if now is inside the quiet window (default 22:00-08:00 ET)."""
    try:
        start = int(os.environ.get("QUIET_START", "22"))
        end = int(os.environ.get("QUIET_END", "8"))
    except ValueError:
        start, end = 22, 8
    hour = _get_hour()
    # ── THE NON-WRAPPING CASE WAS A NO-OP (fixed 2026-09-29) ─────────────────────────────────
    # This used to read:
    #     if start < end:
    #         # e.g. 22->8 spans midnight handled by the OR below
    #         pass
    #     return hour >= start or hour < end
    # The `pass` branch did NOTHING, so the wrapping formula ran for every window. For a
    # non-wrapping window like 08:00-22:00 that INVERTS the answer — `hour >= 8 or hour < 22`
    # is True for all 24 hours, so a daytime window was quiet ALL DAY and active never.
    # Only a wrapping window is correct today, which is why this stayed hidden: the single
    # caller that sets one (buylist-cron.sh, 22->7) wraps. Any future caller using a
    # same-day window would have had the guard silently swallow every run.
    #
    # The three cases are genuinely different and are now all handled:
    if start == end:
        # Zero-width window = quiet hours DISABLED. Note the old wrapping formula returned
        # True for every hour here, so the natural way to switch the guard off (START==END)
        # switched it permanently ON instead.
        return False
    if start < end:
        # Same-day window (e.g. 08:00-22:00): quiet strictly inside it.
        return start <= hour < end
    # Window spans midnight (start=22, end=8): quiet from 22:00 to 23:59
    # and 00:00 to 07:59. So quiet when hour >= start OR hour < end.
    return hour >= start or hour < end


if __name__ == "__main__":
    print("Quiet hours active" if is_quiet_hours() else "Active hours")
