# Auto-Rebalance Gas Abstraction — Spec for DMOB

**Author:** Desmond (Gentech Creative)
**Date:** April 21, 2026
**Status:** Draft — pending YoYo review on financials
**Target Chain:** Avalanche (primary), Solana (future)

---

## Overview

Users deposit funds once. The platform handles LP rebalancing + gas automatically. Zero manual intervention. Gas is abstracted from the user's deposit — they never need to top up a separate gas wallet.

---

## User Flow

```
User deposits USDC/AVAX into AgentEscrow
         ↓
Contract allocates deposit:
  - ~98% → LP position
  - ~1%  → gas reserve
  - ~1%  → platform fee
         ↓
[Cron monitors LP price range]
         ↓
Price exits range (e.g., 9.10–9.65)
         ↓
Operator wallet signs rebalance tx:
  - Remove liquidity
  - Swap tokens
  - Re-deposit at new range
         ↓
Gas auto-deducted from gas reserve
         ↓
User sees: updated position, gas costs logged
```

---

## Contract Changes (AgentEscrow)

### New State Variables
```solidity
mapping(address => uint256) public gasReserve;
mapping(address => uint256) public totalGasUsed;
uint256 public gasReservePercent = 100; // 1% = 100 basis points
uint256 public platformFeePercent = 100; // 1%
```

### Modified `deposit()`
```solidity
function deposit(uint256 amount) external {
    uint256 gasAmt = amount * gasReservePercent / 10000;
    uint256 feeAmt = amount * platformFeePercent / 10000;
    uint256 lpAmt = amount - gasAmt - feeAmt;

    gasReserve[msg.sender] += gasAmt;
    platformFees += feeAmt;
    // lpAmt goes to LP position
    _addToLP(msg.sender, lpAmt);
}
```

### New `executeRebalance()`
```solidity
function executeRebalance(
    address user,
    uint256 gasCost
) external onlyOperator {
    require(gasReserve[user] >= gasCost, "Insufficient gas reserve");

    gasReserve[user] -= gasCost;
    totalGasUsed[user] += gasCost;

    // Rebalance logic: remove → swap → re-deposit
    _rebalancePosition(user);

    emit RebalanceExecuted(user, gasCost, block.timestamp);
}
```

### New `topUpGas()`
```solidity
function topUpGas(uint256 amount) external {
    gasReserve[msg.sender] += amount;
}
```

### Events
```solidity
event RebalanceExecuted(address indexed user, uint256 gasCost, uint256 timestamp);
event GasReserveLow(address indexed user, uint256 remaining);
event DepositSplit(address indexed user, uint256 lpAmount, uint256 gasAmount, uint256 fee);
```

---

## Operator Model

- **Operator wallet** signs rebalance transactions (Gentech-controlled)
- Operator cannot withdraw user funds — only calls `executeRebalance()`
- Gas cost is calculated off-chain (YoYo's cron) and passed to contract
- Operator is trusted for now; future: multi-sig or timelock

---

## Cron Integration (YoYo's Side)

1. Monitor LP position range via LFJ/subgraph
2. Detect when price exits user's range
3. Calculate optimal new range
4. Estimate gas cost for rebalance tx
5. If `gasReserve[user] >= gasCost` → call `executeRebalance()`
6. If `gasReserve[user] < gasCost` → emit `GasReserveLow` → notify user

---

## Two-Tier Model

| Feature | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Rebalance | Manual (user signs) | Auto (operator signs) |
| Gas | User pays own | Abstracted from deposit |
| Notifications | Out-of-range alerts | Out-of-range + auto-execute |
| Analytics | Basic PnL | Full PnL + optimization |

---

## Chain-Specific Notes

### Avalanche (LFJ)
- Gas: ~$0.02–0.05 per rebalance
- $10 gas reserve → ~200+ rebalances
- Model makes sense: charge for gas abstraction

### Solana (Future)
- Gas: ~$0.00025 per tx (negligible)
- **Do NOT charge users for gas** — it's a rounding error
- Monetize on: priority rebalancing, analytics, subscription
- Near-zero gas = can offer auto-rebalance as baseline feature

---

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Gas reserve hits zero | Revert to manual mode, notify user |
| Rebalance tx fails | Gas still consumed, retry on next trigger |
| User withdraws mid-cycle | Refund remaining gas reserve |
| Slippage during swap | Set max slippage in rebalance params |
| Multiple rebalances in short window | Cooldown period (e.g., 1 hour min between rebalances) |

---

## Open Questions for YoYo

1. What's the optimal gas reserve %? (1% seems right for AVAX, need validation)
2. Platform fee structure: flat %, per-rebalance, or subscription?
3. How do we handle gas price spikes (e.g., AVAX congestion)?
4. Revenue projection: how many users/rebalances to break even on operator costs?

## Open Questions for DMOB

1. Can `executeRebalance()` be made more gas-efficient?
2. Should we use a pull pattern (operator pushes) or keepers (Chainlink-style)?
3. Access control: how to secure operator role?
4. Upgrade path: proxy pattern or deploy new version?

---

## Next Steps

- [ ] YoYo: validate gas reserve math + fee structure
- [ ] DMOB: review contract changes, estimate gas costs
- [ ] Desmond: write user-facing docs + tier comparison
- [ ] Gentech: approve operator model + fee structure
