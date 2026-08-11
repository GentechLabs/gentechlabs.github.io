#!/usr/bin/env python3
"""Tests for steward_progress.py deposit detection (no funds move)."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steward_progress as sp

failures = 0
def check(name, cond, detail=""):
    global failures
    status = "✅" if cond else "❌"
    if not cond:
        failures += 1
    print(f"{status} {name}" + (f" — {detail}" if detail else ""))

# Backup + redirect baseline file to a temp one so tests are hermetic
_orig = sp.BASELINE_FILE
_tmp = tempfile.mktemp(suffix=".json")
sp.BASELINE_FILE = _tmp

def set_baseline(value):
    with open(sp.BASELINE_FILE, "w") as f:
        json.dump({"value_usd": value, "ts": sp._now_iso()}, f)

try:
    # 1. No baseline -> no deposit (first run just establishes baseline)
    if os.path.exists(sp.BASELINE_FILE):
        os.remove(sp.BASELINE_FILE)
    d = sp.detect_deposit({"value_usd": 100.0})
    check("first run (no baseline) -> no deposit", d["detected"] is False, str(d["detected"]))

    # 2. Deposit detected: +10% from $100 -> $110
    set_baseline(100.0)
    d = sp.detect_deposit({"value_usd": 110.0})
    check("+10% deposit detected", d["detected"] is True, f"delta ${d['delta_usd']} pct {d.get('delta_pct')}%")
    check("delta_usd correct", d["delta_usd"] == 10.0, str(d["delta_usd"]))

    # 3. Price drift (small %) -> no deposit (below 2% floor)
    set_baseline(100.0)
    d = sp.detect_deposit({"value_usd": 101.0})
    check("+1% price drift -> NO deposit", d["detected"] is False, f"pct {d.get('delta_pct')}%")

    # 4. Below $ floor but high % -> no deposit (tiny absolute value)
    set_baseline(10.0)
    d = sp.detect_deposit({"value_usd": 10.5})
    check("+5% but under $1 floor -> NO deposit", d["detected"] is False, f"delta ${d['delta_usd']}")

    # 5. rank_and_progress: 0.07/day -> Unranked, progress toward Scout
    p = sp.rank_and_progress(0.072)
    check("0.07/day -> Unranked", p["rank"] == "Unranked", p["rank"])
    check("progress toward Scout", p["next_rank"] == "Scout", p["next_rank"])

    # 6. 30/day -> Raider (past Scout), next Warlord
    p = sp.rank_and_progress(30.0)
    check("30/day -> Raider", p["rank"] == "Raider", p["rank"])
    check("next Warlord", p["next_rank"] == "Warlord", p["next_rank"])

    # 7. 200/day -> Sovereign (max)
    p = sp.rank_and_progress(200.0)
    check("200/day -> Sovereign (max)", p["rank"] == "Sovereign", p["rank"])
    check("max -> no next", p["next_rank"] == "MAX", p["next_rank"])

    # 8. 250/day -> still Sovereign (beyond max)
    p = sp.rank_and_progress(250.0)
    check("250/day -> Sovereign max", p["rank"] == "Sovereign", p["rank"])

finally:
    # Restore original baseline file
    sp.BASELINE_FILE = _orig
    try:
        os.remove(_tmp)
    except OSError:
        pass

print(f"\n{'ALL PASS' if failures == 0 else f'{failures} FAILURES'}")
sys.exit(1 if failures else 0)
