Multi-agent team coordination protocols (established Apr 27, 2026; updated May 7, 2026 — Option 1):
- **Option 1 (May 7, 2026):** Gentech is single point of contact in ALL Telegram groups. All specialist cron jobs rerouted to HQ (-1003863540828). Specialists (YoYo, DMOB, Desmond) on-demand only — activate when @mentioned or routed to by Gentech. Fail-safe: if Gentech unresponsive >10min, specialists auto-activate. Weekly token audit (Sundays 8 AM UTC, job a320481334a7).
- **Green Room**: Internal coordination during work. Consolidate input before presenting to Jordan.
- **Mess Hall**: Outside work discussions (ISO week format: YYYY/WXX/YYYY-MM-DD/).
- **Approval Workflow**: Checkbox format in 00-HQ/Approvals/.
- **No-Idle Directive (May 5):** When hitting a stopping point, queue next priority task. Do NOT idle.
- **Duplicate Messages**: Consolidate into a single response with clear sections.
§
Portfolio site updated May 5, 2026: "Jordan the ProtoJay" header, filterable Projects, AAE DeFi Milestones rename, hackathon statuses. Deployed to GitHub Pages + daily health check cron (4e21a92b8c79).
§
Portfolio Daily Health Check (job_id: 4e21a92b8c79): Cron job monitoring portfolio system health daily at 6 AM UTC. Checks index.html, projects.json, JS errors, GitHub Pages sync, broken links.
§
Option 1 live May 7, 2026. Gentech = single POC in all 4 groups. Specialists on-demand only. Weekly token audit Sundays 8 AM. Fail-safe: >10min unresponsive → specialists auto-activate. Doc: 00-HQ/option-1-gentech-team-leader.md.
§
Smart Routing v2 enforcement (May 7): When Jordan shares links/photos, agents MUST go to Mess Hall first, get specialist input, return consolidated brief to HQ. Jordan explicitly tested this — solo answers are a miss.
§
LFJ rebalance workflow (May 7, 2026): Jordan screenshots → use `lfj-rebalance-handler` skill → update `.lfj-aae-config.json` (range/shape) + `.lfj-aae-state.json` (price/TVL/snapshot). Config is source of truth for cron jobs. Current: AVAX/USDC bid-ask 9.44–9.74.
§
Terminology note (May 7, 2026): It's "DeFi Milestones" not "D5". Jordan corrected this — never abbreviate to D5.