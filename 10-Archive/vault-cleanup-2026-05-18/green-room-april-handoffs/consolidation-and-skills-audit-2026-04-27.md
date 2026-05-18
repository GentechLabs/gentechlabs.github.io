---
date: 2026-04-27
author: YoYo
type: audit
status: pending-approval
tags: [consolidation, skills, github, vault-structure]
---

# Consolidation + Skills Audit — 2026-04-27

## 1. Brain Consolidation Proposal

### Current State
- `02-Labs` exists with 17 subfolders (Apollo-Age, Bug-Bounties, GenLayer-SDK, Hackathons, ProtoBots, R&D, Reference, SDK-Comparisons, Security-Analysis, Technical, handoffs, research, security-audit, social-layer-poc, tech-payment-router).
- `03-Projects` exists separately with 10 subfolders (AAE, AgentFi, BirdeyeBIP, Kite, auto-rebalance-gas-abstraction, genlayer-recon, tech-burn-test, Personal-Portfolio, From-Entertainment, _merged-01-Projects).
- Duplicates found: `social-layer-poc` in both 02-Labs and 03-Strategies; `tech-payment-router` in 02-Labs while `tech-burn-test` sits in 03-Projects.

### Proposed Structure
Rename `02-Labs` → `02-Gentech-Labs` and fold `03-Projects` into it:
```
02-Gentech-Labs/
├── AAE/
├── AgentFi/
├── Apollo-Age/
├── BirdeyeBIP/
├── Bug-Bounties/
├── GenLayer-SDK/
├── Hackathons/
├── Kite/
├── ProtoBots/
├── R&D/
├── SDK-Comparisons/
├── Security-Analysis/
├── Technical/
├── auto-rebalance-gas-abstraction/
├── genlayer-recon/
├── handoffs/
├── research/
├── security-audit/
├── social-layer-poc/   (merge duplicates, keep canonical)
├── tech-payment-router/ (merge with tech-burn-test if related)
└── Reference/
```

### GitHub Consolidation
- **ProtoJay4789 (personal, 20 repos)** hosts all product code: aae-contracts, agent-escrow, birdeye-adapter-bip, kite-agent-commerce, arc-hackathon, agent-economy-solana, etc.
- **Gentech-Labs (org, 6 repos)** only has infra/landing: gentech-agency, hermes-workspace, hermes-control-interface, hermes-brain, gentech-vault, hermes-brain-backup.
- **Action:** Migrate active product repos to Gentech-Labs org. Keep personal forks as archives. Update vault links after migration.

## 2. Skills Audit Results

### Active Pending Skills to Promote (recent commits)
| Skill | Last Commit | Priority |
|-------|-------------|----------|
| calesthio/OpenMontage | 2026-04-24 | HIGH |
| addyosmani/agent-skills | 2026-04-26 | MEDIUM |
| almanak-co/sdk | 2026-04-26 | MEDIUM |
| HKUDS/AI-Trader | 2026-04-24 | MEDIUM |
| ZealynxSecurity/krait | 2026-04-16 | HIGH |
| trailofbits/skills | 2026-04-16 | HIGH |
| OpenBMB/VoxCPM | 2026-04-21 | HIGH |
| NethermindEth/defi-skills | 2026-04-19 | HIGH |

### Stale — Recommend Drop
| Skill | Last Commit | Reason |
|-------|-------------|--------|
| immunefi-team/Web3-Security-Library | 2025-03-25 | 13+ months stale |

## 3. Next Actions (Requires Gentech / Jordan)
1. **Approve vault folder merge** — consolidate `03-Projects` into `02-Labs` (or rename to `02-Gentech-Labs`).
2. **Approve GitHub repo migration** — move active product repos from ProtoJay4789 to Gentech-Labs org.
3. **Approve skill installs** — promote 8 active pending skills (especially OpenMontage for Desmond, almanak/sdk + defi-skills for YoYo).
4. **Approve skill drop** — remove immunefi-team/Web3-Security-Library from pending list.

---
*Route to: Gentech HQ for execution planning. Jordan approval required for all moves.*
