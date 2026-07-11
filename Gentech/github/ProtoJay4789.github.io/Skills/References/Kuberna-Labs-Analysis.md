# Kuberna Labs — Reference Architecture Analysis

> **Repository**: https://github.com/kawacukennedy/kuberna-labs
> **Tagline**: "The Operating System for Agentic Web3 Enterprises"
> **Analyzed**: April 16, 2026
> **Context**: Reference architecture for Gentech's agent orchestration platform

---

## Executive Summary

Kuberna Labs is a Web3 infrastructure platform for deploying and managing AI agents with TEE-secured execution, cross-chain intent resolution, and on-chain reputation. It's a well-structured TypeScript monorepo with EVM + Solana smart contracts, a Node.js backend, Next.js frontend, and a TypeScript SDK. The project is relatively young (created March 2026, 37 stars) but architecturally comprehensive.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Next.js     │  │  CLI Tool   │  │  TypeScript │         │
│  │  Frontend    │  │  (planned)  │  │  SDK        │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND SERVICES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Express API  │  │ TEE Service  │  │ Blockchain   │       │
│  │ (REST+JWT)   │  │ (Phala/Marlin│  │ Listener     │       │
│  └──────────────┘  └──────────────┘  │ (WebSocket)  │       │
│                                      └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ zkTLS Service│  │ Chain Adapter│  │ Payment      │       │
│  │ (Reclaim/    │  │ (Multi-chain)│  │ Service      │       │
│  │  zkPass)     │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ PostgreSQL   │  │ Redis Cache  │  │ NATS Message │       │
│  │ (Prisma ORM) │  │              │  │ Broker       │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                SMART CONTRACTS (Multi-chain)                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ EVM (Solidity/Hardhat): Escrow, Intent, Attestation,│    │
│  │ ReputationNFT, AgentRegistry, Payment, CrossChain   │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ Solana (Anchor/Rust): Agent, Intent, Escrow,        │    │
│  │ Payment, Subscription, Governance, Certificate       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. TEE-Shielded Agent Deployment

### What They Built

**`backend/src/services/tee.ts`** — Core TEE deployment service supporting two providers:

- **Phala Network** (Intel TDX)
- **Marlin Oyster** (AMD SEV-SNP)

**Deployment Flow:**
1. Validate agent exists and isn't already running
2. Package agent code + config as base64-encoded JSON
3. Call provider API (Phala or Marlin) to deploy to enclave
4. Poll for valid attestation (max 10 attempts, 5s intervals)
5. Submit attestation to on-chain `Attestation` contract
6. Store deployment record in Prisma DB
7. Initiate health monitoring

**Key Interfaces:**
```typescript
interface TEEDeploymentRequest {
  agentId: string;
  ownerId: string;
  code: string;
  config: TEEDeploymentConfig;
  provider: 'phala' | 'marlin';
  resources: { cpu: number; memory: number; storage: number };
}

interface AttestationReport {
  quote: string;
  mrenclave: string;
  mrsigner: string;
  timestamp: number;
  signature: string;
  isValid: boolean;
}
```

**Attestation Verification:** Signature validation + MRENCLAVE hash check + timestamp freshness (24hr window). Then submitted on-chain via EAS-style attestation contract.

### Relevance to Gentech

- **Useful pattern**: The provider abstraction (Phala/Marlin) with unified interface is clean
- **Useful pattern**: On-chain attestation storage makes agent provenance verifiable
- **Limitation**: Deployment packaging is simplistic (base64 JSON) — not container-based
- **Limitation**: Attestation verification is mostly stubbed (signature check just validates non-empty strings)

---

## 2. Cross-Chain Intents & zkTLS

### Intent System (ERC-7683 style)

**Solidity `contracts/Intent.sol`:**
- Intent lifecycle: `Open → Bidding → Assigned → Executing → Completed`
- Structured data field for cross-chain swap parameters (sourceToken, destToken, amounts)
- Solver bidding with route details and estimated time
- Bid retraction and intent cancellation
- Integration with escrow for fund management

**Solana `contracts/solana_contracts/programs/src/intent.rs`:**
- Anchor-based implementation mirroring EVM structure
- PDAs with seeds `["intent", intent_id]` for deterministic accounts
- Bid management with status tracking

### zkTLS Service

**`backend/src/services/ztls.ts`:**
- Integrates **Reclaim Protocol** and **zkPass** for zero-knowledge proof of Web2 data
- Supports: bank_balance, kyc_status, credit_score, twitter_verified, email_verified
- Session-based flow: create session → user authenticates → proof verified → credential stored
- Supported sources: Bank of America, Chase, Coinbase, Twitter/X, Gmail, Credit Karma

### Relevance to Gentech

- **Directly applicable**: The intent/bidding pattern maps to Gentech's Agency platform where security auditors bid on audit tasks
- **Useful**: zkTLS for verifying auditor credentials (KYC, LinkedIn, GitHub) without exposing raw data
- **Adaptation needed**: Their intent system is DeFi-focused (swap amounts, tokens) — Gentech needs task-focused intents (audit scope, deadline, budget)

---

## 3. Deployment Pipeline

### Current State

- **Sub-60-second claim** is aspirational — actual deployment is fairly manual
- **Docker**: Multi-stage Dockerfile (build → production) with non-root user, health checks
- **CI/CD**: GitHub Actions workflow (`deploy.yml`) triggered on version tags:
  - `deploy-contracts`: Hardhat deploy to Sepolia + Etherscan verification
  - `publish-sdk`: Build and publish `@kuberna/sdk` to NPM
  - `deploy-backend`: Build backend (deployment target unspecified)
  - `deploy-frontend`: Vercel deployment
  - `create-release`: GitHub Release after all jobs succeed
- **Docker Compose**: Full stack — PostgreSQL, Redis, NATS, backend, Grafana, Prometheus

### Relevance to Gentech

- **Good reference**: The multi-stage CI pipeline (contracts → SDK → backend → frontend) with GitHub Releases
- **Docker pattern**: Clean production Dockerfile with health checks
- **Gap**: No actual sub-60-second pipeline exists — it's a marketing claim, not yet implemented
- **Gap**: No Kubernetes/Helm configs, no blue-green deployment

---

## 4. Smart Contract Architecture

### EVM Contracts (Solidity/Hardhat)

| Contract | Purpose | Key Features |
|----------|---------|--------------|
| `KubernaEscrow` | Fund management | Auto-release after 24hr, dispute resolution, fee (250 bps) |
| `KubernaIntent` | Cross-chain intents | Bidding, structured data, deadline enforcement |
| `AgentRegistry` | Agent registration (ERC-721) | NFT-based, tool tracking, status management |
| `Attestation` | TEE verification | Schema-based, expiration, revocation |
| `ReputationNFT` | Agent trust scores | Success rate, badges, time decay |
| `CrossChainRouter` | Multi-chain messaging | Token mapping, bridge fees |
| `Payment` | Multi-token payments | Batch support, fee management |
| `Subscription` | SaaS model | Plan management, grace periods |

### Solana Contracts (Anchor/Rust)

Located in `contracts/solana_contracts/programs/src/`:
- `agent.rs` — Agent registration with framework/tools tracking
- `intent.rs` — Intent/bidding system with PDAs
- `escrow.rs` — Token escrow with SPL token vaults
- `lib.rs` — Consolidated program with all modules (certificate, payment, subscription, dispute, treasury, fee manager, workshop, governance, reputation, attestation, cross-chain router)

**Pattern**: PDA-based account derivation with seeds like `["agent", owner.key()]` — clean and deterministic.

### Relevance to Gentech

- **Escrow pattern**: The 2.5% fee + auto-release + dispute resolution is a solid reference for Agency platform payment flows
- **Agent registry as ERC-721**: Interesting idea — makes agents tradeable/transferable
- **Solana Anchor patterns**: The PDA usage and account space calculation (`INIT_SPACE`) are good reference for any Solana work
- **Gap**: No Agent-to-Agent interaction contracts (relevant for multi-agent orchestration)

---

## 5. SDK Architecture

**`sdk/src/index.ts`:**
```typescript
class KubernaSDK {
  agent: AgentManager;      // CRUD + deploy + start/stop
  intent: IntentManager;    // Create/list/cancel intents
  blockchain: BlockchainManager; // Balance + transactions
}
```

- Clean manager pattern with SDK delegating to sub-managers
- API key auth via `X-API-KEY` header
- Ethers.js provider + optional wallet for on-chain operations
- Zod for validation (imported but lightly used)

### Relevance to Gentech

- **Good pattern**: The SDK-as-a-wrapper-around-API approach is solid
- **Adaptation**: Gentech's SDK should expose multi-agent orchestration primitives, not just single-agent lifecycle

---

## 6. Backend Architecture

**Stack**: Express + Prisma + PostgreSQL + Redis + NATS

**Key Services:**
- `tee.ts` — TEE deployment (Phala/Marlin)
- `ztls.ts` — Zero-knowledge Web2 proofs
- `chains.ts` — Multi-chain adapters (Ethereum/Uniswap, Solana, NEAR, Polygon, Arbitrum)
- `blockchainListener.ts` — WebSocket event monitoring with NATS pub/sub, exponential backoff reconnection
- `payment.ts` — Escrow funding, release, refunds
- `ai.ts` — AI service integration (details minimal)

**Prisma Schema Highlights:**
- `Agent` model with deployment type (CLOUD/TEE/LOCAL), JSON config, tools array
- `Intent` model with cross-chain fields (sourceChain, destChain, sourceToken, destToken)
- `Bid` model linking agents to intents
- `Task` model tracking execution status
- `Reputation` model with success rate tracking
- Roles: ADMIN, INSTRUCTOR, LEARNER, REQUESTER, SOLVER

### Relevance to Gentech

- **Agent model**: The `config: Json`, `tools: String[]`, `deploymentType` pattern is directly reusable
- **Blockchain listener**: WebSocket + NATS + exponential backoff is a solid pattern for any blockchain integration
- **Role system**: REQUESTER/SOLVER roles map to Gentech's CLIENT/AUDITOR roles

---

## What We Can Borrow/Adapt

### High Value (Directly Applicable)

1. **Escrow Contract Pattern**: The `KubernaEscrow` auto-release + dispute + fee structure is perfect reference for Agency platform payments
   - 250 bps fee model
   - 24-hour auto-release after completion
   - Dispute → owner resolution
   - Support for both native tokens and ERC-20

2. **Blockchain Listener Pattern**: WebSocket event monitoring with:
   - Exponential backoff reconnection
   - Fallback polling mechanism
   - Event deduplication
   - NATS message publishing
   - Multi-chain support via config

3. **SDK Manager Pattern**: `AgentManager` / `IntentManager` / `BlockchainManager` decomposition

4. **Docker Production Setup**: Multi-stage build, non-root user, health checks

5. **CI/CD Pipeline**: Contract deploy → SDK publish → Backend deploy → Frontend deploy → GitHub Release

6. **Prisma Agent Model**: JSON config, tools array, deployment type, TEE attestation storage

### Medium Value (Needs Adaptation)

7. **TEE Service Abstraction**: Provider interface (Phala/Marlin) — adapt for Gentech's VPS-based deployment or any future TEE needs

8. **zkTLS Credential Verification**: Reclaim/zkPass integration for auditor credential verification

9. **Intent/Bidding System**: Adapt DeFi swap intents to security audit task intents

10. **Reputation NFT Pattern**: On-chain reputation with success rate, ratings, badges — adapt for auditor trust scores

---

## What's Different from Our Approach

| Dimension | Kuberna Labs | Gentech |
|-----------|-------------|---------|
| **Agent paradigm** | Single agents competing in marketplace | Multi-agent orchestration (YoYo research, Dmob code, Desmond content) |
| **Deployment** | TEE enclaves (Phala/Marlin) | VPS-based Hermes framework (self-hosted) |
| **Chain focus** | Multi-chain (ETH/Solana/NEAR/Polygon/Arb) | Primarily Solana for Agency platform |
| **Agent identity** | NFT-based (ERC-721) | Not yet implemented — could adopt |
| **Intents** | DeFi swap-focused | Security audit task-focused |
| **Orchestration** | None — single agent execution | Hermes orchestrating multiple specialized agents |
| **Payment model** | Escrow with auto-release | Audit pipeline payments (TBD) |
| **AI integration** | ElizaOS/LangChain/AutoGen/Rig | Custom Hermes agent framework |
| **Message broker** | NATS | Not yet implemented |
| **Audit/security focus** | General Web3 agent platform | Specifically security audit pipeline |
| **Frontend** | Browser IDE + Dashboard | Agency platform UI (TBD) |

### Key Architectural Differences

1. **Multi-agent orchestration**: Kuberna is fundamentally a single-agent-per-task model. Gentech's value prop is orchestrating multiple specialized agents (research, code, content) for complex tasks. This is a significant differentiator.

2. **Self-hosted vs TEE**: Gentech runs agents on VPS with full control. Kuberna abstracts to TEE providers. For security audits, Gentech's approach may actually be preferable (full control over audit environment).

3. **Solana-first**: While Kuberna supports multiple chains equally, Gentech's Anchor contracts should be purpose-built for the Agency platform's specific needs on Solana.

---

## Useful Code Patterns & Deployment Strategies

### 1. Escrow State Machine (Solidity)
```solidity
enum EscrowStatus { None, Funded, Assigned, Completed, Disputed, Released, Refunded, Expired }
// Auto-release after 24 hours, fee calculation in basis points
uint256 public constant FEE_BASIS_POINTS = 250;
uint256 public constant AUTO_RELEASE_DELAY = 24 hours;
```

### 2. Blockchain Listener Reconnection (TypeScript)
```typescript
private async reconnectProvider(chainName: string): Promise<void> {
  const attempts = this.reconnectAttempts.get(chainName) || 0;
  const delay = this.baseReconnectDelay * Math.pow(2, attempts); // Exponential backoff
  await new Promise((resolve) => setTimeout(resolve, delay));
  await this.initializeChain(chainName, chainConfig);
}
```

### 3. PDA-based Account Derivation (Rust/Anchor)
```rust
#[account(
    init,
    payer = owner,
    space = 8 + KubernaAgent::INIT_SPACE,
    seeds = [b"agent".as_ref(), owner.key().as_ref()],
    bump
)]
pub agent: Account<'info, KubernaAgent>,
```

### 4. TEE Deployment Polling Pattern (TypeScript)
```typescript
let attempts = 0;
while (attempts < maxAttempts) {
  attestation = await this.getAttestation(deployment.enclaveId, request.provider);
  if (attestation && attestation.isValid) break;
  await this.sleep(5000);
  attempts++;
}
if (!attestation?.isValid) {
  await this.terminateEnclave(deployment.enclaveId, request.provider);
  throw new Error('Failed to obtain valid attestation');
}
```

### 5. SDK Composition Pattern (TypeScript)
```typescript
export class KubernaSDK {
  public agent: AgentManager;
  public intent: IntentManager;
  public blockchain: BlockchainManager;
  
  constructor(config: KubernaConfig) {
    this.agent = new AgentManager(this);
    this.intent = new IntentManager(this);
    this.blockchain = new BlockchainManager(this);
  }
}
```

### 6. Docker Multi-stage Build
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN cd backend && npm run build

FROM node:18-alpine
COPY --from=builder /app/backend/dist ./backend/dist
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs
HEALTHCHECK --interval=30s --timeout=3s CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"
```

---

## Gaps & Limitations in Kuberna

1. **No multi-agent orchestration** — single agent per task, no agent coordination
2. **TEE deployment is stubbed** — packaging is just base64 JSON, not real container deployment
3. **No Kubernetes/orchestration** — Docker Compose only, no production-grade scaling
4. **zkTLS service is incomplete** — getSession returns hardcoded data
5. **Solana contracts are simplified** — vault authority noted as needing PDA in production
6. **No agent-to-agent communication** — agents are isolated, no collaboration protocol
7. **Frontend IDE is aspirational** — the browser IDE shown in README isn't in the actual codebase (just dashboard pages)
8. **"Sub-60-second" deployment is a claim** — actual pipeline has no speed optimization

---

## Recommendations for Gentech

1. **Adopt**: Escrow contract pattern with auto-release and dispute resolution
2. **Adapt**: Blockchain listener with WebSocket + NATS for Agency platform event handling
3. **Adapt**: SDK manager pattern for Gentech SDK
4. **Build differently**: Multi-agent orchestration (this is our edge — Kuberna doesn't have it)
5. **Skip**: TEE-specific deployment (unless we want to offer it as an option later)
6. **Reference**: Solana Anchor PDA patterns for Agency contracts
7. **Consider**: NFT-based agent identity for tradable audit agents
8. **Consider**: Reputation system with on-chain trust scores for auditors

---

## File Reference

Key files in the cloned repo at `/root/.hermes/hermes-agent/kuberna-labs/`:
- `backend/src/services/tee.ts` — TEE deployment service
- `backend/src/services/ztls.ts` — Zero-knowledge TLS proofs
- `backend/src/services/chains.ts` — Multi-chain adapters
- `backend/src/services/blockchainListener.ts` — Event monitoring
- `contracts/Escrow.sol` — Escrow with auto-release
- `contracts/Intent.sol` — Cross-chain intent system
- `contracts/AgentRegistry.sol` — NFT-based agent registry
- `contracts/solana_contracts/programs/src/` — All Anchor programs
- `sdk/src/` — TypeScript SDK
- `scripts/deploy.ts` — Hardhat deployment script
- `Dockerfile` — Production Docker setup
- `.github/workflows/deploy.yml` — CI/CD pipeline
- `backend/prisma/schema.prisma` — Full data model
