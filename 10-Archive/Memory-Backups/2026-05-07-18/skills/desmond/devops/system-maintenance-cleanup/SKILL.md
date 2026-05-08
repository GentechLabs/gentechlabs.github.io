---
name: system-maintenance-cleanup
description: Audit disk usage, identify bloat, and execute safe cleanup across Hermes workspace
triggers:
  - "spring cleaning"
  - "disk cleanup"
  - "bloat"
  - "running out of space"
  - "gig usage"
  - "clear cache"
  - "prune"
  - "disk >70%"
priority: 2
enabled: true
---

# System Maintenance & Cleanup — Gentech

**Purpose:** Audit system disk usage, identify bloat, and execute safe cleanup operations across Hermes workspace. Used for spring cleaning, space reclamation, and routine maintenance.

**Triggers:**
- User mentions: "spring cleaning", "disk cleanup", "bloat", "running out of space", "gig usage", "clear cache", "prune"
- Disk usage exceeds 70% threshold
- Regular interval (monthly) maintenance recommended

**Prerequisites:**
- Terminal access with sudo/root privileges
- Familiarity with vault structure (`/root/vaults/gentech/`)
- Hermes agent running as root user

---

## Procedure

### Phase 1 — System-Wide Audit

1. **Check overall disk health**
   ```bash
   df -h /
   ```

2. **Scan top-level directories** (sort by size descending)
   ```bash
   du -sh /root/* 2>/dev/null | sort -rh
   ```

3. **Drill into key workspaces**
   - `/root/workspace/` — active project code
   - `/root/vaults/` — Gentech vault content
   - `/root/.hermes/` — agent profiles, skills, checkpoints
   - `/root/projects/`, `/root/repos/` — additional codebases

4. **Hunt common bloat patterns** (run each):
   ```bash
   # Rust build artifacts
   find /root -name 'target' -type d 2>/dev/null

   # Node.js package cache
   du -sh ~/.npm ~/.cache/node* 2>/dev/null

   # Python package cache
   du -sh ~/.cache/pip ~/.cache/uv 2>/dev/null

   # Docker images/containers
   docker system df 2>/dev/null || echo 'Docker not running'

   # Hermes logs and checkpoints
   du -sh ~/.hermes/logs ~/.hermes/profiles/*/logs ~/.hermes/checkpoints 2>/dev/null
   ```

5. **Vault health check** — ensure only intended content in vaults
   ```bash
   du -sh /root/vaults/gentech/* | sort -rh
   ```

### Phase 2 — Cleanup Planning

Create a table of findings:

| Source | Size | Action | Notes |
|--------|------|--------|-------|
| Rust `target/` dirs | estimated | DELETE | Rebuild on demand |
| NPM cache | measured | CLEAN | `npm cache clean --force` |
| UV/Pip cache | measured | CLEAN | `rm -rf ~/.cache/uv ~/.cache/pip` |
| Docker images | measured | PRUNE | `docker system prune -a -f` |
| Hermes logs (>30d) | measured | ARCHIVE or DELETE | Check dates first |

**Expected savings:** Sum of measured bloat sources.

### Phase 2.5 — Necessity Verification for Build Artifacts

Before any deletion, classify each bloat candidate to avoid removing active hackathon work or running services.

**For Rust `target/` directories:**
- Check parent project for uncommitted changes: `git -C <project> status --short`. If any output → **KEEP** (flag as preserve).
- Look for hackathon indicators: DEMO_SCRIPT.md, DEMO_STORYBOARD.md, or README containing "submission", "demo", "hackathon". Found? → **KEEP**, confirm with owner.
- Check modification time: `stat -c '%y' <target_dir>`. If modified in last 7 days, treat as active → **VERIFY** with DMOB.
- If multiple similar codebases exist (e.g., `agent-starter-pack/colosseum-frontier` vs `projects/colosseum-frontier`), determine the submission version by checking vault docs (`02-Labs/Hackathons/Active/`) and Green Room handoffs. Do not delete any until confirmed.

**For Docker images:**
- Identify running containers: `docker ps --format "{{.Image}}\\t{{.Names}}"`. If image is in use by a running container → **KEEP**.
- Check if service is documented in vault as required (e.g., RSSHub for fee tracking). Search vault for the image name. If referenced → **VERIFY** with owner.
- If image is >1GB and not used by any running container, it's a candidate for pruning, but still ask user before aggressive `-a` prune.

**Document findings** in the cleanup table with column "Verification" status: `VERIFIED_SAFE`, `PRESERVE`, or `NEEDS_CONFIRMATION`.

### Phase 3 — Execution (User Confirmation Required)

**Conservative approach** (recommended first run):
- Clear caches only (`npm`, `pip`, `uv`)
- Remove expired logs (>30 days)
- Prune Docker stopped containers & dangling images

**Aggressive approach** (user-approved, after verification):
- Delete only `target/` directories marked `VERIFIED_SAFE`
- Prune unused Docker images (`-a` flag) only after confirming none are needed by running services
- Clear entire Hermes profile caches
- Tar old vault archives to cold storage

**Safety notes:**
- Rust `target/` deletion requires recompilation of affected projects
- Docker `-a` prune removes ALL unused images (not just dangling)
- Never delete vault content without explicit user approval
- Preserve any directory with uncommitted changes, demo files, or active hackathon status — these require owner confirmation even if space is tight

### Phase 4 — Verification

Re-run `df -h /` and compare to baseline. Confirm expected savings achieved.

---

## Pitfalls

- **False positives:** Some `target/` dirs may be under active compilation. Check `lsof +D <dir>` before deletion if uncertain.
- **Docker reclaimable 0B:** Docker may report 0B reclaimable if all images are referenced by containers. Stop containers first (`docker stop $(docker ps -q)`) or use `--volumes` flag.
- **Hermes profile bloat:** Profile checkpoints and model caches can be large. Do not delete `profiles/*/home/` directories wholesale — inspect subfolders.
- **Vault confusion:** Vaults are intentionally lean; 10-Archive can grow large by design. Never auto-delete from vaults.
- **npm cache clean:** Use `--force`; otherwise npm refuses to clean if packages are still referenced.

- **Active hackathon bloat:** Do not assume `target/` directories are reclaimable during active hackathons. They may contain compiled binaries for demo recordings. Always check for DEMO_SCRIPT.md or README with "submission"/"hackathon" keywords first. When uncertain, ask in Green Room.

- **Docker services in use:** A running container doesn't mean its image is safe to prune — other containers may restart from it. Check both `docker ps` and vault service documentation before any Docker cleanup. Treat documented services (e.g., RSSHub) as essential until confirmed otherwise.

---

## References

- `references/rust-cargo-cache-locations.md` — where Cargo stores registry + target builds
- `references/docker-prune-flags.md` — safe Docker cleanup flags and what they remove
- `references/hermes-profile-layout.md` — Hermes agent profile directory structure
- `references/vault-conventions.md` — what belongs in each vault folder
- `references/hackathon-artifact-verification.md` — checklist to identify active hackathon artifacts vs reclaimable bloat

---

## Scripts

- `scripts/disk-audit.sh` — full audit pipeline (Phases 1–2) with JSON output
- `scripts/bloat-estimator.py` — aggregate bloat sizes across common patterns
- `scripts/vault-health-check.sh` — vault-only health check (no system scan)
