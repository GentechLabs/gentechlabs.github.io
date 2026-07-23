# Agent Kit × Q402 — Payment Module

**Status:** ✅ Working | **Tests:** 36/36 passing

Gasless payments for AI agents. Agents pay for APIs, get paid for serving them, and every transaction gets an audit trail with identity enforcement.

## Architecture

```
Agent A  →  Enforcement  →  Q402 Payment  →  Trust Receipt  →  Audit Trail  →  API Response
                              ↕                              ↕
                         Policy Check                  Receipt Verify
                         Identity Check                Immutable Log
                         Rate Limiting                 Compliance Query
```

## Modules

| Module | Purpose | File |
|--------|---------|------|
| **PaymentModule** | Spending — policy enforcement, limits, audit | `payment_module.py` |
| **RevenueModule** | Receiving — receipt verification, revenue tracking | `revenue_module.py` |
| **Gateway** | Unified — ties spending + revenue into one API | `gateway.py` |
| **AuditTrail** | Post-settlement — receipt verification, immutable log | `audit_trail.py` |
| **EnforcementEngine** | Pre-settlement — identity, policy, rate limiting | `enforcement.py` |

## Quick Start

```python
from gateway import AgentPaymentGateway

gateway = AgentPaymentGateway()

# Register your API for sale
gateway.register_api(
    path="/v1/score/{mint}",
    price_usd=0.01,
    description="Token risk scoring"
)

# Register an agent identity
gateway.register_agent(
    address="0x1234",
    chain="base",
    credit_score=500,
    reputation=0.8
)

# Run enforcement before payment
result = gateway.enforce_payment(
    agent_id="0x1234",
    amount=5.0,
    endpoint="/v1/score"
)

# Verify incoming payment
result = gateway.handle_request(
    receipt_id="rct_abc123",
    endpoint="/v1/score/{mint}",
    payer="0x1234"
)

# Record settlement to audit trail
gateway.record_settlement(
    payment_id="pay_001",
    receipt_id="rct_abc123",
    receipt_data={"chain": "base", "amount": 5.0, "tx_hash": "0x..."},
    chain="base", amount=5.0,
    payer="0x1234", provider="0x5678",
    endpoint="/v1/score"
)

# Query audit trail
entries = gateway.query_audit(payer="0x1234")

# Check receipt status
status = gateway.check_receipt("rct_abc123")

# Daily report
summary = gateway.daily_summary()
```

## Enforcement (Pre-Settlement)

Every payment goes through enforcement BEFORE touching Q402:

1. **Identity Check** — Agent must be registered with valid ERC-8004 identity
2. **Credit Score** — Minimum credit score threshold (default: 300)
3. **Reputation** — Minimum reputation score (default: 0.1)
4. **Policy Compliance** — Spending limits, blocked chains/tokens
5. **Rate Limiting** — Per-minute and per-hour transaction caps
6. **KYC Warning** — Flag large transactions for compliance

## Audit Trail (Post-Settlement)

After Q402 settles, every receipt gets:

1. **Format Validation** — Chain, amount, address, tx_hash verification
2. **Payment Linking** — Receipt linked to original payment ID
3. **Immutable Log** — Append-only JSONL, entries never modified
4. **Query API** — Filter by payer, provider, endpoint, date, amount
5. **Flagging** — System or manual flags for suspicious entries

## Policy Controls

- Daily spending limits
- Per-transaction caps
- Chain/token approval/block lists
- Recipient allow/block lists
- Memo requirements
- Rate limiting per payer
- Identity verification requirements
- Credit score thresholds

## Q402 Integration

Uses Q402 MCP tools for actual settlement:
- `q402_pay` — send payments
- `q402_batch_pay` — batch payouts
- `q402_balance` — check balances
- `q402_verify_receipt` — verify receipts
- `q402_schedule` — recurring payments

The enforcement module validates BEFORE calling Q402.
The audit trail records AFTER Q402 confirms settlement.

## Config

Edit `config.yaml` to set limits, approved chains/tokens, and endpoints.

## Tests

```bash
python3 test_payment.py      # Policy + limits + audit (6 tests)
python3 test_revenue.py      # Revenue tracking + double-spend (5 tests)
python3 test_gateway.py      # Full integration + enforcement + audit (6 tests)
python3 test_audit_trail.py  # Receipt verification + immutable log (7 tests)
python3 test_enforcement.py  # Identity + policy + rate limiting (12 tests)
```

## File Structure

```
agent-kit-q402/
├── payment_module.py     # Spending — policy enforcement
├── revenue_module.py     # Receiving — receipt verification
├── gateway.py            # Unified gateway (spending + revenue + enforcement + audit)
├── audit_trail.py        # Post-settlement receipt verification + immutable log
├── enforcement.py        # Pre-settlement identity + policy enforcement
├── config.yaml           # Policy and limits configuration
├── test_payment.py       # Payment module tests (6)
├── test_revenue.py       # Revenue module tests (5)
├── test_gateway.py       # Gateway integration tests (6)
├── test_audit_trail.py   # Audit trail tests (7)
├── test_enforcement.py   # Enforcement tests (12)
└── README.md             # This file
```
