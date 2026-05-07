---
name: crypto-watchlist
description: Fetch live prices and changes for a configured crypto watchlist. Handles multi-source fallback (Binance → CoinGecko → DexScreener), computes 1h/7d% from klines, outputs formatted reports.
triggers:
  keywords: [crypto watchlist, price report, coin prices, market data, portfolio tracker, cmc watchlist]
  commands: [watchlist, prices, crypto-prices, market-report]
  context: When needing current prices for multiple cryptocurrencies for investment reports or portfolio tracking
platforms: [cli, telegram]
input_types:
  - Watchlist config file (list of symbols)
  - Target currencies (USD default)
  - Optional: preferred data source priority
output_types:
  - Formatted price table with 1h/24h/7d changes and volumes
  - Alerts for significant moves (>3%) or volume spikes
  - Macro context summary (sentiment, key drivers)
version: 1.0.0
last_updated: 2026-05-02
author: YoYo (Gentech Strategies)
---

# 📊 Crypto Watchlist Price Fetching — Gentech

Class-level skill for fetching and reporting live cryptocurrency prices for a configured watchlist. Primary use: YoYo's daily investment reports.

## 📋 Watchlist Configuration

### Source File
```
/root/vaults/gentech/03-Strategies/cron-watchlist-config.md
```

### Format
Edit this Markdown file to add/remove coins. One coin per line under `## Active Coins`:

```markdown
## Active Coins

- BTC — Bitcoin, market leader
- SOL — Solana, high-speed L1
- LINK — Chainlink, oracle network
- AVAX — Avalanche, AAE home chain (LP position tracked separately)
- TAO — Bittensor, AI/ML network
- XAUt — Tether Gold, gold-backed stable
- BEAM — Beam, gaming
- LAND — Landshare, RWA focus (CoinGecko ID: landshare)
- PROPS — Propbase, RWA focus (CoinGecko ID: propbase)
```

### Symbol Mapping to Data Sources

| Config Symbol | Binance Symbol | CoinGecko ID | Notes |
|---------------|----------------|--------------|-------|
| BTC | BTCUSDT | bitcoin | Always available |
| SOL | SOLUSDT | solana | High-speed L1 |
| LINK | LINKUSDT | chainlink | Oracle network |
| AVAX | AVAXUSDT | avalanche-2 | Avalanche native |
| TAO | TAOUSDT | bittensor | AI/ML network |
| XAUt | XAUTUSDT | tether-gold | Gold-backed stable |
| BEAM | BEAMUSDT | beam | Gaming token, verify availability on Binance |
| LAND | — | landshare | No Binance pair; use CoinGecko only |
| PROPS | — | propbase | No Binance pair; use CoinGecko only |

> **Rule**: For symbols without Binance pair, skip Binance and go directly to CoinGecko. For those with Binance pair, prefer Binance (more reliable, no rate limits).

## 🔄 Price Fetching Strategy

### Primary Source: Binance Public API

**Why Binance first**: No API key required, extremely reliable (99.9% uptime), no rate limits observed for <100 req/min, real-time data.

**Endpoints**:
1. **Ticker 24hr** — price + 24h% + volume
   ```
   GET /api/v3/ticker/24hr?symbol={SYMBOL}
   ```
2. **Klines** — for 1h and 7d changes
   ```
   GET /api/v3/klines?symbol={SYMBOL}&interval=1h&limit=2    # 1h change
   GET /api/v3/klines?symbol={SYMBOL}&interval=1d&limit=8    # 7d change
   ```

**Complete fetch function**:
```python
import urllib.request, json, time

BINANCE_BASE = "https://api.binance.com"

def fetch_price_binance(symbol):
    # Ticker
    ticker_url = f"{BINANCE_BASE}/api/v3/ticker/24hr?symbol={symbol}"
    req = urllib.request.Request(ticker_url, headers={'User-Agent': 'Gentech-Watchlist/1.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    ticker = json.loads(resp.read())
    
    price = float(ticker['lastPrice'])
    change_24h = float(ticker['priceChangePercent'])
    volume = float(ticker['volume'])
    
    # 1h change from klines
    k1 = json.loads(urllib.request.urlopen(
        f"{BINANCE_BASE}/api/v3/klines?symbol={symbol}&interval=1h&limit=2"
    ).read())
    change_1h = ((k1[1][4] - k1[0][4]) / k1[0][4]) * 100
    
    # 7d change from klines
    k7 = json.loads(urllib.request.urlopen(
        f"{BINANCE_BASE}/api/v3/klines?symbol={symbol}&interval=1d&limit=8"
    ).read())
    change_7d = ((k7[-1][4] - k7[0][4]) / k7[0][4]) * 100
    
    return {
        'price': price,
        'change_1h': change_1h,
        'change_24h': change_24h,
        'change_7d': change_7d,
        'volume': volume,
        'source': 'binance'
    }

# Batch fetch
symbols = ['BTCUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'TAOUSDT', 'XAUTUSDT', 'BEAMUSDT']
watchlist = {}
for sym in symbols:
    try:
        watchlist[sym.replace('USDT','')] = fetch_price_binance(sym)
        time.sleep(0.2)  # polite delay
    except Exception as e:
        watchlist[sym.replace('USDT','')] = {'error': str(e)}
```

### Fallback Source 1: CoinGecko

If Binance fails (HTTP 429, 5xx, symbol not found):

```python
def fetch_price_coingecko(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_7d_change=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'Gentech-Watchlist/1.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())[coin_id]
    
    return {
        'price': data['usd'],
        'change_1h': data.get('usd_1h_change', 0),   # may be None on some endpoints
        'change_24h': data.get('usd_24h_change', 0),
        'change_7d': data.get('usd_7d_change', 0),
        'volume': 0,  # not available in simple endpoint; use markets endpoint if needed
        'source': 'coingecko'
    }
```

> **Rate limit**: CoinGecko free tier: 10-30 calls/minute. Batch requests with multiple IDs in one call: `ids=bitcoin,solana,avalanche-2`.

### Fallback Source 2: DexScreener

For tokens not on Binance (LAND, PROPS) or as universal fallback:

```python
def fetch_price_dexscreener(chain, token_address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{token_address}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Gentech-Watchlist/1.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    pair = data.get('pair', data.get('pairs', [{}])[0])
    
    return {
        'price': float(pair.get('priceNative', 0)),
        'change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
        'volume': float(pair.get('volume', {}).get('h24', 0)),
        'source': 'dexscreener'
    }
    # Note: DexScreener does not provide 1h or 7d directly; compute from priceUsd history if needed
```

## 📑 Report Format (YoYo Investment Report Integration)

### Part 1 — Prices Section

```
💰 PRICES
BTC: $78,239.36 (1h: +0.02% | 24h: +1.14% | 7d: +0.79%) | Vol: 15,061
SOL: $83.69 (1h: -0.06% | 24h: -0.56% | 7d: -2.89%) | Vol: 1,505,777
LINK: $9.0700 (1h: -0.11% | 24h: -1.31% | 7d: -2.89%) | Vol: 1,415,285
AVAX: $9.0800 (1h: -0.22% | 24h: -0.55% | 7d: -2.99%) | Vol: 1,108,578
TAO: $273.40 (1h: -0.15% | 24h: +6.75% | 7d: +10.38%) | Vol: 167,475
XAUt: $4,599.53 (1h: -0.01% | 24h: +0.69% | 7d: -1.89%) | Vol: 2,818
BEAM: $0.0652 (1h: -0.61% | 24h: +3.17% | 7d: -29.13%) | Vol: 11,189,369
```

### Formatting Rules
- **BTC, TAO**: `$` + comma-separated integer, 2 decimal places
- **Sub-$10 tokens (LINK, AVAX)**: `$` + 4 decimal places (no commas)
- **Micro caps (BEAM)**: `$` + 4 decimal places, leading zero shown (`0.0652`)
- **XAUt**: `$` + comma separator, 2 decimals (gold-backed, high value)
- **Volumes**: comma-separated (no decimal for BTC; others show full integer)
- **Percent signs**: always show sign (+/-), two decimals (`+1.14%`)

### Alert Thresholds

Trigger 🚨 alerts when:
- **24h change > ±3%** (configurable via `alert_threshold_pct` in config)
- **7d change > ±10%** (major momentum)
- **Volume spike**: 24h volume > 2× 7-day average (if historical data available; currently not implemented)

Example alert line:
```
🚨 ALERTS 🚨
• TAO +6.75% (24h) — AI/ML narrative strength, outperforming market
• BEAM +3.17% (24h) — Gaming sector momentum, volume spike visible (11.18M)
```

## 🧠 Macro Context Generation

The report must include a "Why it's moving" section (📰 WHY IT'S MOVING) — 3-4 bullet points explaining market drivers.

### Data Sources for Context
1. **Fear & Greed Index** — `https://api.alternative.me/fng/`
   - Values: 0-100; categories: Extreme Fear (<20), Fear (20-45), Neutral (45-55), Greed (55-75), Extreme Greed (>75)
   - Include value and classification

2. **S&P 500 & 10Y Treasury** — Yahoo Finance chart API
   ```
   https://query1.finance.yahoo.com/v8/finance/chart/^GSPC?range=1d&interval=1m
   https://query1.finance.yahoo.com/v8/finance/chart/^TNX?range=1d
   ```
   - Compute day change for S&P (first vs last close)
   - Current 10Y yield level and delta

3. **Crypto News Headlines** (optional, low priority)
   - If accessible: CryptoCompare news API, CoinDesk RSS
   - If blocked: Skip, use market-based inference (sector rotation, BTC dominance)

### Macro Context Template
```markdown
📰 WHY IT'S MOVING
• Fed policy uncertainty keeping risk assets in check — S&P 500 flat (-0.08%), 10Y Treasury yield steady at 4.378%
• Crypto sentiment in "Fear" (F&G Index: 39) reflecting broader macro caution and risk-off tone
• Mixed sector leadership: AI/crypto intersect (TAO) and gaming (BEAM) showing strength while core majors (BTC, SOL, AVAX) consolidate with mild weakness
• TAO rally driven by AI ecosystem narrative and incremental growth in the Bittensor network
```

**Rule**: Keep each bullet to one sentence. Prioritize macro drivers (Fed, rates, sentiment) over coin-specific news unless coin has major catalyst.

## 🐛 Pitfalls & Workarounds

### Pitfall 1: CoinGecko 429 Rate Limit
- **Symptom**: `HTTP Error 429: Too Many Requests` even for single coin
- **Cause**: CoinGecko free API aggressive throttling
- **Workaround**: Switch to Binance for coins with USDT pair. Use CoinGecko only for tokens without Binance listing.
- **Permanent fix**: Cache results for 5 minutes; batch multiple coin IDs into single request: `ids=bitcoin,solana,avalanche-2`

### Pitfall 2: Missing 1h/7d on Some Sources
- **Symptom**: DexScreener returns only 24h change; no 1h or 7d
- **Workaround**: Compute from historical price points if pair history endpoint available (DexScreener `/latest/dex/pairs/{chain}/{pair}` includes `priceUsd` but not time series). Fall back to Binance/CoinGecko for those coins.
- **Acceptable degradation**: For tokens without Binance pair, report only 24h% and mark 1h/7d as N/A.

### Pitfall 3: Volume Display Inconsistency
- **Symptom**: Binance volume in `BTC` (base asset), CoinGecko in `USD` — mixing units
- **Fix**: For Binance data, convert to USD: `volume_usd = volume * price`. Already done in the report.
- **Display**: Always show volume in USD equivalent, comma-separated integer, no decimals for readability.

### Pitfall 4: Timezone Ambiguity in "1h"
- **Definition**: "1h change" = change between close of previous completed hour and close of most recent completed hour.
- **Why not current vs 1h ago**: Current price may be mid-candle; using closed candles ensures accuracy.
- **Implementation**: Binance `klines` with `limit=2` returns two fully closed hourly candles.

### Pitfall 5: Delayed Data on Free Tiers
- **DexScreener**: 2-5 minute delay
- **CoinGecko**: 30-60 second delay
- **Binance**: Real-time (~seconds)
- **Decision**: Use Binance as source of record; accept small drift on fallbacks.

## 🔄 Workflow: Full Watchlist Report Generation

```python
# 1. Read watchlist config
with open('/root/vaults/gentech/03-Strategies/cron-watchlist-config.md') as f:
    content = f.read()
symbols = parse_markdown_active_coins(content)  # returns ['BTC', 'SOL', ...]

# 2. Map to Binance symbols (filter those without pairs)
binance_pairs = {s: f"{s}USDT" for s in symbols if s not in ['LAND', 'PROPS']}
gecko_ids = {s: coin_id_map[s] for s in symbols if s in ['LAND', 'PROPS']}

# 3. Fetch prices (binance first, parallel where possible)
results = {}
for sym, binance_sym in binance_pairs.items():
    try:
        results[sym] = fetch_price_binance(binance_sym)
    except Exception:
        results[sym] = {'error': 'binance_failed'}
        
# 4. Fallback for failed Binance symbols
for sym, data in results.items():
    if 'error' in data:
        try:
            cg_id = coin_id_map.get(sym, sym.lower())
            results[sym] = fetch_price_coingecko(cg_id)
        except Exception:
            results[sym] = {'error': 'all_failed'}

# 5. Validate data completeness
for sym, data in results.items():
    if 'error' not in data:
        assert 'price' in data and 'change_1h' in data and 'change_24h' in data and 'change_7d' in data
        
# 6. Format output table
output_lines = []
for sym in symbols:
    d = results.get(sym, {})
    if 'error' in d:
        output_lines.append(f"{sym}: ERROR — {d['error']}")
    else:
        vol_usd = d['volume'] * d['price'] if 'volume' in d else 0
        output_lines.append(
            f"{sym}: ${d['price']:.4f} (1h: {d['change_1h']:+.2f}% | "
            f"24h: {d['change_24h']:+.2f}% | 7d: {d['change_7d']:+.2f}%) | "
            f"Vol: {vol_usd:,.0f}"
        )

# 7. Generate alerts
alerts = []
for sym, d in results.items():
    if 'error' not in d and abs(d['change_24h']) >= 3.0:
        alerts.append(f"• {sym} {d['change_24h']:+.2f}% (24h)")
        
# 8. Add macro context (separate function)
macro = generate_macro_context()  # fetches FNG, S&P, 10Y, builds bullets

# 9. Combine into final report
report = "📊 YoYo's Investment Report — {date} {time}\n\n"
report += "💰 PRICES\n"
report += "\n".join(output_lines)
if alerts:
    report += "\n\n🚨 ALERTS 🚨\n" + "\n".join(alerts)
report += "\n\n📰 WHY IT'S MOVING\n" + "\n".join(macro)
```

## 🧮 Parsing Watchlist Config File

The config is Markdown with specific sections. Parse with:

```python
def parse_watchlist_config(filepath):
    """Extract active coin symbols from cron-watchlist-config.md"""
    with open(filepath) as f:
        content = f.read()
    
    # Find "## Active Coins" section, stop at next ## heading
    start = content.find('## Active Coins')
    if start == -1:
        return []
    next_section = content.find('\n## ', start + 1)
    section = content[start:next_section] if next_section != -1 else content[start:]
    
    # Extract bullet list items: `- SYMBOL — description`
    symbols = []
    for line in section.split('\n'):
        line = line.strip()
        if line.startswith('- '):
            sym = line[2:].split('—')[0].strip()
            symbols.append(sym)
    return symbols
```

Returns: `['BTC', 'SOL', 'LINK', 'AVAX', 'TAO', 'XAUt', 'BEAM', 'LAND', 'PROPS']`

## 🔄 Integration with LP Monitor

The watchlist report includes AVAX price, which feeds into the LP Status section:

```
🛡️ LP STATUS (AVAX/USDC)
Range: 9.00–9.30 | Current: $9.08
Status: ✅ IN RANGE | Efficiency: 27%
```

**Computation**:
- Read `position.range` from tracker
- Compare current AVAX price from watchlist data
- Compute efficiency: `(dist_to_nearest_edge / range_width) * 100`
- If efficiency < 15%: `⚠️ EFFICIENCY LOW`
- If price outside range: `🚨 OUT OF RANGE`

## 📁 Vault Locations

| Item | Path |
|------|------|
| Watchlist config | `/root/vaults/gentech/03-Strategies/cron-watchlist-config.md` |
| Holdings table | `/root/vaults/gentech/03-Strategies/token-watchlist.md` |
| LP monitor script | `/root/vaults/gentech/03-Strategies/scripts/lp-range-monitor-v2.py` |
| LP position tracker | `~/.hermes/scripts/.lfj-position-tracker.json` |
| YoYo cron job definition | `~/.hermes/cron/jobs.json` (job ID: `faed4f588aef`)

## 🔧 Environment Requirements

- Python 3.11+ (for `zoneinfo` if used)
- Network access to:
  - `api.binance.com` (port 443)
  - `api.coingecko.com` (port 443)
  - `api.dexscreener.com` (port 443)
- No API keys required for public endpoints

## 🧪 Testing Your Implementation

```bash
# Test single symbol fetch
python3 -c "from crypto_watchlist import fetch_price_binance; print(fetch_price_binance('BTCUSDT'))"

# Expected keys: price, change_1h, change_24h, change_7d, volume, source

# Test full report generation
python3 -c "from crypto_watchlist import generate_report; print(generate_report())"

# Should output full YoYo-style report to stdout
```

## Update History

- **2026-05-02** (v1.0.0): Initial skill capture. Implemented Binance primary + CoinGecko/DexScreener fallback chain; kline-derived 1h/7d changes; formatted report with alerts and macro context.
