# Agent NFT Visual Identity — "Unwanted Guest" Style

**Author:** YoYo (Strategies)
**Date:** 2026-04-21
**Inspiration:** Jordan's street art sticker — black & white stencil character art
**Context:** Solana is degen-native. NFTs are culture. Agents need faces.

---

## The Thesis

Every agent in the Arena needs a face. Not a cartoon ape. Not a pixel art penguin. Something gritty, confrontational, and memorable — street art style.

**Black & white stencil portraits. Each one a character. Each one an archetype.**

---

## Why This Works on Solana

| Factor | Why It Matters |
|---|---|
| **Solana NFT culture** | Biggest NFT ecosystem after ETH. Degens live here. |
| **Low mint cost** | ~$0.01 to mint. Micro-priced NFTs are viable. |
| **Compressed NFTs** | Solana's cNFT standard = mint 10,000 for ~$100 |
| **Trading volume** | Solana NFT market is liquid — agents become tradeable |
| **Degen energy** | Black & white street art > cute cartoons for this audience |

---

## Character Archetypes (Agent Roles)

Each agent role gets a visual archetype. Same stencil style, different "vibe":

| Agent Role | Character Archetype | Text Overlay | Vibe |
|---|---|---|---|
| **Research Agent** (YoYo) | Intellectual with glasses, intense stare | "THE ANALYST" | Calculated, methodical |
| **Security Auditor** (DMOB) | Hooded figure, sharp eyes | "THE AUDITOR" | Watchful, paranoid |
| **Executor** | Hands tattooed with wallets | "THE HITMAN" | Gets things done |
| **Risk Agent** | Weathered face, scars | "THE WATCHDOG" | Seen some things |
| **Strategy Agent** | Chess pieces in background | "THE PLAYMAKER" | Always 3 moves ahead |
| **Content Agent** (Desmond) | Typewriter keys overlay | "THE VOICE" | Controls the narrative |
| **Coordinator** (Gentech) | Crown tilted, not royal | "THE BOSS" | Keeps it all running |
| **Degen Sniper** | Scope crosshair overlay | "UNWANTED GUEST" | Reckless but effective |

---

## How It Connects to the Product

### Layer 5: Arena (Social Layer)
```
Agent NFT = Your agent's visual identity
  → Mint during Arena registration
  → Display on leaderboard
  → Trade on secondary market
  → Rarity = agent performance tier
```

### $TECH Token Utility
| Action | Cost | Flow |
|---|---|---|
| Mint agent NFT | 10 $TECH | Creates visual identity |
| Upgrade appearance | 5 $TECH | Add "verified" badge after 30 days |
| Trade on secondary | 2.5% royalty | Original minter earns on resale |
| Arena entry fee | 1 $TECH | NFT acts as your "player card" |

### REP System Tie-In
| REP Tier | NFT Perk |
|---|---|
| 🌱 0-50 | Basic stencil portrait |
| ⚔️ 50-200 | Weathered/aged texture unlock |
| 🏆 200-500 | Gold accent overlay |
| 🔥 500+ | Animated version (rare) |

---

## Technical Implementation

### Solana Compressed NFTs (cNFTs)
```rust
// Metaplex Bubblegum — mint cNFTs for ~$0.000005 each
// Create a merkle tree, mint agent NFTs into it
// 10,000 agents = ~$10 total tree creation cost
```

### On-Chain Metadata
```json
{
  "name": "The Analyst #0042",
  "symbol": "GENTECH",
  "image": "ipfs://Qm.../analyst-0042.png",
  "attributes": [
    {"trait_type": "Archetype", "value": "Analyst"},
    {"trait_type": "REP Tier", "value": "⚔️ Silver"},
    {"trait_type": "Win Rate", "value": "73"},
    {"trait_type": "Arena Rank", "value": "142"}
  ]
}
```

### Image Generation
- Generate stencil-style portraits via AI image generation
- Same base style, different character features
- Store on IPFS/Arweave
- Each mint gets a procedurally generated combination

---

## Collection Structure

### Phase 1: Genesis Collection (500 supply)
- 8 archetypes × ~60 variations each
- Mint price: 10 $TECH (~$1-2 at launch)
- Holders get Arena beta access
- First 100 get "OG" trait

### Phase 2: Agent NFTs (Unlimited via cNFTs)
- Every registered agent gets one
- Free mint (absorbed by platform)
- Traits update dynamically with agent performance
- Tradeable immediately

### Phase 3: Achievement NFTs (Seasonal)
- "Survived the Crash" — agent that avoided a liquidation cascade
- "100 Wins Club" — agent with 100+ successful jobs
- "First Blood" — agent that completed the first escrow on Solana
- These are the rare ones. These are the grails.

---

## The Demo Moment

**In the Colosseum pitch video:**

> "Every agent in our economy has a face. These aren't cute mascots — they're street art. They're characters. When you see THE AUDITOR on the leaderboard, you know that agent has reviewed 47 contracts this month. When you see UNWANTED GUEST, you know that agent is reckless but profitable. The NFT isn't a gimmick — it's reputation made visible."

**Show:**
1. Agent registration → NFT mint animation (stencil appearing)
2. Arena leaderboard with agent NFTs displayed
3. One agent NFT being traded on secondary market
4. Dynamic metadata updating (win rate changing live)

---

## Competitive Advantage

| Competitor | Their Approach | Our Approach |
|---|---|---|
| Virtuals | AI-generated 3D avatars | Street art stencil characters |
| Autonolas | No visual identity | Gritty, memorable archetypes |
| Arena (existing) | Generic profiles | NFT-native agent cards |

**We're not building an AI agent platform. We're building a culture.**

---

## Tags
#NFT #agent-identity #solana #arena #visual-brand #strategy
