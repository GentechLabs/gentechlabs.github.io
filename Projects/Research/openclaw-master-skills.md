# OpenClaw Master Skills — Reference

**Date:** 2026-06-01
**Source:** https://github.com/LeoYeAI/openclaw-master-skills
**Status:** Cherry-picked 4 skills

---

## What is OpenClaw Master Skills?

Curated, weekly-updated collection of **1609+ skills** for OpenClaw agents. Massive library covering AI, search, productivity, dev, marketing, media, finance, comms, smart home, memory, security, data, social.

**Source:** https://github.com/LeoYeAI/openclaw-master-skills
**Powered by:** https://myclaw.ai

---

## Skills Installed (Cherry-picked)

### 1. agent-team-orchestration
- **Category:** DevOps
- **Purpose:** Multi-agent task routing, handoff protocols, review workflows
- **Value:** Direct upgrade to our dispatch system
- **Path:** `~/.hermes/profiles/gentech/skills/agent-team-orchestration/`

### 2. agent-security-hardening
- **Category:** DevOps
- **Purpose:** 7 rules of prompt injection defense, data boundaries, WAL protocol
- **Value:** Production security for our agents
- **Path:** `~/.hermes/profiles/gentech/skills/agent-security-hardening/`

### 3. stock-analysis
- **Category:** Finance
- **Purpose:** Yahoo Finance analysis, 8-dimension scoring, portfolio, watchlist, alerts, rumor scanner
- **Value:** TradeRoast upgrade
- **Path:** `~/.hermes/profiles/gentech/skills/stock-analysis/`

### 4. bitmart-wallet
- **Category:** Blockchain
- **Purpose:** 12 endpoints, no API key, Solana/BSC/ETH/Arbitrum/Base, smart money tracking
- **Value:** Free multi-chain data
- **Path:** `~/.hermes/profiles/gentech/skills/bitmart-wallet/`

---

## Skills Evaluated but Not Installed

### binance-derivatives-trading-portfolio-margin
- **Reason:** Binance-specific, not our focus

### agent-memory
- **Reason:** Basic, we already have better (vault + memory tool)

### vincent-trading-engine
- **Reason:** Polymarket + HyperLiquid specific, not our focus yet

### chainbase-openapi-skill
- **Reason:** Requires API key, we have bitmart-wallet (no key needed)

### elite-longterm-memory
- **Reason:** Requires LanceDB plugin, we already have vault memory

---

## How to Use OpenClaw Skills in Hermes

OpenClaw skills are written for Clawdbot/OpenClaw but can be adapted to Hermes:

1. **Copy SKILL.md** to Hermes skills directory
2. **Adapt paths** — change `{baseDir}` to actual paths
3. **Replace commands** — OpenClaw uses `uv run` and `clawhub`, Hermes uses `terminal` and `skill_manage`
4. **Keep the knowledge** — the actual value is in the SKILL.md content, not the tooling

---

## Related

→ See [[Green-Room/lobby-ui-order-book.md]] (Order book design)
→ See [[Green-Room/pay-sh-multi-chain.md]] (Pay.sh + x402)
→ See [[Projects/AAE/]] (Agent economy infrastructure)
