---
name: de-fi-lp-milestone-analysis
description: Analyze DeFi LP position progress toward Safe-to-Safe milestones; compute capital gap, DCA path, and yield projections
trigger:
  - Analyze DeFi position
  - milestone tracking
  - DCA path
  - capital gap
  - yield farm tracker
output_format:
  - 💰 Capital Update
  - 🏁 Progress
  - ⏳ Gap
  - 🛠️ DCA Path
  - 💡 Pro Tips
steps:
  - Detect capital increase by comparing current total position to last recorded value
  - Calculate current daily yield (fees + rewards) from position growth over known time period
  - Compare daily yield against milestone target (e.g., $20/day M2)
  - Compute capital gap: principal needed at current APR to hit target
  - Project DCA path: weeks remaining at $50-100/week (Sun-Wed/Thu-Sat split)
  - Provide 2-3 actionable optimization tips
references:
  - vault-data-sources
  - calculation-methods
  - onchain-bin-scan-technique
pitfalls:
  - Config-vs-on-chain drift (CRITICAL): Config files can diverge from the actual on-chain position when rebalances are planned but not executed, or configs are updated from stale screenshots. Always verify range via on-chain bin scan before trusting config values. See references/onchain-bin-scan-technique.md.
  - Script divergence: lp-position-reader.py reads range from the config file, so a stale config makes the reader wrong too. Use on-chain bin scan to determine actual range when discrepancies appear.
  - State file fragmentation: State caches may be scattered across ~/.hermes/scripts and profile-specific locations. Ensure unified state or acknowledge uncertainty.
  - Yield Farm Tracker HTML is manual: CURRENT.html templates are not live feeds; never cite as data.
  - Low efficiency bias: LP efficiency < 30% makes APR appear low; potential exists via range adjustment. Recommend fix before computing gap.
  - Milestone ladder mismatch: Hardcoded cron thresholds may conflict with config. Verify correct target from strategy docs.
  - Multi-profile config sync: lfj-aae-config.json exists in 6+ profile dirs. Script reads from calling profile's home. Updating one copy does NOT update others. After any config change, find all copies and update ALL of them. Verify with a test run of the script.
related_skills:
  - defi-lp-position-monitor
  - d5-milestone-tracker
  - hybrid-lp-spot-strategy
---
This skill captures the workflow and lessons from analyzing LFJ AVAX/USDC LP position (May 3–4, 2026), including script discrepancy resolution, APR inference, and projection methodology for D5 milestones.