# Compound vs. Extract Protocol — Architecture

**Project:** compound-extract-protocol
**Chain:** Avalanche (Phase 1), Multi-chain (Phase 2)
**Stack:** Python + JavaScript + Smart Contracts
**Status:** Phase 1 — Fee Monitoring

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Dashboard  │  │   Settings  │  │   History   │    │
│  │  (Position)  │  │  (Prefs)    │  │  (Logs)     │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │             │
│  ┌──────┴────────────────┴────────────────┴──────┐    │
│  │              API Gateway / Router              │    │
│  └──────────────────────┬────────────────────────┘    │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│                   CORE ENGINE                           │
│  ┌──────────────┐  ┌────┴─────┐  ┌──────────────┐    │
│  │ Fee Monitor  │  │ Decision │  │   Executor   │    │
│  │ (Tracking)   │  │ Engine   │  │ (Compound/   │    │
│  │              │  │ (AI)     │  │  Extract)    │    │
│  └──────┬───────┘  └────┬─────┘  └──────┬───────┘    │
│         │               │               │             │
│  ┌──────┴───────────────┴───────────────┴──────┐    │
│  │              State Manager                   │    │
│  │  (Position state, fee history, user prefs)  │    │
│  └──────────────────────┬──────────────────────┘    │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│                   EXTERNAL LAYER                        │
│  ┌──────────────┐  ┌────┴─────┐  ┌──────────────┐    │
│  │  LFJ RPC     │  │ Jupiter  │  │   User       │    │
│  │  (Position)  │  │ (Swap)   │  │   Wallet     │    │
│  └──────────────┘  └──────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Fee Monitor (`fee_monitor.py`)

**Responsibility:** Track real-time fee accumulation per LP position

```python
# Core data structure
position = {
    "id": "position_123",
    "dex": "lfj",
    "chain": "avalanche",
    "pair": "AVAX/USDC",
    "address": "0x...",
    "nft_id": "12345",
    "principal": {
        "avax": 10.0,
        "usdc": 250.0
    },
    "fees": {
        "avax": 0.0,
        "usdc": 0.0,
        "last_updated": "2026-01-01T00:00:00Z"
    },
    "status": "in_range",
    "range": {
        "lower": 35.0,
        "upper": 45.0
    }
}
```

**Methods:**
- `get_position(position_id)` — fetch current state from RPC
- `get_fees(position_id)` — calculate accumulated fees
- `update_fees(position_id)` — refresh fee data
- `get_fee_velocity(position_id)` — fees per hour trend

**Implementation:**
- JSON-RPC calls to Avalanche node
- Parse LFJ factory contract for position data
- Cache results (1-minute TTL) to reduce RPC calls
- WebSocket subscription for real-time updates (Phase 2)

### 2. Decision Engine (`decision_engine.py`)

**Responsibility:** Determine optimal compound vs. extract timing

**Decision Matrix:**

```python
def should_compound(position, user_prefs, market_data):
    """Return (action, confidence, reasoning)"""
    
    # Rule 1: User threshold reached
    if position.fees.usdc >= user_prefs.extract_threshold:
        return ("extract", 1.0, f"Fees hit ${user_prefs.extract_threshold}")
    
    # Rule 2: Gas is cheap — compound now
    if market_data.gas_price < user_prefs.gas_threshold:
        return ("compound", 0.9, f"Gas low: {market_data.gas_price} gwei")
    
    # Rule 3: Market is stable — compound to grow
    if market_data.volatility < 0.02:  # <2% daily vol
        return ("compound", 0.8, "Stable market, compounding grows position")
    
    # Rule 4: Market is volatile — extract to secure profits
    if market_data.volatility > 0.05:  # >5% daily vol
        return ("extract", 0.7, "Volatile market, extracting profits")
    
    # Rule 5: Default — follow user split preference
    return (user_prefs.default_action, 0.6, "Following user preference")
```

**Input Signals:**
- Fee velocity (accelerating = compound, decelerating = extract)
- Gas price (low = compound, high = wait)
- Market volatility (stable = compound, volatile = extract)
- User balance (low stablecoin = extract, high = compound)
- Time in position (long = compound, short = extract)

### 3. Executor (`executor.py`)

**Responsibility:** Execute compound or extract operations

**Extract Flow:**
```python
def extract_fees(position, amount):
    """Extract specified amount from position fees"""
    
    # Step 1: Claim fees from DEX
    tx1 = claim_fees(position.nft_id)
    wait_for_confirmation(tx1)
    
    # Step 2: Swap fees to stablecoin
    tx2 = swap(
        token_in=position.fees_token,
        token_out="USDC",
        amount_in=amount,
        max_slippage=0.005  # 0.5%
    )
    wait_for_confirmation(tx2)
    
    # Step 3: Send to user wallet
    tx3 = transfer(
        token="USDC",
        amount=amount_out,
        to=user_wallet
    )
    wait_for_confirmation(tx3)
    
    return {
        "action": "extract",
        "amount_claimed": amount,
        "amount_received": amount_out,
        "fees_paid": tx2.fee,
        "tx_hashes": [tx1, tx2, tx3]
    }
```

**Compound Flow:**
```python
def compound_fees(position):
    """Reinvest fees back into position"""
    
    # Step 1: Claim fees from DEX
    tx1 = claim_fees(position.nft_id)
    wait_for_confirmation(tx1)
    
    # Step 2: Swap half to other token in pair
    tx2 = swap(
        token_in=position.fees_token,
        token_out=position.other_token,
        amount_in=position.fees / 2,
        max_slippage=0.005
    )
    wait_for_confirmation(tx2)
    
    # Step 3: Add liquidity back to position
    tx3 = add_liquidity(
        position_id=position.id,
        amount0=position.fees / 2,
        amount1=amount_out
    )
    wait_for_confirmation(tx3)
    
    return {
        "action": "compound",
        "amount_compounded": position.fees,
        "new_position_value": get_position_value(position.id),
        "tx_hashes": [tx1, tx2, tx3]
    }
```

### 4. State Manager (`state_manager.py`)

**Responsibility:** Persist position state, fee history, user preferences

**Storage:** SQLite (local) + JSON (dashboard)

```sql
-- Position state
CREATE TABLE positions (
    id TEXT PRIMARY KEY,
    dex TEXT,
    chain TEXT,
    pair TEXT,
    address TEXT,
    nft_id TEXT,
    principal_json TEXT,
    fees_json TEXT,
    status TEXT,
    range_json TEXT,
    last_updated TIMESTAMP
);

-- Fee history
CREATE TABLE fee_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id TEXT,
    timestamp TIMESTAMP,
    fees_claimed REAL,
    action TEXT,  -- 'compound' or 'extract'
    tx_hash TEXT,
    FOREIGN KEY (position_id) REFERENCES positions(id)
);

-- User preferences
CREATE TABLE user_prefs (
    id INTEGER PRIMARY KEY,
    extract_threshold REAL DEFAULT 10.0,
    compound_split REAL DEFAULT 0.7,  -- 70% compound, 30% extract
    gas_threshold REAL DEFAULT 25.0,  -- gwei
    default_action TEXT DEFAULT 'auto',
    auto_enabled BOOLEAN DEFAULT TRUE
);
```

## Phase 1: Fee Monitoring MVP

### Deliverables
1. `fee_monitor.py` — track fees for LFJ positions
2. `position_state.json` — current position state
3. `fee_history.json` — historical fee data
4. Dashboard integration — new "Compound/Extract" tab

### API Endpoints (Internal)
```
GET  /api/positions              — list all positions
GET  /api/positions/:id          — get position details
GET  /api/positions/:id/fees     — get accumulated fees
POST /api/positions/:id/extract  — trigger extraction
POST /api/positions/:id/compound — trigger compounding
GET  /api/history                — fee history
GET  /api/prefs                  — user preferences
PUT  /api/prefs                  — update preferences
```

### Dashboard Tab Design
```
┌─────────────────────────────────────────────────────────┐
│  COMPOUND / EXTRACT                              [AUTO] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Position: AVAX/USDC on LFJ                            │
│  Status: In Range ✅                                    │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  Principal          Accumulated Fees                    │
│  ┌──────────────┐   ┌──────────────┐                   │
│  │  10.0 AVAX   │   │  0.42 AVAX   │                   │
│  │  250.0 USDC  │   │  10.50 USDC  │                   │
│  └──────────────┘   └──────────────┘                   │
│                                                         │
│  Fee Velocity: $1.67/day (steady)                      │
│  Days to $10: ~0.3 days                                │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  Mode: [Compound] [Extract] [Auto]                     │
│                                                         │
│  Auto Settings:                                         │
│  ├─ Extract threshold: $10.00                          │
│  ├─ Compound/Extract split: 70% / 30%                 │
│  ├─ Gas limit: 25 gwei                                 │
│  └─ Max slippage: 0.5%                                 │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  Last 5 Operations:                                     │
│  ├─ Jun 16 14:32 — Compound $8.20 USDC → +0.23 AVAX  │
│  ├─ Jun 15 09:15 — Extract $10.00 USDC                │
│  ├─ Jun 14 21:48 — Compound $7.50 USDC → +0.21 AVAX  │
│  ├─ Jun 13 16:22 — Extract $10.00 USDC                │
│  └─ Jun 12 11:05 — Compound $6.80 USDC → +0.19 AVAX  │
│                                                         │
│  [Extract Now]  [Compound Now]                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Testing Strategy

### Unit Tests
- `test_fee_monitor.py` — fee calculation, RPC mocking
- `test_decision_engine.py` — decision matrix, edge cases
- `test_executor.py` — extract/compound flows, error handling
- `test_state_manager.py` — persistence, queries

### Integration Tests
- Testnet deployment on Avalanche Fuji
- Mock LFJ position creation
- Execute compound/extract on testnet
- Verify fee claims work correctly

### Edge Cases
- Position goes out of range during compound
- Gas spikes during execution
- DEX contract call fails
- User cancels mid-operation
- Multiple extractions in rapid succession

## Security Considerations

1. **Private Key Management:** Never store keys in plaintext. Use environment variables or hardware wallet integration.
2. **Slippage Protection:** Always set max slippage parameter.
3. **Reentrancy:** Use checks-effects-interactions pattern.
4. **Approval Limits:** Request minimum necessary token approvals.
5. **User Confirmation:** Require confirmation for large extractions (> $100).

## Deployment

### Phase 1: Local Dashboard
- Fee monitoring only
- No execution (manual compound/extract)
- Dashboard tab shows accumulated fees

### Phase 2: Testnet Execution
- Execute on Avalanche Fuji
- Test compound/extract flows
- Gather performance data

### Phase 3: Mainnet (Controlled)
- Limited execution (user-approved)
- Monitoring and logging
- Gradual rollout

---

*Architecture version 1.0 — Jun 17, 2026*
