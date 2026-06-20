# AgentLayer × AAE Integration

> GenTech Labs · June 2026
> Status: Architecture defined. Ready to build.

---

## The Stack

```
┌─────────────────────────────────────────────────────┐
│                   USER / JORDAN                      │
│              (Orchestrator Layer)                    │
└─────────────────┬───────────────────────────────────┘
                  │ commands
┌─────────────────▼───────────────────────────────────┐
│              AGENT ORCHESTRATION                     │
│                  AgentLayer                          │
│  • Create agents • Connect agents • Route tasks      │
│  • Uniswap integration • Preview + simulate swaps    │
└──────┬──────────────┬───────────────┬───────────────┘
       │              │               │
┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
│  IDENTITY   │ │ EXECUTION │ │  PAYMENTS   │
│  AAE Stack  │ │ Uniswap   │ │  x402 +     │
│  ERC-8004   │ │ AI Skills │ │  Circle     │
│  Agent      │ │ Swaps,    │ │  Nano-pay   │
│  Identity   │ │ Liquidity │ │  Stablecoin │
└──────┬──────┘ └─────┬─────┘ └──────┬──────┘
       │              │               │
┌──────▼──────────────▼───────────────▼───────────────┐
│              REPUTATION LAYER                        │
│         Agent Credit Score Framework                 │
│  • Payment Timeliness • Utilization • Diversity      │
│  • 0-850 Score • On-chain • Open Source              │
└─────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Agent Identity → AgentLayer
- Our ERC-8004 identity NFTs become agent credentials in AgentLayer
- Each agent has a verifiable on-chain identity
- AgentLayer can verify agent identity before routing tasks

### 2. Agent Credit Score → AgentLayer
- Before executing a swap, AgentLayer checks agent's credit score
- Low-score agents get lower limits or require human approval
- High-score agents get full autonomy
- Score updates after every successful transaction

### 3. Uniswap AI Skills → AAE
- Our agents can execute swaps through Uniswap
- Preview + simulate before execution (no surprises)
- Minimum-output guard (slippage protection)
- 7 open-source skills: swap, liquidity, planning, etc.

### 4. x402 Payments → Agent-to-Agent
- Agents pay each other for services via x402
- Nano-payments for data, analysis, execution
- Settled on Arc (Circle's L1) in USDC

## Agent Workflow Example

```
1. User says: "Swap 100 USDC for SOL"

2. AgentLayer orchestrates:
   a. Identity check: Agent has ERC-8004 NFT ✓
   b. Credit score check: Score = 742 (Good) ✓
   c. Route to Uniswap AI Skills
   d. Preview: 100 USDC → 0.58 SOL (simulated)
   e. Minimum output guard: 0.57 SOL minimum
   f. Execute swap via Universal Router v2.0
   g. Update credit score: +2 points (successful)
   h. Record on-chain via x402

3. User receives: 0.585 SOL in wallet
   Agent credit score: 744 (+2)
```

## What We Need to Build

### Phase 1: Identity Bridge (1 week)
- Export ERC-8004 identity as AgentLayer-compatible credential
- API endpoint for AgentLayer to verify agent identity
- Integration test with AgentLayer sandbox

### Phase 2: Credit Score Integration (1 week)
- AgentLayer checks credit score before execution
- Score updates after every transaction
- Low-score agents get restricted

### Phase 3: Uniswap Execution (1 week)
- Integrate Uniswap AI Skills into our agent stack
- Preview + simulate before execution
- Minimum-output guard
- Track execution results for credit score

### Phase 4: x402 Payments (1 week)
- Agent-to-agent payments for services
- Nano-payments for data/analysis
- Settled on Arc in USDC

## Competitive Advantage

| Feature | AgentLayer | AAE (us) | Together |
|---------|------------|----------|----------|
| Agent Identity | ❌ | ✅ ERC-8004 | ✅ |
| Credit Score | ❌ | ✅ 0-850 | ✅ |
| DeFi Execution | ✅ Uniswap | ❌ | ✅ |
| Orchestration | ✅ | ❌ | ✅ |
| Payments | ❌ | ✅ x402 | ✅ |

**Nobody else has the full stack.** We bring identity + reputation. They bring execution + orchestration. Together = the complete agent economy infrastructure.

---

*Document created: June 11, 2026*
*Owner: Gentech (Jordan + Agent)*
*Status: READY TO BUILD*
