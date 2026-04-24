# Bridge Security Analysis — April 2026

## Trigger: LayerZero DVN Security Concern

- KelpDAO exploited due to 1-of-1 DVN configuration on LayerZero
- Dune analysis: ~47% of 2,665 OApps run 1-of-1 DVN, ~45% run 2-of-2, only ~5% run 3-of-3+
- Source: @CryptoCurb alert, Dune analytics on LayerZero integrations (last 90 days)

## Status: Needs deeper research when web access returns
- [ ] Pull specific Dune dashboard
- [ ] Map LayerZero exposure in watchlist tokens (BTC,SOL,LINK,AVAX,TAO,XAUt,BEAM)
- [ ] Compare: Wormhole vs Axelar vs Hyperlane vs native bridges

## Preliminary Assessment

### Wormhole
- 19 Guardians, 13/19 threshold
- Recovered from $320M hack (Feb 2022) — Jump absorbed loss
- More predictable security model (no user-configurable risk)
- Risk: Guardian set centralization

### For AAE Cross-Chain (future)
- If building cross-chain features: 3-of-3+ DVN minimum on LZ, or evaluate Axelar/Hyperlane
- Never ship with 1-of-1 DVN config

Last updated: 2026-04-21
