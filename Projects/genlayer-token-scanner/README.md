# 🛡️ Token Scanner — GenLayer Intelligent Contract

> On-chain token risk assessment powered by GoPlus API + LLM analysis, running as a GenLayer Intelligent Contract.

## What It Does

Token Scanner is an **Intelligent Contract** that scans any EVM token address and returns a 0–100 risk score with labeled risk factors — all stored on-chain as a tamper-proof registry.

**What makes it unique:** The contract itself reads external APIs (GoPlus) and uses LLM analysis inside the contract logic — something impossible on traditional blockchains. This is GenLayer's "Intelligent Contract" superpower.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    USER / DAPP                               │
│         (calls scan_token with token address)                │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              GENLAYER INTELLIGENT CONTRACT                   │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  GoPlus API  │───▶│  LLM Analysis │───▶│  On-Chain    │  │
│  │  (web.get)   │    │  (exec_prompt)│    │  Storage     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  Risk Factors (11 weighted):                                │
│  • Honeypot (20%)     • Hidden Owner (10%)                  │
│  • Closed Source (10%) • Self-Destruct (8%)                  │
│  • Owner Change (10%)  • External Call (5%)                  │
│  • Take Liquidity (12%) • Is Proxy (5%)                     │
│  • Malicious (10%)     • Slippage (5%)                      │
│  • Blacklisted (5%)                                         │
│                                                              │
│  Output: risk_score (0-100), risk_level, risk_factors       │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **LLM-Powered Analysis**: Contract uses LLM to analyze GoPlus data and provide nuanced risk assessment
- **Deterministic Fallback**: If LLM analysis fails, falls back to weighted scoring
- **Batch Scanning**: Scan multiple tokens in a single transaction
- **On-Chain Registry**: All assessments stored with timestamps for audit trail
- **Quick Checks**: `is_safe()`, `is_honeypot()`, `get_risk_level()` for fast queries
- **Re-scan Support**: Track how a token's risk profile changes over time

## Risk Levels

| Level | Score Range | Meaning |
|-------|-------------|---------|
| 🟢 LOW | 80–100 | Safe token, established, no red flags |
| 🟡 MEDIUM | 60–79 | Some concerns, do your own research |
| 🟠 HIGH | 40–59 | Significant risk factors detected |
| 🔴 CRITICAL | 0–39 | Extreme danger, likely scam/honeypot |

## Contract Methods

### Write (State-Modifying)
- `scan_token(token_address)` — Scan a single token, store assessment
- `scan_batch(token_addresses)` — Scan multiple tokens at once

### Read (View Only)
- `get_assessment(token_address)` — Full assessment details
- `is_safe(token_address)` — Quick boolean check
- `is_honeypot(token_address)` — Quick honeypot check
- `get_risk_level(token_address)` — Risk level string
- `get_scan_count(token_address)` — How many times scanned
- `get_total_scans()` — Total scans by this contract
- `get_all_assessments()` — All stored assessments

## Setup

### Prerequisites
- [GenLayer Studio](https://docs.genlayer.com/developers/intelligent-contracts/tooling-setup) running locally or [hosted](https://studio.genlayer.com/)
- [GenLayer CLI](https://github.com/genlayerlabs/genlayer-cli) installed (`npm install -g genlayer`)

### Deploy

```bash
# Select network
genlayer network

# Deploy the contract
genlayer deploy
```

### Frontend

```bash
cd frontend
cp .env.example .env  # Fill in contract address
bun install
bun dev
```

### Test

```bash
# Install Python deps
pip install -r requirements.txt

# Run tests (requires GenLayer Studio)
gltest
```

## Architecture

```
contracts/
  token_scanner.py      # The Intelligent Contract
deploy/
  deployScript.ts       # GenLayer deployment script
tests/
  test_token_scanner.py # Integration tests
frontend/               # Next.js 15 dApp (optional)
```

## Why This Matters

Traditional smart contracts can't access external APIs or reason about data. GenLayer's Intelligent Contracts can. This token scanner demonstrates that capability:

1. **Reads GoPlus API** directly inside the contract (no oracle needed)
2. **Uses LLM** to analyze and reason about security data
3. **Stores results on-chain** with full audit trail
4. **Works for any EVM token** — not hardcoded to specific chains

This is the pattern for building AI-powered DeFi tools on GenLayer.

## Built By

**GenTech Labs** — [ProtoJay4789.github.io](https://ProtoJay4789.github.io)

Part of the GenLayer Builder Program — shipping working Intelligent Contract templates for the developer community.

## License

MIT
