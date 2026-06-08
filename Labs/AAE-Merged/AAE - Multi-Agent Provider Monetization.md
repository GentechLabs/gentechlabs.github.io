# AAE Multi-Agent Provider Selection & Monetization

**Date:** 2026-04-19
**Source:** Jordan conversation

## Core Idea
Let users select their own LLM provider and model for each agent role — similar to how OpenRouter lets you pick models. This creates a flexible, user-controlled agent ecosystem.

## Monetization Models
1. **Provider Selection** — Users bring their own API keys or pick from bundled providers
2. **Pay-Per-Launch** — Users pay per agent execution, we handle the infrastructure
3. **Hybrid** — Free tier uses default models, premium unlocks provider choice + better models

## Social/Meta Game Layer
This is where it gets interesting for content and engagement:

- **"What combo creates the best trader?"** — Community shares agent configs
- **"Best Staker Setup"** — Yield farmers compare model stacks
- **Leaderboards** — Top-performing agent configurations ranked by returns
- **Config Sharing** — Users publish their agent layer combos, others can fork/replicate
- **Model Wars** — Community debates: GPT-4 vs Claude vs open-source for on-chain analysis

## Agent Layers to Mix & Match
- **Perception Layer** — What model reads/interprets on-chain data?
- **Decision Layer** — What model makes trading/allocation decisions?
- **Execution Layer** — What model handles transaction construction?
- **Social Layer** — What model generates posts/engagement?

## Content Angle
This is *highly* shareable content:
- "We tested 47 model combos for yield farming — here's what won"
- "The $10/month agent stack that outperformed GPT-4 in DeFi"
- Community-created tier lists of model combos by use case
- Live experiments: "We're running 6 agents with different stacks, tracking PnL"

## Technical Notes
- Hermes already supports provider switching (opencode-go, Nous, etc.)
- OpenRouter API provides unified access to 100+ models
- Cost optimization: cheaper models for perception, expensive ones for decisions
- Latency matters: fast models for real-time, slower ones for analysis
