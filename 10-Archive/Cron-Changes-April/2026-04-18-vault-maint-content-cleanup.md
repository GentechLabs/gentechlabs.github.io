# Vault Maintenance — Content Cleanup Added

**Date:** 2026-04-18
**Job:** 93e43ddac261 (Vault Maintenance & Green Room Cleanup)
**Change:** Added Task 3 — Content cleanup

## What changed
- Added content cleanup to vault maintenance cron
- Scans `08-Daily/content-drafts/` and `04-Entertainment/Content-Clips/`
- Files marked `**Status:** POSTED` → archived after 7 days
- Files marked `**Status:** READY TO DRAFT` older than 30 days → flagged stale

## Status convention
When content is published to Twitter/X, update the draft file:
- Change `**Status:** READY TO DRAFT` → `**Status:** POSTED`
- Cron handles the rest automatically
