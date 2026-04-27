# Gentech HQ

Central command folder for the Gentech Agency. This is where approvals land, cross-group TODO items live, and daily summaries from all teams get rolled up.

- **Approvals/** — Pending decisions, sign-offs, and budget approvals formatted as `YYYY-MM-DD — [Topic].md`. Jordan approves with [x], rejects with [ ].
- **TODO/** — Cross-group action items that don't belong to any single department.
- **Summaries/** — Daily morning digest (cron-generated at 6:00 AM EDT) consolidating highlights from Labs, Strategies, and Entertainment.

## Daily Summary Cron
Every morning at 6:00 AM EDT, a scheduled agent:
1. Reads 24h of activity from 02-Labs, 03-Strategies, 04-Entertainment, 09-Green Room, 11-Mess Hall
2. Condenses into one `YYYY-MM-DD Summary.md` placed in `Summaries/`
3. Posts a TL;DR to the main Telegram group
