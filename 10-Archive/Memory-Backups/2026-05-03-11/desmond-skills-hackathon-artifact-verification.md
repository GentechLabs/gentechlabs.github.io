# Hackathon Artifact Verification Checklist

When auditing disk space during active hackathons, distinguish between reclaimable build artifacts and mission-critical materials.

## Quick Checks (per project directory)

1. **Recent activity** — high count suggests active work:
   ```bash
   find . -type f -newermt '7 days ago' 2>/dev/null | wc -l
   ```

2. **Uncommitted changes** — work in progress:
   ```bash
   git status --short
   ```

3. **Demo/Submission indicators** — look for:
   - `DEMO_SCRIPT.md`, `DEMO_STORYBOARD.md`
   - `README.md` containing keywords: "submission", "hackathon", "demo", "pitch"
   - `videos/`, `demo/`, or `submission/` directories

4. **Vault cross-reference** — search:
   - `/root/vaults/gentech/02-Labs/Hackathons/Active/` for project name
   - `/root/vaults/gentech/09-Green Room/` for handoff notes

5. **Build artifact status** — check timestamps:
   ```bash
   stat -c '%y' target/  # if modified <7 days, treat as active
   ```

## Decision Matrix

| Condition | Action |
|-----------|--------|
| Uncommitted changes OR demo files present OR listed in Active hackathon folder | **KEEP — verify with owner before any deletion** |
| No recent changes (>30 days), no vault references, multiple similar forks | Candidate for ARCHIVE after owner confirmation |
| Clear old experiment with no connection to current work | Safe to delete (but ask user first) |

## Docker Image Verification

1. Running containers check:
   ```bash
   docker ps --format "{{.Image}}\t{{.Names}}"
   ```
   If image is used by a running container → **KEEP**.

2. Service dependency check — search vault for image name (e.g., "rsshub", "browserless"):
   ```bash
   grep -r "rsshub" /root/vaults/gentech/ 2>/dev/null | head
   ```
   If referenced in specs or setup docs → **VERIFY** with owner.

3. Size threshold — images >1GB and unused are prune candidates, but still confirm with user.

4. Remember: stopping a container doesn't free the image if another container may restart from it. Use `docker images -a` to see all.

## Rust Target Verification

- Large `target/` directories (>1GB) often contain build artifacts, but may include demo binaries.
- Check parent project for `Cargo.toml`/`Anchor.toml` and README. Presence of `DEMO_SCRIPT.md` = active hackathon work.
- If multiple forks exist (e.g., `agent-starter-pack/colosseum-frontier` vs `projects/colosseum-frontier`), do not delete any until the submission version is identified via vault docs or Green Room handoffs.
- Ask DMOB (Labs) to confirm which codebase is the submission source.

## Coordination Protocol

When uncertain, create a note in Green Room (`09-Green Room/`) tagging the responsible agent:
- DMOB — for codebase/build questions
- Jordan — for approval of deletions >500MB
- Wait for explicit confirmation before executing destructive operations.
