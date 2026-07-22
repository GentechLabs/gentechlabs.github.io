# Rugcheck v2 API — Pay-Skills Catalog Submission

**Provider:** `gentechlabs/rugcheck-v2-api`
**Author:** GenTech Labs
**Date:** 2026-07-22
**AI Disclosure:** This submission was generated with AI assistance (Hermes Agent / DeepSeek V4 Flash). Code was reviewed and verified against the pay-skills CONTRIBUTING.md and x402 Python SDK v2 API before submission.

---

## What this PR adds

A new pay-skills provider entry for **Rugcheck v2 API** — a comprehensive agent security scanning and credit scoring platform with x402/Q402 payment middleware.

### Key features

- **Agent Security Scanning** — POST `/api/v1/agent/scan` ($0.025) evaluates agents across 5 security domains: token risk, identity, MCP trust, payment flow, and attack vectors
- **Agent Credit Scoring** — POST `/api/v1/agent/credit-score` ($0.01) returns a 0-850 credit score with on-chain activity, reputation, age, and volume factors
- **x402 Payment Middleware** — Multi-facilitator (CDP + x402.org), multi-chain (EVM + Solana) payment support
- **Q402 Gasless Payments** — Optional Q402 integration for gasless USDC payments
- **Bazaar Discovery** — `/.well-known/x402-bazaar` for automated agent routing
- **OpenAPI 3.1 Spec** — Full OpenAPI document committed as sidecar

### Files

```
providers/gentechlabs/rugcheck-v2-api/
├── PAY.md          # Provider metadata and documentation
├── openapi.json    # OpenAPI 3.1 specification
└── README.md       # (this file — setup instructions)
```

### Payment compatibility

| Endpoint | Method | Price | Chain | Protocol |
|----------|--------|-------|-------|----------|
| `/api/v1/agent/scan` | POST | $0.025 | Solana mainnet | x402 + Q402 |
| `/api/v1/agent/credit-score` | POST | $0.01 | Solana mainnet | x402 + Q402 |
| `/api/v1/agent/status` | GET | Free | — | — |
| `/api/v1/pricing` | GET | Free | — | — |
| `/.well-known/x402-bazaar` | GET | Free | — | — |

### Verification

```bash
# Validate the provider entry
pay catalog check providers/gentechlabs/rugcheck-v2-api/PAY.md

# Or with npx
npx @solana/pay catalog check providers/gentechlabs/rugcheck-v2-api/PAY.md
```

### Why this matters

As AI agents proliferate, agent-to-agent security and trust are critical blind spots. Rugcheck v2 fills this gap by providing:
1. **Security scanning** — catch vulnerabilities before agent-to-agent interactions
2. **Credit scoring** — evaluate agent trustworthiness for DeFi and commerce
3. **x402 micropayments** — pay-as-you-go model aligned with agent economics

---

## Submission instructions

1. Fork https://github.com/solana-foundation/pay-skills
2. Copy `10-Labs/rugcheck-v2-api/` to `providers/gentechlabs/rugcheck-v2-api/`
3. Run: `pay catalog check providers/gentechlabs/rugcheck-v2-api/PAY.md`
4. Open a PR with title: `feat: add gentechlabs/rugcheck-v2-api security and credit scoring provider`
5. PR body: paste this README
