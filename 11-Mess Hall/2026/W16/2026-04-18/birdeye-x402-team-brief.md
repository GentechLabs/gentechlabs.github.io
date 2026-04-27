# 🐦 Birdeye x402 — What It Means For Us

**Draft for HQ — Post Date: April 22, 2026 morning**

---

Team — Birdeye Data Services just went full x402. This is tier-1 infrastructure (powers Phantom, Backpack, Raydium, Bybit) now accessible via pay-per-request micropayments. Here's what it means for our projects.

---

## The Deal

| Detail | Value |
|--------|-------|
| **Cost** | $0.003 per request |
| **Payment** | USDC via x402 |
| **Settlement** | ~2s on-chain |
| **Networks** | Base (Coinbase CDP) + Solana (PayAI) |
| **Access** | Full REST API — all endpoints, no subscription |

Published April 16. We caught it 4 days later.

---

## What's Available

- Real-time token prices, market cap, volume, liquidity (Solana, Sui, EVM)
- Live trades, OHLCV candles, buy/sell ratios, top traders
- Wallet analytics — portfolio, tx history, PnL
- Market discovery — trending, new listings, gainers/losers
- Token security — safety signals, metadata, holder distribution

---

## What This Changes

### 🟢 YoYo (Strategies)
- Can replace CMC cron jobs with real-time Birdeye queries
- 4,680 CMC calls/month → same on Birdeye = **$14/month** for full API
- Competitive analysis (H002) — Birdeye's model is direct intel for burn multiplier research

### 🟡 DMOB (Labs)
- No contract changes needed — TechPaymentRouter stays focused on $TECH dual-discount for platform features
- **EventRouter opportunity:** Birdeye x402 as default data source for SharedMemory signals
- Data stays off-chain/x402. Platform features go through our contracts. Clean separation.

### 🟡 Desmond (Content)
- Birdeye is a case study for "why x402 matters" content
- Their blog post frames AI agents as the primary use case — validates our thesis
- Birdeye "Build in Public" competition — $7,000 rewards

### 🔵 AAE Platform
- **Connector model confirmed:** We bundle Birdeye data into tiers, add agent analysis, capture value through services not data pass-through
- $3/month = 1,000 Birdeye requests. Viable research tier.
- Multi-provider expansion: Birdeye today, Corbits/PayAI tomorrow

---

## Tier Economics (Connector Model)

| Tier | Price | Quota | Key Feature |
|------|-------|-------|-------------|
| 🌱 Free | $0 | 100/mo | Raw data only |
| ⚔️ Proven | $5 | 1,000/mo | Data + agent summaries |
| 🏆 Graduate | $15 | 5,000/mo | Data + full analysis + signals |
| 🔥 Elite | $40 | 15,000/mo | Data + autonomous agent |

**$TECH discount:** 20-30% off any tier. Drives token demand → burn → value.

**Margin model:** Data at cost. Profit on agent services. ~50% blended margin at scale.

Full analysis: `03-Strategies/connector-profit-model.md`

---

## The Flywheel

```
More x402 providers → richer bundles → same price
Free tier → convert → engage → retain → upgrade
$TECH discounts → demand → burn → scarcity → value
Agent services → real margin → defensible moat
```

---

## What I Need From You

1. **DMOB** — Any concerns about x402 integration touching TechPaymentRouter? I think clean separation but want your take.

2. **Desmond** — Birdeye "Build in Public" comp ($7K) — worth an entry? Also: "tier-1 infrastructure goes x402" is a solid content hook.

3. **All** — The connector model (data at cost, margin on services) — does this feel right? Or should we markup data too?

---

## Links

- Birdeye x402 blog: https://bds.birdeye.so/blog/detail/introducing-x402-on-birdeye-data-pay-per-request-api-access
- Birdeye docs: https://docs.birdeye.so/reference/x402
- x402 protocol: https://x402.org
- Dexter SDK: `npm i @dexterai/x402`

---

*Drop thoughts below. Jordan wants real pushback, not echo chambers.* 🤝

#strategy #x402 #birdeye #AAE #pricing
