# GenLayer SDK Recon Brief for Dmob

## Context
GenLayer is an AI-powered L2 running "Intelligent Contracts" — Python contracts with native LLM calls + web access. They validated the thesis: AI agent staking/fee-sharing is real money. We're evaluating whether we can build a Kite/AAE layer on top of GenLayer and start earning revenue.

## What Dmob Needs to Map

### 1. SDK Architecture (genlayer-js)
- Repo: https://github.com/genlayerlabs/genlayer-js (v0.28.5, active)
- How the JS SDK interacts with Intelligent Contracts
- Deploy flow, state read/write, transaction lifecycle
- Staking interface (IGenLayerStaking already exists in ABI)

### 2. genlayer-studio (Local Sandbox)
- Repo: https://github.com/genlayerlabs/genlayer-studio (120 stars)
- Current limitations: no token transfers, no contract-to-contract, no gas
- Can we prototype an escrow/dispute contract here?
- What's the gap between studio and testnet/mainnet?

### 3. Boilerplate (Starting Point)
- Repo: https://github.com/genlayerlabs/genlayer-project-boilerplate (10.7k stars)
- This is the canonical project template — clone and build

### 4. Contract Development
- Contracts written in Python, run on GenVM (WASM, Rust)
- Native LLM integration (GPT-4, Llama, etc.)
- Web access without oracles
- Storage, error handling, upgradability patterns
- Fee mechanics — who pays, who earns, how much?

### 5. Revenue Mechanics
- Fee sharing: how are contract fees distributed?
- Validator staking economics (min stake, APY, slashing)
- Delegation mechanics (can users delegate to our validator?)
- Is there a "skill marketplace" revenue model? (Spoiler: probably not — the `genlayerlabs/skills` repo is a Claude Code plugin, not an agent revenue system)

### 6. Integration Feasibility for AAE/Kite
- L5 (Marketplace + Escrow): Strongest fit — GenLayer handles dispute resolution
- L4 (Enforcement/SLAs): "Did the agent do good work?" = subjective = AI consensus
- Can we wrap a Kite layer as an Intelligent Contract?
- What would the Solidity (AgentEscrow) → GenLayer bridge look like?

## Deliverables
- [ ] SDK architecture diagram
- [ ] Contract deployment walkthrough
- [ ] Fee/revenue mechanics breakdown
- [ ] Feasibility assessment: build on GenLayer vs. compete
- [ ] Recommended next step (prototype, validator setup, or pass)

## Resources
- Docs: https://docs.genlayer.com/
- Studio: https://studio.genlayer.com/contracts
- GitHub org: https://github.com/genlayerlabs
- Discord: https://discord.gg/8Jm4v89VAu
