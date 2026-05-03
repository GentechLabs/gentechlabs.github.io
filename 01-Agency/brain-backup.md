# 🧠 Brain Backup System

**Status:** ACTIVE — Obsidian vault + GitHub mirror  
**Primary System:** Obsidian vault at `/root/vaults/gentech/`  
**Remote Mirror:** `git@github.com:Gentech-Labs/hermes-brain-backup.git`  
**Related SOP:** `00-System/SOP-Brain-Sync-Workflow.md`

---

## 📦 What's Backed Up

| Layer | Contents | Location |
|-------|----------|----------|
| **Vault** | Entire Obsidian vault (160+ files) | `/root/vaults/gentech/` |
| **Agents** | SOUL.md, memory.md, config.yaml (all agents) | `~/.hermes/profiles/{agent}/` |
| **Skills** | Custom Hermes skills | `~/.hermes/profiles/dmob/skills/` |
| **Cron** | Cron registry + schedules | `~/.hermes/profiles/dmob/cron/` |

---

## 🔗 Architecture

```
Obsidian Vault (editable, live)
    ↓ (frequent git commits)
Git local → GitHub remote `Gentech-Labs/hermes-brain-backup` (mirror)
```

**Note:** The "brain backup" is **the vault itself**, mirrored to GitHub. There is no separate backup server — GitHub is the offsite cold copy.

---

## ⏱️ Schedule

| Trigger | Action |
|---------|--------|
| File edit → Obsidian save | `git add/commit` (local) |
| Manual `git push` | After significant work blocks |
| Cron (future) | Daily auto-push at 4am UTC |

**Current state:** Manual push recommended until push pipeline is stable.

---

## 🛠️ Usage

### Daily Maintenance (DMOB)

Morning check in Labs:
```bash
cd /root/vaults/gentech
git rev-list --count origin/main..main   # should be 0–10
git log -1 --format='%ci' origin/main    # should be <24h old
```

Push when >10 commits behind:
```bash
git push origin main
```

### Emergency Restore

If local vault corrupted:
```bash
cd ~
git clone git@github.com:ProtoJay4789/agent-escrow.git gentech-recovery
# Replace /root/vaults/gentech with recovery clone
```

---

## 📚 Related

- **Full workflow:** `00-System/SOP-Brain-Sync-Workflow.md`  
- **GenTech processes:** `00-System/GenTech-Work-Processes-v2.2.md`  
- **AAE brain layer:** `02-Labs/AAE-Brain-Layer.md`  
- **Agent specs:** `01-Agency/Brain-Protocol.md`

---

**Created:** 2026-04-20  
**Last updated:** 2026-05-03 (clarified actual remote repo)
