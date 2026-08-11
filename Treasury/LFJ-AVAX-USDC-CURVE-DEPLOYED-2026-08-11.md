# LFJ AVAX/USDC Curve LP — DEPLOYED (Aug 11, 2026)

**Status:** ✅ LIVE — 24h test running
**Wallet:** Steward `0x572ABd6461BED2258615E6b99c585Ab7c5d05037`

## Position
- **Shape:** CURVE (SDK-corrected distribution)
- **Pool:** `0x864d4e5e...` (LFJ V2.2, WAVAX/USDC, binStep 10, factory `0xb43120c4`)
- **Router:** V2.2 `0x18556DA13313f3532c54711497A8FedAC273220E`
- **Active bin:** 8362828 | Range bins: 8362823–8362833 (11 bins, ±5)
- **Price range:** $6.4167 – $6.4812 (AVAX ~$6.45)
- **Deployed:** 3.4766 WAVAX + $22.50 USDC (~$45)
- **addLiquidity tx:** `0x2e0c478dfd3f320602846aaee3dd060b13c149c139737e9a8afc8144543b535f`

## The Bug We Fixed (CompositionFactorFlawed)
Flat `[1]*n` distribution weights for both X and Y across the range breaks the
bin composition math at the edges. The correct LFJ curve distribution is
**asymmetric**: X tokens (WAVAX) go only to the active bin + positive (upper)
bins; Y tokens (USDC) go only to the active bin + negative (lower) bins, each
weighted by a Gaussian centered on the active bin. Implemented from the
`@traderjoe-xyz/sdk-v2` `getCurveDistributionFromBinRange` source.

## Verified working rail (the real win)
- **Swap rail:** ✅ USDC→WAVAX and back both work through V2.2 router (`versions=[3]`)
- **LP deploy:** ✅ with correct SDK distribution
- **RPC reads:** on-chain reader confirms position (11 bins, active 8362828)

## 24h test goals
- Compare autonomous (regime-gated, shape-aware, gas-conscious) vs manual
- Confirm fees accrue, position stays in range, agent preserves its own gas
- Withdraw path tested end-to-end when Jordan decides
