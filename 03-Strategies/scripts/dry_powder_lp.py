#!/usr/bin/env python3
"""Dry Powder Mode — Phase 2: LP Withdrawal Module

Performs LP position withdrawals from LFJ V2.2 pools.
Requires wallet private key in config or env for real execution.

Usage:
    python3 dry-powder-lp.py --preview         # Dry run — show what would be withdrawn
    python3 dry-powder-lp.py --withdraw --all   # Withdraw 100% of LP
    python3 dry-powder-lp.py --withdraw 50      # Withdraw 50% of LP

Config:     ../config/dry-powder-config.json
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
CONFIG_PATH = CONFIG_DIR / "dry-powder-config.json"
STATE_DIR = Path(os.path.expanduser("~/.hermes/state"))
STATE_PATH = STATE_DIR / "dry-powder-state.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_state():
    defaults = {
        "total_withdrawn_usd": 0,
        "position_before_crash": None,
        "current_stable_holdings": 0,
    }
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH) as f:
                data = json.load(f)
                merged = dict(defaults)
                merged.update(data)
                return merged
        except (json.JSONDecodeError, OSError):
            pass
    return dict(defaults)


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    tmp.replace(STATE_PATH)


def format_pool_info(config: dict) -> dict:
    """Format pool details for display/operations."""
    return {
        "chain": config["chain"],
        "pool_address": config["pool_address"],
        "pool_type": "LFJ V2.2",
        "token0": "AVAX",
        "token1": "USDC",
    }


def estimate_lp_value(config: dict) -> dict:
    """Estimate current LP position value.

    Returns dict with usd_value, token0_amount, token1_amount.
    Uses mock data when wallet is not configured (preview mode).
    """
    pool = format_pool_info(config)

    # TODO: Replace with actual LFJ V2.2 subgraph query or RPC call
    # Subgraph: https://api.studio.thegraph.com/query/.../exchange-v2-2/.../avalanche
    mock_position = {
        "usd_value": 1500.00,
        "token0_amount": 112.5,
        "token0_symbol": "AVAX",
        "token1_amount": 750.00,
        "token1_symbol": "USDC",
        "pool": pool["pool_address"][:10] + "...",
        "fee_tier": "0.05%",
        "is_mock": True,
    }
    return mock_position


def preview_withdrawal(config: dict, pct: float = 100) -> dict:
    """Preview what would be withdrawn. Doesn't execute anything."""
    position = estimate_lp_value(config)
    usd_value = position["usd_value"]
    withdraw_usd = usd_value * (pct / 100)

    return {
        "total_position_usd": usd_value,
        "withdrawal_pct": pct,
        "withdrawal_usd": round(withdraw_usd, 2),
        "expected_stables": round(withdraw_usd, 2),
        "target_stable": config["stable_target"],
        "pool": position["pool"],
        "farm_estimate": position,
        "is_mock": position["is_mock"],
        "note": "MOCK DATA — only real after wallet keys are configured",
    }


def execute_withdrawal(config: dict, pct: float = 100) -> dict:
    """Execute LP withdrawal.

    REAL WITHDRAWAL — requires wallet key.
    Currently returns a placeholder. Will integrate with LFJ contract:
      1. Remove liquidity from LFJ V2.2 pool
      2. Swap token0 → stable target
      3. Update state file
    """
    # TODO: Phase 3 — implement swap-to-stables logic
    msg = (
        "LP withdrawal requires wallet key configuration.\n"
        "Set PRIVATE_KEY in env or add to dry-powder-config.json (not recommended).\n"
        "For now use --preview to see what would be withdrawn."
    )
    print(f"   ⚠ {msg}")
    return {"success": False, "error": "wallet_key_needed", "message": msg}


def show_status(config):
    """Print LP module status."""
    print("=" * 50)
    print("  DRY POWDER LP — Module Status")
    print("=" * 50)
    print(f"  Pool:      {config['pool_address'][:10]}...{config['pool_address'][-6:]}")
    print(f"  Chain:     {config['chain']}")
    print(f"  Pool Type: LFJ V2.2 (AVAX/USDC)")
    print(f"  Mode:      {config['mode']}")
    print(f"  Max Withdraw: {config['max_withdraw_pct']}%")
    print(f"  Min Withdraw: ${config['min_withdraw_usd']}")
    print()
    preview = preview_withdrawal(config)
    print(f"  Current Position: ${preview['total_position_usd']:.2f} (MOCK)")
    print(f"  100% Withdrawal:  ${preview['withdrawal_usd']:.2f} → {config['stable_target']}")
    if preview["is_mock"]:
        print("  ⚠ Position data is MOCK — real values need subgraph integration")
    print("=" * 50)


def main():
    config = load_config()

    if "--status" in sys.argv:
        show_status(config)
        return 0

    if "--preview" in sys.argv:
        # Parse optional percentage argument
        pct = 100
        for arg in sys.argv:
            try:
                pct = float(arg)
            except ValueError:
                continue
        if pct < 0 or pct > 100:
            print("Withdrawal percentage must be 0-100")
            return 1
        preview = preview_withdrawal(config, pct)
        print(json.dumps(preview, indent=2))
        return 0

    if "--withdraw" in sys.argv:
        pct = 100
        for arg in sys.argv:
            try:
                pct = float(arg)
            except ValueError:
                continue

        # Check if wallet is configured
        pk = os.environ.get("PRIVATE_KEY", "") or config.get("private_key", "")
        if not pk:
            print("❌ No wallet key configured. Use --preview to see what would be withdrawn.")
            return 1

        result = execute_withdrawal(config, pct)
        print(json.dumps(result, indent=2))
        return 0 if result.get("success") else 1

    # Default: show help
    print("Dry Powder LP Module")
    print()
    print("Usage:")
    print("  --preview [pct]    Preview withdrawal (default 100%)")
    print("  --withdraw [pct]   Execute withdrawal (requires wallet key)")
    print("  --status           Show module status")
    return 0


if __name__ == "__main__":
    sys.exit(main())
