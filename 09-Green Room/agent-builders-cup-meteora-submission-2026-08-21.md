# Agent Builders Cup — Meteora Submission Draft (2026-08-21)

**Team chosen:** Meteora (Solana-native seat)
**Strategy:** Consigliere — LP Slot Operator (Solana CLMM market-making)
**Code:** `/root/condor/agents/solana_dex_lp_expert/strategies/consigliere/strategy.md`
**Status:** Draft ready → needs wallet fund + final submit before Aug 31

## SCOPE NOTE (Jordan correction Aug 21)
We do NOT have Hyperliquid access. The strategy is scoped to **Solana-only**
CLMM LP market-making (Meteora / Orca / Raydium via Jupiter). The Hyperliquid
perp arb leg is DROPPED from the submission — we don't claim a venue we can't
execute. All copy below reflects Solana-only.

---

## Form Field Drafts (matches the Botcamp "New Strategy" form)

### Strategy Title
**Consigliere — Solana CLMM LP Market-Making Agent**

### Summary
A live execution agent that runs a **fee-yield LP core** on Solana CLMM pools
(Meteora / Orca / Raydium), with per-slot TP/SL and disciplined capital
rotation. One Condor agent, deterministic slot discipline, built on GenTech's
trustless x402 rail.

### Detailed Description

**Description**
Consigliere reads the market, applies judgment, and acts on the builder's
behalf. It runs a single coordinated LP loop on a ~2-minute tick:
1. **Adopt + monitor** open CLMM slots (Meteora/Orca/Raydium).
2. **Exit** any slot at take-profit / stop-loss / idle out-of-range.
3. **Fill ONE free slot** with the best-yielding pool it doesn't already hold,
   with deterministic per-slot range logic and width clamps.

**Markets**
- Solana CLMM: **Meteora / Orca / Raydium** (spot LP), swaps via **Jupiter**
- Token universe: SOL, JUP, WIF, PENGU (+ what the pool scanner ranks top)

**Parameters**
- `frequency_sec`: 120 (2-min tick) · `quote_asset`: SOL · `base_pct`: 20
- `slots`: 3 · `take_profit_pct` / `stop_loss_pct`: 20 · `out_of_range_max_sec`: 1800
- `venues`: meteora,orca,raydium · `ranking_window`: 24h
- `risk_limits.min_wallet_sol_reserve`: 0.3
- Guardrails: mint-not-symbol matching, per-slot width clamp (Meteora < 69
  bins, Orca/Raydium ≤ 120), 0.995 hair-cut on entry, one slot fill per tick,
  one distinct token per slot.

**Status**
- Slot inventory + P&L per tick (slots held, exits, fills, free slots)
- Wallet reserve (min SOL kept for rent) + solvency

**Events**
- Slot TP/SL exits and fills (journaled per tick)
- Out-of-range / idle-slot re-entry triggers
- Solvency / reserve guardrails

### Code Files
- `agents/solana_dex_lp_expert/strategies/consigliere/strategy.md` — the
  strategy playbook (LP slot operator)
- `agents/solana_dex_lp_expert/strategies/consigliere/` — routines, skills
  (`pool_ranking`, `lp_range_config`, `slot_exit`), per-session journals
- Repo: GenTech Labs Condor stack (`/root/condor/`)

### Video Link
https://gentechlabs.net/videos/agent-builders-cup-meteora-demo.mp4

---

## What remains for Jordan
1. Fund the Condor gateway wallet (racer can't trade without it)
2. Final submit on botcamp.xyz before **Aug 31**
