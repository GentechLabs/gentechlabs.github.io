# Somnia Agentathon Runbook — Saturday Execution

**Deadline:** June 10, 2026 (Encode Club)
**Goal:** Testnet deploy → E2E test → demo → submit

## Pre-Flight Checklist (Do First)

### 1. Network Info
| Property | Value |
|----------|-------|
| Chain ID | 50312 |
| RPC | https://api.infra.testnet.somnia.network |
| Platform Contract | 0x037Bb9C718F3f7fe5eCBDB0b600D607b52706776 |
| Explorer | https://shannon-explorer.somnia.network |
| Faucet | https://agents.testnet.somnia.network (UI-only) |

### 2. STT Balance Check
```bash
# Check wallet balance on Somnia testnet
cast balance <YOUR_ADDRESS> --rpc-url https://api.infra.testnet.somnia.network
```
- **Need:** ≥0.30 STT per agent call (0.12 minimum + buffer)
- **Dual-agent needs:** ≥0.60 STT (two separate deposits)
- **If below:** Get from faucet — UI only, needs browser

### 3. Codebase Status
- **Location:** `/root/somnia-agentic-examples/`
- **Contracts:** 6 examples (PriceOracle, SentimentAnalyzer, WebDataExtractor, IdeaReview, DaoProposalReview, TokenRiskOracle)
- **Build status:** Compiled, artifacts exist, typechain-types generated
- **Git:** 5 commits, last update "solve Insufficient Balance"
- **Hardhat config:** somnia network configured (chain 50312)

---

## Phase 1: Fund Wallet (10 min)

### Faucet (Browser Required)
1. Navigate to https://agents.testnet.somnia.network/
2. Connect wallet (MetaMask with Somnia Testnet network)
3. Request STT from faucet
4. Verify balance:
```bash
cast balance <YOUR_ADDRESS> --rpc-url https://api.infra.testnet.somnia.network
```

**Add Somnia Testnet to MetaMask:**
- Network Name: Somnia Testnet
- RPC URL: https://api.infra.testnet.somnia.network
- Chain ID: 50312
- Currency: STT
- Block Explorer: https://shannon-explorer.somnia.network

**Fallback:** If faucet is slow/unavailable, try https://testnet.somnia.network/

---

## Phase 2: Deploy TokenRiskOracle (20 min)

The TokenRiskOracle is our best submission — dual-agent pattern (JSON API + LLM) shows the full power of Somnia's agent primitives.

### Step 1: Set Private Key
```bash
cd /root/somnia-agentic-examples
export PRIVATE_KEY=<your-private-key>
# Or add to .env file
echo "PRIVATE_KEY=<your-private-key>" > .env
```

### Step 2: Compile
```bash
npm run compile
# Verify: no errors, artifacts/ updated
```

### Step 3: Deploy
```bash
npm run deploy:risk-oracle
```

**Expected output:**
```
Deploying TokenRiskOracle...
Deployed to: 0x<contract-address>
Transaction: 0x<tx-hash>
```

**Save the contract address — needed for invoke script and demo.**

### Step 4: Verify Deployment
```bash
# Check contract on explorer
curl -s https://shannon-explorer.somnia.network/api?module=account&action=txlist&address=<contract-address> | python3 -m json.tool | head -20
```

---

## Phase 3: E2E Test (20 min)

### Step 1: Invoke the Oracle
```bash
# Update contract address in invoke script first
# Edit 06-token-risk-oracle/scripts/invoke.ts:
# const CONTRACT_ADDRESS = "0x<deployed-address>"

npm run invoke:risk-oracle -- <token-address-to-analyze>
```

**Test with a known token:**
- Use a well-known ERC-20 address (e.g., USDC on Ethereum: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48)
- The oracle will fetch GoPlus security data → LLM classification

### Step 2: Poll for Result
The invoke script polls for the callback event. Dual-agent flow:
1. Phase 1: JSON API fetches GoPlus security data (~10-30s)
2. Phase 2: LLM classifies risk level (~10-30s)
3. Total: ~60-120s

**Expected output:**
```
Result: {
  riskLevel: "low_risk",
  riskScore: 25n,
  status: "Passed"
}
```

### Error Recovery
- **Insufficient budget:** Set `SOMNIA_DEPOSIT_BUFFER_STT=0.30` and retry
- **Timeout (3 min):** Increase timeout in invoke script to 180s
- **No callback event:** Check explorer for transaction status, verify platform contract address

---

## Phase 4: Demo Recording (30 min)

### Demo Script (2-3 min)
```
[0:00-0:15] Hook
"AI agents need to assess risk before interacting with tokens. 
This is TokenRiskOracle — an on-chain agent that evaluates 
token security using real-time data and AI classification."

[0:15-0:45] Problem
"Right now, agents can't tell if a token is safe. 
Humans use DexScreener's token sniffer or GoPlus Security. 
This gives agents an on-chain oracle that does the same thing."

[0:45-1:45] Demo Walkthrough
1. Show the contract on Somnia explorer (deployed address)
2. Run invoke script — show the request being submitted
3. Show Phase 1: JSON API fetching GoPlus security data
   - Honeypot check, buy/sell tax, holder concentration
   - Proxy status, mint capability, ownership
4. Show Phase 2: LLM classifying the risk
   - Returns: safe / low_risk / moderate_risk / high_risk / scam
   - Plus a 0-100 numeric risk score
5. Show the final result on-chain

[1:45-2:15] Architecture
"Built on Somnia's Agentic L1. Two agent primitives chained:
JSON API Agent fetches real-time security data from GoPlus API.
LLM Inference Agent classifies the data into risk levels.
Dual-agent callback pattern — each phase triggers the next.
Deployed on Somnia Testnet, Chain ID 50312."

[2:15-2:30] Close
"TokenRiskOracle — agent-native risk assessment on Somnia. 
Code available at github.com/ProtoJay4789/somnia-agentic-examples."
```

### Recording Options
1. **Terminal recording:** Show the full invoke flow with timestamps
2. **Screen recording:** Terminal + explorer tabs side by side
3. **Hybrid:** Terminal output + architecture diagram overlay

---

## Phase 5: Encode Club Registration (Jordan's Browser)

1. Navigate to https://encodeclub.com/programmes/agentathon
2. Sign in (Discord)
3. **CRITICAL:** Complete "Join or Create a Project" step IMMEDIATELY
   - This is the checkpoint that locked us out of Kite AI
   - Do NOT skip this step
4. Verify project is created and submission slot is active

---

## Phase 6: Submission (15 min)

### Required Materials
- [ ] Contract deployed on Somnia Testnet (address saved)
- [ ] E2E test passed (result screenshot)
- [ ] Demo video (≤5 min)
- [ ] GitHub repo: https://github.com/ProtoJay4789/somnia-agentic-examples
- [ ] Encode Club project created

### Submission via Encode Club
1. Go to your project page on encodeclub.com
2. Submit:
   - Project description
   - Demo video
   - GitHub repo link
   - Contract address
   - Any additional notes

---

## Blockers & Escalations

| Blocker | Solution | Time |
|---------|----------|------|
| No STT in wallet | Faucet via browser | 5 min |
| Compilation error | Check ViaIR in hardhat.config.ts | 5 min |
| Deploy fails (no funds) | Fund wallet, retry | 2 min |
| Invoke timeout | Increase to 180s, retry | 2 min |
| Encode Club project locked | Jordan must create from browser | 5 min |
| LLM classification fails | Check deposit buffer (0.30 STT min) | 2 min |

---

## Quick Reference

- **STT needed:** ≥0.60 STT (dual-agent)
- **Platform contract:** 0x037Bb9C718F3f7fe5eCBDB0b607b52706776
- **Agent IDs:**
  - JSON API: 13174292974160097713
  - LLM Inference: 12847293847561029384
  - LLM Parse Website: 12875401142070969085
- **Deposit minimum:** getRequestDeposit() (~0.12 STT)
- **LLM buffer:** 0.30 STT recommended
- **Repo:** /root/somnia-agentic-examples/
- **Encode Club:** https://encodeclub.com/programmes/agentathon
- **Portfolio:** ProtoJay4789.github.io (update after deploy)

---

## Architecture Diagram (for demo overlay)

```
┌─────────────┐       ┌──────────────────┐       ┌────────────────┐
│Your Contract│──────►│ Somnia Platform  │──────►│   Validators   │
│             │       │                  │       │                │
│  TokenRisk  │◄──────│  JSON API Agent  │◄──────│  GoPlus API    │
│  Oracle     │       │  (Phase 1)       │       │  Security Data │
│             │       │                  │       │                │
│             │◄──────│  LLM Agent       │◄──────│  AI Reasoning  │
│             │       │  (Phase 2)       │       │  Classification│
└─────────────┘       └──────────────────┘       └────────────────┘
```
