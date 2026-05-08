---
name: lp-position-monitor
description: Monitor liquidity provider positions with fallback strategies, error handling, and milestone tracking.
---

# LP Position Monitor

Monitor liquidity provider positions across various AMMs with automatic fallback strategies when primary data sources fail, comprehensive error handling, and integration with milestone tracking systems.

## Overview

This skill provides a systematic approach to monitoring LP positions, handling data fetching failures gracefully, and providing actionable insights even when complete data isn't available.

## Core Components

### 1. Data Sources & Fallback Strategy

```python
class LPMonitor:
    def __init__(self, pool_config):
        self.pool_config = pool_config
        self.data_sources = [
            ("blockchain_explorer", self._fetch_via_explorer),
            ("defi_llama", self._fetch_via_llama),
            ("rpc_endpoint", self._fetch_via_rpc),
            ("historical_data", self._use_historical_estimate)
        ]
    
    def fetch_position_data(self):
        """Fetch LP position data with automatic fallback."""
        for source_name, fetch_func in self.data_sources:
            try:
                data = fetch_func()
                if data:
                    return {"source": source_name, "data": data, "status": "success"}
            except Exception as e:
                self._log_error(f"Failed to fetch from {source_name}: {str(e)}")
        
        return {"status": "failed", "error": "All data sources unavailable"}
```

### 2. Fallback Strategies

#### A. Blockchain Explorer Access
- Primary: Direct browser automation with stealth techniques
- Fallback: API access if available
- Error handling: Captcha detection, retry with delays

#### B. DeFi Data Aggregators
- DeFi Llama API
- Token Terminal
- Zapper.fi

#### C. RPC Endpoint Queries
- Direct blockchain RPC calls
- Custom subgraph queries

#### D. Historical Estimation
When real-time data is unavailable:
- Use last known position and price movements
- Apply impermanent loss calculations
- Provide conservative estimates with clear caveats

### 3. Error Handling & Assessment Protocol

```python
def assess_position(self, current_data, last_known_state, prices):
    """
    Assess LP position even when complete data isn't available.
    Returns actionable insights and recommendations.
    """
    assessment = {
        "status": "unknown",
        "confidence": "low",
        "action_needed": False,
        "recommendations": []
    }
    
    # Case 1: Full data available
    if current_data.get("status") == "success":
        assessment.update(self._analyze_full_data(current_data["data"]))
    
    # Case 2: Partial data or estimates
    elif last_known_state:
        assessment = self._analyze_with_estimates(last_known_state, prices)
    
    # Case 3: No data available
    else:
        assessment = self._analyze_without_data()
    
    return assessment
```

### 4. Milestone Tracking Integration

```python
def calculate_milestone_progress(self, daily_fees, target_fees):
    """Calculate progress toward milestone targets."""
    if target_fees <= 0:
        return {"percentage": 100, "status": "complete"}
    
    percentage = (daily_fees / target_fees) * 100
    bar_width = 20
    filled = min(int(percentage / (100 / bar_width)), bar_width)
    
    return {
        "percentage": round(percentage, 1),
        "bar": "[" + "=" * filled + "○" * (bar_width - filled) + "]",
        "status": "complete" if percentage >= 100 else "in_progress"
    }
```

### 5. Price Monitoring & Alerts

```python
def check_price_movements(self, current_prices, last_prices, thresholds={1.5, 5.0}):
    """Check for significant price movements and generate alerts."""
    alerts = []
    
    for symbol, current_price in current_prices.items():
        if symbol in last_prices:
            last_price = last_prices[symbol]
            change_pct = ((current_price - last_price) / last_price) * 100
            
            for threshold in thresholds:
                if abs(change_pct) >= threshold:
                    alerts.append({
                        "symbol": symbol,
                        "current_price": current_price,
                        "change_pct": change_pct,
                        "threshold": threshold,
                        "severity": "high" if threshold == 5.0 else "medium"
                    })
                    break  # Don't double-alert for multiple thresholds
    
    return alerts
```

### 6. Vault Update Generation

```python
def generate_vault_entry(self, timestamp, market_data, lp_assessment, milestone_progress):
    """Generate formatted vault entry with consistent markdown structure."""
    entry = f"""## {timestamp} Update

**Market Data**:
"""
    for symbol, price in market_data.items():
        entry += f"- **{symbol} Price**: ${price['value']} ({price['change']:+.2f}% 24h)"
        if abs(price['change']) >= 1.5:
            entry += " - **ALERT: >1.5% movement**"
        entry += "\n"
    
    entry += "\n**LP Position Monitoring**:\n"
    if lp_assessment.get("status") == "success":
        entry += f"- **Status**: ✅ Stable\n"
        # Add detailed LP data here
    elif lp_assessment.get("status") == "partial":
        entry += f"- **Status**: ⚠️ Partial Data - {lp_assessment.get('confidence')} confidence\n"
    else:
        entry += f"- **Status**: ❌ Data Fetching Failed - See Error Log\n"
    
    entry += f"""
**Error Log**: 
- {lp_assessment.get('error_log', 'No errors')}

**Current Assessment**: {lp_assessment.get('summary', 'Unable to assess')}

**Milestone Progress**: {milestone_progress['bar']} {milestone_progress['percentage']}% — ${milestone_progress.get('current_fees', 0)}/day

**Next Steps**:
{lp_assessment.get('recommendations', 'None')}
"""
    return entry
```

## Workflow

### Daily Monitoring Process

1. **Fetch Market Prices**
   - Use crypto-price-fetch skill for all tracked tokens
   - Check for price movements exceeding threshold values
   - Generate price alerts

2. **Fetch LP Position Data**
   - Attempt data retrieval from primary source (blockchain explorer)
   - Apply fallback strategies if primary fails
   - Log all errors and partial successes

3. **Assess Position**
   - If full data available: perform detailed analysis
   - If partial data: use estimation techniques with clear caveats
   - If no data: document assessment limitations

4. **Update Vault**
   - Generate timestamped entry with consistent format
   - Include market data, LP status, error log, and recommendations
   - Use ISO 8601 dates

5. **Generate Telegram Report**
   - Concise summary of key findings
   - Price alerts
   - LP position status
   - Milestone progress
   - Link to vault entry

## Pitfalls & Lessons Learned

### 1. External API Restrictions
- **Problem**: Many blockchain APIs have rate limits or require API keys
- **Solution**: Implement multi-source fallback with exponential backoff
- **Lesson**: Never rely on a single data source; always have at least 2-3 fallback options

### 2. Bot Detection on Explorers
- **Problem**: Public block explorers actively block automated access
- **Solution**: Use stealth techniques, rotate user agents, add delays
- **Alternative**: Use official APIs when available

### 3. Data Freshness vs. Availability
- **Problem**: Sometimes no real-time data is accessible
- **Solution**: Develop robust estimation techniques using last known state and price movements
- **Best Practice**: Clearly document when estimates are used and their confidence level

### 4. Rate Limiting on Free APIs
- **Problem**: Free APIs (CoinGecko, DeFi Llama) have strict rate limits
- **Solution**: Cache results, batch requests, use multiple providers
- **Implementation**: The crypto-price-fetch skill now includes retry logic and multiple fallbacks

### 5. Stablecoin Pricing
- **Problem**: Stablecoins should be priced at $1.00, not fetched from APIs
- **Solution**: Hardcode stablecoin prices in the price fetcher
- **Benefit**: Reduces API calls and avoids unnecessary errors

### 6. Error Logging
- **Problem**: Failures can occur at multiple points in the data chain
- **Solution**: Comprehensive error logging at each step
- **Value**: Enables quick diagnosis and targeted fixes

## Integration with Existing Systems

### D5 Milestone Tracker
- Automatically cross-reference LP data with milestone targets
- Generate progress bars and percentage calculations
- Flag when milestones are achieved or at risk

### Telegram Reporting
- Format concise summaries for team communication
- Include key metrics and action items
- Link to detailed vault entries for deeper analysis

## Testing Scenarios

```python
def test_lp_monitor():
    # Test 1: Full data available
    monitor = LPMonitor(pool_config)
    result = monitor.run_full_cycle()
    assert result["lp_assessment"]["status"] == "success"
    
    # Test 2: Data fetching fails but estimation works
    monitor = LPMonitor(pool_config_with_no_access)
    result = monitor.run_full_cycle()
    assert "estimate" in result["lp_assessment"]["method"]
    
    # Test 3: Complete failure with proper error logging
    monitor = LPMonitor(unreachable_pool)
    result = monitor.run_full_cycle()
    assert result["lp_assessment"]["status"] == "failed"
    assert "error_log" in result
```

## Performance Considerations

- Implement caching for frequently accessed data
- Use asynchronous requests when checking multiple pools
- Respect rate limits of all external services
- Consider local node access for blockchain data to avoid rate limits

## References

- DeFi Pulse: https://defipulse.com/ (alternative data source)
- Token Terminal: https://tokenterminal.com/ (revenue data)
- Zapper.fi API: https://docs.zapper.fi/ (wallet and position data)