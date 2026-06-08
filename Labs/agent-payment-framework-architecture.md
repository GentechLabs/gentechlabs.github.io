# Agent Payment Framework — Architecture

## Core Concept
ONE framework, THREE chains. Write core logic once, swap settlement adapters.

## Architecture

```
┌─────────────────────────────────────────────────┐
│           AGENT PAYMENT FRAMEWORK               │
│         (core logic — stays the same)           │
├─────────────────────────────────────────────────┤
│  • Agent registration                           │
│  • Service discovery + approval                 │
│  • Payment execution with spending limits       │
│  • Daily budget tracking                        │
│  • Event logging for auditability               │
└───────────────┬──────────────┬──────────────────┘
                │              │
    ┌───────────▼──────┐  ┌───▼──────────────┐
    │   Kite Adapter   │  │  Circle Adapter  │
    │  • KITE token    │  │  • USDC          │
    │  • Kite chain    │  │  • Arc chain     │
    │  • AA SDK        │  │  • x402 protocol │
    │  • Agent Passport│  │  • CCTP bridge   │
    └──────────────────┘  └──────────────────┘
                │              │
    ┌───────────▼──────────────▼──────────────┐
    │         Avalanche Adapter              │
    │  • AVAX + USDC                         │
    │  • C-Chain                             │
    │  • Retro9000 grant alignment           │
    └────────────────────────────────────────┘
```

## Core Contract: AgentPaymentFlow
Functions:
- `registerAgent()` — agent registration
- `discoverService()` — service discovery + approval
- `executePayment()` — payment with spending limits
- `getDailyBudget()` — daily budget tracking
- `getEventLog()` — audit trail

## Chain Adapters
| Chain | Settlement | Protocol | Notes |
|-------|-----------|----------|-------|
| Kite | KITE token | AA SDK + Agent Passport | Hackathon #1 |
| Arc | USDC | x402 + CCTP | Hackathon #2 |
| Avalanche | AVAX + USDC | C-Chain | Retro9000 grant |

## Dogfooding
We use Kite for our own Gentech operations:
- Building the tool
- Using the tool
- Demo = "We use this ourselves"

## Hackathon Strategy
1. Kite hackathon: "Agent payments on Kite"
2. ARC hackathon: "Same framework, USDC via Circle"
3. Retro9000: "Same framework, Avalanche C-Chain"
4. Portfolio: "Multi-chain agent payment protocol"

One codebase. Three chains. Maximum leverage.

## Revenue Model (from YoYo's analysis)

### Three Revenue Streams
| Stream | Revenue Type | Scale Potential |
|--------|-------------|-----------------|
| Launch fees | $5-10 USDC per bot | Per-user, bounded |
| Extensions | $2-7/mo add-ons | Recurring, predictable |
| Swap fees | 0.1-0.3% on every trade | Per-volume, uncapped 🔥 |

Swap fees = the real money. Every trade agents execute = platform cut. Volume scales with users AND activity.

Example: 1,000 users × $50 avg daily volume = $50k/day → $50-150/day swap fees alone.

### Multichain Roadmap
| Phase | Chain | Why |
|-------|-------|-----|
| Launch | Avalanche | Cheap gas, LFJ ecosystem, sub-second finality |
| Phase 2 | Base | Coinbase L2, retail influx, low gas |
| Phase 3 | Arbitrum | Largest DeFi L2 by TVL |
| Phase 4 | Solana | Speed, huge volume, different user base |
| Phase 5 | Ethereum | Prestige + whale liquidity |

### Marketing Hook
"No subscriptions. No hidden fees. Pay when you trade. Learn for free."

---

*From previous session context — YoYo's revenue model analysis*
*Saved: Apr 20, 2026*
