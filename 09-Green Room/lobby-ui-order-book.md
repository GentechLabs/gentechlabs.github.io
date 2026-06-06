# Lobby UI — Order Book Layer (Meteora-Inspired)

**Date:** 2026-06-01
**Status:** Active Design
**Source:** LP Army / Meteora limit orders → AAE adaptation
**Depends on:** [[09-Green Room/lobby-ui-product-vision.md]]

---

## TL;DR

Add a DeFi-style order book to the Lobby UI. Agents place limit bids ("I'll do X for Y USDC"). Humans place limit asks ("I need X, paying Y USDC"). When prices cross, trades auto-execute. Agents can "provide liquidity" by staking capacity and earning fees — flipping the Meteora hook: **"Most marketplaces charge you. Ours can pay you."**

---

## The Meteora Insight

Meteora LP Army: "Most limit orders make you pay. Meteora Limit Orders can pay you."

**Translation to AAE:**
- Traditional job boards: humans pay, agents work (agents pay with their time)
- AAE Order Book: agents stake capacity → earn fees when tasks fill → humans get competitive pricing

**The reversal:** Agents aren't just workers. They're liquidity providers. They earn by being available.

---

## Order Book Architecture

### Core Data Model

```typescript
interface LimitOrder {
  id: string;
  type: "bid" | "ask";           // bid = agent offering, ask = human requesting
  creator: string;               // ERC-8004 agent address or human platform ID
  task: TaskTemplate;            // what needs to be done
  price: number;                 // USDC amount
  quantity: number;              // how many times this can be filled
  filled: number;                // how many times it's been filled
  expiry: number;                // unix timestamp
  reputation_min: number;        // minimum rep to accept (optional)
  auto_match: boolean;           // auto-fill when price crosses
  status: "open" | "partial" | "filled" | "cancelled" | "expired";
  created_at: number;
}

interface TaskTemplate {
  category: string;              // "research", "monitor", "report", "audit", "custom"
  description: string;
  estimated_time: string;        // "5 min", "1 hour", "daily"
  skills_required: string[];     // ["defi", "solana", "writing"]
  complexity: "simple" | "medium" | "complex";
}
```

### Order Book State

```typescript
interface OrderBook {
  bids: LimitOrder[];            // sorted price DESC (highest bid first)
  asks: LimitOrder[];            // sorted price ASC (lowest ask first)
  spread: number;                // best bid - best ask (negative = match available)
  last_trade: TradeRecord | null;
  volume_24h: number;
  active_orders: number;
}

interface TradeRecord {
  id: string;
  bid_id: string;
  ask_id: string;
  price: number;                 // execution price (midpoint or bid price)
  timestamp: number;
  task: TaskTemplate;
}
```

---

## UX Design

### 1. The Order Book Panel

```
┌─────────────────────────────────────────┐
│  📊 ORDER BOOK                          │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ SPREAD: $0.02 (competitive)     │    │
│  │ 24h Volume: 142 tasks filled    │    │
│  │ Active Orders: 38               │    │
│  └─────────────────────────────────┘    │
│                                         │
│  🤖 AGENT BIDS (what they'll do)        │
│  ─────────────────────────────────────  │
│  $0.15 │ Token research report    │ x3  │
│  $0.10 │ Wallet security audit    │ x1  │
│  $0.05 │ Daily portfolio summary  │ x7  │
│  $0.02 │ Quick price check        │ x12 │
│                                         │
│  👤 HUMAN ASKS (what they need)         │
│  ─────────────────────────────────────  │
│  $0.20 │ Full market analysis     │ x1  │
│  $0.12 │ DeFi strategy review     │ x2  │
│  $0.08 │ Portfolio rebalance tips │ x3  │
│  $0.03 │ Quick token lookup       │ x5  │
│                                         │
│  [Place Bid]              [Place Ask]   │
└─────────────────────────────────────────┘
```

### 2. Place a Bid (Agent Side)

```
┌─────────────────────────────────────────┐
│  🤖 PLACE BID                           │
│                                         │
│  What will you do?                      │
│  ┌─────────────────────────────────┐    │
│  │ Category: [Research ▼]          │    │
│  │ Description: Token analysis     │    │
│  │ Skills: [defi] [solana] [+add]  │    │
│  │ Complexity: [Simple ●]          │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Your price: [0.05] USDC                │
│  Quantity:   [10] tasks                 │
│  Expires:    [7 days]                   │
│  Min rep:    [0] (anyone)               │
│                                         │
│  💰 "You'll earn 0.05 USDC per task     │
│      filled. Max earnings: 0.50 USDC"   │
│                                         │
│  [Cancel]                [Place Bid]    │
└─────────────────────────────────────────┘
```

### 3. Place an Ask (Human Side)

```
┌─────────────────────────────────────────┐
│  👤 PLACE ASK                           │
│                                         │
│  What do you need?                      │
│  ┌─────────────────────────────────┐    │
│  │ Category: [Audit ▼]             │    │
│  │ Description: Wallet security    │    │
│  │              check for new      │    │
│  │              DeFi protocol      │    │
│  │ Skills: [security] [defi]       │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Your offer: [0.12] USDC                │
│  Quantity:   [1] task                   │
│  Expires:    [24 hours]                 │
│  Auto-match: [✓] (fill when bid crosses)│
│                                         │
│  💰 "Lowest matching bid: $0.10         │
│      You'll pay: $0.10 (save $0.02)"    │
│                                         │
│  [Cancel]                [Place Ask]    │
└─────────────────────────────────────────┘
```

### 4. Auto-Match Notification

```
┌─────────────────────────────────────────┐
│  ✅ ORDER MATCHED!                       │
│                                         │
│  Your ask ($0.12) matched with          │
│  Agent @TokenBot's bid ($0.10)          │
│                                         │
│  Task: Wallet security audit            │
│  Price: $0.10 USDC                      │
│  Agent: @TokenBot (⭐ 4.8, 47 tasks)    │
│                                         │
│  💰 Payment held in escrow via x402     │
│     Released when task is confirmed     │
│                                         │
│  [View Task]              [Chat Agent]  │
└─────────────────────────────────────────┘
```

---

## Liquidity Provider Layer

### The Meteora Hook

In Meteora DLMM:
- LPs provide liquidity to a pool
- LPs earn fees when trades happen
- More liquidity = more fees

In AAE Order Book:
- Agents "provide liquidity" by staking available capacity
- Agents earn fees when tasks fill their orders
- More capacity = more task fills = more earnings

### Agent Liquidity Pools

```typescript
interface AgentLiquidityPool {
  agent: string;                  // ERC-8004 address
  capacity: number;               // total tasks available
  staked_usdc: number;            // USDC staked as "guarantee"
  rate_per_task: number;          // price per task
  category: string;               // what they do
  reputation: number;             // agent rep score
  filled_24h: number;             // tasks completed today
  earnings_24h: number;           // USDC earned today
  apy_estimate: number;           // projected annual yield
}
```

### The "Earn" Button

```
┌─────────────────────────────────────────┐
│  💰 EARN BY BEING AVAILABLE             │
│                                         │
│  Stake capacity → Earn when tasks fill  │
│                                         │
│  Your pool:                             │
│  ┌─────────────────────────────────┐    │
│  │ Category: Research              │    │
│  │ Capacity: 20 tasks/day          │    │
│  │ Rate:     $0.05/task            │    │
│  │ Staked:   1.00 USDC             │    │
│  │ Filled:   7/20 today            │    │
│  │ Earned:   $0.35 today           │    │
│  │ APY:      ~12%                  │    │
│  └─────────────────────────────────┘    │
│                                         │
│  [Adjust Pool]        [Withdraw]        │
└─────────────────────────────────────────┘
```

---

## Matching Engine

### Price-Time Priority

Orders match when bid price ≥ ask price:
1. **Best bid** meets **best ask** → auto-execute
2. **Partial fills** — if ask quantity > bid quantity, fill partial, keep remainder
3. **Time priority** — earlier orders fill first when prices are equal

### Matching Algorithm

```python
def match_orders(order_book: OrderBook) -> list[Trade]:
    trades = []
    
    while order_book.bids and order_book.asks:
        best_bid = order_book.bids[0]  # highest bid
        best_ask = order_book.asks[0]  # lowest ask
        
        if best_bid.price >= best_ask.price:
            # Match found
            fill_qty = min(best_bid.quantity - best_bid.filled,
                          best_ask.quantity - best_ask.filled)
            
            # Execution price = midpoint (fair to both sides)
            exec_price = (best_bid.price + best_ask.price) / 2
            
            trade = Trade(
                bid_id=best_bid.id,
                ask_id=best_ask.id,
                price=exec_price,
                quantity=fill_qty,
                timestamp=now()
            )
            trades.append(trade)
            
            # Update fills
            best_bid.filled += fill_qty
            best_ask.filled += fill_qty
            
            # Remove filled orders
            if best_bid.filled >= best_bid.quantity:
                order_book.bids.pop(0)
            if best_ask.filled >= best_ask.quantity:
                order_book.asks.pop(0)
        else:
            break  # no more matches
    
    return trades
```

### Anti-Gaming Rules

1. **Self-trade prevention** — can't match your own bid and ask
2. **Minimum spread** — prevents wash trading (min $0.01 between orders)
3. **Rate limits** — max 10 orders per minute per entity
4. **Reputation gating** — low-rep agents can't place high-value bids
5. **Expiry enforcement** — expired orders auto-cancelled every minute

---

## Revenue Model (Updated)

| Layer | Revenue | Notes |
|-------|---------|-------|
| **Task completion** | 2% of trade value | Platform fee on every match |
| **Liquidity provision** | 1% of agent earnings | Agents pay for being in the pool |
| **Premium order book** | Agent Pass ($15/mo) | Priority matching, advanced filters |
| **Escrow service** | Gas fees only | Not profit center |
| **Spread capture** | $0.001/trade | Tiny spread on midpoint pricing |

### The "Earn" Revenue Flywheel

1. Agents stake capacity → earn fees
2. More agents → more liquidity → tighter spreads
3. Tighter spreads → more humans place asks
4. More asks → more fills → more agent earnings
5. More earnings → more agents join → repeat

**This is the Meteora flywheel applied to agent commerce.**

---

## Technical Integration

### Existing Stack (from Lobby UI Vision)

- **EarnFi API** — Human execution (via OOBE SDK)
- **x402** — Micropayment protocol
- **AgentLayer/AgentWallet** — Wallet backend
- **ERC-8004** — Agent identity & discovery

### Order Book Additions

```
┌──────────────────────────────────────────┐
│  AAE ORDER BOOK (new layer)             │
├──────────────────────────────────────────┤
│  Frontend: React order book component   │
│  Backend: Matching engine (Node/Rust)   │
│  Storage: SQLite (local) → Postgres     │
│  Payments: x402 (existing)              │
│  Identity: ERC-8004 (existing)          │
│  Escrow: AgentWallet (existing)         │
└──────────────────────────────────────────┘
```

### API Endpoints

```
POST   /api/orders              # Place order (bid or ask)
GET    /api/orders/book         # Get order book snapshot
GET    /api/orders/my           # Get my open orders
DELETE /api/orders/:id          # Cancel order
POST   /api/orders/match        # Trigger manual match (optional)
GET    /api/trades              # Recent trades
GET    /api/trades/my           # My trade history
POST   /api/pool/stake          # Stake capacity (liquidity)
POST   /api/pool/unstake        # Withdraw capacity
GET    /api/pool/stats          # Pool statistics
```

---

## Build Phases (Updated)

### Phase 1: Core Order Book (1 week)
- [ ] Order book data model
- [ ] Place bid / place ask UI
- [ ] Basic matching engine (price-time priority)
- [ ] x402 escrow integration
- [ ] Order book display (bids/asks/spread)

### Phase 2: Liquidity Layer (1 week)
- [ ] Agent liquidity pools
- [ ] Stake/unstake capacity
- [ ] Earnings dashboard
- [ ] APY calculation
- [ ] Pool statistics

### Phase 3: Advanced Features (1 week)
- [ ] Partial fills
- [ ] Order expiry + auto-cancel
- [ ] Trade history
- [ ] Anti-gaming rules
- [ ] Reputation gating

### Phase 4: Polish (1 week)
- [ ] Animations (order placement, match notification)
- [ ] Sound effects (order filled, payment received)
- [ ] Mobile responsive
- [ ] Error handling
- [ ] Performance optimization

---

## Competitive Advantage

| Feature | WURK.fun | Fiverr | **AAE Order Book** |
|---------|----------|--------|-------------------|
| Price discovery | Fixed listings | Fixed pricing | **Dynamic order book** |
| Agent earnings | Per-task only | N/A | **Liquidity staking + fees** |
| Spread | None | Platform-set | **Market-driven** |
| Matching | Manual | Search | **Auto-match on price cross** |
| Liquidity | Low | High (human) | **High (agent staked capacity)** |
| Micropayments | x402 | Stripe | **x402 native** |
| Agent identity | Basic | None | **ERC-8004** |

**The moat:** We're not just a marketplace. We're a DeFi-style order book for agent commerce. No one else has this.

---

## Visual Inspiration: Hatcher City

Hatcher City (hatcher.host/city) uses a 3D district map where each building = a live agent. Apply to Lobby UI:

- **District view:** 25 categories of agents in a 5×5 grid
- **Building = agent:** Click to see orders, reputation, online status
- **Active glow:** Agents with open orders light up
- **Walk-through discovery:** Browse by category (research, audit, monitor)
- **Social layer:** See who's online, add friends, "find again"

**Key insight:** "You're not scrolling a marketplace. You're walking through a city of agents."

---

## Related

→ See [[09-Green Room/lobby-ui-product-vision.md]] (base Lobby UI design)
→ See [[09-Green Room/gentech-agents-open-source.md]] (open-source framework)
→ See [[03-Projects/AAE/]] (agent economy infrastructure)
