# Agentic Treasury — Regime-Driven Yield ↔ Trade Engine
**End-to-End Spec** — Jordan greenlit (Aug 5, 2026)
**Build flow:** DeepSeek V4 Flash (DEV) → Kimi K2.7 (AUDIT). Per `develop-and-verify` + `build-queue` skills.

---

## 1. Why this build

Jordan's thesis (verbatim intent):
> "Yield farm now to accumulate daily swap fees. When clear breakout signals fire (up or down), get more risky with trading."

The **brain already exists** — `regime_classifier.py` + `allocation_engine.py` compute exactly this rotation, and the fused `aae-hybrid-signal.py` / `agentic-treasury.py` report it. **What's missing is execution.** Today the engine says "rotate 40% to LP" but nothing moves funds.

**Goal:** Make the four allocation legs (`lp / hodl / staking / lending`) actually executable, in build order that de-risks the treasury. The agent closes the loop from signal → action → verify → remit.

**Current ground truth (Aug 5 07:00 UTC):** regime = `RANGE_BOUND` (conf 0.65) → target LP **40%** / staking 30% / hodl 15% / lending 15%. The engine is already telling us to lean into yield.

---

## 2. Architecture — AAE rules above, venues below

```
             ┌──────────────────────────────────────────────┐
             │  AAE RULE LAYER (venue-agnostic, the brain)  │
             │  regime_classifier → allocation_engine        │
             │  → decide() → plan() → verify() → remit()     │
             └───────────────┬──────────────────────────────┘
                             │ venue-agnostic order plans
        ┌────────────────────┼────────────────────────────┐
        │                    │                            │
   ┌────▼─────┐        ┌─────▼─────┐              ┌───────▼───────┐
   │ LP leg   │        │ Trade leg │              │ Remit leg     │
   │ yield    │        │ basis arb │              │ CDP→EOA→card  │
   │ (swap    │        │ / momentum│              │ (self-orbit)  │
   │ fees)    │        │           │              │               │
   └──────────┘        └───────────┘              └───────────────┘
   COINBASE    SOLANA   AVALANCHE  ETHEREUM       COINBASE CDP
   (base)      (Jupiter) (Almanak)  (PAXG/ONDO)   server account
```

**Principle (locked by Jordan Aug 5):** AAE rules are the product; venues are interchangeable rails. Restriction-bypass = choosing the *right compliant venue*, never a ToS-violating one. Hyperliquid stays detection-only (US gray zone); execution runs on Coinbase spot (LIVE), Robinhood perps (pending), Solana/AVAX rails (built).

---

## 3. Build phases (Easy → Hard, Karpathy-gated)

### Phase A — Executable Yield (LP) Leg  ← START HERE
**Why first:** matches "accumulate swap fees now," is the regime's top allocation (40%), and is the lowest-risk rail (stablecoin LP).

- **A1. `yield_lp_engine.py` (new module)** — venue-agnostic LP executor:
  - Reads allocation target from `.aae-allocation-result.json`
  - `DRY_RUN` default (no funds move) — mirrors `gta_executor.py` pattern
  - `REAL` only with explicit `AAE_LP_REAL=1` + funded wallet
  - Order plan: {leg, venue, token_pair, amount, action: provide/rebalance/withdraw}
- **A2. Wire stablecoin LP venue** (determine which on the box — Base Aave/other stable pool; KeeperHub `kh_` key is execution-eligible per memory)
- **A3. Daily swap-fee accumulator** — cron harvests fees, logs to `agent-flow.jsonl` (Layer-3 attribution), remits
- **A4. Tests** — TDD: dry-run produce/rebalance/withdraw plans, quiet-hours, threshold gating

**Acceptance (Phase A done):** engine produces a verified, executable LP order plan in DRY_RUN; a real (funded) run can provide liquidity and harvest a fee; P&L reflected in treasury report.

### Phase B — Close + Remit Leg (self-orbit loop)
**Why second:** closes the loop for ANY position (LP or trade). Currently the missing piece per skill.
- **B1. Wire CLOSE path** in `gta_executor.py` (currently a deliberate stub) to Coinbase CDP `transfer()` for exit
- **B2. `gta_remit.py` verified** — profit CDP → Jordan EOA (`0x3d11…eCb`) → card. Already exists, verify receipt on-chain each run.
- **B3. Auto-exit** on engine's own signals (spread normalize <3bps / stop-loss +50bps / 7-day hold)

**Acceptance:** an open position can be closed by the engine's own signal AND profit sweeps back to the EOA, verified by tx receipt.

### Phase C — Regime-Triggered Auto-Trade
**Why last:** highest risk. Only flips on clear trending signal.
- **C1. Gate:** auto-ENTER trading leg ONLY when regime ∈ {BULL_TRENDING, BEAR_TRENDING, PRICE_DISCOVERY} AND confidence ≥ threshold
- **C2. Risk auto-tilt:** aggressive allocations only in trending; RANGE_BOUND/HIGH_VOLATILITY force back to yield mode
- **C3. Position sizing** scales with regime confidence (Kelly-lite, capped)

**Acceptance:** engine demonstrably stays in yield mode in RANGE_BOUND, flips to trading mode when regime flips to trending — verified by replay against `.aae-price-history.json`.

---

## 4. Dev/Audit workflow (Jordan's directive)

Per `develop-and-verify`:
- **DEV (write code + tests):** DeepSeek V4 Flash — `deepseek-v4-flash:0731` (ollama-cloud, current)
- **AUDIT (review pass):** Kimi K2.7 — `kimi-k2.7` via ollama-cloud/llama cloud when available
- **Big-boy (only if needed):** Kimi K3 via OpenRouter for architecture/security sign-off
- **Karpathy gates every phase:** no scope creep, no drive-by refactors, testable acceptance criteria, verify persistence before declaring done
- **Audit checklist:** hardcoded secrets, error-detail leakage, input bounds, weak randomness (use `secrets`/`uuid4`), verify-then-mutate ordering, pre-compiled regex

---

## 5. Deliverables & demo

- **Executable modules:** `yield_lp_engine.py`, CLOSE wiring in `gta_executor.py`, verified `gta_remit.py`
- **Tests:** TDD suite, green on DRY_RUN (no funds), audit-passed by K2.7
- **Vault spec (this file):** plan of record
- **Build queue:** add as items with `recommended_tier` (A→flash, B→k2.7, C→k2.7) + `needs_jordan` flags where funding/decision gated
- **Demo (per Jordan's rule):** major product → auto-add to demo site (gentechlabs.net) with live DRY_RUN dashboard showing regime → allocation → order plan → would-trade

---

## 6. Blockers to flag (not hide)

- **Funding:** LP/trade legs need funded wallets (Coinbase CDP Base + native gas). KeeperHub Base wallet `0x53A8…8EA` has 0 ETH / 0 USDC — blocks the live-tx proof.
- **Venue choice for stable LP** on Base to confirm (Aave vs curated Q402 yield market — Q402 `q402_yield_deposit` already exists for BNB/Base supply APY).
- **Regime feed health:** `.aae-hybrid-signal.json` producer was previously missing — confirm `aae-hybrid-signal.py` is running before Phase C depends on it.

---

## 7. Definition of Done

The Agentic Treasury is "real" when, end to end:
1. Reads regime → allocation **live** (not static)
2. **Actually executes** the top allocation leg (yield LP first)
3. Harvests daily swap fees into the treasury
4. **Auto-exits + remits** profit CDP → EOA → Jordan's card (self-orbit closed)
5. **Flips to trading** only when the regime signal is clear (trending)
6. Every step verified by on-chain receipt, not declared success
