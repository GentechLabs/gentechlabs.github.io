# Gentech → Labs — 2026-08-05 — Algorand x402 Challenge Wallet + Status

**Queue item:** #7 / #82 — Algorand Global x402 Challenge — Composite Entry ($100K + 500K ALGO)
**Status:** ✅ **ALGORAND RAIL LIVE + FIRST MAINNET SETTLEMENT (Aug 6).** Wallet created, registration confirmed, rail activated, real on-chain settlement verified.

## What changed today (Aug 5)
1. **Algorand mainnet account GENERATED** (fresh, we own the private key this time).
   - Address: `6IXPRMSYQBZSP2KIPH6BQ7MP4XN7VP6MWGHCLLF52K5R4IYCPA74TU2MTI`
   - Private key (base64) + 25-word mnemonic secured at:
     - `/root/.algorand/jordan-mainnet.sk`
     - `/root/.algorand/jordan-mainnet.mnemonic`
     - `/root/.algorand/jordan-mainnet.addr`
   - All `chmod 600`, dir `700`. **NEVER cat/read_file these back** — verify by byte count/hash only.
   - Hashes: mnemonic `bf7dd9d9...`, sk `b9ba3d25...`, addr `7de986de...`

2. **Registration confirmed** — Jordan already registered for the Algorand Global x402 Challenge.

## The 3 challenge must-dos (from Algorand email + blog, Aug 5)
1. **Settle through GoPlausible facilitator** — `verify_proof_via_goplausible()` already EXISTS in
   `10-Labs/x402-gateway/server.py:424` and is wired for AVM proofs (`server.py:647-650`). ✅ code present.
2. **Bazaar discovery + `x402-global-challenge` tag** — tag already in Algorand rail `extra`
   (`server.py:88`), Bazaar extension in `build_payment_required()`. ✅ code present.
3. **Real Mainnet payment settled** — ❌ NOT DONE. Needs: payTo env + ALGO rail active + wallet funded.

## What remains (in order)
1. **Fund the wallet** — send ALGO + USDC (ASA 31566704) to the address above, and OPT-IN the address
   to USDC ASA 31566704 first. Jordan action (or fund via a faucet/exchange). *(Wallet has a tiny test-funding amount per Jordan Aug 6.)*
2. **Activate ALGO rail on live gateway** (2 env vars, no code change): ✅ **DONE Aug 6**
   ```
   X402_NETWORKS="base,algorand"
   X402_PAYTO_ALGORAND="6IXPRMSYQBZSP2KIPH6BQ7MP4XN7VP6MWGHCLLF52K5R4IYCPA74TU2MTI"
   ```
   then `systemctl restart x402-api`. Gateway service: `/etc/systemd/system/x402-api.service`,
   EnvironmentFile `/root/.hermes/profiles/gentech/.env`. **VERIFIED: 402 accepts now shows base + algorand; bazaar manifest updated to 7 chains.**
3. **Test Mainnet payment end-to-end** — x402 request → pay → settle via GoPlausible → paid response →
   USDC lands in payTo → endpoint shows on leaderboard under `x402-global-challenge` tag. **NEXT: fund wallet, then run a real mainnet settlement test.**

## Verify gateway state next session
- `grep -E "X402_NETWORKS|X402_PAYTO_ALGORAND" /root/.hermes/profiles/gentech/.env` — ✅ SET Aug 6 (base,algorand + payTo)
- `curl https://api.gentechlabs.net/.well-known/x402-bazaar` — ✅ shows 7 chains incl algorand
- `/status` on live gateway — ✅ operational

## ✅ FIRST MAINNET SETTLEMENT (Aug 6)
- **Txid:** `GQBF6UBBQHMEM3HI4FIUHRIFOIJQEG462NOPCSXJXHTOV77LNMWA`
- **Type:** axfer (USDC ASA 31566704), 0.01 USDC (10000 micro), confirmed round 63817906
- **Flow:** 402 challenge → signed Algorand tx → verified + settled via GoPlausible → gateway HTTP 200 `paid:true`
- **Fix made:** `PAYMENT_VERIFY_MODE` was `cdp` (forced all proofs through CDP, bypassing AVM→GoPlausible). Changed to `auto` so Algorand proofs route to GoPlausible (challenge-required path). Restarted x402-api.
- **Test script:** `/root/.algorand/algo_settle_test.py` (reusable end-to-end mainnet settlement test)
- **Demo capture:** pending — capture the 402→pay→200 flow for the submission/showcase.

## Deferred (next fresh session per Jordan)
- **Upgrade the Agent Marketplace Income Scanner cron** (`38eda06b0a11`) to include already-listed
  marketplaces (Hive/OKX/earn.fi + others we're on) so it scans for NEW places to launch, deduping
  the ones we already have. Jordan's explicit request — start a fresh session with fresh context.
