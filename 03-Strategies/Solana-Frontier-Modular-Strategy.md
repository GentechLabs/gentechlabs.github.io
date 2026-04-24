# Solana Frontier Hackathon — Modular Layer Strategy

**Owner:** YoYo (Strategies) + Dmob (Labs)
**Status:** Planning — Pre-Dev
**Deadline:** May 11, 2026
**Total Prize Pool:** $680,000+ sidetracks + main Colosseum prizes

---

## The "Ogre Strategy" 🧅

**Core idea:** Build one modular architecture, submit different layers to different sidetracks. Each layer is a standalone module that plugs into the whole.

```
┌─────────────────────────────────────────────────────────────────┐
│                    GENTECH AGENT ECONOMY                        │
│                    (Solana / Anchor)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Layer 5: Data Dashboard (GoldRush + Dune integration)  │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Layer 4: Macro Watch (external signals → on-chain)     │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Layer 3: Tokenomics Radar (on-chain analysis engine)   │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Layer 2: Agent Vault (capital + trade execution)       │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Layer 1: Agent NFT (ownership + lifecycle + marketplace)│  │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer → Sidetrack Mapping

### Layer 1: Agent NFT (Identity & Ownership)
**Sidetrack target:** *NFT / Marketplace tracks*
**What it is:** SPL token representing agent ownership. Lifecycle states, marketplace listing, performance history on-chain.

**Solana port from existing:**
- `AgentNFT.sol` → Rust/Anchor program
- ERC721 → Metaplex Core (compressed NFTs = cheaper)
- AgentState enum stays
- Marketplace functions stay

**Standalone value:** Without the vault or strategy layers, this is still a "buy/sell trading agents" marketplace.

---

### Layer 2: Agent Vault (Capital Management)
**Sidetrack targets:**
- **Build an Autonomous Onchain Agent using Zerion CLI** — $5,000 USDC
- **Agentic Engineering Grants (Superteam)** — ~200 USDG

**What it is:** PDA-based vault per agent. Holds SOL + SPL tokens. Agent can execute trades, owner controls deposits/withdrawals.

**Solana port from existing:**
- `AgentVault.sol` → Anchor program with PDAs
- Native SOL gas → SOL is native, no separate gas reserve needed
- Token trades via Jupiter aggregator (not raw DEX calls)
- Reentrancy → Solana doesn't have reentrancy by design (account model)

**Key difference from AVAX version:** Solana's account model means each vault is a PDA (Program Derived Address), not a standalone contract. Cheaper to create, easier to index.

**Standalone value:** "Autonomous agent that trades on-chain with user capital" — literally the Zerion sidetrack.

---

### Layer 3: Tokenomics Radar (Analysis Engine)
**Sidetrack target:** *Build with GoldRush (Covalent)* — $3,000 USDC

**What it is:** On-chain analysis program that:
- Reads token supply, holder distribution, emissions
- Calculates health scores
- Stores results on-chain (or in PDAs for cheap reads)
- Triggers alerts/flags

**Solana-specific advantages:**
- Token holder data via Solana SPL Token program (native, fast)
- Account ownership verification is native
- Can use Clockwork/Pyth for scheduled analysis

**GoldRush integration:** Use Covalent's GoldRush API for historical holder data and cross-chain signals (AVAX activity feeding Solana intelligence).

**Standalone value:** "On-chain token analysis engine" — useful for any DeFi protocol, not just agents.

---

### Layer 4: Macro Watch (External Signals)
**Sidetrack target:** *Signal/Oracle integration tracks* (if available)

**What it is:** Oracle-fed external data (Fed statements, ETF flows, geopolitical) that agents can read on-chain to inform decisions.

**Solana approach:**
- Switchboard oracles for price feeds
- Custom oracle for sentiment/macro data (off-chain compute → on-chain verification)
- Agent reads oracle before executing trades

**Standalone value:** "On-chain macro intelligence layer" — infrastructure other protocols can build on.

---

### Layer 5: Data Dashboard (Analytics)
**Sidetrack targets:**
- **Build with GoldRush (Covalent)** — $3,000 USDC
- **Dune Analytics Dashboard** — (if sidetrack exists)

**What it is:** Web dashboard showing:
- Agent performance (fees earned, PnL, rebalances)
- Vault health (balances, gas usage)
- Tokenomics scores over time
- Community sentiment trends

**Tech stack:** Next.js frontend, GoldRush/Dune APIs for data, Solana RPC for live state.

**Standalone value:** "Glassnode for agent trading" — analytics dashboard that works even without the full system.

---

## Existing Codebase → Solana Translation Map

| AVAX (Solidity) | Solana (Anchor) | Notes |
|---|---|---|
| `AgentNFT.sol` (ERC721) | `agent_nft` program (Metaplex Core) | Compressed NFTs = 100x cheaper |
| `AgentVault.sol` | `agent_vault` program (PDA per agent) | No reentrancy concern, SOL native |
| `SafeERC20` | SPL Token CPI | Native token program |
| `Ownable` | PDA seeds + authority checks | Different model |
| Trade execution (raw calls) | Jupiter CPI | Best aggregator on Solana |
| `AgentState` enum | Same enum in Anchor | 1:1 port |
| Events | Anchor events | Same concept |

---

## Recommended Submission Order (Priority)

### 🥇 Must-Submit (High alignment, existing code can port)
1. **Agent Vault + Zerion CLI** — $5,000 — AgentVault port + Zerion CLI integration
2. **Agent NFT Marketplace** — AgentNFT port, Metaplex Core
3. **GoldRush Data Layer** — $3,000 — Covalent API integration into vault

### 🥈 Nice-to-Have (Extra work but high value)
4. **Agentic Engineering Grant** — ~200 USDG — Low prize, but signals ecosystem participation
5. **Tokenomics Radar** — On-chain analysis as standalone module
6. **Dune Dashboard** — If sidetrack exists, easy frontend work

### 🥉 Stretch Goals
7. **Macro Oracle Layer** — Custom oracle infrastructure
8. **Full Stack Integration** — All layers combined as one submission

---

## Dev Workflow — Making It Modular

### Architecture Principles
1. **Each layer is its own Anchor program** — deploy independently
2. **Shared types in a `common` crate** — AgentState, AgentType, etc.
3. **CPI between layers** — Vault calls NFT to verify ownership, Radar calls Vault to read balances
4. **Each layer has its own tests** — `anchor test` works per-layer
5. **One repo, multiple program directories:**

```
gentech-solana/
├── programs/
│   ├── agent-nft/          # Layer 1
│   ├── agent-vault/        # Layer 2
│   ├── tokenomics-radar/   # Layer 3
│   ├── macro-oracle/       # Layer 4
│   └── common/             # Shared types
├── app/                    # Layer 5 (Next.js dashboard)
├── tests/
│   ├── nft/
│   ├── vault/
│   ├── radar/
│   └── integration/
├── scripts/
│   ├── deploy.sh
│   └── initialize.sh
└── Anchor.toml
```

### Submission Workflow Per Sidetrack
1. Fork the layer(s) relevant to that sidetrack
2. Add sidetrack-specific README + demo
3. Record video demo per layer
4. Submit to Colosseum + Superteam Earn

---

## Dependencies & Blockers

| Item | Status | Owner |
|---|---|---|
| Solana dev environment | ❌ Not set up | Dmob |
| Anchor framework | ❌ Not installed | Dmob |
| Rust toolchain | ❌ Not installed | Dmob |
| Metaplex Core docs review | ❌ Pending | YoYo + Dmob |
| Jupiter CPI integration | ❌ Pending | Dmob |
| Covalent GoldRush API key | ❌ Pending | YoYo |
| Zerion CLI research | ❌ Pending | YoYo |
| Colosseum account + submission | ❌ Pending | Jordan |

---

## Risk Assessment

### Bear Case
- Rust/Anchor learning curve eats deadline time (23 days)
- Only one developer (Dmob) — single point of failure
- Sidetrack requirements may change or add constraints
- Competition is fierce (Solana-native teams)

### Bull Case
- Existing Solidity contracts = logic is proven, "just" porting
- Modular approach = partial wins (submit what's ready)
- Agent narrative is hot (AI + DeFi = narrative premium)
- Jordan's real LP experience = authentic origin story
- $680K+ prize pool = even partial wins meaningful

### Mitigations
- Start with Layer 2 (Vault) — it's the core, everything else depends on it
- Parallel work: Dmob builds Anchor, YoYo researches integrations
- If Rust blocks, pivot to existing Solidity + AVAX subnet focus
- Submit to multiple sidetracks with what's ready, not what's perfect

---

## Next Steps

1. **YoYo:** Research Zerion CLI requirements + Covalent GoldRush API
2. **Dmob:** Set up Solana dev environment (rustup, solana-cli, anchor)
3. **Dmob:** Port `AgentVault.sol` → `agent_vault` Anchor program (Layer 2 first)
4. **Dmob + YoYo:** Review Metaplex Core for NFT layer
5. **Jordan:** Create Colosseum account, review sidetrack exact requirements
6. **All:** Weekly sync on progress (deadline May 11)

---

## References

- Existing contracts: `/root/repos/agent-escrow/src/` (Solidity)
- AAE Premium spec: `03-Strategies/AAE-Premium-Product-Spec.md`
- Superteam Earn: [Frontier sidetracks page]
- Colosseum: [Main hackathon page]
- Anchor book: https://www.anchor-lang.com/
- Metaplex Core: https://developers.metaplex.com/core
- Jupiter API: https://station.jup.ag/
