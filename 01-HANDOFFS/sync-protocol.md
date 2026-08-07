# Handoff Sync Protocol (V4 — all groups)

## The loop: every group sends work back, Gentech consumes overnight

```
OUTBOUND (Gentech → group agent)
Gentech writes → 01-HANDOFFS/gentech-to-<group>/   (dated task files, per group)
                 gentech-to-forge/                 (legacy Forge path)

RETURN (group agent → Gentech)
Group writes    → 01-HANDOFFS/<group>-to-gentech/  (dated "here's what I did" files)
                 <group>-completions.md            (item IDs shipped, e.g. "- **#42** — built X")

Groups: labs, entertainment, finance (Treasury), hq, forge.

CONSUME (overnight, Gentech)
group-returns-scanner.py  → reads EVERY <group>-to-gentech/ + <group>-completions.md,
                            extracts shipped item IDs + notes, emits JSON
Nightly Build Session     → applies returned IDs to build_queue.json (status → shipped)
Morning Digest            → surfaces group returns + stale notes to Jordan

VAULT SYNC → git push vault → github.com/ProtoJay4789/gentech-vault.git
```

## Return file contract (for any group agent)

Each group agent has a symmetric return path so Gentech picks up its work:

- **Return folder:** `01-HANDOFFS/<group>-to-gentech/` — drop dated `.md` files here:
  ```
  ## From <Group> — <date>
  ### ✅ Completed this session
  - #<id> — what was built
  ### ⏸ Blocked / waiting on
  - #<id> — what's blocking
  ### 📝 Notes
  ```
- **Completion file:** `01-HANDOFFS/<group>-completions.md` — list shipped item IDs:
  ```
  ## Shipped
  - **#<id>** — brief description
  ```
  The scanner parses `#<id>` tokens from both the folder notes and the completion file.

## Gentech overnight consumption

1. `group-returns-scanner.py` runs as a cron script — its JSON is injected into the
   Nightly Build Session AND the Morning Digest.
2. Nightly Build applies returned IDs to the queue (status → shipped, notes the group+date).
3. `stale-notes-scanner.py` surfaces unaddressed brain items (considerations.md,
   agent-brain/, ideas.md) so the digest flags them.
4. Deterministic gate: if `pending AND needs_jordan=false` count >= 1 → BUILD; else
   MAINTENANCE (ob sync, vault push, flesh ideas, infra health). Never idle.

## Legacy Forge paths (kept)

- `for-the-forge.md` + `from-the-forge.md` + `forge-completions.md` still work and are
  still consumed by `tick_build_queue.py`. The new per-group return folders generalize
  this to labs/entertainment/finance/hq.

## ROUTING RULE — Forge = the desktop lane (Jordan, Aug 5)

"Forge only" is shorthand for **desktop only**. Forge runs on Jordan's PC, so anything
that's easier done on the desktop should route to Forge **regardless of group**:
- MetaMask / wallet signing
- Browser logins + account actions (uphive wallet link, OKX, etc.)
- Local files / desktop-only tools
- Opening a website Jordan has to see

When writing a handoff, if the task needs Jordan at a desktop, direct it to
`gentech-to-forge/` (or note "Forge (desktop)" in the per-group note) so it lands on
the right lane. Forge returns via `forge-to-gentech/` + `forge-completions.md`.

## Important

- **Group agents sometimes push only to GitHub** — always `git pull vault main` before reading handoffs.
- **`02-HANDOFFS/forge-to-gentech/`** — archived, not used.
- **`gentech-vault-new`** — deprecated. All handoffs live in `/root/vaults/gentech/01-HANDOFFS/`.
