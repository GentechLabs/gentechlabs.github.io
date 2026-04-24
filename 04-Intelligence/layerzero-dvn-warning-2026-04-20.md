# LayerZero DVN Security Warning

**Date:** 2026-04-20
**Source:** @CryptoCurb on X, citing @Dune analysis

---

## Summary

**KelpDAO got hacked** via LayerZero bridge vulnerability. LayerZero blamed KelpDAO for running a **1/1 DVN** (Decentralized Verifier Network) configuration.

## Dune Analysis Results

- **2,665 unique OApp contracts** analyzed (last 90 days)
- **47%** run 1-of-1 DVN (single point of failure) ← KelpDAO config
- **45%** run 2-of-2
- **~5%** run 3-of-3 or higher

## Risk Assessment

1/1 DVN = only ONE verifier needs to sign cross-chain messages. If compromised, bridge is compromised. LayerZero blamed KelpDAO for this pattern, but nearly HALF their ecosystem has the same vulnerability.

## Action Items

- Audit all positions for LayerZero bridge exposure
- Check if VDEX or any cross-chain vaults use LayerZero
- LFJ/Pangolin AVAX does NOT use LayerZero (native chain)
- Monitor for additional hacks exploiting 1/1 DVN configs

## Tweet Stats

- 64K+ views
- 333 likes
- 47 reposts
- Posted Apr 20, 2026
