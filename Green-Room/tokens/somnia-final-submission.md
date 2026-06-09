# Somnia Agentathon — Final Submission Materials

## Project: TokenRiskOracle

## Short Description (for submission form)
An on-chain token risk scoring oracle built on Somnia's Agentic L1. Uses a dual-agent callback pattern: JSON API Agent fetches real-time security data from GoPlus API (honeypot checks, buy/sell tax, holder concentration, proxy status, mint capability), then LLM Inference Agent classifies the data into risk levels (safe/low_risk/moderate_risk/high_risk/scam) with a 0-100 numeric score. Agents execute autonomously on-chain — no human intervention required once triggered.

## Detailed Description
AI agents need to assess token risk before interacting with tokens on-chain. Currently, agents have no way to autonomously evaluate whether a token is safe. Humans use tools like DexScreener's token sniffer or GoPlus Security, but these are off-chain, manual processes.

TokenRiskOracle solves this by putting risk assessment on-chain using Somnia's dual-agent pattern:

**Phase 1 — JSON API Agent:** Fetches live security data from GoPlus API including honeypot detection, buy/sell tax analysis, holder concentration, proxy contract status, mint capability, and ownership verification.

**Phase 2 — LLM Inference Agent:** Receives the raw security data and classifies it into structured risk levels with a numeric confidence score. Returns: safe (0-20), low_risk (21-40), moderate_risk (41-60), high_risk (61-80), scam (81-100).

**Dual-Agent Callback Pattern:** Each agent phase triggers the next automatically. Contract requests analysis → Platform routes to JSON API agent → Data fetched → Platform routes to LLM agent → Classification complete → Result stored on-chain.

Built on Somnia's Agentic L1 (Chain ID 50312). Contract verified on Shannon Explorer.

## Key Technical Details
- **Chain:** Somnia Testnet (Chain ID 50312)
- **Contract:** 0x1171538ed34a0a3d82e23bcd2f1ccc438177fb42
- **Explorer:** https://shannon-explorer.somnia.network/address/0x1171538ed34a0a3d82e23bcd2f1ccc438177fb42
- **GitHub:** https://github.com/ProtoJay4789/somnia-agentic-examples
- **Agent IDs:**
  - JSON API Agent: 13174292974160097713
  - LLM Inference Agent: 12847293847561029384
- **Platform Contract:** 0x037Bb9C718F3f7fe5eCBDB0b600D607b52706776

## Architecture
```
Your Contract → Somnia Platform → Validators
     ↑              ↑                ↑
 TokenRisk    JSON API Agent    GoPlus API
 Oracle       (Phase 1)         Security Data
     ↑              ↑                ↑
              LLM Agent          AI Reasoning
              (Phase 2)         Classification
```

## Why This Matters
Agents can't tell if a token is safe. This gives agents an on-chain oracle that does the same thing humans do with DexScreener — but autonomously, with AI classification, and fully on-chain.

## Note on Network Limitation
E2E invocation is currently blocked on Somnia testnet with "AgentRequester: not enough active members." The contract is deployed and verified; the agent network needs more active validator nodes to fulfill requests. This is a network-level limitation, not a code issue. The contract compiles, deploys, and the invoke script is correctly structured for the dual-agent flow.

## Links
- GitHub: https://github.com/ProtoJay4789/somnia-agentic-examples
- Contract: https://shannon-explorer.somnia.network/address/0x1171538ed34a0a3d82e23bcd2f1ccc438177fb42
- Portfolio: https://protojay4789.github.io/
