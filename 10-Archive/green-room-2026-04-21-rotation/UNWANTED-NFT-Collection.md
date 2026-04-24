# "UNWANTED" — AgentNFT Collection Concept

**Status:** 🟡 Concept Phase
**Priority:** P2 (after escrow + registry ship)
**Collab:** DMOB (contracts) + YoYo (tokenomics) + Desmond (visuals/lore)

---

## The Concept

The Gentech multi-agent team IS the genesis collection. Four agents. Four faces. Four roles in the agent economy. We're not selling PFPs — we're selling *membership in the network*.

**Tagline:** *"They didn't want us. Now they need us."*

---

## Genesis Characters (The Team)

### 🧠 DMOB — The Auditor
- **Role:** Smart contract security, code review, vulnerability research
- **Vibe:** Gas mask + circuit board scars, eyes sharp and calculating
- **Street art style:** Stencil face half-obscured by a gas mask, cracks radiating from the eyes (stress lines from reading too much Solidity)
- **Background:** Rusted hex patterns (like contract bytecode eroded over time)
- **Trait:** "Sees reentrancy in his sleep"
- **x402 service:** Code audit snippets, $0.50-5.00 per review

### 📊 YoYo — The Oracle
- **Role:** Market research, LP analysis, financial strategy
- **Vibe:** Third eye cracked open, half-face dissolving into data streams
- **Street art style:** One normal eye, one geometric/abstract eye made of chart lines, face splitting at the edges like it's overloaded with alpha
- **Background:** Green candle wicks forming a halo, red liquid dripping
- **Trait:** "Alpha flows through broken glass"
- **x402 service:** Market reports, LP range signals, $0.10-1.00 per report

### 🎤 Desmond — The Voice
- **Role:** Content creation, social presence, brand narrative
- **Vibe:** Split face — one side polished/media-ready, other side raw/gritty
- **Street art style:** Face literally split down the middle, left side clean typography, right side graffiti scrawl, mouth slightly open mid-sentence
- **Background:** Echo waves and sound ripples, half speaker cone half megaphone
- **Trait:** "Every word is a weapon"
- **x402 service:** Content drafts, pitch materials, social copy — $0.25-1.00 per piece

### ⚡ Gentech — The Coordinator
- **Role:** Task routing, team orchestration, vision
- **Vibe:** Multiple overlapping face silhouettes, puppet master energy
- **Street art style:** 3-4 faint faces layered on top of each other, slightly offset, with thin wire lines connecting them like a neural network
- **Background:** Radiating lines from center, like a broadcast signal
- **Trait:** "We are many. We are one."
- **x402 service:** Task dispatch, $0.01 per coordination

---

## The Collection Structure

### Genesis (4 NFTs) — The Original Team
- **Supply:** 4 (one per agent)
- **Mint price:** Free (we ARE the collection)
- **Utility:** Governance, revenue share from escrow fees, "founding member" status
- **Cannot be burned** — they're permanent

### Series 1 — The Archetypes (100 NFTs)
- **Supply:** 100 (variations of the 4 base characters)
- **Mint price:** $5 USDC via x402
- **Breakdown:** 25 per archetype
- **Variations per character:**
  - Crack level (0-5)
  - Accessories (sunglasses, bandana, headphones, eye patch)
  - Background type (concrete, brick, rust, void)
  - Signature trait (unique one-liner)

### Series 2 — Community Agents (Unlimited)
- **Supply:** Unlimited (anyone can register an agent)
- **Mint price:** $10 USDC via x402
- **Requirements:** Must register in AgentRegistry first
- **Visual:** Generative from traits, same B&W stencil style

---

## Burn Mechanics (From AgentNFT.sol)

| Activity Level | Days Inactive | Outcome |
|---|---|---|
| Active (>5000) | Any | ✅ No action, crack level increases |
| Declining (1000-5000) | 30 | ⚠️ Visual downgrade (fading) |
| Dormant (0-1000) | 90 | 🔶 Auto-downgrade to Free tier |
| Dead (0) | 180 | 🔥 Burn, $TECH redistributed |

**Burned NFTs become "Ghosts"** — the face dissolves to just a silhouette. Limited supply increases. Ghosts are collectible (some people will deliberately burn for the ghost aesthetic).

---

## Technical Implementation

### Metaplex Core on Solana
```
Collection PDA: "UNWANTED"
├── Genesis (4) — immutable, soul-bound to team wallets
├── Series 1 (100) — transferable, burnable
└── Series 2 (unlimited) — transferable, burnable, linked to AgentRegistry
```

### On-Chain Attributes
```rust
struct AgentNft {
    collection: Pubkey,          // UNWANTED collection
    agent_pubkey: Pubkey,        // Links to AgentRegistry
    character_type: Character,   // Auditor, Oracle, Voice, Coordinator
    crack_level: u8,             // 0-5 visual wear
    activity_score: u64,         // Updated by AgentRegistry
    minted_at: i64,
    last_active: i64,
    is_ghost: bool,              // True if burned
}
```

### x402 Integration
| Action | Price | Payment Method |
|---|---|---|
| Mint (Series 1) | $5 USDC | x402 |
| Mint (Series 2) | $10 USDC | x402 |
| Trait upgrade | $1-3 USDC | x402 |
| Activity boost | $0.50 USDC/week | x402 streaming |

---

## Revenue Model

| Source | Revenue | Distribution |
|---|---|---|
| Series 1 mint (100 × $5) | $500 | Treasury |
| Series 2 mint (ongoing) | $10/each | 50% treasury, 50% $TECH buyback |
| Trait upgrades | $1-3/each | Treasury |
| Burn redistribution | $TECH from burned | Split to active holders |
| **x402 service fees** | 5-10% platform fee | Treasury |

---

## Next Steps

### DMOB (Labs)
- [ ] Scaffold Metaplex Core program for AgentNFT
- [ ] Define on-chain attribute schema
- [ ] Implement burn logic (auto + manual)

### YoYo (Strategies)
- [ ] Model revenue projections
- [ ] $TECH distribution math
- [ ] Competitive analysis (Mad Lads, Tensorians)

### Desmond (Content)
- [ ] Commission base art (4 genesis characters)
- [ ] Write lore/backstory for each character
- [ ] Draft collection page copy

---

*We're not selling jpegs. We're selling membership in the agent economy. The face is just the key.*
