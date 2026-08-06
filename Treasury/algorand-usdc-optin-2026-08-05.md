# Algorand Wallet — USDC Opt-in Complete

**Date:** 2026-08-05
**Wallet:** `6IXPRMSYQBZSP2KIPH6BQ7MP4XN7VP6MWGHCLLF52K5R4IYCPA74TU2MTI`
**Action:** Opted into USDC ASA 31566704 (0-unit asset transfer to self)
**Txn:** `D4ZESUWYNZ6HYN77FQDVDQ2RVN7MRNRCC3FVH4ATJVZIKZJUAYUA`
**Round:** 63794335
**Status:** ✅ CONFIRMED — wallet now holds USDC asset (0 balance, ready to receive)

## Why this was needed
Coinbase refused to send USDC to the Algorand address because it hadn't opted in to the USDC ASA. Algorand requires opt-in before receiving an ASA (unlike EVM). The opt-in was paid from the wallet's own 55 ALGO.

## Next
- Jordan sends $5 USDC to the address → lands clean now
- Then fire the Algorand x402 Challenge mainnet payment

## Script
`/root/.algorand/optin_usdc.py` (uses jordan-mainnet.mnemonic)
