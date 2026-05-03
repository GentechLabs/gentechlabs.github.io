# Vault Atomic Writer — Shared Brain Access

Gentech's vault is our single source of truth. This utility provides atomic, concurrent-safe read/write operations so any agent can append context without race conditions.

## Quick Use

```bash
# Append a decision or finding
vault_writer.py write <relative-path> --content "Your markdown here" --author "DMOB" --group "Labs"

# Read a file (optionally tail last N entries)
vault_writer.py read 02-Labs/decisions.md --tail 3

# Search across vault
vault_writer.py search "reentrancy" --group Labs --limit 20
```

## Conventions

- **Lock namespace** = `{group}-{filename}` (Labs decisions → `Labs-decisions`)
- **Append mode** = each call adds new `## {timestamp} — {author}` entry
- **Overwrite mode** = replace entire file (use sparingly)
- **Frontmatter** = optional YAML passed via `--metadata '{"key":"value"}'`
- **Idempotency** = same timestamp won't duplicate (detected via `---` delimiter)

## Integration Pattern

Agents should:
1. `vault_writer.py read <group-brain>.md` on task start (pulls latest context)
2. Work in isolation
3. `vault_writer.py write <group-brain>.md --append` on completion (pushes findings)

## Example Workflow

```bash
# Labs audit agent pulls shared context
vault_writer.py read 02-Labs/decisions.md

# After finding a vuln, record it
vault_writer.py write 02-Labs/decisions.md \
  --content "Found storage collision in AccessControl.sol: roleBitmap overlaps with admin slot (slot 0)." \
  --author "DMOB" --group "Labs"
```

**Path**: `02-Labs/scripts/vault_writer.py`
