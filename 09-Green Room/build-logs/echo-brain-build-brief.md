# Build Brief — Echo Brain (Agent Arena Integration)

**Date:** 2026-05-22
**Green Light:** Jordan, May 22, 2026 (voice message)
**Design Doc:** 09-Green Room/designs/echo-brain-architecture.md
**Target:** Agent Arena (github.com/ProtoJay4789/Agent-Arena)

---

## What We're Building

Echo — a companion bot inside Agent Arena that remembers the player's trading history, reflects on patterns across weeks, and provides contextual advice. The brain is a game mechanic, not a separate product.

## Scope

### Phase 1: Brain Core (MVP)
- SQLite-based memory store per player
- 4-layer architecture: working → short-term → long-term → connection graph
- Memory pipeline: trade action → context tag → store → retrieve
- Basic pattern detection (trade frequency, timing, outcomes)

### Phase 2: Game Integration
- Trade tagging system (reasoning, market state, outcome, emotional inference)
- Bot consultation UI (player asks bot, bot retrieves relevant memories)
- Weekly reflection engine (cross-week comparisons, pattern surfacing)
- Bot personality layer (warm, honest, slightly competitive)

### Phase 3: Intelligence
- Auto-consolidation cron (daily distillation, weekly patterns, monthly identity)
- Cross-domain connections (stressed about X → spent more on Y)
- Pattern alerts (overtrading, FOMO detection, patience tracking)
- Risk profiling from actual behavior, not questionnaires

## Architecture

```
Player trades in-game
        │
        ▼
┌─────────────────┐
│  Trade Tagger    │ ← market context, reasoning, emotional state
└────────┬────────┘
         ▼
┌─────────────────┐
│  Brain Core      │ ← SQLite (structured) + vectors (semantic)
│  Layer 1-4       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Bot Companion   │ ← consultation UI, weekly recaps, pattern alerts
│  (Game Face)     │
└─────────────────┘
```

## Tech Stack

- **Storage:** SQLite per player (lightweight, game-local)
- **Embeddings:** ChromaDB or in-process vector store
- **Pipeline:** Python or JS (match existing Agent Arena stack)
- **Game UI:** HTML/JS canvas (existing Agent Arena demo pattern)

## Success Criteria

1. Brain stores and retrieves trade context accurately
2. Bot can reference past trades ("you did X in week 2")
3. Weekly reflection generates meaningful comparisons
4. Pattern detection works after 2+ weeks of simulated data
5. Integration doesn't break existing Agent Arena game loop

## Not In Scope (Yet)

- Real wallet connection (game simulation first)
- Multi-user / social features
- Monetization tiers
- Echo as standalone product (game face first)
