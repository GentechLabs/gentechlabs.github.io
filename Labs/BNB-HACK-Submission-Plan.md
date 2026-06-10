# BNB HACK: AI Trading Agent Edition — Submission Plan

## Hackathon Details
- **Name:** BNB HACK: AI Trading Agent Edition
- **Prize Pool:** $36,000
- **Partners:** BNB Chain + CoinMarketCap + Trust Wallet
- **Duration:** 3 weeks (opened June 3, 2026)
- **Register:** https://dorahacks.io/hackathon/bnbhack-twt-cmc
- **Stack:** Trust Wallet Agent Kit + BNBAgent SDK

## BNBAgent SDK — Key Components

### ERC-8004 (Agent Identity)
- Register AI agent on-chain with unique identity token (ERC-721)
- Discoverable profile with name, description, protocol endpoints
- Gas-free registration on BSC Testnet via MegaFuel paymaster
- `pip install bnbagent`

### ERC-8183 (Agentic Commerce)
- **AgenticCommerce** kernel — job state + escrow
- **EvaluatorRouter** — routes jobs to policies
- **OptimisticPolicy** — silence = approval, dispute window for conflicts
- Job lifecycle: OPEN → FUNDED → SUBMITTED → COMPLETED/REJECTED/EXPIRED
- Negotiation: off-chain HTTP, anchored on-chain
- Deliverable: off-chain storage (IPFS/local), keccak256 hash on-chain
- Platform fee: basis points deducted on complete

### Architecture
```
Client → negotiate → createJob → fund → provider submits → settle
                                                    ↓
                                          policy.check() → approve/reject
```

## Our Submission: Agent-to-Agent DeFi Defense Network

### Concept
Multi-agent system where:
1. **Oracle Agent** — monitors token risk, sentiment, protocol health
2. **Defense Agent** — receives alerts, executes protective actions (withdraw, hedge)
3. **Settlement Agent** — handles payments between agents via ERC-8183 escrow

### Why This Wins
- Uses ERC-8004 for agent identity (built-in discovery)
- Uses ERC-8183 for agent-to-agent payment (trustless escrow)
- Real DeFi security use case (not just a trading bot)
- Demonstrates the full agentic commerce loop

### Tech Stack
- Python + BNBAgent SDK (`pip install bnbagent`)
- BSC Testnet (gas-free via MegaFuel)
- Trust Wallet Agent Kit (if needed for wallet integration)

### Timeline (3 weeks)
- Week 1: Register agents, set up ERC-8004 identities, basic Oracle Agent
- Week 2: Defense Agent + ERC-8183 job negotiation between agents
- Week 3: Integration testing, demo video, submission

## References
- GitHub: https://github.com/bnb-chain/bnbagent-sdk
- PyPI: https://pypi.org/project/bnbagent/
- Blog: https://www.bnbchain.org/en/blog/bnbagent-sdk-is-now-live-on-bnb-chain-mainnet
- Thread: https://x.com/BNBChainDevs/status/2064562778795557244
