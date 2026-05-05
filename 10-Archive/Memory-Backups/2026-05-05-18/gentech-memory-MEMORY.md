Multi-agent team coordination protocols (established Apr 27, 2026):
- **Green Room**: Internal coordination during work. Consolidate input before presenting to Jordan.
- **Mess Hall**: Outside work discussions (ISO week format: YYYY/WXX/YYYY-MM-DD/).
- **Approval Workflow**: Checkbox format in 00-HQ/Approvals/.
- **Stopping-Point Protocol**: Ask "What's next?" if Jordan is away 10-20 minutes.
- **No-Idle Directive (May 5, 2026):** When any agent hits a stopping point (waiting on Jordan approval, unavailable tool/person, external dependency), immediately queue the next priority task and keep working. Do NOT idle. Applies to all agents across all projects.
- **Duplicate Messages**: Avoid sending duplicate or overlapping messages. Consolidate into a single response with clear sections.
§
Portfolio Update Completed (May 5, 2026): Successfully updated Jordan's portfolio website with all requested changes:
- Header changed to "Jordan the ProtoJay"
- About section updated with GenTech HQ delegation layer context and timeline extended to 2027-2028
- Added filterable Projects section with JavaScript filtering
- Renamed "LFJ AVAX/USDC Auto-Rebalance" to "AAE Defi Milestones"
- Updated hackathon table: Solana Frontier and Kite AI set to BUILDING status
- Committed changes to vault and deployed to GitHub Pages
- Set up daily health check cron job (job_id: 4e21a92b8c79)
- All systems operational
§
Portfolio Daily Health Check (job_id: 4e21a92b8c79): Cron job created on May 5, 2026 to monitor portfolio system health daily at 6 AM UTC. Checks: index.html and projects.json validity, JavaScript errors, GitHub Pages sync, commit dates, broken links, missing assets.
§
Cron job routing philosophy (clarified May 5, 2026): HQ group (-1003863540828) is Jordan's personal dashboard — ALL summaries, approvals, portfolio updates, cross-department intel, and anything needing his eyes goes here. Department groups (YoYo: -1002916759037, DMOB: -1003872552815, Desmond: -1003893562036) are WORK EXECUTION channels only — no side conversations, no summaries. Internal/local jobs use 'local' or 'origin' for vault maintenance tasks.