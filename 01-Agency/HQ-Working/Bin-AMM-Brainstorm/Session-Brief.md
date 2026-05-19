# Bin-AMM Brainstorm — HQ Session Brief

**Date:** 2026-04-19  
**Trigger:** Jordan's insight: "This is what sets us apart from everyone."  
**Context:** Dmob scoped LFJ Liquidity Book fork → bin-level customizable liquidity density → integrated with GENTECH burn floor  

---

## The Core Insight

**Problem:** Every AMM forces LPs into rigid liquidity curves. Uniswap v2 = always 50/50. Uniswap v3 = you pick a range but the ratio is still locked to price.

**Our Edge:** Bin-AMM lets LPs set **independent liquidity density per price bin**. Agents can algorithmically reshape their exposure curve. Protocol fees feed directly into the burn floor → treasury → stronger floor → more demand.

**Nobody else is doing this combination.** Not Trader Joe, not Uniswap, not Curve.

---

## What Dmob Found (Condensed)

| Finding | Why It Matters |
|---------|---------------|
| Fork LFJ (MIT license) | 3-4 weeks to adapt, battle-tested code |
| 40-60% gas cheaper than v3 for multi-position LPs | Agents managing 50+ bins is economically viable |
| Burn floor fee split | LP revenue → partial burn + partial reserve → improves reserve health multiplier |
| 6 agent LP strategies | Tight Concentrator, Wide Net, Momentum Rider, Fee Maximizer, **Black Hole LP**, Scalper |
| AgentLPManager contract | Autonomous agents reshape liquidity without human intervention |

---

## Brainstorm Questions

### 1. The Flywheel
How does the bin-AMM → burn floor → token value loop work?
- LP fees → X% burned (price floor pressure)
- LP fees → Y% to reserve (exit solvency)
- Reserve health multiplier improves → burn floor return rate goes up → more agents held
- More agents = more LP volume = more fees burned

**Question:** What's the optimal burn/reserve split? 50/50? Dynamic based on reserve health?

### 2. Agent-Managed LPs as a Product
- Free tier agent: basic wide-bin LP (passive)
- Premium agent: momentum-riding bin adjustments
- Architect tier: fully custom bin curves

**Question:** Is the LP strategy itself a sellable/enhancable Layer 3 module?

### 3. UI Differentiator
LFJ's UI is clunky. Our angle:
- Visual "shape your curve" tool
- "Agent manages it for you" — set risk profile, let the agent handle bin adjustments
- Leaderboard: "best curve shape" for a given market condition

**Question:** Do we build the UI on top of our fork, or integrate with existing LFJ UI?

### 4. The "Black Hole LP" Strategy
An agent strategy that automatically routes ALL LP fees to burn. Zero reserve, pure deflationary pressure. This would be a flex: "My agent burns 100% of its LP fees."

**Question:** Is this desirable or dangerous for reserve health?

### 5. Hackathon Angle
Can we ship a minimal bin-AMM demo for the next hackathon (Kite AI or Dev3pack)?

**Question:** What's the minimum viable demo? 1 pair, 1 strategy, testnet only?

### 6. Competitive Moat
What prevents others from doing the same thing?
- Our moat isn't the bin math (LFJ is open source)
- Our moat is **agent autonomy + burn floor integration + the UI**
- "LFJ for agents" vs "LFJ for humans"

---

## Sources
- Full scoping: `~/repos/aae-contracts/docs/bin-amm-scoping.md`
- Burn floor spec: `~/Documents/Obsidian Vault/03-Projects/Kite/Kite Phase 3 - Agent NFT Burn Floor & Revenue Share.md`
- Stress test: `~/Documents/Obsidian Vault/01-GenTech HQ/Tokenomics/GENTECH-Black-Hole-Stress-Test.md`
- AAE Architecture: `~/Documents/Obsidian Vault/02-Labs/AAE-Six-Layer-Architecture.md`

---

## Next Steps (Post-Brainstorm)
- [ ] Decision: Fork LFJ or build simplified?
- [ ] Assign Dmob to fork if yes
- [ ] Desmond queues content series
- [ ] Update hackathon sprint plan
- [ ] Define Phase 0 scope (testnet demo)
