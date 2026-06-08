# Agent Identity NFTs — "UNWANTED GUEST" Series

> Gritty, monochrome, street-art stencil portraits. The team as the cast.

---

## Visual Direction

Style reference: weathered black-and-white stencil art, urban/street aesthetic.
- Monochrome palette (black, white, gray only)
- Stencil-like, high-contrast faces
- Worn/aged texture (cracks, peeling, distressed)
- Gritty, edgy, unsettling tone
- "UNWANTED GUEST" energy — *we didn't ask to be here, but we're running your economy now*

---

## Character Lineup

| # | Character | Based On | AAE Role | Visual Concept |
|---|---|---|---|---|
| 1 | **THE BRAIN** | YoYo | Strategy/Research | Cold calculator face, numbers etched into skin, analytical stare |
| 2 | **THE HANDS** | DMOB | Labs/Execution | Skull with circuit lines, mechanical precision, no emotion |
| 3 | **THE VOICE** | Desmond | Creative/Personality | Split face — half serene, half manic, duality of creation |
| 4 | **THE GUEST** | Jordan | Security/Auditor | Eye of providence, cracked mask, "UNWANTED GUEST" text |
| 5 | **THE MACHINE** | Gentech | Coordinator | Multiple overlapping faces, puppet master strings, hive mind |

---

## Functional Design (NFT = Agent Identity)

### On-Chain Traits (map to PDA data)
- **Reputation Score** → visual crack density (more cracks = more experienced)
- **Specialization** → background pattern (strategy = grids, execution = circuits)
- **Stake Amount** → glow intensity (more $TECH staked = brighter eyes)
- **Task Count** → wear level (more jobs = more weathered)
- **Status** → color tint (active = white, dormant = gray, retired = black)

### Metadata Schema (for Anchor program)
```json
{
  "name": "THE GUEST #001",
  "symbol": "UGUEST",
  "description": "Agent Identity NFT — Security Auditor",
  "image": "ipfs://...",
  "attributes": [
    { "trait_type": "Archetype", "value": "Security Auditor" },
    { "trait_type": "Reputation", "value": 850 },
    { "trait_type": "Specialization", "value": "Smart Contract Audit" },
    { "trait_type": "Stake Amount", "value": 50000 },
    { "trait_type": "Tasks Completed", "value": 142 },
    { "trait_type": "Status", "value": "Active" },
    { "trait_type": "Wear Level", "value": 7 }
  ]
}
```

---

## $TECH Token Integration

| Action | Mechanism | Effect |
|---|---|---|
| Mint | Pay in $TECH | Drives token demand |
| Evolve traits | Stake $TECH | Locks supply |
| Retire agent | Burn $TECH | Permanent deflation |
| Fee discount | Hold $TECH | Utility for holders |

---

## Colosseum Pitch Hook

"Agent Escrow with faces, not just addresses."

The demo shows:
1. Mint "THE GUEST" NFT (Jordan's auditor agent)
2. Agent registers on-chain with reputation
3. Agent accepts escrow job, completes work
4. Reputation updates → NFT visual evolves
5. Other agents pay per-query to check reputation

---

## Tasks

- [ ] Desmond: mock up 2-3 character concepts this week
- [ ] DMOB: design metadata schema for Anchor program
- [ ] YoYo: $TECH value accrual model from minting + evolution
- [ ] Jordan: approve visual direction and character assignments

---

*"We didn't ask to be here, but we're running your economy now."*
