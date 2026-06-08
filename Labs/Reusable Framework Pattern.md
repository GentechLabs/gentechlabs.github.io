# Reusable Framework Pattern — Multi-Chain Agent Payment System

**Documented:** 2026-04-16
**Status:** Active Strategy
**Key Insight:** Build core logic once, adapt to chains via lightweight adapters

## The Pattern

Hackathons and grants in the agent/blockchain space share common themes:
- Agent-to-agent or agent-to-service payments
- Identity and attestation
- Spending controls and budgets
- On-chain settlement

The chain changes. The payment token changes. The core business logic stays the same.

## Architecture

```
┌─────────────────────────────────────────────────┐
│           AGENT PAYMENT FRAMEWORK               │
│         (core logic — Solidity contract)        │
├─────────────────────────────────────────────────┤
│  • Agent registration                           │
│  • Service discovery + approval                 │
│  • Payment execution with spending limits       │
│  • Daily budget tracking                        │
│  • Event logging for auditability               │
└───────────────┬──────────────┬──────────────────┘
                │              │
    Chain-Specific Adapters:
    • Kite AI (KITE token, AA SDK, Agent Passport)
    • Circle Arc (USDC, x402 protocol, CCTP)
    • Avalanche C-Chain (AVAX/USDC, Retro9000)
```

## Why This Works

1. **Core contract is chain-agnostic** — AgentPaymentFlow.sol works on any EVM chain
2. **Adapters handle chain-specific logic** — wallet setup, token approval, gas abstraction
3. **Each hackathon = new adapter, not new codebase**
4. **Portfolio compounds** — "multi-chain agent payment protocol" sounds better than "one-off hackathon project"

## Current Adapters

### Kite AI (Active — Encode Club Hackathon)
- Chain: Kite Testnet (Chain ID 2368)
- Token: KITE
- SDK: gokite-aa-sdk (ERC-4337 account abstraction)
- Identity: Agent Passport CLI
- Gasless: Yes (bundler handles gas)
- Status: In development

### Circle Arc (Planned)
- Chain: Arc
- Token: USDC
- SDK: Circle SDKs
- Protocol: x402 (agent-to-API payments)
- Gasless: Yes (sponsor pays gas)
- Status: Registered as Gentech Labs

### Avalanche C-Chain (Planned)
- Chain: C-Chain
- Token: AVAX / USDC
- SDK: AvalancheJS
- Grant: Retro9000 ($75K)
- Status: Application pending

## Strategic Benefits

1. **Reduced development time** — each new chain is ~30% of the original build
2. **Stronger portfolio** — "multi-chain" > "single-chain"
3. **Cross-pollination** — lessons from one adapter improve the others
4. **Future-proof** — new chains/adapters can be added as the ecosystem grows
5. **Dogfood potential** — use the framework for Gentech's own agent operations

## Related Notes
- [[Agent Economy on Kite — Project Status]]
- [[Kite AI — Reference]]
- [[Kite AI Hackathon Results]] — (pending Apr 28)
- [[Skills Audit & Cleanup Plan]]
