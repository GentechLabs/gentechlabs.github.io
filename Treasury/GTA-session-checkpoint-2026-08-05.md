# GTA — Session Progress Checkpoint (Aug 5, 2026)

## What's DONE (this session + prior)
1. **Execution rail LIVE** — first real trade: $5 USDC → cbBTC on Base, verified on-chain.
   - Root cause of the old blocker: `CDP_WALLET_SECRET` was the wrong format (Ed25519 vs
     required DER EC P-256). Jordan provided the correct one; wired into both profiles.
   - Permit2 approval is a REQUIRED one-time step for USDC swaps (else `TRANSFER_FROM_FAILED`).
   - ALWAYS verify tx receipt (status==1); the SDK's `executed: true` is NOT proof.
2. **Buy list expanded** — LINK verified + added to `gta_coinbase_leg.py SUPPORTED` map.
3. **Remit path built** — `gta_remit.py` CDP server account → Jordan EOA → card. Dry-run verified.
4. **Agentic Treasury tracks real positions + P&L** — added `💼 GTA Pos` layer reading live
   on-chain balances + `.gta-positions.json` entry state → shows P&L.
5. **Cron fleet consolidated** — removed GTA Watcher, GTA Signal, GTA Fund Monitor, dup
   CLARITY tracker. Kept data producers (Arb Monitor, Executor, Narrative, CMC, FOMC, CLARITY, LP).
6. **Regime producer rebuilt** — `.aae-hybrid-signal.json` feed restored; treasury shows RANGE_BOUND (65%).

## Live account state (Base, CDP server account 0x77C6…)
- USDC: $5.50 | cbBTC: 0.0000772 | native ETH: ~0.0003 (gas)

## OPEN / NEXT
### Immediate (buildable now)
- **Pause/remove the remaining legacy crons that duplicate the treasury** — CMC watchlist &
  the dry-run GTA Executor are the main candidates to reconcile against the fused report.
  (Exec keeps the Layer-3 agent-flow.jsonl attribution ledger — consider keeping it for data.)
- **PAXG / ONDO rails** — CDP spot on the **ethereum** network (not Base). Verify addresses
  live against `get_swap_price`, add to SUPPORTED, test.
- **AVAX rail** — native Avalanche (CDP server account is Base-only; needs an Avalanche path).
- **SOL / TAO rail** — Jupiter swap on Solana; USDC Base→Solana bridge adapter exists in the brain.

### Blockers / decisions for Jordan
- **GitHub PAT dead** — vault git push fails (no SSH keys). Brain is local-only until a fresh
  credential is provided. Also blocks filing the cdp-sdk bug issue.
- **Payments MCP** — downloaded but NOT activated (needs email/OTP + Onramp funding; it's a
  spend rail, not the trade rail). Stand up behind Xvfb when ready.
- **Remit in production** — script built & dry-run verified; NOT run with real funds (nothing
  to remit yet, $0 profit).

## Key files
- `gta_coinbase_leg.py` — Coinbase spot executor (BTC + LINK in SUPPORTED)
- `gta_remit.py` — profit remit CDP → EOA
- `.gta-positions.json` — executed position entry state
- `agentic-treasury.py` — fused report (Regime + GTA Pos + Arb + Narrative + rainbows)
- `.gta-arb-state.json` — arb window feed (from GTA Arb Monitor cron)
- `aae-hybrid-signal.py` + components — regime producer (cron bc999a35e0cd)
- Brain: `Treasury/GTA-execution-rail-live-2026-08-04.md`
