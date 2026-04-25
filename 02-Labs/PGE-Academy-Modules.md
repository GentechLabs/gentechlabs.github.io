# 🎓 GenTech Academy — Personal Goal Engine Learning Track

**Status:** Draft v1.0  
**Owner:** YoYo (Strategies) + Desmond (Content)  
**Date:** 2026-04-25  
**Prerequisite:** PGE Spec (`03-Strategies/Personal-Goal-Engine-Spec.md`)  
**Target Audience:** GenTech platform users — newcomers to intermediate DeFi participants

---

## Track Overview

The PGE Learning Track teaches users to **think like a trader while the system trades for them**. This is not abstract theory — every module connects to live positions, real data, and the user's own personalized ladder.

**Track Structure:** 10 modules across 4 tiers. Each module = 10–25 min. Completion unlocks tier advancement + REP rewards.

| Tier | Modules | Theme | Time |
|------|---------|-------|------|
| 1 — Scout | 1–3 | Foundations | ~35 min |
| 2 — Raider | 4–6 | Strategy | ~50 min |
| 3 — Warlord | 7–8 | Portfolio | ~45 min |
| 4 — Sovereign | 9–10 | Mastery | ~45 min |

---

## Module 1: What Is Liquidity Provision?
**Tier:** Scout (Tier 1)  
**Duration:** 10 min  
**Format:** Interactive explainer + simulator

### Learning Objectives
1. Define "liquidity provision" in plain language
2. Explain why DEXs need liquidity providers
3. Understand the basic LP position: two tokens, one range
4. Identify the core risk: impermanent loss

### Content Script

**Opening Hook (30 sec):**
> "Every trade you make on a DEX — swapping AVAX for USDC, buying $TECH, exiting a position — someone has to be on the other side of that trade. Liquidity providers are the market makers of DeFi. They put up capital so trades can happen. And they get paid for it."

**Concept 1 — The Pool (2 min):**
- Visual: Two buckets — Token A and Token B
- Analogy: A currency exchange booth at an airport. The booth holds both dollars and euros. When you trade, you take one and leave the other. The booth needs both to function.
- Live connection: "Our AVAX/USDC pool on LFJ is that booth. $16.6M in volume today. Every swap pays a fee — and a slice goes to LPs."

**Concept 2 — The Position (3 min):**
- You deposit AVAX + USDC into the pool
- The pool gives you an NFT representing your position
- That NFT tracks: how much you put in, what range you chose, what fees you've earned
- Interactive: "Build your first position" simulator — user drags a slider to pick AVAX/USDC ratio, sees projected fee share

**Concept 3 — The Risk (3 min):**
- Impermanent Loss (IL): If AVAX moons while you're in the pool, you miss some upside vs just holding
- Why "impermanent"? If price returns to your entry, the loss disappears
- Key insight: "Fees earned vs IL suffered — that's the game."
- Quiz: "AVAX goes from $9 to $15 while you're in a pool. You miss some upside. Is this loss permanent?" (Answer: Only if you exit at $15.)

**Key Takeaway:**
> "LP is not passive income — it's managed income. You are a market maker now. The fees are your paycheck. IL is your cost of doing business."

### Interactive Element
- **Simulator:** "First Position Builder" — user selects AVAX/USDC ratio, sees fee share %, gets instant feedback
- **Quiz:** 3 questions, 80% to pass

### REP Reward
+10 REP on completion

---

## Module 2: Range Shapes — Curve, Spot, Bidirectional
**Tier:** Scout (Tier 1)  
**Duration:** 15 min  
**Format:** Visual simulator + case studies

### Learning Objectives
1. Explain the three range shapes and when to use each
2. Understand fee efficiency: where in the range you earn most
3. Predict which shape suits different market conditions
4. Connect shape choice to risk/reward profile

### Content Script

**Opening Hook (30 sec):**
> "You don't just 'put money in a pool.' You choose a shape. That shape determines where you earn fees, how much you earn, and what happens when price moves. Picking the right shape is your first real trading decision."

**Concept 1 — Curve (Default) (4 min):**
- Visual: Bell curve. Peak fee efficiency at the center of your range.
- When to use: You think price will stay roughly where it is. Low volatility expectation.
- Live example: "Our AVAX/USDC position uses Curve. Range: $9.33–$9.52. Current price: $9.45. We're near peak efficiency."
- Risk: If price drifts to the edge, efficiency drops to zero. Rebalancing needed.

**Concept 2 — Spot (4 min):**
- Visual: Flat line. Uniform efficiency across the entire range.
- When to use: You have no directional bias. You just want exposure.
- Trade-off: Lower peak efficiency than Curve, but more forgiving if price drifts.
- Analogy: Curve is a sniper rifle. Spot is a shotgun.

**Concept 3 — Bidirectional (4 min):**
- Visual: U-shape. Peak efficiency at the EDGES of your range.
- When to use: You expect volatility but don't know direction. Price will move — you want to catch fees at the extremes.
- Advanced concept: "You're betting on movement, not stability."
- Risk: If price stays in the middle, you earn almost nothing.

**Simulator (2 min):**
- User selects a shape for 3 scenarios:
  1. "AVAX is stable, trading sideways" → Curve
  2. "AVAX might pump or dump after a governance vote" → Bidirectional
  3. "You just want set-and-forget exposure" → Spot

**Key Takeaway:**
> "Shape is your market thesis expressed in code. Curve says 'I think it stays here.' Bidirectional says 'I think it moves.' Spot says 'I don't know, and that's okay.'"

### Interactive Element
- **Shape Simulator:** Drag price across range, watch efficiency change in real time for each shape
- **Case Study Quiz:** 3 market scenarios, pick the right shape

### REP Reward
+15 REP on completion

---

## Module 3: Impermanent Loss — The Math That Matters
**Tier:** Scout (Tier 1)  
**Duration:** 12 min  
**Format:** Calculator + video

### Learning Objectives
1. Calculate IL for a given price movement
2. Compare IL against fees earned to determine net P&L
3. Understand why IL is "impermanent" (and when it becomes permanent)
4. Use the IL calculator to evaluate any position before entering

### Content Script

**Opening Hook (30 sec):**
> "Impermanent Loss is the most misunderstood concept in DeFi. It's not a bug. It's not a scam. It's math. And once you understand the math, you can beat it."

**Concept 1 — The Formula (3 min):**
- Simple version: If price changes, your pool is worth less than if you just held the tokens
- Visual: Side-by-side "HODL value" vs "LP value" as price moves
- Live data: "AVAX at $9.45. Our position value: $83.92. If we just held the tokens: $83.53. We're +$0.39 ahead — fees are winning."

**Concept 2 — IL vs Fees (4 min):**
- The break-even question: "Am I earning enough in fees to cover my IL?"
- Rule of thumb: In concentrated liquidity, you need ~15–20% APR in fees to comfortably cover typical IL
- Calculator demo: Input price change %, see IL %, compare to your APR
- Our position: "APR ~76%. AVAX would need to 2x or 0.5x before IL overtakes fees."

**Concept 3 — When IL Becomes Permanent (3 min):**
- IL is only "impermanent" if you wait for price to return
- If you exit at a loss — it's permanent
- Strategy implication: "Don't panic-exit a down position. Rebalance or wait."
- Exception: If fundamentals change (protocol hack, token death), IL is the least of your worries. Exit.

**Quiz (1 min):**
- "Your position is down 5% due to IL. Fees earned so far: +8%. What should you do?"
  - A) Exit immediately → Wrong
  - B) Hold, fees are winning → Correct
  - C) Add more liquidity → Maybe, but not the best answer

**Key Takeaway:**
> "IL is the cost of doing business. Fees are your revenue. Run the numbers before you enter. Run them again before you exit."

### Interactive Element
- **IL Calculator:** Input token pair, entry price, current price, range width → see IL %, fee breakeven
- **Quiz:** 4 questions, 75% to pass

### REP Reward
+15 REP on completion

---

## Module 4: Reading DexScreener — Pool Selection
**Tier:** Raider (Tier 2)  
**Duration:** 10 min  
**Format:** Walkthrough + scavenger hunt

### Learning Objectives
1. Evaluate any pool using 5 key metrics: TVL, Volume, Fees, APR, Age
2. Spot red flags: low volume, suspicious TVL spikes, new pools
3. Understand the relationship between volume and fee sustainability
4. Apply the "Volume/TVL ratio" heuristic

### Content Script

**Opening Hook (30 sec):**
> "Not all pools are created equal. Some print fees. Some print regrets. DexScreener is your due diligence tool. Here's how to read it like a pro."

**The 5 Metrics (5 min):**
1. **TVL (Total Value Locked):** Higher is generally safer (deeper liquidity = less slippage). But beware sudden spikes — could be a trap.
2. **Volume 24h:** This is your fee engine. No volume = no fees. Look for consistent volume, not one-day spikes.
3. **Fees 24h:** Directly tied to volume. Should be steady.
4. **APR:** The headline number. Be skeptical — can it last?
5. **Pool Age:** New pools (<7 days) are risky. Older pools have track records.

**The Heuristic (3 min):**
- **Volume/TVL Ratio:** 
  - <5% = Low activity, probably not worth it
  - 5–15% = Healthy
  - >15% = High activity, but check sustainability
- Live example: "Our AVAX/USDC pool: $16.6M volume / $2.4M TVL = 6.9%. Healthy. Sustainable."

**Red Flags (1 min):**
- Brand new pool with $5M TVL and $100K volume → Dead pool, don't touch
- APR dropping 50% day-over-day → Volume left, you're the last one in
- No verified token icons → Possible scam

**Scavenger Hunt:**
- User is given 3 real DexScreener pools. Must evaluate: Healthy, Risky, or Avoid. Gets instant feedback.

**Key Takeaway:**
> "A good pool has volume, history, and balance. A bad pool has hype, mystery, and desperation."

### Interactive Element
- **Scavenger Hunt:** Evaluate 3 real pools, get scored
- **Quick Quiz:** 5 red flag scenarios — spot the danger

### REP Reward
+15 REP on completion

---

## Module 5: Multi-Shape Strategies
**Tier:** Raider (Tier 2)  
**Duration:** 20 min  
**Format:** Case studies + sandbox

### Learning Objectives
1. Combine shapes into multi-position strategies
2. Understand when to switch shapes based on market regime
3. Build a "ladder of ranges" for volatility capture
4. Evaluate the capital efficiency of complex strategies

### Content Script

**Opening Hook (30 sec):**
> "One position is a bet. Two positions is a strategy. Three positions is a system. This is where you stop gambling and start building."

**Concept 1 — The Ladder of Ranges (5 min):**
- Instead of one wide range, use 3 narrow ranges stacked
- Example: AVAX at $9.45
  - Position A (Curve): $9.30–$9.40 — catches downside
  - Position B (Curve): $9.40–$9.50 — catches current zone
  - Position C (Curve): $9.50–$9.60 — catches upside
- Benefit: Higher fee efficiency in each zone. If price moves, one position goes out of range but the others pick up slack.

**Concept 2 — Shape Switching (5 min):**
- Market regimes:
  - **Accumulation (sideways):** All Curve
  - **Breakout (high vol):** Mix Curve + Bidirectional
  - **Trend (directional):** Spot on the trend, Curve on support
- Case study: "AVAX breaks $10 resistance. You had Curve at $9.33–$9.52. Now what? Option A: Rebalance wider. Option B: Add a Bidirectional position at $9.80–$10.50 to catch the move."

**Concept 3 — Capital Efficiency (5 min):**
- Multiple positions = more gas, more management
- The trade-off: "Is the extra fee capture worth the extra complexity?"
- Rule of thumb: Don't split positions if total capital < $500. Gas eats your edge.

**Sandbox (4 min):**
- User gets $1,000 simulated capital and a volatile market chart
- Must build a 2–3 position strategy
- System simulates 7 days. User sees fees, IL, net P&L
- Leaderboard: Who built the most efficient strategy?

**Key Takeaway:**
> "A single position is reactive. A multi-shape strategy is predictive. You're not just responding to price — you're building a net that catches it wherever it goes."

### Interactive Element
- **Sandbox Simulator:** Build multi-position strategy, simulate 7 days, see results
- **Case Study:** 3 market regimes, design the right strategy

### REP Reward
+25 REP on completion

---

## Module 6: Gas Optimization — Timing Your Transactions
**Tier:** Raider (Tier 2)  
**Duration:** 15 min  
**Format:** Tutorial + gas tracker exercise

### Learning Objectives
1. Understand what gas is and why it matters for LPs
2. Identify the cheapest times to transact on Avalanche
3. Use batching to reduce gas costs
4. Calculate "gas breakeven" — when is a rebalance worth the cost?

### Content Script

**Opening Hook (30 sec):**
> "Every time you deposit, withdraw, or rebalance — you pay gas. On Avalanche, it's cheap. But cheap adds up. A $0.50 gas fee on a $100 position is 0.5%. Do that weekly and you've lost 26% of your capital to friction."

**Concept 1 — Gas on Avalanche (3 min):**
- Base fee + priority fee = total gas
- AVAX gas is cheap but not free: ~$0.10–$0.50 per transaction
- Compare to Ethereum: $5–$50 per transaction. This is why we build on AVAX.
- Live tool: Show gas tracker. Best times: Weekends, early UTC mornings.

**Concept 2 — Batching (4 min):**
- Instead of: Deposit Monday, rebalance Wednesday, compound Friday (3 transactions)
- Better: Rebalance + compound in one transaction (1 transaction)
- Advanced: Use a vault or keeper to batch automatically
- "Our auto-compound system batches claims + redeposits. One transaction, not three."

**Concept 3 — Gas Breakeven (4 min):**
- Formula: `gas_cost / position_value = breakeven_fee_%`
- Example: $0.50 gas / $100 position = 0.5%. You need to earn 0.5% in fees just to cover the rebalance.
- Rule: Don't rebalance a position < $200 unless fees are >1%.
- Calculator: Input position size, gas cost, see breakeven %

**Exercise (3 min):**
- User gets 5 scenarios:
  1. $50 position, $0.40 gas → Rebalance? No. Breakeven = 0.8%. Too high.
  2. $500 position, $0.30 gas → Rebalance? Yes. Breakeven = 0.06%. Easy.

**Key Takeaway:**
> "Gas is friction. Friction compounds. Batch your transactions, time your rebalances, and never let gas eat your edge."

### Interactive Element
- **Gas Breakeven Calculator:** Input position + gas, see if rebalance is worth it
- **Timing Exercise:** Pick the best time to transact from a 7-day gas chart

### REP Reward
+15 REP on completion

---

## Module 7: Portfolio LP — Multi-Pool Management
**Tier:** Warlord (Tier 3)  â€œDuration:** 25 min  
**Format:** Spreadsheet template + portfolio builder

### Learning Objectives
1. Allocate capital across multiple pools for diversification
2. Understand correlation risk (AVAX and SOL both dropping = double IL)
3. Rebalance a portfolio, not just a position
4. Use the "75/15/10" framework for LP allocation

### Content Script

**Opening Hook (30 sec):**
> "One pool is a job. A portfolio of pools is a business. You're no longer managing a position — you're managing a treasury."

**Concept 1 — The 75/15/10 Framework (5 min):**
- **75% Core Pools:** Stable, high-volume pairs you understand deeply (AVAX/USDC, ETH/USDC)
- **15% Growth Pools:** Higher risk, higher reward (new tokens, lower TVL)
- **10% Experimental:** Learning capital. Small positions to test strategies.
- "This is our framework at GenTech. Your numbers might differ — but have a framework."

**Concept 2 — Correlation Risk (5 min):**
- If you hold AVAX/USDC and SOL/USDC, you're long both AVAX and SOL
- When crypto crashes, both positions suffer IL simultaneously
- Hedge: Add a stablecoin-stablecoin pool (USDC/USDT) for ballast
- "Our watchlist: BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM. We don't LP all of them. We LP the ones with the best volume/TVL."

**Concept 3 — Portfolio Rebalancing (5 min):**
- Monthly review: Which pools are underperforming? Which are exceeding?
- Rebalance rule: "If a pool's fees drop below its IL for 2 weeks, consider exiting."
- Don't over-trade. Monthly rebalancing is usually enough.

**Portfolio Builder (9 min):**
- User gets $5,000 simulated capital
- Must allocate across 5 pools with different metrics
- System simulates 30 days
- Scoring: Total fees earned, max drawdown, Sharpe-like ratio (fees/volatility)

**Key Takeaway:**
> "A portfolio is a system. Systems don't panic. They rebalance, they compound, they survive."

### Interactive Element
- **Portfolio Builder:** Allocate across 5 pools, simulate 30 days, get scored
- **Correlation Quiz:** Given 3 pools, identify correlation risk

### REP Reward
+25 REP on completion

---

## Module 8: Custom Range Design
**Tier:** Warlord (Tier 3)  
**Duration:** 20 min  
**Format:** Sandbox + blueprint exercise

### Learning Objectives
1. Design custom ranges based on technical analysis (support/resistance)
2. Understand width vs efficiency trade-off
3. Backtest a range against historical price action
4. Build a "playbook" of ranges for different market conditions

### Content Script

**Opening Hook (30 sec):**
> "Curve, Spot, Bidirectional — those are training wheels. Custom range design is where you become the architect. You decide where the liquidity goes."

**Concept 1 — Width vs Efficiency (4 min):**
- Wide range = more time in range = more fees, but lower efficiency
- Narrow range = higher efficiency, but more rebalancing
- The optimal width depends on: volatility, your monitoring frequency, gas costs
- "Our AVAX range is $9.33–$9.52 = $0.19 wide. On a $9.45 price, that's Â±1%. Tight. Active."

**Concept 2 — Support & Resistance (5 min):**
- Support = price level where buying pressure historically enters
- Resistance = price level where selling pressure historically enters
- LP strategy: Place your range between support and resistance
- "If AVAX support is $9.20 and resistance is $9.80, a $9.25–$9.75 range captures most of the action."

**Concept 3 — Backtesting (5 min):**
- Look at 30-day price history
- Ask: "How often would my range have been in-range?"
- Tool: Input a range, see "in-range %" for last 30 days
- Goal: >80% in-range time for Curve, >60% for Bidirectional

**Blueprint Exercise (5 min):**
- User gets a blank chart with support/resistance marked
- Must design 3 ranges:
  1. Conservative (wide, safe)
  2. Aggressive (narrow, high yield)
  3. Volatility capture (Bidirectional at extremes)
- System backtests all 3. User sees fees, IL, rebalance count.

**Key Takeaway:**
> "Custom ranges are your signature. They reflect how you see the market. There are no right answers — only tested ones."

### Interactive Element
- **Backtest Sandbox:** Design a range, see 30-day performance
- **Blueprint Exercise:** Build 3 ranges for a market scenario

### REP Reward
+25 REP on completion

---

## Module 9: Risk Management & Position Sizing
**Tier:** Sovereign (Tier 4)  
**Duration:** 20 min  
**Format:** Scenario game + checklist

### Learning Objectives
1. Apply the 1% rule: Never risk more than 1% of portfolio on a single rebalance
2. Design stop-ranges (automatic exit conditions)
3. Build a personal risk matrix: What would make you exit entirely?
4. Understand tail risk: Black swan events, protocol hacks, oracle failures

### Content Script

**Opening Hook (30 sec):**
> "You can be right 90% of the time and still go broke if the 10% wipes you out. Risk management is not about avoiding losses. It's about surviving them."

**Concept 1 — The 1% Rule (4 min):**
- Never risk more than 1% of total portfolio on any single position adjustment
- Example: $10,000 portfolio → max $100 at risk per rebalance
- This means: Small positions, frequent rebalancing ≠ reckless size
- "We rebalance our $83 position weekly. The risk per rebalance? ~$0.50 in gas. That's 0.006% of our portfolio."

**Concept 2 — Stop-Ranges (4 min):**
- A stop-loss for LPs: "If price exits my range by >10%, exit the position"
- Why? Extreme moves = extreme IL. Better to take a small loss than a large one.
- How: Set an alert. When triggered, evaluate: rebalance or exit?
- "Our system sends ALERT when efficiency drops below 30%. That's your stop-range warning."

**Concept 3 — The Risk Matrix (4 min):**
- Build your personal exit conditions:
  - Protocol hack? → Exit immediately
  - Token delisting? → Exit immediately
  - Market down 50%? → Hold, rebalance wider, accumulate
  - Fees dry up for 2 weeks? → Evaluate, possibly exit
- Write it down. Follow it. "Your risk matrix is your pre-commitment contract."

**Scenario Game (7 min):**
- 5 scenarios, timed:
  1. "AVAX drops 30% overnight. Your position is out of range. Gas is cheap. What do you do?"
  2. "LFJ announces a critical bug. No funds lost yet. What do you do?"
  3. "Fees have dropped 80% for 10 days. IL is accumulating. What do you do?"
  4. "BTC is in free fall. Your AVAX/USDC pool is correlated. What do you do?"
  5. "You've hit your $20/day goal for 30 straight days. What do you do?"
- Scoring: Speed + consistency with stated risk matrix

**Key Takeaway:**
> "The best traders aren't the ones who never lose. They're the ones who lose small, win big, and always live to trade another day."

### Interactive Element
- **Scenario Game:** 5 timed decisions, scored against your risk matrix
- **Checklist Builder:** Build your personal exit-condition checklist

### REP Reward
+30 REP on completion

---

## Module 10: Building a System — Automation & Compounding
**Tier:** Sovereign (Tier 4)  
**Duration:** 25 min  
**Format:** Checklist + template + live demo

### Learning Objectives
1. Design a personal LP system: rules, schedules, triggers
2. Understand auto-compounding mechanics and when to use them
3. Build a weekly review ritual
4. Create a "playbook" document for your future self

### Content Script

**Opening Hook (30 sec):**
> "You've learned the pieces. Now you build the machine. A system is a set of rules that make decisions for you when you're tired, emotional, or distracted. Trading is 90% psychology. A system removes the psychology."

**Concept 1 — The System Architecture (5 min):**
- Every system needs:
  1. **Entry rules:** When do I open a position? (DexScreener criteria, capital available)
  2. **Monitoring rules:** How often do I check? (Daily alerts, weekly deep-dives)
  3. **Rebalance rules:** When do I adjust? (Efficiency <50%, price near edge, weekly schedule)
  4. **Exit rules:** When do I close? (Risk matrix triggers, goal achievement)
  5. **Compound rules:** When do I reinvest? (Fees > $X, monthly schedule)

**Concept 2 — Auto-Compounding (5 min):**
- What it is: Automatically claim fees and redeposit them into the position
- Benefit: Compound growth. $1 in fees today = $1.05 next month = $1.10 the month after
- When to trigger: When cumulative fees > gas cost × 3 (safety margin)
- "Our system auto-compounds when fees exceed $5. Below that, gas eats the gain."
- Manual vs auto: Auto is convenient. Manual lets you redirect to new opportunities.

**Concept 3 — The Weekly Ritual (5 min):**
- Sunday evening, 15 minutes:
  1. Check all positions: in-range? efficiency? fees earned?
  2. Check watchlist: any new opportunities?
  3. Rebalance if needed (follow your rules, not your gut)
  4. Log reflections: What worked? What didn't?
  5. Update playbook if lessons learned

**Playbook Template (9 min):**
- User fills out a template:
  - My capital: ___
  - My monthly commitment: ___
  - My risk tolerance: ___
  - My entry criteria: ___
  - My rebalance triggers: ___
  - My exit triggers: ___
  - My compound threshold: ___
  - My weekly ritual time: ___
- System saves it. User can export as PDF.
- Live demo: Show YoYo's actual weekly ritual (anonymized data)

**Key Takeaway:**
> "A trader without a system is a gambler with extra steps. A trader with a system is a business owner. Build your business."

### Interactive Element
- **System Builder:** Fill out playbook template, get a personalized "system card"
- **Live Demo:** Walkthrough of automated LP monitoring + compounding
- **Export:** Download playbook as PDF

### REP Reward
+50 REP on completion (largest module reward — capstone)

---

## Academy Integration Notes

### Completion Flow
1. User completes all 3 Tier 1 modules → **Scout Badge unlocked** → Can enter live LP positions with default ladder
2. User completes all 3 Tier 2 modules → **Raider Badge unlocked** → Can use multi-shape strategies, access advanced simulator
3. User completes all 2 Tier 3 modules → **Warlord Badge unlocked** → Can manage portfolio LP, access portfolio builder
4. User completes all 2 Tier 4 modules → **Sovereign Badge unlocked** → Full platform access, custom system builder, mentorship eligibility

### Prerequisite Chain
- Module 1 → Module 2 → Module 3 (sequential)
- Module 3 completion unlocks Module 4
- Module 4 + 5 completion unlocks Module 6
- Module 6 completion unlocks Module 7
- Module 7 + 8 completion unlocks Module 9
- Module 9 completion unlocks Module 10

### REP Budget (per user completing full track)
| Tier | Modules | REP per Module | Tier Total |
|------|---------|---------------|------------|
| Scout | 3 | 10+15+15 | 40 |
| Raider | 3 | 15+25+15 | 55 |
| Warlord | 2 | 25+25 | 50 |
| Sovereign | 2 | 30+50 | 80 |
| **Total** | **10** | — | **225 REP** |

### Connection to Live Contracts
Per `labs-academy-curriculum-mapping` skill:
- Module 1–3: Map to `AgentEscrow.sol` CEI pattern — "Just as escrow updates state before transfer, you update your understanding before deploying capital"
- Module 4–6: Map to LP Monitor cron — "YoYo's alerts are your safety net. Understand what they measure."
- Module 7–8: Map to multi-pool portfolio tracking — "Our dashboard aggregates positions exactly as you'll learn to think."
- Module 9–10: Map to `BurnSplitter` and auto-compound logic — "Systems beat emotions. Code your rules."

---

## Tags
#academy #pge #education #modules #learning-track #gen-tech-academy
