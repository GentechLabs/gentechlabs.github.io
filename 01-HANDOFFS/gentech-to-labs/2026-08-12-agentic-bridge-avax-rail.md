# Handoff — Agentic Bridge: Base→Avalanche USDC rail (item #51)

**From:** Gentech (nightly build)
**To:** Labs
**Date:** 2026-08-12
**Queue item:** #51 — Agentic Bridge — Base→Avalanche USDC rail + per-bridge fee layer
**Status:** ✅ SHIPPED by gentech (verified)

## What shipped
- **`10-Labs/AAE-Dry-Powder-Vault/agent/avax_bridge_adapter.py`** — fills the missing
  Base→Avalanche USDC rail for the Agentic Treasury (the gap identified in
  `Treasury/Agentic-Bridge-capability-and-spec-2026-08-06.md`).
  - **Live Across API fee quotes** (`app.across.to/api/suggested-fees`) for
    Base(8453)→Avalanche(43114) USDC→USDC.
  - **Per-bridge GenTech fee layer** — `bridge_fee_bps` (20 bps default) from
    `vault-config.json`, applied on top of the underlying bridge cost (the fee
    model Jordan asked about).
  - **`bridge()` execution path** — approve USDC → `depositV3` on Across SpokePool
    → submit + verify receipt. EVM→bytes32 recipient conversion.
  - **`get_bridge_status()`** — tx receipt status check.
  - **Graceful fallback** to a static estimate if the Across API is unreachable
    (no crash, `source: "estimate"`).
- **`10-Labs/AAE-Dry-Powder-Vault/agent/test_avax_bridge.py`** — 8 tests, all pass.

## Verification
- `python3 test_avax_bridge.py` → **8/8 PASS** (incl. 2 live network tests).
- Live quote verified: $100 → 0.010051% fee, 3s fill, output $99.989949.
- Both `avax_bridge_adapter` and `solana_bridge_adapter` import cleanly (no regression).

## Live quote sample (real, 2026-08-12)
```
Amount:            $100.00 USDC
Output:            $99.989949 USDC
Bridge fee:        $0.010051 (0.0101%)
GenTech fee:       $0.20 (20 bps)
Est. fill time:    3s
Quote source:      live
```

## Next steps (for Labs / Steward)
1. **Fund the Steward Avalanche wallet** (`0x572ABd6461BED2258615E6b99c585Ab7c5d05037`)
   with AVAX gas + native USDC — currently 0 (per Almanak-AVAX-rail-build doc).
2. Fold this adapter into the treasury's rail-agnostic `bridge()` abstraction
   (alongside `solana_bridge_adapter.py`).
3. Demo: treasury moves $X Base→Avalanche, rebalances TraderJoe AVAX/USDC, reports
   full cost (bridge fee + GenTech fee + gas).
4. Consider CCTP as a second rail (free, ~15 min) for large institutional moves.

## Blocker
- **Execution is Jordan-gated**: the adapter is code-complete + verified, but a
  live on-chain bridge needs the Steward wallet funded (AVAX gas + USDC). No funds
  moved this session — quote-only verification.
