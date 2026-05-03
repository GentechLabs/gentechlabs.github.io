---
name: tech-payment-router
description: Dynamic dual-payment router for ERC20 tokens with burn/recycle split and adaptive discount
category: smart-contracts
---

# TECH Payment Router — Dynamic Burn & Discount

## When to use
Building a dual-payment system where users can pay with either a stablecoin (USDC) or a utility token ($TECH) with automatic burn/recycle and dynamic discounting.

## Contract pattern

### Core features
1. **Dual payment**: Stablecoin = full price, token = discounted
2. **Dynamic burn ratio**: Keeper-adjustable (10-90%) split between burn address and treasury
3. **Adaptive discount**: Auto-adjusts so token is always cheaper than stablecoin
4. **Cumulative tracking**: `totalBurned` and `totalRecycled` for dashboard analytics
5. **Custom errors**: Gas-efficient, OZ v5 compatible

### Key invariants (fuzz test these)
- **Token conservation**: `totalBurned + totalRecycled + contract balance == total paid in`
- **Discount guarantee**: Token price must always be cheaper than USDC for same service
- **Ratio bounds**: Burn ratio between MIN_BURN_RATIO (10%) and MAX_BURN_RATIO (90%)

### Test suite structure
1. Core payments — split verification across ratios (50/70/90)
2. Dynamic admin — bounds, access control, keeper role
3. Price math — discount calculation at different token prices
4. Keeper simulations — bull/bear market adjustments
5. Fuzz tests — token conservation + discount guarantee (256 runs)

## Integration strategy
- **Phase 1**: Deploy standalone alongside existing USDC-only escrow (AgentEscrow)
- **Phase 2**: Compose — PaymentRouter creates escrows with token payments
- **Phase 3**: Merge — add payment currency enum to escrow contract
- **Don't merge before having users.** Token sink only matters with real payment volume.

## Pitfalls
- OZ v5 uses custom errors, not string messages — test for `OwnableUnauthorizedAccount()` not `"Ownable"`
- Fuzz tests may generate initial value matching current value, causing `NoChange` error — exclude zero-delta case
- Decimal mismatch between token (18) and stablecoin (6) must be handled in price calculations

## Files
- Contract: `contracts/TECHPaymentRouter.sol`
- Tests: `test/TECHPaymentRouter.t.sol`
- Vault doc: `03-Strategies/TECH-token-dynamic-burn-research.md`
