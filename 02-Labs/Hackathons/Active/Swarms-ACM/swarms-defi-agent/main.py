#!/usr/bin/env python3
"""
DeFi Signal Agent — Swarms Marketplace Entry Point
Monitors on-chain LP positions, detects yield opportunities, and delivers
actionable signals through Swarms orchestration.

Built for: Swarms ACM Hackathon — Finance & Market Analysis track
Deadline: May 27, 2026
"""

import os
import sys
import json
from typing import Optional

# ── Import Signal Engine ──────────────────────────────────────────────────

from signals.lp_monitor import (
    fetch_token_prices,
    read_pool_state,
    calculate_il,
    get_recommendation,
    lp_position_report,
    whale_watch,
    scan_yield_opportunities,
)


# ── Agent System Prompt ───────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a DeFi Signal Agent — an on-chain monitoring specialist for concentrated liquidity positions.

Your job is to help liquidity providers track their positions, detect risks, and identify opportunities.

Available tools:
1. fetch_token_prices — Get live token prices (CoinGecko + DexScreener fallback)
2. read_pool_state — Read LP pool data (TVL, volume, APR, fees)
3. calculate_il — Calculate impermanent loss with concentration modeling
4. get_recommendation — Generate rebalance recommendations
5. lp_position_report — Full position report with all metrics
6. whale_watch — Monitor for large liquidity events
7. scan_yield_opportunities — Compare multiple pools by APR

When a user asks about their LP position:
1. Fetch current prices and pool state
2. Calculate IL and fee efficiency
3. Check if position is in/out of range
4. Provide a clear recommendation

When a user asks about opportunities:
1. Scan pools and rank by APR
2. Flag high-volume pools with unusual activity
3. Suggest optimal shapes based on price behavior

Be concise and actionable. Focus on numbers and decisions, not fluff.
Use emoji indicators: ✅ healthy, ⚠️ warning, 🚨 critical."""


# ── Agent Configuration ───────────────────────────────────────────────────

TOOLS = [
    fetch_token_prices,
    read_pool_state,
    calculate_il,
    get_recommendation,
    lp_position_report,
    whale_watch,
    scan_yield_opportunities,
]

DEFAULT_MODEL = os.getenv(
    "LP_MONITOR_MODEL",
    "openrouter/google/gemini-2.0-flash-001",
)


def resolve_api_key(model_name: str) -> Optional[str]:
    """Resolve API key from environment based on model provider."""
    if "openrouter" in model_name.lower():
        return os.getenv("OPENROUTER_API_KEY")
    return os.getenv("OPENAI_API_KEY")


def create_agent(model_name: str | None = None, api_key: str | None = None):
    """Create the DeFi Signal Agent with Swarms SDK."""
    from swarms import Agent

    model = model_name or DEFAULT_MODEL
    key = api_key or resolve_api_key(model)

    if not key:
        print("ERROR: No API key found.")
        print("  OpenRouter: export OPENROUTER_API_KEY=your_key")
        print("  OpenAI:     export OPENAI_API_KEY=your_key")
        sys.exit(1)

    # Set key in environment for LiteLLM
    if "openrouter" in model.lower():
        os.environ["OPENROUTER_API_KEY"] = key
    else:
        os.environ["OPENAI_API_KEY"] = key

    agent = Agent(
        agent_name="DeFi Signal Agent",
        agent_description=(
            "Monitors concentrated liquidity LP positions with IL tracking, "
            "efficiency scoring, whale detection, and yield opportunity scanning. "
            "Supports LFJ (Avalanche), Uniswap V3 (Ethereum/Base), and DexScreener pools."
        ),
        system_prompt=SYSTEM_PROMPT,
        model_name=model,
        tools=TOOLS,
        max_loops="auto",
        temperature=0.3,
        max_tokens=4096,
    )

    return agent


# ── CLI Commands ──────────────────────────────────────────────────────────

def cmd_report(args: list[str]):
    """Run a full LP position report."""
    prices = fetch_token_prices("AVAX,USDC")
    pool = read_pool_state()

    avax_price = prices.get("AVAX", {}).get("price_usd", 0)
    if not avax_price:
        avax_price = pool.get("price_usd", 0)

    # Parse CLI overrides
    range_low = 10.15
    range_high = 10.38
    entry_price = 9.95
    initial_value = 134.94

    for i, arg in enumerate(args):
        if arg == "--range-low" and i + 1 < len(args):
            range_low = float(args[i + 1])
        elif arg == "--range-high" and i + 1 < len(args):
            range_high = float(args[i + 1])
        elif arg == "--entry" and i + 1 < len(args):
            entry_price = float(args[i + 1])
        elif arg == "--value" and i + 1 < len(args):
            initial_value = float(args[i + 1])

    report = lp_position_report(
        range_low=range_low,
        range_high=range_high,
        entry_price=entry_price,
        initial_value_usd=initial_value,
    )

    print(json.dumps(report, indent=2, default=str))


def cmd_whale(args: list[str]):
    """Run whale watch signal."""
    threshold = 50_000
    for i, arg in enumerate(args):
        if arg == "--threshold" and i + 1 < len(args):
            threshold = float(args[i + 1])

    result = whale_watch(threshold_usd=threshold)
    print(json.dumps(result, indent=2, default=str))


def cmd_scan(args: list[str]):
    """Scan yield opportunities across pools."""
    # Default: AVAX/USDC pool
    pools = [
        {
            "address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
            "chain": "avalanche",
            "name": "AVAX/USDC (LFJ)",
        },
    ]

    result = scan_yield_opportunities(pools)
    print(json.dumps(result, indent=2, default=str))


def cmd_agent(args: list[str]):
    """Launch the full Swarms agent with interactive mode."""
    model = args[0] if args else None
    agent = create_agent(model_name=model)

    print(f"DeFi Signal Agent initialized")
    print(f"Model: {agent.model_name}")
    print(f"Tools: {len(agent.tools)}")
    print(f"\nTry: 'Check my AVAX/USDC LP position. Range: $10.15-$10.38'")
    print("     'Scan for yield opportunities'")
    print("     'Any whale activity detected?'")
    print("     (type 'quit' to exit)\n")

    while True:
        try:
            query = input("> ").strip()
            if query.lower() in ("quit", "exit", "q"):
                break
            if not query:
                continue
            result = agent.run(query)
            print(f"\n{result}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        cmd_agent([])
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "report": cmd_report,
        "whale": cmd_whale,
        "scan": cmd_scan,
        "agent": cmd_agent,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(commands.keys())}")
        sys.exit(1)

    commands[command](args)


if __name__ == "__main__":
    main()
