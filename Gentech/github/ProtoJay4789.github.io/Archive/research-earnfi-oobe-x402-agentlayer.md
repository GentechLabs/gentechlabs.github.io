# EarnFi + OOBE + x402 + AgentLayer — Lobby UI Integration Research

**Date:** 2026-06-01
**Purpose:** Understand available APIs and patterns for GenTech Pals Lobby UI prototype (agent-to-human USDC micropayment matchmaking)

---

## 1. EarnFi API (Agent API — `ai-agent/v1`)

**Base URL:** `https://app.earnfi.fun/api/ai-agent/v1`
**Docs:** `https://docs.earnfi.fun`
**OpenAPI:** `https://app.earnfi.fun/openapi-x402.json`
**MCP:** `https://app.earnfi.fun/mcp`
**Well-known x402:** `https://app.earnfi.fun/.well-known/x402`
**TypeScript Client:** `npm install @earn-fi/agent-client`

### What EarnFi Is
A Solana marketplace for **micro jobs settled in USDC**. Agents (or humans) can post jobs for social engagement, manual tasks, contests, and interrupt-style Q&A. Workers complete tasks and get paid in USDC.

### Endpoints (all under `/api/ai-agent/v1`)

| Billing | Endpoint | Description |
|---------|----------|-------------|
| **Free** | `GET /catalog` | List job types, minimum rewards, suggested sizes |
| **Free** | `GET/POST /register/challenge` | Get Ed25519 message to sign for registration |
| **Free** | `POST /register` | Register agent → returns `agent_id` + `agent_token` |
| **402 probe** | `GET /x402` | Preview pricing (returns 402 with quote shape) |
| **Paid** | `GET/POST /jobs/social` | Create social job (likes, reposts, comments, follows, YouTube) |
| **Paid** | `GET/POST /jobs/manual` | Create custom manual job (briefs, labeling, review) |
| **Paid** | `GET/POST /jobs/contest` | Create contest with prize pool |
| **Paid** | `GET/POST /interrupt` | One question, many answers |
| **Free poll** | `GET /jobs/{id}?secret=...` | Get job status |
| **Free poll** | `GET /jobs/{id}/submissions?secret=...` | List worker submissions |
| **Free poll** | `GET /jobs/{id}/completions?secret=...` | List completed work |
| **Creator** | `GET /jobs/{id}/pause?agent_token=...` | Pause/resume job |
| **Creator** | `GET /jobs/{id}/verifications?agent_token=...` | List pending verifications |
| **Creator** | `GET /jobs/{id}/detail?agent_token=...` | Dashboard-style detail |
| **Creator** | `GET /jobs/{id}/payments?agent_token=...` | Payment history |
| **Creator** | `GET /jobs/{id}/contest/submissions?agent_token=...` | Contest submissions |
| **Creator** | `POST /jobs/{id}/contest/mark-winner?agent_token=...` | Mark contest winner |

### Registration Flow
```
1. GET /register/challenge?wallet_address=PUBKEY&agent_name=my-agent
   → returns { message, nonce, expires_at }
2. Sign `message` with Ed25519 (tweetnacl / nacl.sign.detached)
3. POST /register with { wallet_address, agent_name, message, signature, nonce }
   → returns { agent_id, agent_token }
```

### Job Creation Flow (x402 Paid)
```
1. GET /jobs/social?agent_token=TOKEN&task_type=like&slots=10&reward_per_user=0.05&execution_mode=human
   → 402 Payment Required with accepts[] and quote
2. Build Solana tx: SetComputeUnitLimit → SetComputeUnitPrice → TransferChecked (USDC)
3. Retry same request with header: PAYMENT-SIGNATURE: { signed_tx: "base64...", requirements: {...} }
   → 200 with { job_id, secret, status_url }
4. Poll with ?secret=SECRET (free, no USDC per read)
```

### Key Constraints
- x402 payment: ≤40,000 CU, ≤5 microLamports/CU
- SPL TransferChecked (USDC) from payer ATA → recipient ATA
- ATAs must exist before payment tx
- feePayer must be `accepts[0].extra.feePayer` (facilitator)
- Execution mode: currently **human-only**
- Token gate: requires 500K EARNFI tokens in agent wallet

### TypeScript Client API
```typescript
import { EarnFiAgentClient, EARNFI_DEFAULT_API_BASE } from '@earn-fi/agent-client';

const client = new EarnFiAgentClient({
  baseUrl: EARNFI_DEFAULT_API_BASE,
  agentToken: process.env.EARNFI_AGENT_TOKEN!,
  connection: new Connection(process.env.SOLANA_RPC_URL!),
  wallet: myWallet,
});

// Discovery
const catalog = await client.getCatalog();
const preview = await client.getX402Preview();

// Paid create
const job = await client.createSocialJob({
  taskType: 'like',
  slots: 10,
  rewardPerUser: '0.05',
});

// Polling
const status = await client.getJob(job.jobId);
const subs = await client.listSubmissions(job.jobId);
```

---

## 2. OOBE Protocol (On-Chain Agent Registry)

**Program ID:** `3GE2ac1UgJpmuXTUGruMXNq9UCjefch8GFrjVuuqGRJS`
**Location:** `/root/oobe-protocol/`
**Stack:** Anchor 0.30 on Solana

### What OOBE Is
A Solana on-chain **agent registry and reputation system**. It's the primitive for registering AI agents with capabilities, pricing, and a reputation score governed by an oracle.

### On-Chain Accounts

**Agent PDA** (seeds: `["agent", authority, name]`):
| Field | Type | Description |
|-------|------|-------------|
| authority | Pubkey | Owner wallet |
| agent_id | [u8; 32] | Unique identifier |
| name | String (≤64 chars) | Agent name |
| capabilities | Vec<String> (≤10, ≤32 chars each) | Skill tags |
| pricing_tier | PricingTier enum | Free / Premium / Enterprise |
| price_lamports | u64 | Price in lamports |
| reputation_score | u64 | Running score |
| reputation_count | u32 | Number of reputation updates |
| registered_at | i64 | Timestamp |
| updated_at | i64 | Timestamp |
| is_active | bool | Soft-delete flag |

**ReputationOracle PDA** (seeds: `["oracle"]`):
- Singleton; authority controls reputation updates

### Instructions
| Instruction | Description |
|-------------|-------------|
| `initialize_oracle` | Create oracle PDA (one-time) |
| `register_agent(name, capabilities, tier, price_lamports)` | Register new agent |
| `update_agent(name, capabilities?, tier?, price?)` | Update agent metadata |
| `update_reputation(score_add)` | Add reputation (oracle authority only) |
| `deactivate_agent(name)` | Soft-delete agent |
| `get_agent()` | View agent details |

### SDK Usage
```typescript
import { findAgentPda, registerAgent, getAgent, PricingTier } from './sdk/src/index';

// Register
await registerAgent(program, authority, "game-helper", ["strategy", "pvp"], PricingTier.Premium, new BN(1000000));

// Fetch
const agent = await getAgent(program, authority, "game-helper");
console.log("Reputation:", agent.reputationScore.toString());
```

### Lobby Integration Pattern
OOBE provides the **on-chain identity layer** for agents in the Lobby:
1. Each AI agent registers on-chain with name + capabilities (e.g., "pvp-teammate", "raid-healer")
2. Players can browse registered agents by capability
3. Reputation score tracks quality over time
4. Pricing tier gates access

---

## 3. x402 Protocol (HTTP 402 Micropayments)

**Spec:** `https://www.x402.org/x402-whitepaper.pdf`
**SDK:** `npm install @x402/fetch @x402/core @x402/svm`
**Python:** `pip install x402-solana`
**Solana Guide:** `https://solana.com/developers/guides/getstarted/intro-to-x402`

### What x402 Is
An open standard leveraging HTTP's reserved **402 "Payment Required"** status code to enable **instant, machine-native USDC micropayments** over HTTP. No API keys, no subscriptions — just pay-per-request.

### End-to-End Flow
```
1. Client makes request to protected endpoint
2. Server returns HTTP 402 with JSON body:
   { x402Version: 2, resource: {...}, accepts: [{ scheme: "exact", network: "solana:...", amount: "66000", payTo: "...", asset: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", extra: { feePayer: "...", tokenDecimals: 6 } }] }
3. Client builds Solana tx: SetComputeUnitLimit → SetComputeUnitPrice → TransferChecked (USDC)
4. Client retries request with header: PAYMENT-SIGNATURE: { signed_tx: "base64...", requirements: {...} }
5. Server verifies payment via facilitator, serves content
```

### Solana Payment Requirements
- Compute budget: ≤40,000 CU, ≤5 microLamports/CU
- Exactly 3 instructions: SetComputeUnitLimit, SetComputeUnitPrice, TransferChecked
- ATAs must exist before payment tx (no ATA creation in payment tx)
- feePayer must be facilitator's address (not sender's wallet)
- USDC mint: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`

### x402 Ecosystem Players
- **Circle** — Gateway batching for gasless settlement on Arc
- **Coinbase, Cloudflare, Google, MetaMask, Ethereum Foundation** — Backers
- **WURK.FUN** — Crypto-native microtask marketplace using x402
- **PayAI** — Payments infrastructure for the agent economy

---

## 4. AgentLayer Wallet Backend

**Package:** `@agentlayer.tech/wallet` (npm)
**GitHub:** `https://github.com/lopushok9/Agent-Layer`
**Docs:** `https://docs.agent-layer.tech/`
**Install:** `npx @agentlayer.tech/wallet install --yes`
**Hermes Install:** `npx @agentlayer.tech/wallet install --yes && npx @agentlayer.tech/wallet hermes install --yes`

### What AgentLayer Is
A **local-first wallet and finance stack for agents**. Keeps keys, approvals, and signing local. Supports OpenClaw, Hermes, and Codex as agent hosts.

### Architecture
- `agent-wallet/` — Main wallet backend (Python)
- `hermes/` — Hermes Agent plugin bridge
- `.openclaw/` — OpenClaw wallet integration
- `codex/` — Codex plugin bridge
- `wdk-btc-wallet/` — Bitcoin wallet service
- `wdk-evm-wallet/` — EVM wallet service
- `provider-gateway/` — Solana RPC, Bags, finance reads
- `mcp-server/` — Finance and crypto MCP layer

### x402 Integration (Built-In)
AgentLayer has **native x402 support** through its wallet tools:
- `x402_search_services` — Search x402-paid services (CDP Bazaar, Agentic Market)
- `x402_get_service_details` — Resolve service into normalized detail payload
- `x402_preview_request` — Unpaid request, detect 402, summarize payment terms
- `x402_pay_request` — Prepare or execute the paid retry through active wallet backend

### Other Wallet Capabilities
- **LI.FI** cross-chain routing (Solana ↔ Ethereum ↔ Base)
- **Jupiter** trading, swaps, and Earn vault flows
- **Houdini** private payouts (SOL→SOL, USDC→USDC)
- **Kamino** lending integration
- **BTC** wallet operations (balance, transfer, fee-rate)

### Security Model
- Keys stored locally in `~/.openclaw/sealed_keys.json`
- Boot key in runtime `.env` unlocks the sealed bundle
- Agents see constrained wallet tools (not raw key management)
- Approval-token checks before execution

---

## 5. Lobby UI Integration Strategy

### How These Pieces Fit Together for GenTech Pals

```
┌─────────────────────────────────────────────────────┐
│                    LOBBY UI                          │
│  Player browses AI agent teammates, pays USDC       │
│  to access premium agents for gaming sessions        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  OOBE Protocol│  │   EarnFi API │  │ AgentLayer │ │
│  │  (on-chain   │  │  (job/task   │  │  (wallet   │ │
│  │   registry + │  │   marketplace│  │   backend  │ │
│  │   reputation)│  │   + x402     │  │   + x402)  │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │           x402 Payment Layer                  │    │
│  │  USDC micropayments via HTTP 402              │    │
│  │  Solana SPL TransferChecked                   │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### Recommended Integration Steps

1. **Agent Registration (OOBE)**
   - Register each AI agent on-chain with capabilities: `["pvp-teammate", "raid-healer", "quest-guide"]`
   - Set pricing tiers (Free for basic, Premium for expert agents)
   - Track reputation over time via oracle updates

2. **Player-Agent Matching (EarnFi-style)**
   - Use EarnFi's `createManualJob` pattern: player pays USDC to access an agent for a session
   - Or use `createInterrupt` for quick one-question matches
   - Job flow: quote (402) → sign payment → retry → poll with secret

3. **Wallet Backend (AgentLayer)**
   - Install AgentLayer for local wallet management
   - Use built-in x402 tools for service discovery and payment
   - Keep agent keys local, expose constrained wallet surface

4. **Payment Flow (x402)**
   - Use `@x402/fetch` + `@x402/svm` for Solana USDC payments
   - Facilitator handles gas fees (gasless for player)
   - Sub-cent payments make per-interaction billing viable

### Key Dependencies
```json
{
  "@earn-fi/agent-client": "latest",
  "@x402/fetch": "latest",
  "@x402/core": "latest",
  "@x402/svm": "latest",
  "@solana/web3.js": "^1.18.0",
  "@solana/spl-token": "latest",
  "@coral-xyz/anchor": "^0.30.0",
  "@agentlayer.tech/wallet": "latest"
}
```

### What's Already Built Locally
- `/root/oobe-protocol/` — Full Anchor program + TypeScript SDK (built, tested)
- `/root/arc-nanopayments/` — x402 nanopayment demo with Circle Gateway (reference impl)
- `/root/sdk/` — Appears to be related to the arc-nanopayments demo

---

## 6. Existing Vault Research

Relevant files found in vault:
- `dmob-skills-smart-contract-x402-subscription-pricing-SKILL.md` — x402 subscription tier pricing model with blended cost analysis
- `kite-passport-agent-identity.md` — Agent identity patterns
- `t54-ai-trust-layer-agentic-economy.md` — Trust layer for agent commerce

The x402 subscription pricing skill already models:
- Blended cost across connectors (~$0.0011/request)
- Three tiers: Basic ($15/mo), Pro ($50/mo), Power ($150/mo)
- Overage rates as profit maximizer
- Break-even at 20-50 users
