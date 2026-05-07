// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title MockOracle — Simulates a price feed for testing dynamic discount
contract MockOracle {
    uint256 public price; // price in USD with 18 decimals (e.g., 1e18 = $1)

    constructor(uint256 _initialPrice) {
        price = _initialPrice;
    }

    function setPrice(uint256 _newPrice) external {
        price = _newPrice;
    }

    function getLatestPrice() external view returns (uint256) {
        return price;
    }
}
