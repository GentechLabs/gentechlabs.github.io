# 🔴 Solana Frontier Sprint — T-6 Days (May 5-11)

**Deadline:** May 11, 2026
**Submission:** AgentEscrow — Trust infrastructure for the agent economy
**Repo:** `/root/projects/colosseum-frontier/colosseum-programs/`
**Vault code:** `/root/vaults/gentech/02-Labs/Hackathons/Active/Colosseum-Frontier/agent-escrow-solana/`

---

## What's Built (from Apr 28 sprint)
- ✅ 4 Anchor programs: agent-registry, job-escrow, dispute-resolver, reputation
- ✅ 2,075 lines Rust (vault version — more complete than repo)
- ✅ 53/53 tests passing
- ✅ Client SDK scaffold (index.ts, escrow.ts, world-id.ts, oobe.ts)
- ✅ All docs: Technical Architecture, Submission Writeup, Demo Storyboard, Social Thread

## What's Left (prioritized)

### 🔴 P0 — Must Ship (Days 1-3)
| Task | Owner | Est. | Status |
|------|-------|------|--------|
| Sync vault code → repo (vault is more complete) | DMOB | 1hr | ⬜ |
| Full test suite — all 12 instructions covered | DMOB | 3hr | ⬜ |
| TypeScript client SDK — Phantom wallet integration | DMOB | 4hr | ⬜ |
| Deploy all 4 programs to Solana devnet | DMOB | 2hr | ⬜ |
| BurnSplitter fix (security audit flag) | DMOB | 1hr | ⬜ |

### 🟡 P1 — Demo Ready (Days 3-5)
| Task | Owner | Est. | Status |
|------|-------|------|--------|
| Next.js frontend — Phantom connect + escrow flow | DMOB | 6hr | ⬜ |
| Swig payment routing integration | DMOB | 3hr | ⬜ |
| Metaplex reputation NFT minting in UI | DMOB | 2hr | ⬜ |
| World ID verification flow | DMOB | 2hr | ⬜ |

### 🟢 P2 — Polish + Submit (Days 5-6)
| Task | Owner | Est. | Status |
|------|-------|------|--------|
| Demo video recording (5-min flow) | Desmond | 3hr | ⬜ |
| README final polish | Desmond | 1hr | ⬜ |
| Submission to Colosseum portal | Jordan | 30min | ⬜ |
| Sidetrack submissions (Zerion $5K, GoldRush $3K) | YoYo | 2hr | ⬜ |
| Social thread posting | Desmond | 30min | ⬜ |

---

## Daily Check-ins
- **May 5 (today):** Code sync + test suite + devnet deploy prep
- **May 6:** Client SDK + frontend scaffold
- **May 7:** Frontend complete + sponsor integrations
- **May 8:** Full demo flow working end-to-end
- **May 9:** Demo video recording + README
- **May 10:** Final polish + submission
- **May 11:** **DEADLINE** — submit by EOD

---

## Sponsor Integration Status
| Sponsor | Integration | Status |
|---------|-------------|--------|
| Phantom | Wallet connect + signing | ⬜ |
| Swig | Multi-token payment routing | ⬜ |
| Metaplex | Soulbound reputation NFTs | ⬜ |
| World | Identity verification | ⬜ |

## Sidetrack Opportunities
- ✅ **Option B LOCKED** (Jordan confirmed May 5)

| Track | Prize | Fit | Status |
|-------|-------|-----|--------|
| Zerion CLI | $5K | Agent portfolio management | Planned |
| GoldRush (Covalent) | $3K | On-chain data + agent reputation | Planned |

**Total sidetrack target: $8K extra**

### What these adapters look like
- **Zerion:** Thin wrapper — agent discovers portfolio, proposes actions via CLI. ~2-3hr build
- **GoldRush:** Covalent API adapter — feed on-chain risk data into AgentEscrow reputation. ~2-3hr build
- Both are SDK integrations, not new programs. DMOB builds main submission first, adapters last 2 days

### Video Demo Plan (May 6 experiments)
- Jordan exploring local Hermes model + Hagen video agent for polished demo
- Demo recording currently scheduled Day 5 (May 9) — buffer for experiments

---

*Last updated: 2026-05-05 by YoYo*
