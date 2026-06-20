# Agent Kit × Q402 Payment Module

**Status:** Phase 2 — SDK Integration
**Date:** June 20, 2026

## What This Is

A payment module for Agent Kit that wraps Q402's gasless payment infrastructure with:
- Policy enforcement (spending limits, approved recipients)
- Audit trail (every payment logged with Trust Receipt)
- Multi-chain support (11 EVM chains)
- Receipt verification (cryptographic proof of settlement)

## Architecture

```
Agent Kit Payment Request
        │
        ▼
┌───────────────────┐
│  Policy Engine     │ ← spending limits, approved recipients
│  (AAE Hooks)       │
└────────┬──────────┘
         │ approved
         ▼
┌───────────────────┐
│  Q402 Payment Rail │ ← gasless USDC/USDT settlement
│  (MCP: q402_pay)  │
└────────┬──────────┘
         │ settled
         ▼
┌───────────────────┐
│  Trust Receipt     │ ← cryptographic proof
│  (on-chain verify) │
└────────┬──────────┘
         │ verified
         ▼
┌───────────────────┐
│  Audit Trail       │ ← logged to vault
│  (immutable record)│
└───────────────────┘
```

## Supported Operations

| Operation | Q402 Tool | Agent Kit Wrapper |
|-----------|-----------|-------------------|
| Single payment | `q402_pay` | `agent_pay()` |
| Batch payout | `q402_batch_pay` | `agent_batch_pay()` |
| Recurring payment | `q402_schedule` | `agent_recurring()` |
| Yield routing | `q402_aave_deposit` | `agent_yield()` |
| Cross-chain bridge | `q402_ccip_bridge` | `agent_bridge()` |
| Balance check | `q402_balance` | `agent_balance()` |
| Receipt verify | `q402_verify_receipt` | `agent_verify()` |

## Supported Chains

BNB, Ethereum, Avalanche, Arbitrum, Base, Monad, Mantle, Scroll, Injective, X Layer, Stable

## Tokens

USDC, USDT, RLUSD

## Pricing

| Plan | TXs | Cost |
|------|-----|------|
| Free | 2K/30 days (BNB only) | $0 |
| Starter | 500 TXs | $29/mo |
| Pro | 10K TXs | $149/mo |
| Scale | 50K TXs | $449/mo |

## Files

- `payment_module.py` — Core payment logic with policy enforcement
- `audit_trail.py` — Transaction logging and receipt verification
- `config.yaml` — Agent Kit payment configuration
- `test_payment.py` — Unit tests
