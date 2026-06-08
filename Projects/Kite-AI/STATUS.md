# Kite AI — Agentic Commerce

**Status:** 🎬 Demo video re-rendering (fixed scene timing bug)
**Hackathon:** Kite AI Global — Encode AI Club
**Deadline:** May 17, 2026

## Deployed Contracts (Kite Testnet)
- **AgentEscrow:** `0xf7DcebAEC0356c96926a6619Fc80F24590932F06`
- **TECHPaymentRouter:** `0x963Cb46670c4F13C2dbB3a10BEE49BBb3650AC14`
- **MockTECH:** `0x2C7DE7F6C149808E66B87cE138fdDb00dDAf085E`

## Wallets
- Deployer: `0xE00a46132Fd03456cEcd05de8C69F43C5138Db95` (0.5 KITE)
- Demo: `0x61B7b7F67D596458Be0aF6c7d261F129FAeb9aC5` (0.5 KITE)

## What's Done
- [x] Smart contracts (AgentEscrow, TECHPaymentRouter, MockTECH)
- [x] 52/52 tests passing
- [x] Deployed to Kite testnet (chain 2368)
- [x] UI HTML updated with contract addresses
- [x] GitHub repo: ProtoJay4789/kite-agent-commerce
- [x] README updated with real addresses, correct deadline

## What's Left
- [ ] Demo video render (re-rendering — fixed data-start timing bug)
- [ ] Submit to Encode AI Club hackathon
- [ ] Post-submission: audit Kite core contracts for $10K Code4rena bounty

## Key Files
- Repo: `/root/.hermes/profiles/gentech/home/repos/kite-agent-commerce/`
- Demo video comp: `/tmp/kite-final/`

## Bug Fixed (May 15)
All scenes had `data-start="0"` — HyperFrames renderer ignores GSAP timeline and uses data attributes for clip timing. Fixed to staggered values: 0, 3, 6, 11, 16, 20.
