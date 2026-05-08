# Portfolio Allocation Template

**File:** `03-Projects/Portfolios/Active/{YYYY}-{Strategy-Name}.md`

---

## Portfolio Profile

**Name:** [e.g., "Gentech Multi-Chain Core"]  
**Start Date:** YYYY-MM-DD  
**Time Horizon:** 2–3 years  
**Objective:** Compounding through cycles (not short-term yield chasing)  
**Total Capital Deployed (target):** $X,XXX

---

## Bucket Allocation

| Bucket | Target % | Current % | Budget (monthly) | Notes |
|--------|----------|-----------|------------------|-------|
| Core DeFi | 50% | 0% | $XXX | AVAX/USDC LP, SOL/USDC LP |
| RWA / Thesis | 30% | 0% | $XXX | PROPS, LAND, TAO |
| Cycle Plays | 20% | 0% | $XXX | BONK, JUP, new L1 rotations |

**Actual deployment proceeds bucket by bucket, not all-at-once.**

---

## Asset Inventory

### Core DeFi Positions
| Token | Chain | Strategy | Amount | Entry | Range | Status |
|-------|-------|----------|--------|-------|-------|--------|
| AVAX | Avalanche | LFJ LP (bid-ask) | 3.88 AVAX + 46.82 USDC | $9.418 | $9.00–$9.30 | ✅ Active |
| SOL | Solana | Raydium CLMM | TBD | TBD | TBD | ⬜ Planned |

### RWA / Thesis Holdings
| Token | Chain | Strategy | DCA Monthly | Position Target | Status |
|-------|-------|----------|-------------|-----------------|--------|
| PROPS | Ethereum | Spot hold | $100–200 | 50,000 PROPS | ⬜ Buying |
| LAND | BSC | Spot hold | $50–100 | 2,000 LAND | ⬜ Buying |
| TAO | Bittensor | Spot hold | $100 | 0.387 TAO | ⬜ Watching |

### Cycle Play Allocations
| Token | Pool | Platform | Weekly DCA | Max Position | Status |
|-------|------|----------|------------|--------------|--------|
| BONK | BONK/USDC | Raydium | $50 | $500 | ⬜ Q3 entry |
| JUP | JUP/USDC | Orca | $50 | $500 | ⬜ Q3 entry |

---

## DCA Schedule

### Weekly Micro-DCA (Automated where possible)
- **Monday:** Core DeFi top-up (if price in range)
- **Thursday:** Cycle Play entry (based on volatility filter)
- **Amount:** $50–100 per bucket (max $300/week)

### Monthly Macro-DCA (Discretionary)
- **Date:** 15th of month
- **RWA bucket:** $200–400 based on news/research
- **Adjust:** If any token ±20% from last buy, skip this month (buy the dip logic)

### Opportunistic Buys
Conditions:
- >5% drop in 24h → buy 1.5× normal weekly amount
- Consolidation after -15% weekly drop → buy 2× normal weekly amount
- Parabolic >30% weekly rise → **do not buy** (wait for pullback)

---

## Monitoring Cadence

| Bucket | Price Watch | Volume Review | Position Health | Monitor Tool |
|--------|-------------|---------------|-----------------|--------------|
| Core | 4× daily (cron) | Daily | 10-min LP in-range | `defi-lp-monitor` |
| RWA | Hourly (1.5% alert) | Daily | Weekly IL review | Manual vault check |
| Cycle | Real-time alerts | Real-time | Daily fee claim | Custom script |

---

## Rebalance Rules

**Core DeFi:**
- Price exits range → rebalance within 24h
- IL hits 2% → review position size
- Efficiency < 50% for 3 consecutive days → widen range

**RWA:**
- Any token +20% → take 10% profit into Core
- Any token -30% from entry → double DCA for 2 months (if conviction intact)
- Quarterly review: exit if narrative broken (e.g., real estate tokenization regulation hostile)

**Cycle:**
- Exit on +50% (take profit) OR -40% (stop-loss)
- Never let cycle position exceed 20% of portfolio
- Rotate into new ecosystem narratives every 3–6 months

---

## Exit Criteria (Time-based)

- **Minimum hold:** 2 years (unless exit signal triggered earlier)
- **Target review dates:** YYYY-MM-DD, YYYY-MM-DD, YYYY-MM-DD (quarterly reviews)
- **Full portfolio review:** Every 6 months — reassess allocation percentages

---

## Vault & Reporting

**Primary vault:** `03-Projects/Portfolios/Active/{YYYY}-{Strategy-Name}.md`  
**Sync:** `ob sync` after every material change

**Telegram group:** `GenTech Strategies` (for weekly summaries)  
**Individual alerts:** Sent to `-1002916759037` (YoYo) for LP health, gentech for portfolio review

---

## Notes

[Free-form field for session-specific observations, decisions, deviations from plan]
