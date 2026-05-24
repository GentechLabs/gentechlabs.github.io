# 🌿 Green Room — Active Ideas & Explorations

## In Progress
- [ ] **Claude Code Game Studios — Hierarchy Model for Agent Arena** (Queued May 23, Active May 24)
  - Source: Donchitos/Claude-Code-Game-Studios — 49 agents, 73 skills, 12 hooks, full studio hierarchy
  - Key insight: 3-tier model maps to our setup
    - Tier 1: Directors (creative, technical, producer) → HQ
    - Tier 2: Department Leads (game designer, lead programmer, art director) → Specialist groups
    - Tier 3: Specialists (gameplay programmer, AI programmer, QA) → Cron jobs + subagents
  - Action: Clone repo, analyze agent definitions, extract hierarchy patterns, adapt to AAE loadout system
  - Status: Research started
- [ ] **Fhenix "Private By Design" dApp Buildathon** (Akindo) — $50K USDC grants, wave-based. FHE encrypted compute on EVM. AAE angle: private agent trading, encrypted strategies, confidential agent state. Link: https://app.akindo.io/wave-hacks/Nm2qjzEBgCqJD90W
- [ ] **Daydreams Systems** (daydreams.systems) — commerce harness for agents. x402 payments, ERC-8004 identity, xGate discovery. SDK: github.com/daydreamsai/lucid-agents. Potential AAE integration for agent-to-agent payments + discovery.
- [ ] **TermiX AACP** — Agent Autonomous Commerce Protocol. ERC-8004 identity, ERC-8183 job escrow, zkVM + TEE verification, persistent staking. AAE integration: use AACP as commerce layer, AAE adds gamification. Analysis: `09-Green Room/build-logs/2026-05-24-termiX-aacp-analysis.md`
- [ ] **Nango** — Open-source integration runtime (700+ APIs). MCP server for AI agents. Use for AAE agent integrations (exchanges, data providers, social platforms). Jordan approved. Link: github.com/NangoHQ/nango
- [ ] **Vibe-Trading** — HKUDS multi-agent financial workspace. Natural language → trading strategies → backtest → evolve. Strategy generation layer for AAE agents. Link: github.com/HKUDS/Vibe-Trading

## AAE Stack (approved integrations)
| Layer | Provider | Status |
|-------|----------|--------|
| Identity | ERC-8004 (AACP + AgentRanking) | ✅ Approved |
| Commerce | AACP (TermiX) | ✅ Approved |
| Payments | x402 (Daydreams) | ✅ Approved |
| Privacy | FHE (Fhenix) | 🔍 Researching |
| Discovery | xGate (Daydreams) | 🔍 Researching |
| Integrations | Nango (700+ APIs) | ✅ Approved |
| Strategy | Vibe-Trading | 🔍 Researching |
| Hierarchy | Claude Code Game Studios | 🔍 Researching |

## Backlog
- [ ] Explore x402 protocol deeper for Agent Arena payment rails
- [ ] Investigate xGate MCP server for agent discovery layer
