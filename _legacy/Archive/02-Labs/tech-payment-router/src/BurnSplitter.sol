// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title BurnSplitter
/// @notice Splits $TECH payments between burn and treasury
/// @dev 70% burned (sent to dead address), 30% to treasury
contract BurnSplitter {
    using SafeERC20 for IERC20;

    uint256 public constant BURN_SHARE_BPS = 7000; // 70%
    uint256 public constant TREASURY_SHARE_BPS = 3000; // 30%

    address public constant DEAD_ADDRESS = 0x000000000000000000000000000000000000dEaD;

    IERC20 public immutable techToken;
    address public treasury;

    uint256 public totalBurned;
    uint256 public totalToTreasury;

    event PaymentSplit(
        address indexed from,
        uint256 totalAmount,
        uint256 burned,
        uint256 toTreasury
    );

    event TreasuryUpdated(address oldTreasury, address newTreasury);

    address public router;

    constructor(address _techToken, address _treasury, address _router) {
        require(_router != address(0), "BurnSplitter: zero router");
        techToken = IERC20(_techToken);
        treasury = _treasury;
        router = _router;
    }

    modifier onlyRouter() {
        require(msg.sender == router, "BurnSplitter: only router");
        _;
    }

    /// @notice Split a $TECH payment: burn 70%, treasury 30%
    /// @param from Address to pull tokens from (must have approved this contract)
    /// @param amount Total $TECH amount to split
    function split(address from, uint256 amount) external onlyRouter {
        uint256 burnAmount = amount * BURN_SHARE_BPS / 10000;
        uint256 treasuryAmount = amount - burnAmount; // remainder handles dust

        // Transfer from user to this contract
        techToken.safeTransferFrom(from, address(this), amount);

        // Burn: send to dead address
        if (burnAmount > 0) {
            techToken.safeTransfer(DEAD_ADDRESS, burnAmount);
            totalBurned += burnAmount;
        }

        // Treasury: send to treasury
        if (treasuryAmount > 0) {
            techToken.safeTransfer(treasury, treasuryAmount);
            totalToTreasury += treasuryAmount;
        }

        emit PaymentSplit(from, amount, burnAmount, treasuryAmount);
    }

    /// @notice Preview split amounts without executing
    function previewSplit(uint256 amount) external pure returns (uint256 burnAmount, uint256 treasuryAmount) {
        burnAmount = amount * BURN_SHARE_BPS / 10000;
        treasuryAmount = amount - burnAmount;
    }

    // --- Admin ---

    function setTreasury(address newTreasury) external onlyRouter {
        require(newTreasury != address(0), "BurnSplitter: zero address");
        address old = treasury;
        treasury = newTreasury;
        emit TreasuryUpdated(old, newTreasury);
    }

    function setRouter(address newRouter) external onlyRouter {
        require(newRouter != address(0), "BurnSplitter: zero address");
        router = newRouter;
    }
}
