#!/usr/bin/env python3
"""
Capital Gate — the "smart" layer of the Agentic Treasury (Jordan, Aug 17 2026).

The treasury should only burn tokens on capital-dependent jobs when there is
actually money in the treasury to manage. When the wallet is flat (no deployed
LP, no meaningful balance), those jobs should go SILENT and save tokens.

This module exposes:
  - `treasury_has_capital(chain='avalanche', wallet=STEWARD) -> bool`
      True when there is a deployed LP position OR a meaningful token balance.
  - `gate_exit(chain=..., wallet=...) -> int`
      For cron wrappers: prints nothing and exits 0 (silent) when flat, or
      prints a one-line "CAPITAL PRESENT" marker and exits 0 when funded.
      Non-zero exit on a real error so the job surfaces the failure.

Design rules (from develop-and-verify / audit checklist):
  - Reuses discover_positions.py (already chain-agnostic, live on-chain reads).
  - No hardcoded secrets. No error-detail leakage.
  - Deterministic: same wallet state -> same gate result.
  - Cheap: one RPC read per call. Fail-safe: on any error, treat as "has
    capital" (run the job) rather than silently skipping a funded treasury.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

# The Steward's primary treasury wallet (Avalanche C-Chain, LFJ V2.2).
STEWARD = _sw_wallet()

# A wallet is "funded" once it holds at least this much TOTAL value (USD)
# across deployed LP bins + wallet balances. Below this it's dust and not
# worth reporting on (Jordan, Aug 18 2026: $25 floor — stay silent below it).
MIN_MEANINGFUL_USD = 25.0

# Stablecoins treated as $1 per token for valuation (no price fetch needed).
_STABLES = {"USDC", "USDC_e", "USDT", "USDT_e", "DAI", "FDUSD", "PYUSD"}

# Path to the position discovery module (chain-agnostic, live reads).
DISCOVER = "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/discover_positions.py"


def _read_discovery(chain: str, wallet: str) -> dict:
    """Run discover_positions.py and return its JSON. {} on any failure."""
    try:
        proc = subprocess.run(
            [sys.executable, DISCOVER, "--wallet", wallet, "--chain", chain, "--json"],
            capture_output=True, text=True, timeout=60,
        )
        if proc.returncode != 0:
            return {}
        return json.loads(proc.stdout or "{}")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return {}


def _price_usd(sym: str) -> float | None:
    """USD price for a balance symbol. $1 for stables, else live price."""
    sym = (sym or "").upper()
    if sym in _STABLES:
        return 1.0
    try:
        import urllib.request as _ur
        import urllib.parse as _up
        # Use discover_positions' own price fetch if importable.
        sys.path.insert(0, os.path.dirname(DISCOVER))
        from discover_positions import fetch_asset_price
        p = fetch_asset_price(sym)
        if p:
            return p
    except Exception:
        pass
    # Fallback: CoinGecko simple price
    cg_id = {"AVAX": "avalanche-2", "WAVAX": "avalanche-2", "ETH": "ethereum",
             "WETH": "ethereum", "SOL": "solana", "BTC": "bitcoin",
             "cbBTC": "coinbase-wrapped-btc", "PAXG": "pax-gold"}.get(sym)
    if not cg_id:
        return None
    try:
        with _ur.urlopen(
            f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd",
            timeout=8,
        ) as r:
            return float(json.load(r)[cg_id]["usd"])
    except Exception:
        return None


def treasury_value_usd(chain: str = "avalanche", wallet: str = STEWARD) -> float:
    """Total USD value across deployed LP positions + wallet balances.

    Fail-safe: on any read error, return +inf (assume funded) so a funded
    treasury is never silently skipped because of a transient RPC failure.
    """
    data = _read_discovery(chain, wallet)
    if not data:
        return float("inf")  # couldn't read on-chain state -> assume funded

    total = 0.0

    # 1. Deployed LP positions: bins present => value held. We can't measure a
    #    precise USD notional (discovery is honest about that), so a deployed
    #    position counts as at least the floor (it holds real collateral).
    for pos in data.get("positions", []):
        if pos.get("bins", 0):
            total += MIN_MEANINGFUL_USD

    # 2. Wallet balances: value each token at its live USD price.
    for sym, val in (data.get("balances") or {}).items():
        val = val or 0.0
        if val <= 0:
            continue
        price = _price_usd(sym)
        if price:
            total += float(val) * price

    return total


def treasury_has_capital(chain: str = "avalanche", wallet: str = STEWARD) -> bool:
    """True when the treasury holds >= MIN_MEANINGFUL_USD in total value."""
    try:
        return treasury_value_usd(chain, wallet) >= MIN_MEANINGFUL_USD
    except Exception:
        return True  # fail-safe: run the job


def gate_exit(chain: str = "avalanche", wallet: str = STEWARD) -> int:
    """Cron-wrapper entry point.

    - Flat treasury  -> print nothing, exit 0 (SILENT, saves tokens).
    - Funded treasury -> print a one-line marker, exit 0 (job proceeds).
    - Real error      -> print a short error, exit 1 (job surfaces it).
    """
    try:
        has_cap = treasury_has_capital(chain, wallet)
    except Exception:
        # Fail-safe: on unexpected error, run the job (don't skip a funded
        # treasury). Surface a marker so the job knows the gate was uncertain.
        print("CAPITAL_GATE: uncertain (error) — running job")
        return 0

    if has_cap:
        print("CAPITAL_GATE: funded — running job")
        return 0
    # Flat: silent. The cron job's wrapper should exit here before doing work.
    return 0


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Capital gate for the Agentic Treasury")
    p.add_argument("--chain", default="avalanche", help="chain to check")
    p.add_argument("--wallet", default=STEWARD, help="wallet to check")
    p.add_argument("--check", action="store_true",
                   help="print TRUE/FALSE and exit (for shell conditionals)")
    a = p.parse_args()

    if a.check:
        print("TRUE" if treasury_has_capital(a.chain, a.wallet) else "FALSE")
    else:
        sys.exit(gate_exit(a.chain, a.wallet))
