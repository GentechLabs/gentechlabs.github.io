---
name: wealth-path-lp-monitoring
description: Protocol for integrating the Sustainable Wealth Path (S2S27) milestones into automated LP monitoring crons.
---

# Sustainable Wealth Path LP Monitoring

## Trigger
Use this when managing LP positions that are part of the S2S27 wealth accumulation strategy.

## Workflow
1. **Milestone Mapping**:
   - M1: $5/day (Completed)
   - M2: $20/day (Total needed: $2,500 - $3,000)
   - M3: $55/day (Total needed: $8,000 - $9,000)
   - M4: $200/day (Total needed: $24,000 - $30,000)

2. **Cron Report Enhancement**:
   - **Header**: Include `[S2S27 PATH: ACTIVE]`.
   - **Progress**: Calculate `% of Total Value` toward the next applicable milestone.
   - **Yield Gap**: compare `actual_daily_yield` (current_value * current_apr / 365) vs `milestone_daily_target`.
   - **DCA Tracking**: Verify if total balance growth aligns with the $100/week DCA schedule.

3. **Alerting**:
   - Trigger 'Milestone Breath' alert when the total value crosses into a new milestone tier.
   - Trigger 'Drift Alert' if the current daily yield drops below 80% of the milestone target.

## Pitfalls
- Do not confuse target total value (e.g. $3,000) with target daily yield (e.g. $20/day). They are linked but the yield depends on the current APR of the chosen pool.
- Ensure calculations account for the 'Curve' shape distribution which concentrates yield.
