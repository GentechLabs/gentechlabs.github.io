# DMOB — Specialist Context

## Current State (Updated 2026-05-10)
- **Role**: CTO — Smart contracts, Foundry, security, deployment, hackathons
- **Status**: On-demand only (orchestrator pattern)
- **Home Group**: GenTech Labs

## Active Projects
- **AgentEscrow Contracts**: 14/14 tests passing, ready for deployment
- **x402 Integration**: Sidetrack adapters spec'd (Zerion $5K, GoldRush $3K)
- **Kite AI Hackathon**: Deadline May 17 — CURRENT PRIORITY
- **Swarms ACM Hackathon**: Deadline May 27

## Key Files
- Repo: `github.com/ProtoJay4789/agent-escrow`
- Scripts: `/root/vaults/gentech/03-Strategies/scripts/`

## Cron Jobs
- `x402 Ecosystem Watch`: Bi-weekly — OK
- `LP Position Monitor Hourly`: OK
- `Defi Milestone — Morning`: FAILING (auth)
- `Defi Milestone — Evening`: OK
- `LayerZero DVN Monitor`: FAILING
- `brain-backup`: FAILING
- `blockchain-contest-scanner`: FAILING
- `Sunday Skill Update Check`: FAILING

## Blockers
- Cron auth failures across multiple jobs
- GitHub token issue (stale env var — fix identified, needs verification)

## Removed (Stale)
- ~~Anchor toolchain / Rust 1.85+~~ — Was for Solana Frontier (withdrawn)
- ~~Solana Frontier Hackathon~~ — Withdrawn, not enough time
