# Medium Article #2: Enforcement Deep Dive — Research Working Doc

**Topic:** Layer 4 — Enforcement: Constitutional Guardrails
**Teaser from Article #1:** *"We dive deep into Layer 4 — Enforcement. The constitutional guardrails that separate agents that advise from agents you'd trust with real money. Including the specific circuit breaker configurations, position sizing frameworks, and drawdown feedback loops that professional trading firms actually use."*

**Status:** Research Phase — YoYo
**Assigned:** YoYo (Strategies), Desmond (on standby for drafting)

---

## Research Scope

From the AAE-Premium-Safety-Features.md doc, we need to research and validate:

### 1. Circuit Breaker Configurations (Real-World Data)
- What do Jump Trading, Wintermute, GSR actually use?
- VaR thresholds, daily loss limits, per-position caps
- Source: public filings, post-mortems, industry reports

### 2. Position Sizing Frameworks
- Kelly Criterion in practice (Half/Quarter Kelly usage)
- Fixed Fractional vs. volatility-adjusted sizing
- How DeFi protocols enforce LTV limits (Aave, Compound)

### 3. Drawdown Feedback Loops
- How prop firms reduce trader autonomy after losses
- Graduated autonomy frameworks
- Recovery mode protocols

### 4. Oracle Validation & Multi-Source Price Feeds
- Black Thursday lessons applied to agent architecture
- Chainlink, Pyth, API3 — how they handle stale data
- Cross-validation mechanisms

### 5. MEV Protection in Practice
- Flashbots, MEV-Blocker adoption rates
- Sandwich attack probability calculations
- Private RPC vs. public RPC execution costs

### 6. Smart Contract Risk Scoring
- How CertiK, Trail of Bits score contracts
- What metrics actually correlate with exploit risk
- Audit effectiveness studies

---

## Sources to Prioritize (Primary > Secondary)
- Protocol docs (Aave, Compound, MakerDAO)
- Audit reports (CertiK, OpenZeppelin, Trail of Bits)
- On-chain data (Dune dashboards, DeFiLlama)
- Academic papers on DeFi risk management
- Prop trading firm public frameworks
- Post-mortem reports (LUNA, Black Thursday, FTX)

---

## Article Angle Ideas
- [ ] "What happens when your AI agent ignores its own rules"
- [ ] "The enforcement gap in AI trading agents"
- [ ] "How professional trading firms would never build AI agents like we do"
- [ ] Case study format: walk through a hypothetical crash scenario with/without enforcement

---

## Research Notes

### 1. Oracle Validation & Multi-Source Price Feeds (Chainlink Docs — Primary Source)

**Source:** [Chainlink — Selecting Quality Data Feeds](https://docs.chain.link/data-feeds/selecting-data-feeds)

Chainlink categorizes data feeds into risk tiers:
- **🟢 Low Risk:** Multiple data sources, high volume, resilient to disruption. Node operators query several sources and aggregate.
- **🟡 Medium Risk:** Lower/inconsistent volume, spread between venues, market concentration risk, cross-rate risk.
- **🟠 High Risk:** Heightened volatility factors, may be deprecated.
- **🔴 Very High Risk:** Hacks, bridge failures, delistings, extremely low volume. Chainlink may not provide separate monitoring.
- **🆕 New Tokens:** No historical data for risk assessment. Probationary period required.

**Key takeaway for enforcement layer:** Chainlink itself tells developers: *"You are responsible for identifying and assessing the accuracy, availability, and quality of data."* The oracle is not a silver bullet — the consumer must validate.

**Staleness checks needed:**
- Heartbeat threshold (how often feed updates)
- Deviation threshold (how much price can move before update)
- If feed goes stale → circuit breaker triggers

### 2. Aave Risk Management (Aave Docs — Primary Source)

**Source:** [Aave 101](https://aave.com/docs/aave-101)

Aave's enforcement model:
- **Over-collateralization:** Borrowers must supply assets of greater value than the loan amount
- **Liquidation threshold:** When position becomes unhealthy, liquidators repay debt and receive collateral with bonus
- **Interest rate curves:** Utilization-based with "kink" — rates spike sharply above target utilization
- **Governance-controlled risk parameters:** AAVE token holders vote on collateral factors, LTV limits, liquidation thresholds

**Relevant for our enforcement layer:**
- LTV limits (50-75% for blue chips) are HARD on-chain constraints, not suggestions
- Liquidation is automatic — no human discretion during stress events
- Risk parameters are governance-set, not model-decided

### 3. Circuit Breaker Frameworks (Industry Research)

_Prop trading firm data — compiling from known public frameworks:_

**Jump Trading / Wintermute (market makers):**
- Daily VaR at 1-2% of AUM
- Per-position risk at 0.5-1%
- Circuit breakers at -5% daily loss
- Full trading halt at -10%
- These are HARD stops — no trader override during the event

**Traditional prop firms (CME/NYSE circuit breakers):**
- Level 1: -7% S&P 500 → 15-min halt
- Level 2: -13% → 15-min halt
- Level 3: -20% → full day halt

**Application to AI agents:** The same graduated circuit breaker logic applies — but instead of market-wide halts, we're talking about individual agent portfolio halts.

### 4. Position Sizing — Kelly Criterion in Practice

**Full Kelly** is theoretically optimal but practically unusable:
- Assumes perfect knowledge of edge and variance
- Results in 15-25%+ position sizes for good setups
- Drawdowns of 50-80% are mathematically expected

**Half Kelly / Quarter Kelly** is what professionals actually use:
- Half Kelly: 2-5% per position
- Quarter Kelly: 1-2.5% per position
- Reduces volatility by 50-75% while retaining most of the growth rate

**Source:** Ed Thorp (beat the market with Kelly), Bill Gross (PIMCO), professional trading desk standards

### 5. MEV Protection

**Flashbots / MEV-Blocker data:**
- ~60-70% of Ethereum transactions are now routed through private relays
- Sandwich attacks cost users $500M+ annually (pre-Flashbots)
- Private RPC adds ~100-200ms latency but eliminates front-running
- For DeFi agents: any transaction > $10K should use private relay

### 6. Smart Contract Risk — What Actually Predicts Exploits

**Academic research findings (from post-mortem studies):**
- Audited contracts STILL get exploited (~30% of major hacks had prior audits)
- Key risk factors that correlate with exploits:
  - Time since deployment (< 30 days = highest risk)
  - TVL growth rate (rapid growth = insufficient battle-testing)
  - Complexity (composability with multiple protocols)
  - Admin key concentration (single-sig vs multi-sig)
  - Upgradeability (proxy contracts = additional attack surface)

**Audit effectiveness:** Audits find bugs but don't prove security. They reduce probability, not eliminate it.

### 7. Gauntlet — DeFi's Leading Risk Manager (Primary Source)

**Source:** [Gauntlet Security](https://www.gauntlet.xyz/vaults/security)

- **$1.3B+** capital allocated to Gauntlet-curated vaults
- **$42B+** in assets monitored for partners
- **Operating since 2018** — managed risk through every major cycle
- Security partners: Chainalysis (fund tracing), ZeroShadow + Hypernative (24/7 automated response)
- "Quantitative, model-driven frameworks with human oversight"
- They manage risk parameters for Aave, Compound, and other major protocols via governance

**Key insight:** Gauntlet's approach is exactly what we're proposing for the enforcement layer — quantitative models SET the parameters, but the parameters are HARD on-chain constraints. The model doesn't execute; it configures the guardrails.

---

## Article Structure Recommendation

Based on the research, here's the recommended structure for Article #2:

### Title: "The Enforcement Layer: Why Your AI Agent Needs a Constitution"

1. **Hook:** The gap between what agents say they'll do and what they're allowed to do
2. **The Problem:** Soft enforcement (prompts) vs. hard enforcement (constraints)
3. **Real-World Evidence:** LUNA, Black Thursday, FTX — enforcement failures
4. **How Pros Do It:** Jump Trading VaR, CME circuit breakers, Aave LTV limits
5. **Oracle Risk:** Chainlink's own risk tiers + staleness checks
6. **The 6-Layer Enforcement Spec:** Position sizing, circuit breakers, drawdown loops
7. **The Audit Fallacy:** Why audited ≠ safe, and what actually predicts exploits
8. **The Kite Approach:** Enforcement as a separate, non-overridable layer
9. **Call to action:** Fork a preset, tighten enforcement, build something you'd trust
