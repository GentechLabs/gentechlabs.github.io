# Handoff Sync Protocol (V4 — full mesh, all groups)

## The loop: ANY group can hand off to ANY other group

V4 is a **full mesh**, not hub-and-spoke. Every group can send work to every
other group for approval, context, or handoff — not just back to Gentech.

```
MESH (any group → any group)
<from>-to-<to>/   → 01-HANDOFFS/<from>-to-<to>/   (dated task/context files)
                    e.g. labs-to-treasury/, entertainment-to-hq/, forge-to-labs/

RETURN (any group → any group)
<from>-to-<to>/   → 01-HANDOFFS/<from>-to-<to>/   (dated "here's what I did" files)
<from>-completions.md                            (item IDs shipped, e.g. "- **#42** — built X")

Groups: labs, entertainment, finance (Treasury), hq, forge, gizmo.

CONSUME (overnight, Gentech)
group-returns-scanner.py  → reads EVERY <group>-to-<group>/ + <group>-completions.md,
                            extracts shipped item IDs + notes, emits JSON
Nightly Build Session     → applies returned IDs to build_queue.json (status → shipped)
Morning Digest            → surfaces group returns + stale notes to Jordan

VAULT SYNC → git push vault → github.com/ProtoJay4789/gentech-vault.git
```

### Mesh routing rules
- **Approval/decision needed** → hand off to `hq` (Jordan's lane) or the group that owns the decision.
- **Context needed** → hand off to the group that holds the context (e.g. a finance decision that needs Labs' technical read → `labs-to-treasury/`).
- **Build work** → hand off to `labs` (or `forge` for desktop-only work).
- **Content/social** → hand off to `entertainment`.
- **Finance/portfolio/yield** → hand off to `treasury`.
- **Gentech still consumes ALL returns overnight** — the mesh doesn't remove Gentech's consolidation role; it adds direct peer handoffs on top. Gentech's scanner reads every `<group>-to-<group>/` folder, so nothing gets lost regardless of who sent it to whom.

## Return file contract (for any group agent)

Each group agent has a symmetric return path to ANY other group, so work
flows peer-to-peer and Gentech still picks everything up overnight:

- **Return folder:** `01-HANDOFFS/<from>-to-<to>/` — drop dated `.md` files here
  (e.g. `labs-to-treasury/2026-08-15.md` for Labs → Treasury):
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
