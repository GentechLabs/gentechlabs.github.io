---
name: tech-payment-router
description: Dynamic burn/recycle token sink mechanism for $TECH payments
---

# TECHPaymentRouter Session Decisions

## What Was Built
- Foundry test project at `03-Projects/tech-burn-test/`
- `TECHPaymentRouter.sol` — dynamic burn/recycle split, adaptive discount, circuit breaker
- `MockTECH.sol`, `MockOracle.sol` — test infrastructure
- **29/29 tests passing**

## Architecture: Split Router Pattern
- Default: 60% burn / 40% treasury, governance-adjustable (10-90% range)
- Adaptive discount: 0-50%, auto-adjusts so $TECH always cheaper than USDC
- Cumulative burn tracking for dashboard transparency
- Circuit breaker pause for emergency
- OZ v5 compatible (custom errors)

## Discount Math
- $TECH payment always 75% of USDC price regardless of token price (25% discount)
- At $0.01/TECH → pay 750 tokens for $10 agent
- At $100/TECH → pay 0.075 tokens for $10 agent
- Always $7.50 equivalent

## Oracle-Adjusted Dynamic Pricing
- Price pumps → increase burn %, tighten discount
- Price dumps → decrease burn %, widen discount, more to BuybackReserve
- Keeper-driven, no governance vote needed for micro-adjustments

## Integration Points
| Contract | Router Hook |
|----------|------------|
| AgentNFT.mintPremium() | Route through router instead of direct $TECH transfer |
| JobEscrow.approveJob() | Platform fee split burn/treasury via router |
| AgentMarketplace | Listing/sale fees → router split |
| TECH.sol | Router calls TECH.burn() or transfers to 0xdead |

## Risks
- Discount needs aggressive tightening on price pumps to prevent treasury drain
- 10-50% discount range wide enough but keeper algo needs tuning
- Users may default to USDC if discount not compelling vs gas cost of acquiring $TECH