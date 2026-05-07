# Real Estate Tokens Analysis — 2026-05-03

**Context:** User requested real estate token (PROPS, LAND) inclusion in multi-year portfolio alongside Solana yield farming.

## Token Data (live CMC API)

### PROPS (Propbase)
- **Price:** $0.00544
- **24h:** +7.70% | **7d:** +8.69%
- **Volume 24h:** $1.86M (CEX: $1.85M, DEX: $1.86K)
- **Market Cap:** $2.60M
- **TVL:** $1.09M (from tokenomics/staking, not LP)
- **Chains:**
  - Ethereum ERC-20: `0x6fe56c0bcdd471359019fcbc48863d6c3e9d4f41`
  - Aptos: `0xe50684a338db732d8fb8a3ac71c4b8633878bd0193bca5de2ebc852a83b35099::propbase_coin::PROPS`
- **Classification:** RWA / Thesis (property fractional ownership platform)
- **Liquidity note:** TVL ~$1M, but volume healthy ($1.86M/d) → decent spot liquidity; LP provision risky due to thin order book on DEX

### LAND (Landshare)
- **Price:** $0.14987
- **24h:** -0.11% | **7d:** -2.77%
- **Volume 24h:** $3.00K (CEX: $677, DEX: $2.32K)
- **Market Cap:** $801K
- **TVL:** $621K
- **Chains:**
  - Ethereum: `0x0e2ef8aecb3c01ad5d596f1b67134e199984d`
  - BNB Smart Chain (BEP20): `0x557f20ce25b41640ade4a3085d42d7e626d7965a`
- **Classification:** RWA / Thesis (tokenized land + yield farming component)
- **Liquidity note:** Very thin DEX volume → avoid LP; spot DCA only

## Decision Reasoning

**Why RWA bucket (not Core or Cycle):**
1. Narrative-driven (real estate tokenization) — long-term hold, not short-term cycle
2. Moderate TVL ($1–2M) — too thin for reliable LP income
3. Both tokens embed staking rewards (LAND especially) → spot hold yields via staking, not LP fees
4. Low volume on DEXes → wide spreads, high slippage → systematic DCA with limit orders essential

**Recommended approach:**
- **PROPS:** $100–200/month DCA on Ethereum (lower fees than mainnet, but still L1); hold spot; monitor for future Uniswap V3 pool emergence
- **LAND:** $50–100/month DCA on BSC (cheaper fees, same token); hold spot; stake via Landshare platform if APY attractive

**Why not Solana chains?** Neither token currently deployed on Solana. If Solana deployment announced, treat as Cycle Play (higher volatility, potential farming incentives).

## Links
- CMC PROPS: https://coinmarketcap.com/currencies/propbase/
- CMC LAND: https://coinmarketcap.com/currencies/landshare/
- Propbase site: https://propbase.app/
- Landshare site: https://landshare.io/

## Rate-Limit Workaround Used
- CoinGecko 429 after repeated calls → switched to CMC pro API with stored key (`ff52c5f015c3490da49adf12513a6d55`)
- For SOL price, used Kraken public API (`https://api.kraken.com/0/public/Ticker?pair=SOLUSD`) as CoinGecko fallback

## Vault Update
Added PROPS + LAND to `03-Strategies/token-watchlist.md` holdings table and `Crypto/Watchlist/2026-04-28 1700 UTC.md` Avalanche ecosystem section.
