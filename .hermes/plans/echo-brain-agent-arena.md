# Execution Plan — Echo Brain (Agent Arena Integration)

**From:** Build Brief (09-Green Room/build-logs/echo-brain-build-brief.md)
**Target Repo:** github.com/ProtoJay4789/Agent-Arena
**Date:** 2026-05-22

---

## Tasks

### Task 1: Brain Core — Memory Store
**Files:** `js/engine/brain.js`, `tests/brain.test.js`
**What:** SQLite-backed memory store with 4-layer schema (working, short-term, long-term, connections)
**Verify:** Unit tests — store memory, retrieve by recency, retrieve by relevance, decay old memories

### Task 2: Trade Tagger
**Files:** `js/engine/trade-tagger.js`, `tests/trade-tagger.test.js`
**What:** Tags every trade action with context (market state, reasoning prompt, emotional inference, outcome)
**Verify:** Feed simulated trades → confirm tags stored correctly in brain

### Task 3: Memory Retrieval Pipeline
**Files:** `js/engine/memory-retrieval.js`, `tests/memory-retrieval.test.js`
**What:** Embed input → search long-term + short-term → combine with working memory → return context
**Verify:** Query "what did I do last week" → returns correct trade history with context

### Task 4: Pattern Detector
**Files:** `js/engine/pattern-detector.js`, `tests/pattern-detector.test.js`
**What:** Analyze trade history for patterns (overtrading, FOMO, timing, win rate by day)
**Verify:** Feed 2 weeks simulated data → confirm pattern detection outputs

### Task 5: Bot Companion UI
**Files:** `js/ui/bot-companion.js`, `css/bot-companion.css`
**What:** In-game bot interface — chat-style consultation, weekly recap display, pattern alerts
**Verify:** Visual check — bot panel renders, accepts input, displays responses

### Task 6: Weekly Reflection Engine
**Files:** `js/engine/weekly-reflection.js`, `tests/weekly-reflection.test.js`
**What:** Cross-week comparison ("week 1 vs week 3"), performance deltas, behavioral changes
**Verify:** Feed 3 weeks data → confirm reflection text is meaningful and accurate

### Task 7: Integration + Smoke Tests
**Files:** `smoke_test.js` (update), `js/engine/app.js` (update)
**What:** Wire brain into existing Agent Arena game loop, run full smoke test suite
**Verify:** All existing + new tests pass, game loop still works with brain attached

---

## Execution Order

Tasks 1-4 can be partially parallelized (brain core + tagger together, then retrieval + patterns).
Task 5 depends on Task 1-3.
Task 6 depends on Tasks 1, 4.
Task 7 is integration — last.

## Anti-YAGNI Check

- ✅ SQLite per player (not ChromaDB cloud) — game-local, no infra
- ✅ Basic patterns first (frequency, timing) — not ML models
- ✅ In-game bot first — not standalone Echo app
- ✅ Simulated trades first — no real wallet connection
