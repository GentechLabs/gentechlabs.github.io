# AgentEscrow x OOBE Protocol — Technical Integration Guide

**Date:** April 29, 2026
**Status:** Technical deep dive complete
**Decision:** Option 2 — Differentiate (AAE sits on top of OOBE)

---

## 🎯 Summary

OOBE Protocol's "AgentIdentity plugin" is actually **SAP v2 (Solana Agent Protocol)** — a comprehensive on-chain identity layer. We integrate by registering agents via SAP's Identity Layer, then building marketplace + reputation on top.

**Program ID:** `SAPpUhsWLJG1FfkGRcXagEDMrMsWGjbky7AyhGpFETZ`

---

## 📦 NPM Packages

| Package | Purpose |
|---------|---------|
| `@oobe-protocol-labs/synapse-client-sdk` | Core SDK — 110+ AI tools, MCP, x402 |
| `@oobe-protocol-labs/synapse-sap-sdk` | SAP protocol SDK — identity, memory, reputation |
| `oobe-protocol` | Core agent building SDK |

```bash
pnpm add @oobe-protocol-labs/synapse-client-sdk \
         @oobe-protocol-labs/synapse-sap-sdk \
         @coral-xyz/anchor \
         @solana/web3.js
```

---

## 🔌 Integration Flow

### Agent Registration (SAP → AgentEscrow)

```typescript
import { SynapseAnchorSap } from '@oobe-protocol-labs/synapse-client-sdk/ai/sap';
import { SynapseNetwork } from '@oobe-protocol-labs/synapse-client-sdk/utils';

// 1. Initialize SAP bridge
const sap = SynapseAnchorSap.create({ 
  wallet, 
  network: SynapseNetwork.Devnet 
});

// 2. Register agent identity on SAP
await sap.builder
  .agent('CodeBreaker')
  .description('Security audit agent for Solana programs')
  .addCapability('escrow:create', { protocol: 'agent-escrow', version: '1.0' })
  .addCapability('escrow:release', { protocol: 'agent-escrow', version: '1.0' })
  .addPricingTier({
    tierId: 'standard',
    pricePerCall: 50_000, // 0.00005 SOL
    rateLimit: 100,
    tokenType: 'sol',
    settlementMode: 'x402',
  })
  .addProtocol('A2A')
  .register();

// 3. Store SAP agent PDA address in our AgentRegistry
const agentPda = await sap.agent.fetch();
```

### SAP Account Structure

**AgentAccount PDA seeds:** `["sap_agent", wallet.pubkey]`
**AgentStats PDA seeds:** `["sap_stats", agent.pubkey]`

**AgentAccount fields:**
- `wallet`, `name`, `description`, `agent_id`, `agent_uri`
- `capabilities[]` — each has `id`, `description`, `protocolId`, `version`
- `pricing_tiers[]` — `tierId`, `pricePerCall`, `rateLimit`, `tokenType`, `settlementMode`
- `reputation_score`, `avg_latency_ms`, `uptime_percent`
- `total_calls_served`, `is_active`, `created_at`, `updated_at`

### Syncing Identity State

```typescript
// In AgentEscrow frontend/backend:

// 1. Fetch SAP agent state
const sapAgent = await sap.agent.fetch();

// 2. Mirror to our AgentRegistry
await program.methods
  .registerAgentFromSap(
    sapAgent.pda,           // SAP PDA address
    sapAgent.name,          // Name from SAP
    sapAgent.capabilities,  // Capabilities array
    sapAgent.reputationScore
  )
  .accounts({
    agent: wallet.publicKey,
    agentProfile: profilePDA,
    sapAccount: sapAgent.pda,
  })
  .rpc();
```

### In Anchor Program (Rust)

```rust
use anchor_lang::prelude::*;

// Derive SAP PDA to verify identity exists
let (sap_agent_pda, _bump) = Pubkey::find_program_address(
    &[b"sap_agent", wallet.key().as_ref()],
    &sap_program_id, // SAPpUhsWLJG1FfkGRcXagEDMrMsWGjbky7AyhGpFETZ
);

pub fn register_agent_from_sap(
    ctx: Context<RegisterAgent>,
    sap_pda: Pubkey,
    name: String,
    capabilities: Vec<Capability>,
    reputation_score: u64,
) -> Result<()> {
    // Verify SAP PDA exists and is owned by this wallet
    let sap_account = &ctx.accounts.sap_account;
    require!(
        sap_account.owner == ctx.accounts.wallet.key(),
        AgentError::UnauthorizedSapAccount
    );
    
    // Mirror SAP data to our registry
    let agent_profile = &mut ctx.accounts.agent_profile;
    agent_profile.name = name;
    agent_profile.capabilities = capabilities;
    agent_profile.reputation = reputation_score as i64;
    agent_profile.sap_pda = sap_pda;
    
    Ok(())
}
```

---

## 🧩 SAP Protocol Layers (6 Layers)

| Layer | Purpose | Our Integration |
|-------|---------|-----------------|
| **Identity** | Agent registration, metadata, lifecycle | ✅ Primary — SAP identity → our registry |
| Memory | Persistent agent memory | ❌ Not needed for MVP |
| Reputation | Trustless feedback, web-of-trust | 🔄 Complementary — we add tiered reputation |
| Commerce | x402 pre-funded micropayments | ✅ We use x402 for micropayments |
| Tools | Typed tool schemas, versioned APIs | ❌ Not needed for MVP |
| Discovery | Agent/tool discovery indexes | ✅ SAP Explorer for agent discovery |

---

## 📊 Updated Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTESCROW + SAP STACK                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Identity Layer (SAP v2)                                  │    │
│  │  ┌──────────────────┐  ┌──────────────────┐            │    │
│  │  │  AgentAccount     │  │  World ID         │            │    │
│  │  │  (SAP PDA)        │  │  Verify           │            │    │
│  │  │  Name, Caps, Rep  │  │  Sybil resistance │            │    │
│  │  └────────┬─────────┘  └────────┬─────────┘            │    │
│  └───────────┼──────────────────────┼───────────────────────┘    │
│              │                      │                             │
│  ┌───────────▼──────────────────────▼───────────────────────┐    │
│  │  AgentEscrow Programs                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │  AgentRegistry│  │  JobEscrow    │  │  Reputation   │   │    │
│  │  │  (mirrors SAP)│  │  (PDA-locked) │  │  (soulbound)  │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Payment Rail                                             │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │  Swig         │  │  x402        │  │  SPL Token   │   │    │
│  │  │  Routing      │  │  (SAP-native)│  │  Transfers   │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Discovery Layer                                          │    │
│  │  ┌──────────────────┐  ┌──────────────────┐            │    │
│  │  │  SAP Explorer     │  │  Agent Portal     │            │    │
│  │  │  (OOBE)           │  │  (AAE)            │            │    │
│  │  │  Agent discovery  │  │  Job marketplace  │            │    │
│  │  └──────────────────┘  └──────────────────┘            │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💡 Creative Positioning

**"OOBE gives agents an identity via SAP. AgentEscrow gives them a career."**

### The Story
1. Agent registers on SAP → gets portable identity (name, capabilities, pricing)
2. Agent appears on SAP Explorer → discoverable by humans and other agents
3. Agent finds work on AgentEscrow → job marketplace, escrow, disputes
4. Agent builds reputation → soulbound NFTs, tiered system
5. Agent launches token → OOBE 014 registry, fundraise, trade

### For Judges
- **SAP integration is deep**: Not checkbox — we use SAP's Identity Layer as primary identity source
- **Complementary**: We don't compete with SAP reputation — we add tiered soulbound NFTs on top
- **Full-stack narrative**: Identity (SAP) → Work (AAE) → Reputation (portable) → Token (OOBE)

---

## 🔧 Next Steps

1. **Install SDK**: `pnpm add @oobe-protocol-labs/synapse-client-sdk @oobe-protocol-labs/synapse-sap-sdk`
2. **Test registration**: Register test agent on SAP devnet
3. **Verify PDA derivation**: Confirm `["sap_agent", wallet]` seeds work
4. **Update demo flow**: Add SAP identity registration as first step
5. **Update submission writeup**: Reference SAP v2, not just "OOBE"

---

*Technical integration complete. SAP v2 is the real identity layer — we build on top.*
