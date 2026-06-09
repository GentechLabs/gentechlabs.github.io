---
title: Agent Control Layer — Rain Integration Assessment
created: 2026-05-31
status: active
tier: Tier 1 — Immediate
tags: [AAE, payments, Rain, stablecoins, guardrails, compliance, x402]
---

# Rain — Agent Control Layer Integration Assessment

## Who They Are

**Rain** (rain.xyz) — Stablecoin payments infrastructure company.
- $250M Series C raised
- Mastercard Principal Member
- Visa card issuance (175M+ merchant locations)
- Enterprise-grade stablecoin ↔ fiat on/off ramps

## What They Built

**Agent Control Layer** — Programmatic spending guardrails for AI agents using stablecoins and cards.

### Two Levels of Control

**Agent-level (per-agent):**
- Transaction amount caps
- Merchant/category allowlists
- Spend intervals (daily/weekly/monthly)
- Card expiry windows
- Scoped to specific billers/tasks

**Program-level (per-partner):**
- Max active cards across user base
- Aggregate spend limits
- Unusual activity detection
- Visibility into agent spending patterns

### Enforcement Model

**Pre-transaction enforcement:** Rules are baked into the card/transfer BEFORE the agent acts. A transaction outside parameters **simply doesn't go through.** No post-hoc cleanup needed.

### Already in Production

- **Sponge** (YC-backed) — agent-usable cards on Rain, funded by stablecoins, Visa acceptance
- Agents booking travel, subscribing to software, running procurement, moving money globally

## How This Maps to Our Stack

```
Identity:    ERC-8004 (who is this agent?)
Authority:   ERC-8226/RAMS (is it authorized?)
Spending:    Rain ACL (what can it spend and where?)
Payments:    x402/stablecoins (how does it pay?)
Commerce:    AAE (marketplace + reputation)
```

Rain fills the **spending control layer** between authorization and payment execution.

## Integration Opportunities

### Tier 1 — Immediate
1. **Agent Bill Pay** — AAE agents that automatically pay bills using stablecoins with Rain guardrails
2. **Scoped virtual cards** — Each AAE agent gets a card with specific merchant/amount limits
3. **Rain as payment rail** — x402 + Rain stablecoins = complete agent payment stack

### Tier 2 — Strategic
4. **Rain partnership** — AAE as the marketplace layer for Rain-issued agent cards
5. **Compliance bridge** — RAMS mandates → Rain guardrails → payment execution
6. **Enterprise agent payments** — B2B version for companies deploying agents

## Key Files
- Rain blog: rain.xyz/resources/introducing-the-agent-control-layer
- Rain API docs: docs.rain.xyz
- Sponge (YC): example partner issuing agent cards on Rain
