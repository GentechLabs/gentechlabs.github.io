# Module 2: Impermanent Loss in Plain English
**Tier:** Foundations (Rookie)  
**Duration:** 5 minutes  
**Unlocks:** After Module 1 complete  
**Prerequisite:** Module 1

---

## 🎯 Realize (30 seconds)

You deposited $500 ETH and $500 USDC. ETH doubles in price. You'd think "great, I'm rich!" — but your pool position is worth *less* than if you'd just held ETH in your wallet.  
**That gap is impermanent loss.** It's not a scam. It's math.

---

## 📖 Explain (3 minutes)

### The Vending Machine Problem

Remember the vending machine analogy from Module 1? You're the machine. You stock it with sodas and chips in a 50/50 ratio.

- Day 1: 100 sodas ($1 each) + 100 chips ($1 each) = $200 total
- Day 10: Soda becomes the hot new thing. Now $2 each.
- Traders swarm your machine: they buy sodas, leave chips
- Your machine **automatically rebalances** to stay 50/50
- Now you have: 70 sodas + 140 chips = $280 total

**But if you'd just held 100 sodas in a locker:** 100 × $2 = $200.  
Wait, that doesn't work. Let me redo this.

Actually, let me use the classic example more carefully:

### The Classic Example

You deposit into an ETH/USDC pool:
- 1 ETH @ $1,000 + 1,000 USDC = $2,000 total

ETH price doubles to $2,000.

**If you just held:**
- 1 ETH × $2,000 = $2,000
- 1,000 USDC = $1,000
- **Total: $3,000**

**In the pool (automatic rebalancing):**
- The pool sells ETH as price rises to maintain the 50/50 ratio
- You end up with ~0.7 ETH + ~1,414 USDC
- **Total: ~$2,828**

**The difference: $3,000 - $2,828 = $172**

That $172 is your impermanent loss. You still *gained* $828 from your starting $2,000 — just not as much as if you'd held.

### Why "Impermanent"?

Because if ETH drops back to $1,000, the loss "disappears." You'd have your original 1 ETH + 1,000 USDC again.

**But:** Most people don't wait. They panic-sell, locking in the loss permanently.

### The Fee Defense

Here's why LP still wins long-term:
- Impermanent loss: -$172 in our example
- Trading fees over 6 months: +$400+ (depends on volume)
- **Net result: +$228 vs. holding**

The key word: **long-term.** Impermanent loss hurts day traders. It barely scratches long-term LPs who earn fees the whole time.

### When IL Hits Hardest

| Scenario | Impact |
|---|---|
| One token moons 10x | High IL |
| Both tokens move together (both up 20%) | Almost zero IL |
| Stablecoin pair (USDC/USDT) | Zero IL |
| Sideways market | Zero IL, pure fee accumulation |

---

## ⚡ Act (1 minute)

Go back to your 3 numbers from Module 1. Now add:
4. **ETH price when you deposited** (check your transaction history)
5. **ETH price now**
6. **Did ETH go up, down, or sideways?**

If ETH went up significantly, you've experienced some IL. But check your **total fees earned** — are they covering it?

---

## ✅ Prove (30 seconds)

**Quiz:**

1. **Why is it called "impermanent" loss?**
   - A) Because it only affects temporary pools
   - B) Because it reverses if prices return to where they started ✅
   - C) Because it's not real money

2. **Which pair has the LEAST impermanent loss risk?**
   - A) ETH/USDC
   - B) USDC/USDT (both stablecoins) ✅
   - C) ETH/BTC

3. **How do fees help against impermanent loss?**
   - A) They eliminate IL completely
   - B) They accumulate over time and can outweigh IL ✅
   - C) They reduce the price volatility

**Passing:** 2/3 correct

---

## 💡 Pro Tip

Don't obsess over impermanent loss on a daily basis. Check it monthly. If your fees are growing faster than your IL, you're winning. AAE's rebalancer is specifically designed to minimize IL by adjusting your range — more on that in Module 6.

---

*Next: Module 3 — APR vs. APY: The 1% That Becomes 10%*
