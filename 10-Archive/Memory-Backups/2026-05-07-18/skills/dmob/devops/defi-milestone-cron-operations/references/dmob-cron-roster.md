# DMOB Cron Job Roster

Updated: May 5, 2026

All jobs pinned to `custom:XiaomiMega` / `mimo-v2.5`.

## Active Jobs

| Job Name | ID | Schedule | Deliver | Notes |
|---|---|---|---|---|
| Defi Milestone — Morning | f709d93b25ab | 30 8 * * * | origin | Skills: Crypto Watchlist, LP Monitor, trade-off-platform |
| Defi Milestone — Evening | 6a85a903e471 | 0 21 * * * | origin | Same skills as morning |
| LP Position Monitor Hourly | 629c4e1606c0 | 0 11-23/1 * * * | origin | Script: lp-aae-signal-monitor.py |
| blockchain-contest-scanner | 80ff99e24938 | 0 9 * * * | origin | Scans C4, Cantina, Devpost |
| LayerZero DVN Monitor (3-day) | 99575a3aa4b6 | 0 10 */3 * * | origin | DVN security monitor |
| x402 Ecosystem Watch | f7c7b1dc89a9 | 0 10 */14 * * | origin | Bi-weekly |
| brain-backup | 3044d70c58bc | 0 6 * * * | Labs group | Brain backup to repo |
| Sunday Skill Update Check | 3a2856084f88 | 0 12 * * 0 | DM skills group | Weekly |

## Retired/Disabled

- `3fc1a11a88d7` — Original single daily D5 job (disabled, replaced by morning/evening)
- `67e1969f9b2b` — Old LP monitor cron (replaced by 629c4e1606c0)

## YoYo Jobs (separate profile)

- `3258c64b` — DeFi Milestone (every 10 min, 6-23 UTC) — runs on yoyo profile
