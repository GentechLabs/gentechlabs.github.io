---
status: sweep-complete
date: 2026-05-13
next-sweep: 2026-05-14
---

# Vault Sweep Report — 2026-05-13 11 PM ET

## Summary
Vault is healthy but bloated. One significant issue requires attention; the rest is informational.

---

## ⚠️ Issue: Build Artifact Bloat (Action Needed)

**Path:** `02-Labs/voice-agent/piper/source/build/`
**Size:** 315.5 MB across 6,640 files
**Content:** Third-party build dependencies (onnxruntime, espeak_ng, fmt) — NOT vault content.

These are vendored C++ build artifacts from the Piper TTS project. They inflate the vault from ~4.5 GB to 4.8 GB. The `.gitignore` does NOT cover this path.

**Recommended actions:**
1. Add `02-Labs/voice-agent/piper/source/build/` to `.gitignore`
2. Consider deleting the build dir entirely if voice-agent isn't actively developed
3. Or move it to a standalone repo outside the vault

---

## 📁 Green Room — 2 Misplaced Files

Two Solidity contracts are sitting in the ideas folder:
- `GenLayerOracleResolver.sol`
- `IResolver.sol`

These belong in `02-Labs/` under a GenLayer project folder, not in the Green Room ideas area. Recommend moving them.

---

## 📊 Vault Stats

| Metric | Value |
|--------|-------|
| Total files | 103,496 |
| Total size | 4,823.8 MB |
| Markdown files | 41,459 |
| Stale files (>7 days) | 17,473 |
| Fresh files (<7 days) | 23,986 |
| Build artifacts | 6,640 (315.5 MB) |

---

## 🗂️ Folder Status

### Mess Hall (`11-Mess Hall/`)
- 4 files, all current (0-5 days old)
- No orphaned or stale items
- Status: ✅ Clean

### Green Room (`09-Green Room/`)
- 8 files, all current (0-5 days old)
- 2 misplaced .sol files flagged above
- Status: ⚠️ Minor cleanup needed

### Kanban
- `Labs.md` and `hackathon-pipeline.md` — both 2 days old
- Status: ✅ Active

### Active Project Docs
- **03-Strategies/**: 100+ files, all 5 days old (last sync May 8). No new activity.
- **02-Labs/**: 100+ files, mix of 0-5 days old. Active.
- **03-Projects/**: 1 file (`local-hermes-gpu-setup.md`), 5 days old.
- Status: ✅ Normal — Strategies may benefit from a review to archive completed work

### Archives
- **10-Archive/**: 3 files
- **12-Archive/**: 0 files (empty)
- Status: ℹ️ Archives are underutilized. Completed work in Strategies/Labs could be archived.

### 00-HQ
- 15 files, 0-5 days old. Active and current.
- Status: ✅ Clean

### 00-System
- 13 files, mostly 5 days old. Standard config files.
- Status: ✅ Clean

---

## 🔧 Sync Status

`ob sync` is **not configured** for this vault. Run `ob sync-setup` to enable Obsidian sync.

---

## Items Flagged for Jordan's Attention

1. **Build artifact bloat** — 315 MB of C++ build deps in `02-Labs/voice-agent/piper/source/build/`. Add to `.gitignore` or remove.
2. **Misplaced .sol files** — `GenLayerOracleResolver.sol` and `IResolver.sol` in Green Room should move to Labs.
3. **ob sync not configured** — Run `ob sync-setup` if vault sync is desired.
