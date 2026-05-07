---
name: system-cleanup
title: Disk Space Recovery & System Cleanup — Multi-Phase Methodology
version: 1.0.0
category: devops
trigger: "Disk usage >70% OR manual spring-cleaning request OR 'we're at like N gigs' User complaint about disk space"
description: >
  Systematic, multi-phase disk reclamation with risk-tiered deletions,
  service coordination for Docker cleanup, bloat pattern recognition
  (recursive backups, cache explosions), and verification checks.
  Produces manifests and before/after metrics for audit trail.
input_artifacts:
  - Disk usage reports (`df -h`, `du -sh`)
  - Directory tree listings
  - Docker system inventory (`docker system df`, `docker ps -a`)
  - Agent profile backups (Hermes, other)
  - Cache hierarchies (`/root/.cache`, `/tmp`, npm/yarn caches)
  - Journalctl logs
output_artifacts:
  - Cleanup plan document (`10-Archive/cleanup-manifests/<date>-Spring-Cleaning-Plan.md`)
  - Execution report with before/after metrics (`10-Archive/cleanup-manifests/<date>-Execution-Report.md`)
  - Vaulted manifest for rollback reference
  - Telegram summary message to coordination group
stages:
  - Discover & Audit
  - Categorize by Risk
  - Phase-1 Safe Deletes
  - Phase-2 Cache Cleanup
  - Phase-3 Docker (Coordinated)
  - Phase-4 Archive Compression
  - Verify & Report
practices:
  - "Backup-before-delete: Always generate a text manifest of items targeted for deletion, vault it before execution"
  - "Risk-tier: Category A (safe, no recovery needed) → delete immediately; Category B (conditional) → review with team; Category C (critical) → preserve"
  - "Service coordination: Docker image cleanup requires stopping dependent containers first; never prune active images"
  - "Cache preservation: ML model caches (HuggingFace) and agent state (`.hermes/profiles/`) are NEVER deleted; only re-downloadable caches are purged"
  - "Bloat pattern alerts: Recursive directory copies (nested `.hermes/`, `.git/`, `node_modules/`) are flagged as critical waste — always verify depth >2"
  - "Verification after each phase: Run `df -h`, `du -sh` on target paths, compare vs baseline"
---

## 📋 Skill Body

### When to Invoke
- User complains about disk space ("we're at X GB", "running out of space", "need to free up")
- Proactive maintenance window scheduled
- Post-hackathon/debugging session cleanup (after temporary research artifacts accumulate)
- Before new development sprint (clear working space)

### Core Workflow

#### Stage 1 — Discover & Audit

```bash
# Overall disk health
df -h /

# Top-level directory breakdown (sort by size)
du -xh / --max-depth=1 2>/dev/null | sort -rh | head -20

# Vault-specific size
du -sh /root/vaults/gentech

# Hermes/agent artifacts
du -sh /root/.hermes /usr/local/lib/hermes-agent /tmp/hermes*

# Find large files (>100MB)
find /root/vaults/gentech -type f -size +100M 2>/dev/null | head -20

# Identify recursive backup traps (nested dot-directories)
find /path -type d -name '.hermes' -o -name '.git' -o -name 'node_modules' 2>/dev/null | wc -l
```

**Decision point:** If nested count > 1 for any backup dir → CAREFUL — may be recursive copy disaster.

---

#### Stage 2 — Categorize by Risk

Build a deletion matrix:

| Category | Criteria | Example | Action | Recovery |
|----------|----------|---------|--------|----------|
| **A — Safe** | Zero external references, re-downloadable/built, <br>already vaulted, OR recursive trap | `/tmp/*.html` scrapes, bloated backup with 5x nesting, `npm cache` | DELETE immediately | None needed |
| **B — Conditional** | Possibly in use, but reviewable; <br>old Docker images, cache directories | `browserless/chrome:latest` (2yr old), `/.cache/uv` | TEAM REVIEW → document decision | Re-pull if needed |
| **C — Preserve** | Agent state, ML models, active DBs, <br>volumes with data | `/root/.hermes/profiles/`, `/root/.cache/huggingface`, Docker volumes | DO NOT TOUCH | N/A |

**Rule:** Category A = auto-delete; Category B = manifest + team sign-off; Category C = never delete.

---

#### Stage 3 — Phase-1 Safe Deletes (Zero Risk)

**Targets:**
- Recursive backup traps (identified in Stage 2)
- `/tmp` research artifacts (`*.html`, `*.json`, `*.gif`, `*.mp4`, `*.tar.gz`)
- Corrupted Python bytecode (`find -name '*.pyc' -delete`)
- Journalctl vacuum (`journalctl --vacuum-time=7d`)
- NPM/Yarn cache (if not using nvm, else skip)

**Execution pattern:**
```bash
# Record manifest FIRST
cat > /tmp/cleanup-manifest-YYYY-MM-DD.txt <<'EOF'
[DELETED - Phase 1]
- /path/to/bad/backup (55G) — reason: recursive 5× nesting, zero refs
- /tmp/*.html (120MB) — reason: one-time scrapes, already vaulted
EOF

# Then delete
rm -rf /path/to/bad/backup
rm -f /tmp/*.html /tmp/*.json

# Verify
du -sh /path/to/bad/backup  # should say "No such file"
df -h /
```

**Verification:** Expect 30–60% disk recovery if major bloated backup present.

---

#### Stage 4 — Phase-2 Cache Cleanup (Low Risk)

**Safe caches to purge:**
- `/root/.cache/camoufox` (browser automation)
- `/root/.cache/uv` (Python package cache)
- `/root/.cache/ms-playwright` (browser drivers)
- `/root/.cache/pip` (pip download cache)
- `/root/.npm` (if npm global, not nvm)

**DO NOT TOUCH:**
- `/root/.cache/huggingface` — ML models, expensive to re-download
- `/root/.cache/gh` — trivial, keep
- Any cache inside agent profiles (`.hermes/cache/`) — agent state

**Command:**
```bash
rm -rf /root/.cache/camoufox /root/.cache/uv /root/.cache/ms-playwright
```

**Expected savings:** 2–4GB depending on usage.

---

#### Stage 5 — Phase-3 Docker (Medium Risk — Requires Coordination)

**Pre-requisite:** All Docker-dependent services must be stopped before pruning.

**Discovery:**
```bash
docker system df              # total usage, reclaimable?
docker ps -a                  # what's running?
docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}'
```

**Decision tree:**
- If `docker system df` shows `RECLAIMABLE 0B` → all images in use → can't prune yet
- If images >6 months old → schedule downtime + replace with fresh pulls
- If volumes present → check if data needs backup first (`docker volume ls`, inspect mounts)

**Safe procedure:**
```bash
# 1. Coordinate with team (Desmond/DMOB) — "RSSHub will be down 5 min"
cd /root/workspace/rsshub && docker compose down

# 2. Pull fresh replacements for outdated images
docker pull browserless/chrome:latest   # was 2024, now fresh

# 3. Prune everything unused
docker system prune -a -f

# 4. Restart stack
docker compose up -d

# 5. Verify
docker ps -a
docker system df
```

**Savings:** 4–6GB typical if old browser images present.

---

#### Stage 6 — Phase-4 Archive Compression (Optional)

Old HTML trackers, legacy reports can be gzipped and moved to `10-Archive/`:

```bash
gzip -9 /root/vaults/gentech/03-Strategies/Yield-Farm-Tracker.html
mkdir -p /root/vaults/gentech/10-Archive/compressed-trackers
mv /root/vaults/gentech/03-Strategies/*.html.gz \
   /root/vaults/gentech/10-Archive/compressed-trackers/
```

**Note:** Negligible savings (<100KB) but keeps vault tidy.

---

#### Stage 7 — Verify & Report

**Run full verification suite:**
```bash
df -h /                          # overall disk
du -sh /root/vaults/gentech      # vault integrity
du -sh /root/.hermes             # agent profiles intact?
docker system df                # Docker reclaim
ls -la /root/.cache/huggingface  # models preserved?
```

**Generate execution report:**
- Before/after metrics (disk %, GB freed)
- What was deleted (with sizes)
- What was preserved (and why)
- What's deferred (Docker, team coordination)
- Follow-up tasks (schedule next cleanup)

**Distribution:**
- Vault: `10-Archive/cleanup-manifests/<date>-Execution-Report.md`
- Telegram: Brief summary to coordination group
- Email/Slack: If team uses external comms

---

## 🚨 Bloat Patterns — Recognition Guide

### Pattern 1: Recursive Backup Trap
**Symptoms:**
- Single backup directory appears huge (`du -sh` shows 40G+)
- `find . -name '.hermes'` returns >1 result in that tree
- Path contains `profiles/dmob/home/.hermes/profiles/dmob/home/.hermes/...`

**Root cause:** Backup script copied entire `$HOME` recursively without excluding dot-directories, then that copy got backed up again, etc.

**Action:** Verify no symlinks/references exist (`grep -r 'path' /root/workspace`), then DELETE entire recursive tree. Active profiles live in `/root/.hermes/profiles/` — don't need nested copies.

---

### Pattern 2: Cache Explosion
**Symptoms:**
- `/root/.cache` > 2GB
- Multiple language caches present (pip, uv, npm, playwright, huggingface)
- Old project artifacts mixed with active caches

**Action:** Identify re-downloadable vs precious. Purge re-downloadable, preserve ML models and agent-specific caches.

---

### Pattern 3: Docker Image Graveyard
**Symptoms:**
- `docker images` shows many `<none>:<none>` dangling images
- Old images with months-old timestamps still present
- `docker system df` shows high `SIZE` but `RECLAIMABLE 0B`

**Action:** Stop containers, prune unused layers, pull fresh base images.

---

### Pattern 4: Research Artifact Accumulation
**Symptoms:**
- `/tmp` or `~/Downloads` filled with `*.html`, `*.json`, `*.pdf` from one-off browsing
- Filenames like `ethglobal_full.html`, `cantina_rendered.html`, `x402_open_prs.json`
- Files older than 7 days with no read/modify activity

**Action:** Check vault first — if data already extracted/processed, delete originals.

---

### Pattern 5: Bytecode Cache Corruption
**Symptoms:**
- Python errors: `EOFError: marshal data too short` in `__pycache__/`
- Multiple `.pyc` files reported as corrupt in logs
- Python version upgrades without cache purge

**Action:** `find /path -name '*.pyc' -delete` — Python will regenerate on next import.

---

## 🔧 Tooling

### Scripts (now implemented)

**`scripts/audit-disk.sh`** — Quick disk health check, outputs JSON + human-readable summary
```bash
cd /root/.hermes/profiles/yoyo/skills/devops/system-cleanup
./scripts/audit-disk.sh
# Returns: {"disk_usage_percent":25,"vault_size":"2.1G","nested_hermes_traps":0,...}
```

**`scripts/find-recursive-traps.sh`** — Detect nested backup traps
```bash
./scripts/find-recursive-traps.sh /root/vaults/gentech/10-Archive
# Output: ⚠️  TRAP DETECTED: /path (55G) — nested count: 5
```

*Usage:* Call directly from terminal or integrate into Hermes cron for proactive monitoring.

---

## 📊 Success Metrics

- **Disk usage:** Target <70% after cleanup; ideal 40–50%
- **Recovered space:** Document GB freed per phase
- **Zero data loss:** Active vault, agent profiles, Docker volumes all intact post-cleanup
- **No service disruption:** Unless coordinated (Docker phase with team approval)
- **Repeatability:** Same process can run quarterly without manual re-discovery

---

## 🆘 When Things Go Wrong

**Situation:** Deleted something important
**Recovery:** 
- Check if it was Category A (no recovery) vs Category B (should have had backup)
- Restore from vault if manifest included vaulted copy
- Re-clone from GitHub if code
- Re-download if cache (with bandwidth cost)

**Situation:** Docker cleanup broke RSSHub
**Recovery:**
- `docker compose up -d` will pull missing images automatically
- If volume data lost: `docker volume ls` → inspect → restore from backup if existed
- Always snapshot volumes before prune if uncertain: `docker run --rm -v volume_name:/data -v /backup:/backup alpine tar czf /backup/volume_backup.tar.gz /data`

---

## 🧭 Related Skills

- `devops/docker-cleanup` — Docker-specific image/volume management (more detailed)
- `devops/log-rotation` — Journalctl, application log lifecycle
- `hermes/hermes-agent-health-check` — Agent profile maintenance (related but distinct)

---

## 📌 Quick Reference Card

```
SYSTEM CLEANUP CHEATSHEET

Phase 1 (safe):              Phase 2 (cache):            Phase 3 (Docker):
  rm -rf /path/to/trap         rm -rf /root/.cache/*       docker compose down
  rm -f /tmp/*.{html,json}     (keep huggingface)          docker system prune -a
  find -name '*.pyc' -delete                              docker compose up -d
  journalctl --vacuum-time=7d

Verify each phase:
  df -h /                      du -sh /root/.hermes       docker ps -a
  du -sh /root/vaults          du -sh /root/.cache        docker system df

Manifest template:
  [DELETED - Phase X]
  - /path (SIZE) — REASON
  - /path2 (SIZE) — REASON
  References: vaulted? rebuildable?
```

---

*Class-level skill — reusable across any Gentech system under disk pressure*
