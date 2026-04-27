# Birdeye Token Radar 🛰️

Real-time Solana new token discovery with AI-powered safety scoring via Birdeye Data Services.

## What It Does

1. **Discovers** new token listings on Solana via Birdeye API
2. **Scores** each token's safety (holder concentration, mint authority, LP locks)
3. **Alerts** via Telegram with formatted risk assessments
4. **Pays** per-request via x402 — no subscription needed ($0.003/call)

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Set your Birdeye API key
export BIRDEYE_API_KEY="your_key_here"

# Run once
python src/radar.py

# Run continuous monitoring (checks every 60s)
python src/radar.py --watch
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Birdeye API    │────▶│  Safety Scorer   │────▶│  Telegram Alert │
│  /new_listing   │     │  /token_security │     │  Bot            │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
   New tokens           Risk score 0-100          Formatted message
   every 60s            + flags                   with links
```

## Safety Scoring

| Factor | Weight | Source |
|--------|--------|--------|
| Mint authority revoked | 25 pts | `token_security` |
| Freeze authority revoked | 15 pts | `token_security` |
| LP locked/burned | 25 pts | `token_security` |
| Top 10 holder % | 20 pts | `token_security` |
| Creation age | 15 pts | `new_listing` |

**Score interpretation:**
- 🟢 80-100: Low risk
- 🟡 50-79: Medium risk — review carefully
- 🔴 0-49: High risk — proceed with caution

## Birdeye API Endpoints Used

- `GET /v2/tokens/new_listing` — discover new tokens
- `GET /defi/token_security` — safety signals per token
- `GET /defi/v3/token/overview` — price/volume context

## Build in Public

This project is part of the [Birdeye Data 4-Week BIP Competition](https://superteam.fun/earn/listing/birdeye-data-4-week-bip-competition-sprint-1).

**Tags:** `@birdeye_data` `#BirdeyeAPI` `#Solana` `#AIagents`

## License

MIT
