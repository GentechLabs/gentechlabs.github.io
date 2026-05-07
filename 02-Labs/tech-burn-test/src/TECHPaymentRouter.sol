// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/// @title TECHPaymentRouter — Dynamic burn/recycle split for $TECH payments
/// @notice Routes $TECH payments into burn (deflationary) + treasury (recycle)
/// @dev Burn ratio is adjustable by owner (or keeper/oracle in production)
contract TECHPaymentRouter is Ownable, Pausable {
    using SafeERC20 for IERC20;

    IERC20 public immutable techToken;
    address public treasury;
    address public constant BURN_ADDRESS = 0x000000000000000000000000000000000000dEaD;

    // Basis points (0-10000). 5000 = 50% burn
    uint256 public burnRatioBps;

    // Dynamic discount off USDC price (basis points). 2500 = 25% off
    uint256 public discountBps;

    // Bounds
    uint256 public constant MIN_BURN_BPS = 1000;  // 10%
    uint256 public constant MAX_BURN_BPS = 9000;  // 90%
    uint256 public constant MAX_DISCOUNT_BPS = 5000; // 50%

    // Cumulative tracking
    uint256 public totalBurned;
    uint256 public totalRecycled;
    uint256 public totalPayments;

    // Circuit breaker — inherited from Pausable

    event PaymentProcessed(
        address indexed buyer,
        uint256 totalPaid,
        uint256 burned,
        uint256 recycled,
        uint256 burnRatioAtTime
    );
    event BurnRatioUpdated(uint256 oldRatio, uint256 newRatio);
    event DiscountUpdated(uint256 oldDiscount, uint256 newDiscount);
    event Paused(bool state);

    constructor(
        address _techToken,
        address _treasury,
        uint256 _initialBurnRatio,
        uint256 _initialDiscount
    ) Ownable(msg.sender) {
        techToken = IERC20(_techToken);
        treasury = _treasury;
        burnRatioBps = _initialBurnRatio;
        discountBps = _initialDiscount;
    }

    /// @notice Process a $TECH payment — splits into burn + treasury
    /// @param amount Raw $TECH amount (pre-discount, in token units)
    function processPayment(uint256 amount) external whenNotPaused {
        techToken.safeTransferFrom(msg.sender, address(this), amount);

        uint256 burnAmount = (amount * burnRatioBps) / 10000;
        uint256 recycleAmount = amount - burnAmount;

        if (burnAmount > 0) {
            techToken.safeTransfer(BURN_ADDRESS, burnAmount);
            totalBurned += burnAmount;
        }
        if (recycleAmount > 0) {
            techToken.safeTransfer(treasury, recycleAmount);
            totalRecycled += recycleAmount;
        }

        totalPayments += 1;

        emit PaymentProcessed(msg.sender, amount, burnAmount, recycleAmount, burnRatioBps);
    }

    /// @notice Calculate how much $TECH a user needs to pay for a given USDC price
    /// @param usdcPrice The price in USDC (e.g., 10e6 for $10)
    /// @param techPriceUsd Current $TECH price in USD (e.g., 1e18 for $1)
    /// @return techAmount The $TECH amount the user must pay
    function calculateTechPayment(
        uint256 usdcPrice,
        uint256 techPriceUsd
    ) external view returns (uint256 techAmount) {
        // Discounted USD price
        uint256 discountedUsd = usdcPrice * (10000 - discountBps) / 10000;
        // Convert to $TECH units
        techAmount = (discountedUsd * 1e18) / techPriceUsd;
    }

    // --- Admin functions ---

    function updateBurnRatio(uint256 newRatioBps) external onlyOwner {
        require(newRatioBps >= MIN_BURN_BPS && newRatioBps <= MAX_BURN_BPS, "Ratio OOB");
        uint256 oldRatio = burnRatioBps;
        burnRatioBps = newRatioBps;
        emit BurnRatioUpdated(oldRatio, newRatioBps);
    }

    function updateDiscount(uint256 newDiscountBps) external onlyOwner {
        require(newDiscountBps <= MAX_DISCOUNT_BPS, "Discount OOB");
        uint256 oldDiscount = discountBps;
        discountBps = newDiscountBps;
        emit DiscountUpdated(oldDiscount, newDiscountBps);
    }

    function updateTreasury(address newTreasury) external onlyOwner {
        require(newTreasury != address(0), "Zero addr");
        treasury = newTreasury;
    }

    function setPaused(bool _paused) external onlyOwner {
        if (_paused) {
            _pause();
        } else {
            _unpause();
        }
        emit Paused(_paused);
    }

    // --- View helpers ---

    function getStats() external view returns (
        uint256 _totalBurned,
        uint256 _totalRecycled,
        uint256 _totalPayments,
        uint256 _burnRatio,
        uint256 _discount
    ) {
        return (totalBurned, totalRecycled, totalPayments, burnRatioBps, discountBps);
    }
}
