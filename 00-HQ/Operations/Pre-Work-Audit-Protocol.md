# Pre-Work Audit Protocol

**Status:** Standing directive from Jordan (2026-05-05)
**Applies to:** All agents — YoYo, DMOB, Desmond, Gentech

---

## Rule

Before starting ANY work on ANY project, always do a clean audit of what exists:

1. **Check GitHub** — latest commits, branches, uncommitted work, untracked files
2. **Check Obsidian vault** — search for prior work, notes, handoffs, decisions
3. **Synthesize** — gap analysis before building

Never assume fresh start. Never duplicate work.

---

## Quick Commands

### GitHub
```bash
git -C /path/to/repo log --oneline -10
git -C /path/to/repo status
git -C /path/to/repo diff --stat
```

### Vault
```bash
rg "PROJECT_NAME" /root/vaults/gentech/ --md -l | head -20
rg "PROJECT_NAME" /root/vaults/gentech/09-Green Room/ --md -l
```

---

*This is now agent behavior. Every session. No exceptions.*
