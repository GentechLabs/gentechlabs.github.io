# Auto-Rebalance Gas Abstraction — Spec

**Status:** Draft v1  
**Date:** 2025-04-21  
**Author:** YoYo (Strategies)

---

## 1. Problem

LP providers on LFJ (Pangolin) must manually rebalance when price exits range. This requires:
- Monitoring price constantly
- Having AVAX in wallet for gas
- Executing 3-4 txs (remove liquidity → swap → re-deposit)
- Bearing slippage risk during execution

**For non-technical users, this is a dealbreaker.**

---

## 2. Vision

User deposits funds **once** → system handles rebalancing + gas automatically. **Zero manual intervention.**

---

## 3. Users

| User Type | Need |
|-----------|------|
| **LP depositor** | Passive yield, no manual rebalancing |
| **Protocol/Gentech** | Revenue from gas management fee |
| **Operator (agent/cron)** | Reliable trigger + execution pipeline |

---

## 4. Functional Requirements

### 4.1 Deposit Flow
- User deposits USDC/AVAX into escrow contract
- Contract mints LP tokens and holds them
- 1-2% of deposit reserved as gas fund

### 4.2 Monitoring
- Cron job or oracle checks LP range status hourly
- Trigger when price exits defined range (e.g., $9.10–$9.65)
- Optional: early trigger at 80% toward boundary (preemptive rebalance)

### 4.3 Rebalance Execution
- Contract executes atomically:
  1. Remove liquidity from LP
  2. Swap tokens to rebalance ratio
  3. Re-deposit into new range
- Gas deducted from reserve pool, NOT user wallet

### 4.4 Reserve Management
- Reserve tops up automatically when below threshold (e.g., < $2)
- Top-up deducted from LP yield or deposit principal (configurable)
- User notified if reserve critically low

### 4.5 Withdrawal
- User can withdraw anytime
- Unused gas reserve returned to user
- Position closed and funds sent to user wallet

---

## 5. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Rebalance latency | < 30 min after trigger |
| Gas cost per rebalance | < $1.50 (Avalanche C-Chain) |
| Uptime | 99.5% monitoring availability |
| Failed tx handling | Retry 2x, then alert user |

---

## 6. Constraints

- Avalanche C-Chain gas only (no cross-chain)
- LFJ (Pangolin) V2 5bps pool initially
- Single pool support at launch (AVAX/USDC)
- No leverage or borrowing

---

## 7. Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Reserve hits $0 | Pause rebalancing, notify user to top up |
| Rebalance tx fails (slippage) | Retry with wider slippage tolerance (1%), protocol absorbs gas cost |
| User withdraws mid-rebalance | Queue withdrawal after current rebalance completes |
| Extreme gas spike (>5x normal) | Skip rebalance, alert user, retry next cycle |
| Price whipsaws (in/out of range rapidly) | Cooldown timer: min 2hr between rebalances |
| Contract exploit / hack | Emergency pause, withdraw all LP to safe wallet |

---

## 8. Out of Scope (v1)

- Multi-pool support
- Cross-chain rebalancing
- Yield optimization (just rebalancing, not farming strategy)
- Fiat on-ramp
- Leverage or borrowed positions

---

## 9. Acceptance Criteria

- [ ] User can deposit and never touch gas manually
- [ ] Rebalance executes within 30 min of trigger
- [ ] Gas reserve sustains 10+ rebalances on $1,000 deposit
- [ ] User can withdraw anytime with full accounting
- [ ] Failed txs handled gracefully (no stuck funds)
- [ ] Event logs for every rebalance (for P&L tracking)

---

## 10. Revenue Model (TBD)

| Fee Type | Rate | Notes |
|----------|------|-------|
| Management fee | 0.1-0.3% of AUM/year | Deducted from yield |
| Gas markup | 10-20% | Covers gas + protocol margin |
| $TECH discount | 20-30% off fees | If paid with $TECH |
