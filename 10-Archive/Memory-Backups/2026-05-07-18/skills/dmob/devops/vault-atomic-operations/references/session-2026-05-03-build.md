# Session Build: Vault Atomic Writer

**Date:** 2026-05-03
**Agent:** DMOB (Labs)
**Trigger:** User wants vault as shared brain with concurrent-safe access
**Deliverable:** `vault_writer.py` — atomic append+read utility with file locking

## Problem

Gentech uses vault (`/root/vaults/gentech/`) as single source of truth across multiple agents (Hermes instances, scanners, cron jobs). Without coordination:

- Two agents append simultaneously → lost writes
- Scan + write overlap → torn reads
- No provenance → unclear decision ownership

## Solution

File-lock + append-only pattern:

- **Lock namespace:** `{group}-{filename}` (e.g., `Labs-decisions`)
- **Append format:** `## {iso-timestamp} — {author}\n\n{content}\n\n---\n`
- **Idempotency:** duplicate timestamps are skipped
- **Output:** JSON status with path/timestamp/bytes_written

## Integration

Agents call before/after tasks:

```bash
# Pull latest context
vault_writer.py read 02-Labs/decisions.md --tail 5

# After finding, append
vault_writer.py write 02-Labs/decisions.md \
  --content "Finding: storage collision in AccessControl.sol roleBitmap slot" \
  --author DMOB --group Labs
```

Hermes integration: load `vault-atomic-operations` skill, use `terminal` tool to invoke script directly.

## Files

- Skill: `devops/vault-atomic-operations/SKILL.md`
- Script: `devops/vault-atomic-operations/scripts/vault_writer.py` (also copied to vault path: `02-Labs/scripts/vault_writer.py`)
- In-vault usage doc: `02-Labs/scripts/VAULT_WRITER.md`

## Follow-ups

- Consider git-auto-commit wrapper if audit trail needs diffs per entry
- Add per-group rotation policy (quarterly file splits) to avoid lock contention at scale
