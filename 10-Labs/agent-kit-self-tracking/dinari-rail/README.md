# Dinari Rail — Tokenized Equity Leg (Agentic Treasury)

**Status:** ✅ Scaffolded (Labs, 2026-08-18) · ⏸ Waiting on Jordan's sandbox API key
**Greenlit:** Jordan, 2026-08-15 · **Full intel:** `Treasury/dinari-dshares-rail.md`

Wraps `dinari-api-sdk` v0.15+ into `dinari_rail.py` for the treasury's equity leg.

## Setup
```bash
pip install -r requirements.txt
# Sandbox keys from https://partners.dinari.com (Jordan, human-gated)
export DINARI_API_KEY_ID="..."
export DINARI_API_SECRET_KEY="..."
export DINARI_ENV="sandbox"   # or "production" — production key stays private
```

## Verify (no keys needed)
```bash
python3 dinari_rail.py self-test
```

## CLI
```bash
python3 dinari_rail.py entity                 # current entity
python3 dinari_rail.py accounts               # accounts for current entity
python3 dinari_rail.py portfolio <account>    # cash + portfolio + dividends + orders snapshot
python3 dinari_rail.py orders <account>
python3 dinari_rail.py quote <stock_id>
python3 dinari_rail.py mint <account>         # SANDBOX ONLY — mints mockUSD (no real money)
```

## Python API
```python
from dinari_rail import DinariRail
r = DinariRail()
r.market_buy(account_id, payment_amount=25.0, stock_id="AAPL")
r.limit_sell(account_id, asset_quantity=1.0, limit_price=250.0, stock_id="AAPL")
r.portfolio(account_id)
r.cash_balances(account_id)
r.dividends(account_id, start, end)
```

## Next (blocked on Jordan)
1. Partners signup + sandbox API key + entity/KYC.
2. `mint` faucet → validate reads + a market/limit order in sandbox.
3. Wire into the Agentic Treasury as the equity leg.
4. Revisit for production only after sandbox validated; keep production key private.
