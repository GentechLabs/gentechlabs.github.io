# Solana Yield Farming Landscape — 2026-05-03

**Context:** User asked "yield farm Solana and do the same thing" — mapping Solana ecosystem yield to the same DCA + range-optimization framework used for AVAX/USDC.

## Current Environment

**SOL Price (Kraken):** $84.22

**Top Solana DEX Protocols (2026):**
- **Raydium** — AMM CLMM, largest liquidity
- **Orca** — Whirlpools (concentrated liquidity with easy UI)
- **Jupiter** — Aggregator (routes across all DEXs)

## Pool Categories & Strategy Mapping

### Category 1: Blue-Chip Stable Pairs (Core-ish)
| Pool | Approx. APR (2026 range) | Strategy | Range |
|------|-------------------------|----------|-------|
| SOL/USDC | 50–200% (fee + swap fees) | Tight CLMM | 5–10% |
| SOL/USDt | Similar to USDC | Tight CLMM | 5–10% |

**Note:** These are the "Core DeFi equivalent" on Solana. Use tight ranges, frequent rebalancing, high capital efficiency.

### Category 2: Ecosystem Governance Tokens (Cycle)
| Pool | Incentive Layer | Strategy | Risk |
|------|----------------|----------|------|
| JUP/USDC | JUP emissions + fees | Concentrated | Medium |
| BONK/USDC | BONK rewards + fees | Concentrated | High (meme) |
| PYTH/USDC | PYTH staker rewards | Concentrated | Medium |
| MNGO/USDC | Mango Markets (legacy) | Wider range | Medium |

**Classification:** Cycle Plays — high volatility, farming incentives, asymmetric upside on ecosystem narratives.

### Category 3: New DeFi Experiments (Speculative)
- New protocol launches often offer 500–1000%+ APR initially
- **Risk:** Smart contract risk + farm-and-dump
- **Strategy:** Small positions (≤$100), short duration (2–4 weeks), take profits quickly

## Pool Data Sources

**Raydium API patterns:**
- Official pools: `https://api.raydium.io/v2/sdk/liquidity/mainnet`
- Individual pool: `https://api.raydium.io/v2/sdk/liquidity/mainnet/{poolAddress}`
- Unfortunately 404 on main endpoint in testing (may require updated URL or auth)

**Orca API:**
- Whirlpools: `https://api.orca.so/v2/pools` (currently 404 in this environment)
- Requires API key for production use

**Jupiter Aggregator:** `https://quote-api.jup.ag/v6/price` (for best entry routing)

**Alternative data sources:**
1. **DexScreener** (`https://api.dexscreener.com/latest/dex/pairs/solana`) — works reliably for price/TVL/volume
2. **CoinGecko** `/simple/price?ids=solana&vs_currencies=usd` — SOL price
3. **SolanaFm** or **Helius** RPC for on-chain pool reads (if deep LP monitoring needed)

## Implementation Plan

**Immediate actions:**
1. Write token classification script (`scripts/classify-token.py`) that queries CMC/CoinGecko → outputs bucket + chain + TVL tier
2. Set up Solana LP monitor cron:
   - Track SOL/USDC position on Raydium CLMM
   - Track JUP/USDC as cycle play secondary
   - Frequency: 4× daily (aligned with AVAX LP monitoring)
3. Create Solana vault folder: `03-Projects/DeFi/Solana-Yield-Farms/` (mirrors LFJ-AVAX structure)

**Automation hooks:**
- Use existing `cmc-watchlist.py` framework, extend to track SOL price + selected SPL token prices
- Leverage `defi-lp-monitor` skill but adapt for Solana RPC calls (web3.py → solana.py)

## Rate-Limit Handling (This Session)

**Issue:** CoinGecko API returned 429 Too Many Requests after 3–4 rapid calls.

**Workarounds used:**
1. **Delay strategy:** 5–20 second pauses between calls
2. **Alternative provider:** Kraken public API for SOL price (no key, no rate limit)
3. **CMC pro API** as primary source (key stored in `~/.hermes/scripts/cmc_config.json`)
4. **Batch requests:** CMC allows multiple symbols in one call: `?symbol=SOL,BONK,JUP`

**Recommendation:** Implement fallback chain in `scripts/solana-price-monitor.py`:
```
1. Try CoinGecko (cache 1min)
2. If 429 → Kraken
3. If both fail → Binance public API
```

---

## Vault Integration Points

- **Portfolio allocation:** Update `03-Strategies/Investment_Strategy_Agent_Economy.md` allocation table to include Solana bucket
- **Watchlist:** Add JUP, BONK, PYTH to CMC Bullish watchlist (675437...)
- **LP tracker:** Create `03-Projects/DeFi/Solana-Yield-Farms/SOL-USDC-Raydium.md` mirroring LFJ-AVAX format
- **Strategy doc:** Extend `macro-thesis-four-year-cycle-dead.md` to include Solana ecosystem cycle timing

---

## Open Questions (For Next Session)

1. **Solana RPC setup:** Need persistent RPC endpoint (Helius/QuickNode) for on-chain LP reads
2. **Wallet tracking:** Which wallet holds Solana positions? Need to add to Routescan/Solscan monitoring
3. **Farm compounding:** Auto-compound fees on Solana? Or manual claim/restake?
4. **Cross-chain DCA:** Buy SOL on CEX (Coinbase) → bridge to Solana → LP on Raydium? What's the cost-benefit vs. staying on Avalanche?
