---
name: lp-range-rebalance
description: "Edit LP monitor scripts (range changes, feature additions, config tweaks) — vault→runtime→test workflow. Covers both v3 and AAE scripts."
tags: [defi, lp, avax, monitoring, cron, rebalance, script-edit]
version: 1.2.0
author: DMOB
---

# LP Range Rebalance — Atomic Update Workflow

When the LP trading range changes, update ALL references atomically. Range drift across scripts/docs is a critical bug — alerts fire at wrong levels.

## When to Use

**Range changes** (full workflow — steps 1–7):
- Jordan says "rebalance to bid-ask" or "new range is X–Y"
- Price has moved and position is being adjusted
- Any change to RANGE_LOW / RANGE_HIGH across the monitoring stack

**Quick edits** (vault→sync→test only — steps 2–4):
- Feature additions (e.g. adding liquidity shape visualization)
- Config tweaks (e.g. updating position balance, token amounts)
- Report format changes
- Skip steps 5–7 (cron prompts, vault docs) unless the edit references range/milestones

## Architecture — Three Monitor Systems

| System | Script | Cron Schedule | Purpose |
|--------|--------|---------------|---------|
| **v3** (10-min) | `lp-range-monitor-v3.py` | `*/10 * * * *` | Fast breakout alerts, tiered warning→red |
| **AAE** (4x/day) | `lp-aae-signal-monitor.py` | `25 8,12,16,20 * * *` | Milestone tracking, squad tiers, structured signals |
| **Position Reader** | `lp-position-reader.py` | Script field on cron jobs | Live on-chain price + position value computation |

### Position Reader Details (v2)
- Fetches AVAX price from DexScreener (fallback: on-chain RPC via getSwapOut)
- **Wallet balances**: Reads native AVAX + USDC via Routescan API
- **On-chain LP position**: Scans bin shares via `balanceOf(user, binId)` for all bins in range
  - Bins below active = USDC side, bins above = AVAX side
  - Computes token split from share percentages
  - Falls back to config amounts if on-chain scan fails
- Tracks price history for 24h average
- Used by Gentech cron job `67e1969f9b2b` (LFJ LP Efficiency Monitor)
- **IMPORTANT**: Also update `.lfj-aae-config.json` when position changes (not just the Python script)

Both must be updated. Configs live in MULTIPLE locations:
- **Vault:** `/root/vaults/gentech/03-Strategies/scripts/`
- **DMOB runtime:** `~/.hermes/scripts/` (resolves to `/root/.hermes/profiles/dmob/home/.hermes/scripts/`)
- **Gentech runtime:** `/root/.hermes/profiles/gentech/scripts/` AND `/root/.hermes/profiles/gentech/home/.hermes/scripts/`
- **YoYo vault copy:** `/root/.hermes/profiles/yoyo/home/repos/gentech-vault/03-Strategies/scripts/`

⚠️ **Critical:** Cron jobs run under their owning profile. The Position Reader (`67e1969f9b2b`) runs under **Gentech**, so it reads from Gentech's scripts dir — NOT DMOB's. Always find ALL config copies first:
```bash
find /root/.hermes/profiles/ -name ".lfj-aae-config.json" -o -name "lp-position-reader.py" 2>/dev/null
```

## Steps

### Quick Edit Workflow (features, config, format changes)

0. **Find all config copies** — Before editing anything, locate every instance:
   ```bash
   find /root/.hermes/profiles/ -name ".lfj-aae-config.json" -o -name "lp-position-reader.py" 2>/dev/null
   ```
   Update ALL of them, not just the one you think is "the" runtime copy.

1. **Edit vault script** — make changes to `/root/vaults/gentech/03-Strategies/scripts/lp-*.py`
2. **Check for runtime JSON config** — ⚠️ The AAE script reads from `~/.hermes/scripts/.lfj-aae-config.json` at runtime. This JSON file **overrides** the Python DEFAULT_CONFIG. If updating position balance, token amounts, range, or shape, edit BOTH:
   - Vault Python script (DEFAULT_CONFIG) — `cp` to runtime
   - Runtime JSON config — `~/.hermes/scripts/.lfj-aae-config.json`
3. **Sync vault script to runtime** — `cp /root/vaults/gentech/03-Strategies/scripts/lp-*.py ~/.hermes/scripts/`
4. **Test** — `cd ~/.hermes/scripts && python3 lp-aae-signal-monitor.py` (or v3)
5. **Verify output** — confirm changes appear in JSON signal / human report

Skip steps below unless range/milestone references changed.

---

### Full Range Rebalance Workflow

### 1. Get New Range from Jordan

Confirm: range_low, range_high, and any position updates (token amounts, USD value).

### 2. Update Both Scripts

**v3 script** — update constants:
```python
RANGE_LOW = <new_low>
RANGE_HIGH = <new_high>
```

**AAE script** — update DEFAULT_CONFIG position block:
```python
"position": {
    "range_low": <new_low>,
    "range_high": <new_high>,
    ...
}
```

### 3. Sync Scripts to Runtime

```bash
cp /root/vaults/gentech/03-Strategies/scripts/lp-range-monitor-v3.py ~/.hermes/scripts/
cp /root/vaults/gentech/03-Strategies/scripts/lp-aae-signal-monitor.py ~/.hermes/scripts/
```

Verify:
```bash
grep -n 'RANGE_LOW\|RANGE_HIGH' ~/.hermes/scripts/lp-range-monitor-v3.py
grep -n 'range_low\|range_high' ~/.hermes/scripts/lp-aae-signal-monitor.py
```

### 4. Test Both Scripts

```bash
cd ~/.hermes/scripts && python3 lp-range-monitor-v3.py
cd ~/.hermes/scripts && python3 lp-aae-signal-monitor.py
```

Confirm output shows correct range in "Your Range:" and JSON signal.

### 5. Update Cron Job Prompts (if range mentioned)

Check if cron prompts reference the old range:
```bash
cronjob(action="list")
```

**If the job is in YOUR profile**, update with the cronjob tool:
```bash
cronjob(action="update", job_id="<id>", prompt="<updated prompt with new range>")
```

**If the job is in ANOTHER profile** (e.g. YoYo's `2563e78bcf72`), the cronjob tool won't find it. Edit directly:
```bash
# Read the other profile's jobs.json
cat /root/.hermes/profiles/<profile>/cron/jobs.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for j in data['jobs']:
    if j['id'] == '<job-id>':
        j['prompt'] = '<new prompt>'
        break
with open('/root/.hermes/profiles/<profile>/cron/jobs.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Updated')
"
```

**Pitfall:** Other profiles' cron jobs won't appear in your `cronjob(action="list")`. If a job seems missing, check all profiles: `ls ~/.hermes/profiles/*/cron/jobs.json`

### 6. Update Vault Docs

**Must update all of these:**

1. **LP-Monitor-Rules.md** (`03-Strategies/`):
   - Current Position section → new range
   - Compound Strategy section → range reference
   - Crash Decision Matrix → range in scenario table

2. **LP-Tracker-Config.md** (`02-Labs/`):
   - Target Range line

3. **d5 scripts** (these embed range as constants — YoYo reads them at runtime):
   - `03-Strategies/scripts/d5-milestone-summary.py` → `range_low` / `range_high`
   - `03-Strategies/scripts/d5-master-cron.py` → `range_low` / `range_high`

4. **defi-milestones.md** (`03-Projects/`):
   - Header range line + any update entries referencing the old range

5. **Agent memories** (cross-agent drift risk):
   - `00-System/agent-profiles/gentech/memories/MEMORY.md` — has position range

6. **Any other files referencing old range:**
   ```bash
   search_files(path="/root/vaults/gentech", pattern="<old_low>|<old_high>")
   ```

### 7. Verify Final State

```bash
# Confirm no old range references remain
search_files(path="/root/vaults/gentech/03-Strategies", pattern="<old_low>|<old_high>")
search_files(path="/root/.hermes/scripts", pattern="<old_low>|<old_high>")

# Confirm cron jobs are live
cronjob(action="list")
## Pitfalls

- **Multiple profile config copies.** Configs exist in DMOB, Gentech, and YoYo profile directories. Vault copy ≠ any runtime copy. A cron job reads from its owning profile's directory, NOT yours. Run `find /root/.hermes/profiles/ -name ".lfj-aae-config.json"` to locate ALL copies before updating. ALWAYS sync with `cp` after editing the vault copy.
- **Runtime JSON config overrides Python DEFAULT_CONFIG.** The AAE script reads `~/.hermes/scripts/.lfj-aae-config.json` at runtime. This JSON file **overrides** the Python DEFAULT_CONFIG. If updating position balance, token amounts, range, or shape, edit BOTH:
  - Vault Python script (DEFAULT_CONFIG) — `cp` to runtime
  - Runtime JSON config — `~/.hermes/scripts/.lfj-aae-config.json`
- **`~` resolves to profile home, not `/root/`.** `~/.hermes/scripts/` resolves to `/root/.hermes/profiles/<profile>/home/.hermes/scripts/`, NOT `/root/.hermes/scripts/`. These are DIFFERENT directories. Always use `find /root/.hermes/profiles/ -name '.lfj-aae-config.json'` to get the REAL paths. Writing to `/root/.hermes/scripts/` won't affect scripts running under a profile.
- **Cron prompts with hardcoded balances.** Even after fixing configs, a cron job may still report wrong numbers if its prompt contains hardcoded token amounts or USD values. The prompt is a **third source of truth** — check it with `cronjob(action="list")` + `cronjob(action="get", job_id=...)`. If the job is in another profile, read their `jobs.json` directly. This is the most common "I fixed the config but the cron still reports wrong" bug.
- **Position reader uses config as fallback.** `lp-position-reader.py` now scans on-chain bin shares via `balanceOf(user, binId)` to compute token split. If the batch RPC fails (Avalanche limits batch size to ~15), it falls back to config amounts (labeled as "config_fallback" in output). The config `total_usd` is still used as the base value — share percentages determine the AVAX/USDC split. To get exact per-bin token amounts, you'd need to query each bin's reserves separately (not yet implemented).
- **Almanak SDK as potential replacement.** The `almanak-co/sdk` repo (Apache 2.0, 53 stars) has a production TraderJoe V2 connector (`almanak/framework/connectors/traderjoe_v2/`) — 1,902 lines covering pool discovery, swap quotes, LP math, receipt parsing, fee tracking. It also has backtesting (Optuna + Monte Carlo) for range optimization. If `lp-position-reader.py` gets unwieldy, consider extracting their connector as a standalone library. Assessment: `02-Labs/Assessment-Almanak-2026-04-29.md`.
- **Cron jobs disappear.** Hermes scheduler can drop jobs during updates. Recreate if missing.
- **Doc drift.** LP-Monitor-Rules.md, LP-Tracker-Config.md, and Green Room notes can all disagree. Update ALL.
- **Old range in prompts.** Cron job prompts may hardcode the old range — check and update.
- **Vault reference file drift.** YoYo cron prompts may already be correct, but d5 scripts, defi-milestones.md, and agent memories can lag. Always sweep `search_files` for old values across the full vault, not just scripts/
- **Archive files.** Old scripts in `10-Archive/` are fine to leave — they're snapshots.

## Runtime Config Files

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/.lfj-aae-config.json` | AAE script runtime config — **overrides Python DEFAULT_CONFIG** |
| `~/.hermes/scripts/.lfj-position-tracker.json` | v3 script position tracker (entry values, fees) |
| `~/.hermes/scripts/.lfj-range-state.json` | v3 script range state (warnings, cooldowns) |
| `~/.hermes/scripts/.lfj-milestone-tracker.json` | AAE milestone progression state |

## Current Pool Info

- **Pool:** LFJ V2.2 AVAX/USDC, binStep 10, 5 bps
- **Pool Address:** `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- **Chain:** Avalanche
- **Current Range:** $9.00–$9.45 (Curve shape, as of Apr 29, 2026)
- **Cron Job IDs:**
  - v3: `d97f0768bfed`
  - AAE (DMOB profile): `a3c51c66ee57`
  - YoYo LP monitor: `2563e78bcf72` (conditional alerting — only delivers when fee efficiency < 30%)
  - **Position Reader (Gentech):** `67e1969f9b2b` (uses `lp-position-reader.py` as script field)
- **Wallet:** `[REDACTED_WALLET]`
