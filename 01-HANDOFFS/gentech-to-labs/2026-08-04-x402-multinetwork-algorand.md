# Gentech → Labs — 2026-08-04 — x402 Gateway Multi-Network (Algorand)

**Queue item:** #7 — Algorand Global x402 Challenge ($100K + 500K ALGO)
**Status:** SHIPPED (code side). Registration + wallet still Jordan-gated.

## What was done
Queue item claimed ALGO support was "config-only for our multi-chain gateway."
That was not true — `build_payment_required()` was hardcoded to a single Base
`accepts` entry. It is true now.

Changes in `/root/vaults/gentech/10-Labs/x402-gateway/server.py`:

- **`NETWORKS`** — CAIP-2 registry of settlement rails.
  - `base` → `eip155:8453`, USDC contract `0x8335...2913`, 6 decimals
  - `algorand` → `algorand:wGHE2Pwdvd7S12BL5FaOP20EGYesN73k`, USDC **ASA 31566704**, 6 decimals
- **`enabled_networks()`** — resolves the `X402_NETWORKS` env var into concrete rails.
  - Unknown network names are ignored, not fatal
  - A rail is dropped if it has no configured `payTo` — we never advertise a
    network we cannot actually receive on
  - Always falls back to Base, so the gateway can never advertise zero rails
- **`is_network_accepted()`** — wired into **both** `verify_proof_via_cdp()` and
  `verify_proof_simulation()`. A proof settled on a rail we don't accept is
  rejected *before* any remote facilitator call. Proofs omitting `network`
  are still accepted (backward compat with pre-multi-network clients).
- `accepts` array is now generated per-rail with correct atomic amounts derived
  from each network's own decimals.

## Verification (all real, not declared)
- `pytest test_networks.py` → **17/17 pass** (new file, 4.9KB)
- `systemctl restart x402-api` → active
- `https://api.gentechlabs.net/v1/security/score/0x0...` → **HTTP 402**,
  `accepts` networks `['eip155:8453']` — byte-identical to the pre-change
  payload, so zero regression for existing paying clients
- `/status` → all **8 backends ok**
- Two-rail activation proved on a scratch instance (port 8399) with
  `X402_NETWORKS="base,algorand"` + a placeholder payTo → emitted 2 accepts
  entries with correct ASA id and atomic amounts

## What could be continued
1. **Algorand facilitator settlement** — `verify_proof_via_cdp` only talks to the
   Coinbase CDP facilitator, which is EVM-only. An ALGO proof that passes the
   network check will still fail settlement verification. Needs an Algorand
   verification path (algod indexer txn lookup, or an ALGO x402 facilitator if
   the challenge provides one). **This is the next real build task.**
2. Register the services on the Algorand challenge leaderboard once Jordan has
   the wallet.
3. Consider adding Solana as a third rail — the registry makes it a ~10 line
   addition now.

## To activate ALGO (2 env vars, no code change)
```
X402_NETWORKS="base,algorand"
X402_PAYTO_ALGORAND="<Jordan's Algorand mainnet address>"
```
Then `systemctl restart x402-api`.

**Ping:** Jordan for the Algorand wallet address + challenge registration.
