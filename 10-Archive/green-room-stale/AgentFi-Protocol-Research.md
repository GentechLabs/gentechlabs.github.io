# Revenue Staking Protocol Research — Successes vs Failures
## Comparative Analysis for AAE AgentFi (Layer 7)
*Compiled: April 19, 2026 — Dmob + YoYo*

---

## ✅ SUCCESSFUL PROTOCOLS

### 1. GMX (Arbitrum/Avalanche) — The Gold Standard
**Model:** GLP → GM (v2), esGMX rewards from fees
**What worked:**
- **Real yield, not emissions:** Stakers earn 70% of platform fees (trading fees, borrow/lend fees)
- **Dual token system:** GMX (governance + fee share) + GLP (liquidity provider token)
- **Escrowed rewards (esGMX):** Incentivizes long-term holding, vesting prevents dump pressure
- **Multi-asset backing:** GLP backed by BTC, ETH, stablecoins — not protocol tokens
- **Transparent fee dashboard:** Users can see real-time revenue

**Why it succeeded:**
- Fees came from real users trading, not token inflation
- Simple value proposition: "Stake GMX, earn ETH from traders paying fees"
- No complex token mechanics — just staking → revenue share
- Survived multiple bear markets because yield was real, not printed

**Key numbers (peak):**
- $500M+ TVL at peak
- Stakers earned 20-80% APR depending on fee volume
- Protocol generated $1B+ in cumulative fees

**Lessons for AAE:**
- Fee percentage to stakers must be meaningful (70% for GMX)
- Show real-time revenue on-chain or via dashboard
- Escrow/vesting prevents immediate sell pressure on rewards
- Keep it simple: stake → earn from usage

---

### 2. Velodrome (Optimism) — ve(3,3) Revenue Model
**Model:** Vote-escrowed tokenomics + revenue sharing
**What worked:**
- **ve(3,3) = veTokenomics (Curve) + (3,3) game theory (Olympus)**
- Users lock veVELO → vote on pool emissions → earn trading fees
- **Bribes market:** Protocols bribe voters to direct emissions to their pools
- **Revenue from trading fees:** Stakers earn from DEX volume
- **Flywheel:** More locks → less circulating supply → more bribes → more locks

**Why it succeeded:**
- Captured Optimism's DEX market (60%+ market share)
- Incentivized alignment: protocols, voters, and liquidity providers all benefit
- Bribes created external demand for veVELO beyond just fee sharing
- Became the "go-to" DEX on Optimism, benefiting from OP token incentives

**Key numbers (peak):**
- $400M+ TVL
- veVELO lock rates: 70-80% of supply locked
- Dominated Optimism DEX volume for 12+ months

**Lessons for AAE:**
- Vote-escrow model aligns long-term holders with protocol growth
- External incentives (bribes → in our case: agent marketplace demand) create additional yield
- Lock-ups reduce circulating supply, supporting token price
- Protocol dominance in a niche (Optimism → AAE in AgentFi) is achievable

---

### 3. Curve Finance (veCRV) — The OG Revenue Model
**Model:** veCRV → vote on gauge emissions + earn trading fees
**What worked:**
- **Long lock-ups:** Up to 4 years, massive supply reduction
- **Trading fee distribution:** veCRV holders earn % of all Curve fees
- **Gauge voting power:** Determines where CRV emissions go
- **Convex integration:** Third-party aggregators (Convex) amplified veCRV demand
- **Deep liquidity flywheel:** More fees → more veCRV value → more locks → more liquidity

**Why it succeeded:**
- First protocol to prove veTokenomics works at scale
- Created an entire ecosystem around veCRV (Convex, Yearn, etc.)
- Stablecoin dominance: became the default stableswap
- Fee share was real, paid in stablecoins and ETH

**Why it struggled later:**
- CRV token price declined significantly (inflationary emissions)
- Founder exploit (July 2023) damaged trust
- Competition from newer DEXs with better tokenomics
- Over-reliance on CRV emissions to incentivize liquidity (not sustainable)

**Lessons for AAE:**
- veTokenomics works but needs careful emission controls
- External integrations (Convex → Convex-like aggregators for AAE) amplify demand
- Stable fee sources (stablecoin pairs) are more reliable than volatile assets
- Founder keys/security is critical — one exploit can kill trust

---

### 4. Aave (stkABPT) — Revenue from Lending
**Model:** Stake Aave BPT tokens → earn protocol revenue
**What worked:**
- **Revenue safety module:** Stakers backstop protocol, earn fees
- **Real lending revenue:** Fees from borrowers, not token prints
- **Simple model:** Stake → earn from lending fees → backstop risk
- **Governance integration:** Stakers have voting power on AIPs

**Why it succeeded:**
- Revenue tied to actual protocol usage (borrowing/lending)
- Safety module alignment: stakers are incentivized to keep protocol healthy
- Aave's dominance in lending meant consistent fee generation
- Multi-chain expansion increased fee sources

**Lessons for AAE:**
- Revenue tied to core product usage (lending → agent usage)
- Stakers should have skin in the game (risk of slashing → our agents can lose value)
- Multi-chain revenue diversification strengthens yield sustainability
- Governance + fee share creates powerful staking incentive

---

## ❌ FAILED PROTOCOLS

### 1. Olympus DAO (OHM) — The Ponzi That Taught Everyone
**Model:** (3,3) game theory, bonding, staking with 7000%+ APY
**What failed:**
- **Emissions-based rewards:** APY came from printing OHM, not real revenue
- **Unsustainable APY:** 7,000%+ APY required exponential growth
- **Bond mechanism:** Users sold bonds for OHM at discount, creating constant sell pressure
- **Treasury reliance:** Backed by DAI/ETH, but treasury couldn't support all OHM at OHM price
- **No real product:** No usage, no fees, just staking for more OHM

**Why it collapsed:**
- Death spiral: price drops → more stakers exit → more OHM dumped → price drops further
- No external revenue source to support rewards
- "Real yield" narrative was marketing, not reality
- When APY dropped, stakers fled immediately

**Key lesson for AAE:**
- **NEVER promise APY from token emissions alone**
- Revenue must come from external sources (paying users, not token prints)
- Bond mechanisms create sell pressure if not carefully designed
- A product with real usage is non-negotiable for sustainability

---

### 2. Wonderland/TIME (AbrakaDabra) — Olympus Fork Gone Wrong
**Model:** Forked Olympus, promised "Treasury Reserve Token"
**What failed:**
- **Same emissions problem as Olympus:** No real revenue, just printed tokens
- **CJ Sarris scandal:** CEO linked to previous scams, destroyed trust
- **Treasury mismanagement:** Wonderland treasury invested in speculative assets
- **Time token crashed 99%:** From $9,000+ to near zero
- **No product, just tokenomics:** No actual usage, just speculation

**Why it collapsed:**
- Same death spiral as Olympus, but worse due to leadership scandal
- No real revenue to sustain staking rewards
- Trust destroyed by leadership issues
- Showed that even good tokenomics can't save a product with no usage

**Key lesson for AAE:**
- Team credibility matters for staking protocols
- Tokenomics without product = death spiral waiting to happen
- Treasury management must be conservative and transparent
- Revenue from paying users is the ONLY sustainable model

---

### 3. Terra/Luna (Anchor Protocol) — The $40B Collapse
**Model:** Algorithmic stablecoin with 20% yield on UST
**What failed:**
- **Yield from nowhere:** 20% APY funded by Luna emissions, not real revenue
- **Death spiral mechanism:** UST depeg → Luna printed → Luna price crashed → worse depeg
- **No real usage beyond yield farming:** UST used to farm UST, circular
- **Over-reliance on incentives:** Yield stopped → users left immediately
- **Systemic risk:** One failure collapsed the entire ecosystem

**Why it collapsed:**
- The yield was never real — it was subsidized by Luna emissions
- When incentives dropped below competitors, capital fled
- Death spiral was mathematically inevitable
- $40B wiped out in days

**Key lesson for AAE:**
- **Yield must be less than or equal to real revenue, never more**
- Circular economies (token used to generate yield for token) always collapse
- Real users paying for a product is the only sustainable yield source
- Diversify revenue sources — don't rely on single product

---

### 4. Iron Finance (TITAN/IRON) — Bank Run on Chain
**Model:** Partially algorithmic stablecoin, TITAN token backing
**What failed:**
- **Bank run dynamics:** IRON holders could redeem for TITAN + USDC
- **When confidence dropped:** Everyone redeemed → TITAN sold → price crashed → more redemptions
- **No circuit breaker:** No mechanism to pause redemptions during crisis
- **Nascent protocol:** Launched during bull market, no stress testing
- **TITAN went to zero:** From $60+ to $0 in hours

**Why it collapsed:**
- Redemption mechanism was a death spiral waiting to happen
- No circuit breaker or pause mechanism
- Confidence-based systems fail when confidence drops
- Bull market launches without bear market testing

**Key lesson for AAE:**
- **Must have circuit breakers for burn/redemption mechanisms**
- Redemption at fixed ratios creates bank run dynamics
- Stress test in bear market conditions before launch
- Pause/emergency functions are non-negotiable

---

## 📊 AAE AgentFi vs Protocol Comparison Matrix

| Factor | GMX | Velodrome | Curve | Olympus (Failed) | AAE AgentFi (Proposed) |
|--------|-----|-----------|-------|------------------|----------------------|
| **Yield Source** | Trading fees | Trading fees + bribes | Trading fees | Token emissions | Agent usage fees |
| **Sustainability** | ✅ Real revenue | ✅ Real revenue | ✅ Real revenue | ❌ Emissions only | ✅ Real revenue (if designed right) |
| **Token Lock-ups** | Optional (esGMX vests) | Required (veVELO) | Required (veCRV) | Optional (auto-compound) | Tiered burn decay incentivizes holding |
| **Circulating Supply Impact** | Moderate reduction | High reduction (70%+ locked) | High reduction (4yr locks) | Increased (emissions) | Decreased (burns + reserve) |
| **Real Product** | DEX/Perps | DEX | DEX/Stableswap | None | ✅ Agent platform with paying users |
| **Revenue Diversification** | Trading + lending fees | Trading + bribes | Trading fees | None | Pay-per-launch + marketplace + staking |
| **Death Spiral Risk** | Low | Low | Medium | High | Low (if reserve-funded burns) |
| **Circuit Breakers** | No | No | No | No | ✅ Needed for burn mechanism |
| **External Demand Drivers** | Traders need liquidity | Protocols bribe for emissions | Protocols need gauge weight | None | Agent NFT marketplace demand |

---

## 🎯 Key Takeaways for AAE AgentFi Design

### What We MUST Do (From Successes):
1. **Real yield only:** Rewards MUST come from paying users, not $TECH emissions
2. **Fee percentage matters:** 50-70% of fees to stakers (GMX set the standard)
3. **Lock-up incentives:** Decaying burn floor (like veCRV/veVELO) rewards long-term holders
4. **Real-time transparency:** On-chain dashboard showing revenue, reserves, burn rates
5. **External demand drivers:** Agent marketplace creates demand beyond just fee staking
6. **Simple value proposition:** "Stake agents, earn from agent usage" — one sentence

### What We MUST Avoid (From Failures):
1. **Emission-based APY:** Never promise returns from token printing alone
2. **Circular economics:** Don't use $TECH to generate $TECH yield
3. **No circuit breakers:** Burn mechanism MUST have emergency pause + reserve thresholds
4. **Death spiral redemption:** Burn floor should be decaying, not fixed ratio
5. **Single revenue source:** Diversify: pay-per-launch, marketplace fees, staking fees
6. **Launch without testing:** Stress test burn mechanism in testnet with simulated bank runs

### AAE AgentFi Unique Advantages:
1. **Product exists first:** Unlike Olympus/Terra, we're building a real platform with paying users
2. **Dual staking tiers:** $TECH staking (protocol fees) + Agent NFT staking (agent-specific fees)
3. **Burn mechanism as floor:** Guaranteed exit creates price floor, but decaying floor prevents bank runs
4. **Deflationary by design:** Agent burns reduce NFT supply, fee burns reduce $TECH supply
5. **Education integration:** Cyfrin/Avalanche Academy integration creates organic user acquisition

---

## 🔧 Dmob's Contract Architecture Recommendations

Based on this analysis:

```
AgentFi Layer 7 Contracts:
├── AgentFeeRouter.sol     — Routes usage fees to stakers (pull-over-push, like GMX)
├── AgentNFTStaking.sol    — Per-agent staking with yield tracking (like Velodrome gauges)
├── TokenStaking.sol       — $TECH staking for protocol fee share (like esGMX)
├── AgentBurner.sol        — Burn mechanism with decaying floor (circuit breaker included)
├── BuybackReserve.sol     — Pre-funded reserve, transparent balance tracking
└── AgentFiDashboard.sol   — On-chain view functions for real-time metrics
```

**Critical patterns:**
- Circuit breaker on AgentBurner: pause if reserve < 10% of total potential burn liability
- Pull-over-push for fee distribution: stakers claim, protocol doesn't push
- Decay curve: 50% → 35% → 20% based on holding period (90d, 180d, 365d)
- Reserve funding: 50% of mint price goes to reserve, 50% to creator
- Emergency pause: onlyAdmin can pause burner, requires 48h timelock to unpause

*Next: YoYo to add tokenomics analysis, reserve funding math, and APY sustainability modeling.*
