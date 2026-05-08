# DexScreener API — Quirks & Fallbacks

## Base URL
```
https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}
```

## Response Shape

DexScreener returns either:
- Single object: `{ "pair": { ... } }`
- Multi-pair array: `{ "pairs": [{...}, ...] }` (for some pairs)

### Extraction Pattern (safe)
```python
data = json.loads(response)
pair = data.get("pair", data.get("pairs", [{}])[0] if data.get("pairs") else {})
```

## Key Fields

| Field | Path | Type | Notes |
|-------|------|------|-------|
| Price | `pair.priceNative` | float | In native token (AVAX for AVAX/USDC) |
| 24h Volume | `pair.volume.h24` | float | USD |
| Liquidity | `pair.liquidity.usd` | float | Pool TVL in USD |
| 24h Change | `pair.priceChange.h24` | float | Percent (±) |
| Tokens | `pair.tokens` | array | `[{"symbol": "AVAX", "base": "123.45", "quote": "..."}]` |
| Pair Address | `pair.pairAddress` | string | Checksum address |
| Factory | `pair.factory` | string | May be null |

## Known Quirks

### 1. `priceNative` May Be Zero
**Symptom**: Pool returns `priceNative: 0` even though pool is active.  
**Cause**: Some older Trader Joe V2 pools don't populate this field reliably.  
**Fallback**: Use `pair.priceUsd` and divide by token price from CMC if available.  
**Fix**: In d5-master-cron, prefer `priceNative` first, fall back to compute from `priceUsd` if `priceNative == 0`.

### 2. Missing `liquidity.usd`
**Symptom**: `pair.liquidity` exists but `.usd` field missing.  
**Fallback**: Sum token values manually:
```python
liq_usd = 0
for t in pair.get("tokens", []):
    liq_usd += float(t.get("quote", 0) or 0)
```

### 3. Stale Data
DexScreener caches for ~1–2 minutes. If volume appears unchanged from prior call, consider:
- Adding `Cache-Control: no-cache` header (may not work)
- Adding jitter to request timestamps
- Using `lastUpdatedAt` field to compute staleness

### 4. Rate Limiting
No official rate limit stated, but >10 req/s may trigger 429. Our schedule:
- CMC: Every 4h (4× daily) — safe
- DexScreener: Every 4h concurrent — safe
- DeBank/Snowtrace: Separate calls — safe

### 5. Chain ID Case Sensitivity
Chain slug must be lowercase: `avalanche`, not `Avalanche` or `AVAX`.

## Error Handling Pattern

```python
def fetch_dexscreener():
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_addr}"
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        pair = safe_extract(data)
        return {
            "price": float(pair.get("priceNative", 0)),
            "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
            "liquidity": float(pair.get("liquidity", {}).get("usd", 0)),
            "change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
        }
    except Exception as e:
        # Log error, fall back to cached state or CMC price only
        return {}
```

## Caching Strategy

- Store latest successful response in `~/.hermes/scripts/.dexcache.json`
- On failure, return cached value with `(cached)` marker in logs
- TTL: 5 minutes for price, 15 minutes for volume

## Comparison: LFJ Pool vs Trader Joe Direct

DexScreener aggregates across DEXes. For LFJ (Trader Joe V2.2 concentrated liquidity):
- Pool address: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- Should always resolve via DexScreener
- If not found, check for contract code existence on Snowtrace — may indicate pool was closed/removed

**Sign of issue**: API returns empty `pairs` array or `pairAddress` mismatch.

## Related Skills

- `defi-lp-monitor` — Primary consumer of this data
- `crypto-price-fetch` — CMC API parallel for spot prices
- `stateful-alert-monitoring` — Debounce repeated API failures