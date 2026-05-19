---
title: "Almanak × AAE Integration — Big Brain Discussion"
date: 2026-04-29
type: discussion
tags: [defi, aae, almanak, strategy, architecture]
status: open
---

# Almanak × AAE Integration Discussion

## Context
Jordan found [Almanak](https://almanak.co) — a production DeFi strategy framework (Python, Apache 2.0, 53 stars, 1M+ lines). DMOB did a full codebase assessment. The question is: what's the integration play?

## What Almanak Is
- Intent-based Python SDK for autonomous DeFi strategies
- 12 chains, 20+ protocols (including TraderJoe V2 on Avalanche)
- Non-custodial execution via Safe wallets
- Backtesting engine (Monte Carlo, Optuna parameter sweeps)
- Gateway gRPC sidecar for secure execution
- 100+ demo strategies

## What AAE Already Has
- Identity layer (Kite Passport)
- Payments (Ampersend)
- Marketplace (AAS Marketplace)
- LP position monitoring (custom Python scripts)
- Cron-based alerts + rebalancing suggestions

## What AAE Is Missing
- Robust execution layer for actual DeFi strategies
- Backtesting before deploying ranges
- Proper state management (currently JSON files)
- Intent abstraction (currently raw contract calls)

## The Three Paths

### Path A: Adopt TraderJoe SDK Only
Extract their `traderjoe_v2` connector. Replace raw eth_call reader with production SDK. Get pool discovery, swap quotes, LP math, receipt parsing. Low risk, high value.

### Path B: Use Backtesting Engine
Run historical backtests on WAVAX/USDC to optimize ranges. Use Optuna for parameter sweeps. Validate before deploying.

### Path C: Full Framework Adoption
Rewrite AAE as an Almanak strategy. Use intents, gateway, state management. Maximum capability but maximum complexity.

## Open Questions
1. Does the Gateway architecture make sense for a single-pool operation, or is it overkill?
2. Should AAE adopt Almanak as a dependency, or fork the connector logic?
3. What's the right boundary between "AAE does identity/payments" and "Almanak does execution"?
4. Could the Intent system replace our cron-based rebalancing with something more declarative?
5. Is there a hackathon angle here? Almanak + AAE identity = DeFi agent with identity layer?

## Assessment
Full report: `02-Labs/Assessment-Almanak-2026-04-29.md`
