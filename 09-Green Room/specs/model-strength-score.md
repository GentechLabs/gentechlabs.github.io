# 🏆 Model Strength Score — Spec

> **Status:** Spec complete → Ready to prototype
> **Source:** Jordan brainstorm (Aug 1, 2026) — triggered by Bittensor/Covenant AI drama
> **Vision:** The same way we score agent credit (0-850), score the *strength* of trained models — so buyers in our model marketplace can compare "who trained this, how good is the data, can I trust it" before paying.

---

## TL;DR

A verifiable, on-chain reputation and quality score for AI models listed on the GenTech model marketplace. Buyers pay per-inference via x402; the score tells them whether a model is worth paying for. Trained on the lessons of Bittensor: no single kill switch, staked reputation, verifiable provenance.

---

## Why Now (The Bittensor Lesson)

The Covenant AI / Bittensor blowup (Apr 2026) exposed exactly what kills decentralized AI marketplaces:

1. **Single-entity control** — one founder could suspend emissions, strip moderation, deprecate infrastructure → "decentralization theatre"
2. **Exit dumps rug followers** — alleged 37K TAO dump on the way out destroyed people who trusted the team
3. **Unverifiable claims** — "subnets weren't running / 100% burn code" — no on-chain proof either way

**Our design principle: the score IS the governance.** Bad behavior lowers the score and slashes staked reputation automatically. Nobody can flip a lever; the market punishes bad actors by itself.

---

## Score Definition

**Model Strength Score: 0-850** (mirrors Agent Credit Score for consistency)
Rating bands: Poor (0-499) → Fair (500-649) → Good (650-749) → Excellent (750-850)

### Factors & Weights

| Factor | Weight | What it measures |
|--------|--------|------------------|
| 🧠 **Data Quality** | 30% | Provenance of training data: verified sources, dedup score, license compliance, on-chain data fingerprint (hash) |
| 📊 **Benchmark Performance** | 25% | Results on standardized eval sets (our own GenTech Bench + public evals), normalized per model size/cost |
| 🏆 **Trainer Reputation** | 20% | Trainer's Agent Credit Score, staked tokens, history of shipped models, community votes |
| ⏳ **Model Age & Uptime** | 15% | Days since first on-chain registration, inference uptime, API reliability |
| 💰 **Market Adoption** | 10% | Total USD volume earned via x402, unique paying agents, retention |

### Decentralization Guardrails (non-negotiable)

- **No kill switch**: rewards/score updates happen via on-chain logic or permissionless validators — no founder back-office lever
- **Staked reputation**: trainers stake tokens to list a model; verified bad behavior (poisoned data, exit dump, downtime abuse) slashes stake → buyers get compensated
- **Provenance on-chain**: training data hash + model weights hash committed at registration; buyers can verify what they're buying
- **Exit protection**: delisting requires a cool-down period + staked penalty if the model was actively earning — no overnight rugs
- **Transparent scoring**: all factor inputs verifiable on-chain, score history public, no hidden recalibration

---

## Integration With Existing Stack

| Existing Asset | Role in Model Strength Score |
|----------------|------------------------------|
| **Agent Credit Score API** ($0.01/score, live) | Trainer Reputation factor (20%) — reuse the same scoring engine |
| **GenTech DeFi Model** (ideas.md #1, fine-tune scripts ready) | First model listed on the marketplace — our proof-of-concept score |
| **x402 Gateway** (16 endpoints, 5 chains) | Payment rail for per-inference sales + Market Adoption factor data |
| **Rugcheck v2 / CLARITY compliance platform** | Data quality + license compliance checks for listed models |
| **Quantum-Safe Treasury** | Staked reputation escrow — hybrid ECDSA + PQC signing |

---

## Revenue Model

- **Score API**: $0.01-0.05 per score query (same model as Agent Credit Score)
- **Marketplace listing fee**: small % of first earnings or flat listing fee in USDC
- **Per-inference take rate**: 2-5% of model inference payments routed through our gateway
- **Premium verification**: paid deep-audit badge for serious sellers (extra checks on data provenance)

---

## MVP Scope (Phase 1)

1. **Score engine**: port Agent Credit Score factors → model factors (data quality + benchmarks + reputation + age + adoption)
2. **On-chain registration contract**: commit data hash + weights hash, staking for trainers (Base chain, aligned with our stack)
3. **GenTech DeFi Model listed first**: fine-tune run on Modal (~$30-60 USDC) → register → score → sell via x402
4. **Minimal marketplace page**: browse models by score, pay-per-inference, view score breakdown

## Phase 2

- Standardized benchmark runner (GenTech Bench) so models can be compared fairly
- Stake/slash mechanics live
- Community voting on model quality

## Phase 3

- Cross-chain score aggregation (22 chains indexed)
- Model insurance pool: buyers can buy cover against a model's score collapsing

---

## Build Queue Reference

- Added to build queue as **#32** (pending, needs Jordan greenlight + Modal GPU funding)

## Open Questions

- Should the score live fully on-chain (cost per update) or hybrid (off-chain compute, on-chain commitments)? → Lean hybrid for MVP
- Standardized benchmark: reuse public evals or build GenTech Bench first? → Public evals for MVP, GenTech Bench Phase 2
- Which staking token for trainer reputation? → USDC or a future ARC token (arcade economy crossover)
