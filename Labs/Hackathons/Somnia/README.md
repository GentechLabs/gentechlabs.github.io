# Agent Catcher

On-chain token risk scoring powered by Somnia AI agents.

**Hackathon**: [Somnia Agentathon 2026](https://www.encodeclub.com/programmes/agentathon)
**Deadline**: June 11, 2026
**Network**: Somnia Testnet (Chain ID 50312)

## What It Does

Agent Catcher analyzes any ERC-20 token's security posture using Somnia's dual-agent pattern:

1. **JSON API Agent** fetches real-time security data from GoPlus Security API on-chain
2. **LLM Agent** classifies the risk level based on the fetched data
3. **Result** stored permanently on the Somnia blockchain

Risk levels: Safe (100) - Low Risk (75) - Moderate Risk (50) - High Risk (25) - Scam (0)

## Architecture

```
User Input ──► AgentCatcher.sol ──► JSON API Agent ──► GoPlus Security API
                                         │
                                         ▼
                                   LLM Agent ──► Risk Classification
                                         │
                                         ▼
                                   On-Chain Result + Frontend Display
```

## Tech Stack

- **Solidity 0.8.24** - Smart contract (viaIR enabled)
- **Hardhat + Viem** - Development framework
- **Somnia Agents** - JSON API Request + LLM Inference primitives
- **GoPlus Security API** - Token security data source
- **Vanilla HTML/CSS/JS** - Frontend dashboard

## Quick Start

### Prerequisites

- Node.js v18+
- Wallet with STT (Somnia Testnet Token) from [faucet](https://agents.testnet.somnia.network)

### Setup

```bash
npm install

# Set your private key
cp .env.example .env
# Edit .env with your PRIVATE_KEY
```

### Compile

```bash
npm run compile
```

### Deploy

```bash
npm run deploy:catcher
```

### Invoke

```bash
# After deployment, set the contract address:
export CATCHER_ADDRESS=0x...

# Analyze a token:
npm run invoke:catcher -- 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 1
# (UNI token on Ethereum)
```

## Contract Interface

### `requestAnalysis(string tokenAddress, uint256 chainId)`

Submit a token for risk analysis. Sends STT deposit for dual-agent execution.

### `getRequiredDeposit() -> uint256`

Returns the minimum STT deposit required per agent call.

### `requests(uint256 id) -> AnalysisRequest`

Query any analysis request by ID.

### Events

- `AnalysisRequested` - New analysis submitted
- `RiskScored` - Analysis complete with risk level and score
- `RequestFailed` - Analysis failed (API or LLM error)

## Frontend

Open `frontend/index.html` in a browser. The dashboard provides:

- Token address input with chain selector
- Quick-scan presets for well-known tokens
- Real-time risk visualization with score meter
- Dual-agent workflow explanation

## Dual-Agent Pattern

This project demonstrates Somnia's most powerful pattern - chaining agents:

```
Phase 1: JSON API Agent
  └── Fetches: GoPlus token security data
  └── Callback: handleDataFetched()

Phase 2: LLM Agent (triggered by Phase 1 callback)
  └── Receives: Raw API JSON data
  └── Classifies: Risk level from constrained set
  └── Callback: handleClassification()
```

The `agentRequestToAnalysis` mapping bridges Somnia's platform request IDs with our analysis request IDs across the two callback phases.

## Files

```
contracts/
  AgentCatcher.sol    # Main contract (dual-agent risk oracle)
  deploy.ts           # Deployment script
  invoke.ts           # Invocation script with polling
frontend/
  index.html          # Dashboard UI
hardhat.config.ts     # Network config (Somnia Testnet)
package.json
tsconfig.json
```

## License

MIT
