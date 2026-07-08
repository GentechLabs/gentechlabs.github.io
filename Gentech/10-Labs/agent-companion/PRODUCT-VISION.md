# Agent Companion — Product Vision

**Status:** Paused — Idea Archived for Future  
**Date:** July 6, 2026  
**Owners:** Gentech + Forge  
**Target:** v1.0 MVP — 2 weeks to playable prototype, 1 month to polished release

---

## 🎯 One-Liner

Turn any split-screen co-op game into a solo experience — AI agents play as Player 2 with you locally.

---

## 📋 Core Product (v1.0)

### **What It Does**
- Capture emulator window (Xenia/Dolphin/RPCS3)
- Vision model analyzes game state (enemy position, objective, combat status)
- Agent injects Player 2 inputs via keyboard/virtual gamepad
- Human plays normally, Agent follows, fights, revives

### **First Target Game: Gears of War 2**
- Split-screen co-op mode
- Clear visual cues (cover system, revive icons, objective markers)
- Linear progression (easy for agent navigation)
- Emulation via Xenia (already stable for Jordan)

### **Technology Stack**

| Component | Tech | Owner |
|-----------|------|-------|
| **Screen Capture** | `mss` (Python) | Gentech |
| **Vision Analysis** | Ollama Cloud (Qwen/Llama 7B) | Gentech |
| **Input Injection** | `keyboard` library → WASD + Space | Gentech |
| **Game-Specific Skills** | `emulation-gears2` skill (cover, revive, combat) | Gentech |
| **Session Dashboard** | Web UI (Python/Flask) | Forge |
| **Agent Personality Picker** | UI component | Forge |
| **x402 Payments** | Pay-per-session integration | Both |
| **Highlight Generator** | Video processing (FFmpeg) | Forge |

### **Cost Model (v1.0)**

| Session Length | Ollama Cloud | GLM-4.7 API | GLM-5.2 API |
|----------------|--------------|-------------|-------------|
| 1 hour | $1-4 | $7-15 | $25-50 |
| 2 hours | $2-8 | $15-30 | $50-100 |
| 5 hours | $5-20 | $40-75 | $125-250 |

**Sweet spot:** Ollama Cloud for casual ($2-8/2hr), cloud API for quality ($15-30/2hr)

---

## 🚀 Phase 2: Training Platform (v2.0)

### **The Insight**
> "What if you could train based off of your gaming data, based off your gamer tag and how many games you play and hours?"

### **How It Works**
1. **Record gameplay** — Agent captures your screen + inputs during sessions
2. **Train agent** — Fine-tune Ollama model on your playstyle (aggressive/defensive, rusher/camper)
3. **Sell your agent** — Marketplace where others buy your playstyle as a companion

### **Data Flow**
```
You Play → Agent Records → Upload to Training → Fine-tune → Agent Bundle → Marketplace Sale
```

### **Privacy + Ownership**
- User owns their gameplay data
- Opt-in training (default off)
- Revenue share: 70% to creator, 30% platform
- Exclusive vs. non-exclusive licensing

---

## 🏪 Phase 3: Agent Marketplace + Rec Mode (v3.0)

### **The 2K Park Model**
> "Just like 2K has a Rec Mode where people wait at the park to pick up a game, agents wait to get picked up by other humans."

### **Discovery Interface**
```
┌─────────────────────────────────────┐
│  🎮 Agent Marketplace — Rec Mode     │
├─────────────────────────────────────┤
│                                      │
│  🔥 Trending Agents                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  │AggroBot │ │Tactician│ │MedicPro ││
│  │ 1.2K hrs│ │  850 hrs│ │  600 hrs││
│  │$3/hr    │ │ $4/hr   │ │ $3.50/hr││
│  └─────────┘ └─────────┘ └─────────┘│
│                                      │
│  🎯 Search by Game/Gamertag         │
│  [ Search: Gears of War 2 ]         │
│                                      │
│  🏆 Top Creators                    │
│  • @ShroudGaming — "Rusher Pro"     │
│  • @DrLupo — "Support Specialist"   │
│  • @Ninja — "Aggressive Fragbot"    │
└─────────────────────────────────────┘
```

### **Agent Cards**
Each agent listing shows:
- Playstyle description
- Win rate with human partners
- Average session rating (1-5 stars)
- Creator profile (gamer tag, hours played)
- Price per hour
- Games supported

### **The Universal Problem: Friend Reliability Gap**
> "People aren't making friends like we used to. This could apply to so many different things."

**Three big problems, one solution:**

| Audience | Problem | AI Companion Solution |
|----------|---------|----------------------|
| **Streamers** | Random teammates troll you, ruin clips, can't coordinate for content | Always on-brand, plays exactly how you want, highlight reels perfect first take |
| **Solo Gamers** | Co-op games sit on shelf because "nobody to play with," matchmaking is chaos | Always available, no flaking, no toxicity, play whenever you want |
| **Competitive Players** | Can't practice with consistent teammates, random skill levels | Configurable difficulty, practice specific scenarios, test builds reliably |

#### **For Streamers/Content Creators**
**Why this matters:**
- Demo videos take 10x longer with random teammates
- People sabotage you for clips or content
- You have to edit out their nonsense
- Can't show off game properly when teammates don't coordinate

**AI Companion advantage:**
- Perfect demo videos first take
- Agent follows your content direction
- No trolling, no toxicity
- Highlight reels auto-generated with best moments
- Multiple agents for "Agent Army" content (5 bots vs. audience)

#### **For Modern Gaming**
**The reality:**
- Online toxicity is at all-time highs
- Scheduling with friends is hard (jobs, time zones, life)
- Many gamers don't have consistent groups
- Solo-only content misses co-op experiences

**AI Companion advantage:**
- Reliable partner every time you log on
- No waiting in lobbies for matchmaking
- No bad teammates ruining the session
- Play the games you own that require co-op

---

## 🏆 STRATEGIC PIVOT: Native Xenia Integration

**The opportunity:**
> "Xenia Canary is on GitHub. We could add this as functionality to their GitHub."

### **Why This Changes Everything**

| Approach | Distribution | Integration | Credibility |
|----------|-------------|-------------|-------------|
| **External tool** | Download separately | Hooks into emulator | "Third-party app" |
| **Xenia Canary feature** | Ships with emulator | Native C++ integration | "Official Xenia feature" |

**The advantage:**
- Every Xenia Canary user gets AI Companion automatically
- Native C++ integration (faster, more reliable)
- Xenia team maintains the base, we add the AI layer
- Gentech becomes recognized contributors to a major emulator

### **New Architecture: Emulator-Agnostic Integration**

```
┌─────────────────────────────────────────────────────────────┐
│              AI Companion Core (Proprietary)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Vision Engine (Python)                                │ │
│  │  • Game state understanding                            │ │
│  │  • Decision making                                     │ │
│  │  • Agent personality logic                             │ │
│  │  • Ollama Cloud inference                              │ │
│  └────────────────────────────────────────────────────────┘ │
│         ↓                    ↓                    ↓         │
│    ┌────────┐           ┌────────┐           ┌────────┐     │
│    │ Xenia  │           │ RPCS3  │           │ Dolphin│     │
│    │ Bridge │           │ Bridge │           │ Bridge │     │
│    └────────┘           └────────┘           └────────┘     │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Xenia Core │      │  RPCS3 Core │      │ Dolphin Core│
│  (C++ plugin)│      │  (C++ plugin)│      │  (C++ plugin)│
│  • Screen   │      │  • Screen   │      │  • Screen   │
│    Capture  │      │    Capture  │      │    Capture  │
│  • Input    │      │  • Input    │      │  • Input    │
│    Injector │      │    Injector │      │    Injector  │
└─────────────┘      └─────────────┘      └─────────────┘
```

### **Modular Design Principles**

**Separation of Concerns:**
| Layer | Technology | Open/Closed |
|-------|-----------|-------------|
| **Emulator Plugins** | C++ (native) | **Open** — contributed to each emulator |
| **Bridge Layer** | Python (IPC) | **Open** — standard protocol |
| **AI Companion Core** | Python | **Closed** — proprietary engine |

**Why This Matters:**
- One AI engine, multiple emulator integrations
- We only maintain the core logic once
- Each emulator gets a lightweight plugin
- New emulator support = just build a new bridge

### **Emulator Support Roadmap**

| Emulator | Platform | Complexity | Timeline |
|----------|----------|------------|----------|
| **Xenia Canary** | Xbox 360 | Medium | v1.0 (Week 6) |
| **RPCS3** | PlayStation 3 | Medium | v1.5 (Month 3) |
| **Dolphin** | Wii/GameCube | Low | v1.5 (Month 3) |
| **Yuzu** | Nintendo Switch | Low | v2.0 (Month 4) |
| **PCSX2** | PlayStation 2 | Low | v2.0 (Month 5) |
| **Citra** | Nintendo 3DS | Medium | v2.5 (Month 6) |

**We target the emulators with the biggest co-op libraries:**
- Xbox 360: Gears of War 2, Halo 3, Left 4 Dead, Portal 2
- PS3: Resistance series, Uncharted co-op, Ratchet & Clank: All 4 One
- Wii: Mario Kart Wii, Super Mario Galaxy 2 co-op
- Switch: Mario Kart 8 Deluxe, Splatoon 2 co-op

### **Build Plan**

#### **Phase 0: Emulator Research (Week 1)**
**Repository Targets:**
- Xenia: https://github.com/xenia-project/xenia
- RPCS3: https://github.com/RPCS3/rpcs3
- Dolphin: https://github.com/dolphin-emu/dolphin

**Research Checklist:**
- [x] Clone and explore all three codebase structures
- [x] Identify existing plugin/extension architecture
- [x] Review contribution guidelines (CONTRIBUTING.md)
- [x] Find screen capture implementation points
- [x] Find input/controller handling code
- [x] Document license separation strategy (IPC boundary for GPL emulators)
- [x] Write integration proposals for all three emulators
- [ ] Submit issues to Xenia, RPCS3, and Dolphin repositories
- [ ] Get maintainer approval before coding

**Proposals Drafted:**
- XENIA-PROPOSAL.md — BSD license, direct integration
- RPCS3-PROPOSAL.md — GPL license, IPC separation
- DOLPHIN-PROPOSAL.md — GPL license, IPC separation

**Key Questions Answered:**
1. Does Xenia have an existing plugin system? No, but extensible via InputDriver base class
2. Can we hook into the render pipeline for screen capture? Yes, via GuestOutputRefreshContext
3. Can we inject controller input programmatically? Yes, via AgentInputDriver
4. What's the code style and C++ standards used? C++17, clang-format, xb format command
5. Are there similar automation tools already integrated? No, but capture infrastructure exists

#### **Phase 1: AI Companion Core (Week 2-3)**
- [ ] Build vision engine (Python)
- [ ] Implement game state understanding (generic, game-agnostic)
- [ ] Create decision-making layer (configurable per game)
- [ ] Integrate Ollama Cloud for inference
- [ ] Define bridge protocol (Python ↔ C++ IPC)

#### **Phase 2: Xenia Native Plugin (Week 4-5)**
- [ ] Implement C++ screen capture module
- [ ] Implement C++ input injector
- [ ] Create Python bridge for Xenia
- [ ] End-to-end latency testing
- [ ] Submit PR to Xenia repository

#### **Phase 3: Game-Specific Skills (Week 6-7)**
- [ ] `emulation-gears2` skill (cover system, revive logic, combat priorities)
- [ ] `emulation-halo3` skill (vehicle support, objective following)
- [ ] `emulation-portal2` skill (puzzle recognition, co-op mechanics)
- [ ] Test with real gameplay

#### **Phase 4: RPCS3 + Dolphin Plugins (Week 8-12)**
- [ ] Build RPCS3 C++ plugin (screen + input)
- [ ] Build RPCS3 Python bridge
- [ ] Build Dolphin C++ plugin
- [ ] Build Dolphin Python bridge
- [ ] Submit PRs to both repositories
- [ ] Test with PS3/Wii co-op games

#### **Phase 5: Multi-Emulator Support (Week 13-16)**
- [ ] Yuzu plugin (Switch)
- [ ] PCSX2 plugin (PS2)
- [ ] Citra plugin (3DS)
- [ ] Unified agent personality picker (works across all emulators)
- [ ] Marketplace emulator filtering

### **Contribution Strategy**

**What we contribute to Xenia:**
1. **Screen capture API** — Expose frame buffer to external tools
2. **Input injection API** — Allow external tools to simulate controller input
3. **Plugin system** — General framework for third-party extensions

**What we keep proprietary:**
- Vision models and training data
- Agent logic and decision making
- Marketplace and training platform
- x402 payment integration

**Why this works:**
- Xenia gets better tooling (screen capture, input APIs)
- We get native integration (faster, more reliable)
- Users get AI Companion out-of-the-box
- Both parties benefit, open-source friendly

### **Timeline Impact**

| Milestone | External Tool | Xenia Integration |
|-----------|---------------|-------------------|
| **Research + approval** | N/A | +1 week |
| **Native modules** | N/A | +2 weeks |
| **Agent bridge** | - | +1 week |
| **Beta release** | 2 weeks | 6 weeks |

**Tradeoff:** +4 weeks delay for native integration
**Reward:** Automatic distribution to all Xenia Canary users

---

## 💰 Revenue Model

### **Multi-Stream Revenue**

| Stream | Pricing | Target | Year 1 Potential |
|--------|---------|--------|------------------|
| **Pay-per-session** | $2-30/session | Casual gamers | $30-120K |
| **SaaS subscription** | $20/mo unlimited | Power users | $60-240K |
| **Agent marketplace** | 10-15% commission | Creators | $40-150K |
| **Training data monetization** | 70% creator cut | Influencers | $20-80K |
| **Highlight generation** | $0.50/clip or $10/mo | Streamers | $15-60K |
| **B2B licensing** | $500-5K/yr | Game studios | $100-300K |
| **TOTAL** | | | **$265-950K** |

### **Cost Structure**
- **Server costs:** $200-500/mo (Ollama hosting, video processing)
- **API costs:** $50-200/mo (x402 payments, marketplace backend)
- **Maintenance:** $100-300/mo (Forge dashboard updates, skill maintenance)

**Net margin:** 85-90% after costs

---

## 🎨 Forge Deliverables

### **Phase 1 (Week 1-2)**
- [ ] Session dashboard UI (launch agent, see stats, stop session)
- [ ] Agent personality picker (select agent profile before game)
- [ ] Basic x402 payment integration (unlock sessions)
- [ ] Session history view (past games, duration, cost)

### **Phase 2 (Week 3-4)**
- [ ] Training data upload interface
- [ ] Fine-tuning status dashboard
- [ ] Agent bundle creator (package trained model + metadata)
- [ ] Marketplace listing creator

### **Phase 3 (Week 5-8)**
- [ ] Rec Mode lobby UI (agent discovery, search, ratings)
- [ ] Agent card design (creator profile, stats, pricing)
- [ ] Payment processing for agent purchases
- [ ] Creator dashboard (earnings, sales, ratings)

---

## 🔧 Gentech Deliverables

### **Phase 1 (Week 1-2)**
- [ ] Screen capture pipeline (`mss` → emulator window detection)
- [ ] Vision loop (capture → analyze → inject, 10-30fps)
- [ ] Input injection (keyboard WASD + Space)
- [ ] `emulation-gears2` skill (cover system, revive logic, combat priorities)

### **Phase 2 (Week 3-4)**
- [ ] Gameplay recording (screen + input capture)
- [ ] Data preprocessing (label frames with game state)
- [ ] Fine-tuning pipeline (Ollama model training)
- [ ] Agent validation (test trained agent vs. baseline)

### **Phase 3 (Week 5-8)**
- [ ] Multi-agent coordination (Agent Army support)
- [ ] Marketplace backend API (agent listings, purchases, downloads)
- [ ] Highlight generation (detect exciting moments, extract clips)
- [ ] B2B licensing tools (custom agent training for studios)

---

## 🎮 Expanding Beyond Gears 2

### **Game Expansion Roadmap**

| Game | Emulator | Complexity | Timeline |
|------|----------|------------|----------|
| **Gears of War 2** | Xenia | Medium | v1.0 (Week 2) |
| **Halo 3** | Xenia | Medium | v1.5 (Month 2) |
| **Portal 2** | RPCS3 | Low | v1.5 (Month 2) |
| **Left 4 Dead 2** | RPCS3 | Medium | v2.0 (Month 3) |
| **Call of Duty: Zombies** | RPCS3 | High | v2.5 (Month 4) |
| **Mario Kart Wii** | Dolphin | Medium | v3.0 (Month 5) |

### **Genre-Specific Skills**
- `emulation-fighting-games` — Frame timing, combo recognition
- `emulation-racing-games` — Track position, rubber banding
- `emulation-shooters` — Enemy detection, friendly fire
- `emulation-platformers` — Jump timing, gap recognition

---

## 🚢 Regulatory Strategy

### **The Console Problem**
| Platform | Policy | Workaround |
|----------|--------|------------|
| Xbox Live | TOS prohibits automation | Emulators (Xenia) |
| PlayStation | No third-party AI | Emulators (RPCS3) |
| Steam | VAC bans for AI | Local-only, no VAC |

**Beachhead:** Emulators don't have platform restrictions. This is the "Airbnb of gaming" — platform rules, but workaround exists.

**Long-term:** B2B licensing with game studios (Nintendo, Sony, Microsoft) for official AI companion SDKs.

---

## 🔮 The "Agent Army" Vision

> "What if streamers could do that with agents? So now you can have fun highlights and fun matches the same way the streamers do."

### **Use Case: Streamer + Agent Army**
1. Streamer launches 5 agents with different personalities
2. Audience watches agents play co-op matches
3. Highlight reels auto-generated (best kills, funny fails)
4. Chat can vote on agent tactics mid-match
5. Agents learn from viewer feedback

### **Personalities as IP**
- "Rusher Bot" — Always aggressive, fun chaos
- "Tactician" — Strategic, slow, methodical
- "Medic" — Focuses on revives, support
- "Meme Bot" — Intentionally plays badly for laughs

**Monetization:** Streamers sell their agent personalities on the marketplace. 10-15% commission to platform.

---

## ✅ Success Metrics

### **v1.0 (Week 6) — Xenia Beta**
- [ ] Xenia native plugin merged and released
- [ ] AI Companion Core functional (Python)
- [ ] Playable prototype with Gears of War 2
- [ ] Agent completes Chapter 1 with human partner
- [ ] Cost < $8/2hr session (Ollama)
- [ ] Forge session dashboard functional

### **v1.5 (Month 3) — Multi-Emulator**
- [ ] RPCS3 plugin merged (PS3 support)
- [ ] Dolphin plugin merged (Wii/GameCube support)
- [ ] 3 game skills shipped (Gears 2, Halo 3, Portal 2)
- [ ] Training platform launched
- [ ] 5 creator profiles trained and listed
- [ ] First agent sale completed

### **v2.0 (Month 4-6) — Platform Expansion**
- [ ] Rec Mode marketplace live
- [ ] 50 agents available for purchase
- [ ] Multi-agent support (Agent Army)
- [ ] Yuzu plugin (Switch)
- [ ] PCSX2 plugin (PS2)
- [ ] B2B licensing tools ready

---

## 📝 Build Notes

- **Ollama Cloud subscription is critical** — makes pricing viable
- **State caching reduces token usage** — don't analyze every frame
- **Genre-specific skills are reusable** — one skill, many games
- **Forge builds UI, Gentech builds backend** — clear ownership
- **Emulators are the wedge** — console partnerships come later

---

**Last Updated:** July 6, 2026  
**Next Review:** Forge sync (after reading this doc)

---

## 🚀 Ready for Forge

This document is the complete build blueprint. Forge has everything needed:

✅ **Build queue entry** — Cost, tokens, complexity, threshold  
✅ **Product vision** — 3-phase roadmap (Core → Training → Marketplace)  
✅ **Universal problem statement** — 3 audiences, 1 solution  
✅ **Revenue model** — 6 streams, $265-950K potential  
✅ **Deliverables breakdown** — Forge vs. Gentech ownership  
✅ **Strategic pivot** — Native emulator integration (Xenia, RPCS3, Dolphin)  
✅ **Modular architecture** — One AI core, multiple emulator plugins  
✅ **Emulator roadmap** — 6 emulators, 16-week build plan  
✅ **Success metrics** — Updated for strategic timeline

**Forge's decision:**
- Start with Xenia (Week 1-6)
- Expand to RPCS3 + Dolphin (Week 8-12)
- Full platform expansion (Month 4-6)

**Strategic advantage:**
- Every emulator user gets AI Companion automatically
- Native C++ integration (faster, more reliable)
- Gentech becomes recognized contributor to multiple emulators
- One AI core, unlimited emulator expansion

**Next move:** Forge reads this doc → confirms build plan → we execute.