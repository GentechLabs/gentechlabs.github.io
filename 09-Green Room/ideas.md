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

## New Ideas (May 28, 2026)
- [ ] **Collaborative Trip Planner** — Multiplayer travel planning with 5-10 contributors
  - Each person submits preferences (activities, restaurants, sights)
  - AI agent aggregates preferences, finds overlaps
  - Generates shared itinerary + personal time slots
  - Voting system for group decisions
  - Budget split calculator
  - Voice guides for destinations (Steve Harvey narrating Manila?)
  - Fits our pattern: social/multiplayer aspect across all products
  - Tech: Python + SQLite + Telegram bot or web UI
  - Status: Concept approved, queued after hackathon sprint

## Hackathon Queue
- [ ] **ElevenHacks #11** — Real-time voice agents. Speech Engine ready with Edge TTS fallback (no ElevenLabs credits needed). Link: https://hacks.elevenlabs.io/hackathons/11
  - Status: Queued, waiting for announcement
  - Assets ready: speech-engine repo, Steve Harvey + Vanito voices, FastAPI server
  - Potential enhancement: Add TradeRoast voice integration (roast → voice)

## GenTech Travels (Travel Companion Platform)

- [ ] **GenTech Travels — Full Build Brief** (May 28, 2026)
  - **Status:** 🟡 READY TO BUILD
  - **Type:** Travel community platform with AI moderation + creator economy
  - **Target:** Passport bros, international travelers, digital nomads
  - **Platform Layer:** Built ON TOP of Telegram/Discord/X (not standalone app)
  - **Full brief:** `09-Green Room/designs/gentech-travels-full-brief.md`
  - **Core features:**
    - Two sides (men/women) with co-ed toggle
    - One rule: get along, don't fight
    - Roast layer (👍/👎/🔥, Steve Harvey voice roasts)
    - Repair layer (reputation recovery paths)
    - Voice personalities (Steve Harvey, Vanito, George, Christel)
    - Creator economy (tips, spotlight, leaderboards, badges)
    - Verification system (photo, voice, video, community trust)
    - Challenge system (community-driven moderation)
  - **Build plan:** 11-16 days to MVP
  - **Revenue model:** $10K-15K/month at scale
  - **AAE integration:** Same stack as Trade Roast (execution, identity, governance, economy, personality, memory)
  - **Action:** Build after current hackathon wave

## GenTech Travels (NEW — May 28)
- [ ] **GenTech Travels — Travel Companion Platform**
  - **Concept:** Agentic travel companion — privacy layer ON TOP of Telegram/Discord/X, not standalone app
  - **Target:** Passport bros community, international travelers
  - **Key insight:** Don't build a new social network — build a moderation + privacy layer on existing platforms
  - **Features:** Gender-specific groups, co-ed toggle, content moderation, verification, challenge system, roast layer
  - **Revenue:** Creator economy (tips, spotlight), premium verification, community features
  - **Connection:** Uses LetsFG for flight search, AAE stack for agents/governance
  - **Full brief:** `09-Green Room/designs/gentech-travels-full-brief.md`
  - **Status:** 🟡 Concept — needs scoping

## GenTech Travels — Travel Companion Platform

- [ ] **GenTech Travels — Privacy Layer + Community Platform**
  - **Concept:** Not a new social network — a privacy and moderation layer ON TOP of Telegram/Discord/X
  - **Target:** Passport bros community, international travelers
  - **Pain point:** Mainstream platforms censor/shadowban travel content
  - **Solution:** AI agents moderate content, no shadow banning, community-driven
  - **Structure:** Gender-specific groups (men/women) + co-ed toggle
  - **Rule:** Get along, don't fight. If fighting, report it.
  - **Revenue:** Creator tips, spotlight feature, premium verification
  - **Build:** Uses LetsFG for flights, AAE stack for agents/governance
  - **Full brief:** `09-Green Room/designs/gentech-travels-full-brief.md`
  - **Status:** 🟡 Concept — needs scoping
  - **Priority:** 🟡 After Trade Roast build

## GenTech Travels (NEW — May 28)
- [ ] **GenTech Travels — Travel Companion Platform**
  - **Concept:** Agentic travel companion — privacy layer ON TOP of Telegram/Discord/X, not standalone app
  - **Target:** Passport bros community, international travelers
  - **Key insight:** Don't build a new social network — build a moderation + privacy layer on existing platforms
  - **Features:** Gender-specific groups, co-ed toggle, content moderation, verification, challenge system, roast layer
  - **Revenue:** Creator economy (tips, spotlight), premium verification, community features
  - **Connection:** Uses LetsFG for flight search, AAE stack for agents/governance
  - **Full brief:** `09-Green Room/designs/gentech-travels-full-brief.md`
  - **Status:** 🟡 Concept — needs scoping
