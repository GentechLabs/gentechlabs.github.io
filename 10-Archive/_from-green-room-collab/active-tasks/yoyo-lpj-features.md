## YoYo — LFJ Features Research (2026-04-19)

**Topic:** Bringing LFJ Liquidity Book features to our AAE/AgentEscrow project
**Key insight from conversation:** LFJ's Liquidity Book allows asymmetric LP ratios (60/40 USDC:AVAX), custom bin placement (bid-ask at edges, empty middle), and shape selection (curve vs bid-ask). This is a real edge over Uniswap V3 where deposit ratios are mathematically locked.

**Features worth extracting:**
1. Bin-level liquidity control (discrete price points, not continuous range)
2. Asymmetric LP positioning (custom ratio per side)
3. Shape selection (curve = max fees at center, bid-ask = max fees at edges)
4. Dynamic rebalancing triggers (fee efficiency threshold-based)

**Status:** Jordan suggested moving this to HQ for team discussion.
