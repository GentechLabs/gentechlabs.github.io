# Skill & System Update Analysis — 2026-04-28

## Executive Summary

**Hermes Agent Core**: 5 commits behind upstream — **Low priority, update when convenient**
**Skills**: 944 installed, no broken dependencies detected
**Cron Job Issue**: `Skills GitHub Update Check` references non-existent script — needs fix

---

## Hermes Agent Core Update

**Current**: v0.11.0 (2026.4.23)
**Pending**: 5 commits behind `origin/main`

### Pending Commits (all low-risk)

| Commit | Description | Risk | Files Changed |
|--------|-------------|------|---------------|
| `e0e67a99` | TUI: copilot follow-up review on text selection PR | Low | 2 files, 5 lines |
| `e7091bb3` | TUI: mouse + keyboard text selection in composer | Low | 7 files, 341 lines |
| `bebc1052` | Merge: Docker multi-profile docs | None | Merge commit |
| `273be934` | Docs: restore redacted placeholder strings | None | 1 file |
| `adc2856f` | Docs: add "Multi-profile support" section | None | 1 file |

**Verdict**: All TUI improvements + docs. Zero breaking changes. Safe to update anytime.

**Command**: `hermes update`

---

## Skills Inventory

- **Total**: 944 enabled, 0 disabled
- **Builtin**: 68 (shipped with hermes-agent)
- **Local**: 876 (custom/Gentech-specific)
- **Hub-installed**: 0

### No Broken Skills Detected
- All skills show `enabled` status
- No hub dependencies to sync
- Local skills are self-contained

---

## Issues Found

### 1. Broken Cron Job: `Skills GitHub Update Check`
- **Job ID**: `2d7cb521c8df`
- **Problem**: References `cron/skills-update-github-check.sh` which doesn't exist
- **Impact**: Job will fail on every run (hasn't run yet — `last_run_at: null`)
- **Fix Options**:
  - A) Create the missing script
  - B) Remove the `script` reference from the cron job
  - C) Disable the cron job until the script is built

### 2. No User Skills Directory
- `~/.hermes/profiles/yoyo/skills/` doesn't exist
- All custom skills live in the system-level skills directory
- Not a problem, but means YoYo can't create agent-specific skill overrides

---

## Recommendations

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| **1** | Fix broken cron job `2d7cb521c8df` | 5 min | Prevents silent failures |
| **2** | Run `hermes update` | 2 min | Gets TUI improvements |
| **3** | Create `~/.hermes/profiles/yoyo/skills/` dir | 1 min | Enables skill customization |
| **4** | Build `skills-update-github-check.sh` script | 30 min | Enables weekly skill auditing |

---

## Assumptions
- Upstream commits are tested before merge (NousResearch repo)
- Local skills don't have external dependencies that need syncing
- The 876 local skills are stable and don't require frequent updates

## Risk Assessment
- **Update risk**: Low — all pending changes are UI/docs
- **Skills risk**: Low — no hub dependencies, all local
- **Cron risk**: Medium — broken script means missed audit opportunities
