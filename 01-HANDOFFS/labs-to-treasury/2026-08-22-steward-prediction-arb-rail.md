# From Labs → Treasury — 2026-08-22

## 🎯 The Steward — Prediction-Arb Rail (Phase 1 built, DRY-RUN)

Jordan GREEN LIGHT (Aug 22). New capability for **The Steward** (Agentic Treasury):
a **prediction-market rail** that detects cross-venue arb edges on the SAME event
priced by **Polymarket** (Gamma/CLOB) and **Kalshi** (trade-api). Thesis: *"The One
Paperclip for agents"* — start from nothing, capture the spread every cycle, compound.

### What's built (Phase 1 — edge DETECTOR, no live orders)
- **`Treasury/scripts/steward_prediction.py`** — reads Polymarket + Kalshi, scans
  fed-rate/bitcoin markets, flags:
  - **intra-venue:** Polymarket YES+NO summing to != 1.0
  - **cross-venue:** Polymarket vs Kalshi disagreeing on a shared keyword
- Writes state → **`Treasury/.steward-prediction.json`** (`status: dry_run`)
- **Verified live:** both sources HTTP 200, 22 markets scanned, state written.
- Keyless reads — no capital, no keys, no orders.

### How to wire it (per our fused-cron pattern — NOT a separate spammy cron)
Treat it as a **data producer** feeding the fused Steward report:
1. Add a **"🎯 Prediction" block** to the fused report (next to LP/regime blocks)
   that reads `.steward-prediction.json`.
2. Optional no_agent cron: `python3 steward_prediction.py --show` → silent when no
   edges (watchdog pattern), emit only when an edge fires.

### Phase 2 — Agentic arb + flash-loan executor (DEFERRED, Jordan)
- **Agentic** flash loans (NOT hand-written Uniswap contracts): agent opens a
  credit line underwritten by `agent-credit-score`, borrow→arb→repay atomic,
  Revenue Router auto-services debt (from Agent Arena scored-leverage spec).
- Execute the detected edge cross-venue (Polymarket ↔ Kalshi) + intra-venue.
- **Gate:** requires funded Polymarket wallet + EVM key (never main) + Kalshi
  trading auth. Build decision/executor into Steward's existing decision layer.

### Files
- Spec: `09-Green Room/specs/steward-prediction-arb-flash-loan.md`
- Rail: `Treasury/scripts/steward_prediction.py` + `Treasury/.steward-prediction.json`
- Reference (cloned): `/root/telegraph-usecases/telegraph-supersignal/` (Polymarket bot pattern)
- Rail assessment: `10-Labs/telegraph-miners/PREDICTION-MARKET-RAIL-ASSESSMENT.md`

### Ask from Treasury
- Wire the 🎯 Prediction block into the fused Steward report (or confirm you'd
  rather I add the no_agent producer cron under the Treasury profile).
- Flag when the Steward has capital ready → Phase 2 executor can be armed.
