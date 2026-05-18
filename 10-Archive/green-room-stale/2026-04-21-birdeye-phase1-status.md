# Birdeye BIP Sprint 1 — Phase 1 Status
**Date:** 2026-04-21
**Status:** Scaffolded — awaiting Birdeye API key

## What's Built

### 1. Birdeye x402 Client (`birdeye-x402-client.py`)
- Full API client with caching, error handling, x402 + API key modes
- Endpoints: token overview, security, trade data, trending, new listings
- `full_token_report()` aggregates all three data sources per token
- CLI for quick testing: `python3 birdeye-x402-client.py overview -t SOL`
- Config at `~/.hermes/scripts/birdeye-config.json`

### 2. Enhanced LP Monitor v2 (`lp-range-monitor-v2.py`)
- Birdeye-first with DexScreener fallback (graceful degradation)
- **New analytics when Birdeye available:**
  - Security score (0-100)
  - Top holder concentration %
  - Buy/sell pressure ratio
  - Unique traders 24h
  - Market cap
- Falls back cleanly to DexScreener when no API key

### 3. Config Template
- `birdeye-config.json` — ready for API key
- Supports both API key and x402 payment modes

## Blockers
- [ ] **Birdeye API key** — register at `bds.birdeye.so`
- Once key is set, monitor auto-enriches with Birdeye analytics

## Phase 2 (Option C) Roadmap
- Layer x402 USDC payment flow on top
- PayAI (Solana) or Coinbase CDP (Base) settlement
- Agent autonomously pays per request — no subscription needed
- Estimated 6-8 hrs after Phase 1 is live

## Files
- `/root/vaults/gentech/03-Strategies/scripts/birdeye-x402-client.py`
- `/root/vaults/gentech/03-Strategies/scripts/lp-range-monitor-v2.py`
- `/root/vaults/gentech/03-Strategies/scripts/birdeye-config.json`
