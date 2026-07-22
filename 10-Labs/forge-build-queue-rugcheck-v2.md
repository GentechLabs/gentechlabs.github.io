⚠️ **DEPRECATED — Build Queue moved to JSON**
The canonical build queue is now at `scripts/build_queue.json`.
This file is stale — do not edit or reference it.
Run `python3 /root/.hermes/profiles/gentech/scripts/build_queue_tick.py` to regenerate the Forge handoff.

# Forge Build Queue — Rugcheck v2 Fix

**Priority:** High
**Status:** Pending (Forge lane)
**Issue:** rugcheck.gentechlabs.net returns 522 Cloudflare timeout — origin unreachable

**What's happening:**
- Cloudflare proxy can't reach the origin server
- All requests to rugcheck.gentechlabs.net return 522
- Blocks: security directory listings (GoPlusSecurity, OffcierCia rug-check repos), Ecosystem Lister submissions, x402scan indexing

**Likely causes:**
1. Origin server down or crashed
2. Cloudflare tunnel/Argo disconnected
3. Port binding changed (was port 8088)
4. SSL configuration mismatch

**Fix steps (Forge):**
1. SSH into the VPS and check if rugcheck v2 API is running: `curl localhost:8088/health`
2. If not running, restart: cd into `/root/rugcheck/api/` and restart the service
3. If running, check Cloudflare tunnel status: `cloudflared tunnel list`
4. Verify DNS resolution and proxy status in Cloudflare dashboard
5. Fix any port/SSL mismatches

**Related:** api.gentechlabs.net also needs `.well-known/x402.json` at root path (currently has `.well-known/x402` only) — blocks x402scan and Agentic.Market auto-indexing. Fix when deploying.
