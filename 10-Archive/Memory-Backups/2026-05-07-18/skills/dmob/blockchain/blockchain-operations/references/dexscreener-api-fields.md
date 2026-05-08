---
title: DexScreener API Fields for LP Monitoring
description: Essential response fields and request patterns for fetching live pool data
updated: 2026-05-03
---

## Endpoint

```
GET https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}
```

Example:
```
https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea
```

## Response Structure

```json
{
  "pair": {
    "address": "0x864d4e5ee...",
    "chainId": "avalanche",
    "dexId": "traderjoe",
    "baseToken": { "symbol": "AVAX", "address": "...", "decimals": 18 },
    "quoteToken": { "symbol": "USDC", "address": "...", "decimals": 6 },
    "priceNative": "9.09505",
    "priceUsd": "9.09505",
    "volumeH24": 1356473.45,
    "volumeH6": 456789.12,
    "volumeH1": 82345.67,
    "txnsH24": { "buys": 1263, "sells": 1605 },
    "liquidity": { "usd": 3839628.50, "base": 123456.78, "quote": 987654.32 },
    "pairCreatedAt": 1712345678,
    "label": "LFJ V2.2",
    "tags": ["5bps", "binStep10"]
  }
}
```

## Essential Fields Extraction

| Field | Path | Purpose | Notes |
|-------|------|---------|-------|
| Price | `pair.priceNative` | Current AVAX price | Float |
| 24h Volume | `pair.volumeH24` | Pool trading volume | USD |
| TVL | `pair.liquidity.usd` | Total pool value locked | USD |
| Buy Count | `pair.txnsH24.buys` | Number of buys (24h) | For B/S ratio |
| Sell Count | `pair.txnsH24.sells` | Number of sells (24h) | For B/S ratio |
| Pair Created | `pair.pairCreatedAt` | Pool age | Unix timestamp |

## Fee Calculation Formula

```python
fee_rate_bps = 5
fee_rate = fee_rate_bps / 10000  # 0.0005

daily_fees = volume_24h * fee_rate
position_share = position_usd / tvl_usd
estimated_fees = daily_fees * position_share
```

**Example** (May 3 data):
```
volume_24h = $1,356,473
fee_rate = 0.0005
daily_pool_fees = $678.24
position_usd = $135.60
position_share = 135.60 / 3,839,628 = 0.0000353 (0.00353%)
estimated_fees = $678.24 × 0.0000353 = $0.024
```

## Pitfalls

1. **Zero/null fields**: Some pools return `null` for volume or liquidity if inactive. Always guard with `if not data or not data.get('pair')`.
2. **Price in USD vs Native**: For AVAX/USDC, `priceNative` and `priceUsd` are identical (USDC ≈ USD). For other pairs, use `priceUsd` when available.
3. **Rate limiting**: DexScreener allows generous but not unlimited requests. Add 1-second delay between batch requests.
4. **404 on invalid chain/pool**: Chain ID must be lowercase (`avalanche`, not `Avalanche`); pool address must be checksummed.

## User-Agent Requirement

```python
import urllib.request
req = urllib.request.Request(
    url,
    headers={"User-Agent": "Gentech-Labs/1.0"}
)
```

Without proper User-Agent, DexScreener returns 403/429.

## Fallback Chain

If DexScreener fails (timeout or 404):
1. Try `https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}` with `--retry 3`
2. Fall back to Birdeye API (if configured): `https://public-api.birdeye.so/defi/price?address={pool_address}`
3. Final fallback: use last known price from state file (stale but prevents crash)

## LP Efficiency Calculation (TraderJoe v2.2)

For CURVE-shaped positions in price range `[low, high]`:

```python
def efficiency(price, low, high, shape="curve"):
    if price < low or price > high:
        return 0.0
    position = (price - low) / (high - low)  # 0.0 at low, 1.0 at high
    if shape == "curve":
        # Symmetric parabola; peak = 100% at center
        return round((1 - abs(position - 0.5) * 2) * 100, 1)
    elif shape == "bidirectional":
        return round(abs(position - 0.5) * 2 * 100, 1)
    else:  # spot
        return 100.0
```

Efficiency reflects proportion of position actively earning fees. At 0% efficiency, price is exactly at either range bound; at 100%, price sits at range center.

## Sample Python Fetch Function

```python
def fetch_pair(chain: str, pool_address: str) -> dict:
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read().decode())
        pair = raw.get("pair") or (raw.get("pairs") or [{}])[0]
        return {
            "price": float(pair.get("priceNative", 0)),
            "volume_24h": float(pair.get("volumeH24", 0)),
            "tvl": float(pair.get("liquidity", {}).get("usd", 0)),
            "buys_24h": pair.get("txnsH24", {}).get("buys", 0),
            "sells_24h": pair.get("txnsH24", {}).get("sells", 0),
        }
    except Exception as e:
        return {"error": str(e)}
```
