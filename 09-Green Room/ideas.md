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

## Queued (active)
- [ ] **Injective Agents Platform** — MCP server, grid trader, agent marketplace. Test with AAE agent. Link: agents.injective.com
- [ ] **Swarms ACM Submission** — $30K Finance track, LP Monitor agent. ⚠️ DEADLINE TODAY May 27

## Backlog
- [ ] **Portfolio V3 Website** — Full rebuild with hackathon wins, multi-agent story, embedded demos. Single source of truth (no more inline arrays). Dynamic project loading from JSON. Demo video embeds. Live stats dashboard. Reflects "solo founder + AI agent team" narrative. After current hackathon sprint.
  - **Brainstorm ideas:**
    - Auto-sync: GitHub Actions pulls from repos, updates project statuses automatically
    - Hackathon timeline: visual timeline showing submissions, wins, rankings
    - Agent dashboard: live view of Gentech, DMOB, YoYo, Desmond status
    - On-chain stats: real trades, LP positions, portfolio value pulled from chain
    - Interactive demo: visitors can try a live agent (Steve Harvey roast layer?)
    - Before/after: show what we built vs what it became (e.g., Rugcheck → TokenRiskOracle)
    - Cost savings: "Built with $0 API costs using local inference" (when Hermes Desktop is live)
    - Voice: add audio clips of our agent voices (Steve Harvey, Vanito, etc.)
    - Dark mode + neon: match the AAE aesthetic, not generic portfolio template
    - Fix sync issues: single JSON file, no duplicate arrays, GitHub Actions auto-deploy
- [ ] **Agent Performance Index** — S&P 500 for agents. Track Sharpe ratio, drawdown, win rate, gas efficiency across strategies. Public dashboard. Builds on data we already collect from AAE.
- [ ] **Agent Insurance Pools** — Stake against agent performance. Good agent = cheap premiums. Bad agent = expensive/uninsurable. Unlocks real capital flowing into agent-managed vaults.
- [ ] **Agent Education Academy** — Structured learning path: "Build your first agent in 30 minutes." Uses Hermes + AGT + x402 as curriculum. Graduates deploy into AAE. Feeds the flywheel.
- [ ] **Cross-chain Agent Handoff Protocol** — Agent on Solana detects opportunity on Base → hands off to Base-native agent seamlessly. "TCP/IP for agents." Generalize AgentEscrow handoff chains into a protocol.
- [ ] Explore x402 protocol deeper for Agent Arena payment rails
- [ ] Investigate xGate MCP server for agent discovery layer

## Demo Video Distribution (queued)
- [ ] Upload all demo videos to YouTube channel
- [ ] Update ProtoJay4789.github.io portfolio with embedded demos
- [ ] Need: YouTube channel access/API key, demo video files

## Hermes Agent Update
- [ ] Run `hermes update` — check changelog for breaking changes before updating
- [ ] Post about our stack on X tying into the MCP Catalog announcement

## Base Build MCP Demo Contest (queued)
- [ ] $2K USDC — demo video under 3 min
- [ ] Show Base MCP usage (agent discovers AAE, executes trade, earns fees)
- [ ] Post on X, reply to @buildonbase
- [ ] Post link: https://x.com/buildonbase/status/2059713951974236219
