# AAE — Debt System & Dead Drop Mechanic

**Source:** Jordan voice message, May 22, 2026
**Status:** 🟢 APPROVED — Add to queue. Jordan confirmed May 22.

---

## Core Mechanic: Scheduled Debt Repayment

Inspired by Schedule 1 (video game) dead drop mechanic. When players borrow capital, they don't just owe interest — they have **scheduled repayment deadlines**.

### How It Works

1. **Borrow** — Player takes a loan against their credit score (existing mechanic)
2. **Dead Drop Schedule** — Debt comes due at intervals (e.g., every 3 turns, every market regime shift)
3. **Pay or Suffer** — Miss a payment and consequences stack:
   - Can't borrow more until caught up
   - Credit score takes a hit (existing mechanic, now more frequent)
   - Escalating penalties per missed payment
   - Eventually: forced liquidation of positions to cover debt
4. **Pay Early Bonus** — Paying ahead of schedule improves credit score (incentivizes responsibility)

### Why This Is Different from Yellow Cat

Yellow Cat tried social shaming as a DeFi mechanic — gimmicky, no gameplay loop. Jordan's version ties debt into an actual game with progression, strategy, and consequences. The "shame" is mechanical (you're locked out), not social.

### Tying It All Together

The debt system connects three existing systems:

- **Credit Score** — Determines borrow limit AND affects repayment terms (higher score = lower interest, longer deadlines)
- **Borrowing** — Now has a repayment schedule, not just interest accrual
- **Liquidation Engine** — Triggered by missed payments, not just margin

### The Feedback Layer: Reinforcement & Roasting

The debt system isn't just mechanical pressure — it's an emotional loop. When you're leveraged well and paying off debts on schedule, you get **positive reinforcement**. When you're fumbling, you get **roasted**.

**Positive Reinforcement (winning):**
- "Clean payment — your credit score just climbed. You're building something real."
- "Paid early? Smart. Your next loan just got better terms."
- "Zero missed drops this run. You're operating like a professional."

**Roasting (losing):**
- "You borrowed at 3x leverage and missed the dead drop? What did you think was going to happen?"
- "That's two missed payments in a row. Your dealer is cutting you off."
- "You just liquidated your best position to cover a $50 debt. Respect the game."

**Implementation:** This is Reparathy's domain — the accountability agent. She watches your financial behavior and delivers commentary. Not just alerts (that's the Analyst's job) — *personality*. The roasting creates stakes beyond mechanics. You don't just lose credit score points, you get verbally dressed down by an AI that remembers your patterns.

**Why this works:**
- Positive feedback reinforces good behavior (keeps responsible players engaged)
- Roasting creates social pressure even in single-player (you *feel* the judgment)
- Creates content moments — streamers will react to getting roasted
- Ties the emotional experience to the mechanical consequence

### Standalone Potential

Each mechanic works independently:
- Credit scoring → standalone hackathon piece
- Borrowing/lending → DeFi infrastructure submission
- Debt management → financial literacy tool

### Game-as-Marketing Insight

**Key strategic realization:** The game itself could be submitted to gaming hackathons as a way to advertise the real services underneath (credit layer, x402 payments, agent infrastructure). Agent Arena is the trojan horse.

---

## Next Steps

- [x] ~~Concept approved~~ ✅
- [ ] Integrate debt system into AAE-FORMAL-SPEC.md (new Section — credit score + dead drops + reinforcement)
- [ ] Define dead drop intervals and penalty escalation curve
- [ ] Map which real-world services the game demonstrates
