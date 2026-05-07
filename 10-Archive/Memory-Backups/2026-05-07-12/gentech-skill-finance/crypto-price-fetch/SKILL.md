---
name: crypto-price-fetch
description: Fetch cryptocurrency prices with robust fallback chain and error handling for production use.
---

# Crypto Price Fetch

Fetch cryptocurrency prices with automatic fallback between providers and comprehensive error handling.

## Fallback Chain

1. **CoinMarketCap** (primary) — needs API key in environment
2. **CoinGecko** (free, no key) — reliable fallback, rate-limited  
3. **Binance** (tertiary) — public API, high availability

## Implementation

Use `execute_code` with Python standard library only. The function should handle various error conditions and edge cases.

```python
import json, urllib.request, os, time, socket
from typing import Optional, Dict, Any

class CryptoPriceFetcher:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.socket_timeout = timeout
        
    def fetch(self, symbol: str) -> Optional[float]:
        """Fetch price for a cryptocurrency symbol."""
        for attempt in range(self.max_retries):
            try:
                price = self._try_fetch(symbol)
                if price is not None:
                    return price
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
    
    def _try_fetch(self, symbol: str) -> Optional[float]:
        # Try CoinMarketCap if API key exists
        api_key = os.environ.get("COINMARKETCAP_API_KEY", "")
        if api_key:
            try:
                price = self._fetch_cmc(symbol, api_key)
                if price:
                    return price
            except Exception:
                pass
        
        # CoinGecko fallback
        try:
            price = self._fetch_coingecko(symbol)
            if price:
                return price
        except Exception:
            pass
        
        # Binance tertiary fallback
        try:
            price = self._fetch_binance(symbol)
            if price:
                return price
        except Exception:
            pass
        
        return None
    
    def _fetch_cmc(self, symbol: str, api_key: str) -> Optional[float]:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USDC"
        req = urllib.request.Request(
            url, 
            headers={
                "X-CMC_PRO_API_KEY": api_key,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
            quote = data["data"][symbol]["quote"]["USDC"]
            return float(quote["price"])
    
    def _fetch_coingecko(self, symbol: str) -> Optional[float]:
        # ID mapping for common cryptocurrencies
        id_map = {
            "AVAX": "avalanche-2", "ETH": "ethereum", "BTC": "bitcoin",
            "SOL": "solana", "MATIC": "matic-network", "LINK": "chainlink",
            "UNI": "uniswap", "AAVE": "aave", "ARB": "arbitrum", "OP": "optimism",
            "JOE": "joe", "USDC": "usd-coin", "USDT": "tether", "DAI": "dai"
        }
        
        # Stablecoins return $1.00
        if symbol in ["USDC", "USDT", "DAI"]:
            return 1.00
        
        cg_id = id_map.get(symbol.upper(), symbol.lower())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
        req = urllib.request.Request(
            url, 
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
        
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
            return float(data[cg_id]["usd"])
    
    def _fetch_binance(self, symbol: str) -> Optional[float]:
        # Map symbol to Binance trading pair format
        binance_map = {
            "AVAX": "AVABUSD",
            "BTC": "BTCUSDC",
            "ETH": "ETHUSDC",
            "SOL": "SOLUSDC",
            "JOE": "JOEBUSD"
        }
        
        pair = binance_map.get(symbol.upper(), f"{symbol}USDC")
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}"
        
        with urllib.request.urlopen(url, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
            return float(data["lastPrice"])
```

## Usage

```python
fetcher = CryptoPriceFetcher()
avax_price = fetcher.fetch("AVAX")
avax_change = ((avax_price - last_price) / last_price) * 100
```

## Pitfalls & Edge Cases

### 1. Rate Limiting (CoinGecko)
CoinGecko free tier is rate-limited (~10-30 req/min). The fetcher includes:
- Exponential backoff retry logic
- Multiple fallback sources to distribute load

### 2. Stablecoin Pricing
Stablecoins (USDC, USDT, DAI) are pegged to USD and should return $1.00 directly rather than making API calls.

### 3. Symbol Mapping
Different exchanges use different symbol formats:
- CoinGecko uses IDs (AVAX → "avalanche-2")
- Binance uses trading pairs (AVAX → "AVABUSD")
- Maintain mapping dictionaries for common tokens

### 4. Network Timeouts
Always set reasonable timeouts (default: 10 seconds) to prevent hanging.

### 5. API Key Management
CoinMarketCap requires an API key. The fetcher gracefully falls back to other sources if the key is missing or the API fails.

### 6. Error Handling
All external calls are wrapped in try/except blocks. The fetcher returns None if all sources fail, allowing the caller to handle missing data gracefully.

## Performance Considerations

- Use connection pooling for high-frequency requests
- Cache results to avoid repeated API calls
- Respect rate limits of each provider
- Consider using WebSocket streams for real-time data

## Testing

```python
# Test with known values
assert abs(fetcher.fetch("USDC") - 1.00) < 0.01
assert fetcher.fetch("AVAX") > 0  # Should return a positive number
```