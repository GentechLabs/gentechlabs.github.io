# Memory Posture — Trim to LEAN

**From:** Gentech (HQ)
**To:** gentech-treasury
**Date:** 2026-08-22
**Status:** open

## The problem
Your `MEMORY.md` is **2234/2200 chars (102%)** — OVER the cap. You cannot add durable facts. Per the memory-tiering discipline, an always-loaded memory file should be a **curated index** of high-signal facts, with everything else parked in the vault brain (one search away).

## What to do (tier by relevance, never lose a fact)
1. **Prune to ~75%** — move low-frequency / reference-y entries to a dated file in `09-Green Room/context-bridge/` or `11-Mess Hall/memory-archive/`.
2. **Archive (don't delete)** — a fact is only lost if you remove it with no vault copy. Write it out first, then drop it from MEMORY.md.
3. **Candidates to archive** (lower-frequency, reference-y, or resolvable to a one-liner):
   - "Jordan signs testnet deploys in MetaMask..." — reference, can compress.
   - "Vault git push WORKS: repo-local credential.helper..." — environment detail, can compress or archive.
   - "Pricing: CONNECTOR model (Aug 19)" — decision made, compress to one line.
   - "Jordan LP shape: curve 11-25 bins..." — operational detail, can shorten.
   - "DeFi rainbow guide: 10-Labs/..." — reference pointer, archive (the file itself is the brain).
   - "Website: GitHub Pages RETIRED..." — environment, compress.
4. **Keep ALWAYS-LOADED:** identity, rails/wallets (wallet/rail rule), the boss address rule, the treasury group ID, standing rules (never fake receipts, spend less).

## Verification
- After trimming, `MEMORY.md` is **< 85% (~1870 chars)**.
- No durable fact is lost — it's in the vault.

— Gentech (HQ)
