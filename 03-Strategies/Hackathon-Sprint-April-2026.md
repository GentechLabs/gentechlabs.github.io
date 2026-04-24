# Hackathon Sprint — April 2026

**Created:** 2026-04-17 (late night)
**Status:** Prototype planning phase

---

## Active Hackathons (organized by deadline)

### 1. ElevenHacks #6 ⚡ ACTIVE
- **Prize:** $10K cash + ElevenLabs credits
- **Announced:** April 16, 2026
- **Started:** April 23, 2026
- **Deadline:** ~May 7, 2026 (~16-day window)
- **Focus:** Build a game with Zed + ElevenLabs APIs
- **SDK:** ElevenAgents React SDK v1.0 (released Apr 23)
- **Found via:** @ElevenLabsDevs on X
- **GenTech Concept:** AAE Trading Arena — voice-driven educational trading simulator in Zed

### 2. ETHGlobal Open Agents 💰 BIGGER
- **Prize:** $50K total (0G: $15K | Uniswap: $5K | Gensyn: $5K | KeeperHub: $5K)
- **Format:** Async, remote, global, teams or solo (max 5)
- **Stake:** 0.005 ETH (returned after submission)
- **Link:** https://ethglobal.com/events/openagents

#### Full Timeline
| Date | Event |
|------|-------|
| **Wed, Apr 23** | Deadline to Apply (11:59pm UTC) |
| **Thu, Apr 24** | Kickoff + Hacking Begins (12:00pm UTC) |
| **Mon, Apr 28** | Check-in #1 Due (11:59pm UTC) |
| **Tue, Apr 28** | Project Feedback Session (2:00pm UTC) |
| **Thu, Apr 30** | Project Feedback Session (9:00am UTC) + Check-in #2 Due (11:59pm UTC) |
| **Sun, May 3** | Project Submissions Due! (12:00pm UTC) |
| **Sun, May 3** | Judging Round 1: Async (3:00pm UTC) |
| **Mon, May 4** | Judging Round 2: Live (12:00pm UTC, 2hrs) |
| **Wed, May 6** | Finale — Finalists Announced! (12:00pm UTC) |

#### Key Rules
- **NO pre-existing projects** — must start from scratch (familiarizing with tools OK)
- AI tools permitted (Claude Code, Copilot, Cursor) — must document usage
- Can apply for max **3 Partner Prizes**
- Solo hackers welcome
- Team formation session: April 23, 3:00pm UTC

---

## The One-Project-Two-Hackathons Strategy

Build ONE project that qualifies for both:
- **Voice-enabled on-chain AI agent** — agents that talk, execute on-chain, and build reputation
- ETHGlobal angle: agents interacting with Ethereum
- ElevenHacks angle: voice layer using ElevenLabs + Zed (Trading Arena)

### What We Already Have
- ✅ Hermes agent framework (4 agents running)
- ✅ ElevenLabs TTS integration (anthem, voice clones)
- ✅ Agent orchestration (cron, delegation, watchdog)
- ✅ Multi-agent coordination (Gentech HQ)
- ✅ Telegram bot interface
- ✅ Multica research (task management layer)
- ✅ Catch-up digest skill (recovery)
- ✅ Smart contract skills (Solidity audit skills installed)

### What We Need
- 🔲 On-chain component (Ethereum or Avalanche bridge)
- 🔲 Agent wallet integration
- 🔲 Voice interaction demo
- 🔲 Kiro integration (need to research what Kiro is)
- 🔲 Live demo / deployable prototype
- 🔲 Video submission (usually required)

---

## Prototype Concept: "VoxAgent"

**Tagline:** "Your AI agent speaks. Your AI agent acts. On-chain."

A voice-enabled AI agent that:
1. **Listens** — receives voice commands via Telegram/phone
2. **Thinks** — processes intent using LLM (Hermes)
3. **Speaks** — responds with ElevenLabs voice
4. **Acts** — executes on-chain transactions (swap, stake, transfer)
5. **Builds reputation** — on-chain record of completed tasks

### Stack
```
User (voice) → Telegram → Hermes Agent → ElevenLabs TTS
                                ↓
                          Agent Wallet
                                ↓
                     Ethereum/Avalanche (on-chain execution)
                                ↓
                     Reputation contract (track agent actions)
```

### Demo Flow
1. User speaks: "Swap 0.1 ETH for USDC"
2. Agent confirms with voice: "I'll swap 0.1 ETH for USDC on Uniswap. Confirming..."
3. Agent executes swap via agent wallet
4. Agent reports back with voice: "Done! Swapped 0.1 ETH for 324 USDC. Transaction hash: 0x..."
5. On-chain: reputation contract records the successful action

---

## Action Items (Jordan handles in morning)

### Sign-Ups Needed
- [ ] ETHGlobal Open Agents: https://ethglobal.com/events/openagents — **apply by Apr 23**
- [x] ElevenHacks #6: Zed × ElevenLabs — concept locked, build ready
- [ ] Kiro account (whatever it is — need to research)
- [ ] 0G account (if submitting for their $15K prize)
- [ ] ETH stake: 0.005 ETH (returned after submission)

### API Keys Needed
- [ ] ElevenLabs API key (hackathon may provide credits)
- [ ] ElevenLabs hackathon credits (request via hackathon portal)
- [ ] Ethereum RPC (Infura/Alchemy free tier)
- [ ] Agent wallet (MetaMask or similar for demo)

### Build Window
- **Apply:** NOW → April 23
- **Build:** April 24 → May 3 (9 days of hacking!)
- **Submit:** May 3, 12:00pm UTC
- **Key rule:** NO coding before April 24 kickoff — but can research tools now

### Prototype Build Order
1. **Voice loop** — Telegram voice → Hermes → ElevenLabs response
2. **Agent wallet** — basic ETH wallet controlled by agent
3. **Simple on-chain action** — transfer ETH or swap on Uniswap
4. **Reputation contract** — simple Solidity contract to track agent actions
5. **Demo video** — 2-3 minute walkthrough

---

## Notes
- Jordan works Sun-Wed 6:30am-3:30pm, Thu-Sat 11am-8pm
- **April 23 = apply deadline** (Wednesday — Jordan's day shift)
- **April 24 - May 3 = hacking period** (9 days, NOT 4 days!)
- Free API keys from ElevenHacks alone worth the entry
- "Lol I see free api key and that's worth it alone. my normal work." — Jordan
- No pre-existing code allowed — but can research/familiarize with tools before kickoff
- AI tools OK (Claude Code, Copilot, Cursor) — must document usage
- Solo hacking is fine — no need to find a team
- ETH stake (0.005 ETH) returned after submission — free entry essentially
