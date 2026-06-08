# 💧 AAE DeFi Milestone + LP Tracker — Product Spec

**Status:** Production (active cron)  
**Owner:** YoYo (Strategies)  
**Deliverable:** Telegram group + eventual front-end integration  
**Last Updated:** 2026-04-25

---

## 1. What It Does
An automated, scheduled pipeline that:
- Monitors live LP positions (AVAX/USDC on LFJ v2.2 via DexScreener)
- Tracks position health: in-range status, impermanent loss, yield, efficiency
- Surfaces a curated crypto watchlist (BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM)
- Delivers formatted alerts to **GenTech Strategies** Telegram group

---

## 2. Current Cron Jobs

| Job | Schedule | Scope | Skill |
|-----|----------|-------|-------|
| **AAE DeFi Milestone + LP Monitor** | Daily @ 10:00 AM ET | LP position deep-dive (IL, APR, TVL, fees) | `crypto-lp-monitoring` |
| **Crypto Watchlist (DexScreener)** | 4x/day @ 8:15, 12:15, 4:15, 8:15 PM ET | Price, volume, 24h change for 7 tokens | — |

**Model:** `kimi-k2.6` via Ollama Cloud  
**Delivery:** `telegram:-1002916759037`

---

## 3. Current Output Format

### LP Monitor Alert
```
💧 AAE LP Monitor — [timestamp]
📊 DexScreener · AVAX/USDC 5bps · LFJ v2.2

📍 Position Status
- AVAX Price: $9.3500 | 24h: -0.8%
- Range: $9.00 – $9.45 | Shape: Curve
- In Range: ✅ Yes | Efficiency: 21%
- Entry: $9.45 | IL: -0.00%

💰 Yield & P&L
- Est. Daily Fees: $0.17 | APR: ~76%
- Cumulative Fees: $0.02
- LP Value (est): ~$83.94 | vs HODL: $+0.39
- Pool Vol 24h: $16,613,778 | TVL: [live]
```

### Watchlist Alert
```
⏰ Crypto Watchlist Alert — [timestamp]
📊 DexScreener

BTC  — $93,842  (+0.7%)  | Vol: $28.0B
SOL  — $150.21  (+2.1%)  | Vol: $4.2B
...
```

---

## 4. Front-End & Scaling Considerations

As we add more chains, pools, and tokens, every new layer must consider **how it renders on the eventual front-end / community dashboard**.

### Data Layers to Plan For
| Layer | What Changes | Front-End Impact |
|-------|-------------|------------------|
| **Multi-chain** | AVAX → add Base, Solana, Arbitrum | Chain badges, selector, RPC failover |
| **Multi-pool** | LFJ → add Uniswap, Raydium, Camelot | Pool cards, DEX logos, fee-tier labels |
| **Multi-position** | 1 wallet → many positions | Portfolio view, aggregate P&L, sorting |
| **Multi-wallet** | 1 user → many wallets (EOA + smart) | Wallet switcher, unified dashboard |
| **Yield history** | Snapshots → time-series | Charts (Recharts/Chart.js), CSV export |
| **Alert rules** | Static cron → user-configurable thresholds | Rule builder, push notification prefs |

### UX Patterns We Should Adopt Now
1. **Structured data in every alert** — machine-parseable so the front-end can ingest cron output directly.
2. **Standardized emoji/icon legend** — makes Telegram → web mapping trivial.
3. **Pool identifiers** — always include `chain:DEX:poolAddress` so links resolve unambiguously.
4. **Cumulative vs. snapshot** — distinguish "right now" from "since entry" — both have value.

---

## 5. API & Data Sources
- **DexScreener** (free, no key): pair data, price, volume, TVL
- **LFJ / Trader Joe** (on-chain): position NFT data, fee accumulation
- **CoinMarketCap** (`ff52c5f0...a6d55`): macro cap rankings, metadata

---

## 6. Hybrid Bull Market Strategy (Phase 2)

**Added:** 2026-04-29
**Status:** Design — pending indicator implementation

### Concept
During range-bound or correction markets, LP earns fees via market making. During confirmed bull markets, pull majority of liquidity to spot AVAX to capture upside. Re-LP at key resistance levels where price consolidates.

### Three Phases

| Phase | Market Condition | Action | LP Allocation |
|-------|-----------------|--------|---------------|
| **1 — Market Make** | Range-bound / correction | LP earns fees, accumulate | 100% in pool |
| **2 — Ride the Pump** | Bull breakout confirmed | Pull to spot, hold AVAX | 25% in pool (earn on volume) |
| **3 — Resistance LP** | Price at resistance ($15, $20, $30...) | Re-LP with bid-ask at level | 75% re-LP at resistance |

### Exit Indicator (Phase 1 → Phase 2 Trigger)

**Recommend exiting the pool when ALL of these conditions are met:**

1. **BTC reclaims $130K** on daily close (macro risk-on signal)
2. **AVAX breaks $10 with volume** — not a wick, confirmed daily close above $10
3. **50-day MA trending up** — AVAX 50-day SMA slope turns positive
4. **Fear & Greed > 60** — market sentiment shifts from fear to greed

**When triggered:**
- Withdraw 75% of LP position as spot AVAX
- Keep 25% in LP to earn fees on bull volume
- Set price alerts at resistance levels below

### Resistance Levels for Re-LP (Phase 3)

| Level | Significance | Bid-Ask Range |
|-------|-------------|---------------|
| $12 | Previous support → resistance | $11.50–$12.50 |
| $15 | Psychological + technical | $14.50–$15.50 |
| $20 | Major round number | $19.50–$20.50 |
| $30 | Cycle resistance | $29.00–$31.00 |
| $40 | Extension target | $39.00–$41.00 |
| $60 | Euphoria zone | $58.00–$62.00 |

**At each resistance:**
- Re-LP with bid-ask shape around the level
- Earn fees as price consolidates/bounces
- If it breaks through → pull out again, ride to next level
- If it rejects → you sold some at resistance, keep the rest in LP

### Exit from Bull (Phase 2 → Phase 1 Reset)

**Return to full LP when:**
- BTC loses $110K on daily close (or AVAX loses $8)
- 50-day MA slope turns negative
- Fear & Greed drops below 40

### D5 Milestone Integration

This strategy accelerates D5 progression:
- **Phase 1** (LP): Slow, steady fee accumulation — Tier 1-3 territory
- **Phase 2** (Spot + LP): Bull market = high volume = faster fees in remaining 25% LP
- **Phase 3** (Resistance LP): Concentrated liquidity at key levels = high APR spikes

The exit indicator should be surfaced in AAE alerts as a **STRATEGY signal** (new signal type, severity: ADVISORY).

---

## 7. Open Questions / Next Iterations
- [ ] **Rebalance alerts** — notify when price drifts toward range edges (e.g., AVAX < $9.36 or > $9.48)
- [ ] **Yield APY time-series** — log daily to vault, build trend charts
- [ ] **CSV / JSON export** — for users who want spreadsheet analysis
- [ ] **Vault integration** — write daily snapshot to `08-Daily/` so the front-end can read history
- [ ] **Web dashboard mock** — coordinate with DMOB/Gentech on React component structure
- [ ] **Bull market exit indicator** — implement Phase 1→2 trigger logic in AAE script
- [ ] **Resistance level LP automation** — bid-ask shape presets for each level
- [ ] **STRATEGY signal type** — new AAE alert for advisory recommendations

---

## 8. Ownership
- **YoYo**: data pipeline, alert logic, LP math, token selection
- **DMOB / Gentech**: smart-contract integrations, front-end scaffold, wallet connect
- **Desmond**: community-facing explainers, changelog, docs
