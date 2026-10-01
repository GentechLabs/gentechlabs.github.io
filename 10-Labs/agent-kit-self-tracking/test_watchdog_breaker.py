#!/usr/bin/env python3
"""Prove the rescue circuit breaker actually CAPS the retry loop.

THE INCIDENT THIS GUARDS (measured, 2026-09-27)
-----------------------------------------------
The watchdog attempted a rescue on jordan's book on EVERY 10-MINUTE PASS FROM 04:49 TO 07:12 UTC
— **23 attempts** — on a book it could never repair, because the wallet was below the cost of the
cycle. Each attempt re-derived the same conclusion. There was no cap anywhere in the file.

Jordan: *"we seem to have these issues going on at night when the watcher has a mind of its own."*

The fix is a LIMIT, not a curfew — the arithmetic rules out a nightly stop:
    the book earns           ~$0.19/day
    a stop + restart costs   ~$0.0996
    an 8-hour stop forgives  ~$0.063 of yield to avoid spending $0.10
Stopping at night would pay ten cents to avoid earning six.

WHAT MUST BE TRUE
-----------------
1. attempt 1 and 2 proceed; attempt 3+ is SKIPPED — the loop is capped at 2 per condition.
2. A DIFFERENT condition gets its own budget (one bad condition cannot silence another).
3. A healthy pass RE-ARMS it — clearing needs no human action.
4. The trip is keyed on the CONDITION, never on the incident (a key unique by construction can
   never match its predecessor — the defect the alert signature had).
5. The state file survives a crash: it is written atomically, and a corrupt file must not crash
   the watchdog (it must fail OPEN, but loudly — see #6).
6. A tripped breaker is NOT SILENCE. Suppressing the retry must not read as "everything is fine".
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import watchdog_breaker as B       # noqa: E402

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


TMP = tempfile.mkdtemp(prefix="breaker-test-")
SP = os.path.join(TMP, "b.json")

print("  ── 1. THE LOOP IS CAPPED: 2 attempts, then SKIP ──────────────────────")
v1, _ = B.check(SP, "jordan", "CANNOT_FINISH")
check("attempt 1 -> GO (a single refusal can be transient)", v1 == "GO")
n1 = B.refused(SP, "jordan", "CANNOT_FINISH")
check("refusal 1 recorded", n1 == 1, f"n={n1}")

v2, _ = B.check(SP, "jordan", "CANNOT_FINISH")
check("attempt 2 -> GO (still allowed — it might have been a bad read)", v2 == "GO")
n2 = B.refused(SP, "jordan", "CANNOT_FINISH")
check("refusal 2 recorded", n2 == 2, f"n={n2}")

v3, e3 = B.check(SP, "jordan", "CANNOT_FINISH")
check("attempt 3 -> SKIP  <<< the cap, the thing that was missing", v3 == "SKIP")
v4, _ = B.check(SP, "jordan", "CANNOT_FINISH")
v5, _ = B.check(SP, "jordan", "CANNOT_FINISH")
check("attempts 4 and 5 -> SKIP too (the loop is DEAD, not slowed)", v4 == v5 == "SKIP")
check("suppression counter is honest about how many were skipped", e3.get("suppressed", 0) >= 1,
      f"suppressed={e3.get('suppressed')}")

print("")
print("  ── 2. A DIFFERENT CONDITION GETS ITS OWN BUDGET ──────────────────────")
vu, _ = B.check(SP, "jordan", "UNREADABLE")
check("an unrelated condition is not silenced by the first one", vu == "GO")

print("")
print("  ── 3. A HEALTHY PASS RE-ARMS IT (no human action) ────────────────────")
check("breaker is OPEN before the healthy pass", B.check(SP, "jordan", "CANNOT_FINISH")[0] == "SKIP")
cleared = B.clear(SP, "jordan")
check("clear() reports what it cleared", bool(cleared) and cleared.get("key") == "CANNOT_FINISH")
vafter, _ = B.check(SP, "jordan", "CANNOT_FINISH")
check("after one healthy pass -> GO again  <<< self-clearing, not a switch to reset", vafter == "GO")

print("")
print("  ── 4. THE KEY IS THE CONDITION, NOT THE INCIDENT ─────────────────────")
# Self-contained: section 3 CLEARS the entry on purpose, so reading the shared state here would
# assert on a value the previous section deliberately removed. (Caught by running it: the first
# version of this check read key=None because the key had been re-armed three lines earlier.)
sp4 = os.path.join(TMP, "key.json")
B.refused(sp4, "jordan", "CANNOT_FINISH")
e = (B.status(sp4).get("jordan") or {})
check("stored key is a stable condition token", (e.get("key") or "") in
      ("CANNOT_FINISH", "UNREADABLE", "FLOOR"),
      f"key={e.get('key')!r}")
check("no hash/timestamp/nonce in the key (a key unique by construction cannot trip)",
      not any(t in (e.get("key") or "") for t in ("0x", ":", "T0")))
src = open(os.path.join(HERE, "watchdog_breaker.py")).read()
check("attempts are counted per CONDITION, not globally", 'e.get("key") == key' in src)

print("")
print("  ── 5. IT SURVIVES A CRASH AND A CORRUPT FILE ─────────────────────────")
bad = os.path.join(TMP, "corrupt.json")
open(bad, "w").write("{ this is not json")
try:
    v, _ = B.check(bad, "jordan", "CANNOT_FINISH")
    check("a corrupt state file does NOT crash the breaker", v == "GO", f"v={v}")
except Exception as ex:
    check("a corrupt state file does NOT crash the breaker", False, repr(ex))
check("and the state file is written atomically (tmp + os.replace)",
      "os.replace" in src)

print("")
print("  ── 6. A TRIPPED BREAKER IS NOT SILENCE ──────────────────────────────")
sh = open(os.path.join(HERE, "steward-watchdog.sh")).read()
check("the trip sets MATERIAL (a stranded book still reaches a human)", "BREAKER_TRIPPED=1" in sh)
check("the trip explains itself in the log", "CIRCUIT BREAKER OPEN" in sh)
check("it says a top-up is what clears it, not a mystery wait",
      "a wallet top-up is what clears it" in sh)
check("a second flag exists so SKIP does not fall into the re-arm path",
      "if [ \"$RESCUED\" -eq 0 ] && [ \"$BREAKER_TRIPPED\" -eq 0 ]" in sh,
      "with one flag the SKIP path clears the counter it just tripped")

print("")
print("  ── 7. IT IS WIRED IN, NOT AN ORPHAN ─────────────────────────────────")
check("the watchdog calls check before attempting", "--key \"$BKEY\" check" in sh)
check("the watchdog records the refusal after attempting", "--key \"$BKEY\" refused" in sh)
check("the watchdog re-arms on a healthy pass", "-tenant \"$TENANT\" clear" in sh
      or "--tenant \"$TENANT\" clear" in sh)
check("the state path is overridable so it can be TESTED", "BREAKER=" in sh)
check("the tripped state does NOT run recenter at all (no RPC, no gas)",
      sh.index("RESCUE SKIPPED") < sh.index("retrying with --rescue"),
      "the SKIP branch must come first")
sy = open(os.path.join(HERE, "sync-treasury-scripts.sh")).read()
check("watchdog_breaker.py is in the sync manifest (or it never deploys)",
      "watchdog_breaker.py" in sy)

print("")
print("  ── 8. THE COUNTERFACTUAL: WOULD IT HAVE STOPPED LAST NIGHT? ─────────")
# Replay the real sequence: 23 refusals across 04:49-07:12, one every ~10 min.
sp2 = os.path.join(TMP, "replay.json")
attempts = 0
skips = 0
for i in range(23):
    v, _ = B.check(sp2, "jordan", "CANNOT_FINISH")
    if v == "SKIP":
        skips += 1
    else:
        attempts += 1
        B.refused(sp2, "jordan", "CANNOT_FINISH")
print(f"      replayed 23 passes: {attempts} attempted, {skips} skipped")
check("it would have attempted at most 2 of last night's 23", attempts == 2, f"attempts={attempts}")
check("it would have skipped the other 21 (the churn, eliminated)", skips == 21, f"skips={skips}")
check("the wasted window drops from ~2.5 hours to ~10 minutes",
      attempts == 2 and skips >= 20)

print("")
print(f"  RESULT: {'PASS' if not FAIL else 'FAIL'} — {len(PASS)}/{len(PASS)+len(FAIL)} checks passed")
if FAIL:
    print("  failures:")
    for f in FAIL:
        print(f"    - {f}")
sys.exit(1 if FAIL else 0)
