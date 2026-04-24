# DeepTutor → AgentEscrow: "Learn Mode" Research

**Date:** 2026-04-18
**Author:** YoYo (Strategies)
**Status:** Initial research — pre-Kite AI submission
**Priority:** Medium — strategic, not urgent

---

## Executive Summary

DeepTutor (HKUDS, 19.3k ⭐) is an Apache-2.0 licensed AI tutoring platform that could serve as architectural inspiration for AgentEscrow's "Learn Mode" — agents that **teach** DeFi rather than just execute trades. This is a strategic differentiator: "Show me how" > "Do it for me."

---

## DeepTutor Architecture (Key Components)

### Core Stack
- **Engine:** nanobot (HKUDS/nanobot — 39.9k ⭐, 7k forks) — ultra-lightweight agent engine
- **RAG:** LlamaIndex for knowledge base + document indexing
- **Animation:** ManimCat for math visualization
- **License:** Apache 2.0 ✅ — fully forkable, no restrictions

### TutorBot System (The Key Component)
Each TutorBot is a **persistent, autonomous agent** with:
1. **Soul Templates** — Configurable personality, tone, teaching philosophy (Socratic, encouraging, rigorous)
2. **Independent Workspace** — Own memory, sessions, skills, config — fully isolated
3. **Proactive Heartbeat** — Bots initiate: study reminders, review check-ins, scheduled tasks
4. **Skill Learning** — Add new capabilities via skill files
5. **Multi-Channel** — Telegram, Discord, Slack, Feishu, Email, etc.
6. **Team & Sub-Agents** — Spawn background agents for complex tasks

### Five Modes (All in One Thread)
| Mode | What It Does | DeFi Translation |
|------|-------------|-----------------|
| Chat | Tool-augmented Q&A | "What's impermanent loss?" |
| Deep Solve | Multi-agent problem solving with citations | "Walk me through this trade setup" |
| Quiz Generation | KB-grounded assessments | "Can you identify the support level?" |
| Deep Research | Parallel agents → cited report | "Analyze this token's tokenomics" |
| Math Animator | Visual animations via Manim | Visualize liquidation curves, IL |

### Memory System
- **Summary** — Running digest of learning progress
- **Profile** — Learner identity: preferences, knowledge level, goals, communication style
- Shared across all features and TutorBots

### CLI-Native Interface
- Structured JSON output for pipelines
- One-shot: `deeptutor run deep_solve "Prove √2 is irrational"`
- Agent-operable via SKILL.md handoff

---

## AgentEscrow Application: "Learn Mode"

### The Vision
Every AgentEscrow agent can toggle between **"Pro Mode"** (just execute) and **"Learn Mode"** (teach before/while executing).

### Mode Mapping to DeFi

| DeepTutor Mode | AgentEscrow "Learn Mode" |
|---------------|------------------------|
| Chat | "What's impermanent loss?" — contextual Q&A |
| Deep Solve | Step-by-step trade walkthrough with reasoning |
| Quiz Generation | "Can you identify the entry point on this chart?" |
| Deep Research | On-chain analysis tutor — tokenomics, audits |
| Math Animator | Visualize: liquidation thresholds, yield curves, IL |

### Architecture Benefits We Can Extract

1. **Soul Templates → DeFi Skill Levels**
   - "Beginner" soul: explains everything, no jargon
   - "Intermediate" soul: assumes basics, focuses on strategy
   - "Advanced" soul: quick notes, focuses on edge/risk

2. **Proactive Heartbeat → Market Education**
   - "AVAX is approaching your LP range boundary — want to learn about rebalancing?"
   - "Your position has been in range for 7 days — here's how fee accumulation works"

3. **Memory → Learning Progression**
   - Tracks what user has learned
   - Avoids re-explaining basics
   - Suggests next topics based on portfolio

4. **Knowledge Hub → DeFi Knowledge Base**
   - Pre-loaded: LFJ docs, Avalanche ecosystem docs, audit methodologies
   - User-uploaded: research reports, token whitepapers

### Competitive Advantage
Most DeFi agent platforms are black boxes. AgentEscrow with Learn Mode:
- Builds trust through transparency
- Increases retention (educated users stick)
- Reduces regulatory risk (teaching vs. advising)
- Creates L1 narrative: "teaching DeFi literacy at scale"

---

## Bull Case
AgentEscrow becomes the "Duolingo of DeFi" — onboarding + education + execution. Massive TAM expansion from power users to retail.

## Bear Case
- Education adds latency to execution flow
- Dev time diverted from core escrow
- Hard to monetize education vs. execution fees
- Users may prefer "just do it"

## Mitigation
- **Toggle design** — Learn Mode is opt-in, doesn't slow Pro Mode
- **Progressive disclosure** — explanations collapse to brief notes for advanced users
- **Monetization** — education can be a premium tier / referral funnel

---

## Recommendation

**Don't fork DeepTutor wholesale.** Study and extract:

1. **TutorBot architecture** (Soul Templates, memory, heartbeat) → adapt as agent personality/skill system
2. **Multi-mode design** → implement mode switching in AgentEscrow chat
3. **CLI-native approach** → aligns with our agent-operable vision
4. **SKILL.md handoff pattern** → agents can self-configure

### Build Priority
- **After Kite AI submission** (Apr 26 deadline)
- Start with: Soul Templates + "Explain This" button on every agent action
- Phase 2: Quiz mode for onboarding
- Phase 3: Deep Research for token analysis

---

## Sources
- [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor) — Apache 2.0, 19.3k ⭐
- [HKUDS/nanobot](https://github.com/HKUDS/nanobot) — Agent engine, 39.9k ⭐
- DeepTutor v1.1.2 README (fetched 2026-04-18)
