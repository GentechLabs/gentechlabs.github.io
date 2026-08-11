# Agent Kit — Auto-Provisioning "Self-Tracking Treasury" (Product Idea, Aug 11 2026)

**Jordan's idea:** when a user sets up their Agentic Treasury / Agent Kit, the
cron jobs should AUTOMATICALLY pick up whatever LP/position/rail they deploy —
no manual wiring, no "start from the beginning." The kit should make it trivial
to connect deployed positions to the reporting crons. "We're cooking."

## Why this is buildable (we already did the hard part)
The `agentic-treasury.py` fused report was JUST upgraded (Aug 11) to read the
LIVE on-chain V2.2 LP position on the Steward wallet directly — via RPC reads
(`getActiveId`, `balanceOf(addr,binId)` over a ±20 bin window), not a stale feed.
That pattern (read live on-chain → render a report line) is the reusable core.
It's chain-agnostic and wallet-driven: change the WALLET + PAIR constants and it
tracks any position.

## The product: Auto-provisioning self-tracking treasury
Users set up their Agentic Treasury with a wallet + config. The kit's cron
layer then AUTO-DISCOVERS deployed positions and reports them — no manual
wiring of "which pool," "which wallet," "which range."

### Design — config-driven auto-discovery
```
Agent Kit install
  ├─ treasury_config.json      ← user sets: wallet(s), chains, [optional] pools
  ├─ agentic-treasury.py       ← reads config, auto-discovers + reports
  ├─ provision.sh              ← one-command cron setup (registers crons)
  └─ skills/treasury/*         ← self-onboarding skills the agent loads
```

### How auto-discovery works (reuse the Aug 11 pattern)
1. Read the wallet + chain from config.
2. For each configured chain, probe for LP positions:
   - **LFJ V2.2** (Avalanche): `getActiveId` + `balanceOf(addr, binId)` window
     → bins, range, IN/OUT, live price.
   - **Meteora DLMM** (Solana): same shape system → bin balance query via RPC.
   - **Base/Ethereum**: ERC-20 balances (cbBTC, USDC, LINK, PAXG...).
3. Emit a report line per discovered position (the `layer_lp()` we just built).
4. The cron (same `agentic-treasury.sh` wrapper) picks it up automatically.

### Why this is a moat, not just convenience
- **Zero-friction onboarding** — "deploy a position, the kit tracks it."
  No config plumbing, no "where do I tell it about my pool."
- **Proves the trust loop** at small scale — the same thing we just validated
  with Jordan's $45: the kit watches its own deployed capital, reports honestly,
  and rebalances only when gas-justified.
- **Chain-agnostic = more connector/supplier surface** — LFJ, Meteora, Base,
  Ethereum, Monad (same LB pattern extends) all auto-tracked from one config.

### Deliverables (if greenlit)
1. `provision.sh` — one-command cron provisioning (registers the report crons
   against the user's config).
2. `treasury_config.json` template + docs.
3. Generalize `agentic-treasury.py`'s `layer_lp_live()` into a reusable
   `discover_positions(chain, wallet)` in the kit.
4. Skills: `skills/treasury/self-tracking/SKILL.md` (self-onboarding).

## Status
🟢 **BUILT — Aug 11, 2026.** Deliverables live in `10-Labs/agent-kit-self-tracking/`:
- `discover_positions.py` — generalized `discover_positions(chain, wallet)` (reuses
  the `layer_lp_live()` live-RPC pattern; auto-widens the bin scan to tolerate price
  drift — verified live against the deployed AVAX/USDC curve).
- `treasury_config.json` — wallet + chains + optional pools template.
- `provision.sh` — one-command cron provisioning (validated, dry-run + live).
- `steward_rebalance.py` — **the Steward's autonomous decision loop.** Reads live
  regime + position, picks shape by regime (RANGE_BOUND→CURVE, HIGH_VOLATILITY→
  BID_ASK), and decides rebalance/hold. OUT-of-range + regime-appropriate = rebalance;
  IN-range = hold. 10-min frequency guard. REAL execution guarded (--yes + gas + wallet).
- `test_steward_rebalance.py` — 10 passing decision tests (shape switch, hold, guard).
- `steward_progress.py` — **deposit detection + milestone progress.** Detects NEW
  deposits to the wallet (delta vs persisted baseline, guarded against price drift
  by a %+$ floor), maps daily fees to the canonical AAE DeFi Milestone ladder
  (Scout $5 → Raider $20 → Warlord $55 → Sovereign $200), reports % to next rank +
  estimated fees. `test_steward_progress.py` — 12 passing tests.
- `skills/agent-kit-self-tracking-treasury/SKILL.md` — self-onboarding skill.
- Cron `51bc9900e24d` — **Steward Position Watchdog every 10m** (AAE pattern:
  cheap `no_agent` script job, silent when healthy, emits actionable OUT-of-range
  signal via `steward-watchdog.sh`). Replaces the old paused LP Monitor v2 cadence.
- Cron `bc885594238f` — **Steward Deposit Watchdog every 15m** (no_agent, silent
  until Jordan sends new money, then reports rank/progress/fees via
  `steward-deposit-watchdog.sh`).

Live test (Aug 11): Steward correctly decided **REBALANCE** on the live position —
regime RANGE_BOUND (CURVE shape), position OUT (fee eff 0%, $6.20 vs band
$6.42–$6.48). Gas measured ~$0.001/cycle (0.1 gwei), so re-centering is effectively
free. Scope to extend: Meteora DLMM (Solana), Monad/Trader Joe.
