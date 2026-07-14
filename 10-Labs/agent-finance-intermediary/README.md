# Agent Finance Intermediary — BNPL MVP

**Status:** 🟢 Building (Week 1-2)
**Stack:** Solidity (BNPL Escrow) + Python (Credit Scoring + Risk Engine)
**Deploy Target:** Base (USDC native)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Finance MVP                      │
├─────────────────┬───────────────────┬───────────────────┤
│  BNPLEscrow.sol  │ credit_scoring.py │  risk_engine.py   │
│  (Solidity)      │  (Python API)     │  (Python API)     │
│                  │                   │                   │
│  4-installment   │  ERC-8004 →       │  Portfolio TVL →  │
│  escrow contract │  Credit Score     │  Risk Score       │
│                  │  (300-850)        │  (0-100)          │
└─────────────────┴───────────────────┴───────────────────┘
```

## Components

### 1. BNPLEscrow.sol — Escrow Contract
- **File:** `contracts/BNPLEscrow.sol`
- **Flow:** Merchant deposits full USDC → 4 installments (weekly) → User repays → Merchant released
- **Default:** After grace period, remaining escrow returned to merchant
- **Tests:** `test/BNPLEscrow.t.sol` (5 test cases)

### 2. Credit Scoring API
- **File:** `api/credit_scoring.py`
- **Input:** Agent profile (registrations, months active, payment history, portfolio)
- **Output:** Score (300-850), risk tier, max credit line
- **Factors:** Payment history (±8/-25), portfolio health (0-150), age (0-120), reputation (×3)

### 3. Risk Engine API
- **File:** `api/risk_engine.py`
- **Input:** Portfolio positions (TVL, trend, yield, audit status)
- **Output:** Composite risk score (0-100), tier, recommended credit
- **Factors:** TVL health, yield stability, diversification, exposure risk, audit quality

## Usage

```bash
# Credit scoring
echo '{"agent_id": "agent-001", "registration_count": 5, "months_active": 12, "on_time_payments": 10, "defaults": 0, "portfolio_tvl": 25000, "tvl_trend_30d": 0.1, "yield_stability": 0.8, "protocol_count": 6}' | python api/credit_scoring.py

# Risk assessment
echo '{"agent_id": "whale-001", "positions": [{"name": "Aave", "chain": "ethereum", "tvl_usdc": 20000, "tvl_trend_30d": 0.05, "yield_apy": 4.5, "yield_volatility": 0.15, "is_audited": true, "has_insurance": true}]}' | python api/risk_engine.py
```

## Test Results

```
# Credit Scoring
agent-001 (whale, diversified): 755 — Prime       → $10,000 max credit
agent-002 (new, $500 TVL):      418 — Deep Subprime → $100 max credit
agent-003 (moderate, 1 default): 540 — Subprime    → $1,000 max credit

# Risk Engine
whale-001 ($58K TVL, 5 protocols):  80/100 — Low Risk     → $23,200 credit
degen-002 ($500 TVL, 1 protocol):    16/100 — High Risk    → $40 credit
balanced-003 ($8K TVL, 2 protocols): 60/100 — Medium Risk → $2,400 credit
```

## Next Steps

1. [ ] Deploy BNPLEscrow to Base testnet (need wallet with test USDC)
2. [ ] Deploy credit scoring + risk engine as Cloudflare Workers
3. [ ] Wire up x402 payment flow (receive → split → escrow)
4. [ ] Beta with 10 users (Atelier agents)
5. [ ] Track defaults + iterate risk model

## Revenue Model

| Stream | Take Rate | Est. Annual |
|--------|-----------|-------------|
| Transaction fees | 4% | $4.8K-48K |
| Credit interest | 18% APR | $1.8K-18K |
| **Total** | | **$6.6K-66K** |
