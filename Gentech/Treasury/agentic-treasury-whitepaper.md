# The Agentic Treasury — Whitepaper
**GenTech Labs · The Steward** · Draft v1.0 · August 15, 2026

> **One-line thesis:** A self-custody treasury agent that reads your wallet on-chain, watches your deployed liquidity, rebalances it when the market calls for it, and **never moves your money without you knowing exactly what's happening.**

---

## Abstract

The Agentic Treasury is GenTech's flagship product — an autonomous, self-custody treasury manager for the agent economy. It closes the loop the DeFi industry has only talked about: an agent that doesn't just *report* on a position, but actually *manages* it — detecting, deciding, executing, and verifying — all while keeping the user in control of their own keys.

This whitepaper describes the product, the architecture (AAE — the Autonomous Agentic Economy stack), the security model, the honest-economics framing that defines it, and the roadmap.

---

## 1. The Problem

Three truths are colliding in DeFi right now:

1. **Yield is real but mis-marketed.** Most yield-farmers promise fantasy APY and hide the small-capital reality. A $50 position earns ~$3–4/yr. The industry hides this; we refuse to.
2. **Agents report but don't execute.** Every analytics dashboard tells you *where* your liquidity is, but nothing *moves* it when the market regime shifts. The gap between "signal" and "action" is the untapped value.
3. **Trust is the bottleneck.** The agent economy can't grow until users trust that an autonomous agent won't run off with their money. Self-custody + explicit human gates are the only credible answer.

---

## 2. The Product

The Agentic Treasury reads your wallet on-chain, auto-discovers any liquidity position, watches it continuously, and — depending on your tier — either **recommends** a move for approval or **executes** a well-tested strategy automatically.

**The core loop (this is the whole product):**

> **Check the position → see what it's doing → decide where it should be → withdraw → redeploy → verify on-chain.**

**The two tiers:**

| | **Tier 1 — Operator** | **Tier 2 — User** |
|---|---|---|
| Self-custody | ✅ Your wallet | ✅ Your wallet |
| Position monitoring | ✅ Live | ✅ Live |
| Strategy recommendations | ✅ Yes | ✅ Yes |
| Auto-rebalance | ✅ Yes | ❌ **You confirm every move** |
| Macro war-room (CPI/FOMC/NFP) | ✅ Auto | 📋 Plan only — your call |
| Best for | GenTech operators | First real users |

> **The rule that makes this trustworthy:** your money moves only when you say so. Tier-2 never auto-executes. Period.

---

## 3. Architecture — AAE Rules Above, Venues Below

The treasury is built on the **AAE (Autonomous Agentic Economy)** stack — a modular 8-layer infrastructure stack for AI agents: identity, payments, intelligence, and real DeFi position management.

```
             ┌──────────────────────────────────────────────┐
             │  AAE RULE LAYER (venue-agnostic, the brain)  │
             │  regime_classifier → allocation_engine        │
             │  → decide() → plan() → verify() → remit()     │
             └───────────────┬──────────────────────────────┘
                             │ venue-agnostic order plans
        ┌────────────────────┼────────────────────────────┐
        │                    │                            │
   ┌────▼─────┐        ┌─────▼─────┐              ┌───────▼───────┐
   │ LP leg   │        │ Trade leg │              │ Remit leg     │
   │ yield    │        │ basis arb │              │ CDP→EOA→card  │
   │ (swap    │        │ / momentum│              │ (self-orbit)  │
   │ fees)    │        │           │              │               │
   └──────────┘        └───────────┘              └───────────────┘
   COINBASE    SOLANA   AVALANCHE  ETHEREUM       COINBASE CDP
   (base)      (Jupiter) (LFJ)     (PAXG/ONDO)    server account
```

**Composition model (locked by Jordan, Aug 5):** the treasury is an **orchestration layer, not a protocol builder.** We do NOT build AMMs or farms — we **compose existing protocols** (Trader Joe/LFJ, Morpho, Aave, Jupiter) as interchangeable sockets. The durable value is the brain + guard rails + payment rails + on-ramp, not the venue.

**Portable home chain (locked by Jordan, Aug 5):** users can **choose which chain holds their main treasury funds**, and switch at any time — since chains are fungible config, not rebuilds. The treasury is chain-portable by design.

---

## 4. The Agent (The Steward)

**The Steward** is the treasury's agent — the trusted hand on the treasury. It:

- **Discovers** your positions on-chain (no manual entry).
- **Watches** them continuously (every 10 minutes by default).
- **Decides** the right shape based on the current market regime (chop vs. swing vs. trend).
- **Executes** (in Tier-1) withdraw → convert → redeploy, with a gas buffer and on-chain verification of every step.
- **Verifies** by transaction receipt — never by declaration.

---

## 5. The Shapes (What the Agent "Thinks")

Think of your liquidity as a *shape* the agent places around the current price.

| Shape | When | What it does |
|---|---|---|
| **Curve** | Default — chop, mild trends | Spread across a range; earns fees as price oscillates. **Fewer bins in chop = taller = more per tick.** |
| **Bid-Ask** | Big move coming (CPI/FOMC/NFP) | Concentrated at two edges; catches a hard swing on either side. **Wider to survive the move.** |
| **Spot** | Confirmed one-way trend | All-in one direction — rare, only when you're sure. |

**The lever (Jordan's insight behind the numbers):**
- **Curve in chop → fewer bins** (~23). Tight market, price stays in a narrow zone; concentration makes more per oscillation.
- **Bid-ask when we're about to swing → wider** (~31). The edges must sit far enough apart to catch the whole move.

---

## 6. The Market Regime Engine

The treasury reads the market into a regime (via a hybrid signal of price, narrative, and macro data):

| Regime | Posture |
|---|---|
| **RANGE_BOUND** | → Yield mode (LP/staking) — the default |
| **BULL_TRENDING / BEAR_TRENDING** | → Trading mode, only at high confidence |
| **HIGH_VOLATILITY** | → Back to yield / defense |
| **PRICE_DISCOVERY** | → Trading mode, gated |

The engine stays in yield mode in chop and only flips to trading when the regime signal is clear — verified live (Aug 5): RANGE_BOUND→YIELD, BULL_TRENDING@90%→TRADE, BEAR_TRENDING@50%→stays YIELD. A stale or low-confidence signal forces the treasury back to defense. **It refuses to fake success.**

---

## 7. Security Model

- **Self-custody, always.** Your keys, your wallet, your money. We never hold custody.
- **Human gates.** Tier-2 never auto-executes. Withdrawals always human-confirmed.
- **Least-privilege keys.** Trade-only keys; withdrawal keys kept separate.
- **On-chain verification.** Every action verified by transaction receipt, not declared success.
- **When in doubt, hold.** If a transaction reverts, the agent stops and reports honestly.
- **Honest numbers.** Real on-chain yields, never fabricated APY.

**The CLARITY Act moat:** the treasury operates on **CLARITY Act DeFi Exclusion (Sec. 309/409) compliant** rails. Every endpoint on gentechlabs.net is compliance-verified. As the CLARITY Act makes agent identity + compliance *mandatory*, the treasury is already regulatory-ready — a structural advantage over non-compliant competitors.

---

## 8. Honest Economics

This is the part most yield farmers hide, and the part that defines us.

- A **$50 USDC/AVAX position** on the LFJ rail at current pool rates earns roughly **$0.26–0.30/day ≈ $3–4/yr.** Real. Not a fantasy APY.
- Fees are a function of **movement**, not efficiency. A position in a volatile market out-earns a "high-efficiency" one sitting flat.
- **Impermanent loss is real.** If AVAX moves hard one way, your LP can underperform simply holding AVAX. The agent helps you decide *when* to stay, *when* to DCA, and *when* to exit to hold instead.

**The milestone ladder (honest numbers):**

| Tier | Label | Daily fees |
|---|---|---|
| 0 | Grunt | $5/day |
| 1 | Scout | $10/day |
| 2 | Raider | $20/day |
| 3 | Warlord | $50/day |
| 4 | Sovereign | $100/day |

**The market-maker funnel:** every market maker starts small. Users deposit a small slice → the treasury proves the rail → the user scales. Honest expectations make that funnel *safe*, which is the trust moat.

---

## 9. The Trust Contract

- **Your keys, your wallet, your money.** We never hold custody.
- **Nothing auto-executes on a Tier-2 account.** Every real move is confirmed.
- **We show real on-chain numbers**, never a fabricated APY. If a position earns $3/yr, we say so.
- **When in doubt, we hold.** The agent refuses to fake success — if a transaction reverts, it stops and tells you honestly.

---

## 10. Roadmap

| Phase | Status | Description |
|---|---|---|
| Payment Rails | ✅ Live | x402 gateway, 6 chains |
| Agent Identity | ✅ Live | ERC-8004, credit scoring |
| Executable Yield (LP) leg | ✅ Shipped | Morpho/LFJ LP executor (85 tests) |
| Close + Remit leg (self-orbit) | ✅ Shipped | CDP → EOA → card |
| Regime-triggered auto-trade | ✅ Shipped | Gated on clear trend |
| User onboarding (EDU) | 🔧 Building | Getting-started guide shipped |
| Agent Commerce | 🔧 Building | Marketplace, escrow, dispute |
| **Whitepaper / GTM** | **🔧 This build** | **You are reading it** |

---

## 11. For the Avalanche Retro9000 Round (C-Chain path)

Retro9000's **C-Chain rounds** reward builders generating **real on-chain activity measured by AVAX burned via gas fees.** The Agentic Treasury is a natural submission:

- **The thesis (Jordan):** users use our website with a chat model baked in; the treasury is portable via a cron job that's interchangeable across chains; AgentKit is front-and-center and open source.
- **The activity:** every treasury rebalance, every yield harvest, every bridge generates on-chain transactions — measurable gas burn.
- **The differentiator:** a **CLARITY Act-compliant**, self-custody treasury driving real activity — not a testnet chain with no traffic.

*Note: the L1 route is scoped but deferred (`09-Green Room/specs/agentic-treasury-avalanche-l1-scope.md`). This whitepaper and the C-Chain activity round are the near-term strategy.*

---

*GenTech Labs · The Steward · Draft v1.0 · Aug 15, 2026 · Contact: Jordan Jones — github.com/ProtoJay4789*
