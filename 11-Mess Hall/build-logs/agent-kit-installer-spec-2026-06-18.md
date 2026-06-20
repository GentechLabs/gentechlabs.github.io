# Build Log: Agent Kit Installer Spec

> **Date:** 2026-06-18
> **Task:** Write comprehensive spec for GenTech Agent Kit Installer
> **Status:** ✅ Complete

---

## What Was Done

### 1. Repository Check
- `/root/repos/genTech-agent-kit/` does **not exist** locally
- Similar repos found: gentech-agents, gentech-hub, gentech-labs, gentech-music, gentech-pals
- Spec references `github.com/ProtoJay4789/genTech-agent-kit` as the canonical source

### 2. Ideas.md Review
- Read full ideas.md (155 lines) from `/root/vaults/gentech/09-Green Room/ideas.md`
- Agent Kit Installer entry at line 21-37:
  - Source: Jordan voice message
  - Priority: High
  - Status: "Concept — needs spec"
  - 7 layers identified: Hermes install, skills+crons, wallet wizard, DeFi dashboard, GitHub backup, skill marketplace, health dashboard
- Key quote: "Makes the Agent Kit distributable. Hard to copy because it's tied to local Hermes setup."

### 3. Spec Written
**File:** `/root/vaults/gentech/09-Green Room/ideas/agent-kit-installer-spec.md` (16,213 bytes)

Covers:
- **14 sections** — Vision, Components, Platform Support, Prerequisites, Installation Flow, Config Wizard, Post-Install Verification, CLI MVP (full bash script), GUI Phase 2, Directory Structure, Uninstall, Update, Success Metrics, Open Questions
- **Full install.sh bash script** — ~150 lines, ready to prototype with curl-pipe-bash workflow
- **Component inventory** — All installable pieces cataloged (Hermes, 112 skills, 22 crons, 5 dashboards, wallet, AAE stack)
- **Platform matrix** — Phase 1: Linux/macOS/WSL; Phase 2: Native Tauri apps
- **Non-interactive mode** — Flags for CI/automation use
- **Verification system** — Post-install report generation

### 4. Build Log Written
**File:** `/root/vaults/gentech/09-Green Room/build-logs/agent-kit-installer-spec-2026-06-18.md`

---

## Open Questions Surfaced
1. Hermes distribution method (PyPI vs git install)
2. Skill licensing for paid API dependencies
3. Wallet security/seed phrase handling
4. Auto-update mechanism
5. Branding assets needed for GUI

---

## Next Steps
- [ ] Verify hermes-agent installation method (PyPI? pipx? git?)
- [ ] Create skeleton `genTech-agent-kit` repo on GitHub
- [ ] Prototype `install.sh` end-to-end on a fresh Linux box
- [ ] Design Tauri GUI wireframes for Phase 2
- [ ] Test install on macOS (Homebrew detection)
- [ ] Test install on WSL2

---

## Files Created
| File | Size | Purpose |
|---|---|---|
| `09-Green Room/ideas/agent-kit-installer-spec.md` | 16,213 bytes | Full specification |
| `09-Green Room/build-logs/agent-kit-installer-spec-2026-06-18.md` | This file | Build log |
