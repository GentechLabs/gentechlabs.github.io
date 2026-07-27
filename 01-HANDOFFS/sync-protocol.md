# Forge Sync Protocol

## How this works

```
Gentech writes → 01-HANDOFFS/for-the-forge.md           (tasks for Forge)
                 01-HANDOFFS/gentech-to-forge/           (dated task files)
                 
Forge writes   → 01-HANDOFFS/from-the-forge.md           (what Forge did)
                 01-HANDOFFS/forge-completions.md        (item IDs shipped)

Tick script    → scripts/tick_build_queue.py             (reads completions → updates queue)
                 
Vault sync     → git push vault → github.com/ProtoJay4789/gentech-vault.git
```

## The loop

1. **Gentech** writes `01-HANDOFFS/for-the-forge.md` with current priority items
2. **Forge** reads it (from GitHub or local vault), works, writes `from-the-forge.md` + `forge-completions.md`
3. **Gentech** runs `python3 scripts/tick_build_queue.py --apply` to consume completions into the queue
4. **Gentech** writes a fresh `for-the-forge.md` with updated queue
5. Repeat

## For Forge — template

```
## From Forge — <date>

### ✅ Completed this session
- #<id> — what was built

### ⏸ Blocked / waiting on
- #<id> — what's blocking

### 📝 Notes
- anything worth flagging
```

Also write completed item IDs to `01-HANDOFFS/forge-completions.md`:
```
## Shipped
- **#<id>** — brief description
```

## For Gentech — template

```
## For Forge — <date>

### Priority items
1. **#<id>** <name> — what to build

### Updates since last handoff
- things that changed

### Full queue
See scripts/build_queue.json
```

## Important

- **Forge sometimes pushes only to GitHub** — always `git pull vault main` before reading handoffs
- **Tick script** lives at `scripts/tick_build_queue.py` — run with `--apply` after Forge completes
- **`02-HANDOFFS/forge-to-gentech/`** — archived, not used. Forge writes to `01-HANDOFFS/from-the-forge.md`
- **`gentech-vault-new`** — deprecated. All handoffs live in the root vault at `/root/vaults/gentech/01-HANDOFFS/`
