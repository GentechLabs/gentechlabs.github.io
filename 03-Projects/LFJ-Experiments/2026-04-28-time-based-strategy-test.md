# LFJ Time-Based Strategy Test

**Date Started:** April 28, 2026
**Hypothesis:** Smart money profit-takes during US overnight (Asia hours). Run bid/ask at night, curve during the day.

## Pattern Observed
- **Night (US sleeping):** Price volatile, pullbacks happen — ideal for bid/ask
- **Day (Asia awake):** Price stabilizes (15-18¢ range), tight channel — ideal for curve

## Test Plan
- **Before bed:** Rebalance to bid/ask, range $0.850 → $0.930
- **Morning:** Check results, potentially flip back to curve
- **Duration:** Test for a few days to confirm pattern

## Settings
- Pool: AVAX/USDC
- Bid/Ask range: $0.850 - $0.930
- Goal: Capture fees on the way down during overnight profit-taking

## Log
| Date | Strategy | Range | 24H Fees | Notes |
|------|----------|-------|----------|-------|
| 04/28 | Bid/Ask (overnight test) | 0.850-0.930 | pending | First night of test |
