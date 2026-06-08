# AAE Social Layer & Visual Identity Spec

**Status:** Draft — Architecture Discussion
**Created:** 2026-04-20 (restored from Telegram context)
**Related:** `AAE-Six-Layer-Architecture.md`, `AAE-Layers-Overview.md`

---

## Core Thesis

The social layer is the adoption multiplier. Traditional DeFi has zero flex culture — nobody shows off their GMX position on Twitter. But NFT-based agents with visual identity, rarity, and burn history? That's culture.

**The product is the protocol. The art is the funnel.**

---

## The Social Flywheel

```
1. Visual identity → "I have Desmond, he looks like this"
2. Wallet display → Shows up alongside other NFTs, but it's doing something
3. Status mechanics → Burn count visible on the agent card
4. Community recognition → "That agent's been staked for 6 months"
5. New users see it → "I want one that looks like that"
6. Repeat ♻️
```

---

## The "Wallet Flex" Multiplier

When your agent is visible in a wallet with unique art, three things happen simultaneously:

1. **Retention** — People don't sell things that represent their identity. An agent with a cool avatar isn't just a utility — it's a badge.
2. **Organic Marketing** — Every wallet viewer sees it. Free impressions. No ad spend.
3. **Secondary Market Premium** — Rare traits become collectible. Proven pattern: BAYC, DeGods, Milady. The difference: our agents have real utility underneath.

---

## User Acquisition Funnel

```
Sees agent in friend's wallet
     ↓
"Where'd you get that?"
     ↓
Free tier → try it
     ↓
$10 mint → now I own the art + the bot
     ↓
$15-20 sub → now it actually works for me
     ↓
Burn/stake → now I'm building a portfolio
```

**This is network-effect-driven growth.** Every new user makes agents more visible → drives curiosity → drives more mints.

---

## The DeFi People Who Don't Know They're DeFi Yet

Most people won't call it "burning agents for yield multipliers." They'll call it "upgrading my bot." Same mechanic, zero DeFi jargon. The agent-as-NFT framing makes it feel like a game, not a financial product.

**That's how you get normies in without them realizing they're doing DeFi.**

---

## Visual Identity System

### On-Chain Metadata (AgentNFT)

| Field | Description | Example |
|-------|-------------|---------|
| `agentImage` | IPFS/Arweave link to artwork | `ipfs://Qm...` |
| `agentClass` | Role specialization | trader, researcher, analyst |
| `level` | Tier (1=basic, 2=full) | 2 |
| `multiplierCount` | How many agents burned for power | 3 |
| `activeSince` | Timestamp — OG flex | `1713571200` |

**Your wallet is your resume.** When someone looks at your address:
> "This guy has 3 agents, burned 2 for multipliers, been here since Day 1."

### Visual Evolution

| State | Visual Treatment |
|-------|-----------------|
| Fresh mint | Standard art, base color palette |
| Active staking | Glowing aura, animated elements |
| 3+ burns | Rare traits unlocked, enhanced art |
| OG (6+ months) | Legacy badge, special frame |
| Burned (memorialized) | Ghost/skeleton version, tribute card |

---

## Pricing Tiers → Contract Side

| Tier | What You Get | Contract State |
|------|-------------|----------------|
| $5 | Basic agent, limited features | `AgentNFT(level=1)` |
| $10 | Full agent, all DeFi connectors | `AgentNFT(level=2)` |
| +Subscription | Staking active, multiplier slots unlock | `stake()` + `burnToUpgrade()` |

---

## Burn Multiplier Curve (Proposed)

Diminishing returns — meaningful at every step, but not exponential enough to create whales too early:

| Burn # | Yield Multiplier | Cumulative |
|--------|-----------------|------------|
| 1 | +10% | 10% |
| 2 | +15% | 25% |
| 3 | +20% | 45% |
| 4 | +25% | 70% |
| 5 | +30% | 100% |
| 6 | +35% | 135% |
| 7 | +40% | 175% |
| 8 | +45% | 220% |
| 9 | +50% | 270% |
| 10 | +55% | 325% |

**Design goals:**
- Too linear → burning gets boring
- Too exponential → early burners have unfair advantage
- Diminishing returns → every burn decision is meaningful
- 10x cap feels reachable but takes commitment

**Needs stress-testing with real revenue numbers** — the curve shape should match actual fee generation data.

---

## Why This Works (Engineering Perspective)

1. **The visual IS the metadata** — stored on-chain, composable, verifiable
2. **Burned agents are visible** — "This wallet sacrificed 7 agents" = serious player
3. **Secondary market creates stories** — "This agent earned 50 AVAX in fees"
4. **Social proof compounds** — more users → more visibility → more users

---

## Open Questions

- [ ] Art style direction (pixel, illustration, 3D render, AI-generated?)
- [ ] Rarity trait system design (how many traits, how do they combine?)
- [ ] Animation standards for staked/active agents
- [ ] Memorialized agent behavior (can they be restored? transferable tributes?)
- [ ] Social sharing mechanics (Twitter cards, Telegram previews, wallet gallery)
- [ ] Revenue modeling for the burn curve with real numbers

---

## Tags
#AAE #social-layer #NFT #identity #burn-mechanics #adoption #spec
