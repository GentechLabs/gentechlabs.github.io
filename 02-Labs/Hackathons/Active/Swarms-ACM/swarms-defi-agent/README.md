# DeFi Signal Agent — Swarms ACM Hackathon

> **Category:** Finance & Market Analysis
> **Deadline:** May 27, 2026
> **Prize Pool:** $30,000 ($SWARMS, USDC, Solana)
> **Built by:** GenTech Labs

## What It Does

A tokenized AI agent that monitors on-chain DeFi signals and delivers actionable intelligence:

- **🔴 LP Position Monitoring** — Real-time impermanent loss tracking, fee efficiency scoring, and rebalance alerts for concentrated liquidity positions (LFJ, Uniswap V3)
- **🐋 Whale Detection** — Monitors pool volume-to-TVL ratios for unusual liquidity events
- **💰 Yield Scanner** — Compares multiple pools by APR and flags high-opportunity targets
- **🔊 Voice Alerts** — ElevenLabs TTS integration for hands-free signal delivery

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  On-Chain Data  │────▶│  Signal Engine   │────▶│  Swarms Agent   │
│  (CoinGecko,    │     │  (Python)        │     │  (Orchestration │
│   DexScreener)  │     │  7 tools         │     │   + Marketplace)│
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                   ┌──────▼───────┐
                                                   │  Voice Layer │
                                                   │ (ElevenLabs) │
                                                   └──────────────┘
```

## Quick Start

```bash
# Install dependencies
pip install swarms

# Set API keys
export OPENROUTER_API_KEY=your_key_here
# or
export OPENAI_API_KEY=your_key_here

# Interactive agent mode
python main.py agent

# One-shot position report
python main.py report --range-low 10.15 --range-high 10.38 --entry 9.95 --value 134.94

# Whale watch signal
python main.py whale --threshold 50000

# Scan yield opportunities
python main.py scan
```

## Tools

| Tool | Description |
|------|-------------|
| `fetch_token_prices` | Live prices via CoinGecko + DexScreener fallback |
| `read_pool_state` | Pool data: TVL, volume, APR, fees |
| `calculate_il` | Impermanent loss with concentration modeling |
| `get_recommendation` | Rebalance decision engine |
| `lp_position_report` | Full position report with all metrics |
| `whale_watch` | Large liquidity event detection |
| `scan_yield_opportunities` | Multi-pool APR comparison |

## Project Structure

```
swarms-defi-agent/
├── main.py                 # Agent entry point (Swarms orchestration)
├── signals/
│   ├── __init__.py
│   └── lp_monitor.py       # Signal engine (7 tools)
└── README.md               # This file
```

## Cyfrin Updraft Alignment

This project reinforces lessons from **Cyfrin Updraft — DeFi Security Module**:

### Lesson: Concentrated Liquidity Risk Analysis

**Cyfrin Module:** DeFi Protocol Interaction Patterns

**What we learned:**
- Concentrated liquidity amplifies impermanent loss by the concentration factor: `10 / range_width_pct`
- A 5% range has 2x the IL of a 10% range for the same price movement
- Out-of-range positions earn zero fees while still exposed to price risk

**How our agent applies this:**
1. `calculate_il()` models concentration-aware IL using the amplification factor
2. `get_recommendation()` triggers alerts when IL ≥ 2% or position exits range
3. Fee efficiency scoring warns when capital is deployed below 50% utilization

**Security patterns reinforced:**
- External call safety: All API calls use `urllib` with timeouts, no `eval()` or dynamic imports
- Input validation: Price checks prevent division by zero and negative values
- Fallback chains: DexScreener fallback when CoinGecko is unavailable (no single point of failure)
- Error isolation: Each tool catches and returns structured errors, never crashes the agent

### Lesson: Safe External API Integration

**Cyfrin Module:** Secure Contract Design — External Calls

**Parallel to smart contracts:**
- Smart contracts: Use `try/catch` for external calls, implement fallbacks
- Our agent: Each signal tool has timeout-bounded HTTP calls with structured error returns
- Key principle: Never trust a single data source — always have a fallback path

## Swarms Marketplace

### Tokenization
- Agent is registered via Swarms SDK with `Agent` class
- Tools are exposed as callable functions the agent can invoke
- System prompt defines behavior and tool usage patterns

### Frenzy Mode
- Agent can be published to Swarms Marketplace
- Users interact with the agent via natural language queries
- Pricing model: $9.99 one-time access

### Supported Chains
- **Avalanche** — LFJ (Trader Joe) concentrated liquidity
- **Ethereum** — Uniswap V3 pools
- **Base** — Uniswap V3 pools
- Any chain supported by DexScreener API

## Submission Checklist

- [x] Signal engine implemented (7 tools)
- [x] Swarms agent orchestration (main.py)
- [x] Multi-chain support (Avalanche, Ethereum, Base)
- [x] README with documentation
- [x] Cyfrin lesson alignment documented
- [ ] Agent published to Swarms Marketplace
- [ ] Tokenization via Frenzy Mode
- [ ] Demo video recorded
- [ ] Submission form completed

## License

MIT — Built for the Swarms ACM Hackathon, May 2026.
