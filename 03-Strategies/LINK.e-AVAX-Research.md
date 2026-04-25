# LINK.e (Avalanche) — Acquisition & Yield Assessment

**Date:** 2026-04-24  
**Analyst:** YoYo (Strategies)  
**Status:** Complete

---

## 1. What is LINK.e?

LINK.e is Chainlink bridged to Avalanche via the **legacy Avalanche-Ethereum Bridge (AEB)**.
- **Contract:** `0x5947BB275c521040051D82396192181b413227A3` (Avalanche C-Chain)
- **Symbol:** LINK.e (the `.e` suffix = Ethereum-bridged)
- **Price:** ~$9.34–$9.38 (tracks native LINK at ~$9.37–$9.40 closely)

---

## 2. Acquisition — Where to Buy on AVAX

| DEX | Pair | Liquidity | Vol 24h | Note |
|-----|------|-----------|---------|------|
| **Uniswap V3** | LINK.e / WAVAX | **$112,848** | $247 | Best depth |
| **Trader Joe** | LINK.e / WAVAX | $49,968 | $490 | Highest vol |
| **Pangolin** | LINK.e / WAVAX | $33,862 | $337 | Legacy DEX |
| **Blackhole** | LINK.e / USDC | $6,928 | $3,515 | Thin |
| **Lydia Finance** | LINK.e / WAVAX | $6,533 | $100 | Minimal |

**Total DEX liquidity: ~$210K**

### ⚠️ Liquidity Risk
- Anything above **$1,000–$2,000** in a single trade will move the price meaningfully.
- For a material position, you’ll need to **route through WAVAX** or split across DEXs.
- Slippage on $5K+ orders could exceed 2–4% easily.

---

## 3. Yield Opportunities

### Lending / Single-Sided

| Protocol | Asset | Supply APY | TVL | Status |
|----------|-------|------------|-----|--------|
| **Aave V3** | LINK.E | — | $1.04M | **DISABLED** ❌ |
| **Benqi** | LINK.E | **0.02%** | $729K | Active but negligible |
| **Joe Lend** | LINK.E | **0.00%** | $72K | Dead |

**Aave V3 has ChainLink marked as "Disabled"** — no new deposits or borrows allowed. Existing TVL ($1M) is legacy capital sitting idle.

### LP / Concentrated Liquidity

| Protocol | Pair | APY | TVL |
|----------|------|-----|-----|
| **Uniswap V3** | LINK.e / WAVAX | **0.41%** | $221K |
| **Pangolin V2** | LINK.e / WAVAX | **1.08%** | $34K |

- No reward incentives (AVAX grants, JOE rewards, etc.) on LINK.e pools.
- LP yield is purely fee-based and extremely low.
- **IL exposure:** LINK.e/WAVAX = volatile pair. At 0.41% APY, a 5% divergence wipes out months of fees.

### Vaults / Aggregators
- **Beefy Finance:** No LINK.e vaults on Avalanche.
- **Yield Yak:** No LINK.e strategies.
- **No auto-compounding farms exist.**

---

## 4. Risk Assessment

| Risk | Severity | Detail |
|------|----------|--------|
| **Liquidity Risk** | 🔴 High | $210K total DEX liquidity. Exit slippage is real. |
| **Bridge Risk** | 🟡 Medium | Legacy AEB bridge. Not the new Circle CCTP or LayerZero standard. Bridge hacks are a known vector. |
| **Smart Contract Risk** | 🟡 Medium | Benqi, Trader Joe, Pangolin = established but lower TVL = less battle-tested at scale. |
| **IL Risk** | 🟡 Medium | LINK.e/WAVAX LP = high correlation breakdown risk for near-zero yield. |
| **Opportunity Cost** | 🔴 High | 0.02% lending APY vs. 4–6% on USDC in Aave = capital is better deployed elsewhere. |

---

## 5. Recommendation

### ❌ Do NOT acquire LINK.e on Avalanche for yield.
The risk/reward is unfavorable:
- Near-zero yields across all protocols
- Disabled on Aave (the only protocol Jordan already uses)
- Very thin liquidity makes entry/exit expensive
- No vaults, no farms, no incentives

### ✅ Better Path: Native LINK on Ethereum or Arbitrum/Base
If Jordan wants LINK exposure:
- **Ethereum:** $24M+ Uniswap V3 liquidity. Tight spreads.
- **Arbitrum:** $273K+ liquidity, lower gas.
- **Base:** $180K+ Aerodrome liquidity, very low gas.

### 🟡 If Jordan MUST stay on AVAX
- **Max position size:** $1,000–$2,000 (slippage tolerance)
- **Acquisition route:** Trader Joe LINK.e/WAVAX (best volume) → swap WAVAX → LINK.e
- **No yield play.** Just hold spot. Bridge back to ETH if position grows.

---

## 6. Context Notes

- Chainlink data standard went live on AWS Marketplace (Apr 24) — this is a fundamental catalyst for LINK long-term, but does not change the Avalanche liquidity picture.
- Jordan’s current AVAX plays (LFJ AVAX/USDC LP, Aave loops) are far more capital-efficient than anything available for LINK.e.

---

*#link.e #chainlink #avax #yield #research #strategies*