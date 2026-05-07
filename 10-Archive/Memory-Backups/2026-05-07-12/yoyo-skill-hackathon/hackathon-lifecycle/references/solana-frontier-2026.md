# Solana Frontier Hackathon — Quick Reference

**Platform**: Colosseum
**Dates**: April 6 – May 11, 2026
**URL**: https://colosseum.com (Frontier Hackathon section)
**Status**: Active (deadline May 11)
**Our Submission**: AgentEscrow (trust infrastructure for agent economy)

---

## Prizes

- **$30,000** — Grand Champion
- **$10,000** — Public Goods Award
- **$10,000** — University Award
- **$10,000 × 20 teams** — Sponsor-specific awards (Phantom, Swig, Metaplex, etc.)
- **Accelerator**: All winners considered for Colosseum Accelerator ($250K pre-seed + network + mentorship)

---

## Tracks ("Build by Path")

1. **Agents + Tokenization** ⭐ — AI agents with onchain identity and economic functionality
2. **Payments + Commerce** ⭐ — Accept payments and build commerce on Solana
3. **Treasury + Security** ⭐ — Secure assets, manage treasuries, run financial operations
4. **Identity + Human Verification** ⭐ — Proof-of-human, sybil resistance
5. DeFi + Stablecoins — Interest-bearing dollars and stablecoin primitives
6. Blinks + Actions — Shareable transaction interfaces for Solana actions
7. Governance / DAOs — Governance and DAO tooling
8. Mobile — Native mobile apps powered by Solana
9. Privacy + Confidential Compute — Encrypted applications with private state
10. Games — Fully on-chain games or Solana integration into existing engines

⭐ = tracks our AgentEscrow submission targets

---

## Sponsor Integrations (in our architecture)

| Sponsor | Role in AgentEscrow | Why Judges Care |
|---------|-------------------|-----------------|
| **Phantom** | Primary wallet + UX layer | Embedded iframe buyer onboarding |
| **Swig** | Multi-token payment routing | Agents get paid in preferred token |
| **Metaplex** | Soulbound reputation NFTs | Portable agent reputation on Solana |
| **World** | Identity verification (World ID) | Sybil prevention, trust badge |

---

## Judges (partial list — from Colosseum page)

- Anatoly Yakovenko (Cofounder, Solana)
- Lily Liu (President, Solana Foundation)
- Clay Robbins (Cofounder, Colosseum)
- Adam Gutierrez (Phantom)
- Justin (CEO, Swig)
- Stephen Hess (Metaplex Foundation)

---

## AgentEscrow Build Status (as of 2026-05-05)

- ✅ Architecture spec complete (4 programs + frontend + oracle)
- ✅ AgentEscrow contracts — 53/53 tests passing
- ✅ Two-tier dispute resolution (IResolver refactor)
- ✅ Security audit complete (BurnSplitter fix needed pre-deploy)
- 🔴 Programs not yet deployed to devnet
- 🔴 Frontend not yet built
- 🔴 Sponsor integrations (Swig, Metaplex, World) not wired up
- 🔴 Demo video not recorded

**Critical path**: DMOB needs to deploy programs + build minimal frontend in 6 days.

---

## Submission Requirements

- Working demo (deployed to devnet or localhost)
- GitHub repo with README
- Demo video (required for judging)
- Submit via Colosseum portal

---

*Last updated: 2026-05-05 | Source: Colosseum Frontier website + vault architecture docs*
