# CLARITY Mode Layer — GTA Visibility Overlay (Aug 6, 2026)

**What this is:** a human-readable "mode" layer on top of the AAE regime/allocation
engine, so Jordan sees at a glance whether GTA is in RISK-ON, YIELD, ACCUMULATION,
DEFENSIVE, or VOLATILITY posture — plus the CLARITY Act macro overlay.

## Why this exists (Jordan's read, Aug 6)
Instead of only *tracking* the CLARITY vote, we **position around it** with GTA + the
regime/allocation engine deciding. Jordan wants visibility into *which mode we're in
and when it changes* — "we're in yield mode, when do we get to this mode or that mode?"

## The mode map (regime → posture)
| Regime | Mode | Posture |
|--------|------|---------|
| BULL_TRENDING / PRICE_DISCOVERY | 🟢 RISK-ON / GROWTH | hodl-heavy — long spot via CDP |
| RANGE_BOUND | 🟡 YIELD / LP HARVEST | LP + staking — harvest yield |
| ACCUMULATION | 🟣 ACCUMULATION | building position, hodl 40% |
| BEAR_TRENDING | 🔴 DEFENSIVE / YIELD | staking + lending — shelter |
| HIGH_VOLATILITY | 🟠 VOLATILITY / HEDGED | spread across strategies |

## The CLARITY position logic (Jordan's trade read)
- **BTC at ~$64.8k.** Upside on a PASS is only 65–70k (+3–7%) but downside on a FAIL is
  a volatility flush with no floor. **Asymmetry favors yield-farming the sidelines, not
  a directional long.**
- **If it FAILS** (now likelier after cloture miss) → we're already in stable yield, dodge
  the flush, deploy into the post-flush bottom.
- **If it PASSES** → BTC pops 65–70k; stable yield was safe carry, rotate into the pump
  once confirmed (trigger: RISK_ON mode + vote=PASSED).
- Hard deadline **Aug 7** recess. MISSED → dead until mid-Sept.

## Live yield venues (verified Aug 6)
| Venue | Asset | Chain | APY |
|-------|-------|-------|-----|
| **Morpho USDC vault** | USDC | Base | **4.76%** ⭐ home chain |
| Aave V3 USDC | USDC | BNB | 3.27% |
| Lista Lending USDC | USDC | BNB | 2.37% |
| Aave V3 USDT | USDT | BNB | 2.23% |

⚠️ **Morpho deploy is BLOCKED** — Q402's Base-yield path needs the **Multichain** API key;
only the trial key (BNB/Avalanche) is configured. Not yet deployed. The trigger layer is
built regardless.

## What was built (all verified working)
1. **`clarity-mode.py`** — reads `.aae-hybrid-signal.json` (live AAE engine) → emits
   one-line mode + posture. Modes: RISK_ON / YIELD / ACCUM / DEFENSIVE / VOLATILE / UNKNOWN.
   Persists to `.clarity-mode-state.json`. `--watch` fires only on MODE CHANGE.
2. **`agentic-treasury.py`** — added CLARITY MODE line at the top of the fused report
   (ships at 8/14/20 UTC to Treasury group).
3. **Cron `2771fcc84d46` "CLARITY Mode-Change Alert"** — every 3h, delivers to Treasury
   group ONLY on a mode/regime change. Silent otherwise.
4. **`.clarity-vote-state.json`** — seeded PENDING. The CLARITY tracker cron
   (`8d40bf2cbe43`) now writes PASSED/FAILED/MISSED/PENDING to it each run, feeding the
   macro overlay in the mode report.
5. Synced all scripts to BOTH profiles (treasury + gentech).

## Live test proof
- Mode report renders: `🟡 CLARITY MODE — YIELD / LP HARVEST · Regime RANGE_BOUND (65%)`
- Mode-change detection verified: simulated regime→BULL_TRENDING fired
  `🔄 MODE CHANGE: YIELD → RISK_ON`, then reverted cleanly to YIELD on restore.
- Fused report builds clean with mode line on top.

## Current state
GTA is in **🟡 YIELD / LP HARVEST** (RANGE_BOUND, 65% conf). Engine action HOLD, current
winner LENDING. BTC in Accumulation value zone. Arb window on AVAX (10.7bps).
