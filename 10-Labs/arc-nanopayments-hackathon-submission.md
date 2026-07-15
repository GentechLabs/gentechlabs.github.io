# Encode Club — Programmable Money Hackathon

## Submission: Arc Nanopayments Demo

**Track:** Agentic Economy
**Repo:** https://github.com/ProtoJay4789/arc-nanopayments
**Dates:** Jul 13 – Aug 9 (4 weeks)
**Checkpoint 1:** Jul 19 — Create project, team, idea

## What We're Building

An autonomous AI agent (LangChain) that pays for premium cost-of-living intelligence via x402 gasless USDC nanopayments on Arc. The seller is a Next.js dashboard with x402-protected endpoints.

### Agentic Economy Track Criteria

| Requirement | How We Meet It |
|-------------|---------------|
| Agents with clear decision logic tied to real signals | Agent decides which cities to research, compares cost-of-living, analyzes affordability |
| Autonomous spending, payments or settlement flows using USDC | Agent pays $0.001 per query via Circle GatewayClient on Arc testnet |
| Use of Agent Stack to connect agents to wallets | `@circle-fin/x402-batching` GatewayClient — exactly Circle's recommended Agent Stack |
| Nanopayments, Paymaster or App Kits | x402 batch-settled gasless nanopayments |

### Premium Endpoints

| Endpoint | Price | Description |
|----------|-------|-------------|
| `/api/premium/cost-of-living?city=X` | $0.001 | City cost-of-living data with 60+ price points |
| `/api/premium/cost-of-living?city=X&compare=Y` | $0.001 | City-to-city comparison with differentials + AI analysis |
| `/api/premium/dataset` | $0.001 | Premium dataset download |
| `/api/premium/compute` | $0.001 | AI-powered compute (POST) |
| `/api/premium/agent-task` | $0.001 | Autonomous agent task |
| `/api/premium/quote` | $0.001 | Inspirational quote (control) |

### Agent Capabilities

- Autonomously calls endpoints on a 1-second interval
- Manages ephemeral wallet funded from a master wallet
- Auto-redeposits to Gateway when balance drops below threshold
- Respects configurable spending limits with pause-and-prompt for more
- Handles nonce collisions with retry logic

### Tech Stack

- **Blockchain:** Arc testnet (Circle's stablecoin-native L1)
- **Payments:** Circle Gateway x402 batching (`@circle-fin/x402-batching`)
- **Agent:** LangChain with optional OpenAI (mock mode without key)
- **Frontend:** Next.js 16, React 19, Tailwind CSS 4, shadcn/ui
- **Data:** Supabase (transactions), cost-of-living JSON dataset
- **Wallet:** viem, arcTestnet chain

## To Do

### Checkpoint 1 (Jul 19) — Create Project
- [x] Code ready
- [ ] Create project page on Encode platform
- [ ] Choose Agentic Economy track
- [ ] Write project description

### Further Additions
- [ ] Deploy on Vercel so judges can interact live
- [ ] Add more cities to dataset (expand to 30+)
- [ ] Wire GenTech x402 gateway for real wallet analysis endpoint
- [ ] Create 3-min demo video
- [ ] Final submission: functional MVP on Arc, public repo, video + deck
