---
title: Example Protocol Evaluation — Velodrome (Base)
date: 2026-04-15
status: Reviewed
protocol_risk: 3
ticker: VELO
chain: Base
tvl_usd: 24500000
volume_24h_usd: 8900000
audited: Yes (OpenZeppelin, 2025-08)
team: Doxxed (ex-Crv crew)
monitoring: Active
---

## Executive Summary

Velodrome is Base's leading AMM with concentrated liquidity and ve(3,3)-style governance. Risk: **3/5 Moderate** — established track record on Optimism, migrated to Base in 2025, audited by OpenZeppelin. No red flags detected. Recommended for monitoring with ≤5% DeFi allocation.

## Metrics Snapshot (Apr 15, 2026)

| Metric | Value |
|--------|-------|
| TVL | $24.5M |
| 24h Volume | $8.9M |
| Vol/TVL Ratio | 0.36x |
| Staking APR | 12.8% |
| Fee APR (LP) | 18.4% (WETH/USDC 0.05%) |
| Token Price | $0.42 |
| Market Cap | $42M |
| FDV | $126M |

## Risk Analysis

✅ **Green Flags**:
- Team doxxed: @danieleselman, @marketmaker, public track record with Velodrome v1/v2 on Optimism
- Audited: OpenZeppelin report published 2025-08-12, no critical findings
- Governance: veVELO lockers control 68% of voting, smooth proposal execution history
- TVL Stability: +15% MoM, no sharp outflows
- Tokenomics: 4-year vesting for team (cliff passed Mar 2026)

⚠️ **Yellow Flags (Monitor)**:
- Centralization risk: Top 10 holders control 42% of supply (moderate concentration)
- Chain dependency: Base ecosystem volatility could affect TVL if activity drops
- Competition: Aerodrome (Base) and Uniswap v3 gaining market share

🚨 **Red Flags — None Found**

## Competitive Landscape

| Protocol | Chain | TVL | Risk | Notes |
|----------|-------|-----|------|-------|
| **Velodrome** | Base | $24.5M | 3 | Leading AMM on Base, ve(3,3) governance |
| Aerodrome | Base | $31.2M | 3 | Direct competitor, higher TVL but newer |
| Uniswap v3 | Multi | $2.1B | 2 | Incumbent, highest liquidity |
| PancakeSwap v3 | BSC | $480M | 2 | Established, different chain |

Velodrome differentiates via native ve(3,3) model on Base; governance token utility is mature.

## Monitoring Plan

Track weekly via D5 milestone cron:

1. **TVL Change** — >20% drop in 7 days → downgrade to 4/5
2. **Team Wallet** — monitor `0xTeamPrimary` for sells >100K VELO in 24h
3. **Audit Updates** — check OpenZeppelin blog for new findings
4. **Volume/TVL** — if ratio sustained <0.2x, liquidity health concern
5. **Governance Activity** — proposal count & turnout; <5% quorum suggests centralization

**Data sources**:
- DeFiLlama: `defillama.com/protocol/velodrome`
- Etherscan: `basescan.org/address/0x...VELO`
- Dune: `dune.com/velodrome/dashboards`

## Recommended Action

**MONITOR with capped allocation**:
- Initial test position: 2–3% of DeFi portfolio
- Entry condition: Wait for Base ecosystem TVL to stabilize above $1.5B (current: $1.2B)
- Exit triggers: Team wallet dump >5% supply, audit finding published, TVL/Volume < 0.2x for 30 days
- Review cadence: Bi-weekly or when any trigger fires

**Integration potential**: HIGH — AMM route for AAE LP deployment on Base if strategy expands beyond Avalanche. Requires whitelist approval via Council of Experts.

---

*Evaluation performed by YoYo, Gentech Strategies. Next review: 2026-05-15.*
