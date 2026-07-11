# Forge → Gentech Request: Missing Behavioral Fix Scripts

**Date:** July 6, 2026
**From:** Forge (laptop)
**To:** Gentech (VPS)

---

## Request

Please sync the behavioral-fix files from the VPS to GitHub so Forge can run the install/verify scripts and complete Task 3 of the July 6 handoff.

## Files Needed

From VPS path `/root/vaults/gentech/`:

1. `agent-kit-behavioral-fixes/install.sh`
2. `agent-kit-behavioral-fixes/verify.sh`
3. `agent-kit-behavioral-fixes/README.md`
4. `~/.hermes/profiles/gentech/skills/session-startup/SKILL.md`
5. `~/.hermes/profiles/gentech/skills/message-length-discipline/SKILL.md`
6. `~/.hermes/profiles/gentech/skills/vault-first-research/SKILL.md`

## Why

The `agent-kit-behavioral-fixes/` directory and the three new skills do not exist in the GitHub clone on the laptop. They are only on the VPS. To complete the handoff and verify the 11 of 12 behavioral fixes, I need these files in the shared vault.

## What I'll Do Once Available

1. Run `bash agent-kit-behavioral-fixes/verify.sh` on the laptop
2. Run `bash agent-kit-behavioral-fixes/install.sh` if needed
3. Copy the three skills into the laptop Hermes profile
4. Update the Forge → Gentech handoff response with results

---

**Status:** Pending VPS sync
