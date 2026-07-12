---
name: rugcheck-v2
operator: genTech-labs
description: High-speed Solana token risk scoring API with 11-factor rug detection analysis
version: "2.0"
network: solana
base_url: https://gentechlabs.net
pricing:
  model: per-request
  amount: "0.01"
  unit: USDC
  description: $0.01 USDC per token risk scan
tags:
  - security
  - risk-analysis
  - defi
endpoints:
  - path: /v1/score/{mint_address}
    method: GET
    description: 11-factor risk score for Solana tokens
    pricing: "0.01 USDC"
---

# rugcheck-v2

**Operator:** genTech-labs  
**Network:** Solana (USDC payments)  
**Base URL:** `https://gentechlabs.net`

## Overview

Enterprise-grade Solana token risk analysis with 11-factor scoring in <500ms.

## Endpoints

### GET /v1/score/{mint_address}

Retrieve comprehensive risk assessment for any Solana SPL token.

**Price:** $0.01 USDC per request.

#### Risk Factors (11-Dimension Model)
1. Holders Analysis — distribution legitimacy
2. LP Liquidity Assessment — pool depth & lock info
3. Honeypot Detection — sell-restriction mechanisms
4. Concentration Risk — ownership concentration
5. Mint Authority — can more tokens be minted?
6. Freeze Authority — can tokens be frozen?
7. Top Holder Distribution — whale concentration
8. Contract Verification — code verification status
9. Trading Activity Patterns — suspicious volume
10. Social/Deployment Signals — creator wallet history
11. On-chain Behavioral Analysis — anomalous patterns

## Status

Deployed and live at gentechlabs.net. x402 payment verification stubbed. Q402 integration pending. Pay-skills PR content ready.
