# GenTech Multi-Agent Workflow v1.1
Last Updated: 2026-04-23

## 1. Communication Protocol
- **Internal Sync**: Agents discuss in 'Green Room' or 'Mess Hall' first to vet technical/creative details.
- **The 'Direct Answer' Rule**: Every multi-agent conversation MUST end with a consolidated "Direct Answer" sent to Jordan in HQ.
- **The 'No Interrupt' Policy**: Agents stay on current tasks until a stopping point is reached before processing new messages/links from Jordan.

## 2. The Brain (Obsidian Vault)
- **Source of Truth**: The vault is the primary reference for agent behaviors and project state.
- **Approval Sync**: Direct Answers are synced to the Brain for Jordan's final approval.
- **Maintenance**: A dedicated 'Vault Surgeon' cron job periodically reviews and prunes outdated notes.

## 3. Reporting & Briefings
- **Master Digest**: A single consolidated summary of all 4 groups delivered daily at 6:30 AM EST.
- **Voice Integration**: Long messages are accompanied by TTS voice bubbles for accessibility.

## 4. Model Configuration
- **Primary (gentech, yoyo, desmond)**: opencode-go / kimi-k2.6
- **Fallback (all)**: ollama-cloud / kimi-k2.6:cloud (auto-failover on 429/503)
- **Dmob (Labs)**: ollama-cloud / qwen2.5-coder:32b (code-heavy tasks), fallback to opencode-go
- **Auxiliary vision**: opencode-go / kimi-k2.6
- **Note**: Configs fixed Apr 26 after gateway restart reverted all to ollama-cloud.

## 5. Agent Roles
- **Gentech**: Lead/Orchestrator.
- **YoYo**: Investor/Financial Intelligence.
- **DMOB**: Dev/Security/Auditor.
- **Desmond**: Creative/Content/Brand.

## 6. Collaborators
|- **Vanito** (8774981477) — Music production, Entertainment group. In GenTech Entertainment + GenTech Strategies (NOT HQ).
|- **Dadrian** (6842745552) — Strategies/Entertainment groups. In GenTech Entertainment + GenTech Strategies (NOT HQ).

## 7. AAE LP Position Tracker (Apr 25 2026)
- **Job ID**: `2ca757ee055c` — YoYo’s LP + DeFi Milestone cron job.
- **Source**: DexScreener via LFJ v2.2 — AVAX/USDC 5bps pool.
- **Key Metrics**: $9.35 price (−0.8% 24h), range $9.33–$9.52 (in-range 21% efficiency), $0.17/day fees (~76% APR), LP value ~$83.94 (+$0.39 vs HODL).
- **Front-End Integration**: Design to support D5 milestone tracker expansion across chains/pools. Ready to add yield projections, IL simulations, or CSV exports.
