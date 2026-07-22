# Weekly Skills Update — Sunday Review
**Date:** May 24, 2026 (W21)
**Scan Period:** May 10–24, 2026 (599 commits behind upstream)

---

## ⚠️ CRITICAL: Hermes is 599 Commits Behind Upstream

**341 fixes, 73 new features, 89 security-related commits since our version.**

### 🔴 Security Hardening (16 security-specific commits)
These are P0 — update should be prioritized:
- **Prompt injection protection** — control-plane files now guarded against injection attacks
- **Webhook HMAC bypass fix** — empty-secret HMAC bypass patched (CVE-class)
- **Gateway pairing codes** — now hashed instead of plaintext storage
- **Nous Portal URL allowlist** — validates inference_base_url against host allowlist
- **Dashboard websocket restriction** — loopback-only for security
- **API server key placeholder hardening** — prevents accidental key leakage
- **Webhook toolset restriction** — default capabilities tightened
- **Discord role allowlist auth bypass** — removed
- **Skills guard verdict logic** — corrected + --force limitation enforced
- **File safety** — .env, mcp-tokens/, webhook secrets now read-deny protected
- **Nous control-plane** — refresh/mint persistence sites now validated

### 🟡 Notable New Features (73 total)
- **Bitwarden Secrets Manager integration** — lazy bws install, EU Cloud + self-hosted support, credential labeling by source
- **ntfy platform adapter** — new messaging platform, 81 tests, atomic reconnect
- **Nous Portal one-shot setup** — CLI setup + status, Nous-included markers
- **Kanban bulk promote** — --ids flag for batch operations, manual todo→ready recovery
- **xAI model migration** — `hermes migrate xai [--apply]` detects retired models (May 15, 2026 sunset)
- **Plugin auxiliary task registration** — `register_auxiliary_task()` in PluginContext API
- **Skill AST deep diagnostics** — opt-in AST analysis for skill validation
- **TUI responsive banners** — tier-based display
- **Telegram status message editing** — in-place updates instead of appending
- **Session JSON snapshot writer** — opt-in per-session snapshots
- **Vision support declaration** — `supports_vision` via user config
- **CI 6-way matrix slicing** — performance-optimized test distribution

### 🟢 Hub Skill Changes
- **61 new skills** in hub that aren't locally installed (mostly creative/data-science/niche)
- **baoyu-article-illustrator** — new skill for article illustration
- **baoyu-infographic** + **baoyu-comic** — new creative skills
- **HeyGen skills** — avatar creation + video production (bundled, not in main skills/)
- **Kanban worker updates** — notification routing, scratch workspace warnings
- **Skills guard** — new verdict logic + --force enforcement

### Local Skills Inventory
- **90 local skills** (includes .archive/ and gentech custom)
- **87 hub skills** in repo
- **~20 archived skills** in `.archive/` — candidates for cleanup
- **Custom gentech skills** — all operational, no conflicts detected

---

## Recommended Actions

1. **URGENT: Run `hermes update`** — 599 commits behind, 16 security fixes. This is the highest priority action.
2. **After update: `hermes skills update`** — sync hub skills
3. **Clean `.archive/` skills** — 20 archived skills eating disk, not used
4. **Evaluate new features** — Bitwarden secrets, ntfy platform, and xAI migration are immediately useful
5. **Kanban updates** — bulk promote + corruption defense improvements are worth having

---

## Impact Assessment

- **Security:** HIGH — multiple CVE-class vulnerabilities patched
- **Stability:** MEDIUM — 341 bug fixes, many edge cases resolved
- **Features:** MEDIUM — most new features are niche, but Bitwarden + xAI migration are broadly useful
- **Risk:** LOW — updates are incremental, no breaking changes flagged
- **Recommendation:** Update during next maintenance window (Saturday morning ideal)
