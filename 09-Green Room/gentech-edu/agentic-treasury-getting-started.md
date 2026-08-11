# Agentic Treasury — Getting Started Guide
### GenTech EDU · Pilot Edition (Aug 11, 2026)

> **What you're about to use** is a self-custody treasury agent that watches your
> deployed liquidity, tells you what it's doing, rebalances it when the market
> calls for it, and never touches your money without you knowing exactly what's
> happening.
>
> This guide is written with **honest numbers**, not hype. Every yield-farmer
> promises big APY; we show you what a real position actually earns at your size
> — before you commit a dollar.

---

## 1. The one-paragraph model

You deposit funds into **your own wallet** (never ours). The Agentic Treasury
reads that wallet on-chain, auto-discovers any liquidity position you have,
watches it every 10 minutes, and — depending on your tier — either **recommends**
a move for your approval or **executes** a well-tested strategy automatically.

The core loop (this is the whole product):
> **Check the position → see what it's doing → decide where it should be →
> withdraw → redeploy → verify on-chain.**

---

## 2. The two tiers

| | **Tier 1 — Operator** (trusted) | **Tier 2 — User** (you) |
|---|---|---|
| Self-custody | ✅ Your wallet | ✅ Your wallet |
| Position monitoring | ✅ Live, 10-min | ✅ Live, 10-min |
| Strategy recommendations | ✅ Yes | ✅ Yes |
| Auto-rebalance | ✅ Yes | ❌ **You confirm every move** |
| Macro war-room (CPI/FOMC/NFP) | ✅ Auto schedule | 📋 Plan only — your call |
| Best for | GenTech operators | First real users (e.g. Dadrian) |

**The rule that makes this trustworthy:** your money moves only when you say so.
Tier-2 never auto-executes. Period.

---

## 3. First steps (5–10 minutes)

1. **Fund your own wallet** with a small amount you're comfortable learning with
   (we recommend starting tiny — $50 is plenty to prove the loop).
   - On Avalanche you'll need: some **USDC** for the LP side + a little native
     **AVAX** for gas (gas is ~$0.001/tx on Avalanche right now — trivial).
2. **Tell the treasury your wallet address.** It will auto-discover your position.
3. **Pick a starting pool.** We recommend the **LFJ AVAX/USDC V2.2** rail — it's
   the one we've fired live and verified end-to-end.
4. **Deploy a curve** (the default shape — best for chop, earns fees both ways).
5. **Watch it work.** The agent reports your position live; if it drifts out of
   range, you'll get a signal with a suggested fix.

---

## 4. The shapes (what the agent "thinks")

Think of your liquidity as a shape the agent places around the current price.

| Shape | When | What it does |
|---|---|---|
| **Curve** | Default — chop, mild trends | Spread across a range; earns fees as price oscillates. **Fewer bins in chop = taller = more per tick.** |
| **Bid-Ask** | Big move coming (CPI/FOMC/NFP) | Concentrated at two edges; catches a hard swing on either side. **Wider to survive the move.** |
| **Spot** | Confirmed one-way trend | All-in one direction — rare, only when you're sure. |

**Jordan's lever (the "why" behind the numbers):**
- **Curve in chop → fewer bins** (we use ~23). Tight market, price stays in a
  narrow zone; concentration makes more per oscillation.
- **Bid-ask when we're about to swing → wider** (we use ~31). Left-right-left-right
  means the edges must sit far enough apart to catch the whole move.

---

## 5. The honest-numbers reality check

Let's be real about what a small position earns. This is the part most yield
farmers hide.

- A **$50 USDC/AVAX position** on the LFJ rail at current pool rates earns roughly
  **$0.26–0.30/day** ≈ **$3–4/yr**. Real. Not a fantasy APY.
- Fees are a function of **movement**, not efficiency. A position in a volatile
  market out-earns a "high-efficiency" one sitting flat.
- **Impermanent loss is real.** If AVAX moves hard one way, your LP can underperform
  simply holding AVAX. The agent helps you decide *when* to stay, *when* to DCA,
  and *when* to exit to hold instead.

**The milestone ladder** (what we're climbing, honest numbers):
| Tier | Label | Daily fees |
|---|---|---|
| 0 | Grunt | $5/day |
| 1 | Scout | $10/day |
| 2 | Raider | $20/day |
| 3 | Warlord | $50/day |
| 4 | Sovereign | $100/day |

At $50 deployed, you're at the bottom. That's fine — **every market maker starts
small.** The point is the loop works, you trust it, then you scale.

---

## 6. Common mistakes (read before you deposit)

- **Not funding gas.** You need a little native AVAX on the wallet, or the agent
  can't move anything. We keep a ~$1 buffer rule for exactly this.
- **Wrong chain.** Send USDC to the *right* chain (Avalanche, not Base). Cross-chain
  moves cost gas.
- **Expecting big returns on tiny capital.** A $20 position earns pennies. That's
  physics, not a bug. Scale only once the loop proves itself.
- **Letting a curve drift out of range.** The agent flags it; don't ignore the signal.
- **Holding Bid-Ask too long.** After a macro event settles, Bid-Ask sits in the
  dead zone between its edges and earns 0%. Revert to Curve on time.

---

## 7. Your first macro event (the fun part)

When a big data release is coming (CPI, FOMC, NFP), the treasury reads the
calendar and plans the move:

- **Now:** keep earning in Curve (do what's best for *right now*).
- **T-45 min before release:** reposition to Bid-Ask (edges catch the ±swing).
- **Release +24h:** stand back down to Curve (post-event chop).

For a **Tier-2 user**, you get the plan and confirm. The agent never jumps ahead
of you.

---

## 8. The trust contract

- **Your keys, your wallet, your money.** We never hold custody.
- **Nothing auto-executes on a Tier-2 account.** Every real move is confirmed.
- **We show real on-chain numbers**, never a fabricated APY. If a position earns
  $3/yr, we say so.
- **When in doubt, we hold.** The agent refuses to fake success — if a transaction
  reverts, it stops and tells you honestly.

---

*This is GenTech EDU — the honest-expectations layer. Built Aug 11, 2026, on the
day the treasury's exit rail, re-entry, and macro loop were first fired live with
real funds.*
