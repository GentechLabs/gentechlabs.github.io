# ⛓️ Chainlink Oracle Hardening Guide
**For Gentech Smart Contracts — Cyfrin Course Reference**

---

## Why This Matters for Us
Both `TechPaymentRouter` and `DiscountCalculator` depend on oracle prices. Bad oracle data = wrong discounts = protocol losses or user exploitation.

---

## The 5 Chainlink Checks Every Production Contract Needs

### 1. Staleness Check (updatedAt)
```solidity
(, , , uint256 updatedAt,,) = priceFeed.latestRoundData();
require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price");
```
**Why:** If Chainlink nodes stop updating (sequencer down, feed deprecated), you get ancient prices. On L2s, the sequencer can go down for hours.

### 2. Round Completeness (answeredInRound)
```solidity
(uint80 roundId, , , , uint80 answeredInRound) = priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Incomplete round");
```
**Why:** If a round was started but not completed, you get partial/invalid data. This catches mid-round reads.

### 3. Positive Price Check
```solidity
require(answer > 0, "Invalid price");
```
**Why:** Chainlink can return negative prices for forex feeds. For crypto/USD, this should never happen, but edge cases exist.

### 4. Sequencer Uptime (L2 Only — Arbitrum/Base/Optimism)
```solidity
// Sequencer feed: 0x3dB52cE065f728011Ac752C7B25B39b5CaB3dE54 (Arbitrum)
(, int256 sequencerUp,,,) = sequencerFeed.latestRoundData();
require(sequencerUp == 1, "Sequencer is down");
```
**Why:** If the L2 sequencer is down, transactions queue but oracle updates can arrive before the sequencer is back. You could trade on stale prices during the grace period.

### 5. Feed Deprecation Check
```solidity
// Some feeds return a heartbeat of 0 when deprecated
uint80 roundId = priceFeed.latestRoundData().roundId;
require(roundId != 0, "Deprecated feed");
```
**Why:** Chainlink sometimes deprecates feeds (e.g., UST/USD after the collapse). The feed still exists but stops updating.

---

## Production-Ready Oracle Adapter Pattern

Instead of calling `latestRoundData()` in each contract, create a shared adapter:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IAggregatorV3Interface} from "./interfaces/IAggregatorV3Interface.sol";

/// @title OracleAdapter — Centralized Chainlink price feed handler
/// @notice Handles all oracle edge cases in one place
contract OracleAdapter {
    uint256 public constant MAX_STALENESS = 1 hours;

    IAggregatorV3Interface public immutable priceFeed;

    constructor(address _priceFeed) {
        priceFeed = IAggregatorV3Interface(_priceFeed);
    }

    /// @notice Get a validated price (18 decimals)
    function getPrice() external view returns (uint256) {
        (
            uint80 roundId,
            int256 answer,
            ,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        uint8 decimals = priceFeed.decimals();

        require(answer > 0, "OracleAdapter: negative price");
        require(answeredInRound >= roundId, "OracleAdapter: incomplete round");
        require(
            block.timestamp - updatedAt <= MAX_STALENESS,
            "OracleAdapter: stale price"
        );

        return uint256(answer) * (10 ** (18 - decimals));
    }

    /// @notice Get price with custom max staleness
    function getPrice(uint256 maxStaleness) external view returns (uint256) {
        (
            uint80 roundId,
            int256 answer,
            ,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        uint8 decimals = priceFeed.decimals();

        require(answer > 0, "OracleAdapter: negative price");
        require(answeredInRound >= roundId, "OracleAdapter: incomplete round");
        require(
            block.timestamp - updatedAt <= maxStaleness,
            "OracleAdapter: stale price"
        );

        return uint256(answer) * (10 ** (18 - decimals));
    }
}
```

**Then refactor TechPaymentRouter and DiscountCalculator to use OracleAdapter instead of raw `latestRoundData()` calls.**

---

## Chainlink Automation for SMA Updates

Currently `updateSMA()` is open to anyone. Production approach:

### Option A: Chainlink Automation (Recommended)
Register an Upkeep that calls `updateSMA()` on a schedule. The Chainlink registry ensures only authorized upkeep addresses can call.

```solidity
function updateSMA(uint256 newSma) external {
    require(msg.sender == address(chainlinkRegistry), "Only keeper");
    smaPrice = newSma;
}
```

### Option B: Custom Keeper with Access Control
```solidity
address public keeper;

modifier onlyKeeper() {
    require(msg.sender == keeper, "Only keeper");
    _;
}

function updateSMA(uint256 newSma) external onlyKeeper {
    smaPrice = newSma;
}
```

---

## Key Addresses for Testnet

| Network | Feed Registry | Sequencer Uptime |
|---------|--------------|------------------|
| Base Sepolia | Chainlink docs | Required for L2 |
| Avalanche Fuji | Chainlink docs | N/A (L1) |
| Arbitrum Sepolia | Chainlink docs | 0x3dB52cE... |

Check [Chainlink Docs](https://docs.chain.link/data-feeds/price-feeds/addresses) for latest addresses.

---

## Cyfrin Course Alignment

If you're working through Cyfrin's Chainlink course, these concepts map directly:
- **Lesson: Price Feeds** → Our `latestRoundData()` usage
- **Lesson: Automation** → SMA update keeper pattern
- **Lesson: VRF** → Future: random selection for hackathon winners?
- **Lesson: Functions** → Future: off-chain loyalty tier computation

---

*Created: 2026-04-21 by YoYo*
*Reference: Cyfrin Updraft Chainlink Course*
*Status: Reference doc — no action required until DMOB fixes oracle findings*
