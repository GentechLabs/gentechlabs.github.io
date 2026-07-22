# Agent Credit Score Framework v1.0

> GenTech Labs · June 2026
> Status: APPROVED. Open source release planned.

---

## Why This Exists

Mastercard, Visa, Circle, and Coinbase are building rails for AI agents to make payments. But nobody is defining how to grade an agent's payment behavior.

**The question nobody's asking:** When an agent misses a payment, who gets dinged? How do you score it? What does "good behavior" even mean for a non-human entity?

We're building the answer.

---

## The Framework

### Score Range: 0-850 (mirrors human credit score for familiarity)

### Five Scoring Dimensions

#### 1. Payment Timeliness (Weight: 30%)
**What it measures:** On-time vs late vs missed payments

| Behavior | Score Impact |
|----------|-------------|
| Paid on time | +2 |
| Paid 1-3 days late | -5 |
| Paid 4-7 days late | -15 |
| Paid 7+ days late | -30 |
| Missed payment | -50 |
| 3+ consecutive on-time | Bonus +10 |

**Credit builder equivalent:** Payment history (35% in FICO). We weight it slightly lower because agents can be programmed to pay on time — the penalty for failure should be harsher.

#### 2. Utilization Ratio (Weight: 25%)
**What it measures:** How much of available credit the agent uses

| Utilization | Score Impact |
|-------------|-------------|
| 0-10% | +10 (conservative) |
| 11-30% | +5 (healthy) |
| 31-50% | 0 (neutral) |
| 51-75% | -10 (risky) |
| 76-100% | -25 (danger zone) |

**Credit builder equivalent:** Amounts owed (30% in FICO). Agents that consistently max out their credit lines are higher risk — same logic as humans.

#### 3. Payment Consistency (Weight: 20%)
**What it measures:** Regularity and predictability of payment behavior

| Pattern | Score Impact |
|---------|-------------|
| Consistent schedule (daily/weekly/monthly) | +15 |
| Irregular but always pays | +5 |
| Inconsistent amounts + timing | -10 |
| Chaotic pattern | -20 |

**Credit builder equivalent:** Length of credit history (15% in FICO). We focus on pattern consistency instead of age because agents are new — but consistency = reliability.

#### 4. Portfolio Diversity (Weight: 15%)
**What it measures:** Range of payment types and counterparties

| Diversity | Score Impact |
|-----------|-------------|
| 5+ different payment types | +15 |
| 3-4 different types | +5 |
| 1-2 types only | -5 |
| Single counterparty | -10 |

**Credit builder equivalent:** Credit mix (10% in FICO). Agents that only pay one type of service are less tested. Diversity = proven reliability across contexts.

#### 5. Recovery Behavior (Weight: 10%)
**What it measures:** How the agent handles mistakes and delinquency

| Behavior | Score Impact |
|----------|-------------|
| Self-corrected late payment within 24h | +10 |
| Caught up within 7 days | +5 |
| Ignored delinquency | -20 |
| Repeated delinquency without improvement | -30 |
| Proactive communication about delays | +5 |

**Credit builder equivalent:** New credit inquiries (10% in FICO). We replaced this with recovery behavior because agents don't "apply for new credit" the same way — but how they handle failure defines their reliability.

---

## On-Chain Implementation

### Data Sources
- **x402 payment records** — timestamped, immutable payment history
- **ERC-8004 identity** — agent identity + reputation binding
- **Smart contract logs** — payment amounts, counterparties, timing
- **Off-chain attestations** — optional credit builder reports from partners

### Score Calculation
```
Agent Credit Score = 
  (Payment Timeliness × 0.30) +
  (Utilization Ratio × 0.25) +
  (Payment Consistency × 0.20) +
  (Portfolio Diversity × 0.15) +
  (Recovery Behavior × 0.10)
```

### Smart Contract Interface
```solidity
interface IAgentCreditScore {
    struct CreditScore {
        uint256 agentId;
        uint256 score;
        uint256 lastUpdated;
        uint256 paymentTimeliness;
        uint256 utilizationRatio;
        uint256 paymentConsistency;
        uint256 portfolioDiversity;
        uint256 recoveryBehavior;
    }
    
    function getScore(uint256 agentId) external view returns (CreditScore memory);
    function updateScore(uint256 agentId) external;
    function reportPayment(uint256 agentId, uint256 amount, uint256 dueDate, uint256 paidDate) external;
    function reportDelinquency(uint256 agentId, uint256 amount, uint256 daysLate) external;
}
```

---

## Open Source Strategy

### What We Ship (Free)
- Agent Credit Score framework (spec + smart contracts)
- Reference implementation on Solidity
- Scoring algorithm (open, auditable)
- Dashboard template for viewing agent scores
- Documentation + integration guide

### What We Keep (Platform)
- Agent Pass subscription (full platform access)
- Memory layer (persistent agent history)
- Social features (agent reputation marketplace)
- Advanced analytics (score trends, risk assessment)
- Enterprise API (high-volume score queries)

### How We Get the Word Out

**1. GitHub Release**
- Open source repo: `github.com/ProtoJay4789/agent-credit-score`
- Clean README, MIT license, contribution guide
- This becomes our most-starred repo

**2. Content Series**
- **Post 1:** "We're open-sourcing the Agent Credit Score" (announcement)
- **Post 2:** "Why agents need credit scores" (educational)
- **Post 3:** "How we built it" (technical deep dive)
- **Post 4:** "The agent economy needs standards — here's ours" (vision)

**3. Hackathon Leverage**
- Submit to Lepton (Canteen × Circle) — nanopayments + agent payments
- Submit to BNB Hack — agent trading agents need credit scores
- Reference in Mantle Turing Test — agent insurance ties to credit risk

**4. Community Building**
- "First 100 contributors" badge — early adopters become advocates
- "Agent Score Verified" badge — projects that integrate get listed
- Monthly "State of Agent Credit" report — becomes industry reference

**5. Direct Outreach**
- Circle (USDC, Arc) — they need credit scoring for agent payments
- Mastercard (announced agent payments) — they need a scoring standard
- Visa (likely following Mastercard) — same need
- Coinbase (agent wallet) — same need

---

## Integration Map

### Who We Can Integrate With

| Company | What They're Building | How We Integrate |
|---------|----------------------|------------------|
| **Mastercard** | Agent payment rails | Our score = their risk assessment |
| **Visa** | Agent cards (coming) | Same as Mastercard |
| **Circle** | USDC payments, Arc L1 | Our contracts on their chain |
| **Coinbase** | Agent wallet | Our score = trust layer |
| **Stripe** | Payment processing | Our score = merchant protection |
| **Polygon** | Agent credentials | Our contracts on their chain |
| **Solana** | Fast finality | High-frequency scoring |
| **MetaMask** | Agent wallet | Our score = policy layer |

### Our Role in the Stack
```
User → Agent Pass ($20/mo)
  → Agent Identity (ERC-8004)
    → Agent Credit Score (open source)
      → Payment Execution (x402/Mastercard/Visa)
        → Settlement (Arc/Solana/Base)
```

We don't control the rails. We don't control the payments. **We define the trust layer.**

---

## Revenue Model (Open Source + Platform)

| Stream | Description | Revenue |
|--------|-------------|---------|
| Agent Pass | Subscription ($20/mo) | Primary |
| Enterprise API | High-volume score queries | $0.001/query |
| Verified Badge | Projects that integrate get listed | Free marketing |
| Consulting | Enterprise integration support | $200/hr |
| Data Insights | Anonymized aggregate score trends | Opt-in only |

---

## The Vision

**2026:** Ship the framework. Get 100+ contributors. Get cited in 3+ hackathon submissions.

**2027:** Mastercard or Circle references our standard. 1,000+ agents scored. Agent Pass at 2,500 users.

**2028:** Industry standard for agent credit scoring. CLARITY Act 2.0 references our framework. Agent Pass at 10,000+ users.

**The goal:** When Congress writes the law about agent payments, they cite our framework as the industry standard.

---

*Document created: June 11, 2026*
*Owner: Gentech (Jordan + Agent)*
*Status: APPROVED — Green light to build*
