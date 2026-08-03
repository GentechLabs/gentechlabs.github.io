---
date: 2026-08-02
status: active
last-updated: 2026-08-02 00:07 ET
---

# 🧠 Considerations — Open Decisions

> Decision points requiring Jordan's input. Updated from brain snapshot context.

## 🚨 Urgent — DEADLINES APPROACHING

- [ ] 🚨 **Algorand Global x402 Challenge #82** — **⚠️ DEADLINE PASSED Jul 31.** $100K + 500K ALGO. No record of registration on file. **Jordan: confirm if registered / still eligible for late leaderboard, or mark dead.**
- [ ] 🚨 **Arc Programmable Money Hackathon** — **Deadline Aug 9 (7 days, urgent).** Deploy x402 + Agent Wallet on Arc L1 (Encode Club, Agentic Economy track). **Jordan: (1) get testnet USDC from faucet.circle.com, (2) deploy x402.** *Queue shows PENDING — not passed.*
- [ ] 🚨 **AI Factory Hackathon #79** — **⚠️ STARTS TOMORROW (Aug 3, 1 day).** lablab.ai × NativelyAI, Aug 3-10. **Jordan: register?** *(Elevated from Medium this EOD run — day advanced.)*

## 🔴 High Priority

- [ ] **Super Arcade Tennis #73 production deploy** — Code done and live on dev at arcade.gentechlabs.net. **Jordan: (a) deploy production build, (b) wire crypto payments?**
- [ ] **FrameForge #71** — AI Storyboard Service (previs pipeline). Spec at 09-Green Room/specs/. **Jordan: direction decision?** (Proven on KAGE film — ready to productize.)
- [ ] **Open Generative AI #77** — Self-host AI media studio (400+ models). **Jordan: go/no-go?**

## 🟡 Medium Priority

- [ ] **Narrative Rotation cron — CMC key not loaded in pre-run** — The weekly `narrative-rotation.py` pre-run hit HTTP 401 on every CoinMarketCap fetch (wrote all-zero JSON: BTC $0.00, all narratives "Cooling" score +0.0). Root cause: the inline pre-run step doesn't read `/root/.hermes/scripts/cmc_config.json` (which holds a working `coinmarketcap_api_key`). The 2026-08-02 run was rebuilt manually from the CMC Pro endpoint and pushed. **Jordan: confirm the cron pre-run is fixed to load the CMC key (or switch to CoinGecko free API) so next week's run is real, not zeros.**
- [ ] **Syra Marketplace #76** — Register x402 services on syraa.fun. Easy win. **Jordan: go/no-go?**
- [ ] **Kite AI Global Hackathon #78** — ⚠️ DISPUTED — no source URL or prize. Needs Jordan to confirm removal.
- [ ] **AI Factory Hackathon #79** — lablab.ai × NativelyAI, Aug 3-10. **Jordan: register?**
- [ ] **GenTech Academy #81** — Initial repo live at `ProtoJay4789/gentech-academy`. Module 1 (AI on Grid) + Module 2 (Visual Pipeline) shipped. Module 3 (AI + 3D Engines / Kimi K3 content creation) next. **Jordan: direction — Blender MCP workflow or Kimi K3 frame critic loop?**
- [ ] **Kimi K3 Content Pipeline #82** — Frame critic + prompt engineer loop for Seedance. Test when wallet funded. Kimi K3 available via BlockRun ($3/$15 per M tokens, 1M context, vision). **Jordan: fund wallet → test frame consistency feedback loop.**
- [ ] **CockroachDB × AWS — Agentic Memory #83** — $8.75K, Aug 18 deadline. Persistent memory + MCP Server. **Jordan: register?**

- [ ] **Bug Bounties Comeback?** — We stopped because AI agents couldn't produce solid PoCs ("proof of LOC"). open·kritt (Kritt-ai, Blockian team) now handles that: scan agents run as root in disposable containers (compile/run tests/build exploits) and post-scripts emit PoCs via `_reserved_poc` + reports. **Jordan: test on our own repos first (build-queue #34), then decide if we point it at Immunefi targets for bounty revenue.**

## 🎓 Learning Track — AWS + Cyfrin Updraft (Aug 3)

Jordan's commitment (more free time this week due to reduced work hours). Work BOTH in parallel alongside job apps + hackathons. **Check in Sunday (Aug 9) on progress for both.**

- [ ] **AWS Solutions Architect Associate (SAA-C03)** — Amazon subsidizes the exam. 2-3 week focused sprint. Credential value for the "cloud engineering" half. Not a daily-tooling shift (we run VPS/nginx/Cloudflare) — a resume + credential unlock.
- [ ] **Cyfrin Updraft — Solidity/security-audit track** (Patrick Collins). Deep multi-week curriculum. Highest differentiation value — unlocks paid smart-contract audits ($1K-5K/audit) via the x402 gateway. Complements our `solidity-security`, `audit-fix-verify`, `solana-anchor-development` skills.

**Sequencing note:** Finish active hackathons first (Arc Aug 9, DataHub Aug 10, Keeperhub Aug 13, CockroachDB Aug 18) → AWS cert → Cyfrin as the differentiator. Both now on the website roadmap (gentechlabs.net → Phase 5 — Credential Depth).

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

## 🆕 DeepSeek Code — dedicated coding agent (Harness framework) coming

**Source:** [tweet](https://x.com/i/status/2083851157324046649) (Priya @Priyannkaaaa, Aug 2) + corroborated by ChainCatcher ("Insiders: DeepSeek is forming a Harness team") and SCMP ("DeepSeek's Harness team races to recruit talent"). No official DeepSeek repo yet — org still shows infra only (FlashMLA, DeepEP, DeepGEMM, DeepSpec).

### What's known
- DeepSeek building a dedicated AI coding agent **positioned directly against Claude Code and OpenAI Codex**
- Powered by **DeepSeek Harness** — long-running agent workflows with memory + repository awareness (planning, tool use, code execution)
- **V4-Flash's recent benchmarks were already evaluated using DeepSeek Harness** — it's core to their roadmap, not an experiment
- Closed beta expected to begin soon

### Why this matters to us
- We run on DeepSeek V4-Flash daily — a first-party DeepSeek coding agent is the cheapest, most native delegation backend we could add to the fleet (we already have Claude Code / Codex / OpenCode skills)
- DeepSeek Harness (memory + repo awareness + long-running workflows) is the same architecture our self-evolution harness uses — third-party validation of our design
- The benchmark numbers in the V4-Flash section above were produced by this harness — that's the quality ceiling we can expect

**Status:** 🔭 watch — when closed beta opens, evaluate as 4th delegation backend (build-queue #36)

## 🔗 Related

- [[brain-snapshot-2026-07-28]] — Full context snapshot
- [[context-weight]] — Auto-generated project overview
- [[build_queue.json]] — v52, 30 items
- [x] Bankr API key wired into revenue monitor (bk_usr_...37XZ, saved to profile .env). Bankr wallet EVM 0x99ae... SOL 6mcf... — currently $0 across 9 chains. Distinct from x402 revenue wallet (0x7ebf...). Monitor now reports Bankr portfolio each run.
