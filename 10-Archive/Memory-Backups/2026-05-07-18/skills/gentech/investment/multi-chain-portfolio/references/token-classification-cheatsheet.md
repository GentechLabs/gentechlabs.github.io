# Token Classification Cheatsheet

**Quick-lookup thresholds for multi-chain portfolio bucket assignment.**

---

## Liquidity Metrics → Bucket

| TVL (Total Value Locked) | 24h Volume | Classification | Strategy | LP Viability |
|-------------------------|------------|----------------|----------|--------------|
| **> $10M** | > $1M | Core DeFi | Tight LP (5–15% range) | ✅ Yes |
| **$5–10M** | $500K–$1M | Core DeFi (secondary) | Tight to medium LP (10–20%) | ✅ Yes |
| **$1–5M** | $100K–$500K | RWA / Thesis | Spot hold; wide LP only (30–50%) | ⚠️ Selective |
| **$500K–$1M** | $50K–$100K | Speculative (small) | Spot DCA only | ❌ Avoid LP |
| **< $500K** | < $50K | High-risk / Meme | Spot only, tiny positions | ❌ Avoid LP |

---

## Chain Identification via CMC API

**Endpoint:** `GET /v1/cryptocurrency/info?symbol=XXX`

**Key fields:**
- `data[XXX].platform.name` — Primary chain name
- `data[XXX].platform.token_address` — Contract address on that chain
- `data[XXX].contract_address[]` — Array of all chain deployments

**Example parsing (Python):**
```python
import requests
api_key = "YOUR_KEY"
url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?symbol=PROPS"
resp = requests.get(url, headers={'X-CMC_PRO_API_KEY': api_key}).json()
data = resp['data']['PROPS']
platform = data.get('platform', {})  # May be dict OR string depending on API version
if isinstance(platform, dict):
    chain = platform.get('name', 'Unknown')
    address = platform.get('token_address', 'N/A')
else:
    # Fallback: extract from contract_address array
    contracts = data.get('contract_address', [])
    if contracts:
        chain = contracts[0].get('platform', {}).get('name', 'Unknown')
        address = contracts[0].get('contract_address', 'N/A')
```

---

## Volume-to-TVL Ratio (Health Indicator)

> **Formula:** `volume_24h / TVL`

| Ratio | Interpretation |
|-------|----------------|
| > 0.5 | Very active (high turnover) — could mean volatility or strong usage |
| 0.1–0.5 | Healthy range |
| 0.05–0.1 | Moderate activity |
| < 0.05 | Low activity — thin market, avoid LP |

---

## Multi-Chain Token Flags

When a token lives on multiple chains:

1. **Pick ONE chain for LP provision** — choose chain with:
   - Highest TVL in that token's pool
   - Lowest fees
   - Best wallet integration (already have wallet there?)

2. **Other chains: spot-hold only** — use for DCA accumulation, not liquidity

3. **Record decision in vault:** `03-Projects/Portfolios/Active/{Token}-{Chain}.md`

---

## Quick Classification Examples (from 2026-05-03)

| Token | TVL | Volume | Chain(s) | Bucket | LP? |
|-------|-----|--------|----------|--------|-----|
| PROPS | $1.09M | $1.86M | Ethereum, Aptos | RWA | No (spot + stake) |
| LAND | $621K | $3K | Ethereum, BSC | RWA | No (spot only) |
| AVAX | $3.98M (pool) | $21.5M | Avalanche | Core | Yes (tight LP) |
| SOL | N/A | N/A | Solana | Cycle (proxy) | Yes (tight LP on SOL/USDC) |

---

## When to Upgrade Classification

Monitor monthly:
- **TVL growth > 50%** in 30 days → consider upgrading bucket (RWA → Core)
- **Volume/TVL ratio consistently > 0.3** → liquidity improving → LP viability review
- **New chain deployment** on high-throughput L2 (Base, Arbitrum) → may open better LP opportunities

---

## Rate-Limit Fallback Chain

When fetching classification data:

1. **Primary:** CoinGecko `/simple/price` (free, no key)
2. **Fallback 1:** Wait 20s, retry CoinGecko with different User-Agent
3. **Fallback 2:** CMC Pro API (requires key, stored at `~/.hermes/scripts/cmc_config.json`)
4. **Fallback 3:** Kraken/Binance public API (for price only, not chain info)

**Script location:** `scripts/classify-token.py` (automates this chain)
