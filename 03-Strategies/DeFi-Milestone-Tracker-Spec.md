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
- Range: $9.00 – $9.30 | Shape: Curve
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

## 6. Open Questions / Next Iterations
- [ ] **Rebalance alerts** — notify when price drifts toward range edges (e.g., AVAX < $9.36 or > $9.48)
- [ ] **Yield APY time-series** — log daily to vault, build trend charts
- [ ] **CSV / JSON export** — for users who want spreadsheet analysis
- [ ] **Vault integration** — write daily snapshot to `08-Daily/` so the front-end can read history
- [ ] **Web dashboard mock** — coordinate with DMOB/Gentech on React component structure

---

## 7. Ownership
- **YoYo**: data pipeline, alert logic, LP math, token selection
- **DMOB / Gentech**: smart-contract integrations, front-end scaffold, wallet connect
- **Desmond**: community-facing explainers, changelog, docs
