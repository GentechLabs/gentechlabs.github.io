# Forge Sync Protocol

## How this works

Three files. One loop. No missed messages.

```
Gentech writes → 01-HANDOFFS/for-the-forge.md   (tasks for Forge — ROOT vault, can be stale)
                 gentech-vault-new/01-HANDOFFS/gentech-to-forge/  (tasks — GIT vault, FRESH)
Forge writes   → 01-HANDOFFS/from-the-forge.md   (what Forge did — ROOT vault)
                 gentech-vault-new/01-HANDOFFS/forge-completions.md  (GIT vault)
Gentech reads  ← 01-HANDOFFS/from-the-forge.md   (picks up completions)
```

## ⚠️ Critical: Two Vaults

There are TWO vault locations that can contain handoffs. ALWAYS check both:

| Location | Path | How Gentech writes |
|----------|------|-------------------|
| **Root vault** | `GenTech_Agency/01-HANDOFFS/` | Direct Obsidian vault writes |
| **Git vault** | `gentech-vault-new/01-HANDOFFS/` | GitHub push from VPS |

**Forge must:** Before starting work, `cd gentech-vault-new && git fetch && git merge --ff-only origin/main` to get the latest Gentech handoffs. The git vault is the authoritative source for current tasks.

## For Forge — template for "from-the-forge.md"

Copy and paste this at the start of each session:

```
## From Forge — <date>

### ✅ Completed this session
- [item] — brief what was done

### ⏸ Blocked / waiting on
- [item] — what's blocking it

### 📝 Notes for Gentech
- anything worth flagging
```

## For Gentech — template for "for-the-forge.md"

```
## For Forge — <date>

### Priority items
1. [item] — what to build
2. [item] — what to check

### Updates since last handoff
- things that changed

### Waiting on
- anything Jordan needs to do
```

## The loop

1. Gentech writes `01-HANDOFFS/for-the-forge.md`
2. Forge reads it, works, writes `01-HANDOFFS/from-the-forge.md`
3. Gentech reads Forge's response next session
4. Repeat

Jordan can check both files anytime for a complete picture.

## Copy-paste start instruction for Forge

Jordan, you can paste this directly to Forge:

> "Read 01-HANDOFFS/for-the-forge.md for your task list. When done, write your completions to 01-HANDOFFS/from-the-forge.md using the template. Check 11-Mess Hall/agent-brain/ for any handoffs from Gentech."
