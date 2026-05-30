# Agent Arena — Agent Academy Engine

## Formal Specification v1.0

**Status:** 🟢 TOKENOMICS LOCKED — $TECH as economic backbone confirmed. Pricing decided. Krexa integration resolved. Buyback engine designed.
**Author:** Gentech (HQ)
**Date:** 2026-05-21
**Classification:** Flagship Product — Internal Blueprint

---

## 1. Vision

Agent Arena is a **rogue-lite social trading game** where players manage autonomous AI agents in a simulated DeFi economy. Think *Test Drive Unlimited* meets *FTL* — you outfit agents with loadouts, queue into solo or duo runs, and your risk management skill determines whether you profit or get liquidated.

**The pitch:** Real DeFi mechanics, zero real money. Learn to trade, borrow, manage risk, and build reputation — then take those skills on-chain when you're ready.

**Built on Krexa.** The agent platform is our foundation, not a feature.

---

## 2. Core Identity

| Attribute | Value |
|-----------|-------|
| **Genre** | Rogue-lite social trading simulation |
| **Platform** | Krexa (agent runtime + on-chain integration) |
| **Tone** | Competitive but educational — stakes feel real, losses teach |
| **Inspiration** | Test Drive Unlimited (open-world progression), FTL (run-based risk), Balatro (compounding mechanics) |
| **Target** | Crypto-curious players, DeFi natives wanting practice, hackathon judges |
| **Revenue** | Free-to-play core + Premium tier (stealth mode, private services) |

---

## 3. Game Architecture

### 3.1 The Run

Each game session is a **run** — a discrete attempt to grow capital through trading, borrowing, and strategic risk-taking. Runs end when:

- **Cash out:** Player voluntarily exits with accumulated profit
- **Liquidated:** Margin breached, positions auto-closed, run over
- **Bankrupt:** Balance hits zero, score penalized, fresh start
- **Time limit:** Market regime shifts close the window

Between runs, your **Credit Score** and **Reputation** persist. This is the meta-progression layer — lose a run, your score drops. Win consistently, your borrowing power grows.

### 3.2 Solo vs. Duo Queue

| Mode | Description |
|------|-------------|
| **Solo Queue** | Standard run. You vs. the market. Manage your own agents, your own risk. |
| **Duo Queue** | Two players share a portfolio pool. Coordinate positions, split risk, or betray (take profit and leave partner overleveraged). Trust mechanics apply. |

**Duo-specific mechanics:**
- Shared credit pool with individual risk caps
- Communication layer for strategy coordination
- "Abandon" action — one player exits, the other absorbs full exposure
- Duo reputation score (separate from individual)

### 3.3 Market Regimes

The simulated market cycles through regimes that force strategy adaptation:

| Regime | Characteristic | Strategy Shift |
|--------|---------------|----------------|
| **Bull** | Rising prices, low volatility | HODL + leveraged longs profitable |
| **Bear** | Falling prices, high volatility | Shorting + stablecoins shine |
| **Crab** | Sideways, low volume | Range trading, LP fees earn |
| **Black Swan** | Flash crash, liquidation cascade | Survival mode — who stays solvent? |
| **DeFi Summer** | Yield farming bonanza, new pools | Farm early, harvest before rug |

Regime transitions are signaled 3 turns in advance (analyst agent detects). The transition itself is the critical decision window.

---

## 4. Agent Architecture

### 4.1 The Four-Agent Stack

Each player controls a team of autonomous agents. Agents are not just UI wrappers — they have independent logic, reputation, and failure modes.

```
┌─────────────────────────────────────────────────────────┐
│                    PLAYER LAYER                         │
│  Set Preferences → Fund Portfolio → Monitor Dashboard   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              📊 AGENT 1: ANALYST                        │
│  "The Eyes"                                             │
│  • Market regime detection (trending/ranging/volatile)  │
│  • On-chain liquidity flow tracking                     │
│  • TVL shifts, yield changes, volume analysis           │
│  • Feeds signals → Strategy Brain                       │
│  • Failure mode: false signals → bad trades             │
└──────────────────────┬──────────────────────────────────┘
                       │ signals
┌──────────────────────▼──────────────────────────────────┐
│              🧠 AGENT 2: STRATEGY BRAIN                 │
│  "The Brain"                                            │
│  • Receives analyst signals + player preferences        │
│  • Decides allocation rotation: LP → Stake → HODL → Farm│
│  • Manages risk parameters (drawdown, exposure)         │
│  • Memory layer — learns from past allocations          │
│  • Failure mode: overconfident after win streak         │
└──────────────────────┬──────────────────────────────────┘
                       │ approved orders
┌──────────────────────▼──────────────────────────────────┐
│              ✅ AGENT 3: VALIDATOR                      │
│  "The Safety Net"                                       │
│  • Reviews every Brain decision BEFORE execution        │
│  • Risk checks: position sizing, exposure caps          │
│  • Reputation scoring — tracks Brain's hit rate         │
│  • Approve / Reject / Veto with reasoning               │
│  • Anti-rug: prevents catastrophic single decisions     │
│  • Failure mode: too conservative → missed opportunities│
└──────────────────────┬──────────────────────────────────┘
                       │ validated orders
┌──────────────────────▼──────────────────────────────────┐
│              ⚡ AGENT 4: EXECUTOR                       │
│  "The Hands"                                            │
│  • Pure on-chain execution — NO decision-making         │
│  • LP management, staking, farming, swaps               │
│  • Gas optimization, slippage protection                │
│  • Transaction receipts + status reporting              │
│  • Failure mode: execution failure → slippage loss      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              🔄 FEEDBACK LOOP                           │
│  Execution results → Brain learns                       │
│  Validator scores → Reputation updates                  │
│  Analyst adjusts → Signal calibration                   │
│  Player review → Loadout optimization                   │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Agent Progression

Agents level up through successful runs. Higher-level agents have better base stats but cost more to equip.

| Level | XP Required | Bonus |
|-------|-------------|-------|
| 1 | 0 | Baseline |
| 2 | 100 XP | +5% accuracy |
| 3 | 300 XP | +10% accuracy, -10% false signals |
| 4 | 600 XP | +15% accuracy, early regime detection |
| 5 | 1000 XP | +20% accuracy, autonomous mode unlocked |

**Agent XP** is earned per run: survive longer = more XP. Liquidation = reduced XP gain.

### 4.3 ERC-8004 Agent Identity

Agent Arena agents are identified on-chain via **ERC-8004** — the Trustless Agents standard. ERC-8004 defines agent identity as ERC-721 NFTs, giving each agent a portable, verifiable, self-sovereign identity across EVM chains.

**What ERC-8004 provides:**
- **ERC-721 NFT identity tokens** — each agent owns a non-transferable identity NFT (soulbound-style) that anchors its on-chain reputation, permissions, and history
- **Standardized agent metadata** — name, capabilities, trust level, and registry membership encoded in the token
- **Composable with DeFi** — agents can interact with protocols that recognize ERC-8004 tokens for permissioned access

**Three ERC-8004 Registries → AAE Layer Mapping:**

| ERC-8004 Registry | AAE Layer | Integration Role |
|-------------------|-----------|------------------|
| **Identity Registry** | Identity Layer | Agent self-sovereign identity — register, resolve, verify agent wallets on-chain. Root of trust for all downstream AAE operations. |
| **Reputation Registry** | Credit Layer | Agent reputation scores, transaction history, and creditworthiness. Powers risk assessment, credit limits, and trust propagation across agent networks. |
| **Validation Registry** | Safety Layer | Proof-of-computation, task completion attestation, and dispute resolution hooks. Feeds the AAE safety layer with verifiable execution evidence. |

**Cross-Chain Portability:**
ERC-8004 is deployed across **29+ EVM chains** (Ethereum, Base, Arbitrum, Optimism, BNB Chain, Polygon, Avalanche, etc.). Agent identities are portable — an agent registered on one chain can be recognized on any other supported chain. This is critical for Agent Arena's multi-chain strategy (see §17 Integration Layer).

**SDK Integration Paths:**
- **0xGasless Agent SDK** (primary path) — bundles ERC-8004 + x402 payments, gasless transaction relay removes UX barrier of agent wallet gas management. We have an API key. Cuts Phase 1/3 timelines by ~40%. See build brief below.
- **BNBAgent SDK** (secondary/partner) — Python SDK with 100K+ agents on BNB Chain. Modules: Identity (ERC-8004), Commerce (ERC-8183), Payments (x402/MPP), Memory (Greenfield). Partners: Google Cloud, AWS, Binance Pay. Use for Commerce and Memory only; defer identity/payment to 0xGasless.

**Build brief:** `09-Green Room/build-logs/2026-05-30-erc8004-aae-integration.md`

**Phase 5 on-chain bridge dependency:** ERC-8004 identity registration is a prerequisite for on-chain credit score portability and escrow mechanics (see §13 Roadmap — Phase 5).

---

## 5. NFT Loadout System

### 5.1 Agent Loadouts

Each agent can be equipped with **loadout items** — NFTs that modify agent behavior, stats, or unlock abilities.

**Loadout slots per agent:**
- **Core Module** (1 slot) — Primary behavior modifier
- **Enhancement** (2 slots) — Stat bonuses
- **Risk Modifier** (1 slot) — Changes risk parameters

### 5.2 Item Categories

#### Core Modules
| Item | Effect | Rarity |
|------|--------|--------|
| Alpha Predictor | Analyst gets +20% signal accuracy | Legendary |
| Contrarian Engine | Brain favors counter-trend trades | Epic |
| Safety Override | Validator auto-veto threshold tightened | Rare |
| Speed Executor | 50% faster execution, lower slippage | Epic |
| Yield Maximizer | +15% yield on farming positions | Rare |

#### Enhancements
| Item | Effect | Rarity |
|------|--------|--------|
| Stabilizer | -10% volatility on portfolio | Common |
| Compounder | +5% compound interest on returns | Uncommon |
| Shield | Liquidation threshold raised by 10% | Rare |
| Oracle Lens | Regime detection 1 turn earlier | Epic |

#### Risk Modifiers
| Item | Effect | Rarity |
|------|--------|--------|
| Stop-Loss Protocol | Auto-sell at configurable loss % | Common |
| Leverage Limiter | Caps max borrow multiplier | Common |
| Anti-Rug Scanner | Flags suspicious pool contracts | Uncommon |
| Circuit Breaker | Halts all execution on flash crash | Rare |

### 5.3 Item Acquisition

- **Run rewards:** Complete runs to earn random loot boxes
- **Achievements:** Specific milestones unlock specific items
- **Marketplace:** Trade items with other players (Krexa on-chain)
- **Crafting:** Combine lower-rarity items into higher-rarity ones
- **Premium drops:** Exclusive items for Premium subscribers

### 5.4 Item Ownership

Items are **NFTs on Krexa**. Own them, trade them, flex them. When you sell an item, it removes from your loadout and goes to the buyer's inventory. No item is permanently bound.

---

## 6. Credit & Reputation System

### 6.1 Credit Score (0–1000)

The composite score that determines your borrowing power and matchmaking bracket.

```
score = weighted_sum(
    on_chain_history × 0.30,     // transaction volume, age, consistency
    protocol_diversity × 0.15,   // breadth of ecosystem participation
    financial_health × 0.25,     // collateral, repayment, defaults
    reputation_signals × 0.20,   // vouches, endorsements, dispute outcomes
    identity_verification × 0.10 // KYA status, ERC-8004 registration
)
```

#### Tiers
| Tier | Score | Borrow Multiplier | Matchmaking |
|------|-------|-------------------|-------------|
| Unverified | 0–300 | 0.5x | Tutorial lobbies |
| Bronze | 300–500 | 1.0x | Bronze tier |
| Silver | 500–650 | 1.5x | Silver tier |
| Gold | 650–800 | 2.0x | Gold tier |
| Platinum | 800–900 | 3.0x | Platinum tier |
| Diamond | 900–1000 | 5.0x | Diamond tier (top players) |

#### Score Decay
- Inactivity: -10/month after 30 days inactive
- Liquidation: -100 per event
- Missed payment: -50 per event
- Default: -100 per default event
- Recovery: rebuild through positive activity (no shortcuts)

### 6.2 Borrowing Mechanics

Players borrow virtual capital against their credit score.

- Borrowed capital has a **simulated interest rate** (varies by tier)
- **Revenue Router pattern**: 30% of trade profits auto-repay debt
- Borrowing limit scales with credit score tier
- Missed payments → score penalty → reduced limit
- **Borrow by reputation**: Higher rep = better rates, higher limits

### 6.3 Liquidation Engine

When unrealized loss exceeds margin, position auto-closes.

- Liquidation threshold: 80% of borrowed capital (configurable by loadout)
- **Liquidation penalty**: Score drop + 7-day borrow freeze
- **Recovery path**: Trade back up, rebuild score, learn from the loss
- Game teaches: impatience + ignoring bot advisors = liquidation faster

---

## 7. Consequences Framework

Agent Arena is rogue-lite. **Losses have teeth.** This is what makes the game compelling — real stakes without real money.

### 7.1 Run-Level Consequences

| Event | Consequence | Recovery |
|-------|-------------|----------|
| **Liquidation** | Run ends, -100 credit score, 7-day borrow freeze | Win next run to offset |
| **Bankruptcy** | Run ends, -50 credit score, inventory locked 24hrs | Start new run with reduced capital |
| **Bad debt** | -200 credit score, lose 1 loadout item | Rebuild through 3 successful runs |
| **Duo abandon** | -150 duo reputation, solo queue locked 48hrs | Complete 2 duo runs without abandon |

### 7.2 Meta-Level Consequences

| Event | Consequence | Recovery |
|-------|-------------|----------|
| **5+ consecutive losses** | "Tilted" status — -10% all returns for 24hrs | Wait it out or win 2 in a row |
| **Exploit attempt** | Flagged account — all loadouts unequipped | Appeal process (24hr review) |
| **Top 10 leaderboard demotion** | Loss of exclusive items until re-earned | Climb back up |
| **Credit score < 200** | Restricted to tutorial lobbies | Rebuild from basics |

### 7.3 Why Consequences Matter

The game loop **teaches risk management through loss.** Players who YOLO get liquidated. Players who manage position sizing survive. The credit score makes this persistent — you can't just restart and be fine. This is the core differentiator from every other trading sim.

---

## 8. Premium Tier

### 8.1 Free Tier (Core Game)
- Full access to solo and duo queues
- Standard loadout slots (4 per agent)
- Credit score progression
- All market regimes
- Community marketplace access

### 8.2 Premium ("Academy Graduate")
| Feature | Description |
|---------|-------------|
| **Stealth Mode** | Your positions are hidden from other players' Analyst agents. No one can copy-trade you or front-run your moves. |
| **Private Services** | Access exclusive bot advisors with advanced strategies. Custom risk parameters. Priority queue. |
| **Extended Loadout** | 2 additional loadout slots per agent (6 total) |
| **Replay Library** | Review past runs with full decision tree visualization |
| **Custom Regimes** | Create and share custom market scenarios |
| **Priority Support** | Faster response to exploits, bugs, balance issues |

### 8.3 Pricing Model — "Data Layer is the Product"

**Core insight:** The agent is the delivery mechanism. The data layer is the real product. We subsidize the agent with the intelligence.

| Tier | Price | What you get | What we get |
|------|-------|-------------|-------------|
| **Free** | $0 | Full agent included — trading signals, market analysis, credit scoring | User behavior data feeds the platform (you're the product) |
| **Premium** | $15/mo | Privacy opt-out, no data harvesting, full agent access, stealth mode | Recurring revenue, no data harvesting rights |
| **Pay-per-use** | Variable | Micropayments via x402/Circle — 50¢ for deep route analysis, $2 for full city guide, etc. | Transaction revenue without subscription commitment |

**Key principles:**
- Free tier is generous — the agent works well, the data is what we monetize
- Premium removes data harvesting — privacy is the product upgrade
- Pay-per-use via x402/Circle for premium queries without sub commitment
- NFT-gated access: Hold a Genesis Agent NFT = permanent Premium (tier TBD)
- Dual pricing: USDC full price, $TECH 20–30% discount (when token launches)

**AWS analogy:** We subsidize the agent with the intelligence. Free users generate data that makes the platform smarter. Premium users pay to opt out. Pay-per-use captures value from one-off queries.

---

## 9. Krexa Integration

### 9.1 Why Krexa

Krexa provides the agent runtime infrastructure that makes Agent Arena possible:

- **Agent deployment**: Spin up autonomous agents with persistent state
- **Browser tooling**: Solana-native session management
- **On-chain identity**: Agent wallets, transaction signing
- **Marketplace**: NFT minting, trading, discovery

### 9.2 Integration Points

| Agent Arena Component | Krexa Feature |
|---------------|---------------|
| Agent Runtime | Krexa agent deployment + persistent state |
| NFT Loadouts | Krexa NFT minting + marketplace |
| Credit Score | Krexa on-chain identity + ERC-8004 |
| Duo Queue | Krexa agent-to-agent communication |
| Marketplace | Krexa NFT marketplace + trading |
| Premium | Krexa subscription management |

### 9.3 On-Chain Hooks

Agent Arena bridges game mechanics to real on-chain infrastructure:

- **Credit scores** can eventually port to on-chain reputation (Agent Arena Credit Layer infra)
- **Agent loadouts** are tradeable NFTs with real value
- **Top player strategies** can be published as copy-trade templates
- **Escrow mechanics** enable trustless duo partnerships

---

## 10. Technical Architecture

### 10.1 System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│  Web UI (React/Next.js) ←→ WebSocket ←→ Game State      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 GAME SERVER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Run Manager  │  │  Matchmaker  │  │  Market Sim  │  │
│  │  (lifecycle)  │  │  (solo/duo)  │  │  (regimes)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Agent Engine │  │  Credit Svc  │  │  NFT Manager │  │
│  │  (4 agents)   │  │  (scoring)   │  │  (inventory) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  DATA LAYER                              │
│  PostgreSQL (player state) + Redis (real-time) +        │
│  Krexa (NFT + identity) + SQLite (local dev)            │
└─────────────────────────────────────────────────────────┘
```

### 10.2 Tech Stack (v1)

| Component | Technology |
|-----------|------------|
| **Client** | React + TypeScript + Canvas (charts) |
| **Server** | Python (FastAPI) — reuse existing Agent Arena game logic |
| **Database** | PostgreSQL (prod) / SQLite (dev) |
| **Real-time** | WebSocket (game state sync) |
| **Agent Runtime** | Krexa (agent deployment + persistence) |
| **NFT** | Krexa NFT standard (Solana) |
| **Auth** | Krexa identity + wallet connection |
| **Infra** | Docker → cloud deploy |

### 10.3 Existing Code (Reused)

The credit layer game (`/root/workspace/aae-game/`) provides foundational modules:

| Module | LOC | Status | Reuse |
|--------|-----|--------|-------|
| `credit_engine.py` | 172 | ✅ Shipped | Core scoring → Game Server Credit Service |
| `trading.py` | 190 | ✅ Shipped | Spot trading → Market Sim engine |
| `borrowing.py` | 264 | ✅ Shipped | Borrow mechanics → Credit Service |
| `risk.py` | 233 | ✅ Shipped | Liquidation → Risk engine |
| `game.py` | 318 | ✅ Shipped | Game loop → Run Manager |

**Total reusable:** ~1,177 LOC of tested, working game logic.

---

## 11. Exodia Strategy — Modular Hackathon Deployment

Agent Arena is not a monolith. Each layer can standalone as a hackathon submission:

| Layer | What It Does | Best Hackathon Track |
|-------|-------------|---------------------|
| **Brain** | Decision-making, strategy engine | AI Agents, Autonomous Systems |
| **Credit** | x402 agent-to-agent payments | Payments, DeFi Infrastructure |
| **Agent Marketplace** | On-chain task execution | Agentic, Marketplaces |
| **LP Monitor** | DeFi liquidity monitoring + signals | DeFi, Data, Analytics |
| **Agent Escrow** | Trustless agent task escrow | Payments, Trust, Escrow |
| **Infra** | RPC, deployment, monitoring | Developer Tools, Infrastructure |

**The endgame:** While competitors build single-use tools, we stress-test a modular stack. Each hackathon validates a component in production. Show the pieces first. Show the whole later.

---

## 12. Revenue Model

| Stream | Description | Pricing |
|--------|-------------|---------|
| **Premium Subscription** | Privacy opt-out, no data harvesting, full agent access | $15/mo |
| **Pay-per-use** | Micropayments via x402/Circle for premium queries | Variable (50¢-$2+ per query) |
| **NFT Marketplace** | Loadout item trading fees | 2.5% transaction fee |
| **Genesis Agent NFTs** | Limited edition starter agents | One-time mint |
| **Score API Access** | Protocols query agent credit scores | Free tier → $0.001/query |
| **Premium Data** | Detailed behavioral analytics | $50-500/mo per protocol |
| **Copy-Trade Templates** | Top player strategy subscriptions | Revenue share |

---

## 13. Roadmap

### Phase 1: Foundation (Current)
- [x] Credit layer game mechanics (shipped)
- [x] Hybrid Strategy Brain architecture (approved)
- [x] Exodia modular strategy (defined)
- [x] Credit layer infrastructure research (complete)
- [ ] **This document** — Formal spec (in progress)

### Phase 2: MVP
- [ ] Web UI — trading dashboard with real-time market
- [ ] Agent Engine — 4-agent stack wired to game logic
- [ ] Matchmaker — solo queue with tier-based matchmaking
- [ ] NFT Loadout — basic inventory system on Krexa
- [ ] Credit Score — persistent cross-run scoring

### Phase 3: Social
- [ ] Duo Queue — shared portfolio, trust mechanics
- [ ] Leaderboards — seasonal rankings
- [ ] Marketplace — NFT loadout trading
- [ ] Copy-Trade — follow top players' strategies
- [ ] Chat/Comms — in-game coordination for duos

### Phase 4: Premium
- [ ] Stealth Mode — position hiding
- [ ] Private Services — exclusive bot advisors
- [ ] Custom Regimes — user-created market scenarios
- [ ] Replay System — full decision tree review

### Phase 5: On-Chain Bridge
- [ ] Credit Score portability (cross-chain via CCIP)
- [ ] Agent identity (ERC-8004)
- [ ] On-chain escrow for duo partnerships
- [ ] Strategy publication as on-chain templates

---

## 14. Open Questions

1. ~~**Krexa partnership:** Do we need formal integration approval, or can we build on Krexa permissionlessly?~~ → **RESOLVED:** No formal partnership needed. Krexa has open developer docs and a prompt-based integration kit. Build permissionlessly.
2. **NFT standard:** Krexa's native NFT standard or custom? Need to check Krexa SDK docs (krexa.xyz, t-credit.vercel.app). SDK appears to be Solana-native with PDA wallets.
3. **Matchmaking algorithm:** ELO-based? Credit-score-based? Hybrid?
4. **Season model:** Monthly resets? Quarterly? Permanent with seasonal leaderboards?
5. **Mobile:** Web-first, but mobile-responsive? Native app later?
6. ~~**Tokenomics:**~~ → **LOCKED (2026-05-21):** $TECH is the economic backbone of Agent Arena. Buyback engine design confirmed. See Section 16.

---

## 15. Success Criteria
- [ ] Formal spec reviewed and approved by Jordan
- [ ] Web UI MVP with basic trading dashboard
- [ ] 4-agent stack running in solo queue
- [ ] NFT loadout system functional on Krexa
- [ ] Credit score persisting across runs
- [ ] At least one hackathon submission using an Agent Arena layer
- [ ] 10+ active players in testing

---

## 16. $TECH Tokenomics — The Economic Backbone

**Locked:** 2026-05-21 by Jordan. $TECH is the native economic layer of Agent Arena.

### 16.1 Core Principle

$TECH is not a bolt-on — it is the **economic backbone** of Agent Arena. Every revenue stream in the game flows back to $TECH through a buyback engine, creating a natural demand sink that compounds with the game's growth.

### 16.2 $TECH in Agent Arena

| Use Case | Description |
|----------|-------------|
| **Premium Payments** | Premium tier ($15/mo) accepts $TECH at **20–30% discount** vs USDC pricing |
| **NFT Marketplace** | Loadout items can be bought/sold in $TECH |
| **Crafting Fees** | Combine items using $TECH as gas |
| **Tournament Entry** | Competitive modes require $TECH entry fees |
| **Agent Leveling** | Speed-up agent XP with $TECH (optional, not pay-to-win) |

### 16.3 Buyback Engine

Game revenue funnels back to $TECH buybacks, creating a **self-reinforcing demand loop**:

```
Revenue Sources                →  Buyback Pool  →  $TECH Demand
──────────────────────────────────────────────────────────────
Premium Subscriptions (USDC)   ─┐
NFT Marketplace Fees (2.5%)    ─┤
Genesis Agent NFT Mints        ─┤              →   Buy $TECH
Tournament Entry Fees          ─┤              →   Burn or hold
Crafting Fees                  ─┘
```

**Buyback allocation:**
- **40%** — Direct buyback + burn (permanent supply reduction)
- **30%** — Buyback + hold in treasury (backing reserve)
- **20%** — Player rewards pool (staking, achievements, seasonal airdrops)
- **10%** — Development fund (continued building)

### 16.4 The Flywheel

```
More Players → More Revenue → More Buybacks → Higher $TECH Demand
     ↑                                                    │
     └──── Higher Floor Price ←──────────────────────────┘
```

This is the compounding loop Jordan locked in:
1. **Growth drives demand** — every new player generates revenue that buys back $TECH
2. **Scarcity drives price** — buyback + burn reduces circulating supply
3. **Price drives prestige** — holding $TECH becomes a status signal within Agent Arena
4. **Prestige drives growth** — players want to be part of a thriving economy

### 16.5 Anti-Whale Protections

To prevent $TECH from becoming a pay-to-win vector:
- Premium discounts are capped at 30% (not unlimited purchasing power)
- Agent leveling via $TECH has diminishing returns
- Tournament brackets separate $TECH-heavy players from free-tier
- Core gameplay (solo/duo queue, credit scoring) is fully free

### 16.6 Token Velocity Control

High velocity = spend fast, no hold pressure. Controls implemented:
- **Staking rewards** — lock $TECH for 30/60/90 days, earn boosted rewards
- **Exclusive items** — some loadouts only purchasable with staked $TECH
- **Seasonal sinks** — limited-time items/events that absorb $TECH supply
- **Crafting burns** — combining items permanently removes $TECH from circulation

---

## 17. Integration Layer (Network Effect Strategy)

**Core Principle:** Don't compete — integrate. Build the experience layer, plug into existing infrastructure.

### 17.1 What We Own (Experience Layer)
- **Game Mechanics**: Loadouts, strategies, reputation, matchmaking
- **Voice Interface**: Speech Engine integration (real-time voice trading)
- **User Experience**: Agent Arena app, dashboard, social features
- **Credit System**: Krexa credit scoring + reputation tracking

### 17.2 What We Integrate (Infrastructure Layer)
| Partner | Integration | Value |
|---------|-------------|-------|
| **Bankr** | Token launches + revenue share | 57% trading fees to agents |
| **WURK** | Human verification + microtasks | Real-world data + social campaigns |
| **Swarms** | Agent distribution + marketplace | Reach existing agent users |
| **EarnFi** | Agent API for jobs + campaigns | x402 native payments |
| **x402** | Autonomous payments | Solana + Base + Arc support |

### 17.3 Network Effect Play
- **Be on their platforms** → get their users
- **Build our platform** → give them reasons to stay
- **Multiple chains = multiple brains, same body**
- No rules say we can't be everywhere

### 17.4 The Mantra
"Multiple chains, multiple brains"

---

*This document is the single source of truth for Agent Arena. All other Agent Arena docs reference back to this spec. Update as decisions evolve.*

### EarnFi Campaign Rewards (Added May 22)
High reputation = free/discounted social campaigns on EarnFi.

**Reward Tiers:**
- Diamond (900-1000): Free campaigns monthly
- Platinum (800-900): 50% discount
- Gold (650-800): 25% discount
- Silver (500-650): 10% discount
- Bronze (300-500): Full price
- Unverified (0-300): No access

**Incentive:** Play well → build rep → get tools to grow → more growth → higher rep


### Rep-as-Currency System (Updated May 22)
Rep is spendable across the ecosystem — earn by playing, spend on real services.

**Earn Rep:**
- Complete trades (volume-based)
- Win matches (solo/duo)
- Help other players (verification, feedback)
- Achieve milestones (streaks, first trades, etc.)

**Spend Rep:**
| Service | Rep Cost | Description |
|---------|----------|-------------|
| EarnFi Campaign | 50-200 | Launch social promotion |
| WURK Job | 25-100 | Hire humans for verification |
| Premium Feature Unlock | 300 | Voice interface, advanced analytics |
| NFT Item Purchase | 100-500 | Loadout items in marketplace |
| Agent Upgrade | 150-400 | Boost agent capabilities |

**The Model:** Speedway rewards — earn points, spend on real services. Not tier-based discounts. Actual spendable currency with tradeoffs.

**Decision Points:** Players must choose how to allocate limited rep across services.


### Accountability Layer — Personal Stakes Roasting (Added May 22)
Risk management through personalized roasts based on user goals.

**Onboarding:**
- "Tell us about yourself" — what you have, what matters, what you're saving for
- "What would hurt to lose?" — trip, car, house, relationship
- Profile locked in — system knows what's at stake

**Roast Triggers:**
| Behavior | Roast Example |
|----------|---------------|
| Doing well | "Keep this up and that trip is looking real nice" |
| Doing bad | "I guess we don't have to worry about you saving for that trip, huh?" |
| Getting liquidated | "You ain't going nowhere with trades like this" |
| Reckless leverage | "You really want to lose that car, don't you?" |
| Recovering | "Hey, at least you're not sleeping on the couch tonight" |
| Streak win | "Okay big timer, maybe that vacation IS happening" |
| Streak loss | "Maybe we should talk about that savings account instead" |

**Why it works:** Personal stakes > abstract numbers. Trading isn't abstract anymore — it's about YOUR life. Humor as risk management.

**Integration:** Agent-Repairathy voices (Good Cop/Bad Cop) deliver the roasts.

