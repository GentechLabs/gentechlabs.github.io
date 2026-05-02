# 🧹 Spring Cleaning — Disk Space Recovery Plan

**Date:** 2026-05-02
**Status:** Draft — awaiting Jordan approval for destructive operations
**Current disk usage:** 105G / 193G (55%)
**Target:** Reclaim 40-60GB minimum

---

## 🔍 Audit Findings

### Biggest Offenders

| Item | Size | Type | Action |
|------|------|------|--------|
| `/root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249` | **48G** | Recursive backup disaster | **DELETE** — 5 nested `.hermes` dirs, no refs |
| Docker images (total) | 6.1GB | 3 images, 1 active container | Review/remove |
| `/root/.cache` | 3.9GB | pip/uv/playwright/huggingface | **CLEAN** |
| `/tmp` (research files) | ~120MB | HTML/JSON scrapes | **CLEAN** |
| NPM cache | 620MB | Global cache | **CLEAN** |
| Journalctl | 401MB | System logs | **CLEAN** |
| Hermes logs | 68KB | Agent logs | **ROTATE** |
| Corrupted pycache | 1.2MB | Bytecode errors | **PURGE** (already known) |

**Total recoverable if all cleared:** ~60GB

---

## 🗑️ Deletion Candidates

### Category A: Safe, No Recovery Needed (DELETE IMMEDIATELY)

1. **Bloated Hermes backup** (`/root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249`)
   - **Why:** Recursive copy bug — 5 nested `.hermes` directories
   - **Evidence:** `find ... -name '.hermes'` returns 5 matches
   - **Active data exists:** `/root/.hermes/profiles/` (4.1G, healthy)
   - **No refs:** grep across workspace finds zero references
   - **Recoverable:** The April 27 backup is only 5 days old — active profiles already have this state
   - **Savings:** 48GB

2. **Tmp research artifacts** (`/tmp/*.html`, `/tmp/*.json`, `/tmp/*.gif`, `/tmp/*.mp4`)
   - Files: `gcloud.tar.gz` (93M), `defillama_pools.json` (13M), `x402_*.json`, `cantina_*.html`, `c4_*.html`, `solana_raw.html`, `ethglobal*.html`
   - **Why:** One-time scrapes already processed, vaulted in `05-Learning/` or `03-Strategies/`
   - **Savings:** ~120MB

3. **NPM cache** (`/root/.npm`)
   - **Why:** Re-downloadable, not needed at rest
   - **Command:** `npm cache clean --force`
   - **Savings:** 620MB

4. **Corrupted Python cache** (`/usr/local/lib/hermes-agent/agent/__pycache__/`)
   - **Why:** Already causing `EOFError: marshal data too short`, needs full purge
   - **Command:** `find /usr/local/lib/hermes-agent -name '*.pyc' -delete`
   - **Savings:** 1.2MB (small but fixes critical bug)

---

### Category B: Conditional / Needs Review (REVIEW BEFORE DELETE)

5. **Docker images** (6.1GB total)
   - `browserless/chrome:latest` — 4.51GB, created 2024-02-16 (2 years old)
   - `diygod/rsshub:chromium-bundled` — 1.5GB, created 2026-04-24 (used, actively running)
   - `redis:alpine` — 134MB, actively running

   **Options:**
   - **Conservative:** Keep all (containers are running)
   - **Aggressive:** Prune unused images: `docker image prune -a` (will stop RSSHub if not careful)
   - **Best:** Stop RSSHub, remove old browserless image, pull fresh, restart — safer

   **Recommendation:** STOP → DOCKER PRUNE → RESTART workflow (see commands below)

6. **/root/.cache breakdown**
   - `camoufox`: 1.4G — browser automation cache (safe to clear)
   - `uv`: 1.0G — Python package cache (re-downloadable)
   - `ms-playwright`: 631M — browser drivers (re-downloadable)
   - `huggingface`: 142M — model cache (⚠️ DO NOT DELETE — models are large to re-download)

   **Command:** `rm -rf /root/.cache/camoufox /root/.cache/uv /root/.cache/ms-playwright`
   **Savings:** 3.0GB
   **Keep:** `/root/.cache/huggingface` (models)

7. **Journalctl logs** (401MB)
   - **Command:** `journalctl --vacuum-time=7d` (keep last 7 days)
   - **Savings:** ~300MB

8. **Old vault HTML trackers** (`Yield-Farm-Tracker*.html`, `DeFi-Milestone-Tracker.html`)
   - Current versions: `03-Strategies/Yield-Farm-Tracker-CURRENT.html` (19KB fresh), `DeFi-Milestone-Tracker-Spec.md` (replaces HTML)
   - Old HTML versions can be archived to `10-Archive/` then deleted from main vault
   - **Savings:** ~40KB each, not significant but reduces clutter

---

## 📋 Execution Plan

### Phase 1: Immediate Safe Deletes (Zero Risk)
**Recoverable: ~49GB**

```bash
# 1. Delete the recursive backup disaster (48G)
rm -rf /root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249

# 2. Clean /tmp research files
rm -f /tmp/*.html /tmp/*.json /tmp/*.gif /tmp/*.mp4 /tmp/gcloud.tar.gz 2>/dev/null

# 3. NPM cache clean
npm cache clean --force

# 4. Purge corrupted Python bytecode
find /usr/local/lib/hermes-agent -name '*.pyc' -delete

# 5. Journalctl vacuum (keep 7 days)
journalctl --vacuum-time=7d
```

**Verify:** `df -h /` — expect ~55% → 50%

---

### Phase 2: Cache Cleanup (Low Risk)
**Recoverable: ~3GB**

```bash
# Clear browser/cache without touching models
rm -rf /root/.cache/camoufox
rm -rf /root/.cache/uv
rm -rf /root/.cache/ms-playwright
# DO NOT TOUCH /root/.cache/huggingface
```

**Verify:** `du -sh /root/.cache` — should drop from 3.1G → 600M

---

### Phase 3: Docker Cleanup (Medium Risk — containers must restart)

**⚠️ WARNING:** RSSHub is actively running (Up 4 days). Don't delete images in use.

```bash
# Stop RSSHub stack first
cd /root/workspace/rsshub && docker compose down

# List images
docker images

# Remove old browserless (4.51GB, from 2024)
docker rmi diygod/rsshub:chromium-bundled  # old
docker image prune -a -f  # remove dangling + unused

# Pull fresh browserless if needed
docker pull browserless/chrome:latest

# Restart RSSHub
docker compose up -d
```

**Expected savings:** 4.5GB (if browserless can be replaced with smaller alternative or unused)

**Alternative:** If RSSHub needs browserless, switch to `browserless/chrome` with `--shmsize=1g` flag to reduce footprint.

---

### Phase 4: Archive Old Vault Data (Medium Risk — needs verification)

Old HTML trackers and archived logs can be compressed:

```bash
# Compress old HTML trackers in place (gzip -9)
gzip -9 /root/vaults/gentech/03-Strategies/Yield-Farm-Tracker.html
gzip -9 /root/vaults/gentech/03-Strategies/DeFi-Milestone-Tracker.html

# Move to archive
mkdir -p /root/vaults/gentech/10-Archive/Compressed-HTML-Trackers
mv /root/vaults/gentech/03-Strategies/{Yield-Farm-Tracker.html.gz,DeFi-Milestone-Tracker.html.gz} \
   /root/vaults/gentech/10-Archive/Compressed-HTML-Trackers/
```

**Savings:** Negligible but organizes vault.

---

## ⚠️ Do NOT Touch

- `/root/.cache/huggingface` — models are expensive to re-download
- `/root/vaults/gentech/11-Mess Hall/` — active coordination data
- `/root/.hermes/profiles/` — active agent state (only clean old backups)
- `/root/repos/` — code clones (check if redundant)

---

## ✅ Verification Checklist

After each phase, run:

```bash
df -h /                         # overall
du -sh /root/vaults/gentech     # vault size
du -sh /root/.hermes            # hermes profile size
du -sh /root/.cache             # cache size
docker system df               # Docker reclaimable space
```

**Target:** < 80G used (from 105G) → **25GB freed minimum**

---

## 📦 Backup Strategy Before Deletion

For Category B items (Docker images, vault HTML), create manifest first:

```bash
# Manifest of what we're about to delete
cat > /tmp/spring-cleanup-manifest.txt <<EOF
# 2026-05-02 Spring Cleanup Manifest
# Generated by YoYo (Strategies)

[DELETED - Category A]
- /root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249 (48G) [NO REFS]
- /tmp/*.html, /tmp/*.json (120MB) [vaulted]
- /root/.npm cache (620MB) [re-downloadable]

[ARCHIVED - Category B]
- Old HTML trackers → 10-Archive/Compressed-HTML-Trackers/

[DOCKER - UNDER REVIEW]
- browserless/chrome:latest (4.51GB, 2024-02-16) — replace with fresh?
- rsshub:chromium-bundled (1.5GB) — actively used
EOF

# Copy to vault for record
cp /tmp/spring-cleanup-manifest.txt /root/vaults/gentech/10-Archive/cleanup-manifests/2026-05-02-spring-cleanup.txt
```

---

## 🚀 Recommendation

**Execute Phase 1 + 2 immediately** (52GB, zero risk, no restart needed).

**Phase 3:** Schedule downtime for RSSHub (coordinate with DMOB/Desmond if they're using it).

**Phase 4:** Wait until after Solana Frontier submission (May 11) to avoid disrupting active work.

---

## 📊 Before/After

| Location | Before | After (Phases 1+2) | Δ |
|----------|--------|-------------------|---|
| `/` (root) | 105G | ~53G | **-52G** |
| `/root/vaults` | 57G | 57G (unchanged) | 0 |
| `/root/.cache` | 3.1G | 0.6G | **-2.5G** |
| `/tmp` | 13G | ~20M | **-13G** |
| `/root/.npm` | 620M | ~50M | **-570M** |
| Docker images | 6.1GB | TBD (review) | ? |

**Total Phase 1+2 recovery: ~52GB (49% of current usage)**

---

*Documented by YoYo (Strategies) — 2026-05-02*
