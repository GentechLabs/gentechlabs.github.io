# Revenue Monitor — Treasury Wallet Scan Fix

**Date:** 2026-08-20

## The bug (revenue-blocker)
The Revenue Monitor (`revenue-monitor.py`) only scanned `0x7ebff188...`
(the signer/ops EVM wallet) for incoming USDC transfers. But **buyer x402
settlements land in the treasury wallet `0xF9dc...e734`** — the `payTo`
address carried in our 402 payment challenge.

Consequence: when the first real organic buyer paid us, the monitor would
have **silently missed it** — we'd never see our first external revenue.

## The fix (3 edits to `revenue-monitor.py`)
1. **Config:** added `WALLET_EVM_TREASURY = "0xF9dcBFF7EdDd76c58412fd46f4160c96312ce734"` (distinct from signer wallet).
2. **Scan loop:** now scans **both** `WALLET_EVM` and `WALLET_EVM_TREASURY` on Base/Avalanche/BNB.
3. **Self-transfer filter:** treats signer↔treasury moves as internal (added treasury to `our_wallets`), so internal moves aren't falsely counted as external revenue.

## Verified live
- Treasury wallet scan on Base now returns **5 USDC transfers** it previously missed entirely (senders incl. `0xca11d50b` = Universal Router, the settlement contract path).
- Full monitor run clean: `base: $26.0050 (6 txs)`, `agent_research: $0.0500 (1 tx)`, no errors.
- SOL still scanned; EVM native balances (Base/AVAX/BNB) intact.

## Why this mattered
This closes the demand-revenue loop. With the OKX relist, facilitator
failover, and AgentCash OpenAPI compliance done, the pipeline is now fully
instrumented:
- **Discovery** — AgentCash/x402scan read us (ownership_verified, 10 paid endpoints)
- **Receipt** — treasury confirmed holding USDC (3.94 at fix time)
- **Detection** — Revenue Monitor now scans the treasury wallet, so the first
  real organic buyer settlement will be reported (twice daily: 8:05/20:05)

## File
`/root/.hermes/profiles/gentech/scripts/revenue-monitor.py`
