# Treasury Posture — DEPLOYED Mode

**Date:** 2026-08-20
**Source:** Jordan greenlight (Gentech Treasury group) + Steward Council verdict — yield-farm AVAX rail, DeFi Milestone goal.

## Status
The GTA treasury is now in **DEPLOYED mode**. Jordan funded ~$29 USDC; the Steward auto-deployed the first AVAX/USDC curve position on LFJ V2.2. The treasury is actively earning fees.

## On-chain position (verified live)
- **Pool:** LFJ V2.2 AVAX/USDC 5bps (`0x864d4e5e...516ea`)
- **Position:** 11 bins · IN range · ~$7.19 Y/X [7.1553–7.2272]
- **Deployed value:** ~$21 (0.97 WAVAX + 8.00 USDC in position) + gas buffer
- **Wallet:** `0x572ABd6461BED2258615E6b99c585Ab7c5d05037`

## What this means
- **Auto-deploy wired** — funded wallet + no position → opens a fresh curve automatically (Jordan, Aug 20). The autonomous rebalance loop keeps it in range / fee-efficient.
- **Auto-rebalance live** — detects OUT-of-range / low fee-eff, withdraws + redeploys on its own, alerts Jordan AFTER.
- **DeFi Milestone is the goal** — treasury deployed toward the milestone, not parked as dry powder.

## Reversal trigger
Jordan explicitly returns the treasury to DRY POWDER (emergency funds) → update this file + stand down the deploy/rebalance legs.
