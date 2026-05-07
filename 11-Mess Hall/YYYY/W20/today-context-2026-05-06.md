
🔴 **CRITICAL: Multi-Profile Nous OAuth Failure** 🔴

**Issue:** All Hermes profiles (gentech, yoyo, dmob, desmond) share the same Nous token which has expired.  
**Action:** @DMOB must run `hermes model` to re-authenticate **immediately**.  
**Why manual:** Device code endpoint is rate-limited (429) — automated recovery blocked.  
**Incident log:** 00-HQ/Operations/Infrastructure-Issues.md  
**Priority:** P0 — Entire agent fleet offline.

Verification URL (if device flow were available):
  https://portal.nousresearch.com/manage-subscription?user_code=CLLT-KXY8
User code: CLLT-KXY8

After browser approval, completion script would be:
  ~/.hermes/profiles/gentech/scripts/complete_nous_device_flow.sh
