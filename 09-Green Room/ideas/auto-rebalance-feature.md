# Auto-Rebalancing Feature Request

**Date:** 2026-06-14
**Requested by:** Jordan
**Priority:** High — quality of life improvement

## The Problem
Manual rebalancing is frustrating:
- Price dips or spikes out of range
- Position earns zero fees while out of range
- By the time you notice and rebalance, price may have reversed
- "One minute we're sinking, next minute we're good again"

## The Vision
Gentech automatically rebalances when:
1. Price exits LP range
2. Position is out of range for X minutes (configurable)
3. Optimal rebalance opportunity detected (price near range edge)

## Technical Requirements
- Monitor AVAX price vs LP range (6.30–6.55 or whatever current range is)
- Trigger rebalance when price breaks above/below range
- New range should be set around current price
- Consider spread/width based on volatility
- Notify Jordan before executing (or auto-execute if configured)

## Implementation Path
1. Price monitor script (already have cron jobs for this)
2. Range boundary detection
3. New range calculation (center on current price, maintain width)
4. LFJ SDK integration for actual rebalance execution
5. Notification to Jordan (Telegram)

## Risk Considerations
- Gas costs for each rebalance
- Over-trading in choppy markets (whipsaw)
- Need cooldown period between rebalances
- Consider: only rebalance if out of range for >30 min (avoid noise)

## Status
- [ ] Price monitor with range detection
- [ ] Rebalance logic (new range calculation)
- [ ] LFJ SDK integration
- [ ] Notification system
- [ ] Safety guards (cooldown, min range width)
