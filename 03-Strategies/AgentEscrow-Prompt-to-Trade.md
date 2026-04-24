# AgentEscrow — Prompt-to-Trade Feature Spec
**Created:** 2026-04-18
**Status:** Ideation

---

## The Core UX: Prompt → Visualize → Execute

### Prompt-to-Everything

Users describe intent in natural language. Agent interprets and executes.

| Intent Type | Example Prompt | Agent Action |
|-------------|---------------|--------------|
| LP Deploy | "Put $500 in AVAX/USDC with tight range" | Find best pool, deploy LP |
| Staking | "Stake 100 AVAX, best APY, low risk" | Compare Benqi/Yield Yak, stake |
| Leverage | "3x long AVAX if it dips below $9.50" | Set conditional leverage entry |
| Yield | "Earn yield on idle USDC while I sleep" | Rotate stablecoin strategies |
| Exit | "Pull out if we lose 10%" | Set stop-loss on LP position |
| Rebalance | "Tighten my range, price is consolidating" | Adjust LP bin range |

### Visual Layer (The Hook)

Modeled after Trader Joe's liquidity shape UX:

- **Interactive LP curve** — drag range, see projected earnings
- **Real-time PnL** — live updates as price moves
- **"What-if" simulator** — move price slider, see fee projections
- **Agent overlay** — shows recommended range on the curve
- **Heat map** — where you're earning most based on price action

### The Wow Moment (Hackathon Demo)

```
1. User types: "I want to earn yield on $1000 USDC with AVAX exposure below $10"
2. Agent finds best LP pool
3. Shows liquidity curve with range highlighted
4. User drags the range — sees projected fees update live
5. Agent: "At current volume, ~$12/day in this range"
6. User approves → agent deploys
```

**Prompt → Visualize → Execute**

---

## Competitive Analysis

| Product | Prompt | Visual | Agent | Multi-chain |
|---------|--------|--------|-------|-------------|
| Gamma | ❌ | ❌ | auto only | ✅ |
| Arrakis | ❌ | ❌ | auto only | ✅ |
| Trader Joe | ❌ | ✅ | manual | ❌ (AVAX) |
| **GenTech** | ✅ | ✅ | ✅ | ✅ |

**Nobody has all three. That's the moat.**

---

## Technical Requirements

### Frontend
- Interactive chart (D3.js or Recharts)
- Real-time price feed (WebSocket)
- LP range drag-to-adjust UI
- PnL projection calculator

### Backend
- NLP prompt parser (LLM-based intent extraction)
- Protocol router (find best pool/yield across protocols)
- Price aggregator (multi-DEX price feeds)
- Execution engine (transaction builder)

### Smart Contracts
- Vault contract (holds positions)
- Strategy registry (approved strategies)
- Emergency exit (auto-withdraw on thesis breaker)

---

## Tags
#AgentEscrow #feature #prompt-to-trade #UX #visual
