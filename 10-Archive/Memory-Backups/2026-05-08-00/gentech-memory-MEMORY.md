Multi-agent coordination (Apr 27, 2026; updated May 7 — Option 1): Gentech = single POC in ALL 4 groups. Specialists on-demand only. Fail-safe: >10min unresponsive → auto-activate. Green Room = internal. Mess Hall = outside work (ISO week). No-Idle. Smart Routing v2: Jordan shares links → Mess Hall first, specialist input, consolidated brief to HQ.
§
Portfolio site (May 5, 2026): GitHub Pages + daily health check (job 4e21a92b8c79, 12 UTC). AAE DeFi Milestones rename.
§
LFJ rebalance workflow (May 7, 2026): Jordan screenshots → use `lfj-rebalance-handler` skill → update `.lfj-aae-config.json` (range/shape) + `.lfj-aae-state.json` (price/TVL/snapshot). Config is source of truth for cron jobs. Current: AVAX/USDC bid-ask 9.44–9.74.
§
Terminology note (May 7, 2026): It's "DeFi Milestones" not "D5". Jordan corrected this — never abbreviate to D5.
§
Crime jobs (May 7, 2026): "Crime jobs" = team term for automated cron jobs. Quiet hours: 11 PM → 6:30 AM EST (UTC-5). No Telegram deliveries in this window. All jobs rescheduled outside 4:00–11:30 UTC.
§
Financial crime jobs delivery: All finance/DeFi cron jobs must deliver to the Strategies group, not Labs. Jordan confirmed May 7, 2026.
§
DeFi Milestones cron notification policy (May 7, 2026): Job 3258c64b (every 10min) uses alert-once logic. Shows ONE notification per condition change. If same condition persists → SILENT (empty stdout = no Telegram delivery). Re-alerts only if: condition resolves then returns, severity changes, or 1hr cooldown. Script: d5-lp-consolidated.py (vault + YoYo profile). State: .lfj-d5-state.json.
§
Updated to Hermes v0.13.0 "The Tenacity Release" (May 7, 2026). Jordan directive: test new features as opportunities arise — report how they work and if process updates needed. Key features to evaluate: Kanban multi-agent orchestration, /goal persistence, no_agent cron mode, post-write lint, video_analyze, MCP SSE.