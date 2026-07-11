---
title: AAE Dry Powder Vault — Technical Spec
date: 2026-06-05
status: Approved — Green Light
priority: P0
owner: Gentech Labs
---

# AAE Dry Powder Vault — Cross-Chain Smart Stablecoin Rotation

## Vision

A smart stablecoin vault that auto-rotates idle USDC across chains AND narratives. Two-dimensional rotation: which chain to be on, and which narrative on that chain. Users deposit USDC once — the agent handles everything.

**Core insight:** Nobody is building narrative-based rotation. Smart money rotates between memes, RWA, AI, gaming — but retail can't track it. The Agent ETF makes narrative rotation automatic and visible.

**June 8, 2026:** Added narrative rotation dimension — the "Agent ETF" concept. Vault now tracks both cross-chain rotation AND intra-chain narrative rotation.

## Architecture

### Three-Layer Stack (Extends AAE DeFi Milestone)
### Three-Layer Stack (Extends AAE DeFi Milestone)
```
┌─────────────────────────────────────────────────────────┐
│         PRESENTATION LAYER (Dashboard + Alerts)          │
│   2D rotation view, narrative heat map, zone tracker     │
├─────────────────────────────────────────────────────────┤
│           ORCHESTRATION LAYER (Hermes Agent)             │
│   Narrative momentum engine, yield monitoring, rotation  │
├─────────────────────────────────────────────────────────┤
│              EXECUTION LAYER (Cross-Chain)               │
│   CCTP bridging, DEX swaps, LP positioning, gas mgmt    │
├─────────────────────────────────────────────────────────┤
│               DATA LAYER (Signals)                       │
│   CMC zones, narrative rotation engine, yield feeds      │
└─────────────────────────────────────────────────────────┘
```

### Two-Dimensional Rotation Model

Dimension 1: **Cross-Chain** — which chain to deploy on
Dimension 2: **Narrative** — which sector on that chain

```
              Base      Avalanche     Solana
Blue Chips    ● AERO     ● AVAX        ● SOL
RWA/DeFi      ○          ● ONDO        ○
Memes         ○          ● COQ/ARENA   ● WIF/BONK
AI/DePIN      ○          ○             ● RENDER
Gaming        ○          ● BEAM/ILV    ○
Real Assets   ○          ● XAUt        ○
Political     ○          ○             ● TRUMP
```

User can choose:
  → **Multi-chain mode:** Agent rotates across all chains + narratives
  → **Chain-specific mode:** Pick one chain (e.g., Avalanche), rotate between narratives on that chain only
  → **Narrative-specific mode:** Pick one narrative (e.g., RWA), find the best chain for that narrative

| Chain | Role | Gas Token | Yield Source | Status |
|-------|------|-----------|--------------|--------|
| **Base** | Dry Powder Home | ETH (~$0.001) | Aerodrome LP | ✅ Live |
| **Avalanche** | Primary LP | AVAX (~$0.02) | LFJ (Trader Joe) | ✅ Live |
| **Solana** | High Yield | SOL (~$0.001) | Meteora/Kamino | ✅ Live |

### Future Chains (v2+)

| Chain | Role | Why |
|-------|------|-----|
| **Arc** | Institutional Home | USDC-native gas, built-in FX |
| **Ethereum** | Security | High-value settlements |
| **Arbitrum** | Balanced | Speed + cost |

---

## User Flow

### 1. Deposit
```
User: "I want to deposit $10K USDC into the Dry Powder Vault"
Agent: "Connected. Which chains do you want to use?"
  → Base (default, cheapest)
  → Avalanche (LP opportunities)
  → Solana (high yield)
  → All three (maximum rotation flexibility)
User: "All three"
Agent: "Depositing $10K USDC. Splitting across chains..."
  → $3,333 → Base (USDC sitting idle, earning base yield)
  → $3,333 → Avalanche (entering AVAX/USDC LP on LFJ)
  → $3,334 → Solana (entering USDC-SOL pool on Meteora)
Agent: "Done. You're earning across 3 chains. I'll monitor and rotate as needed."
```

### 2. Daily Monitoring
```
Every 4 hours, agent checks:
1. Current zone for each chain's assets
2. Narrative strength (which chain is hot)
3. Yield comparison (APY across chains)
4. News signals (any catalysts?)

If rotation is warranted:
Agent: "⚠️ Rotation Alert"
  "Avalanche AVAX/USDC LP yielding 12% APY"
  "Solana USDC-SOL pool yielding 8% APY"
  "Recommendation: Rotate $2K from Solana → Avalanche"
  "Approve? [Yes/No]"
```

### 3. Auto-Rotation (Advanced)
```
User enables auto-rotation:
Agent: "Auto-rotation enabled. I'll rotate when:"
  → Yield differential > 3% between chains
  → Narrative shift detected (e.g., AVAX enters Deep Value)
  → Risk threshold triggered (e.g., BTC drops below $58K)

Agent: "🔄 Rotating $1,500 USDC from Base → Avalanche"
  "Bridge: CCTP (Base → Avalanche)"
  "Swap: USDC → AVAX/USDC LP on LFJ"
  "Gas paid: $0.003 (Base) + $0.02 (Avalanche)"
  "Total cost: $0.023"
```

---

## Zone System

### Per-Chain Zones
Each chain has its own zone assessment based on:
- Current yield (APY relative to historical)
- Narrative strength (market sentiment)
- Risk level (volatility, correlation to BTC)
- Liquidity depth (can we exit if needed?)

### Zone Definitions
| Zone | Condition | Agent Action |
|------|-----------|--------------|
| 🔥 Deep Value | Chain undervalued, high yield | Increase allocation |
| 🟢 Accumulate | Chain fairly valued, good yield | Maintain or slight increase |
| 🔵 Watch | Chain overvalued, low yield | Decrease allocation |
| ⚪ Extended | Chain extremely overvalued | Exit to dry powder |

---

## Technical Components

### 1. Vault Contract (Solidity)
- ERC-4626 compatible vault
- Accepts USDC deposits
- Tracks per-chain balances
- Emits events for agent monitoring

### 2. Bridge Adapter
- Circle CCTP for USDC transfers
- Fallback to Across Protocol
- Gas estimation and optimization

### 3. DEX Adapter
- LFJ (Avalanche) — existing integration
- Meteora (Solana) — new integration needed
- Aerodrome (Base) — new integration needed

### 4. Agent Orchestrator
- Hermes agent framework
- Zone monitoring (from CMC watchlist)
- Narrative tracking (from agentic finance landscape)
- Rotation decision engine

### 5. Notification Layer
- Telegram alerts for rotation prompts
- Daily digest with position summary
- Celebration on milestone hits

---

## Revenue Model

| Revenue Stream | Source | Margin |
|----------------|--------|--------|
| Subscription | $15/mo Agent Pass | 100% |
| Swap fees | Each rotation | 0.3% per swap |
| Performance fee | 10% of yield above baseline | Variable |
| Gas rebate | Markup on gas costs | ~20% |

---

## MVP Scope (Hackathon Sprint)

### Week 1: Core Infrastructure
- [ ] Vault contract (ERC-4626)
- [ ] CCTP bridge integration
- [ ] Basic agent orchestrator

### Week 2: Yield Sources
- [ ] LFJ (Avalanche) — extend existing integration
- [ ] Meteora (Solana) — new integration
- [ ] Aerodrome (Base) — new integration

### Week 3: Intelligence Layer
- [ ] Zone monitoring (from CMC watchlist)
- [ ] Narrative tracking
- [ ] Rotation decision engine

### Week 4: User Experience
- [ ] Telegram bot interface
- [ ] Dashboard screenshots (extend DeFi system)
- [ ] Daily digest cron job

---

## Success Metrics

- **TVL:** $100K in first month
- **Rotations:** 50+ successful cross-chain rotations
- **Yield:** Outperform single-chain holding by 2%+
- **Users:** 10 paying subscribers in first quarter

---

## Dependencies

- Circle CCTP (live on mainnet)
- Hermes agent framework (existing)
- CMC watchlist + zones (existing)
- LFJ integration (existing)
- Meteora SDK (needs research)
- Aerodrome SDK (needs research)

---

*Spec approved June 5, 2026. Ready for Labs execution.*
