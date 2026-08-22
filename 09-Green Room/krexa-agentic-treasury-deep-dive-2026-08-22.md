# Krexa × Agentic Treasury — Deep Dive (Aug 22, 2026)

**Source:** x.com/krexa_xyz/status/2091108959944106394 (Polygon integration live) + krexa.xyz/skill.md + pricing.md + llms-full.txt + quickstart

## What Krexa is
The **financial OS for AI agents** — programmable, on-chain credit on **Solana mainnet** (7 Anchor programs) + **Monad** (10 contracts). Agents register on-chain, get a **Krexit Score (200–850)**, borrow USDC against it, repay automatically through a **Revenue Router**. No human co-signer.

## The Polygon integration (the "finally live" part)
Krexa agents can now **bridge cross-chain between Solana and Polygon** (chain 137) via **deBridge** — plus Ethereum, Base, Arbitrum, Avalanche, Optimism, BSC. All txs unsigned, returned for signing. No invite code or credit line required to bridge.

## Credit levels (borrowing)
| Level | Max credit | APR | Requirement |
|---|---|---|---|
| L1 Micro | $500 | 36.50% | None (entry) |
| L2 Standard | $20,000 | 29.20% | Score ≥ 500 |
| L3 Growth | $50,000 | 21.90% | Score ≥ 650 + KYA Tier 2 |
| L4 Prime | $500,000 | 18.25% | Score ≥ 750 + KYA Tier 2 |

- Currency: **USDC**. No subscription/seat fee — Krexa earns a **10% protocol fee** inside the Revenue Router on repayments.
- Every draw passes **8 on-chain safety checks** (per-trade limit, daily limit, venue concentration cap, health factor, venue whitelist, credit-level sufficiency, exposure tracking, freeze status).

## Revenue Router (the key mechanism)
Inbound revenue does NOT reach the agent wallet directly. It flows through the Payment Router, which splits each dollar:
```
Payment $1.00 → Revenue Router
Protocol fee (10%): $0.10 → Treasury
Debt service (40%): $0.40 → Reduces outstanding balance
Agent receives (50%): $0.50 → Agent PDA wallet
```
Repayment is **structurally enforced** — the agent cannot spend revenue without first servicing debt. This is what allows under-collateralized credit to a non-human counterparty.

## Krexit Score (200–850) — 5 behavioral signals
| Signal | Weight | Measures |
|---|---|---|
| Repayment history | 30% | On-time vs late vs missed |
| Profitability | 25% | P&L ratio, Sharpe, max drawdown |
| Behavioral health | 20% | Time in Green/Yellow/Orange/Red zones |
| Usage patterns | 15% | Venue entropy, tx consistency |
| Account maturity | 10% | Age, lifetime volume, completed cycles |

Plus a **compute-credit boost** (+60) when an agent proves an OpenAI/Anthropic billing relationship — the agentic-finance equivalent of "verified income."

## Our treasury's actual Krexit score (LIVE check)
Checked our Solana treasury wallet `DjCjLZM9dAjPKQywfk4z2uLYM4xXhF1zUkHLkiS2Xbf3`:
- **Score: 237** → **L1 Micro, $500 max credit** @ 36.50% APR
- `isRegistered: false` — we have a preview score, not a registered agent
- No SNS boost, no compute boost applied yet

## How Krexa could benefit the Agentic Treasury

### 1. Working capital without a funded wallet (the big unlock)
Our treasury is **capital-constrained** — true total ~$56 across 5 wallets, and multiple plays are gated on "no funds" (Unichain deploy blocked at $1.88, GTA real-execution needs funding). Krexa lets the treasury **borrow USDC against its on-chain history** instead of needing a pre-funded wallet. L1 gives $500 immediately; score 500+ unlocks $20K.

### 2. The Revenue Router IS our x402 model, structurally enforced
We already run x402 services (the 3 treasury agents just relisted). Krexa's Revenue Router is the **per-tx fee middleman** we're building — but they've made it the *repayment mechanism*. If our treasury agents point their x402 payments at a Krexa Revenue Router, every dollar of API revenue **auto-services debt** before the agent sees it. That's a self-funding treasury loop: borrow → run services → revenue auto-repays → borrow more.

### 3. Solana is our second rail
Krexa is Solana-native, and Solana is our compounding agent-economy rail (Base = volume, Solana = agent economy). The Polygon bridge (via deBridge) adds cross-chain reach — treasury can move USDC Solana↔Polygon↔Base without a funded EVM wallet.

### 4. The Krexit Score is a reusable credit signal
The 5-signal behavioral score (repayment, profitability, health, usage, maturity) is exactly the "Agency of Traders" underwriting model. We could either **use Krexa's score** for our own agents or **study it** to build our own.

## Risks / honest caveats
- **36.50% APR at L1 is expensive** — borrowing $500 to deploy costs $0.50/day. Only worth it if the deployed capital earns > that (our LP strategies target ~10-20% APR, so L1 is marginal; L2+ at 29% is better).
- **Score 237 is low** — we'd need to build repayment history + profitability to reach L2 ($20K @ 29%). That takes time and real revenue flow.
- **Invite code required** to activate (`krexa activate KREXA-XXXX-XXXX`) — need to request one.
- **PDA wallet = no private key** — the program enforces rules; agent owner signs. This is a custody model shift from our current keyed wallets.
- **Not a substitute for our own rails** — Krexa is a credit layer, not our x402 gateway. It complements, doesn't replace.

## Recommendation
**Log as a case study + potential credit rail, do NOT integrate yet.** The highest-value next step is:
1. **Register our treasury agent** on Krexa (free, no fee) to start building a real Krexit score + repayment history — this is the "credit score" that unlocks L2+ later.
2. **Study the Revenue Router** as the reference for our own agent-credit / per-tx-fee design.
3. **Revisit when treasury has real revenue flow** — then borrowing against it becomes a genuine leverage play.

**Jordan decision needed:** register the treasury agent on Krexa now (free, starts the score clock), or hold until we have revenue to repay against?
