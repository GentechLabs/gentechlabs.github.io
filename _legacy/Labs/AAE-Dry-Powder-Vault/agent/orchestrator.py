#!/usr/bin/env python3
"""
AAE Dry Powder Vault — Agent Orchestrator

Cross-chain USDC rotation engine. Integrates with:
  - Hermes agent framework
  - CMC watchlist zone monitoring
  - Circle CCTP / Across bridging
  - Aerodrome (Base), LFJ (Avalanche), Meteora (Solana)
  - DeFi Llama API for live yield data

Usage:
  python3 orchestrator.py --mode monitor   # continuous zone monitoring
  python3 orchestrator.py --mode status    # one-shot status report
  python3 orchestrator.py --mode rotate    # evaluate and propose rotations
"""

import json
import os
import sys
import time
import logging
import urllib.request
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

# ──────────────────── Config ────────────────────

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(VAULT_DIR, "config")
STATE_DIR = os.path.join(VAULT_DIR, "state")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("dry-powder")

# ──────────────────── Types ────────────────────

class Chain(Enum):
    BASE = "base"
    AVALANCHE = "avalanche"
    SOLANA = "solana"

class Zone(Enum):
    DEEP_VALUE = "🔥 Deep Value"
    ACCUMULATE = "🟢 Accumulate"
    WATCH = "🔵 Watch"
    EXTENDED = "⚪ Extended"

class BridgeProtocol(Enum):
    CCTP = "cctp"
    ACROSS = "across"

@dataclass
class YieldSource:
    chain: Chain
    protocol: str
    pool_id: str
    apy: float
    tvl_usd: float
    risk_score: float  # 0-1, higher = riskier
    narrative_boost: float  # -1 to +1
    last_updated: str = ""

@dataclass
class ChainState:
    chain: Chain
    zone: Zone
    usdc_deposited: float = 0.0
    usdc_in_lp: float = 0.0
    usdc_bridged: float = 0.0
    gas_balance: float = 0.0
    yield_sources: list = field(default_factory=list)
    narrative_strength: str = ""

@dataclass
class RotationSignal:
    from_chain: Chain
    to_chain: Chain
    amount: float
    reason: str
    expected_apy_delta: float
    bridge_protocol: BridgeProtocol
    estimated_cost: float
    confidence: float  # 0-1

# ──────────────────── Zone Monitor ────────────────────

# Chain-level zones (extends CMC watchlist zones to chains)
CHAIN_ZONES = {
    Chain.BASE: [
        (Zone.DEEP_VALUE, 0.0, 2.0),      # Aerodrome APY < 2%
        (Zone.ACCUMULATE, 2.0, 5.0),        # 2-5% APY
        (Zone.WATCH, 5.0, 10.0),            # 5-10% APY
        (Zone.EXTENDED, 10.0, 999.0),       # > 10% (too risky)
    ],
    Chain.AVALANCHE: [
        (Zone.DEEP_VALUE, 0.0, 5.0),
        (Zone.ACCUMULATE, 5.0, 12.0),
        (Zone.WATCH, 12.0, 25.0),
        (Zone.EXTENDED, 25.0, 999.0),
    ],
    Chain.SOLANA: [
        (Zone.DEEP_VALUE, 0.0, 3.0),
        (Zone.ACCUMULATE, 3.0, 8.0),
        (Zone.WATCH, 8.0, 20.0),
        (Zone.EXTENDED, 20.0, 999.0),
    ],
}

def get_chain_zone(chain: Chain, apy: float) -> Zone:
    """Determine zone for a chain based on its best yield APY."""
    zones = CHAIN_ZONES.get(chain, [])
    for zone, low, high in zones:
        if low <= apy < high:
            return zone
    return Zone.WATCH

# ──────────────────── Narrative Engine ────────────────────

# Extends the CMC watchlist NARRATIVES to chain-level narrative scores
NARRATIVE_MAP = {
    Chain.BASE: {
        "narrative": "🔵 Base Ecosystem",
        "strength": 0.6,  # moderate - L2 but not top L2
        "factors": ["Aerodrome TVL growth", "Base builder activity", "Coinbase backing"],
    },
    Chain.AVALANCHE: {
        "narrative": "🔺 AVAX Ecosystem",
        "strength": 0.8,  # strong fundamentals per CMC watchlist
        "factors": ["FIFA ticketing 24x volume", "C-Chain activity surging", "Subnet adoption"],
    },
    Chain.SOLANA: {
        "narrative": "⚡ Solana Ecosystem",
        "strength": 0.7,  # good but volatile
        "factors": ["Meteora DLMM growth", "Validator economics", "Mobile chain narrative"],
    },
}

def narrative_weight(chain: Chain) -> float:
    """Return 0-1 narrative strength for a chain."""
    return NARRATIVE_MAP.get(chain, {}).get("strength", 0.5)

# ──────────────────── DeFi Llama Yield Fetcher ────────────────────

DEFILLAMA_POOLS_URL = "https://yields.llama.fi/pools"
DEFILLAMA_PROTOCOL_URL = "https://api.llama.fi/protocol/{protocol}"

# DeFi Llama pool IDs for our target pools
DEFILLAMA_POOL_IDS = {
    Chain.BASE: {
        "Aerodrome USDC-WETH": {"pool_id": "aerodrome-base-usdc-weth", "protocol": "aerodrome"},
        "Aerodrome USDC-USDbC": {"pool_id": "aerodrome-base-usdc-usdbc", "protocol": "aerodrome"},
    },
    Chain.AVALANCHE: {
        "LFJ AVAX-USDC": {"pool_id": "trader-joe-avalanche-avax-usdc", "protocol": "trader-joe"},
        "LFJ USDC.e-USDC": {"pool_id": "trader-joe-avalanche-usdc-usdc", "protocol": "trader-joe"},
    },
    Chain.SOLANA: {
        "Meteora SOL-USDC": {"pool_id": "meteora-sol-usdc", "protocol": "meteora"},
        "Meteora USDC-USDT": {"pool_id": "meteora-usdc-usdt", "protocol": "meteora"},
    },
}

# Fallback hardcoded yields (used when API is unavailable)
FALLBACK_YIELDS = {
    Chain.BASE: {
        "protocol": "Aerodrome",
        "pools": {
            "USDC-WETH": {"base_apy": 8.5, "tvl": 15_000_000, "risk": 0.3},
            "USDC-USDbC": {"base_apy": 3.2, "tvl": 25_000_000, "risk": 0.1},
        },
    },
    Chain.AVALANCHE: {
        "protocol": "LFJ (Trader Joe)",
        "pools": {
            "AVAX-USDC": {"base_apy": 12.0, "tvl": 8_000_000, "risk": 0.5},
            "USDC.e-USDC": {"base_apy": 4.5, "tvl": 12_000_000, "risk": 0.1},
        },
    },
    Chain.SOLANA: {
        "protocol": "Meteora DLMM",
        "pools": {
            "SOL-USDC": {"base_apy": 10.0, "tvl": 20_000_000, "risk": 0.4},
            "USDC-USDT": {"base_apy": 5.0, "tvl": 30_000_000, "risk": 0.05},
        },
    },
}

def fetch_live_yields(chain: Chain) -> dict:
    """
    Fetch live yield data from DeFi Llama API.
    Falls back to hardcoded values if API is unavailable.

    Returns:
        dict with pool data matching FALLBACK_YIELDS format
    """
    try:
        # Fetch all pools from DeFi Llama
        req = urllib.request.Request(
            DEFILLAMA_POOLS_URL,
            headers={"User-Agent": "AAE-DryPowder-Vault/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        pools = data.get("data", [])

        # Filter for our chain's pools
        chain_name = chain.value
        chain_pools = [
            p for p in pools
            if p.get("chain", "").lower() == chain_name
            and p.get("project", "").lower() in [
                "aerodrome", "velodrome", "trader-joe", "lfj", "meteora"
            ]
        ]

        if not chain_pools:
            log.warning(f"No live pools found for {chain_name}, using fallback")
            return FALLBACK_YIELDS.get(chain, {})

        # Build yield data
        protocol = chain_pools[0].get("project", "Unknown")
        pool_data = {}

        for pool in chain_pools:
            symbol = pool.get("symbol", "UNKNOWN")
            apy = pool.get("apy", 0.0)
            tvl = pool.get("tvlUsd", 0.0)
            pool_id = pool.get("pool", "unknown")

            # Determine risk based on APY and TVL
            if apy > 20:
                risk = 0.8
            elif apy > 10:
                risk = 0.5
            elif apy > 5:
                risk = 0.3
            else:
                risk = 0.1

            pool_data[symbol] = {
                "base_apy": apy,
                "tvl": tvl,
                "risk": risk,
                "pool_id": pool_id,
                "last_updated": pool.get("updatedAt", ""),
            }

        log.info(f"Fetched {len(pool_data)} live pools for {chain_name}")
        return {
            "protocol": protocol,
            "pools": pool_data,
        }

    except Exception as e:
        log.warning(f"DeFi Llama API error for {chain.value}: {e}")
        log.info("Using fallback hardcoded yields")
        return FALLBACK_YIELDS.get(chain, {})

def fetch_best_apy(chain: Chain, use_live: bool = True) -> tuple[float, str]:
    """
    Return (best_apy, pool_name) for a chain.

    Args:
        chain: Chain to check
        use_live: Whether to fetch from DeFi Llama (fallback to hardcoded)

    Returns:
        (best_apy, pool_name)
    """
    if use_live:
        sources = fetch_live_yields(chain)
    else:
        sources = FALLBACK_YIELDS.get(chain, {})

    best_apy = 0.0
    best_pool = "idle"

    for pool_name, pool_data in sources.get("pools", {}).items():
        apy = pool_data["base_apy"] * (1 + narrative_weight(chain) * 0.2)
        if apy > best_apy:
            best_apy = apy
            best_pool = pool_name

    return best_apy, best_pool

# ──────────────────── Rotation Decision Engine ────────────────────

ROTATION_CONFIG = {
    "min_yield_delta_pct": 3.0,     # rotate if 3%+ APY difference
    "min_narrative_delta": 0.15,    # narrative shift threshold
    "max_rotation_pct": 30.0,       # max 30% of chain balance per rotation
    "cooldown_hours": 4,            # min hours between rotations on same pair
    "risk_cap": 0.7,                # max combined risk score
}

def evaluate_rotations(chain_states: list[ChainState]) -> list[RotationSignal]:
    """Evaluate all chain pairs and propose rotations if warranted."""
    signals = []

    for i, src in enumerate(chain_states):
        for j, dst in enumerate(chain_states):
            if i == j:
                continue

            src_apy, _ = fetch_best_apy(src.chain)
            dst_apy, _ = fetch_best_apy(dst.chain)
            apy_delta = dst_apy - src_apy

            # Check yield delta threshold
            if apy_delta < ROTATION_CONFIG["min_yield_delta_pct"]:
                continue

            # Check narrative
            src_narr = narrative_weight(src.chain)
            dst_narr = narrative_weight(dst.chain)
            narr_delta = dst_narr - src_narr

            # Calculate confidence score
            confidence = min(1.0, (
                (apy_delta / 10.0) * 0.5 +           # yield factor
                (narr_delta / 0.5) * 0.3 +           # narrative factor
                (1.0 - 0.3) * 0.2                     # base factor
            ))

            if confidence < 0.4:
                continue

            # Determine bridge protocol
            bridge_protocol = BridgeProtocol.CCTP  # prefer CCTP (free)
            estimated_cost = 0.0  # CCTP is free

            # If bridging to Solana, use Across
            if dst.chain == Chain.SOLANA:
                bridge_protocol = BridgeProtocol.ACROSS
                estimated_cost = estimate_bridge_cost(src.chain, dst.chain, 0, bridge_protocol)

            # Calculate rotation amount
            max_amount = src.usdc_deposited * (ROTATION_CONFIG["max_rotation_pct"] / 100)
            rotation_amount = min(max_amount, src.usdc_deposited * 0.5)

            reason = (
                f"Yield: {dst_apy:.1f}% vs {src_apy:.1f}% "
                f"(+{apy_delta:.1f}%), "
                f"Narrative: {dst_narr:.2f} vs {src_narr:.2f}"
            )

            signals.append(RotationSignal(
                from_chain=src.chain,
                to_chain=dst.chain,
                amount=rotation_amount,
                reason=reason,
                expected_apy_delta=apy_delta,
                bridge_protocol=bridge_protocol,
                estimated_cost=estimated_cost,
                confidence=confidence,
            ))

    # Sort by confidence
    signals.sort(key=lambda s: s.confidence, reverse=True)
    return signals

# ──────────────────── Bridge Cost Estimator ────────────────────

BRIDGE_COSTS = {
    (Chain.BASE, Chain.AVALANCHE): {
        BridgeProtocol.CCTP: {"gas_base": 0.001, "gas_dest": 0.02, "fee": 0.0},
        BridgeProtocol.ACROSS: {"gas_base": 0.001, "gas_dest": 0.02, "fee_pct": 0.08},
    },
    (Chain.BASE, Chain.SOLANA): {
        BridgeProtocol.ACROSS: {"gas_base": 0.001, "gas_dest": 0.001, "fee_pct": 0.10},
    },
    (Chain.AVALANCHE, Chain.SOLANA): {
        BridgeProtocol.ACROSS: {"gas_base": 0.02, "gas_dest": 0.001, "fee_pct": 0.12},
    },
    (Chain.AVALANCHE, Chain.BASE): {
        BridgeProtocol.CCTP: {"gas_base": 0.02, "gas_dest": 0.001, "fee": 0.0},
        BridgeProtocol.ACROSS: {"gas_base": 0.02, "gas_dest": 0.001, "fee_pct": 0.08},
    },
    (Chain.SOLANA, Chain.BASE): {
        BridgeProtocol.ACROSS: {"gas_base": 0.001, "gas_dest": 0.001, "fee_pct": 0.10},
    },
    (Chain.SOLANA, Chain.AVALANCHE): {
        BridgeProtocol.ACROSS: {"gas_base": 0.001, "gas_dest": 0.02, "fee_pct": 0.12},
    },
}

def estimate_bridge_cost(src: Chain, dst: Chain, amount: float, protocol: BridgeProtocol) -> float:
    """Estimate total bridge cost in USD."""
    costs = BRIDGE_COSTS.get((src, dst), {}).get(protocol, {})
    if not costs:
        return float('inf')

    gas_total = costs.get("gas_base", 0) + costs.get("gas_dest", 0)
    fee_pct = costs.get("fee_pct", 0) / 100
    fee = amount * fee_pct

    return gas_total + fee

# ──────────────────── State Management ────────────────────

def load_state() -> dict:
    """Load orchestrator state from disk."""
    state_file = os.path.join(STATE_DIR, "orchestrator-state.json")
    os.makedirs(STATE_DIR, exist_ok=True)
    if os.path.exists(state_file):
        with open(state_file) as f:
            return json.load(f)
    return {
        "last_rotation": {},
        "chain_balances": {},
        "total_deposited": 0,
        "total_yield": 0,
        "rotation_history": [],
    }

def save_state(state: dict):
    """Save orchestrator state."""
    state_file = os.path.join(STATE_DIR, "orchestrator-state.json")
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

# ──────────────────── Output Formatters ────────────────────

def format_status_report(chain_states: list[ChainState]) -> str:
    """Generate a human-readable status report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"🏦 AAE Dry Powder Vault — Status Report",
        f"📅 {now}",
        "=" * 50,
        "",
    ]

    total_deposited = sum(s.usdc_deposited + s.usdc_in_lp for s in chain_states)
    total_bridged = sum(s.usdc_bridged for s in chain_states)

    lines.append(f"📊 Total Deployed: ${total_deposited:,.2f} USDC")
    lines.append(f"🌉 Total Bridged: ${total_bridged:,.2f} USDC")
    lines.append("")

    for state in chain_states:
        best_apy, pool_name = fetch_best_apy(state.chain)
        zone = get_chain_zone(state.chain, best_apy)
        narr = NARRATIVE_MAP.get(state.chain, {})

        lines.append(f"── {state.chain.value.upper()} ──")
        lines.append(f"  Zone: {zone.value}")
        lines.append(f"  Narrative: {narr.get('narrative', 'Unknown')} ({narr.get('strength', 0):.1%})")
        lines.append(f"  Deposited: ${state.usdc_deposited:,.2f}")
        lines.append(f"  In LP: ${state.usdc_in_lp:,.2f}")
        lines.append(f"  Best APY: {best_apy:.1f}% ({pool_name})")
        lines.append(f"  Gas Balance: ${state.gas_balance:.4f}")
        lines.append("")

    # Zone summary
    lines.append("=" * 50)
    lines.append("🎯 CHAIN ZONE SUMMARY")
    lines.append("=" * 50)
    for state in chain_states:
        best_apy, _ = fetch_best_apy(state.chain)
        zone = get_chain_zone(state.chain, best_apy)
        lines.append(f"  {state.chain.value.upper():12s} → {zone.value} (APY: {best_apy:.1f}%)")

    lines.append("")
    lines.append("=" * 50)
    lines.append("🔄 ROTATION SIGNALS")
    lines.append("=" * 50)

    signals = evaluate_rotations(chain_states)
    if not signals:
        lines.append("  No rotation opportunities found. All chains performing within thresholds.")
    else:
        for sig in signals[:3]:
            lines.append(
                f"  {'🟢' if sig.confidence > 0.7 else '🟡'} "
                f"{sig.from_chain.value} → {sig.to_chain.value}: "
                f"${sig.amount:,.2f} ({sig.expected_apy_delta:+.1f}% APY) "
                f"[{sig.confidence:.0%} confidence]"
            )
            lines.append(f"    Reason: {sig.reason}")
            lines.append(f"    Bridge: {sig.bridge_protocol.value} (${sig.estimated_cost:.4f})")

    lines.append("")
    lines.append("Source: DeFi Llama API + CMC zones + narrative analysis")

    return "\n".join(lines)

def format_rotation_proposal(signal: RotationSignal) -> str:
    """Format a rotation proposal for Telegram notification."""
    return (
        f"⚠️ **Rotation Alert**\n\n"
        f"**Move:** ${signal.amount:,.2f} USDC\n"
        f"**From:** {signal.from_chain.value.upper()}\n"
        f"**To:** {signal.to_chain.value.upper()}\n"
        f"**Expected APY Delta:** +{signal.expected_apy_delta:.1f}%\n"
        f"**Bridge:** {signal.bridge_protocol.value.upper()} (${signal.estimated_cost:.4f})\n"
        f"**Confidence:** {signal.confidence:.0%}\n"
        f"**Reason:** {signal.reason}\n\n"
        f"Approve? Reply with `approve {signal.from_chain.value} {signal.to_chain.value}`"
    )

# ──────────────────── Main ────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AAE Dry Powder Vault Orchestrator")
    parser.add_argument("--mode", choices=["monitor", "status", "rotate"], default="status")
    parser.add_argument("--no-live", action="store_true", help="Use hardcoded yields instead of DeFi Llama")
    args = parser.parse_args()

    # Initialize chain states from saved state
    saved = load_state()

    # Build current chain states (in production, these come from on-chain + API)
    chain_states = []
    for chain in [Chain.BASE, Chain.AVALANCHE, Chain.SOLANA]:
        bal = saved.get("chain_balances", {}).get(chain.value, {})
        chain_states.append(ChainState(
            chain=chain,
            zone=get_chain_zone(chain, 0),
            usdc_deposited=bal.get("deposited", 0),
            usdc_in_lp=bal.get("in_lp", 0),
            usdc_bridged=bal.get("bridged", 0),
            gas_balance=bal.get("gas", 0),
        ))

    use_live = not args.no_live

    if args.mode == "status":
        report = format_status_report(chain_states)
        print(report)

    elif args.mode == "rotate":
        signals = evaluate_rotations(chain_states)
        if signals:
            for sig in signals:
                print(format_rotation_proposal(sig))
                print()
        else:
            print("No rotation signals triggered.")

    elif args.mode == "monitor":
        print("🔍 Starting zone monitor... (Ctrl+C to stop)")
        while True:
            try:
                report = format_status_report(chain_states)
                print(report)
                print(f"\n⏰ Next check in 4 hours...")
                time.sleep(4 * 3600)
            except KeyboardInterrupt:
                print("\nMonitor stopped.")
                break

if __name__ == "__main__":
    main()
