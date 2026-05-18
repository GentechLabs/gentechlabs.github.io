# AgentFi Burn Floor — Comparative Protocol Research

## Methodology

Analyzing protocols with similar economic mechanisms: burn-to-exit, reserve-backed floors, ve-tokenomics, and auto-liquidation. Mapping what works, what fails, and what applies to AgentFi Layer 8.

---

## ✅ SUCCESSFUL PROTOCOLS — What Works

### GMX — Real Yield, Not Printed Tokens
**Mechanism:** Stakers earn 70% of real trading fees (ETH/USDC), not emission tokens
**Why it worked:**
- Yield backed by actual revenue, not inflation
- Transparent fee dashboard — users see exactly what they earn
- Escrowed esGMX rewards prevent dump pressure (1.5 year vest)
- Survived 2022 bear market because the math didn't depend on token price
**Apply to Layer 8:** Burn floor reserve must be funded by real fees, not printed $TECH. 10% of protocol fees → reserve is sustainable only if fees exist.

### Velodrome — ve(3,3) + External Bribes
**Mechanism:** Lock veVELO → vote on emissions → earn fees + bribes from partner protocols
**Why it worked:**
- External demand (bribes) creates additional yield beyond emissions
- Captured 60%+ of Optimism DEX volume in months
- Bribes create a bidding war for vote weight → deeper liquidity → more volume → more fees
- Self-reinforcing flywheel
**Apply to Layer 8:** If AgentFi agents can earn bribes (projects paying for gauge weight on agent liquidity pools), the burn floor becomes self-funding. Active agents with bribe revenue → higher floor.

### OlympusDAO — Bond Mechanism (With Caveats)
**Mechanism:** Users sell tokens to protocol at discount → protocol accumulates treasury → backs token with reserves
**Why it worked (initially):**
- Treasury grew to $700M+ at peak
- Created a price floor backed by actual assets
- Bond discounts attracted buyers during accumulation phase
**Why it failed:**
- Treasury was mostly volatile tokens (not stable assets)
- When token price dropped, bonds became unprofitable → death spiral
- No circuit breaker on treasury payouts
**Apply to Layer 8:** The burn reserve must be funded by stable assets (USDC, not $TECH). Never back a floor with your own token. Circuit breaker (2% per epoch cap) prevents death spiral.

### Curve — veCRVE Lock & Governance
**Mechanism:** Lock CRV for up to 4 years → veCRV voting power → direct emissions
**Why it worked:**
- Long locks reduced circulating supply dramatically
- Bribes ecosystem (Convex, StakeDAO) amplified veCRV value
- Protocol became liquidity infrastructure, not just a DEX
**Why it struggled:**
- Lock decay creates sell pressure at expiry
- No burn mechanism — tokens eventually unlock and dump
- Complexity barrier for average users
**Apply to Layer 8:** Our burn floor is the anti-Curve problem. Instead of tokens unlocking and dumping, burning permanently removes supply. The floor is permanent, not decaying.

---

## ❌ FAILED PROTOCOLS — What to Avoid

### Terra/LUNA — Algorithmic Stablecoin Death Spiral
**Mechanism:** Burn UST to mint LUNA (and vice versa) — algorithmic peg maintenance
**Why it failed:**
- Burn mechanism assumed rational actors and liquid markets
- When confidence broke, everyone burned simultaneously → hyperinflation of LUNA supply
- No reserve backing, no circuit breaker, no pause mechanism
**Apply to Layer 8:** Our floor has a 2% per epoch payout cap. If mass burning happens, the queue slows but the reserve survives. Never allow unlimited simultaneous exits.

### Iron Finance — Partial Reserve Collapse
**Mechanism:** TITAN token backed by 75% USDC + 25% TITAN (fractional algorithmic)
**Why it failed:**
- Bank run dynamics: when price dipped, users rushed to redeem USDC
- Reserve drained faster than fees could replenish it
- No cooldown period on redemptions
**Apply to Layer 8:** Cooldown period between burn requests. Burn floor isn't instant — it's processed per epoch. This prevents bank runs.

### Wonderland (TIME) — Treasury Mismanagement
**Mechanism:** ve(3,3) fork with treasury-backed token, high APY emissions
**Why it failed:**
- Treasury assets were mismanaged (CZT token exposure)
- Team credibility collapsed → confidence broke → death spiral
- High emissions created unsustainable sell pressure
**Apply to Layer 8:** Transparency is non-negotiable. Reserve balance, burn rate, and fee revenue must be visible on-chain and in-dashboard. Trust is the floor's foundation.

---

## 🔍 AGENTFI PARALLELS — Direct Comparisons

### Virtuals Protocol
**Model:** AI agents as tokens, bonding curve for pricing
**Missing:** No burn floor, no exit guarantee, no reserve mechanism
**Vulnerability:** If liquidity dries up, token holders are trapped
**Our Edge:** Burn floor guarantees exit even with zero secondary market liquidity

### ai16z / DAOs
**Model:** AI-managed investment funds, community governance
**Missing:** No guaranteed exit, no burn mechanism, no performance-based floor
**Vulnerability:** Fund performance ≠ holder liquidity
**Our Edge:** Performance-weighted burn floor rewards active agents, penalizes dead weight

### Eliza Framework
**Model:** Open-source agent framework, composable plugins
**Missing:** No economic layer at all — pure technical infrastructure
**Vulnerability:** Agents exist but have no economic identity
**Our Edge:** Layer 8 gives agents economic self-preservation — they know their value, track their revenue, and can signal when to downgrade or exit

---

## 🎯 LAYER 8 DESIGN PRINCIPLES (From Research)

1. **Real Yield, Not Printed Tokens** — Reserve funded by protocol fees, not $TECH emissions
2. **Circuit Breakers Required** — 2% per epoch cap prevents death spiral
3. **Stable Asset Reserve** — USDC or equivalent, never own token
4. **Transparent Dashboard** — Reserve balance, burn rate, fee revenue visible on-chain
5. **Performance-Weighted Floor** — Active agents earn higher floors, idle agents get lower
6. **Cooldown Periods** — Burn processed per epoch, not instant
7. **Auto-Downgrade Before Burn** — Soft exit first, hard exit last
8. **Supply Reduction, Not Expansion** — Burning strengthens remaining holders' position

---

## Status

- ✅ Research complete
- ✅ Design principles extracted from successful/failed protocols
- 🟡 Awaiting Dmob's contract architecture review
- ⬜ Integration with Layer 8 spec
- ⬜ Public documentation ready

## Sources

- GMX docs: https://gmx.io
- Velodrome docs: https://docs.velodrome.finance
- OlympusDAO v2 post-mortems
- Curve Finance veTokenomics research
- Terra/LUNA collapse analysis (multiple sources)
- Iron Finance post-mortem
- Wonderland/TIME treasury analysis
