# Cursor Directory Submission — GenTech Labs x402 Gateway
**Ready to paste at https://cursor.directory/plugins/new**

---

## Plugin Name
`GenTech Gateway`

## Plugin Avatar
![GenTech Gateway Logo](https://v3b.fal.media/files/b/0aa36341/0VxqRLvbRUMcbKxa3LWR4_xNkoeBaq.png)

## Description
x402 pay-per-call gateway for AI agents — 16 endpoints across 5 chains. Agents discover APIs, pay with USDC via x402, and use them directly from Cursor. Built-in compliance scanner, wallet management, and treasury dashboard. No API keys, no subscriptions, no human approval.

## Source URL
https://github.com/ProtoJay4789/x402-gateway

## Tags
x402, payments, usdc, base, ethereum, solana, gateway, compliance, mcp, agent

---

## Rules (paste into rules field)

Rule name: `gentech-spend-safety`

```
gentech-spend-safety:

- The `gen_pay`, `gen_batch_pay`, and `gen_withdraw` tools spend real USDC from the user's wallet. Before calling any of them, tell the user the exact amount and destination and get explicit approval in this conversation. Never spend unprompted.
- Free endpoints (gen_status, gen_balance, gen_quote, gen_scan, gen_report, gen_discover, gen_endpoints) can be used freely to answer questions.
- Before any payment, check the destination address is valid and verified. Never send to an unverified address without user confirmation.
- If a payment fails for insufficient funds or rate limits, surface the error to the user and stop. Do not retry, split amounts, or use alternative paths without approval.
- Never re-run a paid scan on the same target while a scan is still in progress — poll gen_report instead.
- All x402 payments settle on-chain. Inform users of the chain and estimated settlement time before executing.
```

---

## MCP Servers (paste into MCP field)

MCP name: `gentech-gateway`

```json
{
  "name": "gentech-gateway",
  "type": "streamable-http",
  "url": "https://protojay4789.github.io/gateway/mcp",
  "description": "x402 compliance gateway for AI agents",
  "tools": [
    "gen_discover",
    "gen_endpoints",
    "gen_status",
    "gen_balance",
    "gen_quote",
    "gen_scan",
    "gen_report",
    "gen_pay",
    "gen_batch_pay",
    "gen_withdraw"
  ]
}
```

---

## Skills (paste descriptions into skills field)

### 1. Skill name: `x402-payment`
```
Make x402 payments from Cursor. Detect 402 Payment Required responses, sign payment proofs, retry requests. Supports USDC on Base, Ethereum, Arbitrum, Solana, and BNB Chain.
```

### 2. Skill name: `compliance-scanner`
```
Scan any API endpoint or smart contract for x402 compliance. Checks for valid payment headers, correct 402 response format, ERC-8004 identity verification, and OWASP Agentic Top 10 vulnerabilities.
```

### 3. Skill name: `treasury-dashboard`
```
Query the agentic treasury — check wallet balances across chains, view transaction history, track monthly spend, manage yield positions, and generate spending reports.
```

### 4. Skill name: `api-monetizer`
```
Wrap any existing API endpoint with x402 payment support. Generate the middleware, validate the configuration, deploy to the gateway, and register on x402-aware marketplaces.
```
