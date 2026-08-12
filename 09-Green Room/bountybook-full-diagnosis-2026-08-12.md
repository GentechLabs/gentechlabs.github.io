# BountyBook — Full Diagnosis (2026-08-12)

## Status: Platform has NEVER paid out. Both earning rails broken.

### Evidence gathered
1. **Claim flow works** — agent wallet `0x80dD…1e47`, re-auth via viem works, claimed job `0a1c6ae8` (merge_csv, $3.50). No on-chain tx needed.
2. **Submit flow works** — submitted twice with the EXACT documented inline payload (`outputData`), API accepts, attempt logged.
3. **Verifier always crashes on code jobs** — every attempt (mine + 1,276 others) fails:
   `Verification error: Cannot read properties of undefined (reading 'length')`, `checksFailed: ["ipfs_fetch"]`.
   **Lifetime code_test settlements: 0 of 32.**
4. **Even non-code jobs never pay** — verified jobs show `payout_status=failed`, no `payout_tx_hash`. Treasury `0x1bc6c2268260c391C7871cF9f2Dfa43207F72f2b` shows **zero lifetime USDC outflows on Base**. No USDC has EVER moved on the platform.

### Root cause (confirmed by other agents, independently)
The oracle reads `spec.success_condition.required_fields.length`, but code_test specs carry `required_files`. `undefined.length` → crash. This is a **server-side spec-parse bug**, independent of inline-vs-CID delivery. IPFS pinning will NOT fix it — the crash happens before output is even read.

### Contact channels (no public GitHub)
- **Discord:** `https://discord.gg/BXKTe44Y` (built by @_ptonik)
- **X/Twitter:** `@_ptonik`
- Operator already has a $150 fix offer open (job 8a7bd232) — they know.

### Recommendation
Do NOT invest further in BountyBook earning until the operator ships the payout fix (currently claimed by another agent) AND confirms a verified job actually moves USDC on-chain. This is a "$638 available but zero paid" trap. Re-check in ~1 week: if verified jobs start showing payout_tx_hash, BountyBook becomes our best autonomous rail. Until then, park it.

### Draft report (for Jordan to post to Discord/X)
---
**BountyBook agent bug report** — GenTech Labs, agent `0x80dD10df5179ffa08590f49Ae9960fedf9991e47`

Reproduced the code_test verifier crash on job `0a1c6ae8`: inline `outputData` submission (exact documented shape, tested twice) returns `Verification error: Cannot read properties of undefined (reading 'length')`, `checksFailed: ["ipfs_fetch"]`. Root cause appears to be the oracle reading `spec.success_condition.required_fields.length` while code_test specs carry `required_files` (matching the existing bug report job `3c452142`).

Separately, confirmed the payout rail never fires: verified jobs show `payout_status=failed` with no `payout_tx_hash`, and treasury `0x1bc6c2268260c391C7871cF9f2Dfa43207F72f2b` shows zero lifetime USDC outflows on Base (chain 8453). Happy to share full evidence. This is operation-ending — happy to help test a fix if useful.
---
