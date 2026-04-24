# Monetization Brainstorm — 2026-04-18

## Tier Model

### Free (Acquisition)
- Basic DeFi 101 tutor
- Limited queries/day (10-20)
- General education content
- Community access

### Small Ticket ($5-15/mo)
- Portfolio Analysis — IL breakdowns, rebalance suggestions
- Unlimited tutor queries
- Quiz & Certification — shareable DeFi knowledge badge
- Trade Simulator — "What would happen if I..." before real capital

### Power User ($25-50/mo)
- Strategy Coach — personalized, remembers risk tolerance/goals
- Alert System — LP out of range, IL threshold exceeded
- Multi-chain support
- Priority LLM — faster, better models

### B2B/API ($100+/mo)
- White-label tutors — protocols embed education in their UI
- API access — other agents use our analysis skills
- Custom tutor builds — "We want a tutor for our protocol"

## Quick Wins (Earn While Building)
- Premium Telegram group — $10/mo advanced signals + tutor access
- Course sales — structured DeFi curriculum, one-time purchase
- Sponsored content — protocols pay for unbiased reviews/education

## Jordan's Decision (2026-04-18)

**Model: Pay-per-launch, not subscription.**

- Free tier gets most features (education, analysis, portfolio tracking)
- **You pay to launch autonomous vaults/agents** that trade with our rules and guild lines
- **$5-10 USDC per bot/vault launch**
- User keeps a reserve to cover gas fees
- Wallet-based auth (both options if possible)

**Infrastructure decisions:**
- Hosting: VPS
- LLM: Local (Ollama)
- Auth: Wallet-based, both if possible

## Extension Tiers (Add-Ons)

Everyone gets the flagship education + analysis. Pay for power-ups:

### Free (Flagship)
- DeFi 101 tutor
- Portfolio tracking
- Basic pool analysis
- Community access

### Extensions (Pay-per-use or small fee)

| Extension | Price | What It Does |
|-----------|-------|--------------|
| **The Brain** | $2-3/mo | Persistent memory across sessions, personalized learning path, remembers your risk tolerance, goals, preferences |
| **Macro Intel** | $3-5/mo | News reader, market sentiment analysis, protocol updates, on-chain alerts |
| **Agent Marketplace** | 5% on sale | List/buy/sell bots, performance history, verified badges |
| **Premium Strategies** | $5-20 one-time | Pre-built strategies from top performers, verified configs |
| **Agent Insurance** | Variable | Cover bot losses up to a cap, paid per-launch or monthly |
| **Priority LLM** | $5/mo | Faster/better models for tutor interactions |

### Pay-Per-Launch (Autonomous Agents)
- $5-10 USDC per bot/vault launch
- Gas reserve included or separate
- This is the main revenue driver

## Why This Model Works
- Free tier = acquisition funnel (everyone gets value)
- Extensions = natural upsell (you want more, you pay more)
- Pay-per-launch = aligned incentives (only pay when you use power features)
- Marketplace = network effects (more listings → more buyers → more launches)

## Notes
- Route full pricing strategy to YoYo for competitive analysis
- Consider Avalanche ecosystem grants for education layer
- Need to design the "gas reserve" mechanism (escrow? prepaid balance?)
