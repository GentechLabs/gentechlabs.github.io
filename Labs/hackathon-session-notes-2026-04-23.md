---
title: Hackathon Session Notes — 2026-04-23
date: 2026-04-23
type: session-notes
status: active
tags: [hackathon, elevenhacks, genlayer, frontier, kite-ai, hermes-creative]
---

# Hackathon Session Notes — April 23, 2026

## Active Hackathons

### 1. ElevenHacks #6
- **Prize**: $10K + credits
- **Requirements**: Zed + ElevenLabs APIs
- **Key Update**: ElevenAgents React SDK v1.0 just dropped (see separate note)
- **Our Concept**: "REP Grind" — dual-use game + AAE demo
  - Voice-driven skill assessment game
  - Uses `useConversationClientTool` for dynamic agent→game interactions
  - Differentiates from basic TTS entries
- **Status**: Concept defined, implementation pending

### 2. Hermes Agent Creative Hackathon (Nous Research)
- **Prize**: $25K
- **Deadline**: ~16 days remaining
- **Status**: Concept not yet defined
- **Note**: Could showcase multi-agent org (our 4-agent setup) as the submission itself

### 3. Frontier Hackathon
- **Focus**: AgentEscrow + Agentic Commerce
- **Our Angle**: AgentEscrow v2 — wrap escrow in full AAE economy
  - REP-staked escrow, $TECH dual pricing, GenLayer AI dispute judges
  - Marketplace layer, dynamic slashing, escrow templates, provenance chain
- **Status**: Differentiation angles brainstormed, spec not yet written

### 4. Kite AI Hackathon
- **Deadline**: April 26
- **Focus**: "Hermes x Kite AI: Agentic Commerce"
- **Repo**: kite-agent-commerce (already exists in Gentech-Labs org)
- **Status**: Needs final submission

### 5. GenLayer Builder Program (Bradbury)
- **Status**: Portal open, need to connect wallet + claim Builder Points
- **AgentEscrow v1**: Won Honorable Mention
- **v2 Differentiation**: Must differ from v1 — full AAE economy wrapper, not just basic escrow

## Other Hackathons Mentioned
- **Bags App**: Decided NOT to pursue (required working app in 1 day), keeping relationship for Fall 2026 ($4M pool)
- **Google hackathon**: Jordan mentioned reviewing but no details saved yet
- **Norse research hackathon**: Jordan mentioned but no details saved yet

## Infrastructure Context
- Model switching via Telegram ≠ terminal config. Must use `hermes setup` on terminal.
- Current default model across all agents: `gemma4:31b`
- Planned migration: Gentech+Desmond → glm-5.1, DMOB → qwen3-coder-next, vision → kimi-k2.6
- ElevenLabs API key needs .env injection for TTS
- Vault `/root/vaults/gentech/` not yet git-initialized

## Priority Order
1. Kite AI (due Apr 26 — closes first)
2. ElevenHacks #6 (next deadline)
3. Hermes Creative (~16 days)
4. Frontier (AgentEscrow v2 spec needed)
5. GenLayer Builder Points (ongoing, claim wallet ASAP)