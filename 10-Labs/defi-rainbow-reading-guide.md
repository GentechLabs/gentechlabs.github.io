# The DeFi Rainbow — Reading Guide (Jordan, Aug 22 2026)

**Why two rainbows?** "The DeFi yield rainbow is different for yield farming than for
trading." One measures **LP efficiency (are my bins earning?)**, the other measures
**price value (is this coin cheap or expensive?)**. Different questions, different colors,
different actions. Don't mix them.

---

## 🌈 RAINBOW #1 — Coin Price Rainbow (Trading / Buying)

**Script:** `coin-rainbow.py` → `coin-rainbow-data.json`
**Question:** Is this coin cheap or expensive *relative to its own recent range*?
**Input:** 7-day + 30-day momentum → blended **-2 to +2 score**
```
score = 0.6 × (7d change / 10) + 0.4 × (30d change / 10),  clamped to -2…+2
```
**Contrarian meter:** high = overheated (trim), low = cheap (accumulate).

| Band | Emoji | Score | Meaning | Action |
|------|-------|-------|---------|--------|
| Euphoria | 🔴 | +1.5…+2 | Far above range, overheated | Take profits |
| Peak Yield | 🟠 | +0.8…+1.5 | Upper zone, rich | Trim into strength |
| Harvest | 🟡 | +0.3…+0.8 | Mid-upper, healthy | Hold / compound |
| Accumulation | 🟢 | −0.3…+0.3 | Fair value | DCA in |
| Bleeding | 🔵 | −0.8…−0.3 | Cheap | Micro-DCA / prep |
| Panic | 🟣 | −2…−0.8 | Generational low | Be greedy when others fear |

**Reading the cron (Aug 22):** AVAX = 🟠 Peak Yield, LINK = 🔴 Euphoria, SOL = 🔴 Euphoria
(score +2.x). All rich → **don't chase, trim or wait**. A coin at 🟢/🔵/🟣 = buy zone.

---

## 🌈 RAINBOW #2 — DeFi Yield Rainbow (LP Farming / Rebalancing)

**Where:** the LP monitor / defi skill (not the coin script). Also called the yield-efficiency
rainbow. **Question:** Are my LP bins in range and earning fees *right now*?
**Input:** position efficiency + in/out-of-range vs live price, by **shape** (curve / bid-ask / spot).
**The regime drives it** — "as the regime changes for the different chains."

**Efficiency by shape (bin-weighted):**
| Shape | Center | Near edge | Edge | Out of range |
|-------|--------|-----------|------|--------------|
| Curve | 100% | 75–90% | 60% | 0% |
| Bid-Ask | 50% | 75–90% | 100% | 0% (⚠️ 0% real fees between edges) |
| Spot | — | — | 100% | 0% |

**⚠️ The big trap:** a bid-ask position can show "high efficiency" on paper while earning
**$0** because price sits between the bid and ask edges (no bins crossed). Efficiency =
bin density, NOT actual fee earnings. Always ask: is price at an edge?

**Regime → shape (from defi skill):**
| Regime | Shape |
|--------|-------|
| Chop / no direction | CURVE (all bins earn as price oscillates) |
| Macro event (FOMC/CPI/NFP) | BID-ASK (one edge catches the move) |
| Range-bound | Curve, tight range |
| High volatility | Bid-Ask, wide range |
| Bull confirmed | 25% LP + 75% spot |

**Switch timing:** CURVE → BID-ASK ~24h before Fed/CPI/NFP; back to CURVE ~24h after.

---

## 📊 Quick distinction table

| | Coin Price Rainbow | DeFi Yield Rainbow |
|---|---|---|
| **What it measures** | Is price cheap/expensive? | Are my LP bins earning? |
| **Used for** | Trading / buying | LP farming / rebalancing |
| **Input** | 7d/30d price momentum | Efficiency + in-range vs price, by shape |
| **Colors** | 🔴🟠🟡🟢🔵🟣 (price bands) | Range status + efficiency |
| **Driven by** | Coin momentum | **Market regime** |
| **Action** | Buy dips / trim strength | Rebalance shape by regime |

**Jordan's rule:** keep both in mind as the **regime changes per chain** — a coin's price
rainbow (buy/sell) and the yield rainbow (LP shape) respond to different signals and can
point different directions. Read the right one for the job.

*Not financial advice. Value-zone visualization only.*
