# 👑 Jordan Action Items — 2026-07-20

## 🔴 Urgent — Needs Wallet/Decision

### #1 Subscription Hub — Needs Your Wallet Address
- subscribe.html deployed at gentechlabs.net/subscription-hub.html (HTTP 200 ✅)
- Q402 trial key live (2000 credits, 28 days left)
- **BLOCKER:** Need your wallet address to create Q402 payment requests for $3/$10/$25 USDC tiers
- **Action:** Share your wallet address → I wire the Q402 payment links in 5 min

### #11 Bankr $GENTECH Token Launch
- Launch $GENTECH on Bankr. 100B supply, 85% LP, 15% creator vesting.
- **Action:** Connect wallet to Bankr

### #12 Arc Programmable Money Hackathon — Agentic Treasury Submission
- Encode Club x Arc hackathon. Functional MVP needed.
- **Action:** Review scope, green-light submission

### #15 Arc x402 Gateway — Deploy to VPS
- **Built & tested:** 15/15 tests pass at `/root/repos/arc-x402-gateway/`
- Gateway health check: ✅ (simulation mode)
- **Needs:** Your wallet address (RECIPIENT_ADDRESS) + deploy to port 8088
- **Action:** Share wallet address → I deploy and test against Arc testnet RPC

## 🟡 PR Submissions (Need You to Fork & Submit)

### #5 Ripple XRPL — x402 Compliance Skill
- **Draft ready:** `10-Labs/xrpl-x402-compliance-skill.md` (9.3KB)
- **Target:** XRPLF/xrpl-dev-portal/.claude/skills/xrpl-skills/
- **Action:** Fork the repo, add the skill, submit PR

### #6 NEAR Protocol — x402 Integration PR
- **Draft ready:** `10-Labs/near-x402-integration-pr-draft.md` (2.8KB)
- **Target:** near-examples/near-intents-agent-example
- **Action:** Fork the repo, add x402-payment-flow.py example, submit PR

### #40 Dexter-DAO PR #36 — Submit Zod Validation
- **Code ready:** `/root/dexter-sdk-full/` — 229 lines, 3 files
- **Target:** Dexter-DAO/dexter-x402-sdk
- **Action:** Fork from web UI, push feat/zod-validation branch, open PR

### #37 x402 Compliance Scanner — Open PR #2905
- **Code committed:** ProtoJay4789:feat/compliance-scanner (+362 lines)
- **Target:** x402-foundation/x402
- **Action:** `gh pr create --repo x402-foundation/x402 --head ProtoJay4789:feat/compliance-scanner --base main --title 'feat(examples): add x402 compliance scanner'`
- **Note:** My GitHub API rate limit was exceeded — you may need to run this

## 🟢 New — OpenSpace Cloud Auth

### #37 OpenSpace — Upload x402 Compliance Skill to Hub
- **Skill prepared:** `/root/openspace-x402-skill/SKILL.md` (9.6KB)
- OpenSpace v2 installed (6.8k⭐, released Jul 16)
- **Action:** Run `openspace-cloud-auth bootstrap-agent-key --email <your-email>` in `/root/OpenSpace/`
- Then I can run: `openspace-upload-skill --skill-dir /root/openspace-x402-skill --visibility public`

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

## 📋 Quick Summary

| Priority | Item | What You Do | Est. Time |
|----------|------|-------------|-----------|
| 🔴 | Subscription Hub | Share wallet address | 5 min |
| 🔴 | Arc Gateway | Share wallet address | 2 min |
| 🔴 | Bankr $GENTECH | Connect wallet | 2 min |
| 🟡 | XRPL x402 Skill | Fork + submit PR | 10 min |
| 🟡 | NEAR x402 PR | Fork + submit PR | 10 min |
| 🟡 | Dexter-DAO Zod PR | Fork + submit PR | 5 min |
| 🟡 | x402 Compliance Scanner | Run gh pr create | 2 min |
| 🟢 | OpenSpace Cloud Auth | Run bootstrap command | 2 min |
| 🟢 | Sana, CMC, GenLayer | Signups | 15 min total |
