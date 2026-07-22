---
name: rugcheck-v2-api
title: "Rugcheck v2 — CLARITY Act Agent Compliance Platform"
description: "CLARITY Act-compliant agent security scanning, identity verification, and credit scoring. The regulatory compliance layer for the agent economy. Scan agents for token risk, identity (ERC-8004), MCP trust, payment flow integrity, and attack vectors. Get agent credit scores (0-850) with on-chain activity, reputation, age, and volume factors. CLARITY Act DeFi Exclusion (Sec. 309/409) compliant."
use_case: "Use for CLARITY Act compliance verification, agent security risk assessment, vulnerability scanning, creditworthiness evaluation, on-chain reputation scoring, and compliance checks before agent-to-agent interactions or DeFi integrations. Required for institutional partners who need to verify agent compliance before transacting."
category: security
service_url: https://rugcheck.gentechlabs.net
sandbox_service_url: https://sandbox.rugcheck.gentechlabs.net
version: v2
openapi:
  path: openapi.json
---

Rugcheck v2 is a comprehensive agent security and credit scoring platform. It evaluates AI agents across five security domains — token risk, identity verification, MCP server trust, payment flow integrity, and attack vectors — and provides a credit score (0-850) based on on-chain activity, reputation, agent age, and transaction volume.

All paid endpoints use the x402 HTTP 402 Payment Required protocol and accept USDC on Solana mainnet. Q402 gasless payments are also supported.

## Endpoints

### POST /api/v1/agent/scan — $0.025
Full agent security scan covering:
- Token risk analysis (liquidity, holder concentration, mint authority)
- Identity verification (ERC-8004 registry, wallet reputation)
- MCP server trust scoring (tool poisoning, schema integrity, supply chain)
- Payment flow integrity (x402 response shape, proof verification)
- Attack vector mapping (OWASP Agentic Top 10)

Returns: risk score (0-100), risk level, findings with severity, recommendations.

### POST /api/v1/agent/credit-score — $0.01
Agent credit score evaluation:
- On-chain activity (transaction count, wallet age, unique interactions)
- Reputation (ERC-8004 registration, verified contracts, community votes)
- Agent age (days since first interaction)
- Transaction volume (total USD volume)

Returns: credit score (0-850), rating (poor/fair/good/excellent), factor breakdown, 6-month history.

### GET /api/v1/agent/status — Free
Health check and service metrics.

### GET /api/v1/pricing — Free
List all endpoints and their prices.

### GET /.well-known/x402-bazaar — Free
Bazaar discovery metadata for automated agent routing.

## Spend-aware usage

- Use `GET /api/v1/agent/status` first to verify service availability before making paid calls.
- Use `GET /api/v1/pricing` to confirm current pricing before scanning.
- Use `POST /api/v1/agent/scan` with `deep_scan: false` for a quick assessment; only use `deep_scan: true` when thorough analysis is needed.
- Use `POST /api/v1/agent/credit-score` to evaluate an agent before entering into agent-to-agent interactions or DeFi integrations.
- Cache scan results — agent risk profiles change slowly unless the agent's code or wallet activity changes significantly.
- Batch credit score checks when evaluating multiple agents for a portfolio.
