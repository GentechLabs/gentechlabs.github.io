# Oracle Architecture — Chainlink Focus

**Date**: 2026-04-21  \
**Status**: Planning  \
**Study**: Jordan enrolled in Cyfrin Chainlink course

---

## Why Chainlink
- Industry standard for price feeds, VRF, automation
- Battle-tested since 2019, billions in TVL secured
- LayerZero can use Chainlink as DVN — synergizes with cross-chain security
- Cyfrin course covers: Price Feeds, VRF, Chainlink Functions, Automation

## Chainlink Services We Need

| Service | Use Case | Priority |
|---------|----------|----------|
| **Price Feeds** | Token pricing, collateral checks, liquidation triggers | High |
| **VRF** | Fair randomness for raffles, NFT minting | Medium |
| **Automation** | Keeper jobs — rebalancing, harvesting | Medium |
| **Functions** | Off-chain computation for on-chain use | Low |
| **CCIP** | Cross-chain messaging (alternative to LayerZero) | Evaluate |

## Implementation Checklist
- [ ] Complete Cyfrin Chainlink course modules
- [ ] Build Price Feed integration template in Foundry
- [ ] Build VRF v2.5 integration template
- [ ] Compare CCIP vs LayerZero for our cross-chain needs
- [ ] Gas benchmarks: Chainlink calls vs alternatives

## Code Patterns (Foundry)

### Price Feed Consumer
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract PriceConsumer {
    AggregatorV3Interface internal priceFeed;

    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    function getLatestPrice() public view returns (int) {
        (,int price,,,) = priceFeed.latestRoundData();
        return price;
    }
}
```

### Notes from Cyfrin Course
_TBD — add notes as course progresses_

---

## Chainlink vs LayerZero Decision Framework

| Factor | Chainlink CCIP | LayerZero |
|--------|---------------|-----------|
| Security model | Fixed (Chainlink DONs) | Configurable (DVN choice) |
| Footgun risk | Low | High (47% 1-of-1 DVN) |
| Maturity | Newer (CCIP) but Chainlink brand | Longer track record |
| Gas cost | TBD — benchmark | TBD — benchmark |
| Ecosystem | Large | Large |
| Supported chains | Growing | Growing |

**Current lean**: Chainlink CCIP unless LayerZero offers a specific advantage for a use case.
