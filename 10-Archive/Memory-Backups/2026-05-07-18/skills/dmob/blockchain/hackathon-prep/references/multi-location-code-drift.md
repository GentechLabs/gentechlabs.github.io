# Multi-Location Code Drift — Solana Frontier Case Study

Session: 2026-05-05 (Solana Frontier sprint kickoff)

## Problem

Code existed in THREE separate locations with different levels of completeness:

| Location | Path | Programs | Lines | Tests | Status |
|----------|------|----------|-------|-------|--------|
| Git repo | `~/repos/agent-economy-solana/` | 1 (partial) | ~200 | Boilerplate | ❌ Stale — 1 commit, missing instruction files |
| Vault code | `02-Labs/Hackathons/Active/Colosseum-Frontier/agent-escrow-solana/` | 4 | ~2,075 | 53/53 claimed | ✅ Most complete per handoff |
| Projects folder | `/root/projects/colosseum-frontier/colosseum-programs/` | 4 | 2,075 | Unknown | ✅ Has devnet program IDs in Anchor.toml |

Additionally, a Zerion sidetrack adapter existed at:
- `02-Labs/Hackathons/Active/Colosseum-Frontier/zerion-agent/` — TypeScript CLI, built

## How This Happened

1. Initial scaffolding done in git repo (session ~Apr 21)
2. More complete rebuild done in projects folder (session ~Apr 28)
3. Vault received copies/syncs at various points
4. Git repo was NEVER updated with the projects folder version
5. Sprint plan (Apr 29) referenced "2 deployed to devnet" based on vault handoff notes, not filesystem reality

## Detection Commands

```bash
# Find ALL code locations for a project
find ~/repos/ -name "Anchor.toml" -o -name "foundry.toml" 2>/dev/null
find /root/vaults/gentech/02-Labs/ -path "*/Active/*" -name "*.rs" 2>/dev/null | head -10
find /root/projects/ -name "Anchor.toml" 2>/dev/null

# Compare completeness
for loc in ~/repos/agent-economy-solana /root/projects/colosseum-frontier/colosseum-programs /root/vaults/gentech/02-Labs/Hackathons/Active/Colosseum-Frontier/agent-escrow-solana; do
  echo "=== $loc ==="
  find "$loc" -name "*.rs" 2>/dev/null | wc -l
  find "$loc" -name "*.rs" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1
done
```

## Resolution

Use the most complete version (projects folder) as canonical. Sync to git. Archive or delete stale copies.

## Prevention

After any significant build session:
1. Commit and push to git immediately
2. If working in vault or /root/projects/, sync back to the canonical repo
3. Never have >1 active copy of the same codebase
