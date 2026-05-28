# Somnia Agentathon — Checkpoint 2 Submission

## Project: TokenRiskOracle

### What We Built
An on-chain token risk scoring oracle that uses Somnia's dual-agent pattern to evaluate token security in real-time. The oracle chains two agent primitives:
1. **JSON API Agent** — fetches live security data from GoPlus API (honeypot checks, buy/sell tax, holder concentration, proxy status, mint capability)
2. **LLM Inference Agent** — classifies the data into risk levels (safe / low_risk / moderate_risk / high_risk / scam) with a 0-100 numeric score

### The Process
1. Designed a dual-agent callback pattern where each phase triggers the next
2. Deployed Solidity contracts on Somnia Testnet (Chain ID 50312)
3. Integrated GoPlus Security API for real-time token data
4. Built invoke scripts for on-chain execution
5. Created comprehensive error recovery (insufficient balance, timeout, callback failures)

### What's Working
- ✅ Contract compiled and deployed on Somnia Testnet
- ✅ Address: 0x1171538ed34a0a3d82e23bcd2f1ccc438177fb42
- ✅ Explorer verified: https://shannon-explorer.somnia.network/address/0x1171538ed34a0a3d82e23bcd2f1ccc438177fb42
- ✅ 6 contract examples built (PriceOracle, SentimentAnalyzer, WebDataExtractor, IdeaReview, DaoProposalReview, TokenRiskOracle)
- ✅ Hardhat test suite passing
- ✅ Typechain-types generated

### Current Status
E2E invoke is blocked on Somnia testnet network capacity — "AgentRequester: not enough active members." The contract is deployed and verified; the agent network needs more active nodes to fulfill requests.

### Code
GitHub: https://github.com/ProtoJay4789/somnia-agentic-examples

### Architecture
```
Your Contract → Somnia Platform → Validators
     ↑              ↑                ↑
 TokenRisk    JSON API Agent    GoPlus API
 Oracle       (Phase 1)         Security Data
     ↑              ↑                ↑
              LLM Agent          AI Reasoning
              (Phase 2)         Classification
```

### Key Agent IDs
- JSON API: 13174292974160097713
- LLM Inference: 12847293847561029384
- Platform Contract: 0x037Bb9C718F3f7fe5eCBDB0b600D607b52706776

### Why This Matters
Agents can't tell if a token is safe. Humans use DexScreener's token sniffer or GoPlus Security. This gives agents an on-chain oracle that does the same thing — autonomously, with AI classification.

### Demo
Recording pending — terminal output of the invoke flow with timestamp.

### Presentation
Slides pending — architecture diagram + flow walkthrough.
