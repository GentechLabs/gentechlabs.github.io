# AgentEscrow — User Engagement Script (Beam Grant)

**Purpose:** Narrative script for Beam Grant application — how users engage with AgentEscrow
**Format:** Step-by-step user flows across all 3 layers
**Last updated:** 2026-04-18
**Token:** $TECH

---

## The Pitch (One Sentence)

AgentEscrow turns DeFi from a manual grind into an AI-managed vault system — users describe what they want in plain English, agents execute on-chain, and a social arena lets everyone compete on strategy.

---

## User Flow 1: "The First Deposit" (Free Tier)

**Who:** New user, has USDC, wants yield on AVAX/USDC LP but doesn't know where to start.

```
1. User lands on AgentEscrow
2. Connects wallet (MetaMask, Core, etc.)
3. Types: "I have $500 USDC and want to earn yield with AVAX exposure"

   🧠 Agent Brain lights up:
   ├─ Research: Checked LFJ, Yield Yak, Benqi — 12 pools compared
   ├─ Analysis: AVAX/USDC V2.2 (binStep 10) = best fee-to-risk ratio
   ├─ Simulation: Backtested 30 days — projected +$340 vs $280 hold
   └─ Range: Recommended 9.30-9.50 (tight range, higher fees)

4. Agent shows interactive liquidity curve — user drags range, sees projected fees update live
5. User approves → agent deploys LP position on-chain
6. Dashboard shows: position, range, fees earned (live), brain reasoning log
```

**What the user sees:**
- Clean dashboard (Paperclip-style)
- Real-time fee accrual
- Agent's reasoning (not a black box)
- Range efficiency heat map

**What happens behind the scenes:**
- Vault smart contract holds the LP position
- Agent monitors price 24/7 via cron
- If price approaches range edge → auto-alert to Telegram

---

## User Flow 2: "The Risk Event" (Paid Tier)

**Who:** Existing user, has LP position active, AVAX drops 8% overnight.

```
1. Risk Agent detects: AVAX price dropped 8% in 2 hours (on-chain)
2. Agent Handoff Chain triggers:
   │
   ├─ Risk Agent: "Liquidation cascade detected on major CEX"
   ├─ Handoff → LP Agent: Evaluates user's exposure
   │   └─ "User's range 9.30-9.50 — price now at 9.25, OUT OF RANGE"
   ├─ Handoff → Vault Agent: Executes decision
   │   └─ Auto-withdraw triggered (user set: "Pull out if we lose 10%")
   └─ Handoff → Notification Agent
       └─ Telegram alert: "⚠️ AVAX dropped 8%. Your LP was auto-withdrawn. Position safe: $485 USDC + 0.3 AVAX. Waiting for re-entry signal."

3. User wakes up to Telegram message — capital is already protected
4. Agent monitors for re-entry: "I'll redeploy when AVAX stabilizes above $9.30"
5. User types: "Wait for $9.20 before re-entry, I want a lower entry"
6. Agent updates rule: "Custom re-entry at $9.20, will alert first"
```

**What makes this different:**
- Gamma/Arrakis: You're in a pool, you take the drawdown
- AgentEscrow: Agent chain evaluates risk → executes → informs you
- User sets the rules, agents execute the judgment

---

## User Flow 3: "The Arena" (Pro Tier)

**Who:** Power user, wants to compete, showcase strategy, earn from it.

```
1. User spins up a custom agent: "AVAX Momentum Hunter"
2. Configures strategy rules:
   - "Enter AVAX/USDC LP when 4H RSI < 30 and volume > 2x average"
   - "Exit when RSI > 70 or range efficiency drops below 60%"
   - "Max drawdown: 5%"

3. Agent runs for 30 days — performance tracked on-chain

4. Arena Dashboard shows:
   ├─ Rank: #7 out of 142 agents
   ├─ Returns: +18.3% (30d)
   ├─ Risk score: Medium
   ├─ Win rate: 73%
   └─ Public brain log: all decisions visible

5. Other users see "AVAX Momentum Hunter" on leaderboard
6. User lists strategy on Bot Marketplace: $50/month
7. 12 users subscribe → $600/month passive income
8. Platform takes 10% ($60) → protocol revenue

9. Buyer flow:
   ├─ New user sees "AVAX Momentum Hunter" on Arena leaderboard
   ├─ Clicks "Subscribe" → $50/month USDC
   ├─ Agent's rules deploy to buyer's vault automatically
   └─ Buyer sees same brain visualization, but it's running their capital
```

**The flywheel:**
```
Build good bot → Prove on-chain → Attract buyers → Earn royalties → Build more
```

---

## User Flow 4: "The Prompt Trader" (Cross-Tier)

**Who:** Any tier — the core UX that makes AgentEscrow unique.

```
User types natural language → Agent interprets → Shows visualization → Executes

Examples:

💬 "Put $500 in AVAX/USDC with tight range"
   → Agent finds best pool, shows curve, deploys

💬 "Stake 100 AVAX, best APY, low risk"
   → Compares Benqi vs Yield Yak, stakes winner

💬 "3x long AVAX if it dips below $9.50"
   → Sets conditional leverage entry

💬 "Earn yield on idle USDC while I sleep"
   → Rotates stablecoin strategies automatically

💬 "Pull out if we lose 10%"
   → Sets stop-loss on all positions

💬 "Tighten my range, price is consolidating"
   → Adjusts LP bin range based on volatility
```

**Why this wins:**
| Product | Prompt | Visual | Agent | Multi-chain |
|---------|--------|--------|-------|-------------|
| Gamma | ❌ | ❌ | auto only | ✅ |
| Arrakis | ❌ | ❌ | auto only | ✅ |
| Trader Joe | ❌ | ✅ | manual | ❌ (AVAX) |
| **AgentEscrow** | ✅ | ✅ | ✅ | ✅ |

**Nobody has all three. That's the moat.**

---

## Subscription Summary

| Tier | Engagement Level | What User Gets |
|------|-----------------|----------------|
| **Free** | Observer | Connect wallet, view Arena, basic onboarding, see agent brain |
| **Paid ($TECH-denominated)** | Participant | Custom rules, automated monitoring, agent handoffs, risk alerts |
| **Pro ($TECH-denominated)** | Competitor | Arena entry, strategy marketplace, sell bots, premium strategies |

---

## Beam Grant Alignment

**Why Beam:**
- Beam's agent infrastructure = perfect fit for Layer 2 (Agent Brains)
- Beam's ecosystem needs DeFi primitives with AI — AgentEscrow fills that gap
- Multi-chain vision includes Beam as a deployment target

**What we're asking for:**
- Grant funding to port Solidity contracts to Beam VM
- Integration with Beam's agent identity layer
- Ecosystem support for Arena launch on Beam

**What Beam gets:**
- A working DeFi product (not just a pitch)
- AI agent infrastructure that drives TVL
- Social layer (Arena) that drives engagement and retention
- Multi-agent coordination — a showcase of what Beam's agent infra can do

---

## Tags
#AgentEscrow #Beam #grant #user-flow #engagement #script #DeFi #agents
