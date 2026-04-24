# Auto-Rebalance Gas Abstraction — Feature Spec

**Project:** The Trade Off  
**Component:** AgentEscrow + LP Rebalance Automation  
**Status:** DRAFT  
**Author:** Gentech HQ + YoYo Strategies  
**Date:** 2026-04-21  

---

## 1. Problem Statement

Users managing concentrated liquidity positions (e.g., LFJ V2.2 AVAX/USDC) face two friction points:

1. **Manual rebalancing** — When price exits their LP range, they must: remove liquidity → swap tokens → re-deposit at new range. Multiple transactions, timing risk, complexity.
2. **Gas payments** — Each rebalance costs gas. Users must maintain a separate AVAX balance just for gas, adding cognitive overhead.

**The Trade Off's solution:** Users deposit once. The platform handles rebalancing AND gas automatically. Zero manual intervention.

---

## 2. Vision

```
User deposits USDC/AVAX into AgentEscrow
         ↓
Contract holds: LP tokens + gas reserve
         ↓
[Platform monitors price range via oracle/cron]
         ↓
Price exits range (e.g., 9.10–9.65)
         ↓
Contract auto-executes: remove liquidity → swap → re-deposit
         ↓
Gas deducted from reserve → user charged $0 extra
```

**Philosophy:** "Better with us than without us, but I'm not going to bully you into it. I'm going to let you see it."

---

## 3. Architecture

### 3.1 Core Components

| Component | Description | Implementation |
|-----------|-------------|----------------|
| **AgentEscrow** | Holds user deposits (LP tokens + gas reserve) | Solidity smart contract on Avalanche |
| **Gas Reserve** | Small % of deposit earmarked for gas | 1-2% of deposit value, auto-calculated |
| **Range Monitor** | Detects when price exits LP range | Off-chain cron (Hermes) + on-chain oracle fallback |
| **Rebalance Executor** | Orchestrates: remove → swap → re-deposit | Contract function callable by authorized executor |
| **Fee Collector** | Platform fee on rebalance (optional) | Configurable % (e.g., 0.1-0.5% per rebalance) |

### 3.2 Contract Interface (Draft)

```solidity
interface IAgentEscrow {
    // User actions
    function deposit(uint256 amount) external payable;  // Deposit USDC/AVAX
    function withdraw(uint256 amount) external;          // Withdraw funds
    function setRange(int24 lowerTick, int24 upperTick) external;
    
    // Platform actions (restricted)
    function executeRebalance(
        address pool,
        uint256 liquidity,
        uint256 amount0Min,
        uint256 amount1Min,
        int24 newLowerTick,
        int24 newUpperTick
    ) external;
    
    // Views
    function getGasReserve(address user) external view returns (uint256);
    function getPosition(address user) external view returns (Position);
    function isInRange(address user) external view returns (bool);
}
```

### 3.3 Trigger Mechanism

**Primary:** Off-chain cron monitoring (existing LP monitor pattern)
- Polls price every 10 minutes via Birdeye/DexScreener
- Detects price breach: `price < RANGE_LOW || price > RANGE_HIGH`
- Calls `executeRebalance()` on contract with pre-computed params

**Secondary:** On-chain oracle (future hardening)
- Chainlink or Pyth price feed
- Contract-level check before execution (prevents stale rebalances)

**Trigger Logic:**
```
IF price_out_of_range AND gas_reserve_sufficient:
    → Calculate new range (centered on current price, same width)
    → Compute swap amounts
    → Execute rebalance
    → Deduct gas from reserve
    → Log transaction
ELIF price_out_of_range AND gas_reserve_insufficient:
    → Alert user: "Top up gas or rebalance will pause"
    → Continue monitoring (grace period: 24h)
```

---

## 4. Gas Economics

### 4.1 Gas Reserve Model

**Initial reserve:** 2% of deposit value (in AVAX)

**Example:**
- User deposits $1,000
- Gas reserve: $20 worth of AVAX (~2 AVAX at $10/AVAX)
- Remaining: $980 goes to LP position

### 4.2 Rebalance Cost Estimation

| Operation | Estimated Gas | Cost @ 25 gwei, $10 AVAX |
|-----------|--------------|--------------------------|
| Remove liquidity | ~150,000 | ~$0.0375 |
| Swap tokens | ~120,000 | ~$0.0300 |
| Re-deposit | ~200,000 | ~$0.0500 |
| **Total rebalance** | ~470,000 | **~$0.1175** |

**Rebalances per reserve:** $20 / $0.1175 ≈ **170 rebalances** before reserve depleted

### 4.3 Reserve Replenishment

Options (configurable per user):
1. **Auto-top-up:** Deduct from pending yield when reserve drops below threshold ($5)
2. **User notification:** Alert when reserve < 5 rebalances worth, user tops up manually
3. **Yield sweep:** Small % of earned fees auto-convert to gas reserve

---

## 5. State Machine

```
[DEPOSITED] 
    ↓ (price in range)
[MONITORING]
    ↓ (price exits range)
[REBALANCE_PENDING]
    ↓ (executor calls)
[REBALANCING]
    ↓ (tx confirmed)
[MONITORING] ← loop
    ↓ (gas reserve depleted)
[GAS_LOW_ALERT]
    ↓ (user tops up or yield sweep)
[MONITORING] ← loop
```

---

## 6. Failure Modes

| Failure | Cause | Handling |
|---------|-------|----------|
| **Swap slippage** | High volatility during rebalance | Configurable slippage tolerance (default 0.5%), revert if exceeded |
| **Gas reserve dry** | Too many rebalances, AVAX price spike | Pause rebalance, alert user, 24h grace period |
| **Executor failure** | Off-chain bot goes down | On-chain fallback: user can call manually, or secondary executor |
| **Price oracle stale** | Chainlink/Pyth delay | Rebalance rejected if oracle data > 15 min old |
| **MEV sandwich** | Front-running on swap | Use private mempool (MEV Blocker) or time-weighted execution |
| **Contract exploit** | Smart contract vulnerability | Multi-sig governance, timelock on upgrades, audit before mainnet |

---

## 7. Security Considerations

- **Executor authorization:** Only whitelisted addresses can call `executeRebalance()`
- **User funds segregation:** Each user's LP tokens and gas reserve tracked separately
- **Withdrawal guarantee:** Users can always withdraw their funds, regardless of rebalance state
- **Upgrade safety:** Contract upgrades require 48h timelock + multi-sig approval
- **Audit scope:** Full audit before mainnet deployment (Trail of Bits recommended)

---

## 8. Integration with The Trade Off Platform

### 8.1 User Flow (Frontend)
1. User connects wallet → sees available LP pools
2. Selects pool + range → deposits funds
3. Platform shows: "Your position is being managed. Gas: included."
4. Dashboard: yield earned, rebalance history, gas reserve remaining

### 8.2 Revenue Model
- **Platform fee:** 0.25% per rebalance (from position value, not gas)
- **Premium tiers:** Higher gas reserves, tighter range optimization, priority execution
- **Upsell path:** Free basic monitoring → paid auto-rebalance (AAE body layer pattern)

### 8.3 Agent Integration
- Hermes agents monitor positions (existing LP monitor cron)
- YoYo analyzes optimal range based on volatility
- Platform suggests range adjustments proactively

---

## 9. Milestones

| Phase | Scope | Timeline |
|-------|-------|----------|
| **MVP** | Single pool (AVAX/USDC), manual range, auto-rebalance | 2 weeks |
| **V1** | Multi-pool, auto-range optimization, gas reserve management | 4 weeks |
| **V2** | On-chain oracle triggers, premium tiers, multi-chain | 8 weeks |

---

## 10. Open Questions

1. Should gas reserve be denominated in AVAX (volatile) or stablecoin (converted at execution)?
2. What's the minimum deposit to make gas economics viable?
3. Do we support user-defined ranges only, or auto-suggested ranges?
4. Revenue split between The Trade Off and agent operators?

---

## Appendix

- **LP Monitor Rules:** `03-Strategies/LP-Monitor-Rules.md`
- **AAE Body Layer Pattern:** `03-Strategies/AAE-Body-Layer-Pattern.md`
- **LFJ V2.2 Docs:** https://docs.traderjoexyz.com
- **Existing LP Position:** AVAX/USDC, binStep 10, range $9.10-$9.65
