# GenTech Receipts — x402 Spending Tracker

> Track x402 payment volume across agents, endpoints, and chains.
> See who's paying, what they're buying, and how much you're earning.

## What

GenTech Receipts is a spending tracker dashboard for x402 payments. It monitors your x402 gateway, aggregates transaction data, and shows you:

- **Per-agent spend** — how much each agent/caller has spent
- **Per-endpoint revenue** — which endpoints earn the most
- **Daily/weekly/monthly totals** — time-based revenue breakdowns
- **Receipt verification** — validate that payments were legitimate

## How it works

```
x402 Gateway ──► Transaction Log ──► Receipt Tracker ──► Dashboard
     │                                    │
     │  Every payment creates             │  Parses and
     │  an on-chain receipt               │  aggregates data
```

### 1. Transaction Sources

The tracker supports three data sources:

| Source | Description | Setup |
|--------|-------------|-------|
| **x402 Gateway API** | Query the gateway for recent payments | `X402_API_KEY` in env |
| **Blockchain RPC** | Read x402 contract events directly | RPC URL per chain |
| **Manual CSV** | Import transaction exports | CSV file path |

### 2. Metrics Tracked

| Metric | Description |
|--------|-------------|
| Total volume (USDC) | Sum of all payments |
| Unique callers | Distinct wallet addresses |
| Per-endpoint breakdown | Revenue by API endpoint |
| Per-chain breakdown | Volume by chain (Base/Polygon/Arbitrum) |
| Daily active callers | Unique callers per day |
| Average payment size | Mean transaction value |
| Receipt validity % | What % of receipts pass verification |

### 3. Receipt Verification

Each x402 payment generates an on-chain receipt. The tracker verifies:

1. **Receipt exists** — transaction hash is valid on the claimed chain
2. **Amount matches** — paid amount matches the endpoint price
3. **Recipient matches** — payment went to the gateway operator address
4. **Timestamp is current** — payment was within the last N blocks
5. **No double-spend** — receipt hasn't been used for another call

## Quick Start

```bash
# 1. Set up environment
cp .env.template .env
# Edit .env with your X402_API_KEY

# 2. Run the tracker
python scripts/tracker.py --days 7

# 3. View the dashboard
python scripts/dashboard.py
# Opens http://localhost:8080
```

## CLI Usage

```bash
# Daily summary
python scripts/tracker.py --summary daily

# Weekly report
python scripts/tracker.py --summary weekly --format json

# Receipt verification
python scripts/tracker.py --verify --tx 0xabc...123

# Export to CSV
python scripts/tracker.py --export receipts.csv

# Live view (refresh every 30s)
python scripts/tracker.py --watch
```

## Dashboard

The dashboard is a single HTML file that renders transaction data.
Open `dashboard/index.html` in a browser or serve it:

```bash
python -m http.server 8080 --directory dashboard/
```

## API (if running in agent mode)

```bash
# Get total volume
curl http://localhost:8081/api/volume

# Get per-endpoint breakdown
curl http://localhost:8081/api/breakdown/endpoint

# Verify a receipt
curl -X POST http://localhost:8081/api/verify \
  -H "Content-Type: application/json" \
  -d '{"tx_hash": "0xabc...123", "chain": "base"}'
```

## Files

```
10-Labs/gentech-receipts/
├── SKILL.md              # This file
├── .env.template         # API keys template
├── scripts/
│   ├── tracker.py        # Main tracker script
│   └── dashboard.py      # Simple API server
└── dashboard/
    └── index.html        # Dashboard HTML
```
