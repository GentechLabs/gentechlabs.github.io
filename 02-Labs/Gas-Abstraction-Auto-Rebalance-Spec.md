---
created: 2026-04-21
author: Jordan (concept) / Desmond (spec)
status: Proposal — awaiting team feedback
---

# 💰 Gas Abstraction for Auto-Rebalance

## The Vision

Users deposit funds into an LP position. Gas fees for auto-rebalancing are **automatically deducted from their deposit balance** — no manual gas management, no separate wallet top-ups. Passive income covers the cost of staying in range.

**User experience:**
1. Deposit funds once
2. Platform monitors LP range 24/7
3. Rebalance triggers automatically when out of range
4. Gas deducted transparently from deposit
5. User sees: "Rebalanced at 2:34 PM — gas: $0.03"

---

## Architecture

### Deposit Allocation Model

```
User deposits $1,000
├── $980  → LP position (working capital)
├── $10   → gas reserve (auto-funded)
└── $10   → platform fee
```

### Gas Reserve Thresholds

| Chain | Avg Rebalance Gas | $10 Reserve Covers | Top-up Alert |
|-------|-------------------|-------------------|--------------|
| Avalanche (LFJ) | ~$0.03 | ~330 rebalances | Below $1 |
| Solana | ~$0.00025 | ~40,000 rebalances | Below $0.50 |
| Base | ~$0.01 | ~1,000 rebalances | Below $1 |

### Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  User Deposit │────▶│ AgentEscrow  │────▶│  LP Position    │
│  (escrow)     │     │  Contract    │     │  (LFJ/Solana)   │
└─────────────┘     └──────┬───────┘     └────────┬────────┘
                           │                       │
                    ┌──────▼───────┐        ┌──────▼───────┐
                    │  Gas Reserve │        │ Out of Range? │
                    │  (auto-pull) │◀───────│ YoYo monitors │
                    └──────────────┘        └──────────────┘
```

---

## Subscription Tiers

### Free Tier
- Manual rebalance only
- User pays own gas
- Notifications when out of range
- Basic PnL dashboard

### Pro Tier (Paid)
- ✅ Auto-rebalance enabled
- ✅ Gas abstracted from deposit
- ✅ Priority rebalancing (tighter range triggers)
- ✅ Full analytics (fee tracking, PnL, gas breakdown)
- ✅ Multi-position management

### Enterprise / API Tier
- Custom rebalance strategies
- Programmatic access via x402
- White-label LP management

---

## Smart Contract Design (DMOB scope)

### Key Functions

```solidity
// User deposits funds — splits into LP + gas reserve
function deposit(uint256 amount) external;

// Operator triggers rebalance — gas pulled from reserve
function rebalance(
    uint256 tokenId,
    int24 newLowerTick,
    int24 newUpperTick
) external onlyOperator;

// View gas reserve balance
function getGasReserve(address user) external view returns (uint256);

// Top up gas reserve manually
function topUpGas() external payable;
```

### Access Control
- **Operator** (Gentech's agent wallet) can trigger rebalances
- **User** can withdraw anytime (escrow pattern)
- **Guard:** Rebalance gas cost must not exceed X% of position value (prevent spam)

---

## Solana-Specific (if we expand)

On Solana, gas is so cheap ($0.00025/tx) that:
- Auto-rebalance could be **free tier** — gas is rounding error
- Platform margin comes from subscription/performance fee, not gas
- x402 nanopayments handle per-rebalance cost transparently

**Proposal:** Offer free auto-rebalance on Solana as a competitive differentiator.

---

## Revenue Model

| Source | Free | Pro |
|--------|------|-----|
| Subscription | $0 | $X/mo or % of yield |
| Gas markup | N/A | At-cost (no markup) |
| Performance fee | 0% | 0.5-1% of LP yield |
| Analytics | Basic | Full |

**Key principle from Jordan:** Gas at cost, margin on agent services. The value is the intelligence, not the gas.

---

## Status

- [ ] Awaiting DMOB feasibility review (contract architecture)
- [ ] Awaiting YoYo competitive analysis (how does this compare to existing auto-rebalance services?)
- [ ] Awaiting team feedback on tier pricing
- [ ] Integration with AgentEscrow (Solana) TBD after hackathon sprint

---

*Next step: DMOB to assess contract complexity, YoYo to benchmark against DeFi auto-rebalance services (Arrakis, Gamma, etc.)*
