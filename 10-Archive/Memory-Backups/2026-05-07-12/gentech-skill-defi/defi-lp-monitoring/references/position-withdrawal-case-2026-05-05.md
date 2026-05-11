# Position Withdrawal Detection — Case Study (2026-05-05)

## Summary
On-chain scan of LFJ AVAX/USDC pool returned zero positions for the tracked wallet, despite vault entries from earlier the same day showing ~$139 in active LP. Wallet balance confirmed at 0.097 AVAX ($0.91) — dust only.

## Timeline
- **08:15 UTC**: Vault entry written showing 11.64 AVAX + 29.15 USDC = $139.50 (estimated from cached data)
- **12:15 UTC**: Second vault entry showing same balances = $136.47 (range discrepancy noted)
- **11:12-12:49 UTC**: On-chain transactions show 15+ AVAX sent from wallet to 0x18556da... (contract)
- **16:15 UTC**: LP monitor cron detected empty position via on-chain scan

## Key Findings

### 1. Scan Range Must Be Wide Enough
- Initial ±50 bin scan returned nothing
- Expanded to ±200 bins — still nothing
- Conclusion: position was fully withdrawn, not just drifted out of range

**Lesson**: Always scan ±100 minimum. If ±100 returns nothing, expand to ±200 to be certain.

### 2. Vault Entries Were Stale
- Earlier cron runs wrote entries based on estimated/cached data, not live on-chain verification
- The `fetch-lfj-position.py` script was not run (path mismatch — script wasn't at expected location)
- DexScreener pool data showed correct TVL and volume but doesn't reveal per-wallet positions

**Lesson**: Vault entries MUST be backed by on-chain verification. Estimated data should be flagged as `(est.)` and verified on next run.

### 3. Duplicate Vault Entries
- Two "## 2026-05-05 Update" entries existed with contradictory data:
  - Entry 1: Range $9.25-$9.59 (rebalanced range), 64.7% efficiency
  - Entry 2: Range $8.95-$9.36 (old target range), 68.3% efficiency
- Entry 2 used stale config range instead of actual position range

**Lesson**: Use `atomic-vault-append.py` to prevent duplicates. Before writing, check for existing entry on same date.

### 4. Transaction Analysis Revealed Withdrawal Pattern
- Wallet sent AVAX to 0x18556da... (20KB contract — likely a vault or multisig)
- Also interacted with 0x45a62b... (6KB contract — likely a router)
- No direct LFJ pool contract interaction detected in recent txns

**Lesson**: When position disappears, check `txlist` for recent activity. Large AVAX outflows + contract interactions suggest intentional withdrawal.

## Verification Checklist (for future runs)

1. [ ] Run `fetch-lfj-position.py` with ±100 bin scan
2. [ ] If zero positions, expand to ±200
3. [ ] If still zero, check Routescan wallet balance
4. [ ] If dust-only, fetch recent `txlist` for withdrawal evidence
5. [ ] If confirmed withdrawal, update vault with withdrawal notice
6. [ ] Send 🚨 CRITICAL alert to Telegram
7. [ ] Escalate to Gentech via Green Room

## Wallet Address Reference
- **Tracked wallet**: `[REDACTED_WALLET]`
- **LFJ Pool**: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- **Destination (post-withdrawal)**: `0x18556da13313f3532c54711497a8fedac273220e` (contract)
