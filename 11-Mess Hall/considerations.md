---
date: 2026-07-31
status: active
last-updated: 2026-07-31 20:07 ET
---

# 🧠 Considerations — Open Decisions

> Decision points requiring Jordan's input. Updated from brain snapshot context.

## 🚨 Urgent — DEADLINES APPROACHING

- [ ] 🚨 **Algorand Global x402 Challenge #82** — **⚠️ Deadline Jul 31 (DEADLINE TODAY).** $100K + 500K ALGO, leaderboard open. x402 gateway is multi-chain, config-only for ALGO. **Jordan: register at algorand.co/global-x402-challenge.**
- [ ] 🚨 **Arc Programmable Money Hackathon** — **Deadline Aug 9 (9 days, urgent).** Deploy x402 + Agent Wallet on Arc L1 (Encode Club, Agentic Economy track). **Jordan: (1) get testnet USDC from faucet.circle.com, (2) deploy x402.** *Queue shows PENDING — not passed.*

## 🔴 High Priority

- [ ] **Super Arcade Tennis #73 production deploy** — Code done and live on dev at arcade.gentechlabs.net. **Jordan: (a) deploy production build, (b) wire crypto payments?**
- [ ] **FrameForge #71** — AI Storyboard Service (previs pipeline). Spec at 09-Green Room/specs/. **Jordan: direction decision?** (Proven on KAGE film — ready to productize.)
- [ ] **Open Generative AI #77** — Self-host AI media studio (400+ models). **Jordan: go/no-go?**

## 🟡 Medium Priority

- [ ] **Syra Marketplace #76** — Register x402 services on syraa.fun. Easy win. **Jordan: go/no-go?**
- [ ] **Kite AI Global Hackathon #78** — ⚠️ DISPUTED — no source URL or prize. Needs Jordan to confirm removal.
- [ ] **AI Factory Hackathon #79** — lablab.ai × NativelyAI, Aug 3-10. **Jordan: register?**
- [ ] **GenTech Academy #81** — Initial repo live at `ProtoJay4789/gentech-academy`. Module 1 (AI on Grid) + Module 2 (Visual Pipeline) shipped. Module 3 (AI + 3D Engines / Kimi K3 content creation) next. **Jordan: direction — Blender MCP workflow or Kimi K3 frame critic loop?**
- [ ] **Kimi K3 Content Pipeline #82** — Frame critic + prompt engineer loop for Seedance. Test when wallet funded. Kimi K3 available via BlockRun ($3/$15 per M tokens, 1M context, vision). **Jordan: fund wallet → test frame consistency feedback loop.**
- [ ] **CockroachDB × AWS — Agentic Memory #83** — $8.75K, Aug 18 deadline. Persistent memory + MCP Server. **Jordan: register?**

## ✅ Recently Resolved

- **Web tools down** — RESOLVED. Agent Reach is the default web backend. Firecrawl no longer needed.
- **OKX AI Genesis Hackathon #72** — Deadline passed Jul 27. No registration received.
- **Keeperhub Agents Onchain #80** — Build phase started Jul 27. Pending Jordan go/no-go.
- **Celo Agentic Payments Hackathon #69** — Researched (Jul 24). Ready to execute on go-ahead.
- **MengTo Fork #75** — Shipped (Jul 25).
- **x402 Gateway v7.0.0** — Deployed and verified.
- **CLARITY Act Compliance** — Badges live on all repos.
- **Stale PRs** — All 10 PRs confirmed still open (no action needed from us).

## 🆕 DeepSeek V4-Flash Official API — LIVE in public beta (Jul 31, 2026)

**Source:** [DeepSeek announcement tweet](https://x.com/i/status/2083084415157022911) — 2.46M views, 16K likes. Docs: api-docs.deepseek.com

### What changed
- Official API live at api.deepseek.com, native **Responses API** support, fully adapted for **Codex**
- Agent capabilities massively upgraded vs V4-Pro-Preview (Flash-0731 vs Pro-Preview):
  - DeepSWE: **54.4 vs 12.8** (4.2x)
  - Terminal Bench 2.1: **82.7 vs 72.1**
  - Cybergym: **76.7 vs 52.7**
  - Toolathlon-Verified: **70.3 vs 55.9**
  - Agents' Last Exam: **25.2 vs 16.5**
  - AutomationBench: **25.1 vs 12.8**
  - DSBench-FullStack: **68.7 vs 41.8**
  - DSBench-Hard: **59.6 vs 31.1**
- DeepSeek docs now list **Hermes Agent** as an official agent integration (install → setup → select DeepSeek provider)

### Why this matters to us
- We already run on `deepseek/deepseek-v4-flash` (Nous provider) — this is a massive capability jump for the same tier we use daily
- Our DEV tier (develop-and-verify pipeline) is DeepSeek V4 Flash — stronger agentic coding = faster build queue
- **Decision to consider:** switch from Nous provider to direct DeepSeek API (api.deepseek.com, sk- key) for lower cost / official support? Also evaluate Z.AI / Ollama Cloud in the same pass.
- Codex CLI integration now officially supported — our codex delegation path gets a free upgrade

**Status:** ☑️ tracked — **Jordan: evaluate provider switch vs current Nous setup (open question)**

## 🔗 Related

- [[brain-snapshot-2026-07-28]] — Full context snapshot
- [[context-weight]] — Auto-generated project overview
- [[build_queue.json]] — v52, 30 items
