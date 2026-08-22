## From Treasury (The Steward) — Solana wallet handoff (Aug 20, 2026)

### 📍 Solana treasury wallet
- **Address:** `BE815V7ojVz63PDxFfSEQyGSe5PZE2fAdKUU6Rd5pUvP`
- **Purpose:** Solana = our second rail (agent-economy spine). Meteora LP, SOL gas, cross-venue arb.
- **Status:** recorded in Treasury notes (Aug 6). NOT yet wired into the gentech-treasury profile — `solana_homebase.py` reports `no_keypair`. Needs `SOLANA_PRIVATE_KEY` (base58) or `SOLANA_KEYPAIR_FILE` (json) set to activate.

### ✅ Position reader fixed (this session)
- `discover_positions.py` LFJ V2.2 reader now returns a real `positionUsd` (deployed value) instead of `null`. It computes deployed = funded_usd (from treasury_config) − loose wallet value.
- Verified: LFJ AVAX/USDC 11 bins IN range $7.29, deployed ≈ $10.77 (loose 0.96 WAVAX + 9.08 USDC).
- Also fixed earlier: rebalance redeploy bug, deploy stale-price + Gaussian-distribution bugs. Position is live + earning.

### ⏳ Needs Jordan / blocked
- Wire Solana keypair into gentech-treasury profile (env or keyfile) to activate the Solana rail.
- MultiHopper (wallet connect), Krexa (invite), Ramp (alpha) queued for Solana rail — Jordan wallet connects after vacation.
