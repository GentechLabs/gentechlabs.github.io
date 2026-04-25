# LINK.e (AVAX) — Acquisition & Yield Assessment
*YoYo | April 24, 2026*

## 1. What is LINK.e?
- **Contract:** `0x5947BB275c521040051D82396192181b413227A3`
- **Bridge:** Avalanche-Ethereum Bridge (AEB) — legacy bridge, higher risk than modern alternatives (CCTP, LayerZero)
- **Price:** ~$9.35–9.38
- **Relationship to native LINK:** 1:1 backed, but bridge risk applies. Native LINK on Ethereum/Base has deeper liquidity.

## 2. Acquisition — Where to Buy
| DEX | Pair | Liquidity | Vol 24h | Note |
|-----|------|-----------|---------|------|
| Uniswap V3 | LINK.e/WAVAX | $112,848 | $247 | Best depth |
| Trader Joe | LINK.e/WAVAX | $49,968 | $490 | Second best |
| Pangolin | LINK.e/WAVAX | $33,862 | $337 | |
| **Total AVAX** | — | **$217,154** | **~$1,574** | Very thin |

**Assessment:** Total DEX liquidity under $220K. Slippage material above $1–2K position size. Large exits would be costly.

## 3. Yield Opportunities
### Lending
| Protocol | Asset | APY | TVL | Status |
|----------|-------|-----|-----|--------|
| Aave V3 | LINK.e | 0.01% | $1,044,145 | **❌ DISABLED** — no new deposits |
| Benqi | LINK.e | 0.02% | $729,531 | Active but negligible yield |
| Joe Lend | LINK.e | 0.00% | $72,252 | Active but zero yield |

### LP
| Protocol | Pair | APY | TVL |
|----------|------|-----|-----|
| Pangolin V2 | LINK.e/WAVAX | 1.08% | $34,089 |
| Uniswap V3 | LINK.e/WAVAX | 0.41% | $221,200* |

*Uniswap V3 TVL figure from DefiLlama; DexScreener shows $113K. Likely includes broader range positions.

### Vaults / Auto-compounding
| Protocol | Strategy | APY | TVL | Status |
|----------|----------|-----|-----|--------|
| Beefy | LINK.e single | 0.00% | $0 | EOL |
| Beefy | LINK.e-USDC.e LP | 0.00% | $0 | EOL |
| Beefy | LINK.e-AVAX LP | 0.00% | $0 | EOL |

No active auto-compounding vaults exist on Avalanche for LINK.e.

## 4. Risk Assessment
| Risk | Severity | Detail |
|------|----------|--------|
| **Liquidity Risk** | 🔴 High | $217K total liquidity. $5K order = ~2–3% slippage. Exit risk on size. |
| **Bridge Risk** | 🟡 Moderate | Legacy AEB bridge. Not the highest risk but not modern CCTP either. |
| **Smart Contract Risk** | 🟡 Moderate | Aave disabled = governance concern. Benqi/Joe still active but irrelevant yields. |
| **IL Risk** | 🟡 Moderate | LINK.e/WAVAX LP = exposed to both LINK and AVAX volatility. 1% APY doesn't cover IL. |
| **Opportunity Cost** | 🔴 High | AVAX/USDC LP on LFJ yields ~88% APR. Aave USDC yields 4–6%. LINK.e yields <0.05%. |
| **Reward Sustainability** | 🟡 Moderate | No reward tokens. Base yield only. |

## 5. Recommendation
**❌ Do NOT acquire LINK.e on Avalanche.**

**Rationale:**
1. Near-zero yields across all protocols (<0.05% lending, <1.1% LP)
2. Aave V3 — the deepest liquidity venue — is **disabled** for new deposits
3. Beefy vaults are all EOL
4. Liquidity is too thin for meaningful position sizing
5. Opportunity cost is severe: same capital in AVAX/USDC LP earns 80x+ more

**If Jordan wants LINK exposure:**
- **Best option:** Buy native LINK on **Base** or **Ethereum**. Deeper liquidity, active Aave markets, potential staking opportunities.
- **Bridge alternative:** If holding LINK.e already, bridge back to Ethereum via official Avalanche Bridge (bridge.avax.network) and deploy on Base/Ethereum.

## 6. Context Notes
- Chainlink Data Standard on AWS Marketplace is a bullish signal for LINK broadly, but this does not fix Avalanche-specific liquidity/yield issues.
- Jordan's current AVAX focus (LFJ LP, Aave loops) is well-optimized. LINK.e would be a drag on performance.
