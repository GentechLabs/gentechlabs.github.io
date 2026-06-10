# Data Layer Integration — AAE LP Dashboard

**Purpose:** Connect AAE front-end templates to real-time data sources

---

## Data Sources

| Data Type | Source | API | Cost |
|-----------|--------|-----|------|
| Token Price | Chainlink Oracle | On-chain | Free (via proxy) |
| Pool TVL/Stats | DexScreener API | `api.dexscreener.com` | Free tier |
| Fees Earned | Trader Joe Subgraph | `subgraph.traderjoexyz.com` | Free |
| Agent Signals | AAE Internal | Local DB | Free |

---

## Integration Pattern

### 1. Price Oracle (Chainlink)

**Endpoint:** On-chain via `AggregatorV3Interface`

```solidity
// Read from any chain's Chainlink price feed
// AVAX/USD: 0x... (Avalanche mainnet)
// ETH/USD: 0x... (Ethereum mainnet)
// SOL/USD: 0x... (Solana via Wormhole bridge)

function getCurrentPrice(address pair) external view returns (uint256) {
    // Adapter pattern — route to correct aggregator based on pair
    // Returns 8 decimals price, scale to 18 decimals
}
```

**Fallback:** DexScreener REST API (if Chainlink unavailable)

### 2. Pool Stats (DexScreener)

**Endpoint:** `https://api.dexscreener.com/latest/v1/pairs/{chain}/{address}`

```bash
curl https://api.dexscreener.com/latest/v1/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea
```

**Response includes:**
- `url`, `chainId`, `pairAddress`, `baseToken`, `quoteToken`
- `priceNative`, `priceUsd`, `txns`, `volume24h`
- `liquidity`, `fdv`, `pairCreatedAt`

### 3. Fees (Trader Joe Subgraph)

**Endpoint:** `https://subgraph.traderjoexyz.com/subgraphs/name/traderjoe/swap`

**Query:**
```graphql
{
  poolDayDatas(
    where: { pool: "0x864d4e5ee7318e97483db7eb0912e09f161516ea", date: <timestamp> }
    first: 7
  ) {
    date
    volumeToken0
    volumeToken1
    feesUSD
  }
}
```

---

## Agent Data Sync Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                        Data Ingestion                        │
├──────────────────────────────────────────────────────────────┤
│ 1. Price Oracle (on-chain) ──┐                               │
│ 2. DexScreener (off-chain) ──┼──→ Data Cache                │
│ 3. Subgraph (off-chain) ─────┘                               │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                        Data Cache                            │
│  • Redis / SQLite / Local JSON                               │
│  • 5-minute refresh interval                                 │
│  • Versioned snapshots                                       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      Agent Decision Engine                   │
│  • Detect patterns (rebalance, claim, compound)             │
│  • Evaluate conviction thresholds                            │
│  • Generate DeFi milestone progress                           │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                        Front-End Render                      │
│  • HTML dashboard (AAE-LP-Dashboard-Boilerplate)            │
│  • Telegram card (DeFi milestone embedded)                    │
│  • Voice summary (ElevenLabs)                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Error Handling

| Scenario | Fallback | Alert |
|----------|----------|-------|
| Chainlink unresponsive | DexScreener API | 🔴 Chainlink down |
| DexScreener rate limit | Cache last 24h | 🟡 Price stale (>5m) |
| Subgraph timeout | Calculate from chain event logs | 🟡 Fee data late |
| Cache unavailable | Real-time fetch | 🟠 Graceful degradation |

---

## Next Steps

✅ **Create data connector service** (`scripts/connector.py`)  
✅ **Add agent trigger conditions** (`config.example.json` → agent_actions)  
✅ **Add DeFi milestone progress** (weekly DCA % bars)  
✅ **Add Ghost Position toggle** (simulated vs live)

---

## References

- [Chainlink Price Feeds](https://docs.chain.link/data-feeds/price-feeds)
- [DexScreener API](https://docs.dexscreener.com/)
- [Trader Joe Subgraph](https://docs.traderjoexyz.com/)
