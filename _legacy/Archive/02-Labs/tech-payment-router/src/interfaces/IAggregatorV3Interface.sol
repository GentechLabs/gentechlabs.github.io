// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Chainlink AggregatorV3Interface (subset we need)
interface IAggregatorV3Interface {
    function latestRoundData() external view returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    );
    function decimals() external view returns (uint8);
}
