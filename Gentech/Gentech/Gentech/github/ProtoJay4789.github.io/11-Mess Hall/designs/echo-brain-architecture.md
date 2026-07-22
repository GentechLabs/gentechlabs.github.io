# 🧠 Echo — Personal AI Brain Architecture

**Date:** 2026-05-22
**Status:** 🟢 Approved (Green-lit May 22, 2026)
**Product Name:** Echo (working) — "Talk to an agent that remembers you"

---

## Problem

Every AI product today has amnesia. You tell ChatGPT something personal, it's gone after the session. You build context in Claude, it vanishes when the window closes. The "second brain" concept exists in tools like Obsidian, but those are:
- Local files (not accessible across devices)
- Manual (you have to organize them)
- Not conversational (you can't *talk* to your notes)

**The gap:** No product combines persistent memory + conversational interface + cross-domain intelligence (personal + financial + health) in one brain.

---

## Core Concept

Build a personal brain for each user that:
1. **Remembers** — every conversation, every fact, every preference
2. **Connects** — links related memories across time and topics
3. **Reflects** — surfaces patterns the user hasn't noticed
4. **Evolves** — the brain gets smarter about *you* the more you use it

Not a therapist. Not a chatbot. A **companion that listens, connects dots, and makes you feel heard.**

---

## Brain Architecture

### Layer 1: Working Memory
- Current conversation context
- Active topic detection
- Emotional state inference
- Session-level summarization

### Layer 2: Short-Term Memory
- Last 7-30 days of conversations
- Recent decisions and their context
- Ongoing projects/goals
- Auto-decays unless reinforced

### Layer 3: Long-Term Memory
- Distilled insights (not raw transcripts)
- Core identity facts (name, preferences, relationships)
- Life events and milestones
- Emotional patterns and triggers
- Financial history and decisions

### Layer 4: Connection Graph
- Links between related memories
- Cross-domain associations (stressed about X → spent more on Y)
- Temporal patterns (every March you feel Y)
- Relationship mapping (person A → topic B → emotion C)

---

## Technical Stack

### Storage
- **SQLite** per user — structured facts, preferences, metadata
- **ChromaDB** or **Qdrant** — vector embeddings for semantic search
- **JSON documents** — flexible memory objects with nested context

### Embedding Pipeline
- Each conversation → summarized → embedded → stored
- Similarity search for relevant context retrieval
- Periodic consolidation: short-term → long-term

### Memory Retrieval
```
User says something →
  1. Embed the input
  2. Search long-term for relevant memories (top-k)
  3. Search short-term for recent context
  4. Combine with working memory
  5. Generate response with full brain context
```

### Auto-Consolidation (Cron)
- Daily: distill conversations into insights
- Weekly: identify patterns across the week
- Monthly: update core identity model
- Decay: fade memories not reinforced by new conversations

---

## DeFi Integration

This is where it gets powerful. The brain doesn't just remember what you *said* — it remembers what you *did*.

### DeFi Memory Layer

**Transaction Context:**
- Every swap, LP position, borrow, repay gets tagged with:
  - Market conditions at time of execution
  - Your stated reasoning (from conversation)
  - Emotional state (inferred from conversation patterns)
  - Outcome (profit/loss, how much, how long)

**Pattern Detection:**
- "You tend to panic-sell when ETH drops more than 8% in a day"
- "Your best trades happen on Tuesdays- Thursdays when you're well-rested"
- "You've lost $2,400 chasing yield on protocols you researched for <5 minutes"

**Decision Journaling:**
- Auto-log every DeFi decision with context
- Before/after snapshots
- "You entered this LP position because you said X. Here's how it played out."

**Risk Profiling:**
- Not a static questionnaire — dynamic risk profile based on actual behavior
- Updates as your patterns change
- Alerts when you're deviating from your own established patterns

### DeFi Companion Features

1. **Pre-Trade Reflection**
   - "You're about to swap $5K into a new token. You've done this 3 times before — want to review how those went?"

2. **Portfolio Narratives**
   - Weekly brain dump: "Here's what happened with your money this week, and here's the story behind the numbers"

3. **Pattern Alerts**
   - "You've made 4 trades today. Your average is 2. Want to take a break?"

4. **Learning Integration**
   - Connect hackathon learnings to real portfolio decisions
   - "You learned about reentrancy in Cyfrin — your vault has a similar pattern, want to review?"

5. **Tax/Audit Memory**
   - Every transaction with reasoning, timestamp, and outcome
   - Exportable for tax reporting
   - On-chain verification via Base/Solana APIs

---

## Agent Arena Integration — Echo as Game Mechanic

**Decision (May 22):** Echo is not a separate product — it's a core mechanic *inside* Agent Arena.

### How It Works In-Game

1. **Every trade is tagged** — reasoning, market conditions, emotional state, outcome
2. **The bot remembers across sessions** — "week 1 you did better at X"
3. **Consultation is gameplay** — players actively ask their bot for context before trading
4. **Emergent narrative** — no hand-crafted story, the bot's reflections *become* the story
5. **Retention loop** — players come back to see what their bot learned, not just their P&L

### In-Game Examples

- Player enters a trade → Bot: "You made a similar move in Week 2 — lost 15%. Different this time?"
- Player asks for advice → Bot: "Your best trades happen when you research for 5+ minutes first"
- Weekly recap → Bot: "You FOMO'd 3 times this week. Week 1 you were more patient — what changed?"
- Pattern alert → Bot: "You've made 6 trades today. Your average is 2. Take a break?"

### Architecture Impact

The 4-layer brain architecture stays the same. The change is the **interface** — instead of a standalone Echo app, the first face is the in-game companion bot. This means:

- Layer 1-4: unchanged
- Brain API: unchanged (products are interfaces)
- **New:** Game-side integration layer (trade tagging, bot consultation UI, weekly reflection prompts)
- **New:** Game state feeds into the brain (portfolio, trade history, time spent, decisions made)

### Why This Is Better Than Separate

- Organic adoption — players discover the brain through gameplay, not onboarding
- Immediate utility — the bot helps you win, not just "feels nice"
- Viral loop — "my bot told me X" is shareable
- Data flywheel — more trades = smarter brain = better advice = more trades

---

## Multi-Product Brain

The same brain architecture powers multiple products:

| Product | Brain Use | DeFi Integration |
|---------|-----------|-----------------|
| **Echo (Companion)** | Emotional support, life patterns | Portfolio narratives, decision journaling |
| **GenTech Tutor** | Student progress, interest mapping | Learn-to-earn rewards, scholarship tracking |
| **Agent Arena** | Trading patterns, game strategy | Real portfolio mirroring |
| **Rugcheck** | Alert history, risk tolerance | Token safety preferences |
| **Daily Digest** | Preference learning, content curation | Market awareness, portfolio alerts |

**Key insight:** One brain per user, many faces. The brain is the platform. Products are interfaces.

---

## Privacy & Security

- **Per-user isolation** — no cross-user memory contamination
- **Encryption at rest** — SQLite encrypted, vectors encrypted
- **User control** — view, edit, delete any memory
- **No training on user data** — brain is for the user only
- **Export portability** — users can take their brain with them
- **DeFi specifics** — wallet addresses hashed, transaction amounts obfuscated in storage

---

## Monetization

### Free Tier
- Working memory + short-term (last 7 days)
- Basic pattern detection
- 1 product integration

### Pro Tier ($9.99/mo)
- Full long-term memory
- Cross-domain connections
- All product integrations
- DeFi decision journaling
- Pattern alerts

### Brain-as-a-Service (Future)
- License the brain SDK to other AI products
- API access for third-party integrations
- White-label brain for enterprises

---

## Alternatives Considered

1. **Obsidian as backend** — rejected: local-only, no API, not scalable
2. **Notion API** — rejected: vendor lock-in, slow, not designed for real-time
3. **Firebase/Supabase** — possible but no semantic search built-in
4. **Custom + vector DB** — chosen: full control, semantic search native, per-user isolation

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│              User Interface                  │
│  (Echo App / Tutor / Arena / Rugcheck)      │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│            Brain API Layer                   │
│  - Memory CRUD                              │
│  - Context Retrieval                        │
│  - Pattern Detection                        │
│  - Consolidation Engine                     │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ SQLite   │ │ ChromaDB │ │ Graph    │
│ Structured│ │ Vectors  │ │ Links    │
│ Facts    │ │ Semantic │ │ Connections│
└──────────┘ └──────────┘ └──────────┘
```

---

## Success Criteria

1. Brain remembers key facts across sessions (no re-introduction needed)
2. Brain surfaces non-obvious connections ("you mentioned X, which relates to Y from 3 months ago")
3. DeFi decision journal auto-captures reasoning + outcome
4. Pattern detection works after 2+ weeks of daily use
5. User can view/edit/delete any memory
6. Multi-product integration works with single brain instance

---

## Next Steps

1. **Prototype brain core** — SQLite + ChromaDB, single user, basic CRUD
2. **Build memory pipeline** — conversation → summary → embed → store
3. **Test retrieval** — can the brain answer "what did I talk about last week?"
4. **DeFi integration MVP** — wallet connection → transaction tagging → context
5. **First product face** — Echo companion MVP with brain backend
6. **User testing** — Jordan as first user, 2-week daily use trial

---

## Related Docs
- [Voice-Cloned Learning Companions](/root/vaults/gentech/Green-Room/designs/voice-cloned-learning-companions.md)
- [Ideas List](/root/vaults/gentech/Green-Room/ideas.md)
- [Agent Arena Design](/root/vaults/gentech/Green-Room/designs/aeg-agent-economy-gaming.md)

---

*"The brain is the platform. Products are interfaces."*
