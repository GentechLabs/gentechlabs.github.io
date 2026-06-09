# Mantle Sepolia Deploy Guide

## Prerequisites
1. **Mantle Sepolia ETH** — Get from faucet: https://faucet.sepolia.mantle.xyz
2. **Deployer wallet** — Private key with Sepolia ETH

## Deploy Steps

### 1. Set environment variables
```bash
export PRIVATE_KEY="0xYourPrivateKey"
export ORACLE_ADDRESS="0xYourAddress"  # Can be same as deployer for testing
```

### 2. Deploy contracts
```bash
cd /root/gentech/agent-economy-solana
export PATH="$HOME/.foundry/bin:$PATH"

FOUNDRY_PROFILE=mantle forge script script/DeployMantle.s.sol \
  --rpc-url https://rpc.sepolia.mantle.xyz \
  --broadcast \
  --verify \
  --etherscan-api-key "mantle"
```

### 3. Verify on explorer
After deploy, verify each contract on:
https://shannon-explorer.somnia.network/ (Somnia)
https://sepolia.mantlescan.xyz/ (Mantle)

### 4. Update submission
Copy contract addresses to SUBMISSION-DRAFT.md

### 5. Submit to DoraHacks
1. Go to https://dorahacks.io/hackathon/mantleturingtesthackathon2026
2. Connect wallet
3. Submit project with:
   - Name: Agent Economy Protocol (AEP)
   - Track: Agentic Wallets & Economy
   - Repository: https://github.com/ProtoJay4789/agent-economy-solana
   - Demo video: (create 2-min walkthrough)
   - Contract addresses from step 4

## Contract Addresses (after deploy)
- AgentRegistry: (paste here)
- JobEscrow: (paste here)
- AgentKeeper: (paste here)
- ERC8004Adapter: (paste here)

## Test Suite
```bash
forge test --summary
# Expected: 14 passed; 0 failed
```
