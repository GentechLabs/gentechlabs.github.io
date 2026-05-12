# Arbitrum Open House — Hackathon Briefing

**Status:** 🟡 QUEUED (registration pending)
**Event:** Arbitrum Open House London: Online Buildathon
**Host:** Arbitrum Foundation via HackQuest
**URL:** https://www.hackquest.io/hackathons/Arbitrum-Open-House-London-Online-Buildathon

## Timeline

| Phase | Deadline |
|-------|----------|
| Registration | May 25, 2026 |
| Submission | June 14, 2026 |
| Results | June 17, 2026 |

**Duration:** ~3 weeks of building after registration closes

## Prize Structure — $115,000 Total

### Overall Track — $70K USDC
- 🥇 1st: $40,000
- 🥈 2nd: $20,000
- 🥉 3rd: $10,000

### Best Agentic Track — $15K USDC (🎯 OUR TARGET)
- 🥇 1st: $7,000
- 🥈 2nd: $5,000
- 🥉 3rd: $3,000

### Grants — $30K USDC
- Milestone-based, case-by-case at Arbitrum Foundation discretion

### Bonus
- Top 3 overall teams → IRL Founder House in London (4 days mentorship)

## Constraints
- At least 1 of 3 overall prizes reserved for Robinhood Chain builds
- At least 1 of 3 overall prizes reserved for Arbitrum builds
- Projects must deploy on an Arbitrum chain

## Judging Criteria (4 Pillars)
1. **Smart Contract Quality** — clean code, best practices, minimal vulnerabilities
2. **Product-Market Fit** — real users, real demand
3. **Innovation & Creativity** — original approaches
4. **Real Problem Solving** — addressing genuine market needs

## Tech Stack
- **Languages:** Solidity, Rust (Stylus)
- **Chains:** Arbitrum One (42161), Arbitrum Sepolia (421614), Robinhood Chain, Orbit chains
- **Frameworks:** Foundry ✅ (we use this), Hardhat, Remix
- **SDKs:** Arbitrum SDK (TypeScript), Stylus Rust SDK

## Target Strategy: Best Agentic Track

### Why This Track
- AgentForge is an autonomous AI agent marketplace — 100% "agentic"
- Less competition than the overall $70K track
- $15K is still significant prize money
- Our existing contract is already more mature than typical hackathon submissions

### Our Asset: AgentForge
- **Repo:** ProtoJay4789/agentforge
- **Contract:** AgentForge.sol (241 LOC, Solidity 0.8.20)
- **Tests:** 10 passing (Foundry)
- **Frontend:** Demo UI with ethers.js v6 + MetaMask
- **Agent Worker:** Hermes-based agent execution (worker.js)
- **Status:** Pre-deployment, single commit scaffold
- **Arbitrum compat:** Full — no code changes needed, just config

### What Needs Doing
1. ✅ Research complete
2. 🔄 Register (Jordan handling)
3. ⬜ Configure Foundry for Arbitrum Sepolia
4. ⬜ Deploy contract to Arbitrum Sepolia
5. ⬜ Update frontend CHAIN_ID (11155111 → 421614)
6. ⬜ Update worker.js RPC endpoint
7. ⬜ Enhance contract for hackathon scoring (see below)
8. ⬜ Build demo video
9. ⬜ Write submission

### Enhancement Ideas (for higher scores)
- Add ReentrancyGuard for safety
- Integrate with Arbitrum's fast confirmation (~250ms) for near-instant task claiming
- Use Arbitrum's low gas to enable micro-bounties (sub-cent)
- Consider ERC-4337 agent wallets (agents own accounts, have reputation)
- Add on-chain reputation system for agents
- Consider Vibekit integration (Arbitrum-native agent framework, $1M in Trailblazer grants)

## Faucets (Arbitrum Sepolia)
- Chainlink: https://faucets.chain.link/arbitrum-sepolia
- Alchemy: https://alchemy.com/faucets
- Bware Labs: https://bwarelabs.com/faucets/arbitrum-sepolia
- RPC: https://sepolia-rollup.arbitrum.io/rpc

## Recent Arbitrum Hackathon Winner Patterns
- AI + on-chain integration scores very well
- Governance/collaboration tools have strong track record
- On-chain reputation systems win
- Practical utility > fancy demos
- Agent Arena competition shows Arbitrum is investing heavily in agentic DeFi

## Participants
- 164+ registered as of May 11, 2026
