---
name: wealth-path-yield-monitoring
description: Protocol for analyzing LP positions against the "Sustainable Wealth Path" tiered milestones.
---

# Wealth Path Yield Monitoring

## Trigger
Use this skill when analyzing LP tracker screenshots, cron reports, or portfolio snapshots for the AAE project.

## The Milestones
The goals are cumulative daily yield targets:
- **M1**: $5 / Day (Baseline/Completed)
- **M2**: $20 / Day (Immediate Target)
- **M3**: $55 / Day (The Birthday Milestone - Sep 2, 2027)
- **M4**: $200 / Day (The Freedom Milestone)
- **Ultimate Goal**: $500 / Day

## Workflow
1. **Extract Raw Data**: Use `vision_analyze` to get:
    - Current Price
    - TVL / Position Value
    - APR (7D)
    - Range Status (Centered, In-Range, Out-of-Range)

2. **Calculate Daily Contribution**:
    - Formula: `(Position Value * APR) / 365`
    - Result: "Current Daily Yield = $X.XX"

3. **Map to Milestone**:
    - Progress % = `(Current Total Daily Yield / Current Target Milestone) * 100`
    - Identify the active milestone (usually M2 until hit).

4. **Gap Analysis**:
    - Calculate the shortfall: `Target Milestone - Current Total Daily Yield`.
    - Determine required TVL injection at current APR to close the gap.

5. **Strategic Recommendation**:
    - If "Out-of-Range": Priority 1 is re-centering to resume yield.
    - If "Centered": Recommend scaling TVL or shifting to higher APR pools (Base/Solana/AVAX) to accelerate milestone progression.

## Pitfalls
- **Ignoring Range**: High APR is irrelevant if the price is out of range. Always check range first.
- **Overlooking Fees**: Remember that high-frequency re-centering can eat into the daily yield.
- **Single-Chain Bias**: Ensure the yield is aggregated across all AAE layers (Base, Solana, AVAX).

## Reporting Template
**Wealth Path Pulse** 📈
- **Current Daily Yield**: $[Value]
- **Active Milestone**: [M-Number] ($[Target]/day)
- **Progress**: [XX]%
- **Gap**: $[Shortfall]/day
- **Action**: [Hold/Re-center/Scale]
