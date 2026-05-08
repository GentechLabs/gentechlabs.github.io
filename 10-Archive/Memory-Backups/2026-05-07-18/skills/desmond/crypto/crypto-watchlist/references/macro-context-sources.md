# Macro Context Sources — Quick Reference

## 1. Fear & Greed Index
```
GET https://api.alternative.me/fng/
```
Response:
```json
{
  "data": [
    {
      "value": "39",
      "value_classification": "Fear",
      "timestamp": "1746148800",
      "time_until_update": "3599"
    }
  ],
  "metadata": { "error": null }
}
```
- **value**: 0-100 integer string
- **value_classification**: Extreme Fear / Fear / Neutral / Greed / Extreme Greed
- Use: Include in "Why it's moving" as sentiment gauge

## 2. S&P 500 Daily Change
```
GET https://query1.finance.yahoo.com/v8/finance/chart/^GSPC?range=1d&interval=1m
```
Response structure:
```json
{
  "chart": {
    "result": [{
      "indicators": {
        "quote": [{
          "close": [7235.83, 7232.45, ..., 7230.12]
        }]
      },
      "meta": {
        "regularMarketPrice": 7230.12
      }
    }]
  }
}
```
Compute day change:
```python
closes = result[0]['indicators']['quote'][0]['close']
valid = [c for c in closes if c is not None]
day_change = ((valid[-1] - valid[0]) / valid[0]) * 100
current_price = result[0]['meta']['regularMarketPrice']
```

## 3. 10-Year Treasury Yield
```
GET https://query1.finance.yahoo.com/v8/finance/chart/^TNX?range=1d
```
- `^TNX` is CBOE 10Y Treasury yield index
- Response parallel to S&P above
- Extract `close` array for today's range; last value = current yield
- Example: `4.378%` (moves in basis points, typically 0.01% increments)

## 4. Crypto Market News (Optional)
Sources tried but blocked:
- CryptoCompare news: requires API key
- CoinDesk: HTML parsing failed (no consistent headline tags)
- Reddit `/r/CryptoCurrency`: 403 blocked
- CryptoPanic: 404 not found

**Current status**: News fetching not implemented. Macro context inferred from price action + Fear & Greed + equity/rate data.

### Possible Future Sources
- **NewsAPI.org**: Free tier with limited calls; requires API key
- **RSS feeds**: CoinDesk, Cointelegraph, The Block — need robust HTML parser
- **Twitter/X**: Not accessible without API v2 paid tier

## Macro Context Template

Combine the following elements into 3-4 bullet points:

1. **Risk-on/risk-off tone**: S&P direction + 10Y movement
2. **Crypto sentiment**: Fear & Greed value + classification
3. **Sector rotation**: Note which crypto sectors are moving (AI, gaming, DeFi, layer-1s)
4. **Notable outliers**: Flag coins with >3% move and plausible narrative

Example:
```
📰 WHY IT'S MOVING
• Fed policy uncertainty keeping risk assets in check — S&P 500 flat (-0.08%), 10Y Treasury yield steady at 4.378%
• Crypto sentiment in "Fear" (F&G Index: 39) reflecting broader macro caution and risk-off tone
• Mixed sector leadership: AI/crypto intersect (TAO) and gaming (BEAM) showing strength while core majors (BTC, SOL, AVAX) consolidate with mild weakness
• TAO rally driven by AI ecosystem narrative and incremental growth in the Bittensor network
```

## Python Snippet — Macro Fetcher

```python
import urllib.request, json

def fetch_fear_greed():
    url = "https://api.alternative.me/fng/"
    resp = urllib.request.urlopen(url, timeout=5)
    data = json.loads(resp.read())['data'][0]
    return {'value': int(data['value']), 'classification': data['value_classification']}

def fetch_sp500_change():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^GSPC?range=1d&interval=1m"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    result = data['chart']['result'][0]
    closes = [c for c in result['indicators']['quote'][0]['close'] if c is not None]
    change_pct = ((closes[-1] - closes[0]) / closes[0]) * 100
    current = result['meta']['regularMarketPrice']
    return {'current': current, 'day_change_pct': change_pct}

def fetch_10y_yield():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^TNX?range=1d"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    result = data['chart']['result'][0]
    closes = [c for c in result['indicators']['quote'][0]['close'] if c is not None]
    current = result['meta']['regularMarketPrice']
    delta = closes[-1] - closes[0] if len(closes) > 1 else 0
    return {'current': current, 'delta_bps': round(delta * 100, 1)}  # convert to basis points
```

## Error Handling

| Source | Common Errors | Recovery |
|--------|---------------|----------|
| Alternative.me FNG | HTTP 429 (rate limit) | Cache for 1 hour; retry later |
| Yahoo Finance | HTTP 403 (blocked), sometimes malformed data | Use fallback: last known values; skip macro context if both S&P and 10Y fail |
| All network errors | `URLError`, timeout | Return cached values (if <1 hour old); else skip that metric |
