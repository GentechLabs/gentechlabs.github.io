# 🔄 Handoff: Vault Maintenance — Add Daily Summary Cleanup

**From:** DMOB (Labs)
**To:** Gentech (HQ)
**Date:** 2026-04-21
**Priority:** P1
**Status:** ✅ Ready for action

---

## What was done
- Created `08-Daily/Daily-Summaries/` folder with README.md
- Set 7-day retention policy documented in README

## What needs doing (Gentech — cron `4835b4241e9d`)
The vault maintenance cron (`4835b4241e9d`, Sundays 10:30 PM) needs updated prompt to include:

### Add to vault maintenance prompt:
```
## Daily Summary Cleanup
- Scan `08-Daily/Daily-Summaries/` for files older than 7 days
- Move to `10-Archive/Daily-Summaries/YYYY-MM/` before deleting (or just delete if empty)
- Also clean `11-Mess Hall/daily/` entries older than 7 days (already documented in README)
```

## Why I can't do this
Job `4835b4241e9d` is not in my DMOB cron list — it's owned by another agent. Only the owning agent or Jordan can update it.

## Context
Jordan requested this in HQ thread. Folder structure is ready, just needs the cron update.
