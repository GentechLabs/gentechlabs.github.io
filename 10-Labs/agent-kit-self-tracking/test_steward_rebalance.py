#!/usr/bin/env python3
"""Tests for steward_rebalance.py decision logic (no funds move)."""
import json, os, sys, time
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steward_rebalance as sr

def datetime_now():
    return datetime.now(timezone.utc).isoformat()

failures = 0
def check(name, cond, detail=""):
    global failures
    status = "✅" if cond else "❌"
    if not cond:
        failures += 1
    print(f"{status} {name}" + (f" — {detail}" if detail else ""))

# Fixture: an OUT-of-range position (as discover_positions returns it)
out_pos = {
    "chain": "avalanche", "wallet": "0x" + "a"*40,
    "positions": [{"name": "LFJ", "type": "lfj_v22", "bins": 11,
                   "inRange": False, "read": "11 bins · OUT"}],
}
# In-range position
in_pos = {
    "chain": "avalanche", "wallet": "0x" + "a"*40,
    "positions": [{"name": "LFJ", "type": "lfj_v22", "bins": 11,
                   "inRange": True, "read": "11 bins · IN"}],
}
# No position
no_pos = {"chain": "avalanche", "wallet": "0x" + "a"*40, "positions": []}

# 1. OUT + RANGE_BOUND -> REBALANCE with CURVE
d = sr.decide(out_pos, {"regime": "RANGE_BOUND"})
check("OUT + RANGE_BOUND -> rebalance", d["action"] == "rebalance", d["action"])
check("RANGE_BOUND -> CURVE shape", d["shape"] == "CURVE", d["shape"])

# 2. OUT + HIGH_VOLATILITY -> REBALANCE with BID_ASK (shape switches by regime)
d = sr.decide(out_pos, {"regime": "HIGH_VOLATILITY"})
check("OUT + HIGH_VOLATILITY -> BID_ASK", d["shape"] == "BID_ASK", d["shape"])

# 3. IN + RANGE_BOUND -> HOLD (stay in pool)
d = sr.decide(in_pos, {"regime": "RANGE_BOUND"})
check("IN -> hold (stay in pool)", d["action"] == "hold", d["action"])
check("IN fee eff 100%", d["fee_eff"] == 100.0, str(d["fee_eff"]))

# 4. No position -> HOLD (nothing to act on)
d = sr.decide(no_pos, {"regime": "RANGE_BOUND"})
check("no position -> hold", d["action"] == "hold", d["action"])

# 5. OUT but rebalanced recently -> HOLD (frequency guard)
recent = (datetime.now(timezone.utc) - timedelta(seconds=300)).isoformat()
d = sr.decide(out_pos, {"regime": "RANGE_BOUND"}, last_rebalance_ts=recent)
check("recent rebalance -> hold (10min guard)", d["action"] == "hold", d["action"])

# 6. OUT + stale rebalance stamp -> REBALANCE allowed
stale = (datetime.now(timezone.utc) - timedelta(seconds=3600)).isoformat()
d = sr.decide(out_pos, {"regime": "RANGE_BOUND"}, last_rebalance_ts=stale)
check("old rebalance -> rebalance again", d["action"] == "rebalance", d["action"])

# 7. fee_efficiency helper
check("fee_eff OUT = 0", sr.fee_efficiency(out_pos) == 0.0)
check("fee_eff IN = 100", sr.fee_efficiency(in_pos) == 100.0)

print(f"\n{'ALL PASS' if failures == 0 else f'{failures} FAILURES'}")
sys.exit(1 if failures else 0)
