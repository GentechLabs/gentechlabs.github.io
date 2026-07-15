# AAE Hybrid Strategy Engine — Technical Feasibility Assessment

> **Date:** Apr 29, 2026
> **Author:** DMOB
> **Question:** Can our current setup support the hybrid strategy brain, or do we need infrastructure changes?

---

## Current Infrastructure Audit

### ✅ What We Have (Working)

| Component | Status | Details |
|---|---|---|
| **Avalanche RPC** | ✅ Live | `api.avax.network` — eth_call, eth_getBalance work |
| **Wallet Monitoring** | ✅ Live | `wallet-monitor.py` — native AVAX + ERC-20 balances via Routescan |
| **Price Feeds** | ✅ Live | DexScreener (primary), CoinGecko (fallback), Birdeye x402 |
| **LP Position Tracking** | ✅ Live | On-chain bin share queries, position value computation |
| **Cron Scheduling** | ✅ Live | Hermes cron — 10min intervals, 4x/day, daily |
| **Signal Generation** | ✅ Live | AAE signal monitor — JSON + human readable output |
| **Telegram Delivery** | ✅ Live | Alerts, summaries, rebalance reminders |
| **State Persistence** | ✅ Live | JSON state files for cooldowns, milestones, history |
| **Gas Estimation** | ✅ Live | Via Routescan/AVAX RPC |
| **Birdeye x402** | ✅ Live | Premium data for volume, liquidity, pool stats |

### ❌ What We Need (Gaps)

| Component | Status | Difficulty | Notes |
|---|---|---|---|
| **Staking Rate Feed** | ❌ Missing | Easy | Benqi sAVAX exchange rate via RPC (need correct contract) |
| **Lending Rate Feed** | ❌ Missing | Easy | Benqi QiToken supply APR via API or on-chain |
| **Market Regime Classifier** | ❌ Missing | Medium | Pure Python logic — no new deps needed |
| **Multi-Strategy Portfolio Tracker** | ❌ Missing | Medium | Extends existing position reader |
| **Strategy Allocation Engine** | ❌ Missing | Medium | Pure Python logic — allocation matrix |
| **Rotation Execution** | ❌ Missing | **Hard** | DEX swap routing, tx signing, on-chain execution |
| **P&L Tracking Per Strategy** | ❌ Missing | Medium | Historical return tracking across strategies |
| **sAVAX Contract (Correct Address)** | ❌ Wrong addr | Easy | Need to verify correct Benqi proxy address |

---

## Feasibility by Component

### 1. Staking Rate Feed — ✅ Feasible

**How:** Query Benqi's sAVAX contract for exchange rate.

```python
# sAVAX token: 0x2b2c81e08f1af8835a78bb2a90ae924ace0fa45e
# Function: exchangeRate() → returns AVAX per sAVAX
# If proxy returns empty bytecode, try:
# - Benqi API endpoint (https://api.benqi.fi)
# - Subgraph query
# - DeFiLlama adapter
```

**Alternative:** DeFiLlama has Benqi staking data:
```python
# https://api.llama.fi/protocol/benqi-lending → supply/borrow APY
# https://yields.llama.fi/pools → filter for Avalanche + Benqi
```

**Effort:** 1-2 hours to integrate.

### 2. Lending Rate Feed — ✅ Feasible

**How:** Benqi QiToken supply rates via:
- DeFiLlama Yields API (free, no key)
- Benqi subgraph
- On-chain QiReserve queries

**Effort:** 1-2 hours to integrate.

### 3. Market Regime Classifier — ✅ Feasible

**How:** Pure Python computation from existing price/volume data.

Inputs we already have:
- Price history (DexScreener)
- Volume 24h (DexScreener)
- 7-day price change (computed)
- RSI (computed from price history)
- ATR (computed from price history)

Classification logic:
```python
regimes = ["BULL_TRENDING", "BEAR_TRENDING", "RANGE_BOUND", 
           "HIGH_VOLATILITY", "ACCUMULATION", "PRICE_DISCOVERY"]
```

**Effort:** 3-4 hours to implement + test.

### 4. Multi-Strategy Portfolio Tracker — ✅ Feasible

**How:** Extend existing `wallet-monitor.py` to track:
- LP position value (already have)
- HODL value (AVAX × price — already have)
- sAVAX balance + value (need sAVAX balance query)
- USDC lending position (need QiToken balance query)

**New data per strategy:**
```python
strategies = {
    "lp": {"value": float, "fees_24h": float, "apr": float},
    "hodl": {"value": float, "price_change_24h": float},
    "staking": {"value": float, "rewards_24h": float, "apr": float},
    "lending": {"value": float, "interest_24h": float, "apr": float}
}
```

**Effort:** 4-5 hours to implement.

### 5. Strategy Allocation Engine — ✅ Feasible

**How:** Pure Python logic. No new infrastructure needed.

```python
def get_allocation(regime, current_allocation, risk_profile):
    target = ALLOCATION_MATRIX[regime]
    delta = {s: target[s] - current_allocation[s] for s in STRATEGIES}
    # Only rotate if delta > threshold
    if any(abs(d) > 0.20 for d in delta.values()):
        return {"action": "ROTATE", "target": target, "delta": delta}
    return {"action": "HOLD", "target": target}
```

**Effort:** 2-3 hours to implement.

### 6. Rotation Execution — ⚠️ Hard

**This is the blocker.** Executing swaps on-chain requires:

1. **DEX Router Integration** — Pangolin/TraderJoe router contracts
2. **Transaction Signing** — Private key management (SECURITY CRITICAL)
3. **Gas Management** — Estimate, set, monitor
4. **Slippage Protection** — Min amount out, deadline
5. **Error Handling** — Reverts, front-running, MEV

**Options:**

| Approach | Security | Effort | Notes |
|---|---|---|---|
| **Manual execution (Phase 1)** | ✅ Safe | Low | Brain recommends, Jordan executes manually |
| **Semi-auto (Phase 2)** | ⚠️ Medium | Medium | Brain builds tx, Jordan signs via wallet |
| **Full auto (Phase 3)** | ❌ Risky | High | Auto-sign with hot wallet — NEVER recommended |
| **Agent wallet (Phase 4)** | ⚠️ Medium | High | Multisig or spending limit wallet |

**Recommendation:** Start with **manual execution**. The brain generates the rotation recommendation + exact amounts. Jordan executes the swaps himself. This is the safest path and still delivers 80% of the value.

### 7. P&L Tracking — ✅ Feasible

**How:** Extend state file to track per-strategy entry/exit, fees earned, rewards claimed.

**Effort:** 3-4 hours to implement.

---

## Architecture Decision: Build on What We Have

### Recommended Approach

```
EXISTING SCRIPTS (extend, don't replace):
├── lp-aae-signal-monitor.py → add staking/lending rates + regime detection
├── lp-position-reader.py → add sAVAX + QiToken balance queries
└── wallet-monitor.py → add strategy portfolio view

NEW SCRIPTS (minimal):
├── regime-classifier.py → market regime detection (standalone, called by AAE)
├── allocation-engine.py → strategy allocation recommendations
└── strategy-tracker.py → multi-strategy P&L tracking
```

### What NOT to Build Yet
- ❌ Auto-execution (rotation transactions)
- ❌ Private key management
- ❌ Multi-chain support (start Avalanche only)
- ❌ Options/advanced strategies

### What to Build First
1. **Staking/lending rate feeds** (1-2 hours)
2. **Regime classifier** (3-4 hours)
3. **Portfolio tracker** (4-5 hours)
4. **Allocation engine** (2-3 hours)
5. **Proactive alerts** (integrate into existing cron)

**Total estimated effort: 1-2 days of focused development**

---

## Data Flow (Proposed)

```
Every 10 minutes (existing cron):
┌─────────────────────────────────────────────────────┐
│  1. Fetch prices (DexScreener)                       │
│  2. Fetch wallet balances (Routescan)                │
│  3. Fetch LP position (on-chain bins)                │
│  4. Fetch staking rate (DeFiLlama/Benqi)    [NEW]    │
│  5. Fetch lending rate (DeFiLlama/Benqi)    [NEW]    │
│  6. Compute regime (RSI, volume, momentum)  [NEW]    │
│  7. Compare strategy returns                [NEW]    │
│  8. Generate allocation recommendation       [NEW]    │
│  9. Output signal (JSON + human readable)            │
└─────────────────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     ┌──────────────┐     ┌──────────────┐
     │  Telegram     │     │  State File   │
     │  (alerts)     │     │  (history)    │
     └──────────────┘     └──────────────┘
```

---

## Security Considerations

### What's Safe
- **Read-only queries** — all rate/balance/price queries are safe
- **No private keys** — the brain never signs transactions
- **Manual execution** — Jordan approves every rotation
- **Rate limiting** — max 1 rotation per 4 hours

### What's Risky (Future)
- Auto-execution with hot wallet — NEVER
- Private key in scripts — NEVER
- Unlimited token approvals — NEVER

---

## Recommendation

**Start building immediately.** Our current infrastructure supports 80% of what we need. The only hard part is execution routing, and we can defer that by having Jordan execute rotations manually.

**Phase 1 (This Week):**
1. Integrate DeFiLlama for staking/lending rates
2. Build regime classifier
3. Add strategy leaderboard to existing AAE output
4. Add proactive alerts to cron

**Phase 2 (Next Week):**
1. Multi-strategy portfolio tracker
2. Allocation engine with rotation recommendations
3. P&L tracking per strategy

**Phase 3 (Future):**
1. Execution routing (when we're ready for on-chain txs)
2. Multi-chain support
3. Advanced strategies

---

*Assessment: DMOB, Apr 29, 2026*
