# Data Sources & API Endpoints — DeFi LP Monitoring

## Price Feeds

### CoinMarketCap Pro API
**Primary** price source for AVAX, JOE, USDC.

- **Endpoint**: `https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest`
- **Method**: GET
- **Params**: `symbol=AVAX,JOE,USDC&convert=USD`
- **Headers**: `X-CMC_PRO_API_KEY: <key>`
- **Rate limit**: 30 calls/min (free tier), 120/300/600 depending on plan
- **Auth**: Key stored in `~/.hermes/scripts/cmc_config.json` → `coinmarketcap_api_key`
- **Fallback**: None — if CMC fails, use DexScreener price

**Response fields of interest**:
```json
{
  "data": {
    "AVAX": {
      "quote": {
        "USD": {
          "price": 9.0951,
          "percent_change_24h": -0.217,
          "last_updated": "2026-05-02T08:16:04.000Z"
        }
      }
    }
  }
}
```

**Notes**:
- CMC key is auto-redacted in vault logs (`***`)
- Do NOT log full key in any report or vault entry

---

### DexScreener
**Secondary** price + pool state. Also primary when CMC outage.

- **Endpoint**: `https://api.dexscreener.com/latest/dex/pairs/avalanche/POOL_ADDRESS`
- **Method**: GET
- **Rate limit**: Public, no key required; soft rate-limit ~60/min
- **Fallback chain**: DexScreener → on-chain `getSwapOut()` RPC

**Response key fields**:
```json
{
  "pairs": [{
    "pairAddress": "0x864d4e5Ee7318e97483DB7EB0912E09F161516EA",
    "priceUsd": "9.095",
    "priceNative": "9.09505",
    "liquidity": {"usd": 3895710, "base": 403433, "quote": 226460},
    "volume": {"h24": 2545294},
    "txns": {"h24": {"buys": 949, "sells": 1291}},
    "priceChange": {"h24": -0.4}
  }]
}
```

**Notes**:
- `priceUsd` string with up to 3 decimals; prefer `priceNative` for precision
- Volume is native token volume (AVAX × price ≈ USD quoted)
- No API key needed; User-Agent header recommended (`Gentech-Labs/1.0`)

---

## On-Chain RPC

### Avalanche C-Chain Public Endpoint
**Base RPC** for `eth_call` fallbacks and direct contract queries.

- **URL**: `https://api.avax.network/ext/bc/C/rpc`
- **Method**: POST `eth_call`
- **Auth**: None (public)
- **Rate limit**: ~20 calls/sec recommended, use batch calls when possible
- **Timeout**: 15–30s per batch

**Batching**: Batch up to 15 calls per HTTP request to reduce latency. See `lp-position-reader.py` for `rpc_call_batch` pattern.

---

### Routescan API (Wallet Balances)
Used to read native token balances outside LP positions.

- **Endpoint**: `https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api`
- **Method**: GET `module=account&action=tokenbalance&address=WALLET&contractaddress=TOKEN`
- **Auth**: None for read-only public calls
- **Typical calls**:
  * AVAX native → contract `0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7`
  * USDC → `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`
  * LP token → pool address itself

**Note**: Routescan may cache 30–60s; use RPC for freshest data.

---

## Pool Contract ABI Selectors (LFJ V2.2)

LFJ (Liquid Farming) V2.2 uses same ABI as UniswapV3 concentrated liquidity.

| Function | Selector (hex) | Purpose |
|----------|----------------|---------|
| `activeId()` | `0x05fc00e8` or `0xdbe65edc` (V2.2 variant) | Current active bin index |
| `balanceOf(address,uint256)` | `0x00fdd58e` | User's LP share in specific bin |
| `totalSupply(uint256)` | `0xbd85b039` | Total LP shares in bin |
| `getLBPairInformation(address,address,uint256)` (factory) | keccak(text)[:4] | Resolve pool address from token pair + binStep |

**Important**: `activeId` selector varies by LFJ version. The `lfj-position.py` script uses `0xdbe65edc` for V2.2; older V2.1 uses `0x05fc00e8`.

---

## Error Handling & Fallback Chain

For each data source, implement fallback priority:

### Price
1. CMC API (preferred — consistent across tokens)
2. DexScreener pool `priceUsd`
3. RPC `eth_call` to pool `getSwapOut(1 AVAX → USDC)`

### Reserves / Bin Data
1. DexScreener `liquidity.base|quote` (fast)
2. On-chain batch `eth_call` to pool reserves/getAmountsForLiquidity (if needed for decoding)
3. Cached `lfj-position-state.json` if both fail (stale flag)

### Wallet Balances
1. Routescan `tokenbalance` API
2. On-chain `balanceOf` calls (slower, rate-limited)

---

## Key Queries

### Get Active Bin (Python)
```python
import requests, json
rpc_url = "https://api.avax.network/ext/bc/C/rpc"
payload = {
    "jsonrpc": "2.0",
    "method": "eth_call",
    "params": [{"to": POOL_ADDRESS, "data": "0xdbe65edc"}, "latest"],
    "id": 1
}
resp = requests.post(rpc_url, json=payload).json()
active_bin = int(resp['result'], 16)
```

### Get Bin Balances (Batched)
See `scripts/fetch-lfj-position.py` — iterates `balanceOf(wallet, bin)` across position extent; batch groups of 15 to respect Avalanche RPC limits.

### Estimate 24h Fees from Volume
```python
volume = 2545294  # DexScreener h24 volume
fee_tier_bps = 5
total_fees = volume * (fee_tier_bps / 10000)      # $1272.65
share_pct = 0.015  # 0.015% of pool
estimated_fees = total_fees * (share_pct / 100)   # $0.19
```

---

## Endpoint Health Checks

Before full report run, quick health probe:

```bash
# CMC ping (lightweight)
curl -s -I "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?symbol=AVAX" \
  -H "X-CMC_PRO_API_KEY: $CMC_KEY" | head -n1

# DexScreener ping
curl -s -I "https://api.dexscreener.com/latest/dex/pairs/avalanche/POOL_ADDRESS" | head -n1

# RPC ping (simple eth_blockNumber)
curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

If any fail >3 consecutive runs → escalate to `#telegram/error` channel.

---

## Rate Limits & Timing

| Source | Rate Limit | Recommended Delay |
|--------|------------|------------------|
| CMC Pro (free) | 30/min | 2s between calls |
| DexScreener | Soft ~60/min | 1s between calls |
| Avalanche RPC | ~20/sec public | Batch 15 calls → 0.2s pause |
| Routescan | Unknown (public) | 0.5s between token balance calls |

**Total run time**: ~25–40s for full fetch + decode + write (within 60s cron window).

---

*Reference doc — kept lean with essentials; for full code see `scripts/fetch-lfj-position.py`*
