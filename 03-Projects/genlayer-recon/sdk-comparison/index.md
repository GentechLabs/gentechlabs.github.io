# SDK Comparison — Eat the Meat, Spit Out the Bones

## TL;DR for Jordan

| SDK | What It Actually Does | Fit for AgentEscrow | Verdict |
|-----|----------------------|---------------------|---------|
| **genlayer-js** | Deploy & interact with AI-powered contracts | ✅ Strong — escrow/dispute layer | **USE** |
| **genlayer-py** | Same, but Python | ⚠️ Alternative if JS blocks | **BACKUP** |
| **genlayer-studio** | Local sandbox for testing | ✅ Prototype here first | **USE** |
| **push-chain-sdk** | Cross-chain app deployment | ❌ Pivot product, not relevant | **SKIP** |

---

## 1. GenLayer SDK Stack

### genlayer-js (TypeScript) — PRIMARY
- **Repo**: https://github.com/genlayerlabs/genlayer-js
- **Version**: v0.28.5 (Apr 14, 2026) — active
- **Stars**: 50 | **Forks**: 8 | **Branches**: 63
- **Language**: TypeScript
- **What it does**: Frontend/DApp SDK for deploying and interacting with Intelligent Contracts
- **Key modules**:
  - `src/` — Core SDK (contract deployment, state read/write, transactions)
  - `docs/api-references/` — API documentation
  - `tests/` — Test suite
  - Staking ABI: `IGenLayerStaking` (v0.5) — validator staking interface built-in
- **Why it matters**: This is how we'd deploy a Kite escrow contract on GenLayer
- **Meat**: Active development, staking interface exists, TypeScript-friendly
- **Bones**: Only 50 stars, small community, docs sparse outside main site

### genlayer-py (Python) — BACKUP
- **Repo**: https://github.com/genlayerlabs/genlayer-py
- **Stars**: 32 | **Forks**: 2
- **Language**: Python
- **What it does**: Server-side Python SDK for Intelligent Contract interaction
- **Meat**: Contracts are written in Python, so native Python SDK makes sense
- **Bones**: Tiny community, minimal activity

### genlayer-studio (Local Sandbox) — PROTOTYPE
- **Repo**: https://github.com/genlayerlabs/genlayer-studio
- **Stars**: 120 | **Forks**: 45
- **Language**: Python
- **What it does**: Interactive sandbox for testing Intelligent Contracts locally
- **Limitations** (as of Apr 2026):
  - ❌ No token transfers
  - ❌ No contract-to-contract interactions
  - ❌ No gas consumption
- **Meat**: Best place to prototype an escrow/dispute contract before testnet
- **Bones**: Can't test revenue mechanics until those features land

### genvm (WASM VM) — DEEP CUT
- **Repo**: https://github.com/genlayerlabs/genvm
- **Stars**: 16 | **Forks**: 7
- **Language**: Rust
- **What it does**: WASM-based virtual machine for running Intelligent Contracts
- **Meat**: Understanding GenVM helps us know what our Python contracts can/can't do
- **Bones**: Deep internal, not directly usable — Dmob should read, not build on

### genlayer-project-boilerplate — START HERE
- **Repo**: https://github.com/genlayerlabs/genlayer-project-boilerplate
- **Stars**: 10.7k | **Forks**: 544
- **Language**: TypeScript
- **What it does**: Pre-configured project template for building on GenLayer
- **Meat**: This is the canonical starting point — clone and go
- **Bones**: None — this is the entry point

---

## 2. Push Chain SDK — SPIT OUT

### push-chain-sdk
- **Repo**: https://github.com/pushchain/push-chain-sdk
- **Version**: 177 tags, 103 branches — heavily versioned
- **Stars**: 13 | **Forks**: 9
- **Language**: TypeScript (monorepo)
- **What it does**: Universal blockchain SDK — deploy once, reach users on any chain (Ethereum, Solana, etc.)
- **⚠️ CRITICAL**: Push Protocol has completely pivoted from their original notification product ("Beams") to Push Chain. The old notification SDK is gone.

### What Push Chain actually does:
- Cross-chain universal app deployment
- Universal signer abstraction (connect any wallet, any chain)
- UI Kit for React apps
- Smart account management
- It's a **chain**, not a notification layer anymore

### Why we should skip:
- **Wrong problem**: Push Chain solves cross-chain fragmentation, not AI agent trust
- **No notification SDK**: The "Beams" notification product we looked at is deprecated
- **Low traction**: 13 stars vs GenLayer's 10.7k on their boilerplate
- **Different thesis**: We need trust/consensus infrastructure, not cross-chain deployment

### One bone worth keeping:
- The `llms.txt` file they publish (https://push.org/llms.txt) — shows they're building for AI agent discoverability. Worth noting that other chains are optimizing for AI agents now.

---

## 3. SDK Architecture Comparison

| Feature | genlayer-js | push-chain-sdk |
|---------|-------------|----------------|
| **Purpose** | AI consensus contracts | Cross-chain deployment |
| **Contract language** | Python | Solidity (EVM) |
| **AI/LLM native** | ✅ Built-in | ❌ |
| **Web access in contracts** | ✅ Native | ❌ (needs oracles) |
| **Staking built-in** | ✅ IGenLayerStaking | ❌ |
| **Token transfers** | ❌ (studio limitation) | ✅ |
| **Community** | Growing (10.7k boilerplate stars) | Small (13 stars) |
| **For AgentEscrow** | ✅ Direct fit | ❌ Wrong problem |

---

## 4. Recommended SDK Path for AgentEscrow

```
Prototype → Build → Deploy
   ↓          ↓        ↓
genlayer-  genlayer- genlayer-
 studio     js        mainnet
 (local)    (dApp)    (prod)
```

1. **Prototype**: Clone `genlayer-studio`, write Python escrow contract locally
2. **Build**: Use `genlayer-js` + boilerplate to build frontend/dApp
3. **Deploy**: Push to testnet → mainnet when features land

---

## 5. What Dmob Should Focus On

1. **Clone the boilerplate** — 10.7k stars, proven starting point
2. **Test genlayer-studio** — can we write a basic escrow contract?
3. **Map IGenLayerStaking** — how does validator staking work in the ABI?
4. **Check contract limitations** — what can Python contracts actually do on GenVM?
5. **Ignore Push Chain** — wrong problem, wrong product, wrong time
