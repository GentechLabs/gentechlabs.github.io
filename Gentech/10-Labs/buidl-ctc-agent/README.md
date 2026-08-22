# GenTech Verified Agent — BUIDL CTC 2026 Fall (Creditcoin)

**AI track submission:** *"AI apps on Creditcoin that process cryptographically verified
cross-chain data to autonomously inform decisions and trigger on-chain transactions
without centralized oracle operators."*

## The Idea

An autonomous AI DeFi agent that **only trusts cryptographically verified cross-chain
data** — never a centralized oracle. It generates a transaction **inclusion proof**
(Attestcoin Protocol), verifies it **on-chain** on Creditcoin, then makes a decision
and triggers an action. This is the GenTech "machine-money loop": verified cross-chain
events drive autonomous on-chain decisions.

## Why this wins

- **Core requirement met:** meaningful Attestcoin Protocol integration (the USC SDK's
  proof generation + on-chain verification is the *entire* trust model — no oracle).
- **Depth of integration = core scoring criteria:** we use the full stack —
  `PrecompileChainInfoProvider` (query supported chains), `ProofBuilder` (generate
  proof), `PrecompileBlockProver` (verify on-chain).
- **AI track fit:** autonomous decisioning from verified data, no centralized operator.
- **Reuses GenTech assets:** the DeFi-agent + x402 thesis maps directly.

## Stack

- **`@gluwa/usc-sdk`** (Attestcoin Protocol) — generate + verify cross-chain inclusion proofs
- **Creditcoin CC3 Testnet** — the settlement/verification chain (EVM-compatible)
- **ethers v6** — provider + wallet
- **Solidity** (`contracts/`) — Creditcoin on-chain action contracts

## Architecture

```
Source chain (Base/Sepolia)  Creditcoin CC3 Testnet
┌──────────────────────┐     ┌─────────────────────────────┐
│ USDC transfer (tx)   │     │                             │
└─────────┬────────────┘     │  ProofBuilder (hosted)      │
          │ inclusion proof  │    generates Merkle proof   │
          ▼                  └───────────┬─────────────────┘
   ProofBuilder (USC SDK)                │ proofData
          │                              ▼
          └──────────────►  PrecompileBlockProver.verifySingle()
                                              │ verified: true/false
                                              ▼
                                       decideAction()   ← AI layer
                                              │
                                              ▼
                                       Trigger on Creditcoin (contract)
```

## Run

```bash
cp .env.example .env        # fill SOURCE_RPC + AGENT_PRIVATE_KEY
node src/agent.mjs <sourceTxHash>
```

## Verify SDK integration (live testnet)

```bash
# Query supported source chains (proves USC SDK connects to CC3 testnet)
node -e "import('@gluwa/usc-sdk').then(async ({chainInfo}) => {
  const { JsonRpcProvider } = await import('ethers');
  const p = new JsonRpcProvider('https://rpc.cc3-testnet.creditcoin.network');
  const ci = new chainInfo.PrecompileChainInfoProvider(p);
  console.log(await ci.getSupportedChains());
})"
# → [{chainKey:3, chainId:1, Ethereum}, {chainKey:1, chainId:11155111, Sepolia}]
```

## Requirements met

- [x] Working Attestcoin Protocol integration code (USC SDK proof + verify) — **verified live on CC3 testnet** (getSupportedChains returns Ethereum + Sepolia)
- [x] Creditcoin action contract (`contracts/VerifiedRebalance.sol`) — **compiles + 4/4 tests pass** (records verified events, refuses unverified, triggers rebalance above threshold, owner-only)
- [x] Agent wired to trigger on-chain action (`src/agent.mjs` → `triggerOnChain`)
- [ ] Deployed on testnet (Creditcoin CC3 Testnet) — **HUMAN-GATED: fund throwaway key `0x72d4...E041` via Creditcoin Discord `/faucet`, then `npx hardhat run scripts/deploy.mjs --network cc3`**
- [ ] GitHub repo + README
- [ ] Project deck / whitepaper
- [ ] Prototype demo video

## Resources

- Attestcoin docs: https://docs.creditcoin.org/creditcoin-usc
- USC SDK: https://www.npmjs.com/package/@gluwa/usc-sdk
- Hackathon: https://dorahacks.io/hackathon/buidl-ctc-2026-fall
