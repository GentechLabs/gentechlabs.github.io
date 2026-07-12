# Deployment Checklists — Mantle Turing Test & Arbitrum HackQuest

---

## 🟢 MANTLE TURING TEST — Deployment Checklist

**Deadline:** June 15, 2026 15:59 UTC
**Track:** Agentic Wallets & Economy
**Repo:** github.com/ProtoJay4789/mantle-turing-test

### 1. Wallet Funding (Mantle Sepolia)

- [ ] Export your deployer private key (or create a new one with `cast wallet new`)
- [ ] Get MNT testnet tokens from Mantle Sepolia faucet:
  - https://faucet.sepolia.mantle.xyz
  - Or via Alchemy faucet with Mantle Sepolia selected
- [ ] Verify balance: `cast balance <YOUR_ADDRESS> --rpc-url mantle-sepolia`
- [ ] **Need minimum ~0.5 MNT** for contract deployment + verification + frontend interaction

### 2. Configure Environment

- [ ] Set env vars in `.env`:
  ```
  PRIVATE_KEY=<deployer_private_key>
  MANTLE_SEPOLIA_RPC=https://rpc.sepolia.mantle.xyz
  MANTLESCAN_API_KEY=<get from mantlescan.xyz>
  ```
- [ ] If using `foundry.toml`, ensure RPC is set:
  ```toml
  [rpc_endpoints]
  mantle-sepolia = "https://rpc.sepolia.mantle.xyz"
  ```
- [ ] Install dependencies: `forge install && cd frontend && npm install`

### 3. Deploy Contracts (Foundry)

- [ ] Compile: `forge build`
- [ ] Run deploy script:
  ```bash
  forge script script/Deploy.s.sol \
    --rpc-url mantle-sepolia \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify
  ```
- [ ] **Alternative** (if verification needs separate step):
  ```bash
  forge script script/Deploy.s.sol \
    --rpc-url mantle-sepolia \
    --private-key $PRIVATE_KEY \
    --broadcast
  ```
- [ ] Record deployed contract addresses from broadcast output
- [ ] If `--verify` fails, verify manually:
  ```bash
  forge verify-contract <CONTRACT_ADDRESS> <CONTRACT_NAME> \
    --chain-id 5003 \
    --etherscan-api-key $MANTLESCAN_API_KEY
  ```

### 4. Verify on MantleScan

- [ ] Go to https://sepolia.mantlescan.xyz
- [ ] Search your contract address
- [ ] Confirm source code is verified (green checkmark)
- [ ] Test contract reads/writes from the explorer
- [ ] Save contract address and verification link

### 5. Update Frontend

- [ ] Update contract address in frontend config (e.g., `.env.local` or constants file):
  ```
  NEXT_PUBLIC_CONTRACT_ADDRESS=<deployed_address>
  NEXT_PUBLIC_CHAIN_ID=5003
  NEXT_PUBLIC_RPC_URL=https://rpc.sepolia.mantle.xyz
  ```
- [ ] Ensure frontend wallet connects to **Mantle Sepolia** (chainId 5003)
- [ ] Test end-to-end flow locally with Mantle Sepolia
- [ ] Build frontend: `cd frontend && npm run build`

### 6. Deploy Frontend

- [ ] Deploy to Vercel/Netlify/your host
- [ ] Set environment variables on hosting platform
- [ ] Verify frontend connects to wallet and interacts with contracts
- [ ] Test full flow: connect wallet → interact → confirm transaction on MantleScan

### 7. Submit to DoraHacks

- [ ] Go to https://dorahacks.io/hackathon/mantleturingtesthackathon2026
- [ ] Click "Submit Project" (or equivalent)
- [ ] Fill in:
  - [ ] Project name
  - [ ] One-line description
  - [ ] Detailed description (what it does, how it uses Mantle, agentic wallet/economy angle)
  - [ ] GitHub repo link: https://github.com/ProtoJay4789/mantle-turing-test
  - [ ] Demo video (3-5 min, show end-to-end flow)
  - [ ] Live demo URL (frontend)
  - [ ] Contract addresses on Mantle Sepolia
  - [ ] Team members
- [ ] Double-check submission before deadline

### 8. Post X/Twitter Thread

- [ ] Draft thread (5-8 tweets):
  1. Hook: What we built + why it matters for agentic wallets
  2. Problem statement
  3. Solution overview + architecture
  4. How it uses Mantle (low fees, EVM compat, etc.)
  5. Demo screenshot or GIF
  6. Technical deep-dive (contract design, key innovation)
  7. Links: repo, live demo, MantleScan
  8. CTA: Check it out on DoraHacks / Like & RT
- [ ] Include hashtags: #MantleTuringTest #Mantle #AgenticWallets #Web3
- [ ] Tag @MantleOfficial
- [ ] Post thread (ideally 24h+ before deadline for visibility)

### 9. Final Checks

- [ ] Contracts deployed and verified on Mantle Sepolia ✅
- [ ] Frontend live and functional ✅
- [ ] DoraHacks submission complete ✅
- [ ] X thread posted ✅
- [ ] All links working (repo, demo, explorer) ✅
- [ ] Demo video uploaded/embedded ✅

---

## 🔵 ARBITRUM HACKQUEST — Deployment Checklist

### 1. Wallet Funding (Arbitrum Sepolia)

- [ ] Export your deployer private key (or create a new one with `cast wallet new`)
- [ ] Get Sepolia ETH from a faucet:
  - https://sepoliafaucet.com
  - https://faucets.chain.link/sepolia
  - https://www.alchemy.com/faucets/ethereum-sepolia
- [ ] Bridge to Arbitrum Sepolia (if needed) via the Arbitrum bridge testnet:
  - https://bridge.arbitrum.io (select Sepolia)
- [ ] Or use Arbitrum Sepolia-specific faucet if available
- [ ] Verify balance: `cast balance <YOUR_ADDRESS> --rpc-url arbitrum-sepolia`
- [ ] **Need minimum ~0.01 Sepolia ETH** for deployment + verification

### 2. Configure Environment

- [ ] Set env vars in `.env`:
  ```
  PRIVATE_KEY=<deployer_private_key>
  ARBITRUM_SEPOLIA_RPC=https://sepolia-rollup.arbitrum.io/rpc
  ARBISCAN_API_KEY=<get from arbiscan.io>
  ```
- [ ] If using `foundry.toml`, ensure RPC is set:
  ```toml
  [rpc_endpoints]
  arbitrum-sepolia = "https://sepolia-rollup.arbitrum.io/rpc"
  ```
- [ ] Install dependencies: `forge install && cd frontend && npm install`

### 3. Deploy Contracts (Foundry)

- [ ] Compile: `forge build`
- [ ] Run deploy script:
  ```bash
  forge script script/Deploy.s.sol \
    --rpc-url arbitrum-sepolia \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify
  ```
- [ ] **Alternative** (if verification needs separate step):
  ```bash
  forge script script/Deploy.s.sol \
    --rpc-url arbitrum-sepolia \
    --private-key $PRIVATE_KEY \
    --broadcast
  ```
- [ ] Record deployed contract addresses from broadcast output
- [ ] If `--verify` fails, verify manually:
  ```bash
  forge verify-contract <CONTRACT_ADDRESS> <CONTRACT_NAME> \
    --chain-id 421614 \
    --etherscan-api-key $ARBISCAN_API_KEY
  ```

### 4. Verify on Arbiscan

- [ ] Go to https://sepolia.arbiscan.io
- [ ] Search your contract address
- [ ] Confirm source code is verified (green checkmark)
- [ ] Test contract reads/writes from the explorer
- [ ] Save contract address and verification link

### 5. Update Frontend

- [ ] Update contract address in frontend config:
  ```
  NEXT_PUBLIC_CONTRACT_ADDRESS=<deployed_address>
  NEXT_PUBLIC_CHAIN_ID=421614
  NEXT_PUBLIC_RPC_URL=https://sepolia-rollup.arbitrum.io/rpc
  ```
- [ ] Ensure frontend wallet connects to **Arbitrum Sepolia** (chainId 421614)
- [ ] Test end-to-end flow locally with Arbitrum Sepolia
- [ ] Build frontend: `cd frontend && npm run build`

### 6. Deploy Frontend

- [ ] Deploy to Vercel/Netlify/your host
- [ ] Set environment variables on hosting platform
- [ ] Verify frontend connects to wallet and interacts with contracts
- [ ] Test full flow: connect wallet → interact → confirm transaction on Arbiscan

### 7. Submit to HackQuest (DoraHacks)

- [ ] Go to https://dorahacks.io (find Arbitrum HackQuest hackathon)
- [ ] Click "Submit Project" (or equivalent)
- [ ] Fill in:
  - [ ] Project name
  - [ ] One-line description
  - [ ] Detailed description (what it does, how it leverages Arbitrum)
  - [ ] GitHub repo link
  - [ ] Demo video (3-5 min)
  - [ ] Live demo URL
  - [ ] Contract addresses on Arbitrum Sepolia
  - [ ] Team members
- [ ] Double-check submission before deadline

### 8. Post X/Twitter Thread

- [ ] Draft thread (5-8 tweets):
  1. Hook: What we built + why it matters
  2. Problem statement
  3. Solution overview + architecture
  4. How it leverages Arbitrum (fast, cheap L2)
  5. Demo screenshot or GIF
  6. Technical deep-dive
  7. Links: repo, live demo, Arbiscan
  8. CTA: Check it out / Like & RT
- [ ] Include hashtags: #Arbitrum #HackQuest #L2 #Web3
- [ ] Tag @arbitrum
- [ ] Post thread

### 9. Final Checks

- [ ] Contracts deployed and verified on Arbitrum Sepolia ✅
- [ ] Frontend live and functional ✅
- [ ] DoraHacks/HackQuest submission complete ✅
- [ ] X thread posted ✅
- [ ] All links working ✅
- [ ] Demo video uploaded/embedded ✅

---

## Quick Reference — RPC & Explorer URLs

| Network | Chain ID | RPC URL | Explorer |
|---------|----------|---------|----------|
| Mantle Sepolia | 5003 | `https://rpc.sepolia.mantle.xyz` | https://sepolia.mantlescan.xyz |
| Arbitrum Sepolia | 421614 | `https://sepolia-rollup.arbitrum.io/rpc` | https://sepolia.arbiscan.io |

## Quick Reference — Faucets

| Token | Faucet URL |
|-------|-----------|
| MNT (Mantle Sepolia) | https://faucet.sepolia.mantle.xyz |
| Sepolia ETH | https://sepoliafaucet.com |
| Sepolia ETH (Chainlink) | https://faucets.chain.link/sepolia |
