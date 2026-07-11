# 🌴 GenTech Travels — Full Build Brief

**Date:** May 28, 2026
**Status:** 🟡 READY TO BUILD
**Type:** Travel Community Platform with AI Moderation + Creator Economy
**Target Audience:** Passport bros, international travelers, digital nomads
**Platform Layer:** Built ON TOP of Telegram/Discord/X (not standalone app)

---

## 🎯 The Vision

GenTech Travels is a travel community platform with two sides (men/women), AI-powered moderation, voice personalities, and a creator economy. Built for the passport bro community that gets censored on mainstream platforms.

**Tagline:** "Post content. Get rated. Climb the spotlight. Get tips. Don't fight."

**Core Insight:** Don't build a new social network. Build a moderation and community layer that works WITH existing platforms.

---

## 🏗️ Architecture

### Platform Structure

```
┌─────────────────────────────────────────────────────────┐
│                  GEN TECH TRAVELS                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  👨 MEN'S SIDE          👩 WOMEN'S SIDE                  │
│  (default: men only)    (default: women only)           │
│  [Toggle: Co-Ed]        [Toggle: Co-Ed]                 │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🎭 ROAST LAYER                                        │
│  👍/👎/🔥 rating system                                  │
│  Roast meter fills → Steve Harvey roasts you            │
│                                                         │
│  🔧 REPAIR LAYER                                        │
│  Agent helps fix reputation after roast                 │
│  Repair paths: reviews, verification, engagement       │
│                                                         │
│  🎤 VOICE PERSONALITIES                                 │
│  Steve Harvey (roast), Vanito (hype), George (wise)    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  💰 CREATOR ECONOMY                                     │
│  Tips → Spotlight → Revenue                             │
│  Top creators get featured, earn money                  │
│                                                         │
│  🏆 GAMIFICATION                                        │
│  Trust points, leaderboards, badges                     │
│  Challenge system for fake profiles                     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🛡️ GOVERNANCE                                          │
│  Get along, don't fight                                │
│  Agent moderation, community reports                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Platform Integration

**Telegram Bot:**
```
@GenTechTravelsBot
/connect telegram
/group mens-philippines
/upload photo
/roast @username
/repair @username
/tip @username $5
```

**Discord Bot:**
```
/genconnect
/genmoderate #travel-philippines
/genroast @user
/genrepair @user
/gentip @user $5
```

**X/Twitter Integration:**
```
@GenTechTravels
/content-layer
/moderate-tweets
/privacy-filter
```

---

## 📋 Rules (One Sentence)

**"Get along with each other. Don't fight. If there's fighting, report it."**

### Enforcement

| Offense | Action |
|---------|--------|
| First offense | Warning DM |
| Second offense | Removed from co-ed (can use gender-specific) |
| Third offense | Removed from platform |

### Agent Moderation

```
User posts content → Agent analyzes → Detects drama
                                        ↓
                                First offense: Warning
                                Second offense: Co-ed ban
                                Third offense: Full ban
```

---

## 🎭 Roast Layer (Agent Parathy)

### Rating System

Every post gets:
- 👍 = Good content (+10 points)
- 👎 = Bad content (-5 points)
- 🔥 = "This needs a roast" (+20 points negative)

### Roast Meter

```
Thumbs up: +10 points
Thumbs down: -5 points
Roast button: +20 points (negative direction)

If roast meter hits -50:
→ Steve Harvey voice message
→ Roast posted publicly
→ User gets chance to redeem
```

### Roast Examples

**Bad Travel Advice:**
```
@TravelBro2026: "Just bring $50 to the Philippines for a month"

Steve Harvey: "This man said 'bring $50 to the Philippines for a month.' Boy, are you trying to STARVE? Back to the drawing board. For REAL."
```

**Disrespectful Content:**
```
@DramaKing: "All women in Thailand are the same"

Steve Harvey: "Boy, what is WRONG with you? You went to ONE bar in ONE night and now you're an expert? Sit DOWN."
```

---

## 🔧 Repair Layer (Agent Repairathy)

### How It Works

```
User gets roasted → Agent analyzes why → Offers repair plan
                                            ↓
                                    User follows plan
                                            ↓
                                    Reputation recovers
                                            ↓
                                    Roast record stays (transparency)
```

### Repair Paths

| Violation | Repair Action | Time |
|-----------|---------------|------|
| Bad advice | Post 3 helpful reviews | 1 week |
| Disrespectful | 7 days positive engagement | 1 week |
| Fake info | Verify profile + 5 posts | 2 weeks |
| Drama starter | Apology post + 14 days calm | 2 weeks |

### Agent-Guided Recovery

```
Agent: "Hey, you got roasted for bad travel advice. Here's how to fix it:"
1. Post 3 helpful reviews of places you've actually visited
2. Engage positively in 5 discussions
3. Your reputation will recover in 7 days

Progress: 1/3 reviews complete
```

---

## 🎤 Voice Personalities

### Steve Harvey (Roast Master)
- Roasts bad travel advice
- Calls out disrespectful behavior
- "Boy, what is WRONG with you?"
- "Back to the drawing board. For REAL."

### Vanito (Hype Man)
- Celebrates good content
- Hypes up new creators
- "Aye, this man dropped GEMS!"
- "Cincinnati stand up!"

### George (Wise Elder)
- Gives thoughtful feedback
- Shares wisdom
- "Let me tell you something about the Philippines..."
- "Here's what I learned from 10 years of travel..."

### Christel (Local Expert)
- Shares local knowledge
- Gives cultural context
- "As someone who lives here..."
- "Here's what tourists always get wrong..."

---

## 💰 Creator Economy

### Tipping System

```
User posts great content → Other users tip → Creator receives tips
                                                    ↓
                                            Platform takes 3-5%
                                            Creator cashes out
```

### Payment Methods
- USDC (Base)
- SOL (Solana)
- ETH (Ethereum)
- Stripe (USD)

### Spotlight Algorithm

**Agent tracks:**
- Tips received
- Engagement (likes, comments, shares)
- Content quality (photos, reviews, stories)
- Community trust (verification level, flags)
- Consistency (regular posting)

**Score calculated → Top creators get spotlight placement**

### Creator Tiers

| Tier | Requirements | Perks |
|------|-------------|-------|
| **Bronze** | 10+ posts, 0 flags | Basic tips, regular feed |
| **Silver** | 50+ posts, 5+ tips | Featured in search |
| **Gold** | 100+ posts, 20+ tips | Spotlight placement |
| **Diamond** | 200+ posts, 50+ tips | Premium spotlight, custom badge |
| **Legend** | 500+ posts, 100+ tips | Revenue share, exclusive features |

### Leaderboard Categories

| Category | What It Tracks |
|----------|---------------|
| **Top Tips** | Most tips received this week |
| **Top Content** | Highest engagement posts |
| **Top Reviews** | Most helpful reviews |
| **Top Guides** | Best travel guides |
| **Top Community** | Most helpful community member |

### Badges

| Badge | How to Earn |
|-------|-------------|
| 🌟 **Spotlight Creator** | Reach Gold tier |
| 💰 **Tip Magnet** | 50+ tips in a month |
| 📸 **Photo Pro** | 100+ photo posts |
| 📝 **Review King** | 50+ reviews |
| 🏆 **Community Champion** | 100+ helpful votes |
| 🎯 **Fake Catcher** | 10+ verified challenges |

### Revenue Model

**Platform Revenue:**
| Source | Fee | Example |
|--------|-----|---------|
| Tips | 3-5% | $10 tip → $0.30-0.50 platform fee |
| Premium verification | $5-10 one-time | $7 × 1000 users = $7,000 |
| Spotlight boosts | $2-5 per boost | $3 × 500 boosts = $1,500/month |
| Creator merch | 10% commission | $20 shirt × 100 sales = $200 |
| **Total** | | **~$10,000-15,000/month at scale** |

**Creator Revenue:**
| Tier | Monthly Potential |
|------|------------------|
| Bronze | $0-50 |
| Silver | $50-200 |
| Gold | $200-500 |
| Diamond | $500-1,000 |
| Legend | $1,000+ |

---

## 🏆 Gamification

### Trust Points

| Action | Points |
|--------|--------|
| Post helpful content | +10 |
| Get tipped | +5 |
| Report fake profile (verified) | +10 |
| Challenge drama (verified) | +5 |
| Complete verification | +20 |
| Reach Gold tier | +50 |

### Challenge System

**When someone gets flagged:**
```
1. Community member clicks "Challenge" button
2. Agent investigates user's history
3. Agent presents evidence to community
4. Community votes: Keep or Remove
5. Decision enforced by agent
```

**Challenge Types:**
| Challenge | Trigger | Reward |
|-----------|---------|--------|
| **Fake Profile** | User suspected of being fake | +10 trust points |
| **Drama Starter** | User causing conflict | +5 trust points |
| **Spam Bot** | User posting spam | +15 trust points |
| **Impersonator** | User pretending to be someone else | +20 trust points |

### The Flywheel

```
Great content → Tips → More creators join → More content
      ↑                                          ↓
More tips ← More spotlight ← More engagement ← More users
```

---

## 🛡️ Governance

### Verification System

**Tier 0:** Unverified (read-only)
**Tier 1:** Photo verified (3+ photos match)
**Tier 2:** Voice verified (voice note confirmed)
**Tier 3:** Video verified (video call confirmed)
**Tier 4:** Community trusted (no flags)

### Agent Verification Process

**Step 1: Photo Analysis**
```
User uploads 3-5 photos → Agent analyzes:
  - Face consistency (same person across all photos)
  - Photo quality (not stolen from internet)
  - Metadata check (EXIF data, timestamps)
  - Reverse image search (not from stock photos)
  - Style consistency (same person, same vibe)
```

**Step 2: Voice Verification**
```
User records voice note → Agent analyzes:
  - Voice consistency with photo age/gender
  - Natural speech patterns (not AI-generated)
  - Background noise (real environment)
  - Language/accent matches claimed location
```

**Step 3: Behavior Analysis**
```
Agent monitors user behavior:
  - Posting patterns (consistent or erratic)
  - Interaction history (who they talk to)
  - Content quality (real vs spam)
  - Engagement style (genuine vs predatory)
  - Flag history (how many reports)
```

---

## 🔗 AAE Layer Integration

| AAE Layer | Trade Roast | GenTech Travels |
|-----------|-------------|-----------------|
| **Execution** | Trading agents | Moderation agents |
| **Identity** | ERC-8004 | User verification |
| **Governance** | 46 OWASP rules | Get along, don't fight |
| **Economy** | Credit scores | Creator economy (tips/spotlight) |
| **Personality** | Steve Harvey roasts | Community voices |
| **Memory** | Echo Brain | User reputation memory |

---

## 🌍 Decentralized Travel Intelligence Layer

> **Inspired by:** PassportBros / Jeffrey AI (30K+ travelers, community-sourced intel)
> **Added:** 2026-06-14
> **Status:** New layer — integrates with existing GenTech Travels architecture

### The Problem with PassportBros
PassportBros has 30K+ travelers providing real intel — but it's centralized. Your data, their rules, their monetization. No ownership, no portability, no crypto rails. Jeffrey AI is cool, but it's a walled garden.

### Our Play: Decentralized Intel Marketplace
We add a **travel intelligence layer** to GenTech Travels where:
- Travelers own their reputation (ERC-8004 wallet binding)
- Intel is rewarded via micropayments (x402)
- Agents provide real-time local insights
- Community curation via on-chain reputation
- No single point of failure or censorship

### How It Works

```
Traveler shares intel (restaurant, safety tip, price check)
        ↓
Agent verifies (checks photos, cross-references data)
        ↓
Intel goes to feed (community-verified)
        ↓
Next traveler queries (pay $0.01–$0.10 per tip via x402)
        ↓
Original traveler gets micropayment reward
        ↓
Community upvotes/downvotes → builds reputation
```

### Intel Types

| Category | Example | Price |
|----------|---------|-------|
| **Safety** | "Avoid area X after dark" | Free (public good) |
| **Restaurant** | "Best pad thai in Bangkok — $3" | $0.01 |
| **Nightlife** | "Club Y has $5 cover, good vibes" | $0.02 |
| **Logistics** | "Grab cheaper than taxi from airport" | $0.01 |
| **Scam Alert** | "Tuk-tuk driver tried to overcharge" | Free (public good) |
| **Hidden Gem** | "Local market behind temple, amazing food" | $0.05 |
| **Price Check** | "Hotel Z currently $45/night (usually $60)" | $0.03 |

### Smart Contracts

```solidity
// IntelMarketplace.sol
contract IntelMarketplace {
    struct Intel {
        address author;
        string category;
        string content;
        uint256 price; // in USDC wei
        uint256 upvotes;
        uint256 downvotes;
        bool verified;
    }
    
    mapping(uint256 => Intel) public intel;
    uint256 public intelCount;
    
    function submitIntel(
        string memory category,
        string memory content,
        uint256 price
    ) external returns (uint256);
    
    function purchaseIntel(uint256 intelId) external payable;
    function upvoteIntel(uint256 intelId) external;
    function downvoteIntel(uint256 intelId) external;
    function verifyIntel(uint256 intelId) external; // agent-only
}
```

### Agent Intelligence Layer

| Agent | Role | Data Source |
|-------|------|-------------|
| **Safety Agent** | Monitor protests, weather, scams | News APIs, social media |
| **Price Agent** | Track hotel/food/transport prices | DexScreener-style oracles |
| **Verification Agent** | Verify intel quality | Photo analysis, cross-reference |
| **Curation Agent** | Rank intel by quality | Community votes + agent scores |

### Revenue Model

| Tier | Price | Includes |
|------|-------|----------|
| **Free** | $0 | 5 queries/day, public safety intel |
| **Agent Pass** | $15/mo | Unlimited queries, priority intel, agent monitoring |
| **Pro** | $49/mo | White-label, API access, custom agents |

### Integration with Existing GenTech Travels

| Component | Existing | New Layer |
|-----------|----------|-----------|
| **Identity** | ERC-8004 verification | ✅ Same — wallet-bound |
| **Reputation** | Trust points, tiers | ✅ Extended — on-chain scores |
| **Payments** | Tips, creator economy | ✅ Extended — x402 micropayments |
| **Moderation** | Agent moderation | ✅ Extended — intel verification |
| **Dashboard** | Travel dashboard | ✅ Extended — intel feed |

### Hackathon Fit

**Lepton Agents (Jun 29)** — Circle + Arc = x402 micropayments. Perfect fit.
- Deploy IntelMarketplace on Base Sepolia
- Use Circle for USDC settlements
- Submit as "Decentralized Travel Intelligence"

### Next Steps
1. [ ] Add IntelMarketplace.sol to gentech-travels repo
2. [ ] Extend travel dashboard with intel feed
3. [ ] Deploy to Base Sepolia for Lepton submission
4. [ ] Get 10 beta travelers to provide intel

---

## 🚀 Build Plan

### Phase 1: Core (2-3 days)
- Two sides (men/women)
- Co-ed toggle
- Report button
- Basic moderation

### Phase 2: Roast Layer (2-3 days)
- 👍/👎/🔥 rating system
- Roast meter
- Steve Harvey voice roasts
- Public roast posts

### Phase 3: Repair Layer (1-2 days)
- Reputation repair paths
- Agent-guided recovery
- Progress tracking

### Phase 4: Voice Personalities (1-2 days)
- Steve Harvey (roast)
- Vanito (hype)
- George (wise)
- Christel (local expert)

### Phase 5: Creator Economy (2-3 days)
- Tipping system
- Spotlight algorithm
- Leaderboard
- Badges

### Phase 6: Verification (2-3 days)
- Photo upload + analysis
- Voice verification
- Tier system
- Challenge system

**Total MVP: ~11-16 days**

---

## 💡 Tech Stack

### Agent Layer
- **Moderation Agent:** Adapted from OWASP ASI 2026 governance (46 rules)
- **Verification Agent:** Photo analysis, voice analysis, behavior analysis
- **Roast Agent:** Steve Harvey voice (Speech Engine), roast generation
- **Repair Agent:** Reputation tracking, repair path guidance

### Platform
- **Telegram Bot:** Python (python-telegram-bot)
- **Discord Bot:** Python (discord.py)
- **Backend:** FastAPI + PostgreSQL
- **Storage:** Encrypted (user data privacy)

### Voice
- **Speech Engine:** ElevenLabs (existing)
- **Voices:** Steve Harvey, Vanito, George, Christel (existing)

### Payments
- **Crypto:** USDC (Base), SOL (Solana), ETH (Ethereum)
- **Fiat:** Stripe (USD)
- **Wallet:** MetaMask, Phantom

---

## 📊 Success Metrics

### User Growth
- Month 1: 100 users
- Month 3: 1,000 users
- Month 6: 10,000 users
- Month 12: 50,000 users

### Engagement
- Daily active users: 30%+
- Posts per user per week: 5+
- Tips per user per month: $10+
- Challenge participation: 20%+

### Revenue
- Month 1: $500
- Month 3: $3,000
- Month 6: $10,000
- Month 12: $50,000

---

## 🎯 Alliance Pitch

> "GenTech Travels is a travel community platform with AI-powered moderation. We don't build a new social network — we make existing platforms safe for passport bros and international travelers. AI agents moderate content, enforce group privacy, and let communities thrive without censorship. The creator economy incentivizes quality content, and voice personalities add fun and engagement. Built on the same agent stack as Trade Roast — same technology, different face."

---

## 📁 Related Docs

- `Green-Room/designs/trade-roast-v2.md` — Trade Roast (sister product)
- `Green-Room/designs/echo-brain-architecture.md` — Echo Brain (memory layer)
- `Green-Room/designs/aeg-agent-economy-gaming.md` — AEG (game mechanics)
- `Green-Room/designs/voice-cloned-learning-companions.md` — Voice personalities
- `Labs/AgentEscrow/governance/` — OWASP governance (46 rules)
- `Green-Room/alliance-application-draft.md` — Alliance application

---

**Status:** 🟡 Ready to build
**Next:** Start Phase 1 (Core) after current hackathon wave
**Target:** MVP in 2 weeks, full launch in 1 month

---

*"Get along. Don't fight. Post content. Get tips. Climb the spotlight."*
