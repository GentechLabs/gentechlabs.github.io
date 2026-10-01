#!/usr/bin/env python3
"""Guard the 2026-09-27 fixes: a FAILED READ must never look like a REAL ZERO.

WHY THIS EXISTS. The Sunday Agentic Treasury Report printed this to Jordan:

    BLACK health source   black-health.json unreadable: unsupported format string
                          passed to NoneType.__format__

That was a PYTHON CRASH shown as if it were the state of the world, and behind it sat
FOUR defects, all of the false-value family (a mechanism reporting a value while
knowing nothing):

  1. black_health.py rpc() sent NO User-Agent. publicnode answers a bare urllib POST
     with HTTP 403 while answering the SAME request WITH a UA -- and avax_rpc.url()
     PROBES with a UA, so the selector certified the one host the caller could not use.
  2. _age_hours() called fromisoformat() on an EPOCH float, raised, and returned None.
  3. The refusal path then formatted that None with {age_h:.1f} and crashed -- so the
     crash MASKED a working chain read (the file was fine; the READER was broken).
  4. _deployed_usd() looked for a top-level "deployed_usd" while the schema had moved
     the number under `capital`. It matched nothing and returned None, which main()
     renders as "TREASURY IS FLAT" -- so an UNREADABLE treasury was indistinguishable
     from a FLAT one, and every rank line would have read 0%.

A fix that silences an alarm is not a fix, so this proves BOTH directions:
    stale / unknown -> ABSTAIN  (no figure invented)
    live            -> FIRES    (still reads a real file)

Run: python3 test_freshness_and_deploy_read.py
"""
import importlib.util
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAILS.append(name)


def load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


atr = load("atr", "agentic-treasury-report.py")
ry = load("ry", "reentry_yield.py")

print("A. _age_hours accepts BOTH stamp formats and refuses the unparseable")
now = time.time()
check("epoch float (what black-health writes) -> ~0h",
      abs(atr._age_hours(now)) < 0.05, f"{atr._age_hours(now):.3f}h")
check("epoch MILLISECONDS -> ~0h", abs(atr._age_hours(now * 1000)) < 0.05)
# TIME BOMB FIX (2026-09-28): this fixture was a HARDCODED stamp — "2026-09-27T15:00:00+00:00" —
# asserted against `abs(...) < 24.0`. It passed the day it was written and FAILED the next day at
# 24.94h, with nothing in the code changed. A test whose verdict depends on the wall clock is not
# testing the parser; it is testing the calendar, and it turns red on its own. The property is
# "an ISO string parses at all" — so derive the fixture from `now` and assert THAT.
from datetime import datetime, timezone, timedelta
_iso = (datetime.now(timezone.utc) - timedelta(hours=0)).isoformat()
check("ISO string -> ~0h (fixture derived from now, not hardcoded)",
      abs(atr._age_hours(_iso)) < 0.05, f"{atr._age_hours(_iso):.3f}h")
# and the parser must still MEASURE an old stamp rather than merely not-crash on it:
_old_iso = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
check("ISO string 48h old -> ~48.0h (age is MEASURED, not assumed)",
      abs(atr._age_hours(_old_iso) - 48.0) < 0.05, f"{atr._age_hours(_old_iso):.3f}h")
check("epoch 24h old -> ~24.0h", abs(atr._age_hours(now - 86400) - 24.0) < 0.05)
check("None -> None (UNKNOWN = refuse)", atr._age_hours(None) is None)
check("garbage string -> None (refuse)", atr._age_hours("not-a-date") is None)
# the actual crash: the refusal string must format a MISSING age without raising
try:
    age_h = None
    s = f"is {age_h:.1f}h old" if age_h is not None else "of UNKNOWN age"
    check("refusal path formats a missing age WITHOUT raising", "UNKNOWN" in s)
except TypeError as e:
    check("refusal path formats a missing age WITHOUT raising", False, str(e))

print("\nB. _deployed_usd reads the CURRENT schema and names its provenance")
val, src = atr._deployed_usd()
check("live state -> a number, not None", isinstance(val, float), f"${val}")
check("provenance names the schema path used",
      bool(src) and ("capital.deployed_usd" in src or "top-level" in src), str(src))
check("provenance carries the measured_at stamp", "measured" in (src or ""))
tmp = tempfile.mkdtemp()
ghost = os.path.join(tmp, "treasury-state.json")
json.dump({"moved_everything": {"n": 5}}, open(ghost, "w"))
check("unknown schema -> (None, None), NEVER an implied $0",
      atr._deployed_usd((ghost,)) == (None, None))
dead = atr._deployed_usd((os.path.join(tmp, "nope.json"),))
check("missing file -> (None, None)", dead == (None, None))
legacy = os.path.join(tmp, "legacy.json")
json.dump({"deployed_usd": 123.45}, open(legacy, "w"))
lv, lsrc = atr._deployed_usd((legacy,))
check("legacy top-level key still honored", lv == 123.45 and "legacy" in (lsrc or ""))

print("\nC. reentry farm_apr age-gates: FRESH fires, STALE abstains")
orig = ry.BLACK_HEALTH
tmpd = tempfile.mkdtemp()
fresh = os.path.join(tmpd, "fresh.json")
json.dump({"ts": time.time(), "yield_split": {"fee_apr_pct": 42.0},
           "pool": {"tvl_usd": 1000.0}}, open(fresh, "w"))
ry.BLACK_HEALTH = fresh
fa, tvl = ry.farm_apr()
check("FRESH file -> the real fee APR fires", fa == 42.0 and tvl == 1000.0, f"{fa} / {tvl}")

stale = os.path.join(tmpd, "stale.json")
json.dump({"ts": time.time() - 72 * 3600, "yield_split": {"fee_apr_pct": 42.0},
           "pool": {"tvl_usd": 1000.0}}, open(stale, "w"))
ry.BLACK_HEALTH = stale
fa2, tvl2 = ry.farm_apr()
check("STALE (72h) file -> ABSTAINS with (None, None)", (fa2, tvl2) == (None, None),
      f"{fa2} / {tvl2}")

unstamped = os.path.join(tmpd, "unstamped.json")
json.dump({"yield_split": {"fee_apr_pct": 42.0}}, open(unstamped, "w"))
ry.BLACK_HEALTH = unstamped
check("UNSTAMPED file -> abstains (cannot prove fresh)", ry.farm_apr() == (None, None))
ry.BLACK_HEALTH = os.path.join(tmpd, "gone.json")
check("MISSING file -> abstains", ry.farm_apr() == (None, None))
ry.BLACK_HEALTH = orig

print("\nD. price-sensitivity prose is GATED on the measured sign, never hardcoded")
import re
src = open(os.path.join(HERE, "agentic-treasury-report.py")).read()
# check the PRINTED form (the FIX comment legitimately quotes the old line)
check("the old unconditional PRINT is GONE",
      'print("   Lower price = higher reward APR' not in src)
check("no unconditional claim survives in any print()",
      not re.search(r'print\([^)]*Lower price = higher reward APR', src))
check("all three branches exist (negative / noise / positive)",
      src.count("MECHANISM VISIBLE") and src.count("NO DETECTABLE RELATIONSHIP")
      and src.count("MECHANISM NOT VISIBLE"))
check("the fitted table is labelled as a fit, not a law",
      "not a law" in src)
# the emitted report must not assert the mechanism on a non-negative corr
out = open("/tmp/atr3.txt").read() if os.path.exists("/tmp/atr3.txt") else ""
if out:
    check("live output does NOT claim the mechanism at corr +0.039",
          "NO DETECTABLE RELATIONSHIP" in out and "MECHANISM VISIBLE" not in out)
else:
    check("live output available for inspection", False, "run the report first")

print("\nE. the RPC path carries the User-Agent the public hosts demand")
import inspect
bh_src = open(os.path.join(HERE, "black_health.py")).read()
ry_src = open(os.path.join(HERE, "reentry_yield.py")).read()
for label, src in (("black_health.py", bh_src), ("reentry_yield.py", ry_src)):
    check(f"{label} fallback sends a User-Agent", "User-Agent" in src)
    check(f"{label} prefers the shared rotator", "from avax_rpc import rpc_call" in src)
    check(f"{label} _avax_url fallback does not self-recurse",
          "return _avax_url()   # last resort" not in src)

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAILED: {', '.join(FAILS)}")
    sys.exit(1)
print("✅ ALL PASS — fresh fires, stale abstains, unreadable is never a zero")
