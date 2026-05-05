# Gentech HQ Status — Apr 24, 2026

## Active Workstreams

### 🔐 Token Security Audit (IN PROGRESS)
- Old GitHub PAT `ghp_Hrnt8g...xlo3` exposed across session archives
- `.hermes_history` + `hosts.yml` + archive files sanitized ✅
- **BLOCKED:** Live session files still contain token — need Jordan to rotate token
- **BLOCKED:** Cannot delete GitHub repos (ethglobal-open-agents) — gh auth broken
- Action needed: New PAT from Jordan → update `.env` + re-auth + finish cleanup

### 🌐 Kite AI Hackathon — Deadline Corrected to May 11
- Was incorrectly listed as Apr 26 across vault
- Updated: `02-Kite-AI-Apr26.md`, `Active/02-Kite-AI-Apr26.md`, `Kite-AI-Strategic-Watch.md`
- Updated hackathon roster skill
- Build brief: Agent Commerce Marketplace (Option B) — modular, chain-agnostic
- Ready to route to DMOB when Labs connection is restored

### 🚫 ETHGlobal — DROPPED
- Local repo deleted: `/root/gentech/ethglobal-open-agents/`
- Contracts salvaged to: `/root/gentech/kite-agent-commerce/salvaged-ethglobal/`
  - `AgentRegistry.sol`, `TaskManager.sol`, `AgentKeeper.sol` + interfaces
- Vault notes archived to: `10-Archive/ETHGlobal-Dropped/`
- GitHub repo delete failed (auth) — Jordan needs to delete `ProtoJay4789/ethglobal-open-agents` manually
- Updated: hackathon roster skill, AAE master plan, Hackathon-Tracker

### 🔧 DMOB Model Fix (Jordan working on)
- qwen3-coder-next coding model confirmed
- Vision not available on that model — images route through HQ first

## Blockers for Jordan
1. **New GitHub PAT** — rotate old token, provide new one for `.env` + gh auth
2. **Delete ethglobal-open-agents repo** manually (gh CLI auth broken)
3. **Labs/Entertainment Telegram groups** — Jordan diagnosing connection issue

## Next Available Work (No Blockers)
- Write Kite AI build brief to Green Room
- Arena game design doc scoping (Solana Frontier)
- Content pipeline strategy for Desmond

---
*Written by: Gentech*
*Next check-in: When Jordan provides new PAT or Labs is back online*
