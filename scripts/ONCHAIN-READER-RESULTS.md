# On-Chain Position Reader — Test Results
## Date: 2026-06-16

### Wallet: 0x7ebff188f2Eba16518C02864589b1403a5d1296a

## ✅ Working (Free, No API Keys)
| Feature | Source | Status |
|---------|--------|--------|
| Native AVAX balance | Avalanche RPC | ✅ 0.097629 AVAX |
| WAVAX balance | ERC-20 RPC call | ✅ 0.000001 |
| USDC balance | ERC-20 RPC call | ✅ 0.000009 |
| AVAX/USDC price | DexScreener API | ✅ $6.95 |
| Pool reserves | `getReserves()` RPC | ✅ 35,338 WAVAX / 134,259 USDC |
| 24h volume/change | DexScreener API | ✅ Full data |
| Deposit event history | Snowtrace logs API | ✅ 200+ events decoded |
| Withdrawal event history | Snowtrace logs API | ✅ Query works |

## ⚠️ Partially Working
| Feature | Issue | Fix Needed |
|---------|-------|------------|
| LP bin balances | `balanceOf(addr, binId)` reverts on proxy contract | Need LFJ SDK or correct V2.1/V2.2 selector |
| Position value calculation | Can't read individual bin liquidity | Use event-based reconstruction |

## Key Findings
1. **Position is active** — 100+ DepositedToBins events, most recent June 15 2026
2. **Liquidity lives in the pool** — not in wallet (standard for LP positions)
3. **Managed via Router + Vault** — 0x18556da (LFJ Router) + 0x45a62b (auto-compounder/strategy)
4. **All liquidity is USDC-side** — deposits show X=0 (no WAVAX), Y>0 (USDC amounts)
5. **Bin range**: 8363244-8363294 (50 bins in latest deposit)
6. **Proxy pattern**: Pool is EIP-1167 minimal proxy → implementation at 0x7a5b...

## Architecture (Agent Kit Template)
```
Layer 1: Chain-Agnostic (works for ALL chains)
  └── RPC balance queries (native + ERC-20)
  └── DexScreener/Pyth price feeds
  
Layer 2: DEX-Specific Adapters
  └── LFJ: Event-based position tracking (DepositedToBins/WithdrawnFromBins)
  └── Uniswap V3: NonfungiblePositionManager.positions(tokenId)
  └── Pangolin: Similar to LFJ (fork)
  
Layer 3: Unified Output
  └── defi-data.json format (compatible with all dashboards)
```
