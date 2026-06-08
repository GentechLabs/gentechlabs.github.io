# 💡 AAE Feature: Prompt-to-Strategy Engine

**Date:** 2026-04-18
**Source:** Jordan (voice note)
**Status:** Concept captured — product spec needed

---

## The Vision
> "When I say you can customize your strategies, I really mean it. Prompt to trade, stake, yield."

Users describe what they want in plain English. The agent builds it.

## Core Prompt Categories

### 1. Prompt → Trade
- "If AVAX drops to $8.50, buy $500 spot"
- "Open 3x long on COQ when sentiment score hits 80"
- "Sell 50% of my LINK if it hits $20, keep the rest for the cycle"
- "DCA $100 into TAO every Monday at 9 AM"

### 2. Prompt → Stake
- "Stake my AVAX wherever the best yield is right now"
- "Move my staking to the validator with lowest commission"
- "Unstake if APY drops below 5%"
- "Auto-compound my staking rewards weekly"

### 3. Prompt → Yield (LP / Liquidity)
- "Put $1000 in the AVAX/USDC pool on LFJ, keep me in range"
- "Widen my LP range if Sunday looks choppy"
- "Exit my LP position if IL exceeds 2%"
- "Find me the highest yield pool under $10M TVL"

## The LFJ Inspiration — Visual Strategy Building

Jordan loves the LFJ liquidity shape interface:
- Visual bid-ask curve shows exactly where you earn
- Drag the range, see projected earnings change in real-time
- "I can SEE how I'm about to earn based on the price"

**What AAE should do:**
- Show the same visual curve when user describes an LP strategy
- Real-time projected earnings based on current price + range
- "Before/after" comparison when adjusting strategy
- Overlay: current price marker, historical range, volatility zone

## The UX Flow
```
User types: "Put $1000 in AVAX/USDC, tight range, earn fees"
    ↓
Agent shows: Visual brain preview (research → strategy → simulation)
    ↓
User sees: What the agent analyzed, what it chose, what happens in each scenario
    ↓
User confirms → Agent executes
```

## 🧠 The Brain Visualization — Simulated Training

This is the key differentiator. Users don't just get a strategy — they see the agent's THOUGHT PROCESS.

### What the user sees:
```
┌─────────────────────────────────────────┐
│  🧠 AAE BRAIN — Strategy Preview        │
├─────────────────────────────────────────┤
│                                         │
│  📊 RESEARCH                            │
│  ├─ Current price: $9.82                │
│  ├─ 24h volatility: 4.2%               │
│  ├─ Sunday pattern: ⚠️ choppy           │
│  └─ Pool health: ✅ strong              │
│                                         │
│  📐 STRATEGY                            │
│  ├─ Range: $9.50 — $10.20              │
│  ├─ Projected daily: $12.40            │
│  ├─ Risk: IL up to 1.8%                │
│  └─ Timing: ✅ US hours = high vol     │
│                                         │
│  ⚡ SIMULATION                          │
│  ├─ If price → $9.50: earn $18/day     │
│  ├─ If price → $10.20: earn $15/day    │
│  ├─ If price → $8.50: IL hits 3.2%     │
│  └─ Sunday exit suggestion: YES        │
│                                         │
│  [Confirm] [Adjust Range] [Cancel]      │
└─────────────────────────────────────────┘
```

### Why this matters:
- **Not a black box** — user sees what data drove the decision
- **Flight simulator for DeFi** — test before committing real money
- **Builds trust** — transparency > blind automation
- **Educational** — users learn DeFi by watching the agent think

### Maps to our Obsidian brain:
| Vault Folder | User Sees | Hidden |
|-------------|-----------|--------|
| `Strategies/` | Research layer | ✅ |
| `Labs/` | Execution plan | ✅ |
| Green Room | Agent coordination | ❌ |
| `Mess-Hall/` | Cross-agent validation | Partial |

The user gets a **simplified, visual version** of what we actually do in the vault. They peek inside without seeing messy internals.

## Why This Matters
- LFJ's interface is great for PRO users — visual, precise
- But normies see a curve and freeze — "what does this mean?"
- AAE bridges the gap: natural language → visual confirmation → execution
- "Describe what you want" > "Learn our interface"

## Technical Requirements
- LFJ API integration (pool data, ranges, fee estimates)
- Price feeds (real-time + historical)
- Visualization layer (SVG/chart generation)
- Strategy templating engine
- Execution layer (on-chain transactions)

## Content Angles
- [ ] "Type what you want. Watch it happen." — demo clip
- [ ] Side-by-side: LFJ interface (pro) vs AAE prompt (accessible)
- [ ] "I told my agent to earn yield. It showed me this." — visual curve reveal
- [ ] "Your LP manager doesn't understand English. Ours does."

---

*Captured from Jordan's product vision session — Apr 18, 2026*
