# Binance Public API — Price Fetching Reference

## Endpoints Used

### 1. Current Price + 24h Change
```
GET /api/v3/ticker/24hr?symbol=AVAXUSDT
```
Response fields:
- `lastPrice`: string (current price)
- `priceChangePercent`: string (24h % change)
- `volume`: string (24h volume in base asset)
- `weightedAvgPrice`: string

Example response:
```json
{
  "symbol": "AVAXUSDT",
  "lastPrice": "9.0800",
  "priceChange": "-0.0500",
  "priceChangePercent": "-0.5470",
  "volume": "1108574.0000"
}
```

### 2. Historical Klines (for 1h/7d change)
```
GET /api/v3/klines?symbol=AVAXUSDT&interval=1h&limit=2
GET /api/v3/klines?symbol=AVAXUSDT&interval=1d&limit=8
```
Kline array format (each element):
```
[
  0: kline_open_time (ms),
  1: open price,
  2: high price,
  3: low price,
  4: close price,
  5: volume,
  6: kline_close_time (ms),
  7: quote_asset_volume,
  8: number_of_trades,
  9: taker_buy_base_asset_volume,
  10: taker_buy_quote_asset_volume,
  11: ignore
]
```

## Computing 1h Change
```python
# Fetch 2 most recent completed hourly candles
response = GET /api/v3/klines?symbol=AVAXUSDT&interval=1h&limit=2
prev_close = float(response[0][4])   # First candle close (previous hour)
curr_close = float(response[1][4])   # Second candle close (most recent completed hour)
change_1h_pct = ((curr_close - prev_close) / prev_close) * 100
```

**Why this works**: The most recent hourly candle may still be open. Using the *completed* candles (klines returns closed candles by default) gives accurate 1h change.

## Computing 7d Change
```python
# Fetch 8 daily candles to span 7 days + current day
response = GET /api/v3/klines?symbol=AVAXUSDT&interval=1d&limit=8
week_ago_close = float(response[0][4])    # Close 8 days ago
today_close = float(response[7][4])       # Close of most recent completed day
change_7d_pct = ((today_close - week_ago_close) / week_ago_close) * 100
```

**Note**: Using 8 candles ensures we capture a full 7 calendar days even if today's candle is still open.

## Rate Limits & Best Practices

- **No authentication needed** for public endpoints
- **Rate limit**: 1200 requests per minute per IP (generous)
- **Best practice**: Batch requests or use `batch_orders` endpoint if fetching many symbols
- **Error handling**: HTTP 429 → backoff 5s and retry; 4xx → check symbol validity

## Why Binance Over CoinGecko Public API

Issue encountered: CoinGecko returns HTTP 429 (Too Many Requests) even with single requests due to aggressive rate limiting. Binance public spot API is:
- No API key required
- No observed rate limiting on single-digit requests
- Real-time (updates every few seconds)
- Consistent JSON format

Trade-off: Binance only gives 24h change. Must compute 1h/7d manually via klines.

## Fallback Chain in YoYo Report

When generating the watchlist report:
1. **Try** `ticker/24hr` endpoint for price + 24h% (fast, reliable)
2. **Parallel fetch** klines (1h interval × 2 candles, 1d interval × 8 candles) for 1h and 7d%
3. **If Binance fails** (connection error, 5xx, symbol not found):
   - Fall back to CoinGecko simple price endpoint (if not rate-limited)
   - Else: DexScreener pair endpoint
   - Else: Report stale data from last successful fetch with "stale" flag

## Python Snippet — Full Watchlist Fetcher

```python
import urllib.request, json, time

BINANCE_BASE = "https://api.binance.com"

def get_binance_price(symbol):
    """Fetch price, 24h%, and compute 1h/7d%"""
    # Step 1: Ticker 24h
    ticker_url = f"{BINANCE_BASE}/api/v3/ticker/24hr?symbol={symbol}"
    req = urllib.request.Request(ticker_url, headers={'User-Agent': 'Gentech-Labs/1.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    ticker = json.loads(resp.read())
    
    price = float(ticker['lastPrice'])
    change_24h = float(ticker['priceChangePercent'])
    
    # Step 2: 1h change from klines
    klines_1h = get_klines(symbol, '1h', 2)
    change_1h = ((klines_1h[1][4] - klines_1h[0][4]) / klines_1h[0][4]) * 100
    
    # Step 3: 7d change from klines
    klines_7d = get_klines(symbol, '1d', 8)
    change_7d = ((klines_7d[-1][4] - klines_7d[0][4]) / klines_7d[0][4]) * 100
    
    return {
        'price': price,
        'change_1h': change_1h,
        'change_24h': change_24h,
        'change_7d': change_7d,
        'volume_24h': float(ticker['volume'])
    }

def get_klines(symbol, interval, limit):
    url = f"{BINANCE_BASE}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Gentech-Labs/1.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

# Usage
symbols = ['BTCUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'TAOUSDT']
for sym in symbols:
    data = get_binance_price(sym)
    print(f"{sym.replace('USDT','')}: ${data['price']:.4f} | 1h: {data['change_1h']:+.2f}% | 24h: {data['change_24h']:+.2f}% | 7d: {data['change_7d']:+.2f}%")
    time.sleep(0.2)  # Be nice to API
```

## Known Symbol Mappings

| Binance Symbol | CoinGecko ID | Notes |
|----------------|--------------|-------|
| BTCUSDT | bitcoin | Always available |
| SOLUSDT | solana | Always available |
| AVAXUSDT | avalanche-2 | Always available |
| LINKUSDT | chainlink | Always available |
| TAOUSDT | bittensor | Always available |
| XAUTUSDT | tether-gold | Tether Gold, XAUt ticker |
| BEAMUSDT | beam | Gaming token, may have low liquidity |

## Troubleshooting

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| `{"code":-1121,"msg":"Invalid symbol."}` | Symbol not listed on Binance | Check spelling; verify symbol exists on Binance spot market |
| HTTP 429 | Rate limit exceeded | Wait 60 seconds; reduce request frequency |
| Connection timeout | Network issue or Binance API down | Retry with backoff; fall back to CoinGecko |
| Empty klines array | Symbol just listed or delisted | Verify active trading; reduce limit parameter |
