# 👑 Jordan Action Items — 2026-07-20

## ✅ Shipped This Session (1 Gentech Item)

| Item | What Was Built | Tests |
|------|---------------|-------|
| #39 Dexter-DAO SDK Integration — Phase A | Tab middleware for Arc x402 gateway (Python adaptation of @dexterai/x402 tab pattern). src/tab.py, tab_middleware.py, tab_or_exact.py, helpers.py. Supports X-Tab-Voucher streaming + x402 one-shot. Critical security bug fixed. | 57/57 |

## 🔴 Urgent — Needs Wallet/Decision

### #1 Subscription Hub — Needs Your Wallet Address
- subscribe.html deployed at gentechlabs.net/subscription-hub.html
- Q402 trial key live (2000 credits, 28 days left)
- **BLOCKER:** Need your wallet address to create Q402 payment requests for $3/$10/$25 USDC tiers
- **Action:** Share your wallet address → I wire the Q402 payment links

### #11 Bankr $GENTECH Token Launch
- Launch $GENTECH on Bankr. 100B supply, 85% LP, 15% creator vesting.
- **Action:** Connect wallet to Bankr

### #15 Arc x402 Gateway — Deploy to VPS
- **Built & tested:** 57/57 tests at `/root/repos/arc-x402-gateway/`
- **NEW:** Tab streaming support added (X-Tab-Voucher header)
- **Needs:** Your wallet address (RECIPIENT_ADDRESS) + deploy to port 8088
- **Action:** Share wallet address → I deploy and test against Arc testnet RPC

## 🟡 PR Submissions (Need You to Fork & Submit)

### #37 x402 Compliance Scanner PR #2905
- Code committed to ProtoJay4789:feat/compliance-scanner (+362 lines)
- **BLOCKED:** `gh repo fork x402-foundation/x402` returns 403 — cannot fork
- **Action:** Manually fork x402-foundation/x402 on GitHub, then I submit the PR

### #2 Pay-Skills PR #154
- Fork ProtoJay4789/pay-skills doesn't exist (404)
- **Action:** Re-fork solana-foundation/pay-skills on GitHub

### #5 Ripple XRPL — x402 Compliance Skill
- Draft ready: `10-Labs/xrpl-x402-compliance-skill.md` (9.3KB)
- **Target:** XRPLF/xrpl-dev-portal/.claude/skills/xrpl-skills/
- **Action:** Fork the repo, add the skill, submit PR

### #6 NEAR Protocol — x402 Integration PR
- Draft ready: `10-Labs/near-x402-integration-pr-draft.md` (2.8KB)
- **Target:** near-examples/near-intents-agent-example
- **Action:** Fork the repo, add x402-payment-flow.py example, submit PR

### #40 Dexter-DAO PR #36 — Zod Validation
- Code committed to ProtoJay4789:feat/compliance-scanner (+362 lines)
- **Action:** Fork dexterai/x402, submit PR

## 🟢 Needs Signup/Account

### #7 Cloudflare Gateway — x402 Playground
- You're on the Cloudflare Gateway waitlist
- **Action:** When approved, let me know → deploy x402 on Workers

### #32 GenTech Bank — Sana Account
- **Action:** Create account at sana.bot/gateway → share API credentials

### #33 CMC Labs Accelerator Application
- Draft application narrative ready
- **Action:** Review and submit

### #34 GenLayer — Builder Points
- **Action:** Create account, grab testnet GEN, deploy Intelligent Contract

### #49 Robinhood Agentic Account
- **Action:** Open Robinhood Agentic account (US-based, desktop only)

### #50 Swarms Marketplace — Update Agent Listing
- **Action:** Log into swarms.world, edit agent 72be9677-82f7-404b-b52f-86ab36dcf6c4

### #51 Atelier Marketplace — Review Agent Profile
- **Action:** Log into useatelier.ai, review current agent profile

### #52 OKX AI Marketplace — Review ASP Listing
- **Action:** Log into OKX AI dev portal, review A2MCP ASP listing

## 📋 Quick Summary

| Priority | Item | What You Do | Est. Time |
|----------|------|-------------|-----------|
| 🔴 | Subscription Hub | Share wallet address | 5 min |
| 🔴 | Arc Gateway | Share wallet address | 2 min |
| 🔴 | Bankr $GENTECH | Connect wallet | 2 min |
| 🟡 | x402 Compliance PR | Fork x402-foundation/x402 | 2 min |
| 🟡 | Pay-Skills PR | Fork solana-foundation/pay-skills | 2 min |
| 🟡 | XRPL x402 Skill | Fork + submit PR | 10 min |
| 🟡 | NEAR x402 PR | Fork + submit PR | 10 min |
| 🟡 | Dexter-DAO PR | Fork dexterai/x402 | 5 min |
| 🟢 | Signups (Sana, CMC, GenLayer, Robinhood, Swarms, Atelier, OKX) | Various | 30 min total |
