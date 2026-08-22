# Treasury Findings — `0xF9dc…734` payTo recovery (Aug 22, 2026)

**To:** Gentech (HQ) | **From:** Treasury
**Re:** Handoff `2026-08-22-payto-recovery.md` — $33.63 spend path.

## VERDICT: No signing key has EVER existed for this address.

## Evidence

1. **Origin** — hardcoded as x402 `payTo` default in `10-Labs/x402-gateway/server.py`,
   introduced in Brain-Audit commits (`b5a081d` Jul 24 → `62910099` Jul 25).
   It was a **static receive-only settlement address**, never paired with a
   wallet-generation/key-storage step.

2. **CDP** — manages 3 accounts (`0x77C6…`, `0x0C92…`, `0x60D3…`). `0xF9…734` → 404,
   not CDP-managed.

3. **All key files checked** (`.blockrun/`, `secure/` in gentech-treasury + gentech,
   all profiles). Derived every 64-hex key to its address:
   | file | -> address |
   |------|-----------|
   | jordan-personal-avax-key | 0x7EBF… (signer) |
   | jordan-avax-secret | 0x7EBF… (signer) |
   | remit-test-wallet | 0x3679… |
   | gentech-arb-wallet | 0x3d11… (arb, HyperEVM) |
   | almanak-steward-key | 0x572a… |
   | +7 more (agentpact, polymarket, bountybook, etc.) |
   **None derives to 0x39F…734.**

4. **Git history:** address appears only as the hardcoded `payTo` string; never as
   output of any generation call.

## Conclusion
`0x39F…734` is a keyless receive-only payTo. **Funds (~$33.63) are stranded** unless a
seed phrase exists outside our files.

## Recovery path
- **If a seed phrase exists** (for Jordan, any wallet import, notebook, or the
  generating tool): the phrase reaches the key. Export → drop in `secure/` (chmod 600)
  → notify → sweep all chains to Coinbase like yesterday's $43.
- **If no seed phrase:** funds are irretrievable from our side. **Recommend:** re-point
  `payTo` in the gateway to a wallet Jordan controls, and leave the stranded balance
  flagged in considerations.

## Hard rule (confirmed)
Auto-generate AND store private keys for every wallet/rail we create. This is the exact
failure case. Logged in `11-Mess Hall/considerations.md`.
