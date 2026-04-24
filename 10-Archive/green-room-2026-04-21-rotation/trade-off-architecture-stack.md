# The Trade Off — Architecture Stack

*Captured Apr 21, 2026 from Jordan's walkthrough*

## The Stack (top to bottom)

```
1. 🎮 "The Trade Off"        — the product people see
2. 💰 Revenue model           — launch fees (hook) + swap fees (river) + extensions (recurring) + marketplace (cut)
3. 🧠 Rep system              — engagement tracking, non-transferable
4. 💎 Dual-payment            — USDC full / $TECH discount (token sink)
5. 🔗 Multi-chain adapter     — AVAX first, expand outward
6. 🏗️ AgentPaymentFlow        — core contract, chain-agnostic
```

## Revenue Model Breakdown

| Stream | Type | Description |
|--------|------|-------------|
| Launch fees | Hook | One-time fee to launch a token on the platform |
| Swap fees | River | Ongoing per-swap fees (continuous revenue) |
| Extensions | Recurring | Premium features / add-ons (subscription-like) |
| Marketplace | Cut | Percentage cut from marketplace transactions |

## Key Design Decisions

- **Rep system is non-transferable** — earned through engagement, can't be bought/sold
- **Dual-payment is the token sink** — $TECH discount incentivizes holding/using the token, USDC option keeps it accessible
- **AVAX first** — then expand chains via multi-chain adapter
- **AgentPaymentFlow is chain-agnostic** — core logic separated from chain specifics

## The Hook

The revenue model's "hook + river" structure:
- **Hook** = launch fees (pulls people in)
- **River** = swap fees (continuous flow once they're in)

## Related

- [[trade-off-vision]] — Vision doc
- [[beam-sdk-research]] — Beam SDK (Avalanche L1) research
- [[x402-research]] — HTTP 402 agent payments
