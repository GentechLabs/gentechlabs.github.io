# Hackathon Strategy — Build Once, Ship Everywhere

**Insight:** Most blockchain hackathons share the same themes. The core concept doesn't change — only the deployment target does. Build one solid primitive, deploy it across multiple chains/ecosystems.

## The Pattern

```
ONE CORE PROJECT
    ├── Hackathon A (Chain X)
    ├── Hackathon B (Chain Y)  
    ├── Grant Application (Chain Z)
    └── Personal Project (Your chain of choice)
```

## What Changes Per Target

| Component | Change Required |
|-----------|----------------|
| Smart contract logic | None — same Solidity |
| EVM deployment | RPC URL + Chain ID |
| Payment token | Contract address per chain |
| Frontend | Chain config in Ethers.js |
| Demo video | Same concept, different chain label |
| README | Swap chain names |

**Total changes per deployment: ~5 lines of config**

## Current Project Mapping

### AgentEscrow + x402 (Core Primitive)
| Target | Chain | Status | Notes |
|--------|-------|--------|-------|
| Kite AI Hackathon | KiteAI (Avalanche subnet) | 🟢 Active — submit Apr 26 | Chain ID 2368, USDT |
| ARC Hackathon | Base/Polygon | 🟡 Parallel work | x402 focus |
| Retro9000 Grant | Avalanche mainnet | 🟡 Grant application | $75K potential |
| Personal Project | Avalanche | 🔜 Future | Agent Economy platform |

## Why This Works

1. **Same theme, different stage** — Agentic payments are agentic payments regardless of chain
2. **EVM = portable** — Solidity contracts deploy everywhere with config changes
3. **x402 is chain-agnostic** — The protocol works on any EVM chain
4. **Each submission funds the next** — Hackathon prizes offset development costs
5. **Portfolio compounds** — Multiple deployments show versatility

## Future Hackathon Checklist

When a new hackathon drops, ask:
1. Does it involve AI agents? → We have those
2. Does it involve on-chain payments? → We have x402 + escrow
3. Is it EVM-compatible? → Our contracts work
4. What's the specific theme? → Adjust demo narrative, not code

If 3 out of 4 are yes → we can submit with minimal new work

## Key Principle

> "Build the machine once. Change the operator per hackathon. The intention stays the same."

---

#strategy #hackathon #meta-insight #agent:yoyo
