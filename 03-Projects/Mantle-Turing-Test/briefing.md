# Mantle Turing Test Hackathon 2026

## Event Details
- **Host**: Mantle + Bybit + BGA, supported by DoraHacks and HackQuest
- **Co-hosts**: Tencent Cloud, Byreal, Blockchain for Good Alliance (BGA)
- **Prize Pool**: $120K total (Grand: $50K)
- **Platform**: DoraHacks — dorahacks.io/hackathon/mantleturingtesthackathon2026
- **Phase 2 Deadline**: June 15, 2026
- **Event Period**: May 1 – June 16, 2026
- **Registration**: Free via Eventbrite (still open as of May 13)
- **Announced**: April 22, 2026

## Tracks (Phase 2 — "AI Awakening")
1. AI Trading & Strategy
2. AI Alpha & Data
3. AI × RWA
4. Consumer & Viral DApps
5. AI DevTools
6. **Agentic Wallets & Economy** ← Our target

## Agentic Wallets & Economy Track
- Build agentic wallet economies using Byreal Skills CLI and RealClaw
- Agents get an ERC-8004 Identity NFT on Mantle Network
- Every agent action is logged on-chain
- Judging: On-chain performance metrics (ROI, Sharpe ratio, reputation score delta)

## ERC-8004 Identity NFT Standard
- **What**: On-chain identity, discoverability, and reputation for AI agents
- **Created by**: Marco De Rossi (MetaMask), Davide Crapis (Ethereum Foundation), Jordan Ellis (Google), Erik Reppel (Coinbase)
- **Three registries**: Identity (ERC-721), Reputation (signed feedback), Validation (attestation hooks)
- **Does NOT handle payments** — that's application layer

### Mantle Deployment Addresses
| Network | Contract | Address |
|---------|----------|---------|
| Mantle Mainnet | IdentityRegistry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Mantle Mainnet | ReputationRegistry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Mantle Testnet | IdentityRegistry | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| Mantle Testnet | ReputationRegistry | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |

### How to Register an Agent
1. Call `register()` or `register(agentURI)` on IdentityRegistry
2. Mints ERC-721 NFT with auto-incremented `agentId`
3. Set `agentURI` pointing to JSON metadata (name, services, endpoints)
4. Optionally verify wallet via EIP-712 signature

### Key Resources
- GitHub: github.com/erc-8004/erc-8004-contracts (217 stars, CC0 license)
- NPM: `@nirholas/erc-8004-contracts`, `@spectratools/erc8004-cli`
- MCP: `@quantulabs/8004-mcp` for multi-chain registry access
- Spec: eips.ethereum.org/EIPS/eip-8004
- Site: 8004.org/build

## Sponsor Tools

### Byreal Skills CLI
- Solana-native CLMM DEX tool (`@byreal-io/byreal-cli` v0.3.6)
- 7 core skills: Copy Farming, Pool Analysis, Token Discovery, Swap Execution, Position Management, Wallet Management, xStocks Points
- All commands support JSON output (`-o json`)
- **Important**: Public CLI is Solana-only. Mantle EVM integration likely via RealClaw.

### RealClaw
- Byreal's AI agent trading platform (Telegram bot)
- Built on **OpenClaw** framework (github.com/openclaw/openclaw)
- **Multi-chain: Solana + Mantle** (confirmed in docs)
- Non-custodial wallet via Privy split-key
- Features: Stablecoin Farm, TradFi DCA, Crypto DCA, Copy Farm, Idle Yield, LP Limit Orders, Swap
- Beta: 2,000+ users, free during beta (2,000 credits/$20 included)
- Integration path: OpenClaw → Byreal Agent Skills → RealClaw → On-chain execution

## Chain: Mantle Network
- EVM-compatible (Solidity, standard Foundry/Hardhat tooling)
- ERC-8004 standard for agent identity
- DeFi protocols: Merchant Moe, Agni Finance, Fluxion
- Mantle Super Portal bridges MNT between Ethereum and Solana

## Existing Reusable Code

### Base Choice: agent-economy-solana (SELECTED)
**Location**: `/root/gentech/agent-economy-solana/`

| Aspect | Detail |
|--------|--------|
| Contracts | 9 Solidity files (5 contracts + 4 interfaces) |
| Tests | ✅ 14 passing |
| Architecture | Modular 5-layer |
| Access Control | OpenZeppelin RBAC (ADMIN, ORACLE, ARBITRATOR roles) |
| ReentrancyGuard | ✅ |
| Custom Errors | ✅ gas efficient |

**Contracts:**
- `AgentRegistry.sol` — Agent identity + reputation (0-10000 scale)
- `JobEscrow.sol` — Payment escrow with dispute resolution
- `AgentKeeper.sol` — Autonomous execution triggers (conditions → actions)
- `ZerionAdapter.sol` — Portfolio risk detection
- `GoldRushAdapter.sol` — Covalent GoldRush analytics
- 4 interfaces: IAgentRegistry, IJobEscrow, IAgentKeeper, IAdapter

**Why this over AgentForge:** AgentForge has 1 contract (241 lines), 10 tests, no RBAC, no dispute resolution, no adapters. agent-economy-solana is production-grade architecture.

### Why NOT AgentForge
- `/root/agentforge/` — Single monolithic contract, too simple for $120K hackathon
- Keep for reference but don't use as base

## Open Questions
- What specific judging criteria for Agentic Wallets track beyond ROI/Sharpe?
- Is there a Mantle-specific Byreal CLI for Phase 2, or only through RealClaw?
- Team size limits? (DoraHacks CAPTCHA blocked full rules)
- Can we use existing code or must be new?

## Portability Checklist (agent-economy-solana → Mantle)
1. **Contracts**: Zero Solidity changes needed — all pure EVM
2. **foundry.toml**: Add Mantle profile with `eth_rpc_url` and `chain_id`
3. **Frontend**: Update CHAIN_ID to Mantle, update contract addresses after deploy
4. **Agent worker**: Update RPC URL to Mantle
5. **ERC-8004 integration**: Call `register()` on Mantle IdentityRegistry to get agent NFTs
6. **Tests**: Run with `FOUNDRY_PROFILE=mantle forge test`

## Timeline
- May 13: Jordan exploring, registration confirmed open
- May 13-15: Briefing + base assessment ← WE ARE HERE
- May 15-20: Scaffold on agent-economy-solana, add ERC-8004 integration
- May 20-Jun 10: Build + test on Mantle testnet
- Jun 15: Phase 2 submission deadline

## Research Sources
- Press release: chainwire.org, prnewswire.com
- Byreal docs: docs.byreal.io
- ERC-8004 spec: github.com/erc-8004/erc-8004-contracts
- Eventbrite: eventbrite.com/e/the-turing-test-hackathon-2026-tickets-1988149115524
