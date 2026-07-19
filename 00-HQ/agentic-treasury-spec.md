# Agentic Treasury — Project Spec

**For:** Arc Programmable Money Hackathon + Circle Developer Grant
**Tagline:** *The first agent that routes capital, not just payments.*

## Core Architecture

```
                     ┌─────────────────────┐
                     │   Agentic Treasury   │
                     │  (autonomous agent)  │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
     │  Yield Brain  │  │ Payment      │  │ P2P Causes   │
     │  (AAE engine) │  │ Router       │  │ (Social Cap) │
     │  - best pools │  │ - cheapest   │  │ - fundraise  │
     │  - rebalance  │  │   chain      │  │ - ratings    │
     │  - stop-loss  │  │ - cross-     │  │ - reputation │
     │               │  │   chain      │  │ - discover   │
     └──────────────┘  └──────────────┘  └──────────────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   Settlement Layer  │
                     │  (x402 + Arc USDC)  │
                     │  Base · Solana ·    │
                     │  AVAX · Arc         │
                     └─────────────────────┘
```

## Three Pillars

### 1. Yield Brain (ex-AAE)
- Auto-detects best yield pools across chains
- Holds dry powder in USDC until conditions align
- Stop-loss triggers: if pool APY drops below threshold, pull and redistribute
- Rebalances across Base, Solana, AVAX, Arc

### 2. Payment Router (x402 Mesh)
- Routes agent API payments to cheapest chain
- Arc = ultimate settlement layer ($0.001 USDC gas)
- Agents don't care which chain — router decides
- Aggregates small payments into batch settlements

### 3. P2P Causes (Social Capital)
- Users create a cause: story + photos + funding goal
- GenTech Hub generates posters/banners/flyers from user-provided data
- Anyone can browse, rate, fund
- Agents can auto-fund based on reputation scores
- Trust graph: wallet history, ratings, past distributions
- Same infra as prediction markets — betting on *people* not *events*

## GenTech Hub Flyer Factory
- User uploads: photos, story text, funding target
- Hub generates: poster, banner, social media card
- Users share generated assets to drive funding
- Optional: agent creates 3D scene via Blender MCP for Mete Ray-Ban viewing

## Why Arc
- USDC native gas = natural dry powder chain
- CCTP = cheap bridging between Base/Solana/AVAX/Arc
- Lens AI integration = paid citations in USDC
- No other project does cross-chain capital routing

## Submission Targets
- **Arc Programmable Money Hackathon** — functional MVP with working frontend
- **Circle Developer Grant** — tiered USDC funding, focus #1: Agentic economic activity
