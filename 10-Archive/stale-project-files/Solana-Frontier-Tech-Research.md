# Solana Frontier — Technical Integration Research

**Date:** Apr 18, 2026
**Owner:** YoYo (research) → Dmob (implementation)

---

## 1. Zerion CLI — $5K Sidetrack

### What Zerion Is
- DeFi portfolio management platform
- Provides API/CLI for programmatic portfolio queries, swap quotes, and trade execution
- Multi-chain support including Solana

### Architecture Pattern
```
Off-chain Agent (Rust/TS)  ──uses──▶  Zerion API/CLI (data + quotes)
       │
       │ submits signed txns
       ▼
Anchor Program (agent_vault)
       │ holds capital, validates agent authority
       │ CPIs to DEX (Jupiter)
       ▼
Solana DEX Programs
```

**Key insight:** Zerion runs off-chain. The Anchor program holds capital and enforces rules on-chain. The agent uses Zerion for data, then calls your program to execute.

### Key Zerion API Endpoints
| Endpoint | Purpose |
|---|---|
| `GET /v1/wallets/{addr}/portfolio` | Portfolio overview |
| `GET /v1/wallets/{addr}/positions` | DeFi positions |
| `GET /v1/prices/{token}` | Token prices |
| Swaps/quotes endpoints | Trade execution routing |

### Integration Steps
1. Get Zerion API key from developer portal
2. Off-chain agent queries portfolio/positions via Zerion
3. Agent makes decision → signs transaction → calls `execute_trade` on Anchor vault
4. Vault validates agent authority → CPI to Jupiter → trade executes

### ⚠️ Verify Exact Requirements
Web tools were down during research. **Manually check** `https://earn.superteam.fun` for the exact Zerion sidetrack listing, submission criteria, and any specific requirements about using the CLI vs API.

---

## 2. Covalent GoldRush — $3K Sidetrack

### What It Is
- Unified REST API across 200+ blockchains (including Solana)
- Indexed data: balances, transactions, transfers, NFTs, DEX pools, DeFi positions
- **Free tier:** 100K credits/month, no credit card required

### Key Endpoints for Our Project

| Endpoint | Use Case |
|---|---|
| `GET /{chain}/address/{addr}/balances_v2/` | Token holder snapshots |
| `GET /{chain}/address/{addr}/transfers_v2/` | Whale movement detection |
| `GET /{chain}/address/{addr}/portfolio_v2/` | Historical value charts |
| `GET /{chain}/address/{addr}/transactions_v2/` | Activity feed |
| `GET /{chain}/xy=k/` | DEX liquidity pool data |

### Solana Support
- Chain ID: `solana-mainnet`
- Full support for SPL tokens, NFTs, DEX data

### Integration Pattern
- **Cannot call GoldRush from on-chain programs** (no HTTP in Solana programs)
- Use in off-chain backend/frontend for the dashboard and analytics
- Layer 3 (Tokenomics Radar): GoldRush feeds data → analysis engine → writes scores on-chain
- Layer 5 (Dashboard): GoldRush API → Next.js frontend

### Quick Start
```bash
# Sign up at goldrush.dev → get API key
curl "https://api.covalenthq.com/v1/solana-mainnet/address/{WALLET}/balances_v2/?key={API_KEY}"
```

### GoldRush UI Kit
They offer pre-built React components (`@covalenthq/ui-kit`) for rapid dashboard prototyping — drop-in charts for hackathon demo.

---

## 3. Metaplex Core — NFT Layer

### Core vs Token Metadata

| Aspect | Token Metadata (legacy) | Metaplex Core (new) |
|---|---|---|
| Accounts per NFT | 4 (Mint + Token + Metadata + Edition) | **1 (Asset)** |
| Cost | ~0.004 SOL | **~0.0005 SOL** regular, **~0.000005 SOL** compressed |
| Custom on-chain data | Frozen after mint | **Attributes plugin** (mutable) |
| Compression | Bubblegum wrapper | **Native** |

**Verdict:** Use Metaplex Core. Cheaper, simpler, better for our use case.

### Anchor Dependencies
```toml
[dependencies]
anchor-lang = "0.30.1"
anchor-spl = "0.30.1"
mpl-core = { version = "0.7", features = ["anchor"] }
```

### Agent Metadata Storage
**Option A (Preferred): Attributes Plugin** — stores key-value pairs directly in the Asset account:
- `state`: active/paused/closing/closed
- `performance_score`: 0-10000
- `total_earnings`: cumulative
- `agent_type`: lp_manager/leverage/yield/arb/custom
- All mutable by authority via `UpdatePluginV1` CPI

**Option B: Companion PDA** — only if data exceeds ~64KB (match history arrays, etc.)

### Architecture
```
AgentNFT Anchor Program
├── create_agent() ──CPI──▶ mpl-core CreateV2
│   └── Asset account with Attributes plugin
├── update_stats() ──CPI──▶ mpl-core UpdatePluginV1
│   └── Mutate Attributes
├── list_for_sale() ──▶ Create Listing PDA
└── buy() ──CPI──▶ mpl-core TransferV1
    └── Close Listing PDA + SOL to seller
```

### Marketplace Support
- **Tensor** — full Core support
- **Magic Eden** — Core API support
- Build custom marketplace program with Listing PDA + TransferV1 CPI

---

## 4. Jupiter Integration — Trade Execution

All agent trades should route through Jupiter aggregator:
- Best swap routes across all Solana DEXes
- CPI-ready: Jupiter program can be called from Anchor programs
- API: `https://quote-api.jup.ag/v6/quote` for quotes
- API: `https://quote-api.jup.ag/v6/swap` for swap transactions

### Pattern
1. Off-chain agent gets quote from Jupiter API
2. Agent builds swap transaction
3. Agent calls Anchor vault's `execute_trade` with Jupiter calldata
4. Vault validates + CPIs to Jupiter → trade executes

---

## Action Items

### Immediate (Dmob)
- [ ] Set up Rust + Solana CLI + Anchor
- [ ] Create `gentech-solana` repo with program structure
- [ ] Start with `agent_vault` program (Layer 2)
- [ ] Port AgentVault.sol logic → Anchor PDA architecture

### Immediate (YoYo)
- [ ] Get Zerion API key
- [ ] Get GoldRush API key (free tier)
- [ ] Verify exact sidetrack requirements on earn.superteam.fun

### Before May 11
- [ ] Working `agent_vault` with Jupiter CPI
- [ ] Working `agent_nft` with Metaplex Core
- [ ] GoldRush integration in dashboard
- [ ] Video demos per sidetrack
- [ ] Submissions to Colosseum + Superteam Earn
