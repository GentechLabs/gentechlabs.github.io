# 🔧 Vault Maintenance Cron Update — Handoff to Gentech

**From:** Desmond
**To:** Gentech (HQ Bot)
**Date:** Apr 21, 2026
**Priority:** Medium

## What's Done
- ✅ Created `11-Mess Hall/daily/` folder with README.md
- ✅ Retention policy: 7 days

## What Needs Doing
Update cron job `4835b4241e9d` ("Vault Maintenance — Weekly Audit") to include daily summary cleanup.

**Add to the vault maintenance prompt:**

```
## Daily Summary Cleanup
- Scan `11-Mess Hall/daily/` for files older than 7 days
- Move to `10-Archive/Daily-Summaries/YYYY-MM/` before deleting
- Log deletions in Mess Hall status note
```

## Why
Jordan requested a daily summary folder with auto-purge. The cron job is owned by the HQ bot (not in Desmond's or DMOB's cron lists), so only Gentech can update it.

## Job Details
- **Job ID:** `4835b4241e9d`
- **Schedule:** 10:30 PM Sunday
- **Current name:** Vault Maintenance — Weekly Audit
