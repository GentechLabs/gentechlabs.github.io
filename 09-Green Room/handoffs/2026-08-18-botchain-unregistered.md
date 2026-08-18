# BOT Chain Builder Challenge #2 — UNREGISTERED (Aug 18, 2026)

**Decision (Jordan, Aug 18):** Unregistered. Too tight to finish — 4 days to submission
(Aug 22), no BOT wallet/key/gas, no demo, no submission package. The critical path ran
through external gates (1 BOT gas support from Builder Hub) we don't control. Same
pattern as CockroachDB — "way too tight" → drop and free the space.

## What was done (not wasted)
- **`RWAYieldGuard.sol`** — real, well-designed contract (AI operator, risk scoring,
  circuit breaker, human-in-the-loop withdrawals). A **GTA evolution** — same
  treasury-agent logic. **Reusable** for the next RWA/asset-management play.
- Source recoverable from build-info; archived at `_archive/submissions/botchain-rwa-yield-guard/`.
- Build plan + judging criteria mapped (in `09-Green Room/specs/botchain-rwa-build-plan.md`).

## What was archived
- Project dir → `_archive/submissions/botchain-rwa-yield-guard/` (contract + artifacts kept)
- Build plan stays in `09-Green Room/specs/` (reference for future RWA plays)

## Where focus goes instead (better runway)
- **Agent Builders Cup** — build window to Aug 31 (Arbiter built + renamed)
- **Telegraph** — H1 just opened Aug 17, 3 weeks runway (x402 miner track, our exact stack)
