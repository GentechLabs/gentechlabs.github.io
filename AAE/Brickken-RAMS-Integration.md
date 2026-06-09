---
title: Brickken RAMS (ERC-8226) Integration Assessment
created: 2026-05-31
status: active
tier: Tier 1 — Immediate
tags: [AAE, compliance, ERC-8226, ERC-8004, tokenization, RWA]
---

# Brickken — RAMS (ERC-8226) Integration Assessment

## Who They Are

**Brickken** (brickken.com) — Barcelona-based, founded 2020, 30+ team members, 15 nationalities.
- Enterprise tokenization platform: $450M+ in tokenized assets
- Raised €2.4M seed (Jan 2025), valuation >$22.5M
- BKN utility token on Ethereum (contract: `0x0a638f07acc6969abf392bb009f216d22adea36d`)
- Chains: Ethereum, Polygon, BSC, Base, **Taiko L2** (newest, June 2026)

## ERC-8226: Regulated Agent Mandate Standard (RAMS)

**Status:** Draft EIP (April 2026) | **PR:** ethereum/ERCs#1679
**Authors:** Ludovico Rossi, Dario Lo Buglio, Thamer Dridi, Nabil El Alami Khalifi (all @Brickken)

### What It Solves
AI agents can execute transactions, but regulated finance needs to know **who authorized them**. RAMS is a machine-readable power-of-attorney for autonomous agents on tokenized regulated assets.

### Architecture — Two Contracts

| Contract | Role | Deployed By |
|----------|------|-------------|
| `IComplianceProvider` | Verifies principal eligibility (KYC/AML) | Compliance operator |
| `IAgentMandate` | Mandate lifecycle, execution recording, freeze, views | RAMS registry |

### Key Data Structures

**Mandate:**
- `principal` — verified human/entity address
- `identityRef` — off-chain identity reference (DID/attestation hash)
- `scopeHash` — keccak256 of off-chain JSON scope document (IPFS)
- `complianceProvider` — address of `IComplianceProvider`
- `onChainScope` — MandateScopeParams (maxTxValue, maxCumulativeValue, assetAddress, jurisdiction)
- `validFrom` / `validUntil` — time bounds
- `cumulativeUsed` — running total of token units used
- `revoked` — boolean

**Critical:** Each `agentId` has **at most ONE active mandate** — enforces account segregation per MiCA Art. 70, MiFID II Art. 16, VARA.

### Delegation Flow
1. **Grant** — `grantMandate()` — principal delegates scoped, time-bounded, financially-capped authority
2. **Extend** — `extendMandate()` — extends validity, does NOT reset cumulativeUsed
3. **Revoke** — `revokeMandate()` — callable by principal or approved operator
4. **Operators** — `setOperator()` — approve revocation/extension but NOT grant (asymmetric)

### Compliance Check at Transfer Time
1. Token resolves wallet → agentId (via ERC-8004 registry)
2. Token resolves principal via `ramsRegistry.getActivePrincipal(agentId)`
3. Token's own compliance check on principal (`canSend`/`canReceive`)
4. RAMS mandate validity (`isActiveForAmount`)
5. Asset-specific check if mandate specifies token address
6. Records execution via `recordExecution()`

Agents use **standard ERC-20/721/1155 transfers** — no agent-specific transfer functions needed.

### Freeze System
- `PLATFORM` tier — freeze/unfreeze per jurisdiction
- `REGULATORY` tier — per jurisdiction + global freeze (global = regulatory only)

### Scope Document (Off-chain, IPFS)
JSON with type `urn:eip:RAMS:scope:v1`:
- `actions` — delegated actions (buy, sell, etc.)
- `assetClasses`, `tokenAddress`, `maxTransactionValue`, `maxCumulativeValue`
- `jurisdictions` — ISO 3166-1 alpha-2 codes
- `complianceProviderRef`

## The Agent Stack (Three-Layer Model)

| Layer | Standard | Responsibility |
|-------|----------|----------------|
| **Agent Identity** | ERC-8004 | Agent exists and is registered |
| **Mandate Compliance** | ERC-8226 (RAMS) | Agent has authority from principal for scope |
| **Token Compliance** | ERC-7943 (uRWA) / ERC-3643 (T-REX) | Who may hold/transact this asset |

### How This Maps to Our Stack

```
AAE Identity Layer     = ERC-8004 (agent registration, reputation)
AAE Authority Layer    = ERC-8226/RAMS (compliance delegation)
AAE Payment Layer      = x402 (micropayments, settlement)
AAE Commerce Layer     = AAE (marketplace, discovery, trust)
```

## Integration Opportunities

### Tier 1 — Immediate (Build Now)
1. **ERC-8226 SDK/Reference Implementation** — First-mover advantage building the tooling layer that makes RAMS easy to adopt. No one has built this yet.
2. **AAE + RAMS Integration** — When an agent in AAE gets a mandate, it auto-registers in RAMS. Compliance checks happen at transfer time.
3. **Contact Brickken** — They're actively partnering (Assetera, Credefi, Taiko). Our AAE + their RAMS = complete agent commerce stack.

### Tier 2 — Strategic (Next Quarter)
4. **Polymesh Grants** — Purpose-built for regulated assets, active grants program. Build agent compliance modules.
5. **ERC-3643 (T-REX) Overlay** — $32B in tokenized assets use T-REX. Agent authority on top = massive addressable market.
6. **Chainlink ACE Integration** — Agent mandate verification for cross-chain regulated transfers.

### Tier 3 — Monitor
7. **IXS Finance** — Building "agent-ready tokenized vaults" + agentic API. Competitor or partner?
8. **Know Your Agent (KYA)** — a16z flagged as critical. Research paper opportunity.
9. **CredexAI** — Verifiable credentials for agents. Complementary or competing?

## Competitors
- **IXS Finance** — Regulated AI agentic RWA settlement layer. 2026 roadmap includes agent-ready vaults.
- **CredexAI** — Verifiable credentials + gateway enforcement for agents.
- **Verifiable (CredAgent)** — Autonomous credentialing agent.

## Partnerships & Grants
- **Polymesh** — Active grants for regulated asset developers
- **Taiko** — Brickken deployed on Taiko L2, ecosystem grants available
- **AlphaGrowth** — Brickken RFPs via alphagrowth.io/brickken/grants-rfps
- **Brickken Community DAO** — v0.1, BKN staking at 15% yearly yield

## Key Files
- ERC-8226 Spec: github.com/ethereum/ERCs/pull/1679
- ERC-8004 Spec: ethereum-magicians.org
- Brickken Docs: docs.brickken.com
- Brickken GitHub: github.com/Brickken (8 repos)
- Brickken API V2: REST API with API key auth

## Next Steps
1. Read the full ERC-8226 spec on GitHub
2. Draft partnership outreach to Brickken (Ludovico Rossi on X: @Ludovico__Rossi)
3. Build proof-of-concept: AAE agent with RAMS mandate on testnet
4. Explore Polymesh grants for agent compliance modules
5. Save to Green Room for active development planning
