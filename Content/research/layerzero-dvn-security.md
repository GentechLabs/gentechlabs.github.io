# LayerZero DVN Security Concern

**Date:** April 20, 2026
**Source:** @CryptoCurb on X, @Dune analytics
**Severity:** HIGH — systemic risk

---

## TL;DR
KelpDAO got hacked via LayerZero's 1/1 DVN configuration. Dune analyzed ALL LayerZero integrations — 47% are running the same weak config.

## Stats (out of ~2,665 OApp contracts, last 90 days)
- **47%** run 1-of-1 DVN (WEAK — same as KelpDAO)
- **45%** run 2-of-2
- **~5%** run 3-of-3 or higher (safe)

## What This Means
- Nearly half of all LayerZero integrations are vulnerable to the same attack vector
- LayerZero blamed KelpDAO for "irresponsible" 1/1 DVN setup
- But 47% of the ecosystem has the same problem — it's systemic

## Action Items for Gentech
- [ ] Audit our protocols/repos for LayerZero integrations
- [ ] Check if `aae-contracts` or `kite-agent-commerce` touch LayerZero bridges
- [ ] If yes: verify DVN configuration (should be 2/2 or 3/3 minimum)
- [ ] Monitor for exploit news on any protocols we hold positions in

## Reference Tweet
https://x.com/CryptoCurb/status/2046293810934890625
