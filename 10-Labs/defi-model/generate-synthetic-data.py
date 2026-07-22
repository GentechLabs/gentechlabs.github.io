#!/usr/bin/env python3
"""
GenTech DeFi Model — Synthetic Training Data Generator
Generates training pairs from DeFi knowledge
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_PATH = Path("/root/vaults/gentech/02-Labs/defi-model/training-data")

def generate_training_data():
    """Generate synthetic training pairs"""
    pairs = []
    
    # LP Position Management
    pairs.extend(generate_lp_data())
    
    # Yield Farming
    pairs.extend(generate_yield_data())
    
    # Market Analysis
    pairs.extend(generate_market_data())
    
    # Risk Management
    pairs.extend(generate_risk_data())
    
    # Portfolio Optimization
    pairs.extend(generate_portfolio_data())
    
    return pairs

def generate_lp_data():
    """Generate LP position training data"""
    return [
        {
            "question": "What is impermanent loss and how does it affect LP positions?",
            "answer": "Impermanent loss (IL) occurs when the price ratio of tokens in an LP position changes from when they were deposited. For example, if you deposit AVAX and USDC at $35 AVAX, and AVAX drops to $25, you'll have more AVAX and less USDC than when you started. The loss is 'impermanent' because it only realizes if you withdraw. In range-bound markets, IL is minimal and fee generation often compensates. In trending markets, IL can exceed fees.",
            "type": "lp_management"
        },
        {
            "question": "When should I compound my LP fees vs extract them?",
            "answer": "Compound when: (1) Market is range-bound and fees > IL, (2) You want to grow position size, (3) Gas fees are low. Extract when: (1) You need liquidity for other opportunities, (2) Market is trending and IL is high, (3) You want to de-risk, (4) Fees have accumulated significantly (>5% of position). Our Compound vs Extract Protocol automates this decision based on market conditions.",
            "type": "lp_management"
        },
        {
            "question": "How do I set optimal LP ranges?",
            "answer": "Optimal ranges depend on market conditions: (1) Range-bound: Tight ranges (±5-10%) maximize fee capture, (2) Trending: Wide ranges (±20-30%) reduce IL, (3) Volatile: Very wide ranges or single-sided. Use our dashboard's range optimizer which analyzes historical volatility and suggests ranges that balance fee capture vs IL. Always consider your conviction level—wider ranges for long-term holds.",
            "type": "lp_management"
        },
        {
            "question": "What's the difference between concentrated and full-range LP?",
            "answer": "Concentrated LP (e.g., Uniswap V3, LFJ) lets you provide liquidity within a specific price range, earning higher fees on that range but with more IL risk. Full-range LP (e.g., Uniswap V2) spreads liquidity across all prices, earning lower fees but with less IL. Concentrated is better for range-bound markets; full-range is better for volatile markets or when you can't monitor positions.",
            "type": "lp_management"
        },
        {
            "question": "How do I track my LP position performance?",
            "answer": "Track these metrics: (1) Fee APR — daily fees / position value × 365, (2) IL vs fees — compare impermanent loss to fee earnings, (3) Net return — total value - initial deposit, (4) Time in range — % of time position earns fees. Our dashboard auto-calculates these and alerts when metrics change significantly. Check portfolio health daily.",
            "type": "lp_management"
        }
    ]

def generate_yield_data():
    """Generate yield farming training data"""
    return [
        {
            "question": "What's the best yield farming strategy for a $1000 portfolio?",
            "answer": "For $1000: (1) Start with stablecoin pairs (USDC/USDT) for 5-10% APY with minimal risk, (2) Add blue-chip pairs (ETH/USDC) for 10-20% APY, (3) Consider single-sided staking for convenience. Avoid high-APY traps (>100% usually unsustainable). Diversify across 2-3 protocols. Reinvest fees weekly. Our Compound vs Extract Protocol automates this.",
            "type": "yield_farming"
        },
        {
            "question": "How do I evaluate if a yield farming opportunity is sustainable?",
            "answer": "Sustainability signals: (1) Protocol has real revenue (fees from usage, not just emissions), (2) TVL is growing organically, (3) Token emissions are decreasing over time, (4) Team is doxxed and active, (5) Audit completed. Red flags: (1) APY > 100% with no clear revenue source, (2) Anonymous team, (3) No audit, (4) Rapidly declining TVL, (5) Token price crashing.",
            "type": "yield_farming"
        },
        {
            "question": "What's the difference between APY and APR?",
            "answer": "APR (Annual Percentage Rate) is simple interest—no compounding. APY (Annual Percentage Yield) includes compounding. Example: 10% APR compounded daily = 10.52% APY. In DeFi, most yields are APY because fees auto-compound. Always compare APY to APY when evaluating opportunities. Our dashboard shows both for accurate comparison.",
            "type": "yield_farming"
        },
        {
            "question": "How do I optimize gas fees for yield farming?",
            "answer": "Optimize gas: (1) Batch transactions—compound weekly instead of daily, (2) Use Layer 2s (Base, Arbitrum) for lower fees, (3) Time transactions during low network activity (weekends, late night), (4) Use gas-efficient protocols, (5) Set gas alerts to transact when gas < 20 gwei. Our x402 micropayments reduce transaction overhead for small amounts.",
            "type": "yield_farming"
        },
        {
            "question": "What are the risks of yield farming?",
            "answer": "Key risks: (1) Smart contract risk—protocol hacks, (2) Impermanent loss—price divergence, (3) Rug pull—team abandons project, (4) Oracle manipulation—false price feeds, (5) Governance attacks—malicious proposals. Mitigate: (1) Use audited protocols, (2) Diversify across protocols, (3) Monitor positions daily, (4) Set stop-losses, (5) Only farm with capital you can afford to lose.",
            "type": "yield_farming"
        }
    ]

def generate_market_data():
    """Generate market analysis training data"""
    return [
        {
            "question": "How do FOMC meetings affect crypto markets?",
            "answer": "FOMC impacts crypto through: (1) Rate decisions—hikes = bearish (risk-off), cuts = bullish (risk-on), (2) Forward guidance—hawkish tone = bearish, dovish = bullish, (3) Quantitative tightening—reduces liquidity = bearish. Historical pattern: crypto often front-runs FOMC with volatility, then trends post-announcement. Our Fed Event Tracker monitors this and alerts on trading opportunities.",
            "type": "market_analysis"
        },
        {
            "question": "What's narrative rotation in crypto?",
            "answer": "Narrative rotation = capital flowing between crypto sectors. Example: AI tokens pump → capital rotates to DeFi → then to gaming → then to meme coins. Signals: (1) Social media sentiment shifts, (2) TVL migration between sectors, (3) Developer activity changes. Our Narrative Rotation Scanner tracks this weekly and alerts on emerging narratives before they peak.",
            "type": "market_analysis"
        },
        {
            "question": "How do I read DeFi TVL data?",
            "answer": "TVL (Total Value Locked) indicates protocol adoption: (1) Rising TVL = growing trust/use, (2) Falling TVL = potential issues, (3) Compare TVL to revenue—high TVL + low revenue = unsustainable. Use DefiLlama for data. Watch for: (1) Sudden drops (hack/rug), (2) Organic growth vs token incentives, (3) Chain-specific TVL trends. Our dashboard auto-tracks TVL changes.",
            "type": "market_analysis"
        },
        {
            "question": "What's the best time to enter a DeFi position?",
            "answer": "Entry signals: (1) Market fear (high Fear & Greed = greedy, low = opportunity), (2) Protocol fundamentals improving (TVL rising, fees increasing), (3) Technical support levels holding, (4) Macro environment favorable (rate cuts, liquidity increasing). Avoid entering during: (1) Euphoria (everyone bullish), (2) Protocol controversies, (3) Network congestion. Dollar-cost average for large positions.",
            "type": "market_analysis"
        },
        {
            "question": "How do I use on-chain data for trading decisions?",
            "answer": "On-chain signals: (1) Exchange inflows—large inflits = selling pressure, (2) Whale movements—smart money buying/selling, (3) Funding rates—high positive = overleveraged longs, (4) Open interest—rising with price = strong trend. Tools: Dune Analytics, Nansen, our Dashboard. Combine on-chain with technical analysis for best results.",
            "type": "market_analysis"
        }
    ]

def generate_risk_data():
    """Generate risk management training data"""
    return [
        {
            "question": "How much should I risk per DeFi position?",
            "answer": "Risk management rules: (1) Never risk >5% of portfolio on single position, (2) Keep 20% in stablecoins for opportunities, (3) Diversify across 3-5 protocols, (4) Set stop-losses at 10-20% drawdown. For $1000 portfolio: max $50 per position, $200 in stablecoins, spread across 3-5 protocols. Our portfolio health check enforces these limits.",
            "type": "risk_management"
        },
        {
            "question": "What's a stop-loss and how do I set one in DeFi?",
            "answer": "A stop-loss automatically exits a position at a predetermined loss level. In DeFi: (1) Set price alerts via our dashboard, (2) Use limit orders on DEXs, (3) Manual exit when threshold hit. Example: Enter at $100, set stop-loss at $85 (15% loss). In LP positions, monitor IL—exit if IL > 20%. Our Compound vs Extract Protocol has built-in risk thresholds.",
            "type": "risk_management"
        },
        {
            "question": "How do I protect against smart contract risk?",
            "answer": "Protection strategies: (1) Only use audited protocols (check for audits), (2) Diversify across multiple protocols, (3) Start small and scale in, (4) Monitor protocol governance for changes, (5) Use insurance protocols (Nexus Mutual, InsurAce). Red flags: (1) No audit, (2) Anonymous team, (3) Recently deployed, (4) Concentrated ownership. Our Agent Rug scanner flags these.",
            "type": "risk_management"
        },
        {
            "question": "What's the Kelly Criterion and how does it apply to DeFi?",
            "answer": "Kelly Criterion optimizes bet sizing: f* = (bp - q) / b, where b = odds, p = win probability, q = lose probability. In DeFi: (1) Estimate win rate from backtesting, (2) Calculate optimal position size, (3) Usually use half-Kelly for safety. Example: 60% win rate, 2:1 payout → Kelly = 35%. Our portfolio optimizer uses modified Kelly for position sizing.",
            "type": "risk_management"
        },
        {
            "question": "How do I handle a protocol hack or exploit?",
            "answer": "Immediate steps: (1) Withdraw all funds if possible, (2) Check protocol's official channels for updates, (3) Don't interact with compromised contracts, (4) Document everything for potential recovery. Prevention: (1) Use insurance, (2) Diversify, (3) Monitor protocol health daily. Our Agent Rug scanner and real-time alerts help detect issues early.",
            "type": "risk_management"
        }
    ]

def generate_portfolio_data():
    """Generate portfolio optimization training data"""
    return [
        {
            "question": "How do I rebalance my DeFi portfolio?",
            "answer": "Rebalancing strategy: (1) Set target allocation (e.g., 40% LP, 30% staking, 20% stablecoins, 10% reserve), (2) Review monthly or when allocation drifts >5%, (3) Use our Compound vs Extract Protocol to optimize fee extraction, (4) Consider gas costs—don't rebalance for small amounts. Our dashboard auto-tracks allocation and alerts when rebalancing needed.",
            "type": "portfolio_optimization"
        },
        {
            "question": "What's the ideal DeFi portfolio composition?",
            "answer": "Ideal composition depends on risk tolerance: Conservative: 50% stablecoins, 30% blue-chip LP, 20% single-sided staking. Moderate: 30% stablecoins, 40% LP, 20% staking, 10% yield farming. Aggressive: 10% stablecoins, 50% LP, 20% yield farming, 20% new protocols. Our portfolio optimizer suggests allocations based on your goals and risk profile.",
            "type": "portfolio_optimization"
        },
        {
            "question": "How do I track my total DeFi returns?",
            "answer": "Track returns: (1) Initial deposit value, (2) Current position value, (3) Fees earned, (4) Token rewards, (5) Net return = (current + fees + rewards) - initial. Our dashboard auto-calculates: daily P&L, fee APR, IL tracking, and total portfolio performance. Export to CSV for tax reporting.",
            "type": "portfolio_optimization"
        },
        {
            "question": "What metrics should I monitor daily?",
            "answer": "Daily metrics: (1) Portfolio value and daily change, (2) LP position status (in range/out of range), (3) Fee accrual, (4) Gas prices for optimization, (5) Protocol health (TVL changes), (6) Macro events (Fed meetings, economic data). Our dashboard consolidates all this with alerts for significant changes.",
            "type": "portfolio_optimization"
        },
        {
            "question": "How do I optimize for tax efficiency in DeFi?",
            "answer": "Tax optimization: (1) Hold positions >1 year for long-term gains, (2) Harvest losses by closing losing positions, (3) Track cost basis for every transaction, (4) Use tax-loss harvesting across protocols, (5) Consider tax-advantaged accounts where possible. Our dashboard exports transaction history for tax software. Consult a crypto-savvy tax professional.",
            "type": "portfolio_optimization"
        }
    ]

def save_training_data(pairs):
    """Save training pairs to JSON"""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    output_file = OUTPUT_PATH / f"synthetic-training-{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(pairs, f, indent=2)
    
    print(f"Generated {len(pairs)} synthetic training pairs to {output_file}")
    
    # Also save as JSONL for fine-tuning
    jsonl_file = OUTPUT_PATH / f"synthetic-training-{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(jsonl_file, 'w') as f:
        for pair in pairs:
            f.write(json.dumps(pair) + '\n')
    
    print(f"Saved JSONL format to {jsonl_file}")
    
    return output_file, jsonl_file

if __name__ == "__main__":
    print("Generating synthetic DeFi training data...")
    pairs = generate_training_data()
    
    if pairs:
        save_training_data(pairs)
        print(f"\nSummary:")
        print(f"  Total pairs: {len(pairs)}")
        print(f"  By type:")
        for ptype in set(p['type'] for p in pairs):
            count = len([p for p in pairs if p['type'] == ptype])
            print(f"    {ptype}: {count}")
    else:
        print("No training pairs generated.")
