#!/usr/bin/env python3
"""
LP Position Status Checker — reusable component
Reads vault config + state file, checks range, determines status.
Used by d5-master-cron.py and manual YoYo reports.

Exit codes:
  0 = in range / healthy
  1 = efficiency low (edge zone)
  2 = out of range
  3 = error / data missing

Outputs JSON to stdout for piping.
"""

import json
import os
import sys
from datetime import datetime

# Config paths
VAULT_CONFIG = "/root/vaults/gentech/00-HQ/config/defi-lp-config.env"
STATE_FILE  = os.path.expanduser("~/.hermes/scripts/.lfj-position-state.json")

def load_config():
    cfg = {}
    if os.path.exists(VAULT_CONFIG):
        with open(VAULT_CONFIG) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    cfg[k] = v
    return cfg

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def parse_env_number(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def main():
    cfg = load_config()
    state = load_state()

    # Extract config values
    range_low  = parse_env_number(cfg.get("RANGE_LOW"))
    range_high = parse_env_number(cfg.get("RANGE_HIGH"))
    shape      = cfg.get("SHAPE", "curve")
    pool_addr  = cfg.get("POOL_ADDRESS", "")
    last_price = state.get("last_price", 0.0)

    if not last_price:
        print(json.dumps({"error": "no last_price in state file"}))
        sys.exit(3)

    # Core checks
    in_range = range_low <= last_price <= range_high
    range_width = range_high - range_low
    dist_from_low = last_price - range_low
    dist_from_high = range_high - last_price
    pct_from_low  = (dist_from_low / range_width * 100) if range_width else 0

    # Efficiency estimate (if available in state)
    efficiency = None
    if "current_efficiency" in state:
        efficiency = state["current_efficiency"]
    elif "alert_history" in state and state["alert_history"]:
        # Try to extract last efficiency from alert payload
        last_alert = state["alert_history"][-1]
        if "efficiency" in last_alert:
            efficiency = last_alert["efficiency"]

    # Determine status flags
    bid_ask_opportunity = (last_price <= range_low * 1.02) and (in_range)

    if not in_range:
        status_code = 2
        status_label = "OUT_OF_RANGE"
        status_emoji = "🚨"
    elif efficiency is not None and efficiency <= 30:
        status_code = 1
        status_label = "EFFICIENCY_CRITICAL"
        status_emoji = "🚨"
    elif bid_ask_opportunity:
        status_code = 1
        status_label = "EFFICIENCY_LOW"
        status_emoji = "⚠️"
    elif dist_from_low <= range_width * 0.1 or dist_from_high <= range_width * 0.1:
        status_code = 1
        status_label = "NEAR_EDGE"
        status_emoji = "⚠️"
    else:
        status_code = 0
        status_label = "HEALTHY"
        status_emoji = "✅"

    # Build output
    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "pool": {
            "address": pool_addr,
            "shape": shape,
            "range_low": range_low,
            "range_high": range_high,
            "range_width": round(range_width, 4)
        },
        "position": {
            "last_price": round(last_price, 4),
            "in_range": in_range,
            "distance_to_low": round(dist_from_low, 4),
            "distance_to_high": round(dist_from_high, 4),
            "pct_range_from_low": round(pct_from_low, 1),
            "efficiency": efficiency
        },
        "status": {
            "code": status_code,
            "label": status_label,
            "emoji": status_emoji,
            "bid_ask_opportunity": bid_ask_opportunity,
            "urgency": "HIGH" if status_code >= 1 else "LOW"
        }
    }

    print(json.dumps(result, indent=2))
    sys.exit(status_code)

if __name__ == "__main__":
    main()
</content>