# Solana Frontier — Code Location Map (May 5, 2026)

## Three Code Locations Found

### 1. Git Repo (STALE — ignore)
- **Path:** `~/repos/agent-economy-solana/`
- **State:** 1 program (agent_registry), partial, no instruction handler files
- **Git:** 1 commit, boilerplate tests
- **Verdict:** Outdated — do NOT build from here

### 2. Projects Folder (MOST COMPLETE — canonical)
- **Path:** `/root/projects/colosseum-frontier/colosseum-programs/`
- **Programs:** 4 — agent-registry, job-escrow, dispute-resolver, reputation
- **Lines:** 2,075 Rust
- **Anchor.toml:** Devnet program IDs pre-configured
  - agent_registry: `6ZS1rNMKrkHLyFS878mU748BbWwbgWMkKFgBJQNKiAG7`
  - dispute_resolver: `wtPxD8z3K2C515cZaB5CCN4BNmuX4ahhNpvYJn2HCo1`
  - job_escrow: `HqpwrZDaoLtNkhsdM8XqX3UPDDozrWLnNF2q6FrD95vH`
  - reputation: `9CDr7iJrrKvzdxFMmK156EFEHKdXR2jiDDCVqLSX79rb`
- **Sponsor integrations:** World ID, Metaplex

### 3. Vault Code (ALSO COMPLETE — tests claimed)
- **Path:** `/root/vaults/gentech/02-Labs/Hackathons/Active/Colosseum-Frontier/agent-escrow-solana/`
- **Claimed:** 53/53 tests passing, client SDK scaffold
- **Has:** Anchor.toml, Cargo.lock, target/ (may be pre-built)

### 4. Zerion Adapter (SIDETRACK — built)
- **Path:** `/root/vaults/gentech/02-Labs/Hackathons/Active/Colosseum-Frontier/zerion-agent/`
- **Type:** TypeScript CLI agent for Zerion sidetrack ($5K)

## Sync Strategy
1. Use projects folder as canonical (has all 4 programs + deploy IDs)
2. Verify vault version tests pass (53/53 claimed)
3. Sync best version to git repo
4. Install toolchain (Solana CLI + Anchor) if not present

## Key Docs in Vault
- `02-Labs/Hackathons/04-Solana-Frontier-May11.md` — main tracker
- `09-Green Room/active-handoffs/2026-05-05-solana-frontier-sprint.md` — sprint plan
- `02-Labs/EVM-to-Solana-Port-Map.md` — porting reference
- `02-Labs/Hackathons/Modular-Dev-Workflow.md` — build workflow
