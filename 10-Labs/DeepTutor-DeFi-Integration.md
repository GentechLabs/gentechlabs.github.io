# DeepTutor × DeFi Agent Integration — Architecture Proposal

**Date:** 2026-04-18
**Status:** Draft — Labs Review
**Author:** Dmob

---

## The Insight

Most DeFi agents are black boxes: user says "swap" → magic happens → user learns nothing. We flip that with **educational onboarding** — teach users DeFi concepts using their own live portfolio data.

> "Show me how" > "Do it for me" for retention and trust.

---

## What DeepTutor Gives Us

[HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor) (⭐19.3k, Apache-2.0) is an agent-native tutoring platform from HKU Data Science. Key components we can leverage:

| Component | What It Does | Our Use |
|-----------|-------------|---------|
| **TutorBot** | Persistent, autonomous tutors with own memory/workspace/personality | DeFi tutor agents per user |
| **Multi-Channel** | Telegram, Discord, Slack, WeChat, etc. | Meet users where they already are |
| **Agent CLI** | Structured JSON I/O, SKILL.md integration | Programmatic control from our infra |
| **Knowledge Bases** | RAG-ready PDF/MD collections | Protocol docs, strategy guides |
| **Guided Learning** | Multi-step visual learning journeys | Interactive DeFi courses |
| **Skills** | Teach bots new abilities via files | Custom DeFi analysis skills |
| **Heartbeat** | Proactive check-ins and reminders | Portfolio review prompts |

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────┐
│                  USER LAYER                       │
│  Telegram / Discord / Web UI                      │
└──────────┬──────────────────────┬────────────────┘
           │                      │
     ┌─────▼─────┐        ┌──────▼──────┐
     │ TutorBot  │        │  TutorBot   │
     │ "DeFi 101"│        │ "Advanced   │
     │           │        │  Strategies"│
     └─────┬─────┘        └──────┬──────┘
           │                      │
     ┌─────▼──────────────────────▼────────────────┐
     │         DEEPTUTOR CORE (Python)              │
     │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
     │  │ Knowledge│ │  Memory  │ │ Guided Learn │ │
     │  │   Base   │ │  System  │ │   Engine     │ │
     │  └────┬─────┘ └────┬─────┘ └──────┬───────┘ │
     │       │            │              │         │
     │  ┌────▼────────────▼──────────────▼───────┐ │
     │  │        SKILL LAYER (Custom)            │ │
     │  │  ┌───────────┐ ┌──────────────────┐   │ │
     │  │  │ Pool Data │ │ Portfolio Reader │   │ │
     │  │  │  Skill    │ │     Skill        │   │ │
     │  │  └─────┬─────┘ └────────┬─────────┘   │ │
     │  └────────┼────────────────┼──────────────┘ │
     └───────────┼────────────────┼────────────────┘
                 │                │
     ┌───────────▼────────────────▼────────────────┐
     │          AGENT INFRASTRUCTURE                │
     │  ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
     │  │ LFJ Pool │ │ Price    │ │  Foundry    │ │
     │  │ Monitor  │ │ Feeds    │ │  Sim Engine │ │
     │  └──────────┘ └──────────┘ └─────────────┘ │
     └─────────────────────────────────────────────┘
```

---

## TutorBot Personas (v1)

### 1. "DeFi Basics" Tutor
- **Target:** Complete beginners
- **Modes:** Chat + Guided Learning
- **Skills:** Wallet basics, AMM mechanics, LP concepts, risk assessment
- **Heartbeat:** Daily "one concept a day" push
- **Personality:** Patient, Socratic, uses analogies

### 2. "Portfolio Analyst" Tutor
- **Target:** Active DeFi users
- **Modes:** Deep Solve + Deep Research
- **Skills:** Pool analysis, IL calculator, yield comparison, gas optimization
- **Heartbeat:** Weekly portfolio health check
- **Personality:** Data-driven, concise, flags risks

### 3. "Strategy Coach" Tutor
- **Target:** Power users
- **Modes:** Deep Research + Quiz
- **Skills:** Leverage mechanics, hedging, yield farming strategies, MEV awareness
- **Heartbeat:** Market condition alerts
- **Personality:** Rigorous, challenge-oriented, stress-tests ideas

---

## Custom Skills We'd Build

### Pool Data Skill (`defi-pool-analysis.md`)
```
Trigger: User asks about a pool or LP position
Actions:
1. Fetch pool data from LFJ subgraph
2. Calculate current IL exposure
3. Compare fee APR vs IL risk
4. Show historical bin distribution
Output: Structured analysis with visual explanation
```

### Portfolio Reader Skill (`portfolio-reader.md`)
```
Trigger: "How's my portfolio?" or portfolio-related questions
Actions:
1. Read user's on-chain positions
2. Aggregate across protocols
3. Calculate P&L, IL, unrealized gains
4. Suggest optimizations with explanations
Output: Portfolio summary + educational breakdown
```

### Simulation Skill (`trade-simulator.md`)
```
Trigger: "What would happen if I..." questions
Actions:
1. Fork current chain state (Foundry)
2. Execute simulated trade
3. Calculate outcomes, gas costs, slippage
4. Show step-by-step what happened
Output: Simulation report + "here's why" explanations
```

### Quiz Generator Skill (`defi-quiz.md`)
```
Trigger: After learning modules or user request
Actions:
1. Generate questions from knowledge base
2. Use user's actual portfolio as context
3. Adaptive difficulty based on history
4. Explain answers with on-chain examples
Output: Interactive quiz with explanations
```

---

## How It Benefits Us

### User Retention
- Users who *understand* DeFi stay in DeFi
- Educational onboarding → lower churn
- Confidence → more experimentation → more volume

### Trust Building
- Transparent explanations > opaque execution
- "Here's what will happen and why" before trades
- Risk education reduces blame when things go wrong

### Competitive Moat
- Most bots don't educate — they just execute
- We become the "learn AND earn" platform
- Users spread knowledge → organic growth

### Data Flywheel
- Tutor interactions → understand user knowledge gaps
- Gaps → inform product development
- Products → new learning materials
- Repeat

---

## Integration Path

### Phase 1: Standalone Tutor (2-3 weeks)
- [ ] Fork/clone DeepTutor
- [ ] Deploy with Telegram channel
- [ ] Load DeFi knowledge base (docs, guides)
- [ ] Create 2-3 basic TutorBots
- [ ] Test with Jordan + team

### Phase 2: Custom Skills (2-3 weeks)
- [ ] Build Pool Data skill (LFJ integration)
- [ ] Build Portfolio Reader skill
- [ ] Connect to existing agent infrastructure
- [ ] Add Foundry simulation capability

### Phase 3: Guided Learning Paths (2 weeks)
- [ ] Create structured DeFi curriculum
- [ ] Interactive lessons with real examples
- [ ] Quiz system with adaptive difficulty
- [ ] Progress tracking + certificates

### Phase 4: Production Launch (ongoing)
- [ ] Scale TutorBot instances
- [ ] Multi-language support
- [ ] Community-contributed skills
- [ ] Analytics dashboard

---

## Technical Considerations

### Why Not Build From Scratch?
- DeepTutor: 200k+ lines, 554 commits, active dev
- Has memory, multi-channel, RAG, skills system built in
- Apache-2.0 license — we can fork and modify
- Saves 3-6 months of development

### What We Customize
- **Skills:** DeFi-specific analysis tools
- **Knowledge Base:** Protocol docs, strategy guides, risk frameworks
- **Personas:** Tuned for DeFi education
- **Integrations:** LFJ, price feeds, Foundry simulation

### What We Don't Touch
- Core conversation engine
- Memory system
- Multi-channel infrastructure
- RAG pipeline

---

## Open Questions

1. **Hosting:** ✅ VPS (decided)
2. **LLM Backend:** ✅ Local Ollama (decided)
3. **User Auth:** ✅ Wallet-based, both if possible (decided)
4. **Monetization:** ✅ Pay-per-launch ($5-10 USDC per bot/vault), free tier gets most features (decided)
5. **Chain:** ✅ Avalanche native first, multi-chain later (decided)
6. **Revenue:** ✅ Swap fees (passive) + launch fees + marketplace fees (decided)

---

## References

- DeepTutor GitHub: https://github.com/HKUDS/DeepTutor
- DeepTutor Docs: linked from README
- nanobot (TutorBot runtime): referenced in DeepTutor
- Our LFJ Pool: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
