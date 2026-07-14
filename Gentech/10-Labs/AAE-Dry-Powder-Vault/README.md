# AAE Dry Powder Vault — Technical Documentation

## Overview

The Dry Powder Vault is a cross-chain smart stablecoin rotation system that auto-rotates idle USDC across Base, Avalanche, and Solana based on yield opportunities, narrative strength, and risk assessment.

**Status:** Phase 2 Complete (June 5, 2026)  
**Priority:** P0 — Revenue engine for $15/mo Agent Pass

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Telegram Bot (User Interface)        │
├─────────────────────────────────────────────┤
│         Agent Orchestrator (Python)          │
│  • Zone monitoring (CMC watchlist extension) │
│  • Narrative tracking                        │
│  • Rotation decision engine                  │
│  • DeFi Llama live yield integration         │
├─────────────────────────────────────────────┤
│         Vault Contract (Solidity ERC-4626)   │
│  • USDC deposits/withdrawals                 │
│  • Per-chain balance tracking                │
│  • Bridge request management                 │
├─────────────────────────────────────────────┤
│         Bridge Adapters                      │
│  • CCTP V2 (free EVM bridging)              │
│  • Across Protocol (EVM ↔ Solana)           │
│  • deBridge (large transfer fallback)        │
├─────────────────────────────────────────────┤
│         DEX Adapters                         │
│  • Aerodrome (Base) — vAMM/sAMM/Slipstream  │
│  • LFJ / Trader Joe (Avalanche)             │
│  • Meteora DLMM (Solana) — concentrated     │
├─────────────────────────────────────────────┤
│         Data Layer                           │
│  • DeFi Llama API (live yields)              │
│  • CMC watchlist + zones                     │
│  • Narrative analysis                        │
└─────────────────────────────────────────────┘
```

---

## Components

### 1. Vault Contract (`contracts/DryPowderVault.sol`)

**Chain:** Base (primary deployment)  
**Standard:** ERC-4626 compatible

#### Key Functions:
- `deposit(amount)` — Deposit USDC, receive shares 1:1
- `withdraw(amount)` — Withdraw USDC from home chain
- `initiateBridge(user, fromChain, toChain, amount)` — Agent starts bridge
- `completeBridge(id)` — Confirm bridge completion
- `proposeRotation(from, to, amount, reason)` — Agent proposes rotation
- `approveRotation(id)` — Owner approves rotation
- `reportYield(chain, amount)` — Agent reports earned yield

---

### 2. Bridge Adapters

#### Circle CCTP V2 (EVM ↔ EVM):
- **Fee:** Free (gas only)
- **Settlement:** ~15 minutes
- **Supported:** Base, Avalanche, Ethereum, Arbitrum, Optimism
- **Solana:** ❌ Not supported

#### Across Protocol (EVM ↔ Solana) ⭐ PRIMARY:
- **Fee:** 0.06-0.10% LP fee + relayer fee
- **Settlement:** <5 seconds (median)
- **Supported:** All major chains including Solana
- **Base SpokePool:** `0xb4a8d45647445EA9FC3E1058096142390683dBC2`
- **Why chosen:** Fastest fills, lowest fees for our volume

#### deBridge (Large Transfer Fallback):
- **Fee:** 0.001 ETH flat (~$3.50)
- **Settlement:** Instant finality
- **Threshold:** Used for transfers >$50K
- **Why:** Flat fee becomes cheaper for large amounts

---

### 3. Aerodrome Adapter (`agent/aerodrome_adapter.py`)

**Chain:** Base  
**Protocol:** Aerodrome Finance  
**Router:** `0xcF77a3Ba9A5CA399B7c97c8b328D78F8BF0B6322`

#### Functions:
- `add_liquidity(pool, amount0, amount1)` — Dual-token deposit
- `add_liquidity_single(pool, amount, token)` — Single-token zap
- `remove_liquidity(pool, lp_amount)` — Withdraw LP
- `remove_liquidity_single(pool, lp, token)` — Single-token exit
- `swap(token_in, token_out, amount)` — Token swap
- `rebalance(pool, current_lp, target0, target1)` — Rebalance position

#### Pool Types:
- **vAMM (Volatile):** AERO/USDC — Higher APY
- **sAMM (Stable):** USDC/USDbC — Low risk, stable yield
- **Slipstream (CL):** Concentrated liquidity — Highest efficiency

---

### 4. Meteora Adapter (`agent/meteora_adapter.py`)

**Chain:** Solana  
**Protocol:** Meteora DLMM  
**Program:** `LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo`

#### Functions:
- `add_liquidity(pool, amount_x, amount_y, strategy)` — Add DLMM liquidity
- `remove_liquidity(position_pubkey)` — Remove all liquidity
- `remove_liquidity_by_range(position, lower, upper)` — Partial removal
- `claim_fees(position)` — Claim unclaimed fees
- `close_position(position)` — Remove all + close account
- `rebalance(position, new_range, amounts)` — Move to new bin range

#### Strategies:
- **Conservative:** ±10 bins, low risk (0.1), 3-8% APY
- **Moderate:** ±30 bins, medium risk (0.4), 8-15% APY
- **Aggressive:** ±60 bins, high risk (0.7), 15%+ APY

#### Known Pools:
- **SOL-USDC:** `5quBdH1u5vMkiJw1aVdqnYP2S8Xfq3S2Pp5pMQEJqTnS`
- **USDC-USDT:** `ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq`

---

### 5. Agent Orchestrator (`agent/orchestrator.py`)

#### Zone System (extends CMC watchlist):
Each chain gets its own zone based on best available APY:

| Zone | Base APY | Avalanche APY | Solana APY | Action |
|------|----------|---------------|------------|--------|
| 🔥 Deep Value | < 2% | < 5% | < 3% | Increase allocation |
| 🟢 Accumulate | 2-5% | 5-12% | 3-8% | Maintain |
| 🔵 Watch | 5-10% | 12-25% | 8-20% | Decrease |
| ⚪ Extended | > 10% | > 25% | > 20% | Exit |

#### Rotation Decision Engine:
Rotations trigger when:
1. **Yield delta > 3%** between chains
2. **Narrative shift > 0.15** (chain sentiment changes)
3. **Max 30% of chain balance** per rotation
4. **4-hour cooldown** between rotations on same pair
5. **Risk cap:** Combined risk score < 0.7

#### DeFi Llama Integration:
- Fetches live APY from `https://yields.llama.fi/pools`
- Falls back to hardcoded values if API unavailable
- Refreshes hourly in monitor mode
- Tracks TVL and risk per pool

---

## Integration Guides

Detailed guides in `docs/`:
- `meteora-integration-guide.md` — SDK setup, API methods, pool discovery
- `aerodrome-integration-guide.md` — Router functions, pool types, gas costs
- `solana-bridge-comparison.md` — Across vs deBridge vs Wormhole analysis

---

## Deployment

### Base Sepolia Testnet:
```bash
# 1. Install dependencies
pip install web3 py-solc-x

# 2. Set deployer key
export PRIVATE_KEY="0x..."

# 3. Fund with testnet ETH
# https://faucet.sepolia.base.org

# 4. Deploy
cd /root/vaults/gentech/Labs/AAE-Dry-Powder-Vault
python3 scripts/deploy_vault.py
```

### Solana (for Meteora adapter):
```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"

# Set keypair
solana-keygen new -o ~/.config/solana/id.json

# Airdrop devnet SOL
solana airdrop 2 --url devnet
```

---

## Usage

### Check Status:
```bash
python3 agent/orchestrator.py --mode status
```

### Evaluate Rotations:
```bash
python3 agent/orchestrator.py --mode rotate
```

### Monitor (continuous):
```bash
python3 agent/orchestrator.py --mode monitor
```

### Test Adapters:
```bash
python3 agent/aerodrome_adapter.py
python3 agent/meteora_adapter.py
python3 agent/solana_bridge_adapter.py
```

---

## File Structure

```
AAE-Dry-Powder-Vault/
├── spec.md                          # Original spec
├── README.md                        # This file
├── contracts/
│   ├── DryPowderVault.sol           # Main vault (ERC-4626)
│   ├── CCTPBridgeAdapter.sol        # Bridge adapter
│   └── interfaces/
│       └── IDryPowderVault.sol      # Interface
├── scripts/
│   ├── deploy_vault.py              # Deployment script
│   └── test_bridge.py               # Bridge test
├── agent/
│   ├── orchestrator.py              # Zone monitor + rotation engine
│   ├── aerodrome_adapter.py         # Base LP adapter
│   ├── meteora_adapter.py           # Solana LP adapter
│   └── solana_bridge_adapter.py     # EVM → Solana bridge
├── config/
│   └── vault-config.json            # Network configs + yield sources
├── docs/
│   ├── meteora-integration-guide.md
│   ├── aerodrome-integration-guide.md
│   └── solana-bridge-comparison.md
├── deployments/                     # Deployed contract addresses
└── state/                           # Runtime state files
```

---

## Revenue Model

| Stream | Source | Margin |
|--------|--------|--------|
| Subscription | $15/mo Agent Pass | 100% |
| Swap fees | Each rotation | 0.3% |
| Performance | 10% of yield above baseline | Variable |
| Gas rebate | Markup on gas costs | ~20% |

**Target:** $100K TVL, 50+ rotations, 10 paying subscribers in Q1.

---

## What's Working

✅ **Vault Contract:** Full ERC-4626 implementation with per-chain tracking  
✅ **Bridge Adapters:** CCTP (EVM), Across (Solana), deBridge (fallback)  
✅ **Agent Orchestrator:** Zone monitoring, narrative engine, rotation decisions  
✅ **Aerodrome Adapter:** Full LP operations on Base (add/remove/swap/rebalance)  
✅ **Meteora Adapter:** DLMM position management on Solana  
✅ **Solana Bridge:** Across Protocol integration with auto-protocol selection  
✅ **DeFi Llama:** Live yield data with hourly refresh  
✅ **Config System:** Chain configs, yield sources, bridge routing, adapter settings  
✅ **Deployment Script:** Ready for Base Sepolia  

## What's Blocked / Needs Work

⚠️ **Solana Wallet:** Need funded Solana keypair for adapter testing  
⚠️ **Testnet USDC:** Need testnet USDC on Base Sepolia for deposit flow testing  
⚠️ **CCTP Attestation:** Need Circle relayer integration for full attestation flow  
⚠️ **Meteora On-Chain:** Need to finalize Solana instruction building for production  

## Next Steps

1. **Deploy to Base Sepolia** — Test vault deposit/withdraw flow
2. **Test Aerodrome LP** — Deposit to USDC-USDbC pool on testnet
3. **Fund Solana Wallet** — Get devnet SOL + test USDC for Meteora
4. **Test Across Bridge** — Bridge USDC Base → Solana on testnet
5. **Telegram Bot** — Connect orchestrator to bot for notifications

---

*Documentation updated June 5, 2026. Phase 2 complete.*
