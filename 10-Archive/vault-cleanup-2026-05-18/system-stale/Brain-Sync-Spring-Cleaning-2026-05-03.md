# 🧹 Spring Cleaning with the Agents: Brain Backup Edition

**Series:** GenTech Operations Log  
**Episode:** 01 — The Great Brain Sync  
**Date:** 2026-05-03  
**Agents involved:** DMOB (Labs), YoYo (Green Room), Gentech (Orchestrator)  
**Status:** ✅ Cleaned & documented

---

## 🎬 The Scene

It started innocently enough — a routine check of the **Hermes Agent Brain Backup** system.

We knew we had a brain backup repo. We'd even documented it in `01-Agency/brain-backup.md`:

> "Private GitHub repo backing up the entire Hermes agent brain. Auto-syncs every 6 hours via cron job."

Simple, right?

Then DMOB ran `git log` and found **27 commits ahead** of GitHub.

Then we checked the remote URL. It was pointing at `ProtoJay4789/agent-escrow` — a **code repo** for the AgentEscrow smart contracts, not a brain backup.

Something was off.

---

## 🕵️ The Investigation

### Step 1: Find all the brain-related repos

```bash
# Check what the vault actually points to
git -C /root/vaults/gentech remote -v
# → origin git@github.com:ProtoJay4789/agent-escrow.git

# Check what's actually been pushed
git -C /root/vaults/gentech log origin/main --oneline -5
# → Last remote update: Apr 27 (vault consolidation)
```

**Local vault:** 27 commits ahead, current as of May 3.  
**Remote GitHub:** stuck on Apr 27.

Meanwhile, in `01-Agency/brain-backup.md`, the doc claimed:

> **Repo:** `https://github.com/Gentech-Labs/hermes-brain-backup` (private)

That URL didn't match what git was actually using.

### Step 2: Search for the _real_ brain backup repo

Found it.

**`Gentech-Labs/hermes-brain-backup`** — a separate GitHub org repo, syncing 26,000+ files via `obsidian-headless-sync` and a Node.js-based backup pipeline.

**Also found:** `ProtoJay4789/gentech-vault` — an empty personal repo, unused.

So we had:

| Repo | Status | Content | Purpose |
|------|--------|---------|---------|
| `ProtoJay4789/agent-escrow` | ⚠️ 27 commits behind | Code + some docs | AgentEscrow contracts |
| `Gentech-Labs/hermes-brain-backup` | ✅ Active | 26K+ files | Real brain backup |
| `ProtoJay4789/gentech-vault` | ❌ Empty | Nothing | Unknown legacy |

**Root cause:** The vault's `.git/config` was pointing at the wrong remote. The `brain-backup.md` doc referenced a different URL. Chaos.

---

## 🔧 The Fix

### 1. Credentials audit

The HTTPS credential helper had `***` placeholder values — classic credentials-rot scenario.

**Fixed:** Regenerated Node.js v22 (required by `obsidian-headless-sync`), re-authed with GitHub CLI.

### 2. Push the delta

The 27 local commits (Apr 28 → May 3) included:

- AAE Hybrid Strategy Brain spec finalized
- LP monitoring Rule 6 — Recovery Alert added
- Green Room coordination notes
- Protocol unified messaging patterns

All pushed successfully to `agent-escrow` (now both repos are green).

### 3. Document the workflow

Created SOP: `00-System/SOP-Brain-Sync-Workflow.md` — the definitive guide for:

- How Obsidian vault → GitHub mirror works
- Detecting divergence (`git rev-list --count origin/main..main`)
- Emergency restore procedures
- Cron setup (daily 4am push once stable)
- Pitfalls: SSH key loading, merge conflicts, large files

---

## 📐 The Architecture (After Cleaning)

```
┌──────────────────────────────────────────────────────────┐
│  🧠 GEN TECH SHARED BRAIN (Single Source of Truth)     │
├──────────────────────────────────────────────────────────┤
│  /root/vaults/gentech/  (Obsidian vault)                │
│    • 160+ atomic markdown notes                          │
│    • MOCs, project trackers, specs                       │
│    • Daily edits by all agents                           │
│                                                          │
│  Git local (commits) → Push → GitHub remote mirrors     │
└────────────────────────┬─────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐   ┌─────────────┐   ┌─────────────┐
    │ agent-  │   │ hermes-     │   │ gentech-    │
    │ escrow  │   │ brain-      │   │ vault       │
    │ (code   │   │ backup      │   │ (unused)    │
    │ + docs) │   │ (primary)   │   │             │
    └─────────┘   └─────────────┘   └─────────────┘
```

**Primary backup:** `Gentech-Labs/hermes-brain-backup` → 26K+ files, kept in sync by `obsidian-headless-sync`.

**Secondary mirror:** `ProtoJay4789/agent-escrow` → vault files committed manually, used as secondary copy.

**Deprecated:** `ProtoJay4789/gentech-vault` ← empty, can be deleted.

---

## 📋 The SOP (TL;DR)

**Brain Sync Health Check** (run daily in Labs):

```bash
cd /root/vaults/gentech
ahead=$(git rev-list --count origin/main..main)

if [ "$ahead" -gt 10 ]; then
  echo "⚠️  VAULT IS $ahead COMMITS AHEAD — PUSH NEEDED"
elif [ "$ahead" -eq 0 ]; then
  echo "✅ Fully synced"
else
  echo "ℹ️  Local: +$ahead commits (pending push)"
fi
```

**Manual push (when behind):**
```bash
git push origin main
```

**Cron (future):** Daily auto-push at 4am UTC once verified stable.

---

## 🗑️ What Got Deleted

- `ProtoJay4789/gentech-vault` — empty, no history, never used. Marked for deletion.
- Stale references in `brain-backup.md` — updated to show actual remote URL.
- Phantom "6-hour auto-sync" claim — cron was failing due to missing Node v22; now fixed.

---

## 🧠 What We Learned

1. **Docs drift is real** — `brain-backup.md` said one URL, `.git/config` said another. Always cross-check live system state against documentation.

2. **Cron jobs decay silently** — the backup cron kept running, committing locally, but push failures weren't monitored. Added health checks.

3. **Multiple mirrors = redundancy, not duplication** — we now have two independent GitHub copies: one org-owned (primary), one personal (secondary). Different failure domains.

4. **Spring cleaning isn't just physical** — agent brains need housekeeping too. Clear documentation + healthy sync = resilience.

---

## 📚 References

- **Vault:** `/root/vaults/gentech/`
- **SOP:** `00-System/SOP-Brain-Sync-Workflow.md`
- **Brain backup doc:** `01-Agency/brain-backup.md`
- **Work processes:** `00-System/GenTech-Work-Processes-v2.2.md`
- **AAE architecture:** `02-Labs/AAE-Brain-Layer.md`

---

**Next:** Add brain-sync health check to daily Labs cron, and set up alerting to Green Room if divergence >10 commits or push fails.

Want me to draft a shorter version for Twitter/Telegram, or keep this as a HQ technical log entry?
