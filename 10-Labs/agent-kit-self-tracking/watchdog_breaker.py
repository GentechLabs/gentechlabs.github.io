#!/usr/bin/env python3
"""The watchdog's CIRCUIT BREAKER — a limit on rescue retries.

WHY THIS EXISTS
---------------
Measured 2026-09-27: the watchdog attempted a rescue on jordan's book EVERY 10 MINUTES FOR OVER
TWO HOURS — **23 rescue runs between 04:49 and 07:12 UTC** — on a book it could never repair,
because the wallet was below the cost of the cycle. Every attempt burned RPC round-trips and gas
estimations to reach a conclusion it had ALREADY reached on the first pass.

There was no cap anywhere in the watchdog. No counter, no breaker, nothing.

Jordan, seeing the overnight churn: *"we seem to have these issues going on at night when the
watcher has a mind of its own"* — and asked whether to stop the pool at night instead.

THE ANSWER WAS NO, and the reason is arithmetic:
    the book earns            ~$0.19/day
    a stop + restart costs    ~$0.0996
    an 8-hour overnight stop  forgives ~$0.063 of yield to avoid spending $0.10
Stopping at night would PAY ten cents to avoid earning six. The pool is designed to run
continuously; idle time earns nothing while the gas is spent either way.

So the overnight churn was a SYMPTOM, not the cause. **A thing that retries forever is dangerous
at every hour.** The fix is a LIMIT, not a curfew.

THE RULE
--------
    attempt 1   -> allowed   (a single refusal can be transient — a bad RPC read, a reorg)
    attempt 2   -> allowed, and it TRIPS
    attempt 3+  -> SKIPPED   (one suppressed line, no run, no RPC, no gas)

RE-ARM IS AUTOMATIC, AND THAT IS THE PART THAT MATTERS
------------------------------------------------------
Any pass that does NOT produce a refusal CLEARS the entry. So when the wallet is topped up, the
very next healthy pass re-arms the breaker — no human action, no reset command, nothing to
remember. A breaker you have to reset by hand is a breaker that stays tripped.

THE KEY IS THE CONDITION, NEVER THE INCIDENT
--------------------------------------------
The breaker is keyed on WHICH refusal (e.g. CANNOT_FINISH), not on the pass, the timestamp, or a
hash. This is the same mistake the alert signature made once: a key that is unique by construction
can never match its predecessor, so a dedupe that cannot dedupe reports itself as working. A key
that changes on every incident can never trip.

Exit codes: 0 = GO (allowed to attempt), 10 = SKIP (breaker tripped).
"""
import argparse
import datetime
import json
import os
import sys

DEFAULT_MAX_ATTEMPTS = 2


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _load(path):
    try:
        with open(path) as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _save(path, d):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=1)
    os.replace(tmp, path)          # atomic: a half-written breaker must not be readable


def _max_attempts():
    try:
        return max(1, int(os.environ.get("BREAKER_MAX_ATTEMPTS", DEFAULT_MAX_ATTEMPTS)))
    except Exception:
        return DEFAULT_MAX_ATTEMPTS


def check(path, tenant, key):
    """SKIP if this condition has already been attempted the maximum number of times."""
    d = _load(path)
    e = d.get(tenant) or {}
    maxa = _max_attempts()
    if e.get("key") == key and int(e.get("attempts", 0)) >= maxa:
        e["suppressed"] = int(e.get("suppressed", 0)) + 1
        e["last_seen"] = _now()
        d[tenant] = e
        _save(path, d)
        return "SKIP", e
    return "GO", e


def refused(path, tenant, key):
    """Record that a rescue was ATTEMPTED and REFUSED. Returns the new attempt count."""
    d = _load(path)
    e = d.get(tenant) or {}
    now = _now()
    if e.get("key") == key:
        n = int(e.get("attempts", 0)) + 1
        first = e.get("first_seen") or now
    else:
        n = 1
        first = now
    d[tenant] = {"key": key, "attempts": n, "first_seen": first, "last_seen": now, "suppressed": 0}
    _save(path, d)
    return n


def clear(path, tenant):
    """RE-ARM. A pass that produced no refusal means the condition is gone."""
    d = _load(path)
    if tenant in d:
        removed = d.pop(tenant)
        _save(path, d)
        return removed
    return None


def status(path):
    return _load(path)


def main():
    ap = argparse.ArgumentParser(description="watchdog rescue circuit breaker")
    ap.add_argument("--state", required=True)
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--key", default="FLOOR")
    ap.add_argument("action", choices=["check", "refused", "clear", "status"])
    a = ap.parse_args()

    if a.action == "check":
        verdict, e = check(a.state, a.tenant, a.key)
        if verdict == "SKIP":
            print(f"SKIP {e.get('attempts')} attempts on {e.get('key')} since "
                  f"{e.get('first_seen')}, suppressed {e.get('suppressed')}x")
        else:
            print("GO")
        return 10 if verdict == "SKIP" else 0

    if a.action == "refused":
        n = refused(a.state, a.tenant, a.key)
        print(f"attempt {n} refused on {a.key}")
        return 0

    if a.action == "clear":
        r = clear(a.state, a.tenant)
        print(f"re-armed (cleared {r.get('key')} after {r.get('attempts')} attempts)" if r
              else "re-armed (nothing to clear)")
        return 0

    print(json.dumps(status(a.state), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
