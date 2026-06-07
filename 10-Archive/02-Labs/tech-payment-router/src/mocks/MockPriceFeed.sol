// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../interfaces/IAggregatorV3Interface.sol";

/// @notice Mock Chainlink price feed for testing
contract MockPriceFeed is IAggregatorV3Interface {
    int256 public price;
    uint8 public override decimals;
    uint256 public lastUpdateTime;

    constructor(uint8 _decimals, int256 _price) {
        decimals = _decimals;
        price = _price;
        lastUpdateTime = block.timestamp;
    }

    function setPrice(int256 _price) external {
        price = _price;
        lastUpdateTime = block.timestamp;
    }

    function latestRoundData() external view override returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) {
        return (1, price, lastUpdateTime, lastUpdateTime, 1);
    }
}
