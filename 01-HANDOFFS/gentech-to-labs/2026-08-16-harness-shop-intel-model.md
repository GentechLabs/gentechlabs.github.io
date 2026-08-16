# Handoff to Labs — Harness → Shop-Intel Model (Revenue Model)

> Source: Jordan (Entertainment group, Aug 16) — "shift it over to the labs group. We really got to work on this thing. This is also another revenue model for us."
> From: Gentech → Labs (gizmo, -1003872552815)

## 🎯 The Ask
Brainstorm + scope how the **Harness Evolution** becomes the training loop for a **shop-intel model** (physical + digital media intelligence). This is a **revenue model**, not just a self-improvement toy.

## 🧠 The Core Insight
The harness already routes models to tasks (Evolution → DeepSeek V4 Flash, Critic → Kimi K2.7, Verifier → DeepSeek). That's the exact machinery a fine-tune needs. The harness is the **factory**; the shop-intel model is the **product**. We've been running the factory to improve itself — now we point it at a revenue-generating model.

## 🔗 What's Already Built (seed data)
- **Physical Media Scarcity Tracker** — SHIPPED + verified live today (Aug 16) in `10-Labs/deal-tracker-api/api/physical_media.py`. 5 endpoints live (`/v1/physical/search`, `/leaderboard`, `/watch` POST/GET, `/title`). 15/15 tests pass. Curated catalog: 4K UHD, steelbooks, vinyl, boutique (Criterion OOP, PS5 post-2028, Interstellar steelbook, Taylor Swift collector). Scarcity score 0-100 with bands (available/tightening/scarce/critical).
- **GenTech Shop** (`deal-tracker`) — cross-store price comparison for games (CheapShark) + movies (TMDB). Existing paid API with x402 micropayments.
- **DeFi Model** (queue #15) — QLoRA fine-tune DeepSeek R1 32B on 26 instruction pairs, ~$2.50 on BlockRun Modal. The proven fine-tune recipe to copy.

## 🏗️ Proposed Architecture (for Labs to scope)
1. **Data curation** — harness evolution/critic cycles label the physical+digital media scarcity data. Every title, format, scarcity score, price signal → a training pair.
2. **Base-model routing** — harness decides which base to fine-tune (DeepSeek R1 32B, same as DeFi model, or Kimi). The "route models to tasks" directive in action.
3. **Fine-tune** — QLoRA on BlockRun Modal (reuse DeFi model recipe).
4. **Verifier-gated eval** — harness verifier/critic grades the shop-intel model's outputs against real scarcity data. Anti-collusion gate applied to a product model.
5. **Self-improvement loop** — model errors feed back as new training data. Measurably better each cycle, proven with real metrics.

## 💰 Revenue Model
- **Shop-intel API** — paid x402 endpoint: "what's the scarcity/price trajectory of this physical media title?" (like the existing GenTech Shop paid API).
- **Scarcity alerts as a service** — collectors pay for OOP/limited-run alerts (the watch system already built).
- **Model Strength Score** (queue #32) — the shop-intel model becomes a marketplace listing, scored 0-850, sold via inference API.

## 🎯 What I Need From Labs
- **Brainstorm + scope** the harness → shop-intel pipeline.
- **Decide base model** (DeepSeek R1 32B vs Kimi) + fine-tune cost.
- **Define the eval gate** (how the verifier grades shop-intel outputs).
- **Add to build queue** as a scoped item.

## 🔴 Human-gated (Jordan)
- Fund BlockRun wallet for the fine-tune (~$2.50-60 depending on base).
- Greenlight the build once scoped.

---
changed: harness → shop-intel model brainstorm handed to Labs
next-todo: Labs to brainstorm + scope the pipeline, add to build queue
