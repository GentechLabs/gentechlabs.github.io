# Decisions Log

## 2026-07-08 — Hub Sync: Fix Stash-Before-Stage Bug
- **Issue:** hub-sync-nightly.py stashed working tree changes BEFORE `git add`, causing the updated defi-data.json to be stashed away and never committed/pushed
- **Fix:** Moved `git add` + `git diff --cached --quiet` BEFORE `git stash`, so our changes are staged before stashing other modifications
- **Also:** Changed verify_live() to use commit SHA URL instead of `main` branch tag to avoid CDN cache false negatives
- **Data source:** /root/vaults/gentech/defi-data.json (28 keys, 15/15 sections — always the authoritative copy)
- **Status:** ✅ Fixed and pushed (commit e1909285)
