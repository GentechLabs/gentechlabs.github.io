# Auto-Rebalance Gas Abstraction — Implementation Plan

**Status:** Draft v1  
**Date:** 2025-04-21  
**Author:** YoYo (Strategies)

---

## Phase 0: Validate (Week 1)

- [ ] Confirm LFJ V2 rebalance mechanics (DMOB: contract review)
- [ ] Gas cost benchmarks on C-Chain (10 test rebalances)
- [ ] Define reserve model (per-user vs pooled)
- [ ] Legal/compliance check if needed

**Deliverable:** Go/no-go decision + reserve model chosen

---

## Phase 1: Smart Contract (Weeks 2-3) — DMOB

- [ ] `AutoRebalanceVault.sol` — escrow + LP management
  - `deposit()` — accept USDC/AVAX, mint LP, reserve gas
  - `rebalance(address pool, uint256 newLowerTick, uint256 newUpperTick)` — callable by operator
  - `withdraw()` — close position, return funds + unused gas
  - `topUpGasReserve()` — user or protocol can top up
- [ ] `GasReserveManager.sol` — manages pooled/per-user gas reserves
- [ ] Emergency pause mechanism (OpenZeppelin Pausable)
- [ ] Slippage protection on swaps
- [ ] Cooldown timer between rebalances

**Deliverable:** Deployed contracts on Fuji testnet

---

## Phase 2: Monitoring & Trigger (Week 3) — YoYo

- [ ] Cron job: check LP range status every 30 min
- [ ] Price feed: CoinGecko or Birdeye API
- [ ] Trigger logic: price exits range → call `rebalance()`
- [ ] Cooldown enforcement: skip if last rebalance < 2hr ago
- [ ] Alert system: Telegram notification on rebalance events

**Deliverable:** Working trigger pipeline on testnet

---

## Phase 3: P&L & UX (Week 4)

- [ ] P&L tracker: log every rebalance event (entry/exit price, gas cost, new range)
- [ ] Dashboard: show position status, gas reserve, rebalance history
- [ ] User notifications: deposit confirmed, rebalance executed, reserve low
- [ ] Integration with LP Position Tracker skill

**Deliverable:** End-to-end user flow demo

---

## Phase 4: Mainnet Launch (Week 5)

- [ ] Security audit (or DMOB internal review minimum)
- [ ] Deploy to Avalanche mainnet
- [ ] Seed initial gas pool from protocol treasury
- [ ] Beta with $500-1000 test deposit
- [ ] Monitor for 1 week before public launch

**Deliverable:** Live on mainnet

---

## Dependencies

| Task | Owner | Blocker? |
|------|-------|----------|
| Contract architecture | DMOB | Yes — everything depends on this |
| Gas benchmarks | YoYo | Yes — reserve model needs real numbers |
| Birdeye API integration | YoYo | No — can use CoinGecko fallback |
| Dashboard frontend | TBD | No — can use raw data initially |

---

## Open Questions

1. **Per-user vs pooled gas reserve?**
   - Per-user: simpler accounting, more overhead
   - Pooled: smoother UX, shared risk, needs trust
   
2. **Who pays failed tx gas?**
   - Protocol absorbs (user-friendly but costs us)
   - Reserve absorbs (fair but depletes user funds)

3. **$TECH integration?**
   - Accept $TECH for gas payments at discount?
   - REP tier boosts on gas reserve?

4. **Operator model?**
   - Keepers (external incentive to call rebalance)?
   - Our cron job (centralized but controlled)?
   - Hybrid?
