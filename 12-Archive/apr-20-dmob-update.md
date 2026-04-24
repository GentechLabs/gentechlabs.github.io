# DMOB — April 20, 2026 Status

## 1:47 PM EDT — LP Range Monitor Rebuilt

**Problem:** Old LP monitor cron job (`c2c2e40b440e`) was dead — script and state file missing from `/opt/hermes-agents/yoyo/...`

**Rebuilt:**
- Created new Python script: `lp-range-monitor.py` (DexScreener API, no auth needed)
- Deployed to `~/.hermes/scripts/` (cron requirement) + vault copy at `03-Strategies/scripts/`
- Created new cron job: `b2bb2bae4fc5` → delivers to Strategies group (`-1002916759037`)
- Schedule: every 10 min, quiet hours 11PM–6:30AM

**Alert Rules (per Jordan's spec):**
- In range + efficiency ≥ 75% → **silent**
- In range + efficiency < 75% → **alert**
- Out of range → confirm on 2nd check, then **alert**
- Quiet hours → **paused**

**Current Status:** AVAX at $9.26, **0.4% below** $9.30 lower bound → OUT OF RANGE

**Vault docs updated:**
- `02-Labs/cron-jobs-registry.md` — job ID
- `03-Strategies/LP-Monitor-Rules.md` — job ID + script path
- `03-Strategies/Cron-Jobs-Reference.md` — job ID + range fix

**Note:** Pause/resume companion jobs (`2f58ab69f4d2`, `ef9aa51eedbc`) still need rebuild if desired — the script handles quiet hours natively now so they may be redundant.
