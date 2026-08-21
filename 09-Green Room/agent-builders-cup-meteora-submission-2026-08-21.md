# Agent Builders Cup — Meteora Submission Draft (2026-08-21)

**Team chosen:** Meteora (Solana-native seat)
**Strategy:** Consigliere — LP Slot Operator + Cross-Venue Arbitrage
**Code:** `/root/condor/agents/solana_dex_lp_expert/strategies/consigliere/strategy.md`
**Status:** Draft ready → needs wallet fund + final submit before Aug 31

---

## Form Field Drafts (matches the Botcamp "New Strategy" form)

### Strategy Title
**Consigliere — Solana CLMM LP + Cross-Venue Arbitrage Agent**

### Summary
A live execution agent that runs the **fee-yield LP core** on Solana CLMM pools
(Meteora / Orca / Raydium) and layers a **cross-venue arbitrage detector**
against Hyperliquid perps on top. One Condor agent, two coordinated levers,
per-slot TP/SL, capital rotation. Built on GenTech's treasury rail (x402),
moving capital trustlessly, per-transaction.

### Detailed Description

**Description**
Consigliere reads the market, applies judgment, and acts on the builder's
behalf. It runs two coordinated layers in a single ~2-minute tick loop:
1. **LP layer (fee-yield core)** — monitors open CLMM slots, exits on TP/SL,
   fills one free slot with the best-yielding pool it doesn't already hold.
2. **Arb layer (edge lever)** — each tick scans cross-venue spreads
   (Meteora/Orca/Raydium spot vs Hyperliquid perp) for the token universe it
   already holds; only acts when a route clears the mandatory fee fence.

**Markets**
- Solana CLMM: **Meteora / Orca / Raydium** (spot LP)
- Hyperliquid perpetuals (arb vs spot)
- Token universe: SOL, JUP, WIF, PENGU (+ what the pool scanner ranks top)

**Parameters**
- `frequency_sec`: 120 (2-min tick)
- `quote_asset`: SOL · `base_pct`: 20 · `slots`: 3
- `take_profit_pct` / `stop_loss_pct`: 20 · `out_of_range_max_sec`: 1800
- `venues`: meteora,orca,raydium · `ranking_window`: 24h
- `arb_min_spread_pct`: 0.8 (fee fence) · `arb_include_hyperliquid`: true
- `capital_per_slot`: auto · `risk_limits.min_wallet_sol_reserve`: 0.3
- Guardrails: mint-not-symbol matching (no phantom spreads), per-slot width
  clamp (Meteora < 69 bins, Orca/Raydium ≤ 120), 0.995 hair-sub on entry,
  one slot fill per tick, never arb a token not held.

**Status**
Build + verified in GenTech's Condor stack (`agents/solana_dex_lp_expert/`).
Live-tested against Meteora/Orca/Raydium price conventions and Hyperliquid
perp mid. Ready to race with a funded wallet.

**Events**
- LP slot TP/SL exits and fills (journaled per tick)
- Arb route rotations (fee-fence-gated, max 1/tick)
- Solvency / reserve guardrails (min SOL kept for rent)

### Code Files
- `agents/solana_dex_lp_expert/strategies/consigliere/strategy.md` — the
  strategy playbook (LP slot operator + cross-venue arb)
- `agents/solana_dex_lp_expert/strategies/consigliere/` — routines, skills
  (`pool_ranking`, `lp_range_config`, `slot_exit`), per-session journals
- Repo: GenTech Labs Condor stack (`/root/condor/`)

### Video Link
_(narration demo — generated, hosted at URL below)_
https://gentechlabs.net/agent-builders-cup-meteora-demo.mp4

---

## What remains for Jordan
1. Fund the Condor gateway wallet (racer can't trade without it)
2. Final submit on botcamp.xyz before **Aug 31**
