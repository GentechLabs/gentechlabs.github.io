# GTA Execution Engine — Build Plan

**Date:** 2026-08-03
**Greenlit by Jordan:** Aug 3 ("yes build this next")
**Skill:** develop-and-verify (DEV: DeepSeek V4 Flash → AUDIT: Kimi K2.7)
**Driving thesis:** `09-Green Room/specs/gta-product-thesis.md` — GTA = open execution + authorized proxy layer.

## PROGRESS (Aug 3)
- ✅ **gta_executor.py** — decision + order-plan engine. 9/9 tests green. Cron `a11f9e0205f3` (every 3h dry-run) live.
- ✅ **gta_coinbase_leg.py** — Coinbase CDP spot leg. 6/6 tests green (incl. live BTC quote). **Coinbase CDP key verified working.**
- ✅ CDP key stored in profile `.env` (CDP_API_KEY_ID/SECRET), chmod 600.
- ✅ GTA Product Thesis captured: `09-Green Room/specs/gta-product-thesis.md`.
- ⏳ **NEXT (Aug 4, Jordan):** Robinhood KYC/OAuth (perp leg) + fund Coinbase wallet (real spot exec).
- 🔭 **NEXT (Gentech):** Composio research (authorized-proxy layer).

## Key technical findings (verified)
- CDP `get_swap_price` = read-only basis oracle (works unfunded). Real swap needs funded account + contract addresses + raw integer amounts (not tickers).
- Only **cbBTC** verified tradeable on Base today (cbETH no liquidity; PAXG/SOL etc. need real addresses — do NOT invent them).
- HL execution = US gray zone → GTA execution is US-venue-native.

## Goal
Wire GTA from **detection-only** to **execution-capable**: take the arb scan state
(`.gta-arb-state.json` from gta-arb-monitor), apply trade rules, produce an order plan,
and — when a real key is available — execute. Ships with a **dry-run/simulation path**
that is fully testable TODAY without a live key.

## Hard blockers discovered (must be reported, not hidden)
1. **No Hyperliquid execution private key on this box.** tradesta-signal/watcher are
   read-only. Real HL order placement needs `Account.from_key(PRIVATE_KEY)`.
2. **Bridge to HL historically broken** (Across relayers failed, funds stuck Jul 26).
   `deposit_v3_fixed.py` referenced in skill is MISSING.
3. **KeeperHub needs `kh_` org API key** — Jordan has NOT provided it yet (blocked from
   the KeeperHub hackathon plan, queue item #1).

## What IS buildable + verifiable today
An **execution engine module** (`gta_executor.py`) that:
- Reads `.gta-arb-state.json` (already produced by the monitor)
- Applies the rule set from the agentic-arbitrage skill:
  - Report ≥ 5 bps, **Execute ≥ 10 bps**, Close < 3 bps
  - Stop-loss: spread widens > 50 bps from entry
  - Max hold: 7 days (funding erodes profit)
  - Funding cost check (fetch HL funding rate)
- Emits a **decision** (ENTER / HOLD / CLOSE / SKIP) with reasons
- Produces an **order plan** (symbol, side, size, venue)
- **Dry-run mode** (default): logs the exact order that WOULD execute, no funds move
- **Real mode**: executes ONLY if `GTA_HL_KEY` env var is set, else exits with clear error
- Atomic, no partial state, idempotent position tracking

## Files
- `scripts/gta_executor.py` — the engine
- `scripts/test_gta_executor.py` — TDD test suite (runs with no key, uses dry-run)

## Acceptance criteria (Karpathy gates)
- [ ] `test_gta_executor.py` passes 100% with no env key
- [ ] Executor reads real `.gta-arb-state.json` and emits correct decision for PAXG (10.04 bps ≥ 10 → ENTER)
- [ ] Dry-run produces a complete order plan and moves NO funds
- [ ] Real mode with no key → clear "missing GTA_HL_KEY" error, exit non-zero
- [ ] No hardcoded secrets, no wallet addresses in code

## Non-goals (anti-temptation)
- NOT building a new bridge (blocked — report it)
- NOT auto-executing without a key (impossible + unsafe)
- NOT adding KeeperHub integration yet (blocked on kh_ key)
